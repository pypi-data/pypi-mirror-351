from toolset.tool_setup import agent, get_ssh_client, OUTPUT_FILE
from toolset.tool_setup import  HOST, PORT, USER
from content.state import ToolResult
import textwrap


def run(q: None) -> ToolResult:
    logs = []
    logs.append(f"[Step] Connecting to {USER}@{HOST}:{PORT}...\n")
    ssh = get_ssh_client(HOST, PORT, USER)
    logs.append("[Step] SSH connection established.\n")
    query = input("SSH connection is established, input your query OR q/Q/ for quit. \n>>>: ")

    execution = {}
    while query != "q" and query != "Q" and query != "Quit" and query != "quit":
        prompt = f"Given the query of user: <{query}> and previous execution <{str(execution)}>, please generate the corresponding command for HPC cluster. Only return the command in string without any comments and quotation mark."
        cmd = agent.llm.send_request(prompt)

        print(f"SSH: You are going to execute the command in [{HOST}]: {cmd}")
        y_or_n = input("Execute? Y/N: ")
        if y_or_n in ["y", "Y", "yes", "Yes"]:
            try:
                _, stdout, stderr = ssh.exec_command(cmd)
                code = stdout.channel.recv_exit_status()
                out, err = stdout.read().decode(), stderr.read().decode()
                if code == 0:
                    message = f"[SSH]: Command execution at remote server {HOST} is successful for code {code}, output is <{out}>.\n"
                    logs.append(message)
                    out = agent.llm.send_request(f"Summarise the output: <{message}> to short text and keep the key information\n")
                    print(f"[ssh stdout]:\n{textwrap.fill(out, width=80, initial_indent=' '*15, subsequent_indent=' '*15)}")

                else:
                    message = f"[SSH]: Command execution at remote server {HOST} failed with code {code}, error is {err}.\n"
                    logs.append(message)
                    err = agent.llm.send_request(f"Summarise the output: <{message}> to short text and keep the key information\n")
                    print(f"[ssh stderr]:\n{textwrap.fill(err, width=80, initial_indent=' '*15, subsequent_indent=' '*15)}")
                execution[cmd] = out+err
            finally:
                logs.append("[Step] Start next user query.\n")

        else:
            ssh.close()
            logs.append(f"[SSH]:User interupt the execuation!\n")
            return ToolResult(
                output=f"User interupt the execuation! The commands and outputs are: {str(execution)}.\n",
                stop=True
            )

        query = input("SSH connection is established, input your query OR q/Q/quit for quit. \n>>>: ")
    ssh.close()
    logs.append(f"[SSH]: No query has been asked by user!\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fo:
        fo.writelines(logs)

    return ToolResult(
            output=f"Your queries are done with SSH connection. the commands and outputs are: {str(execution)}.\n",
            stop=True
            )

