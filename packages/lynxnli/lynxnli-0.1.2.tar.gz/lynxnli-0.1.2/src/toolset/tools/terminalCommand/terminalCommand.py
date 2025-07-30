import subprocess
import shlex
from typing import Optional, Dict
from content.state import ToolResult

# List of allowed commands for basic safety
ALLOWED_COMMANDS = {
    'ls', 'pwd', 'echo', 'cat', 'grep', 'find', 'wc',
    'date', 'df', 'du', 'free', 'top', 'ps', 'vim', 'nano', 'emacs'
}

def is_safe_command(command: str) -> bool:
    """
    Check if the command is in the allowed list
    """
    first_word = command.strip().split()[0]
    return first_word in ALLOWED_COMMANDS


class CommandExecutionError(Exception):
    """
    Custom exception raised when command execution fails.
    """
    def __init__(self, message: str, returncode: Optional[int] = None, output: Optional[str] = None, stderr: Optional[str] = None):
        super().__init__(message)
        self.returncode = returncode
        self.output = output
        self.stderr = stderr

def run(
    query: Dict,
    timeout: Optional[float] = None,
    check: bool = False,
    capture_output: bool = True,
    text: bool = True,
    shell: bool = True
) -> ToolResult:
    """
    Execute a terminal command safely and handle failures.

    Args:
        cmd: The command to execute, either as a string or a list of arguments.
        timeout: Maximum time in seconds to allow the command to run.
        check: If True, raise CalledProcessError on non-zero exit status.
        capture_output: If True, capture stdout and stderr.
        text: If True, treat output as text (decoded to str); if False, returns bytes.
        shell: If True, the command will be executed through the shell.
               Use with caution to avoid shell injection.

    Returns:
        A subprocess.CompletedProcess instance containing:
          - args: the executed command
          - returncode: exit status
          - stdout: command output (if captured)
          - stderr: command error output (if captured)

    Raises:
        CommandExecutionError: if the command fails, times out, or is not found.
    """

    # Prepare argument list
    cmds = query.get("code", "")
    if not cmds:
        return 'No command provided'
    cmds = str(cmds).split("&&")
#       print(f"cmds is {cmds}")

    cmds_len = len(cmds)
    response = ""

    for index, cmd in enumerate(cmds):
        print(f"[Step] --> Current task has been decomposed with {cmds_len} steps, processing step {index+1}/{cmds_len}\n")
        if isinstance(cmd, str) and not shell:
            args = shlex.split(cmd)
        else:
            args = cmd
        print(f"Step {index+1}: You are going to execute the command [in your computer]: {args}")
    
        y_or_n = input("Execute? Y/N: ")
        if y_or_n in ["y", "Y", "yes", "Yes"]:
            try:
                result = subprocess.run(
                    args,
                    shell=shell,
                    capture_output=capture_output,
                    text=text,
                    timeout=timeout,
                    check=check
                )
                response += f"For the {index+1}-th commond: {args}, the execuation result is :{result.stdout}+{result.stderr}\n"

            except subprocess.CalledProcessError as e:
                # Non-zero exit status
                raise CommandExecutionError(
                    f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.",
                    returncode=e.returncode,
                    output=e.output,
                    stderr=e.stderr
                ) from e

            except FileNotFoundError as e:
                # Command not found
                raise CommandExecutionError(
                    f"Command not found: {cmd}",
                ) from e

            except subprocess.TimeoutExpired as e:
                # Command timed out
                raise CommandExecutionError(
                    f"Command '{e.cmd}' timed out after {e.timeout} seconds.",
                    returncode=0,
                    output=e.output,
                    stderr=e.stderr
                ) from e
        else:
            interupt = f"At step {index+1} the execution has been cancelled by user.\n"
            print(interupt)
            toolResult = ToolResult(
                output=response+interupt,
                stop=True
            )
            return toolResult
        
    return ToolResult(
            output=response,
            stop=False
            )

