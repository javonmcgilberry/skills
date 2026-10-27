#!/usr/bin/env python3
"""Yes-or-no checks on one eval run, so only taste is left for the judge.

usage: grade.py <case-id> <reply.md> [--report REPORT.md] [--seconds N]
Set KNOW_THYSELF_DATA_DIR to the frozen corpus the run used, so counts are checked against the same data.
Prints one JSON object: each check's pass or fail with its evidence, plus the "k of n" counts the script can't vouch for.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = {case["id"]: case for case in json.loads((HERE / "cases.json").read_text())["cases"]}
CONVO = HERE.parent / "scripts" / "convo.py"

PERSONA = re.compile(r"^\W*(i'?m|i am|as) (your |a |the )?(coach|mirror|analyst)\b|^\W*i (read|looked at|went through) ", re.I)
ADVICE_HEADING = re.compile(r"^#+\s*(what to try|try this|next steps|recommendations?)\b|^\*\*what to try", re.I | re.M)
LINK = re.compile(r"\]\(https?://|<https?://")
SOURCES_HEADING = re.compile(r"^#+\s*sources\b|^\*\*sources\*\*", re.I | re.M)
QUOTE = re.compile(r'["\u201c]([^"\u201d\n]{6,200})["\u201d],? \((\d{4}-\d{2}-\d{2})\)')
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


def shift(day, days):
    """A day either side, because a quote's date may be local while stored times are UTC."""
    return (datetime.date.fromisoformat(day) + datetime.timedelta(days=days)).isoformat()


def quote_found(quote, day):
    """Whether every fragment of a dated quote, split at ellipses, appears in what the user typed that day."""
    for part in re.split(r"\s*(?:\u2026|\.\.\.)\s*", quote):
        if len(part) < 4:
            continue
        # Pasted terminal output wraps through box borders, which are layout, not words.
        pattern = r"[\s\u2502\u2503|]+".join(re.escape(word) for word in part.split())
        out = subprocess.run([sys.executable, str(CONVO), "search", "--regex", f"(?i){pattern}", "--since", shift(day, -1),
                              "--until", shift(day, 1), "--limit", "1", "--max-words", "100000"], capture_output=True, text=True).stdout
        if not out.strip() or json.loads(out.splitlines()[0]).get("matches", 0) == 0:
            return False
    return True


def opening(text):
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            return line.strip()
    return ""


def offers(text):
    """Items of the reply's last list that open with a quoted request the user could paste, which is how a mirror offers follow-ups."""
    tail = text.strip().split("\n\n")
    items = []
    for block in reversed(tail):
        lines = [l for l in block.splitlines() if re.match(r"\s*([-*]|\d+\.)\s", l)]
        if lines:
            items = [l for l in lines if re.match(r'\s*([-*]|\d+\.)\s+(\*\*)?["\u201c].{8,}?["\u201d]', l)]
            break
    return items


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

    first = opening(reply)
    check("no_persona_opening", not PERSONA.search(first), first[:120])
    both = reply + "\n" + report
    dashes = sum(both.count(c) for c in "\u2013\u2014")
    check("no_long_dashes", dashes == 0, f"{dashes} found")

    if case["mode"] == "mirror":
        heads = [m.group(0).strip() for m in ADVICE_HEADING.finditer(both)]
        check("mirror_has_no_advice_section", not heads, ", ".join(heads))
        links = len(LINK.findall(both))
        check("mirror_has_no_links", links == 0, f"{links} links")
        items = offers(reply)
        check("mirror_ends_with_3_to_5_offers", 3 <= len(items) <= 5, f"{len(items)} items in the last list")
        offers_at = reply.find(items[0].strip()) if items else len(reply)
        shown_path = re.search(r"`(/[^`\n]+\.md)`", reply[:offers_at])
        check("mirror_reply_gives_report_path_before_offers", bool(shown_path),
              shown_path.group(1) if shown_path else "no absolute report path before the offers")
        deeper = [l for l in items if "deeper" in l.lower()]
        check("mirror_offers_a_deeper_read_and_says_what_it_is", deeper and len(deeper[0].split()) >= 6,
              deeper[0].strip()[:100] if deeper else "no deeper offer")
    if case["mode"] == "coach":
        for name, text in (("reply", reply), ("report", report)):
            if not text:
                continue
            heading = SOURCES_HEADING.search(text)
            body = text[:heading.start()] if heading else text
            inline = len(LINK.findall(body))
            listed = len(re.findall(r"^\s*([-*]|\d+\.)\s.*https?://", text[heading.start():], re.M)) if heading else 0
            check(f"coach_{name}_links_only_in_end_sources", inline == 0, f"{inline} links before Sources")
            check(f"coach_{name}_at_most_5_sources", listed <= 5, f"{listed} listed")
        check("coach_has_no_where_this_comes_from", "where this comes from" not in both.lower())
        shown = [label for label in ("before", "after", "what changed") if re.search(rf"\*\*{label}\b", reply, re.I)]
        check("coach_reply_shows_before_and_after", len(shown) == 3, ", ".join(shown) or "none")
    if case.get("report"):
        check("report_written", bool(report), "no report file" if not report else "")
    if case.get("max_seconds") and args.seconds is not None:
        check("fast_enough", args.seconds <= case["max_seconds"], f"{args.seconds:.0f}s of {case['max_seconds']}s")

    quotes = sorted({(q, day) for q, day in QUOTE.findall(both)})
    missing = [f'"{q}" ({day})' for q, day in quotes if not quote_found(q, day)]
    check("dated_quotes_exist", not missing, "; ".join(missing)[:400] or f"{len(quotes)} checked")

    pairs = known_pairs()
    found = [(int(k.replace(",", "")), int(n.replace(",", ""))) for k, n in PAIR.findall(both)]
    unverified = sorted({f"{k} of {n}" for k, n in found if (k, n) not in pairs})
    print(json.dumps({"case": args.case, "passed": all(c["pass"] for c in checks.values()), "checks": checks,
                      "counts_found": len(found), "counts_not_in_scorecard": unverified}, indent=2))


if __name__ == "__main__":
    main()
