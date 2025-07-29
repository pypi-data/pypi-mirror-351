from dataclasses import dataclass
from typing import List, TypedDict, Dict
from pydantic import BaseModel
from .content import ContextManager

class Tool(TypedDict):
    name:str
    instructions: str

class Evaluation(TypedDict):
    solution: str
    done:str

class Task(BaseModel):
    name: str
    description: str
    done: bool = False
    solution: str = ""
    tool: Tool

class AgentState(BaseModel):
    user_input: str
    name: str = ""
    tasks: List[Task] = []
    result: str = ""
    context: List[Dict[str, str]] = []
