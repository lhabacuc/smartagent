
from typing import Optional
from .llm_base import BaseLLM
from .config import resolve_model, resolve_api_key
from ..core.exceptions import LLMError

class OpenAILLM(BaseLLM):
    """Cliente para OpenAI API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 2,
    ):
        resolved_api_key = resolve_api_key("openai", api_key, "OPENAI_API_KEY")
        super().__init__(resolved_api_key, model=model, timeout=timeout, retries=retries)
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY não encontrada")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = model or resolve_model("openai", "gpt-4o-mini")
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            payload = self._post_json(self.base_url, payload=data, headers=headers)
            return payload["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"Erro OpenAI: {str(e)}")
