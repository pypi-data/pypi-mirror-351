import math
from content.state import ToolResult

def run(inputs) -> ToolResult:
    try:
        expr = inputs.get("expression", "")
        result = eval(expr, {"__builtins__": None}, math.__dict__)
        return ToolResult(
            output=f"The result is {result}",
            stop=False
        )
    except Exception as e:
        return ToolResult(
            output=f"Error evaluating expression: {e}",
            stop=False
        )
    
    
