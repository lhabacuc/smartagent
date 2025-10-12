from typing import Dict, Any
from .utils import clean_response
from .exceptions import ResponseError
import json

class Responder:
    """Gera resposta final humanizada"""

    def __init__(self, llm_client, info: str = ""):
        self.llm_client = llm_client
        self.info = info

    def respond(self, user_prompt: str, execution_data: Dict[str, Any]) -> str:
        """Gera resposta final baseada nos dados executados"""

        info_section = f"\n\nInstruções adicionais:\n{self.info}\n" if self.info else ""

        system_prompt = f"""
Você é um assistente prestativo. 
Baseado nos dados de execução, responda de forma clara e concisa ao usuário.
Não invente informações, use apenas os dados fornecidos.
{info_section}
"""

        data_context = f"""
Pedido do usuário: {user_prompt}

Dados obtidos:
{json.dumps(execution_data.get('results', {}), ensure_ascii=False, indent=2)}

Gera uma resposta natural e útil para o usuário.
"""

        try:
            response = self.llm_client.chat(system_prompt, data_context)
            return clean_response(response)

        except Exception as e:
            raise ResponseError(f"Erro ao gerar resposta: {str(e)}")