import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from agent.core.agent import Agent
from agent.core.registry import ToolRegistry


class DummyLLMToolCall:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "Retorna SEMPRE JSON válido" in system_prompt:
            return json.dumps(
                {
                    "isValid": True,
                    "data_using_util": {"a": 2, "b": 3},
                    "tool_using_exec": ["somar"],
                }
            )
        return "resposta final"


class DummyLLMNoTool:
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        if "Retorna SEMPRE JSON válido" in system_prompt:
            return json.dumps(
                {
                    "isValid": True,
                    "data_using_util": {},
                    "tool_using_exec": [],
                }
            )
        return "sem ferramenta"


class AgentCoreTests(unittest.TestCase):
    def test_provider_argument_overrides_env_and_model(self):
        with patch("agent.core.agent.get_llm_client") as mocked_factory:
            mocked_factory.return_value = DummyLLMNoTool()
            with patch.dict("os.environ", {"SMARTAGENT_PROVIDER": "openai"}, clear=False):
                Agent(model="groq", provider="gemini")
        mocked_factory.assert_called_once_with("gemini", None)

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
