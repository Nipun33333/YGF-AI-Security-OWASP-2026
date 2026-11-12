# YGF AI Security POC — OWASP LLM & Agentic 2026

**Applicant:** Nipun Agarwal  
**Assignment:** Youth Growth Foundation — AI Security Internship, Round 2  
**Scope:** isolated toy data, harmless markers, no real shell/email/HTTP, localhost-only UI.

## Important integrity disclosure

The included `fixture_results.csv` demonstrates **deterministic, offline control-plane simulations only**. Although its rows contain `claude`/`gemini` model-target labels, **neither provider was contacted**. The fixture results are **not** empirical Claude-vs-Gemini performance claims. Real model comparisons must be generated separately with `--mode live` and legitimately obtained API credentials. Live mode is a **text-only prompt probe**: it does not execute proposed external actions. `OBSERVED_MARKER` denotes the appearance of an exact toy string, **not proof of exploitability**.

## Coverage (2026 taxonomy, not 2023/2025)

| Risk | 2026 label | Scenario count | Primary mitigation |
|---|---|---:|---|
| LLM01 | Prompt Injection | 3 | Separate untrusted data from instructions |
| LLM02 | Sensitive Information Disclosure | 3 | Redact confidential context and enforce data access |
| LLM03 | Excessive Agency | 3 | Gate side-effecting tools with authorization |
| LLM08 | Hidden Context Exposure | 3 | Limit/partition system context |
| LLM10 | Improper Output Handling | 3 | Escape HTML, validate output formats |
| ASI01 | Agent Goal Hijack | 3 | Signed trusted goals |
| ASI02 | Tool Misuse and Exploitation | 3 | Target allowlists and tool schemas |
| ASI03 | Identity and Privilege Abuse | 3 | Caller identity enforced server-side |
| ASI05 | Unexpected Code Execution | 3 | No shell/eval; allowed operations only |
| ASI06 | Memory and Context Poisoning | 3 | Provenance and approval for memory writes |
| MCP-POC | Untrusted MCP server connection | 3 | Manifest validation, scoped capabilities, server identity |

**33 scenarios × 2 labeled providers × 2 phases = 132 fixture rows**. Core required risks alone: 30 scenarios, 120 rows. In fixture mode, pre-mitigation toy vulnerabilities are deliberately present and then blocked by the corresponding guard. This establishes a repeatable baseline, **not real-world AI model success rates**.

## Quick start: offline, no keys

```bash
python app.py
# open http://127.0.0.1:8765
python run_tests.py --mode fixture --provider both
python -m unittest discover -s tests -v
```

## Real Claude + Gemini text-probe comparison (requires both API keys)

```bash
python -m pip install -r requirements.txt
# Set ANTHROPIC_API_KEY and GEMINI_API_KEY as environment variables locally.
# Optionally override CLAUDE_MODEL and GEMINI_MODEL with models available on your accounts.
python run_tests.py --mode live --provider both --output results/live_results.csv
```

Output columns include `risk_id`, `model`, `prompt`, `phase`, `result`, `response`, `evidence_type`. Do not include secrets, real personal data, or live provider responses containing sensitive information in public commits. Compare text-level marker appearance, not safety ratings, without human review. A model refusal may lead to `NO_MARKER` even for the intentionally vulnerable fixture; this is meaningful, not an error.

## Architecture

- `app.py` — local browser-based POC; provider/attack/mode/defense switches
- `security_lab.py` — fake KB, 4 sandbox tools (file, mail, HTTP, MCP), deterministic attack fixtures, enforcement
- `providers.py` — official Anthropic and Google GenAI client adapters; lazy imports, explicit API-only mode
- `data/cases.json` — 33 prompts, 11 risk families including MCP
- `run_tests.py` — CSV result generator, before/after loops
- `tests/` — repeatable unit tests; includes proof of no real external action
- `results/fixture_results.csv` — 132 clearly-labeled simulation outcomes
- `docs/` — report, results XLSX and narrated demo (available as downloadable submission bundle)

## MCP connection POC

A mock rogue server manifest offers untrusted capabilities (`send_email`), altered scopes (`read-write`) and a false identity (`rogue-mcp`). In vulnerable mode, it is accepted into an **in-memory list only**. In hardened mode it is rejected unless server identity equals `trusted-local-v1`, advertised tools are a subset of `public_kb_search`, and scope is `read-only`. No actual remote server or MCP network traffic exists. This is a **connection trust-boundary simulation**, not protocol-compliance testing.

## Threat model and limitations

The adversary controls chat messages, fake KB documents, and mock MCP metadata, but not the local test harness. External APIs and actual email/HTTP effects are absent. The intentionally vulnerable code is designed for education; do not deploy publicly. Real tests need provider accounts and local safe environments. For models' true tool-use security, replace the text-only probe with validated function-calling adapters and review the resulting tool logs. No real API keys are included.

## Original sources

- OWASP GenAI LLM Top 10 (2026): https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
- OWASP Agentic Top 10 (2026): https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- Anthropic Python SDK: https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python
- Google GenAI SDK: https://ai.google.dev/gemini-api/docs/get-started

## Usage and research ethics

Demo markers are fictitious: `SECRET-FLAG-123`, `HIDDEN-CONTEXT-42` etc. `example.invalid` is non-routable. No shell commands are executed even in vulnerable fixture mode. Use a Docker/VM sandbox, restrict real provider keys, and only test your own application.