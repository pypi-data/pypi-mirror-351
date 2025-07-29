import os
from content.state import AgentState
from agents.agent_plan import PlanAgent
from agents.agent_tasks import TasksAgent
from agents.agent_sumup import SumupAgent
from content.content_manager import ContextManager
from toolset.tool_executor import ToolExecutor
import textwrap



class TriadOfWises:
    def __init__(self, max_cycles=2):
        self.max_cycles = max_cycles
        self.agentState = AgentState(
            user_input = "",
            name = "",
            complete = False,
            tasks = [],
            result = "",
            context = ContextManager(),
            tool_executor = ToolExecutor())
        
        self.plan_agent = PlanAgent(
                            "plan", 
                            os.getenv("AGENT_LLM_PROVIDER", "OpenAI"),
                            os.getenv("AGENT_LLM_MODEL", "gpt-4o-mini")
                    )
        self.tasks_agent = TasksAgent(
                            "tasks", 
                            os.getenv("AGENT_LLM_PROVIDER", "OpenAI"),
                            os.getenv("AGENT_LLM_MODEL", "gpt-4o-mini")
                            )
        self.sumup_agent = SumupAgent(
                            "sumup", 
                            os.getenv("AGENT_LLM_PROVIDER", "OpenAI"),
                            os.getenv("AGENT_LLM_MODEL", "gpt-4o-mini")
                            )
        
    def run(self, user_input) -> AgentState:
        self.agentState["user_input"] = user_input
        self.agentState["context"].add_user_input(self.agentState["user_input"])

        cycle = 0
        while cycle < self.max_cycles:
            plan_tasks = self.plan_agent.generate(
                self.agentState["user_input"],
                str(self.agentState["tool_executor"].get_tool_dict())
                )
            self.agentState["tasks"] = plan_tasks

            self.agentState = self.tasks_agent.generate(self.agentState)

            self.agentState = self.sumup_agent.generate(self.agentState)

            if  self.agentState["complete"]:
                print("[Query result]:\n")
                print(textwrap.fill(self.agentState['result'], width=80, initial_indent=' '*15, subsequent_indent=' '*15))
                self.agentState["context"].add_query_context(
                    self.agentState["user_input"],
                    self.agentState["result"]
                )
                return self.agentState
            else:
                self.agentState["user_input"] += (".\nTo solve this query again with result from last time: "+self.agentState["result"])
                print(f"[Cycle {cycle}] failed: re-running with updated input as: ")
                print(textwrap.fill(self.agentState['user_input'], width=80, initial_indent=' '*15, subsequent_indent=' '*15))
                cycle += 1


        print("Max cycles reached without completion.")
        self.agentState["context"].add_query_context(
            self.agentState["user_input"],
            self.agentState["result"]
        )
        return self.agentState