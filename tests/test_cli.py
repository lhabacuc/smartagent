import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from agent import cli


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


if __name__ == "__main__":
    unittest.main()
