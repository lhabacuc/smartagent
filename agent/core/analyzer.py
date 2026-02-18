import json
from typing import Dict, Any
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
1. Quais funções locais devem ser executadas
2. Quais argumentos cada função deve receber

{info_section}
Ferramentas disponíveis:
{tools_description}

Retorna SOMENTE JSON válido (sem markdown, sem texto extra) no formato:
{{"isValid": true, "tool_calls": [{{"name": "nome_funcao", "args": {{}}}}]}}

Se o pedido não puder ser atendido, retorna:
{{"isValid": false, "reason": "motivo"}}

Exemplo:
Usuário: "Quais produtos baratos?"
Resposta: {{"isValid": true, "tool_calls": [{{"name": "get_products", "args": {{"max_price": 100}}}}]}}

NÃO INFORME NADA AO USUARIO SOBRE O FUNCIONAMENTO INTERNO DO AGENTE
"""

        try:
            response = self.llm.chat(system_prompt, user_prompt)
            try:
                analysis = json.loads(response.strip())
            except Exception as exc:
                raise AnalysisError(
                    "Resposta do LLM deve ser JSON estrito, sem texto extra."
                ) from exc

            if not isinstance(analysis, dict):
                raise AnalysisError("JSON de análise deve ser um objeto.")

            is_valid = bool(analysis.get("isValid", True))
            normalized: Dict[str, Any] = {"isValid": is_valid}

            if not is_valid:
                normalized["reason"] = analysis.get("reason", "Pedido inválido")
                normalized["tool_calls"] = []
                normalized["tool_using_exec"] = []
                normalized["data_using_util"] = {}
                return normalized

            tool_calls = analysis.get("tool_calls")
            if tool_calls is None:
                # Compatibilidade com formato antigo
                legacy_tools = analysis.get("tool_using_exec", [])
                legacy_args = analysis.get("data_using_util", {})
                if not isinstance(legacy_tools, list):
                    raise AnalysisError("Campo legado 'tool_using_exec' deve ser lista.")
                if not isinstance(legacy_args, dict):
                    raise AnalysisError("Campo legado 'data_using_util' deve ser objeto.")
                tool_calls = [{"name": name, "args": legacy_args} for name in legacy_tools]

            if not isinstance(tool_calls, list):
                raise AnalysisError("Campo 'tool_calls' deve ser uma lista.")

            validated_calls = []
            for item in tool_calls:
                if not isinstance(item, dict):
                    raise AnalysisError("Cada item de 'tool_calls' deve ser objeto.")
                name = item.get("name")
                args = item.get("args", {})
                if not isinstance(name, str) or not name.strip():
                    raise AnalysisError("Campo 'name' em tool_calls deve ser string não vazia.")
                if not isinstance(args, dict):
                    raise AnalysisError("Campo 'args' em tool_calls deve ser objeto.")
                validated_calls.append({"name": name.strip(), "args": args})

            normalized["tool_calls"] = validated_calls
            # Campos legados para compatibilidade externa
            normalized["tool_using_exec"] = [c["name"] for c in validated_calls]
            normalized["data_using_util"] = validated_calls[0]["args"] if validated_calls else {}
            return normalized

        except Exception as e:
            raise AnalysisError(f"Erro na análise: {str(e)}")
