"""Optional real providers; only used when explicitly requesting --mode live."""
import os

class ProviderError(RuntimeError):
    pass

def generate(provider: str, system: str, user: str) -> str:
    if provider == "claude":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ProviderError("ANTHROPIC_API_KEY is missing")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ProviderError("Run pip install -r requirements.txt") from exc
        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=45)
        msg = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
            max_tokens=450,
            system=system, messages=[{"role": "user", "content": user}]
        )
        return "\n".join(getattr(b, "text", "") for b in msg.content)
    if provider == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            raise ProviderError("GEMINI_API_KEY is missing")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError("Run pip install -r requirements.txt") from exc
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        rsp = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            contents=user,
            config=types.GenerateContentConfig(system_instruction=system, max_output_tokens=1200)
        )
        return rsp.text or ""
    raise ProviderError("provider must be claude or gemini")
