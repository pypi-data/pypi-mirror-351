from content.state import ToolResult

def run(prompt) -> ToolResult:
    text = prompt.split(":", 1)[-1].strip()
    return ToolResult(
        output=f"The length of the input string is {len(text)}",
        stop=False
    )
    
