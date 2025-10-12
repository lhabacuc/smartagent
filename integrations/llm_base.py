
from abc import ABC, abstractmethod
from typing import Optional

class BaseLLM(ABC):
    """Interface base para todos os provedores LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Envia mensagem e retorna resposta"""
        pass
