import unittest
from unittest.mock import patch, MagicMock
import os
import json
import requests
from .ollamaEngine import OllamaLLM

class TestOllamaLLM(unittest.TestCase):
    """Test cases for the OllamaLLM class."""

    def setUp(self):
        """Set up test environment before each test."""
        # Set environment variables for testing
        os.environ["OLLAMA_HOST"] = "localhost"
        os.environ["OLLAMA_PORT"] = "11434"
        
        # Create an instance of OllamaLLM with a test model
        self.llm = OllamaLLM(model="llama3.2")
        
        # Save original environment to restore later
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_init(self):
        """Test initialization of OllamaLLM."""
        # Verify that the instance was created with correct attributes
        self.assertEqual(self.llm.model, "llama3.2")
        self.assertEqual(self.llm.timeout, 20)
        self.assertEqual(self.llm.retries, 3)
        self.assertEqual(self.llm.host, "localhost")
        self.assertEqual(self.llm.port, '11434')
        self.assertEqual(self.llm.base_url, "http://localhost:11434")

    def test_init_missing_host(self):
        """Test initialization with missing OLLAMA_HOST."""
        # Remove the OLLAMA_HOST environment variable
        os.environ.pop("OLLAMA_HOST")
        
        # Expect a ValueError when creating an instance
        with self.assertRaises(ValueError):
            OllamaLLM(model="llama2")

    def test_init_missing_port(self):
        """Test initialization with missing OLLAMA_PORT."""
        # Remove the OLLAMA_PORT environment variable
        os.environ.pop("OLLAMA_PORT")
        
        # Expect a ValueError when creating an instance
        with self.assertRaises(ValueError):
            OllamaLLM(model="llama3.2")

    @patch('requests.post')
    def test_send_request_success(self, mock_post):
        """Test successful API request."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        
        # Set up the mock to return our mock response
        mock_post.return_value = mock_response
        
        # Call the method being tested
        result = self.llm.send_request("Test query")
        
        # Verify the result
        self.assertEqual(result, "Test response")
        
        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        self.assertEqual(kwargs["headers"], {"Content-Type": "application/json"})
        self.assertEqual(kwargs["timeout"], 20)
        
        # Verify the payload contains the expected data
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["model"], "llama3.2")
        self.assertTrue("query" in payload)
        self.assertEqual(payload["steam"], "False")  # Note: This is a typo in the original code

    @patch('requests.post')
    def test_send_request_error(self, mock_post):
        """Test API request with error."""
        # Set up the mock to raise an exception
        mock_post.side_effect = Exception("Connection error")
        
        # Call the method being tested
        result = self.llm.send_request("Test query")
        
        # Verify the result contains the error message
        self.assertEqual(result, "Error: API call failed after multiple attempts with Ollama")

    @patch('requests.post')
    def test_chat_success(self, mock_post):
        """Test successful chat API request."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Test response"}}
        
        # Set up the mock to return our mock response
        mock_post.return_value = mock_response
        
        # Call the method being tested
        result = self.llm.chat("Test query")
        
        # Verify the result
        self.assertEqual(result, {"content": "Test response"})
        
        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/chat")
        
        # Verify the payload contains the expected data
        payload = kwargs["json"]
        self.assertEqual(payload["model"], "llama3.2")
        self.assertEqual(payload["stream"], False)
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertEqual(payload["messages"][1]["content"], "Test query")

    @patch('requests.post')
    def test_chat_request_exception(self, mock_post):
        """Test chat API request with request exception."""
        # Set up the mock to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the method being tested
        result = self.llm.chat("Test query")
        
        # Verify the result contains the error message
        self.assertEqual(result, {"response": "Error: Connection error"})

    @patch('requests.post')
    def test_chat_value_error(self, mock_post):
        """Test chat API request with JSON parsing error."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Set up the mock to raise a ValueError when json() is called
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        # Call the method being tested
        result = self.llm.chat("Test query")
        
        # Verify the result contains the error message
        self.assertEqual(result, {"response": "Error: Invalid JSON in response."})

    @patch('requests.post')
    def test_test_connection_success(self, mock_post):
        """Test successful connection test."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Set up the mock to return our mock response
        mock_post.return_value = mock_response
        
        # Call the method being tested
        result = self.llm.test_connection()
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        
        # Verify the payload contains the expected data
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["model"], "llama3.2")
        self.assertEqual(payload["query"], "Test the connection, return True or False")

    @patch('requests.post')
    def test_test_connection_failure(self, mock_post):
        """Test failed connection test."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        # Set up the mock to return our mock response
        mock_post.return_value = mock_response
        
        # Call the method being tested and expect an exception
        with self.assertRaises(RuntimeError):
            self.llm.test_connection()
        
        # Verify the API was called
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
