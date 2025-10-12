
import os
import requests
from typing import Optional
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

class GeminiLLM(BaseLLM):
    """Cliente para Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("GEMINI_API_KEY"))
        if not self.api_key:
            raise LLMError("GEMINI_API_KEY não encontrada")
        
        self.model = os.getenv("LLM") or "gemini-2.0-flask"
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        data = {
            "contents": [{
                "parts": [{"text": combined_prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise LLMError(f"Erro Gemini: {str(e)}")
