import os
import uuid
from importlib.resources import files
from content.state import ToolResult

tool_genCode_path = os.getenv("tool_genCode_path")
path = str(files("toolset").joinpath(tool_genCode_path))


def run(inputs):
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Directory not found: {path}")

    code = inputs.get("gen")
    id = uuid.uuid4().hex
    file_name = path+"/"+ id+".py"

    with open(file_name, "w") as file:
        file.write(code)

    result =  f"Code has been generated at :{file_name}\n"
    print(result)
    return ToolResult(
        output=result,
        stop=False
    )
