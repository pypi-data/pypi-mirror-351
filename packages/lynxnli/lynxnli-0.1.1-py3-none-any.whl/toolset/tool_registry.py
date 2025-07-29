# --- toolset/tool_registry.py ---
from typing import Dict
from toolset.tool_definition import ToolDefinition
from toolset.tool_init_loader import IniToolLoader
from typing import Optional
import os

class ToolRegistry:
    def __init__(self, tool_loader: IniToolLoader):
        self.tool_loader = tool_loader
        self.tools: Dict[str, ToolDefinition] = {}

    def load(self):
        for tool in self.tool_loader.load_all_tools():
            self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self.tools.get(name)

    def list_tools(self) -> Dict[str, ToolDefinition]:
        return self.tools

    def format_for_llm(self) -> str:
        return "\n".join([
            f"- {tool.name}: {tool.instructions} (inputs: {', '.join(tool.inputs)}, outputs: {', '.join(tool.outputs)})"
            for tool in self.tools.values()
        ])

    # --- NEW FUNCTION FOR TRIAD INTEGRATION ---

    @classmethod
    def get_tool_registry(cls) -> Dict[str, dict]:
        """
        Returns a dictionary of tools in the format expected by TriadOfWises.
        """
        path = "tools"
        loader = IniToolLoader(path)
        registry = ToolRegistry(loader)
        registry.load()

        triadic_format = {}
        for name, tool in registry.list_tools().items():
            triadic_format[name] = {
                'matcher': lambda prompt, toolname=name: toolname.lower() in prompt.lower(),
                'required_inputs': tool.inputs,
                'extraction': tool.extraction,  # include extraction patterns
                'instructions': tool.instructions,
                'executor': lambda prompt, tool_instance=tool: tool_instance.run(prompt),
                'interpreter': (lambda n: lambda output: f"Tool '{n}' produced: {output}")(name)
            }
        return triadic_format
