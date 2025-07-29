# --- llm_context_manager.py ---
from typing import List, Dict

class ContextManager:
    def __init__(self):
        self.context: List[Dict[str, str]] = []

    def add_user_input(self, message: str):
        self.context.append({"role": "user", "content": message})

    def add_system_message(self, message: str):
        self.context.append({"role": "system", "content": message})

    def add_llm_response(self, message: str):
        self.context.append({"role": "assistant", "content": message})

    def add_tool_result(self, tool_name: str, output: str):
        self.context.append({
            "role": "tool_result",
            "tool_name": tool_name,
            "output": output
        })

    def get_context(self) -> List[Dict[str, str]]:
        return self.context
    
    def get_full_context(self):
        return [{'prompt': msg.get('content', ''), 'inputs': {}} for msg in self.context]


    def _format_chat_context(self, context: List[Dict[str, str]]) -> str:
        formatted = []
        for entry in context:
            if "role" in entry:
                if entry["role"] == "tool_result":
                    formatted.append(f"[Tool {entry.get('tool_name', 'unknown')}]: {entry.get('output', '')}")
                else:
                    formatted.append(f"[{entry['role'].capitalize()}]: {entry.get('content', '')}")
            elif "prompt" in entry and "output" in entry:
                formatted.append(f"[Prompt]: {entry['prompt']}\n[Tool Output]: {entry['output']}")
            elif "prompt" in entry:
                formatted.append(f"[Prompt]: {entry['prompt']}")
        return "\n".join(formatted)