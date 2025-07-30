import os
from agents.agant_tool import ToolAgent
import paramiko
from importlib.resources import files

agent = ToolAgent(agent_name="agent_tool")

HPC_HOST = os.getenv("tool_hpc_host")
HPC_PORT = os.getenv("tool_hpc_port")
HPC_USER = os.getenv("tool_hpc_user")

REMOTE_HOST = os.getenv("tool_remote_host")
REMOTE_PORT = os.getenv("tool_remote_port")
REMOTE_USER = os.getenv("tool_remote_user")

SSH_CONNECTION = os.getenv("tool_ssh_connection")
HOST = HPC_HOST if SSH_CONNECTION == "hpc" else REMOTE_HOST
PORT = HPC_PORT if SSH_CONNECTION == "hpc" else REMOTE_PORT
USER = HPC_USER if SSH_CONNECTION == "hpc" else REMOTE_USER

MYKEY = os.getenv("mykey")

SSH_KEY_PATH = os.path.expanduser(os.getenv("tool_key_path"))
REMOTE_WORKDIR= os.getenv("tool_remote_workdir").rstrip("/")
tool_genCode_path = os.getenv("tool_genCode_path")

FILES_DIR = str(files("toolset").joinpath(tool_genCode_path))
OUTPUT_FILE   = os.path.join(FILES_DIR, "output_log")

# ——— SSH helpers ———
def get_ssh_client(host=HOST, port=PORT, user= USER) -> paramiko.SSHClient:
    # for encrypted ssh key, please set the correct password, otherwise attribute will be ignored
    key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH, password=MYKEY if MYKEY else None)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=host,
        port=port,
        username=user,
        pkey=key,
        look_for_keys=False,
        allow_agent=True,
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