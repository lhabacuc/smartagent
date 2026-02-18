import unittest
from unittest.mock import patch

from agent.core.config import AgentConfig
from agent.integrations import normalize_provider, get_llm_client
from agent.core.exceptions import LLMError


class ConfigAndFactoryTests(unittest.TestCase):
    def test_agent_config_uses_model_as_legacy_provider(self):
        with self.assertWarns(DeprecationWarning):
            cfg = AgentConfig.from_inputs(model="openai")
        self.assertEqual(cfg.provider, "openai")
        self.assertIsNone(cfg.model)

    def test_agent_config_reads_timeout_and_retries_from_env(self):
        with patch.dict(
            "os.environ",
            {"SMARTAGENT_TIMEOUT": "12.5", "SMARTAGENT_RETRIES": "4"},
            clear=False,
        ):
            cfg = AgentConfig.from_inputs(provider="groq")
        self.assertEqual(cfg.timeout, 12.5)
        self.assertEqual(cfg.retries, 4)

    def test_normalize_provider_alias(self):
        self.assertEqual(normalize_provider("google-gemini"), "gemini")
        self.assertEqual(normalize_provider("xai"), "grok")

    def test_get_llm_client_raises_for_unknown_provider(self):
        with self.assertRaises(LLMError):
            get_llm_client("unknown-provider")


if __name__ == "__main__":
    unittest.main()
