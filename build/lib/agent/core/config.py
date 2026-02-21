import os
import warnings
from dataclasses import dataclass
from typing import Optional


KNOWN_PROVIDERS = {"groq", "openai", "gemini", "google-gemini", "grok", "ollama", "llama"}


@dataclass(frozen=True)
class AgentConfig:
    provider: str
    model: Optional[str]
    api_key: Optional[str]
    timeout: float
    retries: int
    info: str
    enable_history: bool
    history_limit: int

    @classmethod
    def from_inputs(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        info: str = "",
        enable_history: bool = False,
        history_limit: int = 20,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> "AgentConfig":
        env_provider = os.getenv("SMARTAGENT_PROVIDER")
        resolved_provider = (provider or env_provider or "").strip().lower()
        resolved_model = model

        if not resolved_provider:
            model_candidate = (model or "").strip().lower()
            if model_candidate in KNOWN_PROVIDERS:
                if model_candidate != "groq":
                    warnings.warn(
                        "Using model as provider is deprecated; prefer provider='...'.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                resolved_provider = model_candidate
                resolved_model = None
            else:
                resolved_provider = "groq"

        env_timeout = os.getenv("SMARTAGENT_TIMEOUT")
        env_retries = os.getenv("SMARTAGENT_RETRIES")

        resolved_timeout = timeout
        if resolved_timeout is None:
            resolved_timeout = float(env_timeout) if env_timeout else 30.0

        resolved_retries = retries
        if resolved_retries is None:
            resolved_retries = int(env_retries) if env_retries else 2

        return cls(
            provider=resolved_provider,
            model=resolved_model,
            api_key=api_key,
            timeout=float(resolved_timeout),
            retries=max(0, int(resolved_retries)),
            info=info,
            enable_history=bool(enable_history),
            history_limit=history_limit if history_limit and history_limit > 0 else 20,
        )
