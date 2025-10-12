
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
        
        try:
            for tool_name in tools:
                # Executa ferramenta com parâmetros fornecidos
                result = self.registry.execute(tool_name, **params)
                results[tool_name] = result
            
            return {
                'success': True,
                'results': results,
                'executed_tools': tools
            }
            
        except Exception as e:
            raise ExecutionError(f"Erro na execução: {str(e)}")
