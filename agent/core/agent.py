
from typing import Dict, Any, Callable, Optional
from .registry import ToolRegistry, tool
from .analyzer import Analyzer
from .executor import Executor
from .responder import Responder
from ..integrations import get_llm_client

class Agent:
    """Agente inteligente com execução em 3 fases"""
    
    def __init__(self, model: str = "groq", api_key: Optional[str] = None, info: str = "", enable_history: bool = False, history_limit: int = 20):
        """
        Inicializa agente
        
        Args:
            model: Provider do LLM (groq, openai, gemini, grok, ollama, llama)
            api_key: Chave API (opcional, pode usar variável de ambiente)
            info: Instruções adicionais para o agente (contexto, comportamento, etc.)
            enable_history (bool): Ativa/desativa histórico de interações
            history_limit (int): Número máximo de mensagens no histórico
        """
        self.registry = ToolRegistry()
        self.llm_client = get_llm_client(model, api_key)
        self.info = info
        self.enable_history = enable_history or False
        self.history_limit = history_limit or 5
        self.history = []
        self.analyzer = Analyzer(self.llm_client, info=info)
        self.executor = Executor(self.registry)
        self.responder = Responder(self.llm_client, self, info=info, enable_history=enable_history)

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
        
        # Fase 2: Execução
        if analysis.get('isValid', False):
            execution_data = self.executor.execute(
                analysis['tool_using_exec'],
                analysis['data_using_util']
            )
        else:
            execution_data = {
                'executed_tools': [],
                'used_data': {}
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
        
    
    def chat(self, prompt: str) -> str:
        """Atalho para obter apenas a resposta final"""
        result = self.process(prompt)
        self._add_to_history(result)
        return result['final_response']

    def help(self):
        """como usar o agente"""
        print("=== Antes de executar ===")
        print("1. Defina o provider do LLM (ex: groq, openai, gemini, grok, ollama, llama)")
        print("2. (Opcional) Defina a chave API via variável de ambiente ou parâmetro")
        print("3. (Opcional) Forneça instruções adicionais via parâmetro 'info'")
        self.help_var()
        print("\n=== Registrar ferramentas ===")
        print("Use o decorador @agent.tool para registrar funções que o agente pode usar.")
        print("Exemplo:")
        print("@agent.tool")
        print("def minha_ferramenta(param1: str, param2: int = 0) -> str:")
        print('    """Descrição da ferramenta"""')
        print("    return f'Você chamou minha_ferramenta com {param1} e {param2}'")
        print("\n=== Executar consultas ===")
        print("Use agent.process(prompt) para obter resposta detalhada ou agent.chat(prompt) para resposta simples.")
        print("Exemplo:")
        print("response = agent.process('Sua pergunta aqui')")
        print("print(response['final_response'])  # Resposta final")    
        print("print(response['executed_tools'])  # Ferramentas executadas")
        print("print(response['used_data'])       # Dados utilizados na consulta")
        print("\n=== Exemplo Completo ===")
        print("agent = Agent()")
        print("response = agent.process('Sua pergunta aqui')")
        print("print(response['final_response'])  # Resposta final")
        print("print(response['executed_tools'])  # Ferramentas executadas")
        print("print(response['used_data'])       # Dados utilizados na consulta")
        print("\n=== Divirta-se! ===")
        print("Use o agente com responsabilidade e aproveite suas capacidades!")
    
    def help_var():
        """variaveis de ambiente"""
        print("=== Variáveis de Ambiente ===")
        print("Você pode configurar o agente usando as seguintes variáveis de ambiente:")
        print("1. OPENAI_API_KEY: Chave API para OpenAI")
        print("2. GEMINI_API_KEY: Chave API para Google Gemini")
        print("3. GROQ_API_KEY: Chave API para Groq")
        print("4. OLLAMA_API_KEY: Chave API para Ollama")
        print("5. LLM: Define a LLM (ex: gpt-o4-mini, gemini-2.0)")
        print("\nExemplo de uso no terminal:")
        print("export OPENAI_API_KEY='sua_chave_aqui'")
        print("export LLM='gpt-4o-mini'")
        print("\nEssas variáveis permitem que você configure o agente sem precisar passar parâmetros diretamente no código.")
        print("Certifique-se de manter suas chaves API seguras e não compartilhá-las publicamente.")
    
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
        """lista possiveis erros"""
        print("=== Possíveis Erros e Soluções ===")
        print("1. Erro: 'Nenhuma ferramenta registrada.'")
        print("   Solução: Certifique-se de registrar pelo menos uma ferramenta usando @agent.tool.")
        print("\n2. Erro: 'Chave API inválida ou ausente.'")
        print("   Solução: Verifique se a chave API está correta e definida na variável de ambiente ou parâmetro.")
        print("\n3. Erro: 'Resposta inválida do LLM.'")
        print("   Solução: Tente ajustar o prompt ou verificar a conectividade com o serviço LLM.")
        print("\n4. Erro: 'Timeout ao executar ferramenta.'")
        print("   Solução: Aumente o tempo limite na implementação da ferramenta ou otimize a função.")
        print("\n5. Erro: 'Ferramenta não encontrada.'")
        print("   Solução: Verifique se o nome da ferramenta está correto e foi registrada.")
        print("\n6. Erro: 'Parâmetros inválidos para a ferramenta.'")
        print("   Solução: Confirme que os parâmetros fornecidos correspondem à assinatura da função.")
        print("\n7. Erro: 'Limite de taxa excedido no serviço LLM.'")
        print("   Solução: Aguarde um momento antes de tentar novamente ou verifique seu plano de uso.")
    
    def reset(self):
        """Reseta o agente"""
        self.registry = ToolRegistry()
        self.analyzer = Analyzer(self.llm_client, info=self.info)
        self.executor = Executor(self.registry)
        self.responder = Responder(self.llm_client, info=self.info)
    
    def run(self):
        """Inicia modo interativo"""
        import readline
        import sys
        import signal
        def signal_handler(sig, frame):
            print("\nEncerrando o agente. Até logo!")
            sys.exit(0)
        def is_exit_command(command: str) -> bool:
            return command.lower() in ['sair', 'exit', 'quit', 'q', 'fim', 'end'] and len(command.strip()) <= 4
        signal.signal(signal.SIGINT, signal_handler)
        print("=== Modo Interativo do Agente ===")
        print("Digite 'sair' para encerrar.")
        while True:
            user_input = input("\n[your input]>>: ")
            if is_exit_command(user_input):
                print("Encerrando o agente. Até logo!")
                break
            response = self.chat(user_input)
            print(f"Agente: {response}")