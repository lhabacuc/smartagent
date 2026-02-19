import argparse
import os
import signal
import subprocess
import sys
import time
import readline
from pathlib import Path
from typing import Dict, List, Optional

from .core.config import AgentConfig
from .integrations import normalize_provider
from .integrations.config import resolve_api_key, resolve_model


def _print_agent_response(response: str) -> None:
    text = response or ""
    prefix = "Agente: "
    should_animate = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    if should_animate:
        sys.stdout.write(prefix)
        sys.stdout.flush()
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.01)
        sys.stdout.write("\n")
        sys.stdout.flush()
        return
    print(f"{prefix}{text}")


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

    def terminal_clear() -> None:
        cmd = ["cls"] if os.name == "nt" else ["clear"]
        subprocess.run(cmd, check=False)

    def normalize_exec_arg(raw: str) -> str:
        value = raw.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1].strip()
        return value

    def handle_command(command: str) -> bool:
        command = command.strip()
        if not command.startswith("/"):
            return False

        parts = command[1:].split()
        name = (parts[0].lower() if parts else "")

        if name in {"clear", "cls"}:
            agent.clear_history()
            print("Histórico limpo.")
            return True
        if name == "cl":
            terminal_clear()
            return True
        if name in {"help", "h"}:
            print("Comandos disponíveis: /clear, /cl, /exec, /enable, /disable, /help, /tools, /exit")
            return True
        if name == "tools":
            tools = agent.registry.get_tools_list()
            if tools:
                disabled = set(agent.get_disabled_tools()) if hasattr(agent, "get_disabled_tools") else set()
                labeled = []
                for tool_name in tools:
                    status = "off" if tool_name in disabled else "on"
                    labeled.append(f"{tool_name}({status})")
                print("Ferramentas:", ", ".join(labeled))
            else:
                print("Nenhuma ferramenta registrada.")
            return True
        if name in {"disable", "desativar"}:
            if len(parts) < 2:
                print("Uso: /disable <nome_da_funcao>")
                return True
            tool_name = parts[1]
            if not hasattr(agent, "disable_tool"):
                print("Operação não suportada neste agente.")
                return True
            if agent.disable_tool(tool_name):
                print(f"Ferramenta desativada: {tool_name}")
            else:
                print(f"Ferramenta não encontrada: {tool_name}")
            return True
        if name in {"enable", "ativar"}:
            if len(parts) < 2:
                print("Uso: /enable <nome_da_funcao>")
                return True
            tool_name = parts[1]
            if not hasattr(agent, "enable_tool"):
                print("Operação não suportada neste agente.")
                return True
            if agent.enable_tool(tool_name):
                print(f"Ferramenta ativada: {tool_name}")
            else:
                print(f"Ferramenta já ativa ou desconhecida: {tool_name}")
            return True
        if name == "exec":
            raw_exec = command[len("/exec"):].strip()
            exec_cmd = normalize_exec_arg(raw_exec)
            if not exec_cmd:
                print("Uso: /exec \"comando\"")
                return True
            completed = subprocess.run(
                exec_cmd,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.stdout:
                print(completed.stdout.rstrip())
            if completed.stderr:
                print(completed.stderr.rstrip())
            print(f"[exit_code={completed.returncode}]")
            return True
        if name in {"exit", "quit"}:
            print("Encerrando o agente. Até logo!")
            raise SystemExit(0)

        print(f"Comando desconhecido: /{name or ''}")
        print("Use /help para listar comandos.")
        return True

    while True:
        user_input = input("\n[your input]>>: ")
        if is_exit_command(user_input):
            print("Encerrando o agente. Até logo!")
            break
        if user_input.strip().startswith("/"):
            try:
                if handle_command(user_input):
                    continue
            except SystemExit:
                break
        response = agent.chat(user_input)
        _print_agent_response(response)


_PROVIDER_API_ENV: Dict[str, str] = {
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "grok": "XAI_API_KEY",
    "llama": "LLAMA_API_KEY",
}


def _mask_secret(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}***{value[-2:]}"


def _show_env_check() -> int:
    vars_to_check = [
        "SMARTAGENT_PROVIDER",
        "SMARTAGENT_MODEL",
        "SMARTAGENT_API_KEY",
        "SMARTAGENT_TIMEOUT",
        "SMARTAGENT_RETRIES",
        "GROQ_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "XAI_API_KEY",
        "LLAMA_API_KEY",
        "LLM",
    ]
    print("=== smartagent env-check ===")
    for name in vars_to_check:
        value = os.getenv(name)
        if value:
            display = _mask_secret(value) if "KEY" in name else value
            print(f"{name}: SET ({display})")
        else:
            print(f"{name}: UNSET")
    return 0


def _resolve_provider(provider: Optional[str]) -> str:
    raw = provider or os.getenv("SMARTAGENT_PROVIDER") or "groq"
    return normalize_provider(raw)


def _show_doctor(
    provider: Optional[str],
    model: Optional[str],
    timeout: Optional[float],
    retries: Optional[int],
    api_key: Optional[str],
) -> int:
    print("=== smartagent doctor ===")
    try:
        provider_name = _resolve_provider(provider)
        cfg = AgentConfig.from_inputs(
            provider=provider_name,
            model=model,
            api_key=api_key,
            timeout=timeout,
            retries=retries,
        )
    except Exception as exc:
        print(f"ERRO de configuração: {exc}")
        return 1

    legacy_env = _PROVIDER_API_ENV.get(provider_name, "")
    effective_api_key = resolve_api_key(provider_name, cfg.api_key, legacy_env) if legacy_env else cfg.api_key
    effective_model = cfg.model or resolve_model(provider_name, default_model="(default interno do provider)")

    print(f"provider: {provider_name}")
    print(f"model: {effective_model}")
    print(f"timeout: {cfg.timeout}")
    print(f"retries: {cfg.retries}")
    if provider_name == "ollama":
        print("api_key: N/A (ollama local)")
        print("status: OK")
        return 0
    if effective_api_key:
        print("api_key: OK")
        print("status: OK")
        return 0

    hint = legacy_env or "SMARTAGENT_API_KEY"
    print(f"api_key: AUSENTE (defina {hint} ou SMARTAGENT_API_KEY)")
    print("status: ATENCAO")
    return 2


def _list_examples(example_dir: Path) -> List[str]:
    if not example_dir.exists():
        return []
    return sorted(p.stem for p in example_dir.glob("*.py") if not p.name.startswith("_"))


def _run_example(example: str, extra_args: List[str]) -> int:
    root_dir = Path(__file__).resolve().parent.parent
    example_dir = root_dir / "examples"
    available = _list_examples(example_dir)
    if example not in available:
        print(f"Exemplo '{example}' não encontrado.")
        if available:
            print("Disponíveis:", ", ".join(available))
        return 1

    script_path = example_dir / f"{example}.py"
    cmd = [sys.executable, str(script_path)]
    if extra_args:
        cmd.extend(extra_args)
    print(f"Executando: {' '.join(cmd)}")
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smartagent",
        description="CLI oficial do SmartAgent",
    )
    subparsers = parser.add_subparsers(dest="command")

    env_parser = subparsers.add_parser("env-check", help="Valida variáveis de ambiente do SmartAgent")
    env_parser.set_defaults(func=lambda _args: _show_env_check())

    doctor_parser = subparsers.add_parser("doctor", help="Diagnostica configuração de provider/modelo")
    doctor_parser.add_argument("--provider", help="Provider (groq, openai, gemini, grok, ollama, llama)")
    doctor_parser.add_argument("--model", help="Modelo opcional")
    doctor_parser.add_argument("--api-key", help="API key opcional")
    doctor_parser.add_argument("--timeout", type=float, help="Timeout HTTP (segundos)")
    doctor_parser.add_argument("--retries", type=int, help="Retries HTTP")
    doctor_parser.set_defaults(
        func=lambda args: _show_doctor(
            provider=args.provider,
            model=args.model,
            timeout=args.timeout,
            retries=args.retries,
            api_key=args.api_key,
        )
    )

    chat_parser = subparsers.add_parser("chat", help="Inicia chat (prompt único ou interativo)")
    chat_parser.add_argument("--provider", help="Provider (default: SMARTAGENT_PROVIDER ou groq)")
    chat_parser.add_argument("--model", help="Modelo opcional")
    chat_parser.add_argument("--api-key", help="API key opcional")
    chat_parser.add_argument("--info", default="", help="Instruções de sistema")
    chat_parser.add_argument("--history", action="store_true", help="Ativa histórico")
    chat_parser.add_argument("--history-limit", type=int, default=20, help="Limite de histórico")
    chat_parser.add_argument("--prompt", help="Executa um prompt único")
    chat_parser.set_defaults(func=_chat_command)

    run_example_parser = subparsers.add_parser("run-example", help="Executa exemplos locais do projeto")
    run_example_parser.add_argument("example", nargs="?", help="Nome do exemplo (sem .py)")
    run_example_parser.add_argument("--list", action="store_true", help="Lista exemplos disponíveis")
    run_example_parser.add_argument("extra_args", nargs=argparse.REMAINDER, help="Args extras para o script")
    run_example_parser.set_defaults(func=_run_example_command)

    return parser


def _chat_command(args: argparse.Namespace) -> int:
    from .core.agent import Agent

    agent = Agent(
        provider=args.provider,
        model=args.model,
        api_key=args.api_key,
        info=args.info,
        enable_history=args.history,
        history_limit=args.history_limit,
    )
    if args.prompt:
        print(agent.chat(args.prompt))
        return 0
    run_interactive(agent)
    return 0


def _run_example_command(args: argparse.Namespace) -> int:
    root_dir = Path(__file__).resolve().parent.parent
    example_dir = root_dir / "examples"
    available = _list_examples(example_dir)

    if args.list or not args.example:
        print("Exemplos disponíveis:")
        for name in available:
            print(f"- {name}")
        return 0 if available else 1
    return _run_example(args.example, args.extra_args)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
