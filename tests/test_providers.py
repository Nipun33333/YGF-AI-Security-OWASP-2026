"""Regression test: Claude SDK Messages.create no longer accepts temperature.
Uses a strict fake client; no API key, network call, or paid tokens.
"""
import os
import sys
import types
import unittest
from unittest.mock import patch

from providers import generate


class ProviderSDKCompatibilityTest(unittest.TestCase):
    def setUp(self):
        # Avoid sticky fallback selections leaking from other unit tests.
        from providers import _preferred_models
        _preferred_models.clear()

    def test_anthropic_messages_create_uses_supported_keywords(self):
        captured = {}

        class StrictMessages:
            # Deliberately omit 'temperature'; the latest SDK rejects it.
            def create(self, *, model, max_tokens, system, messages):
                captured.update(model=model, max_tokens=max_tokens,
                                system=system, messages=messages)
                return types.SimpleNamespace(
                    content=[types.SimpleNamespace(text="SANDBOX-OK")]
                )

        class FakeAnthropic:
            def __init__(self, *, api_key, timeout, max_retries):
                self.messages = StrictMessages()
                self.api_key = api_key
                self.timeout = timeout
                self.max_retries = max_retries

        fake_module = types.ModuleType("anthropic")
        fake_module.Anthropic = FakeAnthropic

        with patch.dict(sys.modules, {"anthropic": fake_module}):
            with patch.dict(os.environ, {
                "ANTHROPIC_API_KEY": "test-only-no-real-key",
                "CLAUDE_MODEL": "claude-haiku-5-5",
                "ALLOW_PAID_CLAUDE": "true"
            }):
                result = generate("claude", "Follow authorized task",
                                  "What are the office hours?")

        self.assertEqual(result, "SANDBOX-OK")
        self.assertEqual(captured["model"], "claude-haiku-5-5")
        self.assertEqual(captured["max_tokens"], 450)
        self.assertEqual(captured["system"], "Follow authorized task")
        self.assertEqual(captured["messages"], [
            {"role": "user", "content": "What are the office hours?"}
        ])


    def test_gemini_supported_model_no_network(self):
        captured = {}

        class FakeConfig:
            def __init__(self, **kwargs):
                captured["config"] = kwargs

        class FakeModels:
            def generate_content(self, *, model, contents, config):
                captured.update(model=model, contents=contents)
                return types.SimpleNamespace(text="GEMINI-MOCK-OK")

        class FakeClient:
            def __init__(self, *, api_key):
                self.models = FakeModels()

        google_module = types.ModuleType("google")
        genai_module = types.ModuleType("google.genai")
        types_module = types.ModuleType("google.genai.types")
        genai_module.Client = FakeClient
        types_module.GenerateContentConfig = FakeConfig
        genai_module.types = types_module
        google_module.genai = genai_module

        with patch.dict(sys.modules, {
            "google": google_module,
            "google.genai": genai_module,
            "google.genai.types": types_module
        }):
            with patch.dict(os.environ, {
                "GEMINI_API_KEY": "test-only-no-real-key",
                "GEMINI_MODEL": "gemini-3.8-flash"
            }):
                result = generate("gemini", "Authorized system instruction", "Fake FAQ")

        self.assertEqual(result, "GEMINI-MOCK-OK")
        self.assertEqual(captured["model"], "gemini-3.8-flash")
        self.assertEqual(captured["contents"], "Fake FAQ")
        self.assertEqual(captured["config"]["system_instruction"], "Authorized system instruction")
        self.assertGreaterEqual(captured["config"]["max_output_tokens"], 450)


if __name__ == "__main__":
    unittest.main()
