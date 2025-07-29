from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .plan import plan_agent_node
from .tasks import tasks_agent_node
from .sumup import sumup_agent_node
from .router import router_agent
from tenacity import retry, stop_after_attempt, wait_fixed

# Custom StateGraph with retries
class RetryStateGraph(StateGraph):
    def add_node(self, key: str, action, **kwargs):
        @retry(stop=stop_after_attempt(8), wait=wait_fixed(4))
        def retry_action(*args, **kwargs):
            return action(*args, **kwargs)
        super().add_node(key, retry_action, **kwargs)


def build_agent_flow():
    builder = RetryStateGraph(AgentState)
#    builder = StateGraph(AgentState)
    builder.add_node("plan_agent", plan_agent_node)
    builder.add_node("tasks_agent", tasks_agent_node)
    builder.add_node("sumup_agent", sumup_agent_node)
    
    builder.add_edge(START, "plan_agent")
    builder.add_edge("plan_agent", "tasks_agent")
    builder.add_edge("tasks_agent", "sumup_agent")
    builder.add_conditional_edges(
        "sumup_agent",
        path=router_agent,
        path_map= {"True": END, "False": "plan_agent"}
        )

    #builder.add_edge("tasks_agent", END)
    #memory = MemorySaver()
    agent_flow = builder.compile()
    return agent_flow