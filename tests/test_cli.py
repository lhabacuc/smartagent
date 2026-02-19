import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
