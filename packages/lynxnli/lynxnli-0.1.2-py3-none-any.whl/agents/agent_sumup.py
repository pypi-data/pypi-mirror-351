# Import the agent state management system for tracking overall system state
from content.state import AgentState
# Import the base agent class that provides common functionality
from agents.agent import BaseAgent
# Import the Task data structure for representing individual tasks
from content.state import Task

class SumupAgent(BaseAgent):
    """
    SumupAgent is responsible for the third phase of the Trinity system (Sraosha - Divine Listener).
    This agent interprets and summarizes the outputs from all completed tasks into a coherent,
    human-readable response.
    
    The SumupAgent serves as the final step in the Trinity workflow, taking all task solutions
    and creating a comprehensive summary that addresses the original user query. It also
    manages the completion state of the entire agent system.
    """
    
    def __init__(self, agent_name:str, llm_provider:str, llm_name:str):
        """
        Initialize the SumupAgent with specified configuration.
        
        Args:
            agent_name (str): Unique identifier for this agent instance
            llm_provider (str): The LLM provider to use (OpenAI, Ollama, GWDG, Synchange)
            llm_name (str): The specific model name within the chosen provider
        """
        print("[Eval Agent]: ", end="")
        # Call parent constructor to initialize base agent functionality
        super().__init__(agent_name, llm_provider, llm_name)
        
        # Test LLM connection to ensure the agent is ready for operation
        # This validates that the LLM can be reached and is properly configured
        self.llm.test_connection()
        
    def prompt(self, tasks: Task) -> str:
        """
        Generate a specialized prompt for summarizing task solutions.
        This method creates a prompt that instructs the LLM to synthesize
        all task solutions into a concise, coherent summary.
        
        Args:
            task (Task): The task object containing solutions to summarize
            
        Returns:
            str: A formatted prompt for the LLM requesting summary generation
        """
        # Extract all solutions from the task list
        # Each solution represents the output from a completed task
        solutions = [""+ task["solution"] for task in tasks]
        
        # Create a prompt that requests concise summarization
        summary = f"""Summerise the solution from all tasks: {solutions}, 
        please make your summary precisely and as short as possible and return"""

        return summary

    def validation(self, result:str) -> bool:
        """
        Base validation method for summary results.
        Currently not implemented but provides interface for future validation logic.
        
        Args:
            result (str): The generated summary to validate
            
        Returns:
            bool: Validation result (currently not implemented)
        """
        pass

    def generate(self, agentState: AgentState):
        """
        Generate a final summary from all completed tasks and update the agent state.
        This is the main method that orchestrates the summarization process and
        determines the overall completion status of the system.
        
        Args:
            agentState (AgentState): The current state of the agent system containing all tasks
            
        Returns:
            AgentState: Updated agent state with completion status and final result
        """
        # Check if all tasks are completed by evaluating their 'done' status
        # Uses list comprehension with logical AND to ensure all tasks are done
        done = all([ eval["done"] for eval in agentState["tasks"]])
        
        # Update the overall completion status of the agent state
        # This indicates whether the entire workflow has been completed
        agentState["complete"] = done
        
        # Generate the final summary by sending the prompt to the LLM
        result = self.llm.send_request(self.prompt(agentState["tasks"]))
        
        # Store the generated summary as the final result
        agentState["result"] = result
        
        # Return the updated agent state with completion status and result
        return agentState
        