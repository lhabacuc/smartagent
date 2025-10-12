
from typing import Dict, Any, Callable, Optional
from .registry import ToolRegistry, tool
from .analyzer import Analyzer
from .executor import Executor
from .responder import Responder
from ..integrations import get_llm_client

class Agent:
    """Agente inteligente com execução em 3 fases"""
    
    def __init__(self, model: str = "groq", api_key: Optional[str] = None, info: str = ""):
        """
        Inicializa agente
        
        Args:
            model: Provider do LLM (groq, openai, gemini, grok, ollama, llama)
            api_key: Chave API (opcional, pode usar variável de ambiente)
            info: Instruções adicionais para o agente (contexto, comportamento, etc.)
        """
        self.registry = ToolRegistry()
        self.llm_client = get_llm_client(model, api_key)
        self.info = info
        
        self.analyzer = Analyzer(self.llm_client, info=info)
        self.executor = Executor(self.registry)
        self.responder = Responder(self.llm_client, info=info)
    
    def tool(self, func: Callable = None, name: str = None):
        """Decorador para registrar ferramentas"""
        def decorator(f: Callable) -> Callable:
            self.registry.register(f, name)
            return f
        
        if func is None:
            return decorator
        return decorator(func)
    
    def process(self, user_prompt: str) -> Dict[str, Any]:
        """Processa prompt completo em 3 fases"""
        
        # Fase 1: Análise
        tools_desc = self.registry.get_tools_description()
        analysis = self.analyzer.analyze(user_prompt, tools_desc)
        
        if not analysis.get('isValid', False):
            return {
                'final_response': f"Não consegui processar: {analysis.get('reason', 'Pedido inválido')}",
                'executed_tools': [],
                'used_data': {}
            }
        
        # Fase 2: Execução
        execution_data = self.executor.execute(
            analysis['tool_using_exec'],
            analysis['data_using_util']
        )
        
        # Fase 3: Resposta
        final_response = self.responder.respond(user_prompt, execution_data)
        
        return {
            'final_response': final_response,
            'executed_tools': execution_data['executed_tools'],
            'used_data': analysis['data_using_util']
        }
    
    def chat(self, prompt: str) -> str:
        """Atalho para obter apenas a resposta final"""
        result = self.process(prompt)
        return result['final_response']
