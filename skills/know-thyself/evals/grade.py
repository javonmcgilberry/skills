#!/usr/bin/env python3
"""Yes-or-no checks on one eval run, so only taste is left for the judge.

The checks a run must pass before replying live in scripts/lint.py, which the skill runs itself; this adds the ones only an eval
can make: that a report was written, how long the run took, and which "k of n" counts the scorecard doesn't hold.

usage: grade.py <case-id> <reply.md> [--report REPORT.md] [--seconds N]
Set KNOW_THYSELF_DATA_DIR to the frozen corpus the run used, so counts are checked against the same data.
Prints one JSON object: each check's pass or fail with its evidence, plus the "k of n" counts the script can't vouch for.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {case["id"]: case for case in json.loads((HERE / "cases.json").read_text())["cases"]}
CONVO = HERE.parent / "scripts" / "convo.py"
sys.path.insert(0, str(CONVO.parent))
import convo  # noqa: E402
import lint  # noqa: E402

PAIR = re.compile(r"\b(\d[\d,]*) of (?:your |the |those |these )?(?:last )?(\d[\d,]*)\b")


def known_pairs():
    """Every (k, n) the scorecard JSON holds, at any depth."""
    out = subprocess.run([sys.executable, str(CONVO), "score"], capture_output=True, text=True).stdout
    pairs = set()

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("k"), int) and isinstance(node.get("n"), int):
                pairs.add((node["k"], node["n"]))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(json.loads(out) if out.strip() else {})
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case")
    parser.add_argument("reply")
    parser.add_argument("--report")
    parser.add_argument("--seconds", type=float)
    args = parser.parse_args()
    case = CASES[args.case]
    reply = Path(args.reply).read_text()
    report = Path(args.report).read_text() if args.report else ""
    checks = {}

    def check(name, ok, evidence=""):
        checks[name] = {"pass": bool(ok), "evidence": evidence}

    keep_out = lint.keep_out_terms(convo.PROFILE.read_text()) if convo.PROFILE.exists() else []
    checks.update(lint.checks(case["mode"], reply, report, keep_out))
    if case.get("report"):
        check("report_written", bool(report), "no report file" if not report else "")
    if case.get("max_seconds") and args.seconds is not None:
        check("fast_enough", args.seconds <= case["max_seconds"], f"{args.seconds:.0f}s of {case['max_seconds']}s")

    both = reply + "\n" + report
    pairs = known_pairs()
    found = [(int(k.replace(",", "")), int(n.replace(",", ""))) for k, n in PAIR.findall(both)]
    unverified = sorted({f"{k} of {n}" for k, n in found if (k, n) not in pairs})
    print(json.dumps({"case": args.case, "passed": all(c["pass"] for c in checks.values()), "checks": checks,
                      "counts_found": len(found), "counts_not_in_scorecard": unverified}, indent=2))


if __name__ == "__main__":
    main()
