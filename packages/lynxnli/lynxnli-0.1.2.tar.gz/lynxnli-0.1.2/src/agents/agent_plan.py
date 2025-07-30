# Import the agent state management system for tracking overall system state
from content.state import AgentState
# Import the base agent class that provides common functionality
from agents.agent import BaseAgent
# Import json module for parsing and generating JSON data structures
import json
# Import the Task data structure for representing individual tasks
from content.state import Task
# Import type hints for better code documentation
from typing import List


class PlanAgent(BaseAgent):
    """
    PlanAgent is responsible for the first phase of the Trinity system (Rashnu - Judgment of Truth).
    This agent takes user queries and decomposes them into structured, actionable tasks.
    
    The PlanAgent serves as the entry point for query processing, analyzing user input
    and breaking it down into smaller, manageable tasks that can be executed by other agents.
    It implements intelligent task decomposition and generates structured task objects.
    """
    
    def __init__(self, agent_name:str, llm_provider:str, llm_name:str):
        """
        Initialize the PlanAgent with specified configuration.
        
        Args:
            agent_name (str): Unique identifier for this agent instance
            llm_provider (str): The LLM provider to use (OpenAI, Ollama, GWDG, Synchange)
            llm_name (str): The specific model name within the chosen provider
        """
        print("[Plan Agent]: ", end="")
        # Call parent constructor to initialize base agent functionality
        super().__init__(agent_name, llm_provider, llm_name)
        
        # Test LLM connection to ensure the agent is ready for operation
        # This validates that the LLM can be reached and is properly configured
        self.llm.test_connection()

    def prompt(self, query:str, tool_dict:str) -> str:
        """
        Generate a specialized prompt for task decomposition.
        This method creates a detailed prompt that instructs the LLM to break down
        user queries into structured task objects.
        
        Args:
            query (str): The user's original query or request
            
        Returns:
            str: A formatted prompt for the LLM that includes context and instructions
        """
        # Define the problem context and role for the LLM
        problem = f"""You are a professional developer specializing in linux operation. You have already well configured the environment. Your job is to understand the user's query <{query}> and convert the query directly to task. If the query is too complex, break it down into smaller tasks sequentially. You have all available tools <{tool_dict}> for task as reference. Make sure to include all necessary details in the task description."""
        
        # Define the specific output format and processing instructions
        prompt = """You will generate a Task object in json that includes the task 
        name and a description with details. The object should be structured as follows:
        [{
            name: str,
            description: str
        }]
        Process:
        1. Receive the user request.
        2. Decompose the request into smaller tasks.
        3. For each task, generate a object with the required fields in json.
        4. ONLY return the json content, no other information are needed.
        5. Do not return it with markdown format, only return it as string."""
        
        # Combine problem context with formatting instructions
        return problem+prompt

    def validation(self, tasks:List[Task]) -> bool:
        """
        Validate that the generated tasks meet minimum requirements.
        This ensures that the task decomposition was successful and produced
        at least one actionable task.
        
        Args:
            tasks (List[Task]): List of generated task objects to validate
            
        Returns:
            bool: True if validation passes (at least one task), False otherwise
        """
        # Check if at least one task was generated
        if len(tasks) >= 1:
            return True
        else:
            return False

    def generate(self, query: str, tool_dict:str) -> List[Task]:
        """
        Generate a list of tasks from a user query.
        This is the main method that orchestrates the task decomposition process.
        It handles the complete workflow from prompt generation to task validation.
        
        Args:
            query (str): The user's original query or request
            
        Returns:
            List[Task]: A list of structured task objects ready for execution
        """
        # Generate the specialized prompt for task decomposition
        well_promput = self.prompt(query, tool_dict)
        
        # Send the prompt to the LLM and get the response
        tasks = self.llm.send_request(well_promput)
        
        # Parse the JSON response into Python data structures
        tasks = json.loads(tasks)

        # Validate that the task generation was successful
        if self.validation(tasks):
            # Initialize additional task fields for tracking execution state
            for task in tasks:
                task['done'] = False      # Track completion status
                task['solution'] = ""     # Store the solution when completed
            return tasks
        else:
            # If validation fails, recursively retry task generation
            # This ensures we always return valid tasks
            return self.generate(query)
