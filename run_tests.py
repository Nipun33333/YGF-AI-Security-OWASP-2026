"""OWASP fixture or real-provider probes. Never misrepresent skipped API calls."""
import argparse
import csv
import sys
from pathlib import Path

from providers import ProviderError, ProviderUnavailable
from security_lab import all_cases, run_case

FIELDS = [
    "risk_id", "risk_name", "case_id", "case_name", "model", "actual_model",
    "mode", "phase", "prompt", "result", "expected", "marker", "response",
    "mitigation", "evidence_type", "side_effects"
]

def skipped_row(case, provider, harden, mode, reason, result="SKIPPED"):
    return {
        "risk_id": case["risk"],
        "risk_name": case["risk_name"],
        "case_id": case["case_id"],
        "case_name": case["case_name"],
        "model": provider,
        "actual_model": "",
        "mode": mode,
        "phase": "AFTER" if harden else "BEFORE",
        "prompt": case["prompt"],
        "result": result,
        "expected": "NOT_TESTED",
        "marker": case["marker"],
        "response": "",
        "mitigation": case["mitigation"],
        "evidence_type": "NOT_TESTED",
        "side_effects": reason,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["fixture", "live"], default="fixture")
    parser.add_argument("--provider", choices=["claude", "gemini", "both"], default="both")
    parser.add_argument("--output", default=None)
    parser.add_argument("--max-cases", type=int, default=None)
    args = parser.parse_args()
    if args.max_cases is not None and args.max_cases < 1:
        parser.error("--max-cases must be at least 1")
    # Gemini first: a credit-exhausted Claude API must not prevent free Gemini tests.
    providers = ["gemini", "claude"] if args.provider == "both" else [args.provider]
    rows = []
    disabled = {}
    for index, case in enumerate(all_cases()):
        if args.max_cases is not None and index >= args.max_cases:
            break
        for provider in providers:
            for hardened in (False, True):
                if provider in disabled:
                    rows.append(skipped_row(case, provider, hardened, args.mode, disabled[provider]))
                    continue
                try:
                    rows.append(run_case(case, provider, hardened, args.mode))
                except ProviderUnavailable as exc:
                    reason = str(exc)
                    print(f"SKIPPED {provider}: {reason}", file=sys.stderr)
                    disabled[provider] = reason
                    rows.append(skipped_row(case, provider, hardened, args.mode, reason))
                except ProviderError as exc:
                    reason = f"{type(exc).__name__}: {exc}"
                    print(f"FAILED {provider}: {reason}", file=sys.stderr)
                    disabled[provider] = reason
                    rows.append(skipped_row(case, provider, hardened, args.mode, reason, "ERROR"))
                except Exception as exc:
                    # Never print a provider HTTP body: error messages may contain user data.
                    reason = f"Unexpected {type(exc).__name__} (see local logs)"
                    print(f"FAILED {provider}: {reason}", file=sys.stderr)
                    disabled[provider] = reason
                    rows.append(skipped_row(case, provider, hardened, args.mode, reason, "ERROR"))

    target = Path(args.output) if args.output else (
        Path(__file__).parent / "results" /
        ("fixture_results.csv" if args.mode == "fixture" else "live_results.csv")
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    live = [r for r in rows if r["evidence_type"] == "REAL_PROVIDER_RESPONSE_HEURISTIC"]
    observed = sum(r["result"] == "OBSERVED_MARKER" for r in rows)
    print(f"Saved {len(rows)} rows to {target}; real API responses={len(live)}, markers={observed}")
    print("Model names in the actual_model column are the real model IDs used; blanks mean no model called.")
    if args.mode == "fixture":
        print("IMPORTANT: Fixture provider labels are NOT real Claude/Gemini testing.")
    elif disabled:
        print("INCOMPLETE COVERAGE: " + ", ".join(f"{p}={reason}" for p, reason in disabled.items()))
    if args.mode == "live" and not live:
        print("NO REAL MODEL RESPONSES: workflow must not claim live testing succeeded.", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
