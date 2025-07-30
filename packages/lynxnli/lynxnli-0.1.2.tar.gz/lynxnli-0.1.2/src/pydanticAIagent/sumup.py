from pydantic_ai import Agent, RunContext
from .state import AgentState, Task
from .llmodel import get_model
from .tools_search import search_tool_agent
from pydantic_ai import ModelRetry
from .tools_perpare import perpare_tool_agent
from toolset.tool_registry import ToolRegistry
from .tools_evaluate import evaluate_tool_agent


print((lambda s, w: s[:w].ljust(w))("[Agent]: summary and evaluation", 40), end="")
sumup_agent = Agent(
    model=get_model("task"),
    deps_type=AgentState,
    output_type=AgentState,
    output_retries=1,
    prompt_template = "Please provide the result as short as possible."
    )
@sumup_agent.tool
def sumup_agent_tool(ctx: RunContext[AgentState], result: str) -> AgentState:
    print(f"The summary result is {result}\n")
    ctx.deps.result = result
    

# @sumup_agent.system_prompt
# def task_prompt(ctx :RunContext[Task]) -> str:
#     return f"""Given this task description: {ctx.prompt}, using the 
#     searching_tool function to find which one is most suitable tool 
#     and answer only with the tool name."""

# @sumup_agent.output_validator
# def sumup_agent_valid(ctx: RunContext[Task] ):
#     print(f"For Task: {ctx.deps.name},\nTag     : {ctx.deps.done},\n"+
#         f"Solution: {ctx.deps.solution}\n")



def sumup_agent_node(state: AgentState) -> AgentState:
    # print("------"*20)
    # print(state)
    # print("------"*20)

#           state.add_system_message(task.description)
        # state.add_llm_response(task.solution)
        # state.add_tool_result(task.tool["name"], task.tool["instructions"])

#    print(f"The SOLUTION is: {state.tasks[0].solution}, and user query is: {state.user_input}\n")

    result = sumup_agent.run_sync(
        f"""Summerise the solution from all tasks: {state.tasks}, assige it to 
         RunContext dependence AgentState class, and return it.""",
        deps=state
        )
    # print("RESULT OUTPUT\n")
    # print(result.output)

    return result.output

    