# Import the base agent class that provides common functionality
from agents.agent import BaseAgent
# Import the Task data structure for representing individual tasks
from content.state import Task
# Import json module for parsing and generating JSON data structures
import json
# Import the ToolExecutor for managing and executing available tools
from content.state import AgentState
from content.state import ToolResult



class TasksAgent(BaseAgent):
    """
    TasksAgent is responsible for the second phase of the Trinity system (Mithra - Judge of Oaths).
    This agent takes individual tasks and executes them using the appropriate tools from the toolset.
    
    The TasksAgent serves as the execution engine of the Trinity workflow, matching tasks to tools,
    generating proper inputs for tool execution, and validating the results. It implements intelligent
    tool selection and handles the complete task execution lifecycle.
    """
    
    def __init__(self, agent_name:str, llm_provider:str, llm_name:str):
        """
        Initialize the TasksAgent with specified configuration.
        
        Args:
            agent_name (str): Unique identifier for this agent instance
            llm_provider (str): The LLM provider to use (OpenAI, Ollama, GWDG, Synchange)
            llm_name (str): The specific model name within the chosen provider
        """
        print("[Task Agent]: ", end="")
        # Call parent constructor to initialize base agent functionality
        super().__init__(agent_name, llm_provider, llm_name)
        
        # Test LLM connection to ensure the agent is ready for operation
        # This validates that the LLM can be reached and is properly configured
        self.llm.test_connection()


    def prompt(self, query:str) -> str:
        """
        Generate a specialized prompt for tool selection.
        This method creates a prompt that instructs the LLM to identify the most
        suitable tool for executing a given task.
        
        Args:
            query (str): The task description or tool description to analyze
            
        Returns:
            str: A formatted prompt for the LLM requesting tool selection
        """
        # Create a prompt that positions the LLM as a tool-matching agent
        prompt =  f"""You are a LLM agent. You receive this request for this task: {query}. Your job is to find the most suiable tool from all possible tools and give the name and instructions of the best tool back as a Tool object. {self.base_prompt}"""

        # Define the expected output format for tool selection
        format = """Your returned Tool object should be structured as follows:
        {
            "name": str,
            "description": str,
        }"""

        # Combine the prompt with format specifications
        return prompt+format

    def validation(self, task:Task) -> bool:
        """
        Validate that a task has been completed successfully.
        This method uses the LLM to evaluate whether the task solution
        adequately addresses the original task description.
        
        Args:
            task (Task): The task object containing description and solution
            
        Returns:
            bool: True if the task is considered complete and correct, False otherwise
        """
        # Create a validation prompt that asks the LLM to evaluate task completion
        prompt = f"""Check the solution <{task['solution']}> of task <{task['name']}>. Only return `False` if this solution contains error massage, otherwise return `True`. Your estimation should only based on the literally description of solution, no need to check the content of related files. Please ONLY return `True` or `False` as the result, no other information are needed."""
        
        # Send the validation prompt to the LLM
        eval = self.llm.send_request(prompt)
#           print(f"Task validation prompt: {prompt}... The Result is: {eval}\n ")

        if eval == "True":
            return True
        else:
            return False
        

    def generate(self, agentState: AgentState) -> AgentState:
        for index, task in enumerate(agentState["tasks"]): 
            print(f"[TASK] -->  Decomposing query into {len(agentState["tasks"])} tasks, processing task {index + 1}/{len(agentState['tasks'])}: {task['name']}\n")               
            # Get tool descriptions to help with tool selection
            tool_description = agentState["tool_executor"].get_tool_description(task["description"])

            # Use LLM to select the most appropriate tool for this task
            tool = self.llm.send_request(self.prompt(tool_description))
            
#            print(f"The prompt is {self.prompt(tool_description)}\n" )
            # Parse the JSON response to get tool information
            tool = json.loads(tool)
#            print(f"[Tool name for TASK] -->  Selected tool: {tool['name']} for task.\n")

            # Check if the selected tool actually exists in the tool registry
            if tool["name"] not in agentState["tool_executor"].get_tool_dict():
                # If tool doesn't exist, mark task as incomplete and return
                mark = f"Not tool has been found for {task['description']}, new attempt is going on."
                print(mark)
                task["solution"] = mark
                task["done"] = False
                return task
            
            # Uncomment the following line for debugging tool selection
#               print(f"Used tool is {tool["name"]}\n")

            # Generate the proper input format for the selected tool
            # Get tool configuration to understand required inputs
            tool_config = agentState["tool_executor"].registry.get(tool["name"], {})
            required_inputs = tool_config.get('required_inputs', [])
            
            # Create a prompt to convert task description to tool input format
            conversion_prompt = (
                f"Please convert the following prompt to required format.\n"
                f"Instructions: {task["description"]}\n"
                f"Description: {tool["description"]}\n"
                f"Pervious task context: {agentState['context'].get_task_context()}\n"
                f"Answer with format: {{\"{required_inputs[0]}\": \"...\"}}"
                "Please only return the content with valided json format, no mark around it needed."
                )
            
            # Generate the tool input using the LLM
            expression = self.llm.send_request(conversion_prompt)
            
            # Parse the generated input as JSON
            expression = json.loads(expression)
            
            # Get the tool executor function and execute it with the generated input
            executor = agentState["tool_executor"].registry[tool["name"]]['executor']
#            print(f"[TASK] -->  Executing tool: {tool['name']} with input: {expression}\n")

            toolResult: ToolResult = executor(expression)
            task["solution"] = toolResult["output"]
            agentState["context"].add_task_context(task["description"], task["solution"])

            if toolResult["stop"]:
                task["done"] = True
                print(f"Process has been stopped at the step of [{task['name']}].\n")
                return agentState
#                   break

            task["done"] = self.validation(task)
#           print(f"[TASK] -->  Tool: {tool['name']} executed with output: {output}, and validation result: {task['done']}\n")
            
        return agentState