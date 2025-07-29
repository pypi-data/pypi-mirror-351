from pydantic_ai import Agent, RunContext, ModelRetry
from .state import AgentState, Task
from typing import List
from .llmodel import get_model
import textwrap


print((lambda s, w: s[:w].ljust(w))("[Agent]: User query decompose: ", 40), end="")
plan_agent = Agent(
    model=get_model("plan"),
    output_type=AgentState,
    deps_type=AgentState,
    output_retries=3,
    system_prompt="""
    You are a professional developer specializing in linux operation.
    Your task is to solve the user's query. Your task is to decompose
    the user query into smaller tasks.
    You will receive a user request, and your job is
    to understand it and break it down into smaller tasks. For each 
    task, you will generate a Task object that includes the task name,
    description, a done tag, the solution description and corresponding 
    Tool class. The solution field can be empty string and Tool class 
    can be None. The Task object should be structured as follows:
    {
        "name": str,
        "description": str,
        "done": bool,
        "solution": str,
        "tool": None
    }
    Process:
    1. Receive the user request.
    2. Decompose the request into smaller tasks.
    3. For each task, generate a Task object with the required fields.
    4. Use plan_context_compose function to append them in RunContext dependence.
    """
    )


@plan_agent.tool
def plan_context_compose(ctx: RunContext[AgentState], tasks: List[Task])-> AgentState:
    """ Compose the tasks and append them in RunContext dependence for the next step.
    Args:
        ctx (RunContext): The context of the current run.
        tasks (List[Task]): A list of Task objects generated from the user query.
    """
    for task in tasks:
        ctx.deps.tasks.append(task)

    return ctx.deps


@plan_agent.system_prompt
def plan_agent_prompt(ctx: RunContext[AgentState]) -> str:
    """ Generate the system prompt for the plan agent.
    Args:
        ctx (RunContext): The context of the current run.
    Returns:
        str: The system prompt for the plan agent.
    """
    return """You are an orchestrator agent. Your task is to decompose the
    user query into smaller tasks. You are going to generate the
    name and description of each task. You should make sure the descriptions 
    of tasks are relevant to the user query and aim to solve the problem."""


@plan_agent.output_validator
def plan_agent_validation(ctx: RunContext[AgentState], output: AgentState) -> AgentState:
    """ Validate the output of the orchestrator agent.
    Args:
        ctx (RunContext): The context of the current run.
        result (AgentState): The output of the orchestrator agent.
    Returns:
        AgentState: The validated output of the orchestrator agent.
    """
#    def plan_agent_node(state: AgentState) -> AgentState:
    # This function will be called to route the agent
#    print(f"To start the plan agent, we have input: {state.user_input}DONE\n")
    result = plan_agent.run_sync(state.user_input, deps=state)
    print("plan agent is done")
    return result.outputprint(f"We decompose the use query as following:\n")
    for task in output.tasks:
        print(f"Task Name  : {task.name}")
        print(f"Description: {textwrap.fill(task.description, 70, subsequent_indent=' '*13)}")
        print("-" * 60)

    if len(output.tasks) == 0:
        raise ModelRetry(
            """No tasks generated, please check the user query or reformulate it."""
            )
    return output

