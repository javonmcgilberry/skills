#!/usr/bin/env python3
"""Validate know-thyself: routes, evals, samples, signal fixtures, and that nothing identifies its owner.

The skill lives at skills/know-thyself/ in its repository, and its guide is docs/know-thyself.md there. Identity
terms come from the home directory name, `git config user.name`, and one term per line in a gitignored
`.private-terms` file at the repository root (employer, product, and ticket names, for example). The identity scan
covers the skill's directory and the docs/know-thyself*.md pages, and the only place an identity term may appear is
the repository's own slug from its origin remote, inside an install command (`npx skills@latest add <slug>` or
`git clone https://github.com/<slug>.git`), because the repository is published under that name.
"""

import argparse
import contextlib
import datetime
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import convo  # noqa: E402

PROJECT = ROOT.parents[1]
GUIDE = PROJECT / "docs" / "know-thyself.md"
SKIP = {".git", ".cache", "reports", "__pycache__", ".ruff_cache"}
TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".txt", ".toml", ".yml", ".yaml", ""}

SKILL = ROOT / "SKILL.md"
SKILL_WORD_BUDGET = 500
MODES = {"mirror", "checkin", "coach", "trend", "recall", "lessons", "share", "lead", "init", "menu"}
REQUIRED_MODES = {"mirror", "coach"}
SAMPLE_AFTER_SIGNALS = {"altitude", "raw_material", "hard_target", "outside_judge", "aim_high",
                        "scope_control", "shipping_authority"}
failures = []


def report(ok, message):
    print(("PASS  " if ok else "FAIL  ") + message)
    if not ok:
        failures.append(message)


def scanned_files():
    """The skill's own text files and its pages under docs/, which together are what gets published as know-thyself."""
    skill = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES and not SKIP & set(p.relative_to(ROOT).parts)]
    return skill + sorted((PROJECT / "docs").glob("know-thyself*.md"))


