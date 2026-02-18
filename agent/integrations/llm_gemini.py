
from typing import Optional
from .llm_base import BaseLLM
from .config import resolve_model, resolve_api_key
from ..core.exceptions import LLMError

class GeminiLLM(BaseLLM):
    """Cliente para Google Gemini API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 2,
    ):
        resolved_api_key = resolve_api_key("gemini", api_key, "GEMINI_API_KEY")
        super().__init__(resolved_api_key, model=model, timeout=timeout, retries=retries)
        if not self.api_key:
            raise LLMError("GEMINI_API_KEY não encontrada")
        
        self.model = model or resolve_model("gemini", "gemini-2.0-flask")
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        data = {
            "contents": [{
                "parts": [{"text": combined_prompt}]
            }]
        }
        
        try:
            payload = self._post_json(url, payload=data)
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise LLMError(f"Erro Gemini: {str(e)}")
