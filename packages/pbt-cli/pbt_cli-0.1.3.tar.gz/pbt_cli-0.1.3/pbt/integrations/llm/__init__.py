"""LLM Provider Integrations"""

from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .azure import AzureOpenAIProvider
from .ollama import OllamaProvider

# Conditional import for LocalModelProvider
try:
    from .local_models import LocalModelProvider
    _has_local_models = True
except ImportError:
    _has_local_models = False
    LocalModelProvider = None

__all__ = [
    "ClaudeProvider",
    "OpenAIProvider",
    "AzureOpenAIProvider",
    "OllamaProvider",
]

if _has_local_models:
    __all__.append("LocalModelProvider")


async def get_llm_provider(model: str):
    """Get LLM provider instance for a given model"""
    from .base import LLMConfig
    
    # Map generic model names to specific models
    model_mapping = {
        "claude": "claude-3-sonnet-20240229",
        "claude-3": "claude-3-sonnet-20240229",
        "gpt-4": "gpt-4",
        "gpt-4-turbo": "gpt-4-turbo-preview",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        "mistral": "mistral-7b-instruct-v0.1",
        "ollama": "llama2"
    }
    
    # Use mapping or original model name
    actual_model = model_mapping.get(model, model)
    
    # Map model names to providers
    if actual_model.startswith("claude") or model == "claude":
        return ClaudeProvider(LLMConfig(model=actual_model))
    elif actual_model.startswith("gpt") or model.startswith("gpt"):
        return OpenAIProvider(LLMConfig(model=actual_model))
    elif actual_model.startswith("azure"):
        return AzureOpenAIProvider(LLMConfig(model=actual_model))
    elif model == "ollama" or actual_model == "llama2":
        return OllamaProvider(LLMConfig(model=actual_model))
    elif model in ["local", "gpt2", "mistral-7b", "llama-2-7b"] and _has_local_models:
        return LocalModelProvider(LLMConfig(model=actual_model))
    else:
        raise ValueError(f"Unknown model: {model}")