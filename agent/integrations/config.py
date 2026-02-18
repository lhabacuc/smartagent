import os


def resolve_model(provider: str, default_model: str) -> str:
    """Resolve model using provider-specific and global environment variables."""
    provider_key = provider.upper().replace("-", "_")
    return (
        os.getenv(f"SMARTAGENT_{provider_key}_MODEL")
        or os.getenv("SMARTAGENT_MODEL")
        or os.getenv("LLM")
        or default_model
    )
