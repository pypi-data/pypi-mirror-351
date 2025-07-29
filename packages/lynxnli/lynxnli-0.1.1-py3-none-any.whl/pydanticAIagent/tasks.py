from pydantic_ai import Agent, RunContext
from .state import AgentState, Task
from .llmodel import get_model
from .tools_search import search_tool_agent
from pydantic_ai import ModelRetry
from .tools_perpare import perpare_tool_agent
from toolset.tool_registry import ToolRegistry
import json
from .tools_evaluate import evaluate_tool_agent


print((lambda s, w: s[:w].ljust(w))("[Agent]: Tasks processing : ", 40), end="")
tasks_agent = Agent(
    model=get_model("task"),
    deps_type=Task,
    output_type=Task,
    output_retries=1,
    prompt_template="""you are a linux expert,  will receive a task 
    description and call searching_tool function to choose the best 
    tool for the given task."""
    )

@tasks_agent.system_prompt
def task_prompt(ctx :RunContext[Task]) -> str:
    return f"""Given this task description: {ctx.prompt}, using the 
    searching_tool function to find which one is most suitable tool 
    and answer only with the tool name."""


@tasks_agent.tool
def searching_tool(ctx :RunContext[Task]):
    """ This function will be called to execute the task
    Args:
        command (str): The command to be executed.
    Returns:
        str: The result of the command execution.
    """
    tools_registry = ToolRegistry.get_tool_registry()
    get_tool = search_tool_agent.run_sync(ctx.deps.description, deps=tools_registry)
    tool_name = get_tool.output["name"]
    tool_instructions = get_tool.output["instructions"]
    ctx.deps.tool = get_tool.output

    tool_config = tools_registry.get(tool_name, {})
    required_inputs = tool_config.get('required_inputs', [])
    conversion_prompt = (
        f"Please convert the following prompt to required format.\n"
        f"Prompt: {ctx.deps.description}\n"
        f"instructions: {tool_instructions}\n"
        f"Example answer: {{\"{required_inputs[0]}\": \"...\"}}"
        )
#    print(f"The prompt of generate input is : {conversion_prompt}!!\n")
    required_inputs = perpare_tool_agent.run_sync(conversion_prompt)
    expression = json.loads(required_inputs.output)

#    print(f"The required intput is    : {expression}!\n")
    tool = tools_registry[tool_name]['executor']
    if tool_name == "terminalCommand":
        print(f"Tool is going to execute the this: {expression["code"]}")
        y_or_n = input("Execute? Y/N: ")
        if y_or_n in ["y", "Y"]:
            output = tool(expression)
        else:
            print("Tool execution cancelled by user.")
    else:
        output = tool(expression)
#    print(f"the exeuction of tool has result: {output}!\n")

    done = evaluate_tool_agent.run_sync(
                f"""We got the output of current task: {output}.""",
                deps=ctx.deps
        )
    ctx.deps.solution = done.output["solution"]
    ctx.deps.done = (done.output["done"] == "True")


def tasks_agent_node(state: AgentState) -> AgentState:
    """ This function will be called to route the agent
    Args:
        state (AgentState): The current state of the agent.
    Returns:
        AgentState: The updated state of the agent and return.
    """
#    print(f"{len(state.tasks)} tasks have been passed to task agent!!\n")
    for task in state.tasks:
        result = tasks_agent.run_sync(
                f"""try to solve the task {task.name} with the 
                description: {task.description}, and assign the 
                result to {task.solution}""",
                deps=task
        )
#           print(result)
        # state.add_user_input(state.user_input)
        # state.add_llm_response(result.output["solution"])
        # state.add_system_message()

    return state

    