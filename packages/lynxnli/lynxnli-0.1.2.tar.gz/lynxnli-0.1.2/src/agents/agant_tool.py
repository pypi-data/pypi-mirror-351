# Import the base agent class that provides common functionality for all agents
from agents.agent import BaseAgent
# Import os module to access environment variables for configuration
import os


class ToolAgent(BaseAgent):
    """
    ToolAgent is a specialized agent that inherits from BaseAgent.
    This agent is designed to handle tool-related operations and interactions.
    It uses environment variables to configure the LLM provider and model,
    with sensible defaults for tool-specific operations.
    """
    
    def __init__(self, 
                agent_name = "",  # Default agent name identifier
                llm_provider = os.getenv("TOOL_LLM_PROVIDER", "OpenAI"),  # LLM provider from env or default to OpenAI
                llm_name = os.getenv("TOOL_LLM_MODEL", "gpt-4o-mini")  # LLM model from env or default to gpt-4o-mini
                ):
        """
        Initialize the ToolAgent with specified or default configuration.
        
        Args:
            agent_name (str): Name identifier for this agent instance, defaults to "tool"
            llm_provider (str): The LLM provider to use (OpenAI, Ollama, GWDG, Synchange)
                               Retrieved from TOOL_LLM_PROVIDER environment variable or defaults to "OpenAI"
            llm_name (str): The specific model name to use within the provider
                           Retrieved from TOOL_LLM_MODEL environment variable or defaults to "gpt-4o-mini"
        """
        # Call the parent class constructor to initialize base agent functionality
        super().__init__(agent_name, llm_provider, llm_name)

        print("[Tool Agent]: ", end="")
        # Test the LLM connection to ensure the agent is properly configured and ready
        # This will validate that the LLM provider and model are accessible
        self.llm.test_connection()
