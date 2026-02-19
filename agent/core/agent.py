import warnings
from typing import Dict, Any, Callable, Optional
from .registry import ToolRegistry, tool
from .analyzer import Analyzer
from .executor import Executor
from .responder import Responder
from .config import AgentConfig
from ..integrations import get_llm_client

class Agent:
    """Agente inteligente com execução em 3 fases"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        info: str = "",
        enable_history: bool = False,
        history_limit: int = 20,
        provider: Optional[str] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
    ):
        """
        Inicializa agente
        
        Args:
            model: Modelo do LLM (legado: também aceita provider)
            api_key: Chave API (opcional, pode usar variável de ambiente)
            info: Instruções adicionais para o agente (contexto, comportamento, etc.)
            enable_history (bool): Ativa/desativa histórico de interações
            history_limit (int): Número máximo de mensagens no histórico
            provider: Provider do LLM (groq, openai, gemini, grok, ollama, llama)
            timeout: Timeout HTTP em segundos
            retries: Número de retries HTTP por requisição
        """
        self.config = AgentConfig.from_inputs(
            provider=provider,
            model=model,
            api_key=api_key,
            info=info,
            enable_history=enable_history,
            history_limit=history_limit,
            timeout=timeout,
            retries=retries,
        )
        self.registry = ToolRegistry()
        self.llm_client = get_llm_client(
            provider=self.config.provider,
            api_key=self.config.api_key,
            model=self.config.model,
            timeout=self.config.timeout,
            retries=self.config.retries,
        )
        self.info = self.config.info
        self.enable_history = self.config.enable_history
        self.history_limit = self.config.history_limit
        self.history = []
        self._disabled_tools = set()
        self.analyzer = Analyzer(self.llm_client, info=self.info)
        self.executor = Executor(self.registry)
        self.responder = Responder(
            self.llm_client,
            self,
            info=self.info,
            enable_history=self.enable_history,
        )

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

        tools_desc = self.registry.get_tools_description()

        # Quando não há ferramentas registradas, evita análise JSON estrita.
        if not tools_desc.strip():
            analysis = {
                "isValid": True,
                "tool_calls": [],
                "tool_using_exec": [],
                "data_using_util": {},
                "reason": "No tools registered; direct response mode.",
            }
            execution_data = {
                'executed_tools': [],
                'used_data': {},
                'results': {},
                'call_results': [],
                'success': True,
            }
        else:
            # Fase 1: Análise
            analysis = self.analyzer.analyze(user_prompt, tools_desc)

            # Fase 2: Execução
            if analysis.get('isValid', False):
                tool_calls = analysis.get("tool_calls")
                if tool_calls is None:
                    # Compatibilidade com formato antigo de análise
                    legacy_tools = analysis.get("tool_using_exec", [])
                    legacy_args = analysis.get("data_using_util", {})
                    tool_calls = [{"name": t, "args": legacy_args} for t in legacy_tools]

                allowed_calls = []
                blocked_results = []
                for call in tool_calls:
                    name = call.get("name") if isinstance(call, dict) else None
                    if isinstance(name, str) and name in self._disabled_tools:
                        blocked_results.append(
                            {
                                "name": name,
                                "args": call.get("args", {}),
                                "ok": False,
                                "result": None,
                                "error": f"Ferramenta '{name}' está desativada.",
                            }
                        )
                    else:
                        allowed_calls.append(call)

                execution_data = self.executor.execute(allowed_calls)
                if blocked_results:
                    execution_data["call_results"].extend(blocked_results)
                    execution_data["success"] = all(r["ok"] for r in execution_data["call_results"])
            else:
                execution_data = {
                    'executed_tools': [],
                    'used_data': {},
                    'results': {},
                    'call_results': [],
                    'success': False,
                }
        
        # Fase 3: Resposta
        final_response = self.responder.respond(user_prompt, execution_data)
        result = {
            'final_response': final_response,
            'executed_tools': execution_data['executed_tools'],
            'used_data': analysis.get('data_using_util', {}),
            'user_prompt': user_prompt,
            'analysis': analysis,
            'execution_data': execution_data
        }

        if self.enable_history:
            self._add_to_history(result)

        return result
    def _add_to_history(self, entry: dict):
        self.history.append(entry)
        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit:]

    def get_history(self) -> list:
        """Retorna o histórico de interações."""
        return self.history.copy()

    def clear_history(self):
        """Limpa o histórico de interações."""
        self.history = []

    def disable_tool(self, name: str) -> bool:
        """Desativa uma ferramenta registrada para novas execuções."""
        if name in self.registry.list_tools():
            self._disabled_tools.add(name)
            return True
        return False

    def enable_tool(self, name: str) -> bool:
        """Reativa uma ferramenta previamente desativada."""
        if name in self._disabled_tools:
            self._disabled_tools.remove(name)
            return True
        return False

    def is_tool_enabled(self, name: str) -> bool:
        """Retorna se uma ferramenta está ativa."""
        return name not in self._disabled_tools

    def get_disabled_tools(self) -> list:
        """Lista ferramentas atualmente desativadas."""
        return sorted(self._disabled_tools)
        
    
    def chat(self, prompt: str) -> str:
        """Atalho para obter apenas a resposta final"""
        result = self.process(prompt)
        return result['final_response']

    def help(self):
        """Utilitário legado de ajuda (migrado para agent.cli.show_help)."""
        warnings.warn(
            "Agent.help() is deprecated; use agent.cli.show_help().",
            DeprecationWarning,
            stacklevel=2,
        )
        from ..cli import show_help

        show_help()
    
    def help_var(self):
        """Utilitário legado de env help (migrado para agent.cli.show_env_help)."""
        warnings.warn(
            "Agent.help_var() is deprecated; use agent.cli.show_env_help().",
            DeprecationWarning,
            stacklevel=2,
        )
        from ..cli import show_env_help

        show_env_help()
    
    def list_tools(self):
        """Lista ferramentas registradas"""
        tools = self.registry.list_tools()
        if not tools:
            print("Nenhuma ferramenta registrada.")
            return
        print("=== Ferramentas Registradas ===")
        for name, func in tools.items():
            doc = func.__doc__ or "Sem descrição"
            print(f"- {name}: {doc}")
    
    def pociveis_erros(self):
        """Utilitário legado de erros comuns (migrado para agent.cli.show_common_errors)."""
        warnings.warn(
            "Agent.pociveis_erros() is deprecated; use agent.cli.show_common_errors().",
            DeprecationWarning,
            stacklevel=2,
        )
        from ..cli import show_common_errors

        show_common_errors()
    
    def reset(self):
        """Reseta o agente"""
        self.registry = ToolRegistry()
        self._disabled_tools = set()
        self.analyzer = Analyzer(self.llm_client, info=self.info)
        self.executor = Executor(self.registry)
        self.responder = Responder(
            self.llm_client,
            self,
            info=self.info,
            enable_history=self.enable_history
        )
    
    def run(self):
        """Utilitário legado de modo interativo (migrado para agent.cli.run_interactive)."""
        warnings.warn(
            "Agent.run() is deprecated; use agent.cli.run_interactive(agent).",
            DeprecationWarning,
            stacklevel=2,
        )
        from ..cli import run_interactive

        run_interactive(self)
