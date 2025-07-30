import sys
import json
import io
import contextlib
import re
from content.state import ToolResult

def run(input_data):
    """
    Executes Python code provided either as a dict (with key "code")
    or as a raw string. It uses a regular expression to capture the code
    after the keyword "code:" or "code=" (case-insensitive).
    """
    if isinstance(input_data, dict):
        code = input_data.get("code", "")
    elif isinstance(input_data, str):
        # Use a regex to capture the code after "code:" or "code="
        match = re.search(r"code\s*[:=]\s*(.+)", input_data, re.IGNORECASE)
        if match:
            code = match.group(1).strip()
        else:
            # If the keyword is not found, assume the entire input is the code.
            code = input_data.strip()
    else:
        code = ""
    
    # (Optional) Debug: Uncomment the following line to print the extracted code.
    # print("Extracted code:", repr(code))
    
    # Capture printed output during code execution.
    output_stream = io.StringIO()
    with contextlib.redirect_stdout(output_stream):
        try:
            exec(code, {})
        except Exception as e:
            # Return error message in a consistent format.
            return f"Execution error: {str(e)}"
        
    return ToolResult(
        output=output_stream.getvalue(),
        stop=False
    )
#       return output_stream.getvalue()

if __name__ == "__main__":
    # Try to parse input as JSON; if that fails, treat it as a raw string.
    try:
        input_data = json.loads(sys.argv[1])
    except Exception:
        input_data = sys.argv[1]
    result = run(input_data)
    print(result)
    # print("input was ", input_data, "output is ", result)
