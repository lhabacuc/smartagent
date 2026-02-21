import inspect
from typing import Dict, Any, List
from .registry import ToolRegistry


class Executor:
    """Executa ferramentas baseado no plano de análise"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def execute(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa chamadas de ferramentas e retorna resultados estruturados."""
        call_results = []
        results: Dict[str, Any] = {}
        executed_tools: List[str] = []

        if not tool_calls:
            return {
                'success': True,
                'results': {},
                'call_results': [],
                'executed_tools': []
            }

        available_tools = self.registry.list_tools()

        for call in tool_calls:
            tool_name = call.get("name") if isinstance(call, dict) else None
            raw_args = call.get("args", {}) if isinstance(call, dict) else {}

            entry = {
                "name": tool_name,
                "args": raw_args,
                "ok": False,
                "result": None,
                "error": None,
            }

            if not isinstance(tool_name, str) or not tool_name:
                entry["error"] = "Nome da ferramenta inválido."
                call_results.append(entry)
                continue

            if tool_name in available_tools:
                try:
                    if not isinstance(raw_args, dict):
                        raise TypeError("args deve ser um objeto JSON.")

                    func = available_tools[tool_name]
                    sig = inspect.signature(func)
                    bound = sig.bind(**raw_args)
                    bound.apply_defaults()

                    result = self.registry.execute(tool_name, **bound.arguments)
                    results[tool_name] = result
                    executed_tools.append(tool_name)
                    entry["ok"] = True
                    entry["result"] = result
                except Exception as exc:
                    entry["error"] = f"Erro ao executar: {str(exc)}"
            else:
                entry["error"] = f"Ferramenta '{tool_name}' não registrada."

            call_results.append(entry)

        return {
            'success': all(r["ok"] for r in call_results) if call_results else True,
            'results': results,
            'call_results': call_results,
            'executed_tools': executed_tools
        }
