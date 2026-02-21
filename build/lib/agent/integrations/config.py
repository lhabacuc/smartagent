import os
from typing import Optional


def resolve_model(provider: str, default_model: str) -> str:
    """Resolve model using provider-specific and global environment variables."""
    provider_key = provider.upper().replace("-", "_")
    return (
        os.getenv(f"SMARTAGENT_{provider_key}_MODEL")
        or os.getenv("SMARTAGENT_MODEL")
        or os.getenv("LLM")
        or default_model
    )


def resolve_api_key(provider: str, explicit_key: Optional[str], provider_env_key: str) -> Optional[str]:
    """Resolve API key with library namespace and legacy provider keys."""
    provider_key = provider.upper().replace("-", "_")
    return (
        explicit_key
        or os.getenv(f"SMARTAGENT_{provider_key}_API_KEY")
        or os.getenv("SMARTAGENT_API_KEY")
        or os.getenv(provider_env_key)
    )
