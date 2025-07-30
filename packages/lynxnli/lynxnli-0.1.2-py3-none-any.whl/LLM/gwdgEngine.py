import os
from openai import OpenAI
from typing import Dict, Any
import urllib.request
import urllib.error
import json


# GWDGLLM class provides an interface to interact with GWDG's LLM service
# GWDG is likely a specific LLM provider with an OpenAI-compatible API
class GWDGLLM():
    def __init__(self, model:str):
        """Initialize base LLM class.
        
        Args:
            model (str): The name of the model to use for generating responses
        """
        # Store model name
        self.model = model
        # Number of retry attempts for API calls
        self.retries = 3
        # Timeout in seconds for API calls
        self.timeout = 10
        # Default prompt to use if none is provided
        self.base_prompt = "You are a great assistant."
        # Get API endpoint from environment variables
        self.base_url = os.getenv("GWDG_MODEL_URL","")
        # Get API key from environment variables
        self.api_key = os.getenv("GWDG_MODEL_API_KEY", "")
        # Initialize OpenAI client with GWDG-specific configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        # Default system prompt that defines the LLM's behavior
        self.system_prompt = (
            "You are an LLM agent, a prototype AI agent answering to prompts requested by users."
        )
    
    def send_request(self, query: str) -> str:
        """Send a request to the GWDG LLM service and get a response.
        
        Args:
            query (str): The user's query to send to the LLM
            
        Returns:
            str: The LLM's response text or an error message
        """
        # Try multiple times based on self.retries
        for attempt in range(self.retries):
            try:
                # Create a chat completion request using the OpenAI client
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": query}
                    ],
                    stream=False
                )
                # Extract and return the response content
                return response.choices[0].message.content
            except Exception as e:
                # Return error message if request fails
                return f"Error communicating with GWDG LLM: {str(e)}"
        # Return error message if all retry attempts fail
        return "Error: API call failed after multiple attempts with OPENAI"


    def chat(self, prompt: str) -> Dict[str, Any]:
        """Alternative implementation using urllib instead of the OpenAI client.
        
        Note: This method appears to have bugs as it references self.llm_name and self.llm
        which are not defined in the class. It may be a legacy method or incomplete.
        
        Args:
            prompt (str): The user's prompt to send to the LLM
            
        Returns:
            Dict[str, Any]: The LLM's response as a dictionary or an error message
        """
        # Create the request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        }

        # Encode the payload as JSON
        data = json.dumps(payload).encode("utf-8")
        # Create the HTTP request
        req = urllib.request.Request(
            self.base_url+"chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"  # Bug: should be self.api_key
            }
        )
        try:
            # Send the request and get the response
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
            # Parse the JSON response
            data = json.loads(resp_text)
            # Check for errors in the response
            if "error" in data:
                return {"response": f"Error: {data['error']}"}
            # Return the message from the first choice
            return data["choices"][0]["message"]
        
        except urllib.error.URLError as e:
            # Handle URL errors
            return {"response": f"Error: {e}"}
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            return {"response": "Error: Invalid JSON in response."}

    
    def test_connection(self) -> bool:
        """Test the connection to the GWDG LLM service.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            RuntimeError: If connection fails or the model is not available
        """
        # Get a list of available models from the API
        models = self.client.models.list()
        # Extract the model IDs
        available_model_ids = [model.id for model in models.data]
        # Check if the requested model is available
        if self.model in available_model_ids:
            print(f"GWDG LLM backend connection is successful for model: {self.model}!\n")
            return True
        else:
            # Raise an error if the model is not available
            raise RuntimeError(f"OpenAI connection is failed for {self.model}\n")
