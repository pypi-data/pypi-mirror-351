from pydantic_ai import Agent, RunContext
from .llmodel import get_model
from toolset.tool_registry import ToolRegistry
from typing import Dict
from .state import Tool


print((lambda s, w: s[:w].ljust(w))("[Tasks]: tool matching", 40), end="")
search_tool_agent = Agent(
    model=get_model("tool"),
    output_retries=2,
    output_type=Tool,
    deps_type=Dict[str, dict],
    prompt_template="""You are a LLM agent. You will receive a description 
    of the given task. Your job is find the best suiable tool from all possible tools,
    and give the name and instructions of the best choices back. 
    """
    )

@search_tool_agent.system_prompt
def task_prompt(ctx :RunContext[Dict[str, dict]]) -> str:
    tools = ctx.deps
    knowledge = "\n".join([f"Tool: {name}\nInstructions: {tools[name].get('instructions', '')}\n"
                    for name in tools
                ])
    query = (
            f"Given the following user request:\n" 
            f"{ctx.prompt}\n\n"
            f"Which of the following tools is most suitable? return its name and instructions.\n\n{knowledge}"
            )
    full_prompt = (
            "knowledge: " + knowledge + "\n\n"
            "Input: " + query + "\n\n"
            "Provide only a concise final answer with the tool's name and tool's instructions"
            "with Tool class."
            "Do not include any internal processing details or meta commentary."
        )
#    print(f"Tool name search prompt is: {full_prompt}\n")
    return full_prompt