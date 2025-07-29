from .llmodel import get_model
from pydantic_ai import Agent


print((lambda s, w: s[:w].ljust(w))("[Tasks]: solution generation: ", 40), end="")
perpare_tool_agent = Agent(
    model=get_model("tool"),
    output_retries=2,
    output_type=str,
    prompt_template="""You are a Linux expert. You will return the required string back based on 
    gived prompt."""
    )
