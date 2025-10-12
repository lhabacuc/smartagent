
import requests
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

class OllamaLLM(BaseLLM):
    """Cliente para Ollama (execução local)"""
    
    def __init__(self):
        super().__init__(None)
        self.base_url = "http://localhost:11434/api/chat"
        self.model = os.getenv("LLM") or "llama3.2"
    
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
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            raise LLMError(f"Erro Ollama: {str(e)}")
