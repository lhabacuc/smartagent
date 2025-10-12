
from typing import Callable, Dict, Any, List
import inspect

class ToolRegistry:
    """Registro de ferramentas disponíveis para o agente"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(self, func: Callable, name: str = None) -> Callable:
        """Registra uma função como ferramenta"""
        tool_name = name or func.__name__
        self._tools[tool_name] = func
        
        # Extrai metadados da função
        sig = inspect.signature(func)
        params = {}
        for param_name, param in sig.parameters.items():
            params[param_name] = {
                'type': param.annotation if param.annotation != inspect.Parameter.empty else 'any',
                'default': param.default if param.default != inspect.Parameter.empty else None
            }
        
        self._metadata[tool_name] = {
            'name': tool_name,
            'doc': func.__doc__ or '',
            'params': params
        }
        
        return func
    
    def execute(self, tool_name: str, **kwargs) -> Any:
        """Executa uma ferramenta registrada"""
        if tool_name not in self._tools:
            raise ValueError(f"Ferramenta '{tool_name}' não encontrada")
        
        return self._tools[tool_name](**kwargs)
    
    def get_tools_description(self) -> str:
        """Retorna descrição formatada de todas as ferramentas"""
        descriptions = []
        for name, meta in self._metadata.items():
            params_str = ', '.join([f"{k}: {v['type']}" for k, v in meta['params'].items()])
            desc = f"- {name}({params_str})"
            if meta['doc']:
                desc += f" - {meta['doc'].strip()}"
            descriptions.append(desc)
        return '\n'.join(descriptions)
    
    def get_tools_list(self) -> List[str]:
        """Retorna lista de nomes de ferramentas"""
        return list(self._tools.keys())

# Decorador global para facilitar uso
def tool(func: Callable) -> Callable:
    """Decorador para marcar função como ferramenta"""
    func._is_tool = True
    return func
