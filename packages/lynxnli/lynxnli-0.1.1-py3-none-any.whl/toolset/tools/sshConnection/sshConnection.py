from typing import Optional, Dict
from content.state import ToolResult
import os
import paramiko
from importlib.resources import files
from content.state import ToolResult
import os
from agents.agant_tool import ToolAgent


REMOTE_HOST = os.getenv("tool_hpc_host")
REMOTE_PORT = os.getenv("tool_hpc_port")
REMOTE_USER = os.getenv("tool_hpc_user")
SSH_KEY_PATH = os.path.expanduser(os.getenv("tool_hpc_key_path"))
REMOTE_WORKDIR= os.getenv("tool_hpc_workdir").rstrip("/")

tool_genCode_path = os.getenv("tool_genCode_path")
FILES_DIR = str(files("toolset").joinpath(tool_genCode_path))
OUTPUT_FILE   = os.path.join(FILES_DIR, "output_log")

tool = ToolAgent()

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

def summarise_output(output: str) -> str:
    return tool.llm.send_request(f"Summarise the output: <{output}> to short text and keep the key information\n")


def run(q: None) -> ToolResult:


    logs = []
    logs.append(f"[Step] Connecting to {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PORT}...\n")
    ssh = get_ssh_client()
    logs.append("[Step] SSH connection established.\n")
    query = input("SSH connection is established, input your query OR q/Q/ for quit. \n>>>: ")

    execution = {}
    while query != "q" and query != "Q" and query != "Quit" and query != "quit":
        prompt = f"Given the query of user: <{query}> and previous execution <{str(execution)}>, please generate the corresponding command for HPC cluster. Only return the command in string without any comments and quotation mark."
        cmd = tool.llm.send_request(prompt)

        print(f"SSH: You are going to execute the command in [remote server]: {cmd}")
        y_or_n = input("Execute? Y/N: ")
        if y_or_n in ["y", "Y", "yes", "Yes"]:
            try:
                _, stdout, stderr = ssh.exec_command(cmd)
                code = stdout.channel.recv_exit_status()
                out, err = stdout.read().decode(), stderr.read().decode()
                output = ""
                errput = ""
                if out != "":
                    output = summarise_output(out)
                    logs.append(f"[ssh stdout]: {output}")
                    print(f"[ssh stdout]: {output}")
                if err != "":
                    errput = summarise_output(err)
                    logs.append(f"[ssh stderr]: {errput}")
                    print(f"[ssh stderr]: {errput}")
                execution[cmd] = output+errput
            finally:
                logs.append("[Step] Start next user query.\n")

        else:
            logs.append(f"[SSH]:User interupt the execuation!\n")
            return ToolResult(
                output="User interupt the execuation!",
                stop=False
            )

        query = input("SSH connection is established, input your query OR q/Q/quit for quit. \n>>>: ")
    ssh.close()
    logs.append(f"[SSH]: No query has been asked by user!\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fo:
        fo.writelines(logs)
    return ToolResult(
            output="Your queries are done with SSH connection.",
            stop=False
            )

