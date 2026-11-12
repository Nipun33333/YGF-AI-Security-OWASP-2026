"""No-network model fallback and accounting tests."""
import csv
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import providers


class APIError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"mock error {status_code}")


class FallbackTest(unittest.TestCase):
    def setUp(self):
        providers._preferred_models.clear()

    def _google_mocks(self, status):
        calls = []

        class Config:
            def __init__(self, **kwargs):
                self.details = kwargs

        class Models:
            def generate_content(self, *, model, contents, config):
                calls.append(model)
                if model == "gemini-3.8-flash" or status == 404 and status == "all":
                    raise APIError(status)
                return types.SimpleNamespace(text="GEMINI OK")

        class Client:
            def __init__(self, *, api_key):
                self.models = Models()

        google = types.ModuleType("google")
        genai = types.ModuleType("google.genai")
        genai.Client = Client
        gtypes = types.ModuleType("google.genai.types")
        gtypes.GenerateContentConfig = Config
        genai.types = gtypes
        google.genai = genai
        return calls, {"google": google, "google.genai": genai, "google.genai.types": gtypes}

    def test_404_switches_to_next_free_tier_model(self):
        calls, modules = self._google_mocks(404)
        with patch.dict(sys.modules, modules):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake", "GEMINI_MODEL": "gemini-3.8-flash"}):
                result, actual = providers.generate("gemini", "sys", "prompt", return_model=True)
        self.assertEqual(result, "GEMINI OK")
        self.assertEqual(actual, "gemini-3.6-flash")
        self.assertEqual(calls, ["gemini-3.8-flash", "gemini-3.6-flash"])

    def test_429_tries_next_model(self):
        calls, modules = self._google_mocks(429)
        with patch.dict(sys.modules, modules):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake", "GEMINI_MODEL": "gemini-3.8-flash"}):
                self.assertEqual(providers.generate("gemini", "s", "p"), "GEMINI OK")
        self.assertEqual(len(calls), 2)

    def test_successful_model_is_preferred_for_next_probe(self):
        calls, modules = self._google_mocks(404)
        with patch.dict(sys.modules, modules):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake", "GEMINI_MODEL": "gemini-3.8-flash"}):
                providers.generate("gemini", "s", "p")
                providers.generate("gemini", "s", "p")
        self.assertEqual(calls, [
            "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.6-flash"
        ])

    def test_invalid_key_does_not_try_six_more_models(self):
        calls = []

        class Config:
            def __init__(self, **kwargs):
                pass

        class Models:
            def generate_content(self, *, model, contents, config):
                calls.append(model)
                raise APIError(401)

        class Client:
            def __init__(self, *, api_key):
                self.models = Models()

        google = types.ModuleType("google")
        genai = types.ModuleType("google.genai")
        genai.Client = Client
        gtypes = types.ModuleType("google.genai.types")
        gtypes.GenerateContentConfig = Config
        genai.types = gtypes
        google.genai = genai
        with patch.dict(sys.modules, {"google": google, "google.genai": genai, "google.genai.types": gtypes}):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake", "GEMINI_MODEL": "gemini-3.8-flash"}):
                with self.assertRaises(providers.ProviderError):
                    providers.generate("gemini", "s", "p")
        self.assertEqual(len(calls), 1)

    def test_claude_is_skipped_in_free_only_mode(self):
        with patch.dict(os.environ, {"ALLOW_PAID_CLAUDE": "false"}):
            with self.assertRaisesRegex(providers.ProviderUnavailable, "SKIPPED_NO_FREE_CLAUDE_API"):
                providers.generate("claude", "s", "p")

    def test_claude_credit_exhaustion_does_not_try_more_paid_models(self):
        calls = []
        class Messages:
            def create(self, **kwargs):
                calls.append(kwargs["model"])
                raise Exception("Your credit balance is too low to access the Anthropic API. purchase credits.")
        class Anthropic:
            def __init__(self, **kwargs):
                self.messages = Messages()
        module = types.ModuleType("anthropic")
        module.Anthropic = Anthropic
        with patch.dict(sys.modules, {"anthropic": module}):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake", "ALLOW_PAID_CLAUDE": "true", "CLAUDE_MODEL": "claude-haiku-5-5"}):
                with self.assertRaisesRegex(providers.ProviderUnavailable, "credits exhausted"):
                    providers.generate("claude", "s", "p")
        self.assertEqual(calls, ["claude-haiku-5-5"])

    def test_no_model_called_is_not_claimed_as_a_live_result(self):
        import run_tests
        with tempfile.TemporaryDirectory() as folder:
            target = str(Path(folder) / "live.csv")
            with patch("sys.argv", ["run_tests.py", "--mode", "live",
                                    "--provider", "claude", "--max-cases", "3",
                                    "--output", target]):
                with patch.dict(os.environ, {"ALLOW_PAID_CLAUDE": "false"}):
                    code = run_tests.main()
            self.assertEqual(code, 2)
            with open(target, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["result"] == "SKIPPED" for row in rows))
        self.assertTrue(all(not row["actual_model"] for row in rows))
        self.assertTrue(all(row["evidence_type"] == "NOT_TESTED" for row in rows))


if __name__ == "__main__":
    unittest.main()
