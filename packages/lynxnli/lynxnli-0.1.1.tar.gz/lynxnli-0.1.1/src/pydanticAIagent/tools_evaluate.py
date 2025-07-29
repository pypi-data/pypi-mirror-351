from pydantic_ai import Agent, RunContext
from .state import AgentState, Task, Evaluation
from .llmodel import get_model

print((lambda s, w: s[:w].ljust(w))("[Tasks]: result examintion: ", 40), end="")
evaluate_tool_agent = Agent(
    model=get_model("evaluate"),
    deps_type=Task,
    output_type=Evaluation,
    output_retries=2,
    prompt_template="""Please summarise the task output and return Evaluation class back."""
    )

@evaluate_tool_agent.system_prompt
def evaluation_prompt(ctx: RunContext[Task]) -> str:
    prompt = f"""Given this task [{ctx.deps.name}] with description 
    [{ctx.deps.description}], Please summarize the output as solution 
    for Evaluation class. Please make your solution precisely.
    If is there a execution failure in the output contained, 
    assign False to the done field of Evaluation class to return. Otherwise,
    once the output answered the question in current task, assign True 
    to the done field for Evaluation class. Return Evaluation class at end"""
    return prompt


# @evaluate_tool_agent.output_validator
# def evaluation_tool(ctx: RunContext[Task], done: str ) -> str:
#     """ This function will be called to execute the task"""
#     ctx.deps.done = (done=="True")
# #    print(f"the evaluation value is {done}\n")
#     return done

# @evaluate_tool_agent.output_validator
# def evaluation_output_validator(ctx: RunContext[Task], output: AgentState):
#     print(f"For Task: {ctx.deps.name},\nTag     : {ctx.deps.done},\n"+
#           f"Solution: {ctx.deps.solution}\n")
#     return output


