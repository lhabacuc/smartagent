import sys
import types
import unittest
from unittest.mock import Mock, patch

from agent.core.exceptions import LLMError
from agent.integrations.llm_gemini import GeminiLLM
from agent.integrations.llm_grok import GrokLLM
from agent.integrations.llm_groq import GroqLLM
from agent.integrations.llm_llama import LlamaLLM
from agent.integrations.llm_ollama import OllamaLLM
from agent.integrations.llm_openai import OpenAILLM


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self._payload = payload
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self._payload


class IntegrationsHTTPTests(unittest.TestCase):
    def _patch_requests(self, post_callable):
        fake_requests = types.SimpleNamespace(post=post_callable)
        return patch.dict(sys.modules, {"requests": fake_requests})

    def test_openai_parse_and_timeout(self):
        post = Mock(
            return_value=FakeResponse(
                {"choices": [{"message": {"content": "ok-openai"}}]}
            )
        )
        with self._patch_requests(post):
            client = OpenAILLM(api_key="k", model="m", timeout=12, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-openai")
        self.assertEqual(post.call_args.kwargs["timeout"], 12.0)

    def test_groq_parse(self):
        post = Mock(
            return_value=FakeResponse(
                {"choices": [{"message": {"content": "ok-groq"}}]}
            )
        )
        with self._patch_requests(post):
            client = GroqLLM(api_key="k", model="m", timeout=10, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-groq")

    def test_gemini_parse(self):
        post = Mock(
            return_value=FakeResponse(
                {"candidates": [{"content": {"parts": [{"text": "ok-gemini"}]}}]}
            )
        )
        with self._patch_requests(post):
            client = GeminiLLM(api_key="k", model="m", timeout=10, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-gemini")

    def test_grok_parse(self):
        post = Mock(
            return_value=FakeResponse(
                {"choices": [{"message": {"content": "ok-grok"}}]}
            )
        )
        with self._patch_requests(post):
            client = GrokLLM(api_key="k", model="m", timeout=10, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-grok")

    def test_llama_parse(self):
        post = Mock(
            return_value=FakeResponse(
                {"choices": [{"message": {"content": "ok-llama"}}]}
            )
        )
        with self._patch_requests(post):
            client = LlamaLLM(api_key="k", model="m", timeout=10, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-llama")

    def test_ollama_parse(self):
        post = Mock(return_value=FakeResponse({"message": {"content": "ok-ollama"}}))
        with self._patch_requests(post):
            client = OllamaLLM(model="m", timeout=10, retries=0)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-ollama")

    def test_retry_then_success(self):
        post = Mock(
            side_effect=[
                Exception("temporary failure"),
                FakeResponse({"choices": [{"message": {"content": "ok-retry"}}]}),
            ]
        )
        with self._patch_requests(post), patch("agent.integrations.llm_base.time.sleep", return_value=None):
            client = OpenAILLM(api_key="k", model="m", timeout=10, retries=1)
            content = client.chat("sys", "user")
        self.assertEqual(content, "ok-retry")
        self.assertEqual(post.call_count, 2)

    def test_error_after_retries(self):
        post = Mock(side_effect=Exception("network down"))
        with self._patch_requests(post), patch("agent.integrations.llm_base.time.sleep", return_value=None):
            client = OpenAILLM(api_key="k", model="m", timeout=10, retries=1)
            with self.assertRaises(LLMError) as err:
                client.chat("sys", "user")
        self.assertIn("Falha HTTP", str(err.exception))
        self.assertEqual(post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
