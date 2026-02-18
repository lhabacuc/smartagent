import importlib
from typing import Optional, Dict, Tuple
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

_PROVIDER_REGISTRY: Dict[str, Tuple[str, str]] = {
    "groq": (".llm_groq", "GroqLLM"),
    "openai": (".llm_openai", "OpenAILLM"),
    "gemini": (".llm_gemini", "GeminiLLM"),
    "grok": (".llm_grok", "GrokLLM"),
    "ollama": (".llm_ollama", "OllamaLLM"),
    "llama": (".llm_llama", "LlamaLLM"),
}

_ALIASES = {
    "google-gemini": "gemini",
    "google_gemini": "gemini",
    "xai": "grok",
}


def normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    return _ALIASES.get(normalized, normalized)


def get_llm_client(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: float = 30.0,
    retries: int = 2,
) -> BaseLLM:
    """Factory para criar cliente LLM."""
    provider_key = normalize_provider(provider)
    if provider_key not in _PROVIDER_REGISTRY:
        raise LLMError(f"Provider '{provider}' não suportado")

    module_name, class_name = _PROVIDER_REGISTRY[provider_key]
    module = importlib.import_module(module_name, package=__name__)
    llm_class = getattr(module, class_name)
    return llm_class(api_key=api_key, model=model, timeout=timeout, retries=retries)


__all__ = ["get_llm_client", "normalize_provider", "BaseLLM"]
