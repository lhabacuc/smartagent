
import os
import requests
from typing import Optional
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

class LlamaLLM(BaseLLM):
    """Cliente para Llama Cloud API (Meta)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("LLAMA_API_KEY"))
        if not self.api_key:
            raise LLMError("LLAMA_API_KEY não encontrada")
        
        self.base_url = "https://api.together.xyz/v1/chat/completions"
        self.model = os.getenv("LLM") or "meta-llama/Llama-3-70b-chat-hf"
    
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
            response = requests.post(self.base_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"Erro Llama: {str(e)}")
