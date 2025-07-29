import os
import paramiko
from agents.agant_tool import ToolAgent
from importlib.resources import files
import os
from content.state import ToolResult

REMOTE_HOST = os.getenv("tool_remote_host")
REMOTE_PORT = os.getenv("tool_remote_port")
REMOTE_USER = os.getenv("tool_remote_user")
SSH_KEY_PATH = os.path.expanduser(os.getenv("tool_remote_key_path"))
REMOTE_WORKDIR= os.getenv("tool_remote_workdir").rstrip("/")

tool_genCode_path = os.getenv("tool_genCode_path")
FILES_DIR = str(files("toolset").joinpath(tool_genCode_path))
OUTPUT_FILE   = os.path.join(FILES_DIR, "output_log")

# ——— SSH helpers ———
def get_ssh_client() -> paramiko.SSHClient:
    # for encrypted ssh key, please set the correct password, otherwise attribute will be ignored
    key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH, password=os.getenv("mykey"))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=REMOTE_HOST,
        port=REMOTE_PORT,
        username=REMOTE_USER,
        pkey=key,
        look_for_keys=False,
        allow_agent=False,
    )
    return ssh

def upload_directory(sftp: paramiko.SFTPClient, local_dir: str, remote_dir: str):
    """ Recursively create remote_dir and upload all files under local_dir. """
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass  # already exists
    for fname in os.listdir(local_dir):
        lpath = os.path.join(local_dir, fname)
        rpath = f"{remote_dir}/{fname}"
        if os.path.isdir(lpath):
            upload_directory(sftp, lpath, rpath)
        else:
            sftp.put(lpath, rpath)

# ——— Main runner ———
def run(q=None) -> str:
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

            agent = ToolAgent(agent_name="tool")                        
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
    ssh = get_ssh_client()
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
        output = f"Python execution in remote server is done, see output file path in {OUTPUT_FILE}",
        stop=False
        )   
    
if __name__ == "__main__":
    res = run()
    print(f"Logs written to: {res['output_file_path']}")
