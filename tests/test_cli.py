import io
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from agent import cli
from agent.core.registry import ToolRegistry


class DummyAgent:
    last_instance = None

    def __init__(self, **_kwargs):
        self.registry = ToolRegistry()
        DummyAgent.last_instance = self

    def tool(self, func=None, name=None):
        def decorator(f):
            self.registry.register(f, name)
            return f

        if func is None:
            return decorator
        return decorator(func)

    def chat(self, _prompt):
        return "ok"


class CLITests(unittest.TestCase):
    def test_main_without_command_prints_help(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main([])
        self.assertEqual(code, 0)
        self.assertIn("CLI oficial do SmartAgent", out.getvalue())

    def test_env_check_masks_api_key(self):
        out = io.StringIO()
        with patch.dict("os.environ", {"SMARTAGENT_API_KEY": "abcdef123456"}, clear=False):
            with redirect_stdout(out):
                code = cli.main(["env-check"])
        self.assertEqual(code, 0)
        self.assertIn("SMARTAGENT_API_KEY: SET (ab***56)", out.getvalue())

    def test_doctor_ollama_without_key_is_ok(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["doctor", "--provider", "ollama"])
        self.assertEqual(code, 0)
        self.assertIn("status: OK", out.getvalue())

    def test_doctor_reports_missing_api_key(self):
        out = io.StringIO()
        with patch.dict("os.environ", {}, clear=True):
            with redirect_stdout(out):
                code = cli.main(["doctor", "--provider", "openai"])
        self.assertEqual(code, 2)
        self.assertIn("api_key: AUSENTE", out.getvalue())
        self.assertIn("api_key_source: missing", out.getvalue())

    def test_doctor_rejects_invalid_provider(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["doctor", "--provider", "nao-existe"])
        self.assertEqual(code, 1)
        self.assertIn("provider inválido 'nao-existe'", out.getvalue())
        self.assertIn("Providers suportados:", out.getvalue())

    def test_doctor_accepts_xai_alias(self):
        out = io.StringIO()
        with patch.dict("os.environ", {"XAI_API_KEY": "x-test-key"}, clear=True):
            with redirect_stdout(out):
                code = cli.main(["doctor", "--provider", "xai"])
        self.assertEqual(code, 0)
        self.assertIn("provider_input: xai", out.getvalue())
        self.assertIn("provider: grok", out.getvalue())
        self.assertIn("api_key_source: env:XAI_API_KEY", out.getvalue())

    def test_doctor_accepts_google_gemini_alias(self):
        out = io.StringIO()
        with patch.dict("os.environ", {"GEMINI_API_KEY": "g-test-key"}, clear=True):
            with redirect_stdout(out):
                code = cli.main(["doctor", "--provider", "google-gemini"])
        self.assertEqual(code, 0)
        self.assertIn("provider_input: google-gemini", out.getvalue())
        self.assertIn("provider: gemini", out.getvalue())
        self.assertIn("api_key_source: env:GEMINI_API_KEY", out.getvalue())

    def test_doctor_shows_effective_model_from_env(self):
        out = io.StringIO()
        with patch.dict("os.environ", {"SMARTAGENT_MODEL": "gpt-4.1-mini", "OPENAI_API_KEY": "o-key"}, clear=True):
            with redirect_stdout(out):
                code = cli.main(["doctor", "--provider", "openai"])
        self.assertEqual(code, 0)
        self.assertIn("model: gpt-4.1-mini", out.getvalue())
        self.assertIn("model_source: env:SMARTAGENT_MODEL", out.getvalue())

    def test_run_example_list(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["run-example", "--list"])
        self.assertEqual(code, 0)
        self.assertIn("minimal_agent", out.getvalue())

    def test_run_example_executes_subprocess(self):
        class DummyCompleted:
            returncode = 0

        with patch("agent.cli.subprocess.run", return_value=DummyCompleted()) as mocked_run:
            code = cli.main(["run-example", "minimal_agent"])
        self.assertEqual(code, 0)
        mocked_run.assert_called_once()

    def test_interactive_slash_command_clear_is_not_sent_to_chat(self):
        fake_agent = Mock()
        fake_agent.clear_history = Mock()
        fake_agent.chat = Mock(return_value="ok")
        fake_agent.registry.get_tools_list.return_value = []

        out = io.StringIO()
        with patch("builtins.input", side_effect=["/clear", "sair"]), redirect_stdout(out):
            cli.run_interactive(fake_agent)

        fake_agent.clear_history.assert_called_once()
        fake_agent.chat.assert_not_called()

    def test_interactive_slash_command_cl_clears_terminal(self):
        fake_agent = Mock()
        fake_agent.chat = Mock(return_value="ok")
        fake_agent.registry.get_tools_list.return_value = []

        out = io.StringIO()
        with patch("agent.cli.subprocess.run") as mocked_run:
            with patch("builtins.input", side_effect=["/cl", "sair"]), redirect_stdout(out):
                cli.run_interactive(fake_agent)

        mocked_run.assert_called_once()
        called_args = mocked_run.call_args.args[0]
        self.assertIn(called_args[0], {"clear", "cls"})
        fake_agent.chat.assert_not_called()

    def test_interactive_slash_command_exec_runs_shell(self):
        fake_agent = Mock()
        fake_agent.chat = Mock(return_value="ok")
        fake_agent.registry.get_tools_list.return_value = []

        completed = Mock()
        completed.stdout = "hello\n"
        completed.stderr = ""
        completed.returncode = 0

        out = io.StringIO()
        with patch("agent.cli.subprocess.run", return_value=completed) as mocked_run:
            with patch("builtins.input", side_effect=['/exec "echo hello"', "sair"]), redirect_stdout(out):
                cli.run_interactive(fake_agent)

        mocked_run.assert_called_once_with(
            "echo hello",
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertIn("hello", out.getvalue())
        self.assertIn("[exit_code=0]", out.getvalue())
        fake_agent.chat.assert_not_called()

    def test_interactive_disable_command_calls_agent_method(self):
        fake_agent = Mock()
        fake_agent.chat = Mock(return_value="ok")
        fake_agent.disable_tool = Mock(return_value=True)
        fake_agent.get_disabled_tools = Mock(return_value=["somar"])
        fake_agent.registry.get_tools_list.return_value = ["somar"]

        out = io.StringIO()
        with patch("builtins.input", side_effect=["/disable somar", "sair"]), redirect_stdout(out):
            cli.run_interactive(fake_agent)

        fake_agent.disable_tool.assert_called_once_with("somar")
        fake_agent.chat.assert_not_called()

    def test_print_agent_response_plain_mode(self):
        out = io.StringIO()
        with patch.object(cli.sys, "stdout", out):
            cli._print_agent_response("teste")
        self.assertIn("Agente: teste", out.getvalue())

    def test_chat_tools_file_registers_public_functions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_path = f"{tmpdir}/tools_ok.py"
            with open(tools_path, "w", encoding="utf-8") as fh:
                fh.write(
                    textwrap.dedent(
                        """
                        def somar(a: int, b: int):
                            return a + b
                        """
                    ).strip()
                )

            out = io.StringIO()
            with patch("agent.core.agent.Agent", DummyAgent), redirect_stdout(out):
                code = cli.main(["chat", "--prompt", "oi", "--tools-file", tools_path])

        self.assertEqual(code, 0)
        self.assertIn("Tools externas carregadas: somar", out.getvalue())
        self.assertIn("somar", DummyAgent.last_instance.registry.get_tools_list())

    def test_chat_tools_file_missing_path_returns_error(self):
        out = io.StringIO()
        with patch("agent.core.agent.Agent", DummyAgent), redirect_stdout(out):
            code = cli.main(["chat", "--prompt", "oi", "--tools-file", "inexistente_tools.py"])

        self.assertEqual(code, 1)
        self.assertIn("Erro ao carregar tools externas", out.getvalue())
        self.assertIn("Arquivo de tools não encontrado", out.getvalue())

    def test_chat_tools_file_without_tools_returns_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tools_path = f"{tmpdir}/tools_empty.py"
            with open(tools_path, "w", encoding="utf-8") as fh:
                fh.write("VALOR = 1\n")

            out = io.StringIO()
            with patch("agent.core.agent.Agent", DummyAgent), redirect_stdout(out):
                code = cli.main(["chat", "--prompt", "oi", "--tools-file", tools_path])

        self.assertEqual(code, 1)
        self.assertIn("Erro ao carregar tools externas", out.getvalue())
        self.assertIn("Nenhuma tool carregada", out.getvalue())


if __name__ == "__main__":
    unittest.main()
