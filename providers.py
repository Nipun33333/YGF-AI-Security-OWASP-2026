"""Provider adapters with bounded, auditable model fallback.

Gemini candidates are a deliberately reviewed FREE-TIER-ELIGIBLE text allowlist.
An enabled Google Cloud billing account can still incur charges: keep the AI
Studio project on Free Tier to guarantee zero-priced model usage.
Claude API has NO ongoing free tier. Paid Claude calls require opt-in.
"""
import os
import sys

class ProviderError(RuntimeError):
    """A non-retryable provider/configuration error."""

class ProviderUnavailable(ProviderError):
    """No allowed provider/model is available; never fabricate a response."""

GEMINI_FREE_MODELS = (
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
)

# All Claude API models require credits. No entry is advertised as free.
CLAUDE_PAID_MODELS = (
    "claude-haiku-5-5",
    "claude-sonnet-5-5",
    "claude-sonnet-5",
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-8",
    "claude-opus-4-7",
)

# Prefer a previously successful fallback within the same Python test process.
_preferred_models = {}

def _allowed_models(provider):
    if provider == "gemini":
        allowed = GEMINI_FREE_MODELS
        preferred = os.getenv("GEMINI_MODEL", allowed[0]).strip()
    elif provider == "claude":
        allowed = CLAUDE_PAID_MODELS
        preferred = os.getenv("CLAUDE_MODEL", allowed[0]).strip()
    else:
        raise ProviderError("Provider must be claude or gemini")
    if preferred not in allowed:
        raise ProviderError(f"Model {preferred!r} is not in the reviewed {provider} allowlist")
    ordered = [preferred] + [m for m in allowed if m != preferred]
    working = _preferred_models.get(provider)
    if working in ordered:
        ordered.remove(working)
        ordered.insert(0, working)
    return ordered[:7]

def _error_category(exc, provider):
    code = getattr(exc, "status_code", None)
    if code is None:
        code = getattr(exc, "code", None)
    try:
        code = int(code)
    except (TypeError, ValueError):
        code = None
    msg = str(exc).lower()
    if provider == "claude" and any(
        needle in msg for needle in ("credit balance is too low", "insufficient credits", "purchase credits", "billing balance")
    ):
        return "NO_CREDITS"
    if code in (401, 403):
        return "AUTH"
    if code == 429 or "quota exceeded" in msg or "rate limit" in msg:
        return "QUOTA"
    if code == 404 or (
        code == 400 and "model" in msg and
        any(word in msg for word in ("not available", "not found", "unsupported", "no longer available"))
    ):
        return "MODEL_UNAVAILABLE"
    if code in (408, 500, 502, 503, 504) or isinstance(exc, (TimeoutError, ConnectionError)):
        return "TEMPORARY"
    return "INVALID_REQUEST"

def _call(provider, client, model, system, user, config):
    if provider == "claude":
        message = client.messages.create(
            model=model, max_tokens=450, system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "\n".join(getattr(part, "text", "") for part in message.content)
    result = client.models.generate_content(
        model=model, contents=user, config=config,
    )
    return result.text or ""

def generate(provider: str, system: str, user: str, *, return_model=False):
    """Return text (legacy behavior) or (text, actual_model) for audit records.

    Fallback on retired/404, rate-limited, timeout and server-unavailable models.
    Do not retry unauthorized keys, invalid requests, Claude billing exhaustion,
    or safety refusals (a valid refusal is a completed model response).
    """
    if provider not in ("claude", "gemini"):
        raise ProviderError("Provider must be claude or gemini")
    if provider == "claude" and os.getenv("ALLOW_PAID_CLAUDE", "").lower() not in ("1", "true", "yes"):
        raise ProviderUnavailable(
            "SKIPPED_NO_FREE_CLAUDE_API: Claude API requires credits. "
            "Set ALLOW_PAID_CLAUDE=true only after explicitly approving paid usage."
        )
    name = "ANTHROPIC_API_KEY" if provider == "claude" else "GEMINI_API_KEY"
    if not os.getenv(name):
        raise ProviderUnavailable(f"Missing secret {name}; no provider call made")
    models = _allowed_models(provider)
    if provider == "claude":
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ProviderError("Install dependencies from requirements.txt") from exc
        client = Anthropic(api_key=os.environ[name], timeout=45, max_retries=0)
        config = None
    else:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError("Install dependencies from requirements.txt") from exc
        client = genai.Client(api_key=os.environ[name])
        config = types.GenerateContentConfig(
            system_instruction=system, max_output_tokens=1200
        )
    tried = []
    for model in models:
        try:
            text = _call(provider, client, model, system, user, config)
            _preferred_models[provider] = model
            if tried:
                print(f"[{provider}] succeeded with fallback model {model}", file=sys.stderr)
            return (text, model) if return_model else text
        except Exception as exc:
            reason = _error_category(exc, provider)
            if reason == "NO_CREDITS":
                raise ProviderUnavailable(
                    "Claude API credits exhausted; a different Claude model cannot bypass billing."
                ) from None
            if reason in ("AUTH", "INVALID_REQUEST"):
                raise ProviderError(
                    f"{provider} request stopped on {model}: {reason}. Check key/model/configuration."
                ) from None
            tried.append(f"{model}:{reason}")
            print(f"[{provider}] {model} unavailable ({reason}); trying next allowed model", file=sys.stderr)
    raise ProviderUnavailable(
        f"All {len(models)} permitted {provider} models unavailable: " + ", ".join(tried)
    )
