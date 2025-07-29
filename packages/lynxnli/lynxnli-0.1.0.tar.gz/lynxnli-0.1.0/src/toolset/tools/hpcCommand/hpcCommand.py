import os
import paramiko
from agents.agant_tool import ToolAgent
from importlib.resources import files
from content.state import ToolResult
import os


REMOTE_HOST = os.getenv("tool_hpc_host")
REMOTE_PORT = os.getenv("tool_hpc_port")
REMOTE_USER = os.getenv("tool_hpc_user")
SSH_KEY_PATH = os.path.expanduser(os.getenv("tool_hpc_key_path"))
REMOTE_WORKDIR= os.getenv("tool_hpc_workdir").rstrip("/")

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
        allow_agent=True,
    )
    return ssh


# ——— Main runner ———
def run(hpcCommands) -> str:
    cmd = hpcCommands.get("command", "")
    if not cmd:
        raise ValueError("No command provided for HPC execution.")

    logs = []
    logs.append(f"[Step] Connecting to {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}...\n")
    ssh = get_ssh_client()
    logs.append("[Step] SSH connection established.\n")
    y_or_n = input(f"You are going to execute the command in HPC Login Node: {cmd} \nExecute? Y/N: ")
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
    
    
    

