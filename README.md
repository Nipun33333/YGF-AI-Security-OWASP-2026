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
## Running API probes securely with GitHub Actions (no keys in chat or Git)

1. In this repository, open **Settings → Secrets and variables → Actions → New repository secret**.
2. Create a secret named `GEMINI_API_KEY` and paste the Gemini key directly into the GitHub secret value field.
3. Create a second secret named `ANTHROPIC_API_KEY` and paste the Anthropic key. **Claude API may require paid credits even when the key exists.**
4. Open **Actions → YGF Live API Security Tests → Run workflow**. Choose `both` to compare providers, or a single provider to test just that one.
5. Start with **3 cases** for a small smoke test; choosing **33 cases** exercises all 11 risk families. Each case calls each selected provider twice (before and after), so 33 cases with both providers means **132 model API calls**, and may incur charges or exhaust free quotas.
6. After a successful workflow, download the `ygf-live-probe-...` artifact from that run. It contains a CSV of real provider *text-response probes*, not actual tool execution. Review it before putting any claims in the assignment.

This workflow is **manual only** (not scheduled or triggered by code pushes), deliberately does not echo API key values, and never commits live results. If there are no Claude API credits, test Gemini alone first and disclose the Claude limitation rather than fabricating a comparison. Do not paste API keys into ChatGPT, GitHub Issues, README, screenshots or other public files. Rotate any key that has been exposed.


## Seven-model fallback with FREE-TIER-FIRST behavior (November 2026)

Gemini tries these *independently named models in order* (up to 7 per probe), moves on only for **404/model unavailable, 429/quota, timeout or 5xx**, and remembers the first working model for the next probe:

1. `gemini-3.8-flash`
2. `gemini-3.6-flash`
3. `gemini-3.5-flash`
4. `gemini-3.5-flash-lite`
5. `gemini-3.1-flash-lite`
6. `gemini-3-flash-preview`
7. `gemini-2.5-flash-lite` (may no longer be available to newly created keys; skipped on 404)

The list contains only models whose Standard text API has a documented **Free Tier** on Google's pricing page, but **free-tier eligibility does NOT by itself prevent charges on a billing-enabled Google project**. To keep calls free, keep your Google AI Studio API project on the Free usage tier and stay within quotas. Models may be retired, so successful requests record the exact `actual_model` in `results/live_results.csv`. If no candidate is available, the row is explicitly marked **SKIPPED/NOT_TESTED**, never a fictitious success.

**Claude is different: no persistent free Claude API tier exists.** Changing Claude model IDs does not fix the `credit balance is too low` error. The available paid-model fallback list in `providers.py` contains seven Claude model IDs, but the workflow defaults to `allow_paid_claude=false`. If you deliberately obtain API credits, select **allow_paid_claude=true** in the workflow; paid Claude model fallback then applies, and token charges may occur. Without opt-in, a `both` run can collect Gemini results while the Claude rows correctly say **SKIPPED**.

Our fallback will NOT rotate models to bypass an invalid API key, a real safety refusal, or Claude's exhausted billing balance. It does not hide failed requests: the workflow logs which models failed, why (error category only), and the actual serving model, without displaying keys. Skipped models are not counted as live-tested Claude or Gemini performance.

**Workflow:** Actions → YGF Live API Security Tests → Run workflow → Provider `gemini` (or `both` with Claude skipped), Max cases `3`, leave **allow_paid_claude unchecked**. Run with `33` only when enough free quota remains. Every case runs both BEFORE and AFTER; fallbacks may increase request count up to 7x in the worst case. Results are stored as an Actions artifact (not committed to the public repository).

Official pricing: https://ai.google.dev/gemini-api/docs/pricing and https://platform.claude.com/docs/en/about-claude/pricing
