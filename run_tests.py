"""Runs all risk cases. Fixture results are NOT actual Claude/Gemini evaluations."""
import argparse,csv,json,sys
from datetime import datetime, timezone
from pathlib import Path
from security_lab import all_cases, run_case

FIELDS=["risk_id","risk_name","case_id","case_name","model","mode","phase","prompt","result","expected","marker","response","mitigation","evidence_type","side_effects"]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode", choices=["fixture","live"], default="fixture")
    p.add_argument("--provider",choices=["claude","gemini","both"],default="both")
    p.add_argument("--output", default=None)
    args=p.parse_args()
    models=["claude","gemini"] if args.provider=="both" else [args.provider]
    rows=[]
    for c in all_cases():
        for model in models:
            for hardened in (False,True):
                try: rows.append(run_case(c,model,hardened,args.mode))
                except Exception as e:
                    print(f"FAILED {c['case_id']} {model}: {type(e).__name__}: {e}",file=sys.stderr)
                    if args.mode=="live": sys.exit(2)
                    raise
    target=Path(args.output) if args.output else Path(__file__).parent/"results"/("fixture_results.csv" if args.mode=="fixture" else "live_results.csv")
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    violations=sum(r["result"]=="OBSERVED_MARKER" for r in rows)
    print(f"{len(rows)} rows written: {target}; markers observed: {violations}; mode={args.mode}")
    if args.mode=="fixture": print("IMPORTANT: Fixture provider names are LABELS ONLY; zero Claude/Gemini calls were made.")
if __name__=="__main__": main()
