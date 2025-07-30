from typing import List, TypedDict
from .content_manager import ContextManager
from toolset.tool_executor import ToolExecutor

class ToolResult(TypedDict):
    output: str
    stop: bool = False
    

class Task(TypedDict):
    """Represents a single task in the agent's workflow.
    
    Attributes:
        name (str): The name/title of the task
        description (str): Detailed description of what the task entails
        done (bool): Flag indicating if the task is completed (default: False)
        solution (str): The solution or result of the completed task (default: empty string)
    """
    name: str
    description: str
    done: bool = False
    solution: str = ""
    

class AgentState(TypedDict):
    """Represents the current state of an agent's execution.
    
    Attributes:
        user_input (str): The original input/request from the user
        name (str): Name identifier for this state instance (default: empty string)
        complete (bool): Flag indicating if all tasks are completed (default: False)
        tasks (List[Task]): List of tasks to be performed (default: empty list)
        result (str): Final result/output of all tasks (default: empty string)
        context (ContextManager): Manages conversation history and context (default: empty list)
    """
    user_input: str
    name: str = ""
    complete: bool = False
    tasks: List[Task] = []
    result: str = ""
    context: ContextManager = []
    tool_executor: ToolExecutor
