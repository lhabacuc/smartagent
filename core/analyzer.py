from typing import Dict, Any, Optional
from .utils import safe_json
from .exceptions import AnalysisError

class Analyzer:
    """Analisa a intenção do usuário e determina ações necessárias"""

    def __init__(self, llm_client, info: str = ""):
        self.llm = llm_client
        self.info = info

    def analyze(self, user_prompt: str, tools_description: str) -> Dict[str, Any]:
        """Analisa o prompt e retorna plano de execução"""

        info_section = f"\n\nInstruções adicionais:\n{self.info}\n" if self.info else ""

        system_prompt = f"""Tua tarefa é analisar o pedido do usuário e identificar:
1. Quais dados são necessários (data_using_util) - parâmetros para as ferramentas
2. Quais funções locais devem ser executadas (tool_using_exec) - lista de nomes

{info_section}
Ferramentas disponíveis:
{tools_description}

Retorna SEMPRE JSON válido no formato:
{{"isValid": true, "data_using_util": {{}}, "tool_using_exec": []}}

Se o pedido não puder ser atendido, retorna:
{{"isValid": false, "reason": "motivo"}}

Exemplo:
Usuário: "Quais produtos baratos?"
Resposta: {{"isValid": true, "data_using_util": {{"max_price": 100}}, "tool_using_exec": ["get_products"]}}
"""

        try:
            response = self.llm.chat(system_prompt, user_prompt)
            analysis = safe_json(response)

            if not analysis:
                raise AnalysisError(f"Resposta inválida do LLM: {response}")

            # Validação básica
            if 'isValid' not in analysis:
                analysis['isValid'] = True

            if analysis['isValid']:
                if 'tool_using_exec' not in analysis:
                    analysis['tool_using_exec'] = []
                if 'data_using_util' not in analysis:
                    analysis['data_using_util'] = {}

            return analysis

        except Exception as e:
            raise AnalysisError(f"Erro na análise: {str(e)}")