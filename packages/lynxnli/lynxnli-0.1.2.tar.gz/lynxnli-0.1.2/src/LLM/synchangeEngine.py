from typing import Dict, Any
import requests
import json
import urllib.request
import urllib.error


# SynchangeLLM class provides an interface to interact with Synchange's LLM service
# Synchange appears to be a custom or third-party LLM provider
class SynchangeLLM():
    def __init__(self, 
                model: str, 
                api_url: str = "https://synchange.com/sync.php", 
                sender: str = "LynxNLI", 
                retries: int = 3,
                timeout: int = 10,
                access_id: str="trial_version",
                server_name :str = "meta_llama70b"):
        """Initialize the Synchange LLM client with configuration parameters.
        
        Args:
            model (str): The name of the model to use for generating responses
            api_url (str, optional): The URL of the Synchange API. Defaults to "https://synchange.com/sync.php".
            sender (str, optional): The name of the sender to include in prompts. Defaults to "LynxNLI".
            retries (int, optional): Number of retry attempts for API calls. Defaults to 3.
            timeout (int, optional): Timeout in seconds for API calls. Defaults to 10.
            access_id (str, optional): Access ID for authentication. Defaults to "trial_version".
            server_name (str, optional): Name of the server to use. Defaults to "meta_llama70b".
        """
        # Store model name
        self.model = model
        # API endpoint URL
        self.base_url = api_url
        # Sender name to include in prompts
        self.sender = sender
        # Number of retry attempts for API calls
        self.retries = retries
        # Timeout in seconds for API calls
        self.timeout = timeout
        # Access ID for authentication
        self.access_id = access_id
        # Server name to use
        self.service_name = server_name
        # Default system prompt that defines the LLM's behavior
        self.base_prompt = (
            "You are an LLM agent, a prototype AI agent answering to prompts requested by users."
        )

    def chat(self, prompt: str) -> Dict[str, Any]:
        """Send a chat request to the Synchange LLM service.
        
        Note: This method appears to have bugs as it references self.llm
        which is not defined in the class. It may be a legacy method or incomplete.
        
        Args:
            prompt (str): The user's prompt to send to the LLM
            
        Returns:
            Dict[str, Any]: The LLM's response as a dictionary or an error message
        """
        # Prepare HTTP request
        payload = {
            "access_id":    self.access_id,
            "service_name": self.service_name,
            "query":        prompt
        }
        # Encode the payload as JSON
        data = json.dumps(payload).encode("utf-8")
        # Create the HTTP request
        req = urllib.request.Request(
            self.base_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        # Send and parse response
        try:
            # Send the request and get the response
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_text = resp.read().decode("utf-8")
            # Parse the JSON response
            data = json.loads(resp_text)
            # Check for errors in the response
            if "error" in data:
                return {"response": f"Error: {data['error']}"}
            # Return the full response data
            return data
        except urllib.error.URLError as e:
            # Handle URL errors
            return {"response": f"Error: {e}"}
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            return {"response": "Error: Invalid JSON in response."}


    def send_request(self, prompt: str) -> str:
        """Send a single prompt to the Synchange LLM API and return its response.

        This method uses the requests library instead of urllib, and properly uses
        the class attributes (unlike the chat method which has bugs).

        Args:
            prompt (str): The user prompt to send.
            
        Returns:
            str: The LLM's response text or an error message.
        """
        # Build the full payload prompt with instructions
        full_prompt = (
            f"{self.base_prompt}\n\n"
            f"Input (from {self.sender}): {prompt}\n\n"
            "Provide only a concise final answer that directly addresses the query."
        )

        # Create the request payload
        payload = {
            "access_id": self.access_id,
            "service_name": self.service_name,
            "query": full_prompt
        }

        # Attempt the request up to `self.retries` times
        for attempt in range(1, self.retries + 1):
            try:
                # Send the POST request to the Synchange API
                response = requests.post(
                    self.base_url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the JSON response
                    data = response.json()
                    # Extract and return the response content
                    return data.get("response", "").strip()
                else:
                    # Handle non-200 status codes
                    error_msg = response.text.strip()
                    print(f"[Attempt {attempt}] HTTP {response.status_code}: {error_msg}")
            except Exception as e:
                # Log the error and retry
                print(f"[Attempt {attempt}] Exception: {e}")

        # Return error message if all retry attempts fail
        return "Error: API call failed after multiple attempts"

    def test_connection(self)-> bool:
        """Test the connection to the Synchange LLM service.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            RuntimeError: If connection fails
        """
        # Create a simple test payload
        payload = {
            "access_id":    self.access_id,
            "service_name": self.service_name,
            "query":        "Test the connection, return True or False"
        }
        # Send a test request to the API
        response = requests.post(
            self.base_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=self.timeout
            )
        # Check if the request was successful
        if response.status_code == 200:
            print(f"SynChangeLLM LLM backend connection is successful for model: {self.model}!\n")
            return True
        else:
            # Raise an error if the connection failed
            raise RuntimeError(f"SynChangeLLM connection is failed for {self.model}\n")
