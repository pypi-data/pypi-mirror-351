import os
import requests
import json
from typing import Dict, Any

# OllamaLLM class provides an interface to interact with Ollama's LLM service
# Ollama is an open-source framework for running LLMs locally
class OllamaLLM():
    def __init__(self, model:str):
        """Initialize the Ollama client with configuration from .env file.
        
        Args:
            model (str): The name of the model to use for generating responses
            
        Raises:
            ValueError: If required environment variables are not found
        """
        # Store model name
        self.model = model
        # Timeout in seconds for API calls
        self.timeout = 20
        # Number of retry attempts for API calls
        self.retries = 3
        # Get host from environment variables
        self.host = os.getenv('OLLAMA_HOST')
        if not self.host:
            raise ValueError("OLLAMA_HOST not found in environment variables")
        # Get port from environment variables and convert to integer
        self.port = os.getenv('OLLAMA_PORT')
        if not self.port:
            raise ValueError("OLLAMA_PORT not found in environment variables")
        # Construct the base URL for API requests
        self.base_url = f"http://{self.host}:{self.port}"
        # Default system prompt that defines the LLM's behavior
        self.base_prompt = (
            "You are an LLM agent, a prototype AI agent answering to prompts requested by users."
        )
            
    def send_request(self, query: str) -> str:
        """Send a request to the Ollama LLM service and get a response.
        
        Args:
            query (str): The user's query to send to the LLM
            
        Returns:
            str: The LLM's response text or an error message
        """
        # Construct the full prompt with instructions for the model
        full_prompt = (
            self.base_prompt + "\n\n"
            "query: " + query + "\n\n"
            "Provide only a concise final answer that directly addresses the query. "
            "Do not include any internal processing details or meta commentary."
            "Always close your strings with quotation marks properly. Use double quotes (\") and avoid truncating them."
        )

        # Create the request payload
        payload = {
            "model": self.model,
            "query": full_prompt,
            "steam": "False"  # Note: This appears to be a typo, should be "stream"
        }

        # Try multiple times based on self.retries
        for attempt in range(self.retries):
            try:
                # Send the POST request to the Ollama API
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()
                    # Extract and return the response content
                    return data.get("response", "No valid response from API").strip()
            except Exception as e:
                # Log the error and retry
                print(f"[Retry {attempt+1}] Error: {e}")
        # Return error message if all retry attempts fail
        return "Error: API call failed after multiple attempts with Ollama"
    
    def chat(self, prompt: str) -> Dict[str, Any]:
        """Send a chat request to the Ollama LLM service using the chat API.
        
        This method uses the newer chat API format which is more aligned with
        OpenAI's chat completions API.
        
        Args:
            prompt (str): The user's prompt to send to the LLM
            
        Returns:
            Dict[str, Any]: The LLM's response as a dictionary or an error message
        """
        # Construct the API endpoint URL
        url = f"{self.base_url}/api/chat"
        # Create the request payload
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": prompt}
            ]
        }

        try:
            # Send the POST request to the Ollama chat API
            resp = requests.post(url, json=payload, timeout=self.timeout)
            # Raise an exception for HTTP errors
            resp.raise_for_status()
            # Parse the JSON response
            data = resp.json()
            # Ollama returns the assistant response in `message`
            return data["message"]

        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            return {"response": f"Error: {e}"}
        except ValueError:
            # Handle JSON parsing errors
            return {"response": "Error: Invalid JSON in response."}    


    def test_connection(self)-> bool:
        """Test the connection to the Ollama LLM service.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            RuntimeError: If connection fails
        """
        # Create a simple test payload
        payload = {
            "query": "Test the connection, return True or False",
            "model": self.model,
            "steam": "False"  # Note: This appears to be a typo, should be "stream"
        }
        # Send a test request to the API
        response = requests.post(
            f"{self.base_url}/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=self.timeout
            )
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Ollama backend connection is successful for model: {self.model}!\n")
            return True
        else:
            # Raise an error if the connection failed
            raise RuntimeError(f"Ollama connection is failed for {self.model}\n")
