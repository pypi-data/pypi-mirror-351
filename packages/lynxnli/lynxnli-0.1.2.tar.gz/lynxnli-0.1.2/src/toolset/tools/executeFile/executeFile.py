import os
from content.state import ToolResult
from toolset.tool_setup import agent, get_ssh_client, upload_directory
from toolset.tool_setup import FILES_DIR, OUTPUT_FILE, REMOTE_HOST, REMOTE_PORT, REMOTE_USER, REMOTE_WORKDIR


# ——— Main runner ———
def run(q=None) -> ToolResult:
    if not os.path.isdir(FILES_DIR):
        raise FileNotFoundError(f"Directory not found: {FILES_DIR}")

    logs = []
    logs.append(f"[Step] Checking for config and preparing to run at {FILES_DIR}\n")

    # 1) Generate requirements.txt locally if missing
    req_path = os.path.join(FILES_DIR, "requirements.txt")
    if not os.path.isfile(req_path):
        logs.append("[Step] No requirements.txt found locally. Prompting for generation...\n")
        resp = input("No requirements.txt found. Generate one automatically? [y/N]: ").strip().lower()
        if resp in ("y", "yes"):
            combined = ""
            for f in sorted(os.listdir(FILES_DIR)):
                if f.endswith(".py"):
                    with open(os.path.join(FILES_DIR, f), encoding="utf-8") as fh:
                        combined += f"# File: {f}\n" + fh.read() + "\n\n"

            prompt = (
                "Given these Python files, produce a valid requirements.txt "
                "(one package per line). Respond with only the requirements text.\n\n"
                f"{combined}"
            )
#               req_txt = llm.send_request(prompt)
            req_txt = agent.llm.send_request(prompt)
            import re
            pkgs = [p for p in re.split(r"[,\s]+", req_txt.strip()) if p]
            with open(req_path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(pkgs) + "\n")
            logs.append(f"[Step] Generated requirements.txt with packages: {pkgs}\n")

    # 2) Establish SSH connection
    logs.append(f"[Step] Connecting to {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}...\n")
    ssh = get_ssh_client(REMOTE_HOST, REMOTE_PORT, REMOTE_USER)
    logs.append("[Step] SSH connection established.\n")

    try:
        # 3) Upload files
        logs.append(f"[Step] Uploading directory {FILES_DIR} to remote {REMOTE_WORKDIR}...\n")
        base = os.path.basename(FILES_DIR.rstrip("/"))
        remote_dir = f"{REMOTE_WORKDIR}/{base}"
        sftp = ssh.open_sftp()
        upload_directory(sftp, FILES_DIR, remote_dir)
        sftp.close()
        logs.append(f"[Step] Upload complete: {FILES_DIR} → {remote_dir}\n")

        # 4) Install remote requirements if present
        if os.path.isfile(req_path):
            logs.append("[Step] Installing requirements on remote...\n")
            cmd = f"cd {remote_dir} && pip3 install -r requirements.txt"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            code = stdout.channel.recv_exit_status()
            out, err = stdout.read().decode(), stderr.read().decode()
            if out:
                logs.append("[pip stdout]\n" + out)
            if err:
                logs.append("[pip stderr]\n" + err)
            logs.append(f"[Step] Remote pip install exited with code {code}\n")

        # 5) Execute each script
        for f in sorted(os.listdir(FILES_DIR)):
            if f.endswith(".py"):
                logs.append(f"[Step] Executing script {f} on remote...\n")
                cmd = f"cd {remote_dir} && python3 {f}"
                stdin, stdout, stderr = ssh.exec_command(cmd)
                code = stdout.channel.recv_exit_status()
                out, err = stdout.read().decode(), stderr.read().decode()
                if out:
                    logs.append(f"[stdout {f}]\n" + out)
                if err:
                    logs.append(f"[stderr {f}]\n" + err)
                logs.append(f"[Step] Script {f} exited with code {code}\n")

        # 6) Cleanup
        logs.append(f"[Step] Cleaning up remote directory {remote_dir}...\n")
        ssh.exec_command(f"rm -rf {remote_dir}")
        logs.append("[Step] Remote cleanup complete.\n")
    finally:
        ssh.close()
        logs.append("[Step] SSH connection closed.\n")

    # 7) Write logs locally
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fo:
        fo.writelines(logs)

    return ToolResult(
        output = f"Running the Python files is done and successful, see output file path in {OUTPUT_FILE}",
        stop=False
        )   
    
if __name__ == "__main__":
    res = run()
    print(f"Logs written to: {res['output_file_path']}")
