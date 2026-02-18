from typing import Optional
from .llm_base import BaseLLM
from .config import resolve_model
from ..core.exceptions import LLMError

class OllamaLLM(BaseLLM):
    """Cliente para Ollama (execução local)"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 2,
    ):
        super().__init__(api_key, model=model, timeout=timeout, retries=retries)
        self.base_url = "http://localhost:11434/api/chat"
        self.model = model or resolve_model("ollama", "llama3.2")
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }
        
        try:
            payload = self._post_json(self.base_url, payload=data)
            return payload["message"]["content"]
        except Exception as e:
            raise LLMError(f"Erro Ollama: {str(e)}")
