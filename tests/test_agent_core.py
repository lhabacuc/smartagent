import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agent.core.agent import Agent
from agent.core.exceptions import AnalysisError
from agent.core.registry import ToolRegistry


class DummyLLMToolCall:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "tool_calls" in system_prompt:
            return json.dumps(
                {
                    "isValid": True,
                    "tool_calls": [{"name": "somar", "args": {"a": 2, "b": 3}}],
                }
            )
        return "resposta final"


class DummyLLMNoTool:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "tool_calls" in system_prompt:
            return json.dumps(
                {
                    "isValid": True,
                    "tool_calls": [],
                }
            )
        return "sem ferramenta"


class DummyLLMInvalidArgs:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "tool_calls" in system_prompt:
            return json.dumps(
                {
                    "isValid": True,
                    "tool_calls": [{"name": "somar", "args": {"x": 2}}],
                }
            )
        return "sem ferramenta"


class DummyLLMNonJsonAnalysis:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "tool_calls" in system_prompt:
            return "```json {\"isValid\": true} ```"
        return "ok"


class DummyLLMPlainText:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        return "resposta direta"


class AgentCoreTests(unittest.TestCase):
    def test_provider_argument_overrides_env_and_model(self):
        with patch("agent.core.agent.get_llm_client") as mocked_factory:
            mocked_factory.return_value = DummyLLMNoTool()
            with patch.dict("os.environ", {"SMARTAGENT_PROVIDER": "openai"}, clear=False):
                Agent(model="gemini-2.0-flash", provider="gemini")
        mocked_factory.assert_called_once_with(
            provider="gemini",
            api_key=None,
            model="gemini-2.0-flash",
            timeout=30.0,
            retries=2,
        )

    def test_process_executes_registered_tool(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMToolCall()):
            agent = Agent(model="groq")

            @agent.tool
            def somar(a=0, b=0):
                return a + b

            result = agent.process("soma para mim")

        self.assertEqual(result["executed_tools"], ["somar"])
        self.assertEqual(result["used_data"], {"a": 2, "b": 3})
        self.assertEqual(result["execution_data"]["results"]["somar"], 5)
        self.assertEqual(result["final_response"], "resposta final")

    def test_process_reports_invalid_tool_args(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMInvalidArgs()):
            agent = Agent(model="groq")

            @agent.tool
            def somar(a, b):
                return a + b

            result = agent.process("soma para mim")

        self.assertFalse(result["execution_data"]["success"])
        self.assertEqual(result["executed_tools"], [])
        self.assertEqual(len(result["execution_data"]["call_results"]), 1)
        self.assertFalse(result["execution_data"]["call_results"][0]["ok"])
        self.assertIn("missing a required argument", result["execution_data"]["call_results"][0]["error"])

    def test_analyzer_requires_strict_json(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMNonJsonAnalysis()):
            agent = Agent(model="groq")

            @agent.tool
            def ping():
                return "pong"

            with self.assertRaises(AnalysisError):
                agent.process("qualquer coisa")

    def test_process_without_tools_skips_analyzer_json_contract(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMPlainText()):
            agent = Agent(model="groq")
            result = agent.process("olá")

        self.assertEqual(result["final_response"], "resposta direta")
        self.assertEqual(result["executed_tools"], [])
        self.assertTrue(result["execution_data"]["success"])
        self.assertEqual(result["analysis"]["tool_calls"], [])

    def test_chat_history_does_not_duplicate_entries(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMNoTool()):
            agent = Agent(model="groq", enable_history=True, history_limit=3)
            agent.chat("oi")
            agent.chat("tudo bem?")
            history = agent.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["user_prompt"], "oi")
        self.assertEqual(history[1]["user_prompt"], "tudo bem?")

    def test_help_list_tools_and_reset(self):
        with patch("agent.core.agent.get_llm_client", return_value=DummyLLMNoTool()):
            agent = Agent(model="groq", enable_history=True, history_limit=3)

            @agent.tool
            def ping():
                return "pong"

            out = io.StringIO()
            with redirect_stdout(out):
                with self.assertWarns(DeprecationWarning):
                    agent.help()
                agent.list_tools()

            before_reset = agent.registry.get_tools_list()
            agent.reset()
            after_reset = agent.registry.get_tools_list()

        self.assertIn("ping", before_reset)
        self.assertEqual(after_reset, [])
        self.assertTrue(agent.responder.enable_history)

    def test_registry_list_tools_returns_mapping(self):
        registry = ToolRegistry()

        def sample_tool():
            return "ok"

        registry.register(sample_tool)
        tools = registry.list_tools()
        self.assertIn("sample_tool", tools)
        self.assertTrue(callable(tools["sample_tool"]))


if __name__ == "__main__":
    unittest.main()
