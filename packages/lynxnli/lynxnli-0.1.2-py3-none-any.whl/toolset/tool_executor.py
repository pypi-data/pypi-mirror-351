import os
import time
import xml.etree.ElementTree as ET
from toolset.tool_registry import ToolRegistry
from typing import Dict

class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry.get_tool_registry()
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_tool_dict(self)-> Dict:
        return {name:self.registry[name].get("instructions", '') for name in self.registry}

    def get_tool_description(self, query) -> str:
        knowledge = "\n".join([f"Tool: {name}\nInstructions: {self.registry[name].get('instructions', '')}\n"
                    for name in self.registry
                ])
        request = (
            f"Given the following user request:\n" 
            f"{query}\n\n"
            f"Which of the following tools is most suitable? return its name and instructions.\n"
            )
        tool_querying = (
            "knowledge: " + knowledge + "\n\n"
            "Request: " + request + "\n\n"
            "Provide only a concise final answer with the tool's name and tool's instructions for Tool class"
            "Do not include any internal processing details or meta commentary."
        )
        return tool_querying


    def save_tool_output_xml(self, tool_name: str, result: str, is_file: bool = False) -> str:
        root = ET.Element("tool_output")
        ET.SubElement(root, "tool_name").text = tool_name

        if is_file:
            ET.SubElement(root, "generated_file").text = result
        else:
            ET.SubElement(root, "result").text = result

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        xml_path = os.path.join(self.output_dir, f"{tool_name}_{timestamp}.xml")
        ET.ElementTree(root).write(xml_path, encoding="utf-8", xml_declaration=True)
        return xml_path

