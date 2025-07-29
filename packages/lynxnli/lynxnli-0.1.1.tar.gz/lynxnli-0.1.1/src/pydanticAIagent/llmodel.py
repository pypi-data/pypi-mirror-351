import os
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

def get_crentials(stage: str):
    """Get the credentials for the LLM provider."""
    llm_provider = os.environ.get(f'{stage}_LLM_PROVIDER', "OpenAI")
    llm_model = os.environ.get(f'{stage}_LLM_MODEL', "gpt-4o-mini")
    llm_api_key = os.environ.get(f'{stage}_LLM_API_KEY', "")
    llm_url = os.environ.get(f'{stage}_LLM_URL', "")
    return llm_provider, llm_model, llm_api_key, llm_url

def model_init(stage: str):
    """Initialize the model based on the LLM provider."""
    llm_provider, llm_model, llm_api_key, llm_url = get_crentials(stage)
    print(f"llm_provider: {llm_provider}, llm_model: {llm_model}\n")
    if llm_provider == "OpenAI":
        return OpenAIModel(llm_model)
    elif llm_provider == "Ollama":
        from LLM.ollamaEngine import OllamaLLM
        host = os.environ.get('OLLAMA_HOST', "localhost")
        port = os.environ.get('OLLAMA_PORT', "11434")
        base_url = f"http://{host}:{port}"
        privider = OpenAIProvider(base_url=base_url)
        return OpenAIModel(llm_model, provider=privider)
    elif llm_provider == "Synchange":
        from LLM.synchangeEngine import SynchangeLLM
        return SynchangeLLM(model=llm_model)
    elif llm_provider == "gwdg":
        privider = OpenAIProvider(base_url=llm_url, api_key=llm_api_key)
        return OpenAIModel(llm_model, provider=privider)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def get_model(stage: str):
    """Get the model based on the LLM provider."""
    if stage == "plan":
        return model_init(stage.upper())
    elif stage == "task":
        return model_init(stage.upper())
    elif stage == "evaluate":
        return model_init(stage.upper())
    elif stage == "tool":
        return model_init(stage.upper())    
    else:
        raise ValueError(f"Unsupported stage: {stage}")




