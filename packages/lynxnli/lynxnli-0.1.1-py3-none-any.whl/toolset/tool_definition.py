# --- toolset/tool_definition.py ---
import importlib

class ToolDefinition:
    def __init__(self, name, address, inputs, outputs, instructions, extraction=None):
        self.name = name
        self.address = address  # e.g., 'mathTool.mathTool:run'
        self.inputs = inputs
        self.outputs = outputs
        self.instructions = instructions
        self.extraction = extraction or {}  # Store extraction patterns here
        self.run = self.load_run_function()

    def load_run_function(self):
        try:
            module_path, func_name = self.address.split(":")
            module = importlib.import_module(f"toolset.tools.{module_path}")
            return getattr(module, func_name)
        except Exception as e:
            print(f"Error loading run function for tool {self.name}: {e}")
            return lambda prompt: f"[Error: tool '{self.name}' failed to load]"
