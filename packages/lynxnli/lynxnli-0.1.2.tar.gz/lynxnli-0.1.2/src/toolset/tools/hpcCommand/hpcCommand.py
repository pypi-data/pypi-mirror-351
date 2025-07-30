from content.state import ToolResult
from toolset.tool_setup import get_ssh_client
from toolset.tool_setup import OUTPUT_FILE, REMOTE_HOST, REMOTE_PORT, REMOTE_USER


# ——— Main runner ———
def run(hpcCommands) -> ToolResult:
    cmd = hpcCommands.get("command", "")
    if not cmd:
        raise ValueError("No command provided for HPC execution.")

    logs = []
    logs.append(f"[Step] Connecting to {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}...\n")
    ssh = get_ssh_client()
    logs.append("[Step] SSH connection established.\n")
    y_or_n = input(f"You are going to execute the command in [HPC Login Node]: {cmd} \nExecute? Y/N: ")
    if y_or_n in ["y", "Y", "yes", "Yes"]:
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            code = stdout.channel.recv_exit_status()
            out, err = stdout.read().decode(), stderr.read().decode()

            if out:
                logs.append(f"[stdout: {out}]")
            if err:
                logs.append(f"[stderr: {err}]")
            logs.append(f"Command {cmd} exited with code {code}\n")
        finally:
            ssh.close()
            logs.append("[Step] SSH connection closed.\n")
    else:
        logs.append("[Step] HPC Command execution cancelled by user.\n")
        return ToolResult(
            output="HPC Command execution cancelled by user.",
            stop=True
        )

    # 7) Write logs locally
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fo:
        fo.writelines(logs)

    # print(f"Code is {code}\n")
    # print(f"Output is {out}\n")
    # print(f"Error is {err}\n")

    if err == "":
        return ToolResult(
                output=f"The execution in hpc cluster is done. The output is: <{out}>.\n",
                stop=False
            )
    else:
        return ToolResult(
                output=f"The execution in hpc cluster is done. The error is <{err}>\n.",
                stop=False
            )        
