# --- toolset/tool_invocation_parser.py ---
import ast
import re
from typing import Tuple, Dict, Optional

class ToolInvocationParser:
    @staticmethod
    def contains_tool_call(text: str) -> bool:
        return bool(re.search(r'\b\w+\s*\(.*?\)', text)) or "<tool" in text

    @staticmethod
    def parse_tool_call(text: str) -> Tuple[str, Dict[Optional[str], Optional[str]]]:
        # Step 1: Strip surrounding quotes
        text = text.strip()
        if text.startswith(("'", '"')) and text.endswith(("'", '"')):
            text = text[1:-1]

        # Step 2: XML-style tool call
        xml_match = re.search(r'<tool name="(.+?)">(.*?)</tool>', text, re.DOTALL)
        if xml_match:
            tool_name = xml_match.group(1).strip()
            import json
            args = json.loads(xml_match.group(2).strip())
            return tool_name, args

        # Step 3: Function-style tool call (with optional assignment)
        match = re.search(r'(?:(\w+)\s*=\s*)?(\w+)\s*\((.*?)\)', text.strip(), re.DOTALL)
        if not match:
            raise ValueError("No valid tool call found.")

        tool_name = match.group(2).strip()
        arg_string = match.group(3).strip()

        # Load tool definition
        from toolset.tool_registry import ToolRegistry
        from toolset.tool_init_loader import IniToolLoader

        loader = IniToolLoader("tools")
        registry = ToolRegistry(loader)
        registry.load()
        tool = registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        # Step 4: Fix common quote errors in arg_string
        quote_count = arg_string.count("'") + arg_string.count('"')
        if quote_count % 2 != 0:
            # Attempt to close the quote if it's obviously missing
            arg_string += "'" if arg_string.count("'") % 2 != 0 else '"'

        # Step 5: Try to parse safely
        try:
            dummy_func = f"f({arg_string})"
            tree = ast.parse(dummy_func, mode='eval')
            call = tree.body  # ast.Call

            named_args = {}
            if isinstance(call, ast.Call):
                if call.keywords:
                    named_args = {
                        kw.arg: ast.literal_eval(kw.value)
                        for kw in call.keywords
                    }
                else:
                    positional_args = [ast.literal_eval(arg) for arg in call.args]
                    named_args = dict(zip(tool.inputs, positional_args))
                return tool_name, named_args
            else:
                raise TypeError("Parsed expression is not a function call (ast.Call)")
        except SyntaxError as e:
            raise ValueError(f"Syntax error parsing arguments: check quotes and format -> {e}")
        except Exception as e:
            raise ValueError(f"Error parsing arguments safely: {e}")
