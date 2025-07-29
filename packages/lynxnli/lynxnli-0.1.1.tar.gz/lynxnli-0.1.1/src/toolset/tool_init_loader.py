# --- toolset/ini_tool_loader.py ---
import os
import configparser
from typing import List
from toolset.tool_definition import ToolDefinition
from importlib.resources import files

class IniToolLoader:
    def __init__(self, directory_path: str):
        self.directory_path = str(files("toolset").joinpath(directory_path))

    def load_all_tools(self) -> List[ToolDefinition]:
        tool_definitions = []
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".ini"):
                config = configparser.ConfigParser()
                config.read(os.path.join(self.directory_path, filename))

                try:
                    # Build an extraction dictionary from keys starting with "extraction."
                    extraction = {}
                    for key in config["tool"]:
                        if key.startswith("extraction."):
                            extraction_key = key.split(".", 1)[1]
                            extraction[extraction_key] = config["tool"][key]

                    tool = ToolDefinition(
                        name=config.get("tool", "name"),
                        address=config.get("tool", "address"),
                        inputs=[x.strip() for x in config.get("tool", "inputs").split(",")],
                        outputs=[x.strip() for x in config.get("tool", "outputs").split(",")],
                        instructions=config.get("tool", "instructions"),
                        extraction=extraction  # pass the extraction dictionary here
                    )
                    tool_definitions.append(tool)
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        return tool_definitions
