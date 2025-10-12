
from typing import Optional
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

def get_llm_client(provider: str, api_key: Optional[str] = None) -> BaseLLM:
    """Factory para criar cliente LLM"""
    
    provider = provider.lower()
    
    if provider == "groq":
        from .llm_groq import GroqLLM
        return GroqLLM(api_key)
    
    elif provider == "openai":
        from .llm_openai import OpenAILLM
        return OpenAILLM(api_key)
    
    elif provider == "gemini" or provider == "google-gemini":
        from .llm_gemini import GeminiLLM
        return GeminiLLM(api_key)
    
    elif provider == "grok":
        from .llm_grok import GrokLLM
        return GrokLLM(api_key)
    
    elif provider == "ollama":
        from .llm_ollama import OllamaLLM
        return OllamaLLM()
    
    elif provider == "llama":
        from .llm_llama import LlamaLLM
        return LlamaLLM(api_key)
    
    else:
        raise LLMError(f"Provider '{provider}' não suportado")

__all__ = ["get_llm_client", "BaseLLM"]
