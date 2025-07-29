"""
LLM Package - Provides interfaces to various Large Language Model providers

This package contains classes for interacting with different LLM providers:
- GWDGLLM: Interface for GWDG's LLM service (OpenAI-compatible API)
- OllamaLLM: Interface for Ollama's locally-hosted LLM service
- OpenAILLM: Interface for OpenAI's API (GPT models)
- SynchangeLLM: Interface for Synchange's LLM service

Each class provides a consistent interface with methods like:
- send_request: Send a single prompt and get a response
- chat: Send a chat-style request with system and user messages
- test_connection: Verify the connection to the LLM service

Usage example:
    from LLM.openaiEngine import OpenAILLM
    
    llm = OpenAILLM(model="gpt-4")
    response = llm.send_request("What is the capital of France?")
    print(response)
"""
