import signal
import sys


def show_env_help() -> None:
    print("=== Variáveis de Ambiente ===")
    print("Você pode configurar o agente usando as seguintes variáveis de ambiente:")
    print("1. OPENAI_API_KEY: Chave API para OpenAI")
    print("2. GEMINI_API_KEY: Chave API para Google Gemini")
    print("3. GROQ_API_KEY: Chave API para Groq")
    print("4. OLLAMA_API_KEY: Chave API para Ollama")
    print("5. SMARTAGENT_PROVIDER: Provider padrão (ex: groq, openai)")
    print("6. SMARTAGENT_MODEL: Modelo padrão global")
    print("7. SMARTAGENT_TIMEOUT: Timeout HTTP em segundos")
    print("8. SMARTAGENT_RETRIES: Quantidade de retries HTTP")
    print("\nCompatibilidade legada: LLM ainda é suportada.")


def show_help() -> None:
    print("=== Antes de executar ===")
    print("1. Defina provider/modelo do LLM")
    print("2. (Opcional) Defina a chave API via variável de ambiente ou parâmetro")
    print("3. (Opcional) Forneça instruções adicionais via parâmetro 'info'")
    show_env_help()
    print("\n=== Registrar ferramentas ===")
    print("Use o decorador @agent.tool para registrar funções que o agente pode usar.")
    print("\n=== Executar consultas ===")
    print("Use agent.process(prompt) para obter resposta detalhada ou agent.chat(prompt) para resposta simples.")


def show_common_errors() -> None:
    print("=== Possíveis Erros e Soluções ===")
    print("1. Erro: 'Nenhuma ferramenta registrada.'")
    print("   Solução: registre ao menos uma ferramenta usando @agent.tool.")
    print("\n2. Erro: 'Chave API inválida ou ausente.'")
    print("   Solução: verifique variáveis de ambiente e chave informada.")
    print("\n3. Erro: 'Resposta inválida do LLM.'")
    print("   Solução: ajuste prompt ou conectividade com o provedor.")
    print("\n4. Erro: 'Timeout ao executar ferramenta.'")
    print("   Solução: aumente timeout ou otimize a função.")


def run_interactive(agent) -> None:
    def signal_handler(sig, frame):
        print("\nEncerrando o agente. Até logo!")
        sys.exit(0)

    def is_exit_command(command: str) -> bool:
        return command.lower() in ["sair", "exit", "quit", "q", "fim", "end"] and len(command.strip()) <= 4

    signal.signal(signal.SIGINT, signal_handler)
    print("=== Modo Interativo do Agente ===")
    print("Digite 'sair' para encerrar.")
    while True:
        user_input = input("\n[your input]>>: ")
        if is_exit_command(user_input):
            print("Encerrando o agente. Até logo!")
            break
        response = agent.chat(user_input)
        print(f"Agente: {response}")
