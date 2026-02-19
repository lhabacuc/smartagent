from typing import Dict, Any
from .exceptions import AnalysisError
from .utils import safe_json

class Analyzer:
    """Analisa a intenção do usuário e determina ações necessárias"""

    def __init__(self, llm_client, info: str = ""):
        self.llm = llm_client
        self.info = info

    def analyze(self, user_prompt: str, tools_description: str) -> Dict[str, Any]:
        """Analisa o prompt e retorna plano de execução"""

        info_section = f"\n\nAdditional instructions:\n{self.info}\n" if self.info else ""

        system_prompt = f"""Your task is to analyze the user request and identify:
1. Which local functions should be executed
2. Which arguments each function should receive

{info_section}
Available tools:
{tools_description}

Return ONLY valid JSON (no markdown, no extra text) in this format:
{{"isValid": true, "tool_calls": [{{"name": "function_name", "args": {{}}}}]}}

If the request cannot be handled, return:
{{"isValid": false, "reason": "reason"}}

Example:
User: "Which cheap products are available?"
Response: {{"isValid": true, "tool_calls": [{{"name": "get_products", "args": {{"max_price": 100}}}}]}}

Do not reveal internal agent behavior to the user.
"""

        try:
            response = self.llm.chat(system_prompt, user_prompt)
            analysis = safe_json(response)
            if analysis is None:
                raise AnalysisError(
                    "LLM analysis response must be strict JSON without extra text."
                )

            if not isinstance(analysis, dict):
                raise AnalysisError("Analysis JSON must be an object.")

            is_valid = bool(analysis.get("isValid", True))
            normalized: Dict[str, Any] = {"isValid": is_valid}

            if not is_valid:
                normalized["reason"] = analysis.get("reason", "Invalid request")
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
                    raise AnalysisError("Legacy field 'tool_using_exec' must be a list.")
                if not isinstance(legacy_args, dict):
                    raise AnalysisError("Legacy field 'data_using_util' must be an object.")
                tool_calls = [{"name": name, "args": legacy_args} for name in legacy_tools]

            if not isinstance(tool_calls, list):
                raise AnalysisError("Field 'tool_calls' must be a list.")

            validated_calls = []
            for item in tool_calls:
                if not isinstance(item, dict):
                    raise AnalysisError("Each item in 'tool_calls' must be an object.")
                name = item.get("name")
                args = item.get("args", {})
                if not isinstance(name, str) or not name.strip():
                    raise AnalysisError("Field 'name' in tool_calls must be a non-empty string.")
                if not isinstance(args, dict):
                    raise AnalysisError("Field 'args' in tool_calls must be an object.")
                validated_calls.append({"name": name.strip(), "args": args})

            normalized["tool_calls"] = validated_calls
            # Campos legados para compatibilidade externa
            normalized["tool_using_exec"] = [c["name"] for c in validated_calls]
            normalized["data_using_util"] = validated_calls[0]["args"] if validated_calls else {}
            return normalized

        except Exception as e:
            raise AnalysisError(f"Analysis error: {str(e)}")
