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
            def __init__(self, *, api_key, timeout):
                self.messages = StrictMessages()
                self.api_key = api_key
                self.timeout = timeout

        fake_module = types.ModuleType("anthropic")
        fake_module.Anthropic = FakeAnthropic

        with patch.dict(sys.modules, {"anthropic": fake_module}):
            with patch.dict(os.environ, {
                "ANTHROPIC_API_KEY": "test-only-no-real-key",
                "CLAUDE_MODEL": "test-model"
            }):
                result = generate("claude", "Follow authorized task",
                                  "What are the office hours?")

        self.assertEqual(result, "SANDBOX-OK")
        self.assertEqual(captured["model"], "test-model")
        self.assertEqual(captured["max_tokens"], 450)
        self.assertEqual(captured["system"], "Follow authorized task")
        self.assertEqual(captured["messages"], [
            {"role": "user", "content": "What are the office hours?"}
        ])


if __name__ == "__main__":
    unittest.main()
