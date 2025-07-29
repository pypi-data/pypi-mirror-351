# --- llm_context_manager.py ---
from typing import List, Dict

class ContextManager:
    """Manages the conversation context and history between different actors in the system.
    
    This class provides methods to track and maintain the conversation flow between
    users, the system, assistants, and tools.
    """
    
    def __init__(self):
        """Initialize an empty context list to store conversation history."""
        self.context: List[Dict[str, str]] = []

    def add_user_input(self, message: str):
        """Add a user message to the context.
        
        Args:
            message (str): The user's input message
        """
        self.context.append({"role": "user", "content": message})


    def add_task_context(self, task_description: str, solution: str):
        """Add a user message to the context.
        
        Args:
            message (str): The user's input message
        """
        self.context.append({
            "role": "task", 
            "task_description": task_description,
            "solution": solution
            })
        
    
    def get_task_context(self) -> str:
        """Get a summary of task descriptions and solutions from the context."""
        task_update = ""
        for entry in self.context:
            if entry["role"] == "task":
                task_update += f"Task: {entry['task_description']}\nSolution: {entry['solution']}\n"
        return task_update.strip()
    
    def reset_task_context(self):
        """Reset the task context by clearing the task-related entries."""
        self.context = [entry for entry in self.context if  entry["role"] != "task"]


    def add_query_context(self, input: str, result: str):
        """Add a system message to the context.
        
        Args:
            message (str): The system's message
        """
        self.context.append({
            "role": "query",
            "input": input,
            "content": result
            })
        
    def get_query_context(self) -> str:
        """Get a summary of query inputs and results from the context."""
        query_update = ""
        for entry in self.context:
            if entry["role"] == "query":
                query_update += f"Input: {entry['input']}\nResult: {entry['content']}\n"
        return query_update.strip()


    def add_tool_result(self, tool_name: str, output: str):
        """Add a tool's execution result to the context.
        
        Args:
            tool_name (str): Name of the tool that generated the output
            output (str): The tool's execution result
        """
        self.context.append({
            "role": "tool_result",
            "tool_name": tool_name,
            "output": output
        })

    def get_context(self) -> List[Dict[str, str]]:
        """Retrieve the raw context history.
        
        Returns:
            List[Dict[str, str]]: The complete conversation history
        """
        return self.context

    
    def get_full_context(self):
        """Get the context history in a simplified format.
        
        Returns:
            List[Dict]: List of dictionaries containing prompts and their inputs
        """
        return [{'prompt': msg.get('content', ''), 'inputs': {}} for msg in self.context]

