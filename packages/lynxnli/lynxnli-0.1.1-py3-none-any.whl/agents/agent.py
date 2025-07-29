# Import different LLM engine implementations for various providers
from LLM.openaiEngine import OpenAILLM
from LLM.ollamaEngine import OllamaLLM
from LLM.gwdgEngine import GWDGLLM
from LLM.synchangeEngine import SynchangeLLM
# Import the agent state management system
from content.state import AgentState
# Import type hints for better code documentation and IDE support
from typing import Optional, Dict, List


class BaseAgent():
    """
    BaseAgent is the foundational class for all agent types in the system.
    It provides common functionality including LLM initialization, prompt formatting,
    and basic agent operations. All specialized agents inherit from this class.
    
    This class implements a factory pattern for LLM initialization and provides
    standardized methods for prompt handling and context management.
    """
    
    def __init__(self, agent_name:str, llm_provider:str, llm_name:str):
        """
        Initialize the base agent with core configuration.
        
        Args:
            agent_name (str): Unique identifier for this agent instance
            llm_provider (str): The LLM provider to use (OpenAI, Ollama, GWDG, Synchange)
            llm_name (str): The specific model name within the chosen provider
        """
        # Store agent configuration
        self.agent = agent_name
        self.llm_provider = llm_provider
        self.llm_name = llm_name
        
        # Initialize the LLM instance using the factory method
        self.llm = self.init_llm(llm_provider, llm_name)
        
        # Set a base prompt instruction that applies to all agent interactions
        # This ensures consistent output formatting across all agents
        self.base_prompt = "Do not return it with markdown format, only return it as string."

    def init_llm(self, llm_provider, llm_name):
        """
        Factory method to initialize the appropriate LLM engine based on provider.
        Uses pattern matching to select the correct LLM implementation.
        
        Args:
            llm_provider (str): The LLM provider identifier
            llm_name (str): The specific model name
            
        Returns:
            LLM instance: An initialized LLM engine object, or None if initialization fails
        """
        llm = None
        
        # Use pattern matching (Python 3.10+) to select appropriate LLM provider
        match llm_provider:
            case "OpenAI":
                try:
                    # Initialize OpenAI LLM with specified model
                    llm = OpenAILLM(llm_name)
                except Exception as e: 
                    print(f"An error occurred: {e}")
                    
            case "Ollama":
                try:
                    # Initialize Ollama LLM for local model execution
                    llm = OllamaLLM(llm_name)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            case "GWDG":
                try:
                    # Initialize GWDG LLM for academic/research environments
                    llm = GWDGLLM(llm_name)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            case "Synchange":
                try:
                    # Initialize Synchange LLM provider
                    llm = SynchangeLLM(llm_name)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            case _:
                # Default case for unrecognized providers
                try:
                    print("Use default LLM provider and model")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
        return llm
    
        

    def prompt(self) -> str:
        """
        Base method for generating prompts. This is meant to be overridden by subclasses.
        Each specialized agent should implement its own prompt generation logic.
        
        Returns:
            str: A prompt string (currently returns empty string as placeholder)
        """
        prompt =  """"."""
        return prompt

    def validation(self, result:str) -> bool:
        """
        Base method for validating agent results. This is meant to be overridden by subclasses.
        Each specialized agent should implement its own validation logic.
        
        Args:
            result (str): The result to validate
            
        Returns:
            bool: Validation result (currently not implemented in base class)
        """
        pass

    def generate(self, agentState: AgentState):
        """
        Base method for generating agent responses. This is meant to be overridden by subclasses.
        Each specialized agent should implement its own generation logic.
        
        Args:
            agentState (AgentState): The current state of the agent system
        """
        pass
        
    def format_prompt(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Format the prompt with system and user instructions.
        This method combines the base prompt, optional system prompt, and user prompt
        into a well-structured format for LLM consumption.
        
        Args:
            user_prompt (str): The user's input prompt or question
            system_prompt (Optional[str]): Additional system instructions to include
            
        Returns:
            str: The formatted prompt ready for LLM processing
        """
        # Start with the base prompt that ensures consistent formatting
        final_prompt = self.base_prompt
        
        # Add system prompt if provided
        if system_prompt:
            final_prompt += f"\n\n{system_prompt}"
            
        # Add the user prompt with clear labeling
        final_prompt += f"\n\nUser: {user_prompt}"
        
        return final_prompt


    def _format_chat_context(self, context: List[Dict[str, str]]) -> str:
        """
        Format chat context history into a readable string format.
        This method processes conversation history and tool interactions
        to provide context for the LLM.
        
        Args:
            context (List[Dict[str, str]]): List of context entries with various formats
            
        Returns:
            str: Formatted context string with labeled entries
        """
        formatted = []
        
        # Process each context entry based on its structure
        for entry in context:
            if "role" in entry:
                # Handle role-based entries (standard chat format)
                if entry["role"] == "tool_result":
                    # Format tool execution results
                    formatted.append(f"[Tool {entry.get('tool_name', 'unknown')}]: {entry.get('output', '')}")
                else:
                    # Format standard chat roles (user, assistant, system)
                    formatted.append(f"[{entry['role'].capitalize()}]: {entry.get('content', '')}")
                    
            elif "prompt" in entry and "output" in entry:
                # Handle prompt-output pairs from tool interactions
                formatted.append(f"[Prompt]: {entry['prompt']}\n[Tool Output]: {entry['output']}")
                
            elif "prompt" in entry:
                # Handle standalone prompts
                formatted.append(f"[Prompt]: {entry['prompt']}")
                
        # Join all formatted entries with newlines for readability
        return "\n".join(formatted)
