
from typing import Dict, Any, List
from .registry import ToolRegistry
from .exceptions import ExecutionError


class Executor:
    """Executa ferramentas baseado no plano de análise"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def execute(self, tools: List[str], params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa ferramentas e retorna resultados agregados"""
        results = {}
        executed_tools = []

        if not tools:
            return {
                'success': True,
                'results': {},
                'executed_tools': []
            }

        for tool_name in tools:
            if hasattr(self.registry, tool_name) or tool_name in getattr(self.registry, '_tools', {}):
                try:
                    result = self.registry.execute(tool_name, **params)
                    results[tool_name] = result
                    executed_tools.append(tool_name)
                except Exception as e:
                    results[tool_name] = f"Erro ao executar: {str(e)}"
            else:
                results[tool_name] = f"Ferramenta '{tool_name}' não registrada. Nenhuma ação executada."
        
        return {
            'success': True,
            'results': results,
            'executed_tools': executed_tools
        }