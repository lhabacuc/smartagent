from abc import ABC, abstractmethod
import time
from typing import Optional, Dict, Any

class BaseLLM(ABC):
    """Interface base para todos os provedores LLM"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 2,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = float(timeout)
        self.retries = max(0, int(retries))

    def _post_json(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        import requests
        from ..core.exceptions import LLMError

        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                time.sleep(min(0.25 * (2 ** attempt), 1.0))

        raise LLMError(
            f"Falha HTTP após {self.retries + 1} tentativa(s): {last_error}"
        )
    
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Envia mensagem e retorna resposta"""
        pass