def repo_slug():
    """owner/name of the GitHub repository the origin remote points at, or None."""
    url = subprocess.run(["git", "-C", str(PROJECT), "remote", "get-url", "origin"], capture_output=True, text=True).stdout.strip()
    found = re.search(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    return found.group(1).lower() if found else None


def without_install_slug(text, slug):
    """Lowercased text with the repository slug removed from install commands, the one place it may appear."""
    text = text.lower()
    if not slug:
        return text
    return re.sub(rf"(npx skills@latest add |git clone https://github\.com/){re.escape(slug)}(?:\.git)?(?![\w/-])", r"\1", text)


GENERIC_ACCOUNTS = {"runner", "root", "ubuntu", "user", "admin", "vscode", "codespace", "home", "ci"}


def owner_tokens():
    tokens = {Path.home().name.lower()} - GENERIC_ACCOUNTS
    name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout
    tokens |= {part.lower() for part in re.findall(r"[A-Za-z]{3,}", name)}
    private = PROJECT / ".private-terms"
    if private.exists():
        tokens |= {line.strip().lower() for line in private.read_text().splitlines() if line.strip() and not line.startswith("#")}
    return {t for t in tokens if len(t) >= 3}


def credited_names():
    """Bold names and one-word link titles under the guide's Credits heading."""
    section = re.search(r"^## Credits\n(.*?)(?=^## |\Z)", GUIDE.read_text(), re.S | re.M) if GUIDE.exists() else None
    if not section:
        return set()
    names = re.findall(r"\*\*([^*]+)\*\*", section.group(1)) + re.findall(r"\[([\w-]+)\]\(", section.group(1))
    return {word.lower() for name in names for word in re.findall(r"[\w-]{4,}", name)}


skill_text = SKILL.read_text()
front = re.match(r"---\n(.*?)\n---", skill_text, re.S)
report(bool(front) and all(f"\n{k}:" in "\n" + front.group(1) for k in ("name", "description")),
       "SKILL.md frontmatter has name and description")
words = len(re.findall(r"\b[\w'-]+\b", skill_text))
report(words <= SKILL_WORD_BUDGET, f"SKILL.md is {words} words (budget {SKILL_WORD_BUDGET})")

routed = set(re.findall(r"`((?:references|scripts|evals|samples)/[\w./-]+)`", skill_text))
for path in sorted(routed):
    report((ROOT / path).exists(), f"SKILL.md route {path} exists")
for name in ("mirror", "checkin", "coach", "lookups", "lessons", "voice", "init", "audiences", "routing"):
    path = ROOT / "references" / f"{name}.md"
    body = path.read_text() if path.exists() else ""
    last = re.findall(r"^#+ (.+)$", body, re.M)[-1:] or [""]
    report(last == ["Done when"], f"references/{name}.md ends on a Done when list")
all_reference_text = skill_text + "".join(p.read_text() for p in (ROOT / "references").glob("*.md"))
for path in sorted((ROOT / "references").iterdir()):
    report(f"references/{path.name}" in all_reference_text, f"references/{path.name} is routed from SKILL.md or a reference")

try:
    cases = json.loads((ROOT / "evals" / "cases.json").read_text())["cases"]
except (OSError, json.JSONDecodeError, KeyError) as error:
    sys.exit(f"FAIL  evals/cases.json unreadable: {error}")
ids = [c["id"] for c in cases]
report(len(ids) == len(set(ids)), f"{len(ids)} eval case ids are unique")
report(all(c.get("mode") in MODES and c.get("prompt") and c.get("expect") and c.get("report", c["mode"]) in MODES for c in cases),
       "every eval case has a known mode, a prompt, and what to expect, and any report it names is a known mode")
missing = REQUIRED_MODES - {c.get("mode") for c in cases}
report(not missing, f"eval cases cover the {sorted(REQUIRED_MODES)} modes" + (f" (missing {sorted(missing)})" if missing else ""))

emphasis_words = convo.load_vocab()
after = convo.detect((ROOT / "samples" / "opener.after.txt").read_text(), emphasis_words)
before = convo.detect((ROOT / "samples" / "opener.before.txt").read_text(), emphasis_words)
unmatched = SAMPLE_AFTER_SIGNALS - after
report(not unmatched, "sample rewrite hits every expected signal" + (f" (missing {sorted(unmatched)})" if unmatched else ""))
report(not before & set(convo.AMBITION_DIMENSIONS), "sample opener hits no ambition dimension")

result = subprocess.run([sys.executable, str(ROOT / "scripts" / "convo.py"), "check"], capture_output=True, text=True)
report(result.returncode == 0, "signal fixtures: " + (result.stdout.strip().splitlines() or [result.stderr.strip()])[-1])

def close(got, want, tolerance=0.0005):
    return all(abs(a - b) <= tolerance for a, b in zip(got, want, strict=True))


# Newcombe (1998), Statistics in Medicine 17:857-872, single-proportion (Wilson) and difference (method 10) examples.
WILSON_CASES = [((81, 263), (0.2553, 0.3662)), ((15, 148), (0.0624, 0.1605)), ((0, 20), (0.0, 0.1611)), ((1, 29), (0.0061, 0.1718))]
NEWCOMBE_CASES = [((56, 70, 48, 80), (0.0524, 0.3339)), ((9, 10, 3, 10), (0.1705, 0.8090))]
for (k, n), want in WILSON_CASES:
    got = convo.wilson(k, n)
    report(close(got, want), f"Wilson interval {k}/{n} = {tuple(round(v, 4) for v in got)}, expected {want}")
for (k1, n1, k2, n2), want in NEWCOMBE_CASES:
    got = convo.newcombe(k1, n1, k2, n2)
    report(close(got, want), f"Newcombe difference {k1}/{n1} vs {k2}/{n2} = {tuple(round(v, 4) for v in got)}, expected {want}")
adjusted = convo.bh_adjust([0.01, 0.04, 0.03, 0.005])
report(close(adjusted, [0.02, 0.04, 0.04, 0.02]), f"Benjamini-Hochberg adjustment = {adjusted}")

sparse = [{"month": m, "k": 2, "n": 5} for m in range(6)]
report(convo.sparkline(sparse) == "too few to chart", "trend survives months that are all under 10 sessions")
report(convo.sparkline([{"month": m, "k": k, "n": 20} for m, k in enumerate([0, 1, 2, 3, 4, 8])]) == "▁▂▃▃▅█",
       "trend scales to the busiest month")

misses = [(d["id"], phrase) for d in convo.SCORECARD for phrase in re.findall(r"“([^”]+)”", d["counts"])
          if d["id"] not in convo.detect(phrase, emphasis_words)]
report(not misses, "every example phrase in the definitions is counted by its own line" + (f": {misses[:6]}" if misses else ""))

incomplete = [d["id"] for d in convo.SCORECARD if not all(d.get(k) for k in ("label", "why", "counts"))]
report(not incomplete, "every habit has a label, a why, and example phrases" + (f": {incomplete}" if incomplete else ""))

empty, some = convo.proportion(0, 0), convo.proportion(5, 20)
report("no sessions" in convo.compare_markdown(
    {"habit_id": "delegation", "label": "Split work across agents", "since": "2026-01-01",
     "compared_with": {"since": "2025-12-01", "until": "2026-01-01"},
     "habit": {"since": some, "before": empty, "verdict": "too few to tell"},
     "corrected": {"since": some, "before": empty, "verdict": "too few to tell"}}),
    "compare survives an empty span before the date")
report("nothing to compare" in convo.payoff_text({"with": convo.proportion(4, 12), "without": empty}),
       "a card survives a habit every judged session showed")
quoted = convo.clean(convo.unwrap("context\n## My request for Codex:\nsee this log:\n## My request for Codex:\nold ask"))
report(convo.clean(quoted) == quoted and "see this log" in quoted, "re-cleaning a stored turn that quotes the Codex marker changes nothing")
wrapped = convo.redact('token=Some(Token(\\"abcd1234efgh5678ijkl\\")) next')
report("abcd1234" not in wrapped and convo.redact(wrapped) == wrapped, "a credential inside a wrapped value is fully redacted")
report(convo.admissible("you have explicit approval to merge") and not convo.admissible("<task-notification> done"),
       "a typed approval is kept while injected text is dropped")

# Robustness regressions, on synthetic inputs only: nothing here reads the user's corpus or history.
TODAY = datetime.datetime.now(datetime.UTC).date()


def session_row(day, name):
    """One human opener that scopes the work, dated at noon on `day` (None leaves it undated)."""
    return {"source": "pi", "session": name, "timestamp": f"{day}T12:00:00+00:00" if day else None, "cwd": "",
            "words": 10, "spawned": False, "origin": "human", "prose_words": 10, "signals": ["scope_control"],
            "text": "please keep it minimal and only change the parser file now"}


def run_on(rows, command, clean=None, **options):
    """Run a command in-process on a throwaway corpus of `rows`, returning what it printed and what it warned."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "corpus.db"
        db = convo.create(path)
        with db:
            convo.insert(db, rows)
            convo.write_meta(db, clean=clean or convo.CLEAN_HASH, coverage={"rules": convo.RULES_HASH})
        db.close()
        args = {"since": None, "until": None, "source": None, "cwd": None, "origin": "human", "recent_days": 60,
                "baseline_days": 180, "trend_months": 6, "definitions": False, "cards": None, "markdown": False, "seed": 7}
        saved, convo.DB = convo.DB, path
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                command(argparse.Namespace(**{**args, **options}))
        finally:
            convo.DB = saved
        return out.getvalue(), err.getvalue()


def holds(check):
    """Whether a check passes; an exception counts as a failure and is printed, so later checks still run."""
    try:
        return bool(check())
    except (Exception, SystemExit) as error:  # noqa: BLE001
        print(f"      {type(error).__name__}: {error}")
        return False


def scored(rows, **options):
    return json.loads(run_on(rows, convo.score, **options)[0])


def units(habit, corrected, plain, plain_corrected):
    return ([{"corrected": i < corrected, "found": {"opener": {"scope_control"}}} for i in range(habit)]
            + [{"corrected": i < plain_corrected, "found": {"opener": set()}} for i in range(plain)])


def tiny_windows():
    tiny = convo.window_change(convo.proportion(3, 8), convo.proportion(20, 40))
    rare = convo.window_change(convo.proportion(2, 50), convo.proportion(2, 50))
    return (tiny == rare == {"verdict": "too few to tell"} and convo.change_text(tiny) == "too few to tell"
            and "p" in (convo.window_change(convo.proportion(10, 50), convo.proportion(20, 50)) or {}))


def sparse_payoff():
    sparse = convo.payoff(units(12, 1, 30, 2), "scope_control")
    return ("p" not in sparse and "too few to tell" in convo.payoff_text(sparse)
            and "p" in convo.payoff(units(20, 10, 20, 2), "scope_control"))


def malformed_files():
    with tempfile.TemporaryDirectory() as tmp:
        codex, opencode = Path(tmp) / "rollout-x.jsonl", Path(tmp) / "msg.json"
        codex.write_text('{"type":"session_meta","payload":null}\n{"type":"response_item","payload":null}\n'
                         '{"type":"response_item","timestamp":{"at":1},"payload":{"type":"message","role":"user",'
                         '"content":[{"type":"input_text","text":"hello there agent"}]}}\n')
        opencode.write_bytes(b'{"role": "user", "id": "\xff\xfe"}')
        rows = convo.parse_file((convo.read_codex, codex))
        return (rows is not None and [row["timestamp"] for row in rows] == [None] and convo.read_opencode(opencode) == []
                and convo.parse_file((lambda _path: {}["missing"], codex)) is None)


FUTURE = (TODAY + datetime.timedelta(days=40)).isoformat()
RECENT = [session_row((TODAY - datetime.timedelta(days=1)).isoformat(), "recent"), session_row(FUTURE, "future")]
UNDATED = [session_row(None, "a"), session_row(None, "b")]


def future_sessions():
    card = scored(RECENT)
    checked = json.loads(run_on(RECENT, convo.compare, habit="scope_control",
                                since=(TODAY - datetime.timedelta(days=10)).isoformat())[0])
    return (card["windows"]["lately"]["sessions"] == 1 and checked["habit"]["since"]["n"] == 1
            and all(m["month"] <= TODAY.isoformat()[:7] for m in card["dimensions"][0]["monthly"]))


def dedupe_key():
    dated, undated = session_row("2026-01-01", "a"), session_row(None, "b")
    return (convo.row_key(dated) == convo.row_key({**dated, "session": "c"})
            and convo.row_key(undated) != convo.row_key({**undated, "session": "c"}) and convo.rank(dated) < convo.rank(undated))


def harness_patterns():
    warned = io.StringIO()
    with contextlib.redirect_stderr(warned):
        harness = convo.user_harness(["(", "", "x*", 5, "^ok$"])
    return harness is not None and harness.pattern == "(?:^ok$)" and warned.getvalue().count("skipping harness pattern") == 4


report(holds(tiny_windows), "a scorecard line with under 10 sessions a side or under 5 hits gets no test and reads too few to tell")
report(holds(sparse_payoff), "the payoff test skips sides with under 5 corrections between them")
report(holds(malformed_files), "a null Codex payload, an odd timestamp, and a non-UTF-8 OpenCode file parse without raising")
report(holds(future_sessions), "sessions dated after today count toward no window, span, or trend month")
report(convo.parse_cursor((Path("/nonexistent/state.vscdb"), [("c1", None, "")])) is None,
       "a Cursor database that can't be read costs only its own turns, never the whole mine")
report(holds(lambda: json.loads(run_on([session_row(None, "a")], convo.stats)[0])["date_range"] is None),
       "stats reports no date range instead of crashing when no turn has a date")
report(holds(dedupe_key), "a short turn repeated in another session is kept, and a dated copy wins over an undated one")
report(holds(harness_patterns), "a harness pattern that fails to compile or matches empty text is skipped with a warning")
report(holds(lambda: "Run: convo.py mine" in run_on(RECENT, convo.score, clean="older")[1]),
       "queries warn when the corpus was cleaned under older rules")
report(holds(lambda: scored(UNDATED)["first_session"] is None
             and "no session has a date" in run_on(UNDATED, convo.score, markdown=True)[0]),
       "the scorecard survives sessions that have no timestamps")

import lint  # noqa: E402

MIRROR_REPORT = "\n\n".join(f"## {heading}\n\nYou plan in small steps." for heading in lint.SECTIONS["mirror"])
LEAD_REPORT = "\n\n".join(f"## {heading}\n\nI plan in small steps." for heading in lint.SECTIONS["lead"])


def failed(mode, report_text, keep_out=()):
    return {name for name, result in lint.checks(mode, report=report_text, keep_out=keep_out, verify_quotes=False).items()
            if not result["pass"]}


def lint_catches():
    swapped = MIRROR_REPORT.replace("## How you work", "## Placeholder").replace("## The short version", "## How you work")
    return (not failed("mirror", MIRROR_REPORT)
            and failed("mirror", MIRROR_REPORT + "\nOne \u2014 two.") == {"no_long_dashes"}
            and "report_sections_in_order" in failed("mirror", swapped)
            and failed("mirror", MIRROR_REPORT + "\n[a](https://x.dev)") == {"mirror_has_no_links"}
            and failed("mirror", MIRROR_REPORT + "\nWorked on Atlas.", keep_out=["atlas"]) == {"keep_out_terms_absent"}
            and not failed("mirror", MIRROR_REPORT + "\nYou sample a lot. Saved at `/Users/sam/r.md`.", keep_out=["Sam"])
            and not failed("mirror", MIRROR_REPORT.replace("What's changed", "What\u2019s changed")))


def shared_versions():
    leaky = LEAD_REPORT + '\nI said "ship it when green" in /Users/sam/repo.'
    return not failed("lead", LEAD_REPORT) and failed("lead", leaky) == {"shared_version_has_no_quotes",
                                                                     "shared_version_has_no_local_paths"}


def keep_out_list():
    profile = "# Sam\n\n## Keep out\n- Atlas (the customer)\n- `payments-svc`\n- ok\n\n## How to talk to you\nSam"
    edited = profile.replace("## Keep out", "### Keep Out").replace("\n", "\r\n")
    return (lint.keep_out_terms(profile) == lint.keep_out_terms(edited) == ["Atlas", "payments-svc"]
            and lint.keep_out_terms("# Sam") == [])


def latest_reports():
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("2026-01-01-mirror.md", "2026-01-02-mirror-2.md", "2026-01-02-profile-3.md", "2026-01-03-coach.md", "notes.md"):
            (Path(tmp) / name).write_text("x")
        saved, convo.REPORTS = convo.REPORTS, Path(tmp)
        try:
            found = convo.latest_reports()
        finally:
            convo.REPORTS = saved
    return (found["mirror"]["path"].endswith("2026-01-02-profile-3.md") and found["coach"]["date"] == "2026-01-03"
            and found["checkin"] is None and found["share"] is None and found["lead"] is None)


def context_directives():
    with tempfile.TemporaryDirectory() as tmp:
        saved = convo.PROFILE, convo.REPORTS
        convo.PROFILE, convo.REPORTS = Path(tmp) / "ME.md", Path(tmp)
        try:
            fresh = json.loads(run_on(RECENT, convo.context, no_mine=True)[0])
            convo.PROFILE.write_text("# Sam")
            profiled = json.loads(run_on(RECENT, convo.context, no_mine=True)[0])
        finally:
            convo.PROFILE, convo.REPORTS = saved
    codes = [d.split(":")[0] for d in fresh["directives"]]
    return (codes == ["STALE_CORPUS", "NO_PROFILE"] and fresh["profile"]["exists"] is False
            and [d.split(":")[0] for d in profiled["directives"]] == ["STALE_CORPUS"] and profiled["profile"]["text"] == "# Sam")


report(holds(lint_catches), "lint passes a clean mirror report, curly apostrophes and a path holding a Keep out name included, "
       "and catches a dash, sections out of order, a link, and a Keep out word")
report(holds(shared_versions), "lint keeps quotes and local paths out of a version for others")
report(holds(keep_out_list), "the profile's Keep out list reads one short term per bullet, under any heading case or line ending")
report(holds(latest_reports), "context finds the newest report of each kind, counting -2 and -3 and older *-profile.md mirrors")
report(holds(context_directives), "context reports a stale corpus and a missing profile, and prints the profile once it exists")
report(set(lint.SECTIONS) <= MODES, "every mode lint knows report sections for is an eval mode")

practices_text = (ROOT / "references" / "practices.md").read_text()
tagged = set(re.findall(r"`([a-z_]+)`", practices_text)) & ({*convo.SIGNALS, *convo.DERIVED_SIGNALS} | {d["id"] for d in convo.SCORECARD})
scored = {d["id"] for d in convo.SCORECARD}
report(not scored - tagged, "every scorecard dimension has a practice" + (f" (missing {sorted(scored - tagged)})" if scored - tagged else ""))
unknown = {t for t in re.findall(r"\(`([a-z_]+)`", practices_text)} - scored
report(not unknown, "every practice tag names a scorecard dimension" + (f" (unknown {sorted(unknown)})" if unknown else ""))

tokens, slug = owner_tokens(), repo_slug()
leaks = [(p.relative_to(PROJECT), t) for p in scanned_files() for t in tokens
         if t in without_install_slug(p.read_text(errors="replace"), slug)]
report(not leaks, "nothing in the skill or its docs names its owner" + (f": {leaks[:5]}" if leaks else ""))

report(bool(credited_names()), "docs/know-thyself.md has a Credits section with bold names")

# Every source the skill cites is listed once, in references/sources.json, and the guide lists the same ones.
sources = json.loads((ROOT / "references" / "sources.json").read_text())
by_id = {s["id"]: s for s in sources}
report(len(by_id) == len(sources) and all(set(s) == {"id", "title", "publisher", "url"} and all(s.values()) for s in sources),
       f"{len(sources)} sources in sources.json have unique ids and an id, title, publisher, and url each")
insecure = [s["id"] for s in sources if not s["url"].startswith("https://")]
report(not insecure, "every source url is https" + (f": {insecure}" if insecure else ""))
cited = set(re.findall(r"\]\[([\w-]+)\]", practices_text))
defined = dict(re.findall(r"^\[([\w-]+)\]:\s*(\S+)\s*$", practices_text, re.M))
unknown_links = sorted((cited | set(defined)) - set(by_id))
report(not unknown_links, "every link id in practices.md is in sources.json" + (f": {unknown_links}" if unknown_links else ""))
undefined = sorted(cited - set(defined))
report(not undefined, "every link id cited in practices.md has a definition under Sources" + (f": {undefined}" if undefined else ""))
wrong_urls = sorted(i for i, url in defined.items() if i in by_id and by_id[i]["url"] != url)
report(not wrong_urls, "every link definition in practices.md matches its url in sources.json" + (f": {wrong_urls}" if wrong_urls else ""))
habit_ids = {i for d in convo.SCORECARD for i in d.get("sources", [])}
unsourced = [d["id"] for d in convo.SCORECARD if not d.get("sources")]
report(not unsourced, "every scorecard habit has at least one source" + (f": {unsourced}" if unsourced else ""))
unknown_habit_ids = sorted(habit_ids - set(by_id))
report(not unknown_habit_ids, "every scorecard source id is in sources.json" + (f": {unknown_habit_ids}" if unknown_habit_ids else ""))
coach_text = (ROOT / "references" / "coach.md").read_text()
tools_at = coach_text.find("## Tools you can hand over")
report(tools_at >= 0, "coach.md has a Tools you can hand over section")
tools = re.split(r"\n## ", coach_text[tools_at + 3:])[0] if tools_at >= 0 else ""
tool_ids = {i for ids in re.findall(r"Sources: ((?:`[\w-]+`(?:, )?)+)", tools) for i in re.findall(r"`([\w-]+)`", ids)}
unknown_tool_ids = sorted(tool_ids - set(by_id))
report(not unknown_tool_ids, "every hand-over tool source id is in sources.json" + (f": {unknown_tool_ids}" if unknown_tool_ids else ""))
unused = sorted(set(by_id) - cited - habit_ids - tool_ids)
report(not unused, "every source in sources.json is cited by a practice, a habit, or a tool" + (f": {unused}" if unused else ""))
guide = GUIDE.read_text() if GUIDE.exists() else ""
listed = re.search(r"^## Where the advice comes from\n(.*?)(?=^## |\Z)", guide, re.S | re.M)
readme_rows = re.findall(r"^- (.+), \[(.+)\]\((https://\S+)\)$", listed.group(1), re.M) if listed else []
report(sorted(readme_rows) == sorted((s["publisher"], s["title"], s["url"]) for s in sources) and len(readme_rows) == len(sources),
       "docs/know-thyself.md's source list matches sources.json exactly")
report(holds(lambda: "**For you.**" in (card := run_on(RECENT, convo.score, cards="scope_control")[0])
             and "where this comes from" not in card.lower()),
       "a rendered card leaves its sources to the end of the coaching reply")

print(f"\n{'FAILED' if failures else 'OK'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
