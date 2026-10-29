#!/usr/bin/env python3
"""Mechanical checks on a reply and its report, run before the reply reaches the user.

usage: lint.py --mode MODE [REPORT.md] [--reply REPLY.md]
Prints one JSON object with every check's pass or fail and its evidence, and exits 1 when any check fails.
Each check is something a program can settle, so the agent fixes what it finds instead of judging its own work by eye.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

CONVO = Path(__file__).resolve().parent / "convo.py"
MODES = ("mirror", "coach", "share", "lead", "trend", "recall", "lessons", "init", "menu")
SECTIONS = {
    "mirror": ("The short version", "How you work", "What you're good at", "Where friction shows up", "What's changed",
               "What this covers", "Where you could go from here"),
    "coach": ("The short version", "What this covers", "What's working", "What gets in the way", "The habits that matter here",
              "Before and after", "What to try next", "Sources"),
    "share": ("How I work", "What I'm good at", "My tools and workflow", "What's changed", "About this summary"),
    "lead": ("How I work", "Where I'm strongest", "What I'm working on", "How I work with AI agents", "About this summary"),
}

PERSONA = re.compile(r"^\W*(i'?m|i am|as) (your |a |the )?(coach|mirror|analyst)\b|^\W*i (read|looked at|went through) ", re.I)
ADVICE_HEADING = re.compile(r"^#+\s*(what to try|try this|next steps|recommendations?)\b|^\*\*what to try", re.I | re.M)
LINK = re.compile(r"\]\(https?://|<https?://")
SOURCES_HEADING = re.compile(r"^#+\s*sources\b|^\*\*sources\*\*", re.I | re.M)
ANY_QUOTE = re.compile(r'["\u201c]([^"\u201d\n]+)["\u201d]')
REPORT_PATH = re.compile(r"`/[^`\n]+`")
QUOTE = re.compile(r'["\u201c]([^"\u201d\n]{6,200})["\u201d],? \((\d{4}-\d{2}-\d{2})\)')
HOME_PATH = re.compile(r"(?<![\w.])(?:/Users/|/home/|~/)\S+")


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
    """Items of the reply's last list that open with a quoted request the user could paste."""
    for block in reversed(text.strip().split("\n\n")):
        lines = [line for line in block.splitlines() if re.match(r"\s*([-*]|\d+\.)\s", line)]
        if lines:
            return [line for line in lines if re.match(r'\s*([-*]|\d+\.)\s+(\*\*)?["\u201c].{8,}?["\u201d]', line)]
    return []


def plain(text):
    return text.replace("\u2019", "'").replace("\u2018", "'").strip().rstrip(".").lower()


def headings(text):
    return [plain(re.sub(r"^\d+\.\s*", "", h)) for h in re.findall(r"^#{1,4}\s+(.+)$", text, re.M)]


def keep_out_terms(profile_text):
    """The bullets under the profile's Keep out heading: names, repos, and topics never to quote or share."""
    section = re.search(r"^#{2,3}\s*keep out\s*\n(.*?)(?=^#{1,3} |\Z)", (profile_text or "").replace("\r\n", "\n"), re.S | re.M | re.I)
    if not section:
        return []
    terms = [re.sub(r"[*`_]", "", item).split(" (")[0].strip() for item in re.findall(r"^\s*[-*]\s+(.+)$", section.group(1), re.M)]
    return [term for term in terms if len(term) >= 3]


