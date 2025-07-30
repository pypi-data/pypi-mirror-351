import os
import uuid
from content.state import ToolResult
from toolset.tool_setup import FILES_DIR


def run(inputs) -> ToolResult:
    if not os.path.isdir(FILES_DIR):
        raise FileNotFoundError(f"Directory not found: {FILES_DIR}")

    code = inputs.get("gen")
    id = uuid.uuid4().hex
    file_name = FILES_DIR+"/"+ id+".py"

    with open(file_name, "w") as file:
        file.write(code)

    result =  f"Code has been generated at :{file_name}\n"
    print(result)
    return ToolResult(
        output=result,
        stop=False
    )