def checks(mode, reply="", report="", keep_out=(), verify_quotes=True):
    """Every check that applies to this mode, as {name: {"pass": bool, "evidence": str}}."""
    found = {}

    def check(name, ok, evidence=""):
        found[name] = {"pass": bool(ok), "evidence": evidence}

    both = reply + "\n" + report
    if reply:
        first = opening(reply)
        check("no_persona_opening", not PERSONA.search(first), first[:120])
    dashes = sum(both.count(c) for c in "\u2013\u2014")
    check("no_long_dashes", dashes == 0, f"{dashes} found")
    # Whole words only, and never inside the report's own path, which may hold the user's name.
    unpathed = REPORT_PATH.sub("", both)
    leaked = sorted({term for term in keep_out if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", unpathed, re.I)})
    check("keep_out_terms_absent", not leaked, ", ".join(leaked))

    if report and mode in SECTIONS:
        wanted, seen = [plain(s) for s in SECTIONS[mode]], headings(report)
        order = [seen.index(s) for s in wanted if s in seen]
        missing = [s for s in SECTIONS[mode] if plain(s) not in seen]
        check("report_sections_in_order", not missing and order == sorted(order),
              f"missing: {', '.join(missing)}" if missing else "out of order" if order != sorted(order) else "")

    if mode == "mirror":
        heads = [m.group(0).strip() for m in ADVICE_HEADING.finditer(both)]
        check("mirror_has_no_advice_section", not heads, ", ".join(heads))
        links = len(LINK.findall(both))
        check("mirror_has_no_links", links == 0, f"{links} links")
        if reply:
            items = offers(reply)
            check("mirror_ends_with_3_to_5_offers", 3 <= len(items) <= 5, f"{len(items)} items in the last list")
            offers_at = reply.find(items[0].strip()) if items else len(reply)
            shown_path = re.search(r"`(/[^`\n]+\.md)`", reply[:offers_at])
            check("mirror_reply_gives_report_path_before_offers", bool(shown_path),
                  shown_path.group(1) if shown_path else "no absolute report path before the offers")
            deeper = [line for line in items if "deeper" in line.lower()]
            check("mirror_offers_a_deeper_read_and_says_what_it_is", deeper and len(deeper[0].split()) >= 6,
                  deeper[0].strip()[:100] if deeper else "no deeper offer")
    if mode == "coach":
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
        if reply:
            shown = [label for label in ("before", "after", "what changed") if re.search(rf"\*\*{label}\b", reply, re.I)]
            check("coach_reply_shows_before_and_after", len(shown) == 3, ", ".join(shown) or "none")

    quotes = sorted({(q, day) for q, day in QUOTE.findall(both)})
    if mode in ("share", "lead"):
        quoted = [q for q in ANY_QUOTE.findall(report) if len(q.split()) >= 3]
        check("shared_version_has_no_quotes", not quoted, "; ".join(f'"{q}"' for q in quoted)[:300])
        paths = sorted(set(HOME_PATH.findall(report)))
        check("shared_version_has_no_local_paths", not paths, ", ".join(paths)[:300])
        check("shared_version_has_no_links", not LINK.findall(report), "")
    elif verify_quotes:
        missing = [f'"{q}" ({day})' for q, day in quotes if not quote_found(q, day)]
        check("dated_quotes_exist", not missing, "; ".join(missing)[:400] or f"{len(quotes)} checked")
    return found


def add_arguments(parser):
    parser.add_argument("--mode", required=True, choices=MODES)
    parser.add_argument("report", nargs="?", help="the report file this run wrote")
    parser.add_argument("--reply", help="a file holding the draft chat reply")
    parser.add_argument("--profile", help="the profile whose Keep out list to enforce (default: ME.md in the data dir)")


def run(args, default_profile):
    if not args.report and not args.reply:
        sys.exit("lint needs a report, a --reply file, or both")
    profile = Path(args.profile) if args.profile else default_profile
    keep_out = keep_out_terms(profile.read_text()) if profile.exists() else []
    found = checks(args.mode, Path(args.reply).read_text() if args.reply else "",
                   Path(args.report).read_text() if args.report else "", keep_out)
    failed = {name: result["evidence"] for name, result in found.items() if not result["pass"]}
    print(json.dumps({"mode": args.mode, "passed": not failed, "failed": failed, "checked": sorted(found)}, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    import convo
    cli = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(cli)
    run(cli.parse_args(), convo.PROFILE)
