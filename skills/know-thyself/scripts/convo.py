#!/usr/bin/env python3
"""Mine the local AI conversation history of whoever runs this into one SQLite corpus, then measure, score, or search it.

  convo.py mine [--full] [--import PATH]   refresh corpus.db from every readable local store, parsing only new or
                                     changed sources; --full re-parses every source and keeps turns whose files are gone
  convo.py stats  [filters]          behavior metrics as JSON
  convo.py search [filters] [--regex RE | --signal NAME] [--context N] [--sample]
  convo.py score  [filters] [--recent-days N]   the habit scorecard; --markdown, --definitions, --cards id,id
  convo.py compare HABIT --since YYYY-MM-DD   a habit and later corrections after a date against the span before
  convo.py setup [--data-dir DIR] [--reports-dir DIR]   write the config, mine, and run the checks
  convo.py signals                   list signal names usable with --signal
  convo.py check                     run labeled fixtures against the signal rules
  convo.py coverage                  what the last mine read, skipped, and could not read
  convo.py export --jsonl PATH       write every turn as JSON lines
  convo.py paths                     where the database and reports live

Filters: --since YYYY-MM-DD --until YYYY-MM-DD --source codex,pi --cwd SUBSTRING --origin human,subagent,harness

Personal harness patterns, for prompts your own tools write in your name, go in the config file as
{"harness_patterns": ["^MyTool: "]}. They never enter the repository.
"""

import argparse
import collections
import concurrent.futures
import contextlib
import datetime
import hashlib
import inspect
import json
import math
import os
import random
import re
import sqlite3
import subprocess
import statistics
import sys
import zlib
from pathlib import Path

HOME = Path.home()
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or HOME / ".config") / "know-thyself" / "config.json"
DEFAULT_DATA = Path(os.environ.get("XDG_DATA_HOME") or HOME / ".local/share") / "know-thyself"


def read_config():
    """The config file as a dict. A broken file stops every command, because guessing would move the data dir."""
    if not CONFIG.exists():
        return {}
    try:
        config = json.loads(CONFIG.read_text())
    except (ValueError, OSError) as error:
        sys.exit(f"{CONFIG} isn't valid JSON ({error}); fix or delete it and run again")
    if not isinstance(config, dict):
        sys.exit(f"{CONFIG} must hold a JSON object; fix or delete it and run again")
    return config


def resolve_dirs():
    """Where data and reports live, and why: an environment variable wins, then the config file, then the default."""
    config = read_config()
    data = (os.environ.get("KNOW_THYSELF_DATA_DIR"), "KNOW_THYSELF_DATA_DIR") if os.environ.get("KNOW_THYSELF_DATA_DIR") else \
        (config["data_dir"], str(CONFIG)) if config.get("data_dir") else (DEFAULT_DATA, "default")
    data_dir = Path(data[0]).expanduser()
    reports = (os.environ.get("KNOW_THYSELF_REPORTS_DIR"), "KNOW_THYSELF_REPORTS_DIR") if os.environ.get("KNOW_THYSELF_REPORTS_DIR") else \
        (config["reports_dir"], str(CONFIG)) if config.get("reports_dir") else (data_dir / "reports", "default")
    return {"data": (data_dir, data[1]), "reports": (Path(reports[0]).expanduser(), reports[1])}


DIRS = resolve_dirs()
DATA, REPORTS = DIRS["data"][0], DIRS["reports"][0]
DB = DATA / "corpus.db"
PROFILE = DATA / "ME.md"
STALE_HOURS = 24
# Report kinds by filename suffix; older versions wrote the mirror as *-profile.md.
REPORT_KINDS = {"mirror": ("mirror", "profile"), "coach": ("coach",), "share": ("shareable",), "lead": ("lead",)}
# What older versions kept instead of DB; the first run imports them and renames each with a .migrated suffix.
LEGACY_CORPUS, LEGACY_MANIFEST, LEGACY_VOCAB, LEGACY_COVERAGE = (
    DATA / name for name in ("corpus.jsonl", "manifest.json", "vocab.json", "coverage.json"))
OPENCODE = HOME / ".local/share/opencode/storage"
FIXTURES = Path(__file__).resolve().parents[1] / "references" / "signal-fixtures.jsonl"
# The public guides each scorecard habit comes from, keyed by the ids in SCORECARD's `sources`.
GUIDES = {s["id"]: s for s in json.loads((FIXTURES.parent / "sources.json").read_text())}
LARGE_PASTE_WORDS = 2000

BLOCKED_STARTS = (
    "# agents.md instructions", "# files mentioned by the user:", "# files pasted by the user:",
    "# response annotations:", "## code review guidelines:", "<permissions instructions>",
    "<app-context>", "<collaboration_mode>", "<codex_internal_context", "<in-app-browser-context",
    "<recommended_plugins>", "<subagent_notification>", "<task-notification>", "<turn_aborted>",
    "the following is the codex agent history",
    "important: do not use any tools. do not try to read or access any files.",
    "run the next iteration now. use the persisted autoresearch state as needed",
    "caveat: the messages below were generated", "<goal_context>", "[goal confirmation",
)
STRIP_TAGS = ("environment_context", "local-command-caveat", "skill", "command-name", "command-message",
              "command-args", "browser_instructions", "system-reminder")

SLASH_NOISE = {"/model", "/status", "/context", "/help", "init"}
HARNESS_CWD = re.compile(r"^(/private)?/tmp/|^/var/folders/|\.scratch|autoresearch", re.I)
HARNESS_TEXT = re.compile(
    r"^(task:|you are a (delegated )?subagent|read change\.md and|reply (with the word )?ok\b|hello\W*$|say (hi|ok)\W*$|\d+-minute heartbeat|the previous pi operation stopped|run the next iteration now|you are (a|an|the) |perform one final )"
    r"|\(repo /|\bthe user (returns|authorized)\b|\buser asleep\b|\(operator:|\bautonomous (\d+-min )?(stall )?check\b", re.I)
TICKET_BRIEF = re.compile(r"^# [A-Z][A-Z0-9]+-\d+:")

# Signals run on prose(): the text the user typed, with code, logs, links, paths, and pasted agent markdown removed.
# Any change here must keep `convo.py check` passing against references/signal-fixtures.jsonl.
SIGNALS = {
    "short_confirmation": r"^\W*(yes|yep|yeah|ok|okay|confirmed|sounds good|let'?s do it|go ahead|do it)\W*$",
    "agent_rework": (
        r"^\W*(no|nope|nah)\b(?! (biggie|need|worries|problem|rush|pressure)\b)"
        r"|\bi (just |already )?(reverted|undid|rolled back)\b"
        r"|\byou (didn'?t|did not|still|keep|missed|broke|ignored|forgot|removed|deleted|changed|added)\b"
        r"|\bwalk (it |that |this |those |them |all )?(of )?(those |these |the )?(\w+ )?(changes? )?back\b"
        r"|\b(revert|undo|roll back) (it|that|this|those|these|the|all|your|what)\b"
        r"|\b(that'?s|this is|it'?s) (not (right|it|what)|wrong)\b"
        r"|\b(that|this|it) (isn'?t|is not|doesn'?t|does not) (right|work|make sense)"
    ),
    "scope_control": (
        r"\b(minimal(ly)?|smallest|least invasive|narrow(ly|er)?|out of scope|no fallbacks?)\b"
        r"|\b(don'?t|do not) (touch|change|modify|add|refactor)\b|\bleave .{1,40} alone\b"
        r"|\bwithout (changing|touching|modifying)\b|\bonly (change|touch|update|modify|edit|fix|do)\b"
        r"|\bkeep (it|this|the (change|diff|pr)) (small|simple|minimal|focused|tight|scoped)\b|\bscope (it|this|that) (down|to)\b"
    ),
    "overengineering": (
        r"\bover.?engineer|\bover.?complicat|\btoo (much|complex|complicated|verbose|many \w+)\b"
        r"|\bsimpl(er|est|ify)\b|\bwhy (do|did) (we|you) (need|create|add|introduce)"
    ),
    "evidence_demand": (
        r"\b(verify|validate|evidence|prove|reproduce|repro|against the code|source of truth|show me)\b"
        r"|\b(look at|inspect|check|read) the (actual |current )?(code|source|implementation|docs)\b"
        r"|\bdid you (actually )?(test|check|verify|run|confirm|look)\b|\bhow do you know\b"
    ),
    "end_user_reproduction": r"\b(end user|e2e|end.to.end|in the browser|dogfood|real user|pixel|visually|as a user|manually test)\b",
    "quality_gate": r"\b(tests?|lint|typecheck|tsc|ci|flaky|regression|tdd|jest|playwright|cypress)\b",
    "shipping_action": r"\b(commit|push|open (a )?(draft )?pr|pull request|merge|release|publish|deploy|ship|babysit)\b",
    "research_action": r"\b(research|investigate|look into|find out|figure out|compare|alternatives)\b",
    "implementation_action": r"\b(implement|fix|refactor|build|create|update|change|remove|add)\b",
    "planning_action": r"\b(plan|spec|design|architecture|approach|brainstorm|lock in)\b",
    "communication_action": r"\b(slack|standup|retro|rewrite|humanize|message|status update|pr description)\b",
    "certainty_check": r"\b(are you sure|you sure\b|is that (right|true|accurate|correct)|how do you know|according to (what|who|whom)|double.check|really\?)",
    "analogy_search": r"\b(how does .* do this|copy the same approach|existing pattern|similar .* implementation|what does .* do)\b",
    "agent_orchestration": r"\b(agent|subagent|skill|model|prompt|codex|claude|cursor|pi|autoresearch|council)\b",
    "repeated_constraint": (
        r"\bi (already |just |literally )?(told|said|asked|mentioned)( you)?( that| this| to)?\b(?! (it|that) (was|is) (fine|ok))"
        r"|\b(like|as) i (said|mentioned)\b|\bi made it clear\b|\bhow many times\b|\bi keep (telling|saying|asking)\b"
        r"|\byou keep\b|\bfor the (second|third|\w+th|last) time\b"
        r"|\bstill (not|doesn'?t|isn'?t|broken|showing|happening|failing|seeing|there)\b"
    ),
    "profanity": r"\b(fuck\w*|shit\w*|wtf|bullshit|goddamn)\b",
    "exasperation": r"[!?]{3,}|\bugh+\b",
    "contains_question": r"\?",
    "altitude": (
        r"\b(the (real |end |ultimate |bigger )?goal (is|here)|end goal|goal beyond|going forward|from now on)\b"
        r"|\bnever (happens? again|regress(es)?|breaks? again)\b|\bprevent (this|it|these|regressions?|future)\b"
        r"|\bkeep (it|this|the \w+|\w+) (green|fast|stable|crash.free|passing|working|healthy)\b"
        r"|\bso (this|it) (doesn'?t|never|won'?t) happen"
    ),
    "hard_target": (
        r"\b(under|below|less than|at least|at most|within|target(ing)?|aim for|goal of|down to)\s+~?\d[\d.,]*\s*"
        r"(ms|milliseconds?|s|secs?|seconds?|minutes?|mins?|%|x|kb|mb|gb|lines?|loc|runs?|requests?|errors?|flakes?)\b"
        r"|\b\d+x (faster|smaller|fewer|less)\b"
        r"|\bzero (\w+ )?(errors?|crashes|failures|regressions|flakes?|flicker|warnings)\b"
    ),
    "raw_material": (
        r"\b(raw (data|logs?|events?)|logs|log (files?|output|lines)|traces?|profiler|profiling|(cpu|performance|heap) profiles?|crash (reports?|dumps?)|stack ?traces?|datadog|sentry"
        r"|metrics|har file|heap snapshot|flame ?graph|query (the|our)|snowflake|hex|network (tab|waterfall|requests)"
        r"|lighthouse|telemetry|production data|real (data|users?|traffic))\b"
    ),
    "expert_method": (
        r"\bwhat would (a|an|the) (\w+ ){0,2}(expert|senior|staff|principal|top|best|world.class|seasoned)\b"
        r"|\b(top|best|world.class|expert|senior|staff|principal) (\w+ )?(engineers?|professionals?|practitioners?|designers?|researchers?) (would|do|use)\b"
        r"|\bhow (would|do) (experts?|professionals|the best)\b|\b(git bisect|bisect|statistical(ly)?|benchmark(s|ing)?|instrument(ed|ation)?|first principles)\b"
        r"|\bdeeper version\b|\bstate of the art\b"
    ),
    "outside_judge": (
        r"\b(done when|pass(es)? (when|if)|success (criteria|looks like|means|is when)|acceptance criteria|definition of done)\b"
        r"|\b(a |the )?(failing|red) test( first)?\b|\btest that fails\b|\bfails? before and pass(es)? after\b"
        r"|\bbefore.and.after (numbers|measurements?|screenshots?|timings?|benchmarks?)\b|\bmeasure (it |this )?(before|first)\b"
        r"|\bverify (it |this |that )?(by|with|using|in the browser|end.to.end)\b|\breproduce (it |the bug |this )?(first|before)\b"
        r"|\bhow will (we|you|i) know\b|\bproof (that|it)\b|\bpass\s*[=:]"
    ),
    "challenge_assumptions": (
        r"\b(poke holes|devil'?s advocate|adversarial(ly)?|steel.?man|disprove|falsify|try to break|red.?team|prove me wrong)\b"
        r"|\bchallenge (my|our|the|this|these|that) \w+|\bwhat am i missing\b|\bwhere am i wrong\b|\bpush back\b"
        r"|\b(check|test|question|verify|challenge) (my|our|the|that|this) assumptions?\b|\bis (this|that|it) (actually|really) (true|the case|the cause)\b"
    ),
    "range_fields": (
        r"\bfrom (the|a|an) (\w+ ){0,2}(perspective|lens|point of view|standpoint)\b"
        r"|\b(other|different|multiple|adjacent|outside) (fields|disciplines|domains|perspectives|lenses|specialists)\b"
        r"|\bbring in (a|an|some) \w+|\bassemble (a|the) (crew|team)\b"
        r"|\bwhat would (a|an) (designer|pm|product manager|security|sre|ux|qa|data scientist|editor|journalist|lawyer|economist|statistician|accountant)"
    ),
    "aim_high": (
        r"\b(be (more )?ambitious|aim (high|higher)|raise the bar|go deeper|(it'?s|that'?s|treat (it|that|this) as) (possible|solvable|doable|reachable|reasonable)"
        r"|keep going until|don'?t stop until|until (it|this|everything|all \w+) (is|are|passes|pass|works)|no matter how long)\b"
    ),
    "shipping_authority": (
        r"\b(don'?t|do not) (commit|push|merge|open a (draft )?pr|deploy|publish)\b"
        r"|\b(commit|push|merge|open a (draft )?pr|ship)( it| this| that)? (when|once|after|if)\b"
        r"|\b(investigate|research|read) only\b|\bread.only\b|\bno code changes\b|\bjust (investigate|research|explain|tell me)\b"
        r"|\b(open|create) a draft pr\b|\bstop before\b"
    ),
    "plan_first": (
        r"\b(plan mode|make a plan|write (up )?a plan|propose a plan|come up with a plan|plan (it|this) (out|first))\b"
        r"|\bbefore you (start|write|code|edit|implement|touch)\b|\b(don'?t|do not) (start|write|code|implement|edit) (yet|until)\b"
    ),
    "context_management": (
        r"\b(/compact|compaction|compacting|(when you|before you|after you) compact|compact (the|this) (context|session|conversation|thread)|context window|fresh (session|context|chat)|new (session|chat|thread)|hand ?off|checkpoint)\b"
        r"|\bsummari[sz]e (where we are|the session|progress|what we|so far)\b|\bstate ledger\b"
    ),
    "long_runs": (
        r"(?<![\w/])/(goal|loop)\b|\b(run (it |this )?until (done|green|it passes|everything)|keep going until|autonomous(ly)?|overnight)\b"
        r"|\bwhile i'?m (away|asleep|gone|out)\b|\bwalk away\b"
    ),
    "delegation": r"\b(sub.?agents?|spawn (an? |some )?agents?|parallel agents|in parallel|delegate|fan.?out|worktrees?)\b",
    "model_choice": (
        r"\b(use|switch to|try|with) (haiku|sonnet|opus|gpt.?\d\S*|gemini|o\d|a (cheaper|smaller|faster|stronger|bigger) model)\b"
        r"|\bwhich model\b|\breasoning effort\b|\bthinking (level|budget)\b"
    ),
    "independent_review": (
        r"\b(second opinion|fresh.(eyes|context) review|independent (review|reviewer)|cross.?check|cold review(er)?)\b"
        r"|\b(another|different|separate) (agent|model|reviewer) (to )?(review|check|verify)\b"
    ),
    "teach_once": (
        r"\b(add|put|update|write|edit|improve|encode|record)\b[^.?!\n]{0,40}\b(agents|claude)\.md\b"
        r"|\bremember (this|that) (for next time|going forward)\b|\bencode (this|that|it)\b"
        r"|\b(make|create|write|turn (this|it|that) into) (a |an )?(new )?(skill|hook|lint rule|lint|rule|check)\b"
    ),
    "guardrails": (
        r"\b(pre.?commit hook|(pre|post).?tool.?use|stop hook|permission mode|allowed.?tools|auto.?approv\w*|sandbox mode)\b"
        r"|\bhook (that|to) (block|enforce|run|gate|check)\b"
    ),
    "automation": (
        r"\b(headless|cron( job)?|scheduled (run|job|task|prompt)|nightly (run|job|check|build)|on a schedule)\b"
        r"|\b(set up|add|write|create|wire)\b[^.?!\n]{0,30}\b(github action|workflow|ci job)\b"
        r"|\b(claude|pi|codex) (-p|exec)\b"
    ),
    "share_setup": (
        r"\b(package|bundle|ship|publish) (this|these|it|them|the|our|my)( \w+)? as a plugin\b|\bshare (this|it|them) with (the|my) team\b"
        r"|\bpublish (the|this) (skill|plugin)\b|\bopen.?source (this|it)\b|\b(team|shared) (skills|plugin|setup)\b"
    ),
    "decompose": (
        r"\b(break (this|it|that) (down|up|into)|step by step|in (two|three|\d+) (steps|parts|phases)|one (step|thing) at a time)\b"
        r"|\bfirst\b[^.?!\n]{3,80}\bthen\b"
    ),
    "audience_format": (
        r"\bfor (a|an|the|my) (pm|product manager|exec\w*|leadership|manager|team|reviewer|customer|new hire|non.?technical \w+|engineer)s?\b"
        r"|\b(as|in) (a )?(table|bullet(ed)? list|bullets|json|one paragraph|a few sentences|checklist|tl;?dr)\b"
        r"|\b(under|at most|no more than) \d+ (words|sentences|lines|bullets)\b"
    ),
    "role_framing": (
        r"\b(act|respond|answer|review (it|this|that|the)( \w+)?|think|write (it|this)) (as|like) (a|an|the|my|our) (\w+ ){0,2}"
        r"(reviewer|engineer|sre|pm|product manager|designer|editor|tech lead|architect|tester|qa|auditor|new hire|on.?call|maintainer|skeptic|mentor|interviewer|copywriter|analyst)s?\b"
        r"|\b(take|play|assume|adopt) (on )?the role of\b|\byou'?re (now )?(acting|playing) (as )?(a|an|the)\b"
        r"|\b(put on|wear) (your|a|an|the) \w+ hat\b|\bpretend (you'?re|you are|to be) (a|an|the)\b"
),
    "task_type": (
        r"\b(this is|it'?s|treat (this|it) as|think of (this|it) as) (a |an )?(just |purely |mainly |mostly |more of )?(a |an )?"
        r"(brainstorm(ing)?|analysis|research (task|question)|investigation|first draft|rough draft|spike|exploration|exploratory (task|pass))\b"
        r"(?! (pr|pull|branch|doc|docs|document|notes?|paper|comment|thread|ticket|link|repo|file|of|in|on|at|from|by|that|i|we|you)\b)"
        r"|\b(brainstorm|research|analysis|exploration|investigation),? not (implementation|a fix|code|coding|a decision|a plan)\b"
        r"|\b(go wide|range widely|cast a wide net|quantity over quality)\b|\bdon'?t (self.?edit|filter|narrow|judge|rank) (them |anything )?yet\b"
        r"|\bgive me (at least )?(\d{2,}|ten|fifteen|twenty|a dozen|lots of|a bunch of) (\w+ )?(ideas|options|angles|approaches|names|variations|directions|hypotheses)\b"
),
    "targeted_iteration": (
        r"\b(keep|leave) (everything else|the rest|all else)\b(?! (of|running|working|green|passing|in sync|to me)\b)"
        r"|\b(the rest|everything else) (is|looks|reads) (good|fine|great|right|solid|perfect)\b"
        r"|\bsame (thing |again |as before )?,? ?but (shorter|longer|tighter|punchier|simpler|more \w+|less \w+|without|with)\b"
        r"|\b(close|almost|nearly|good|great)[.,!;]* (just|but|only) (change|fix|tighten|shorten|redo|rewrite|tweak|swap|cut|drop|rework) the \w+"
),
    "structured_report": (
        r"(?<!user )(?<!user-)\b(sub.?agents?|agents?|reviewers?|workers?|scouts?|each one)\b[^.?!\n]{0,80}"
        r"\b(report|return|reply|respond|come back|hand back)\b[^.?!\n]{0,60}"
        r"\b(format|template|schema|sections?|json|table|headings|fields|file.?(and.)?line|severity|verdict|evidence|obstacles|blockers)\b"
        r"|\b(obstacles|blockers|workarounds) (you|they|it) (hit|found|ran into|encountered|discovered)\b"
        r"|\bstructured (report|summary|output|findings)\b"
),
    "rewind_restart": (
        r"(^|\s)/rewind\b|\brewind (to|back|this|that|it|the (conversation|session|chat|thread))\b"
        r"|\b(go|jump|roll) back to (the |my |that |before (the|my|that|your) )(last |previous |earlier )?(checkpoint|prompt|message|turn)\b"
        r"|\brestore (the |that )?(conversation|checkpoint)\b"
        r"|\b(let'?s|we should|i want to|just) (start|begin) (over|again)\b"
        r"|\bscrap (this|that|it|all (of )?(this|that)|everything) and\b"
),
    "grounding": (
        r"\b(it'?s|that'?s) (ok|okay|fine|acceptable) to say (you )?(don'?t|do not|can'?t) know\b"
        r"|\b(say|tell me|admit) (so )?(if|when) you (don'?t|do not|can'?t|cannot) (know|find|verify|confirm)\b"
        r"|\bif you('?re| are) not sure,? (say so|just say|tell me|don'?t guess)\b"
        r"|\bdon'?t (guess|make (it|anything|things) up|invent (anything|apis?|functions?|numbers?))\b"
        r"|\b(answer|work|rely) only (on|from) (the|this|these|what)\b|\bonly from (the|this|these) (docs?|files?|code|source|logs?|spec|diff|transcript)\b"
        r"|(?<!we )(?<!they )(?<!i )(?<!you )\bcite (the |each |every |your )?(source|sources|file|line|lines|section)\b|\bquote (first|before)\b|\bpull (the )?(exact )?quotes? (first|before)\b"
),
    "task_context": (
        r"\b(steps to reproduce|repro steps|expected (behavior|result|output)|actual (behavior|result|output)|source of truth)\b"
        r"|\bon (the |my |this )?branch\b|\bpr ?#?\d+\b|(?-i:\b[A-Z][A-Z0-9]{1,9}-\d+\b)|\b(design doc|figma (file|link|frame))\b"
    ),
}
SIGNAL_RE = {name: re.compile(pattern, re.I) for name, pattern in SIGNALS.items()}
DERIVED_SIGNALS = {
    "caps_emphasis": "an all-caps word the user usually types in lowercase (the vocab in corpus.db), so acronyms like API never count",
    "five_words_or_fewer": "prose has five words or fewer",
    "short_context_dependent": "prose of 25 words or fewer that leans on prior context (this, that, keep going, same thing)",
}
# `level` says what a dimension scores: the opening prompt of a session, or any turn in it.
# `area` groups dimensions for coaching and matches a section of references/practices.md.
SCORECARD = [
    {"id": "altitude", "why": "Naming the larger goal lets the agent prevent the next occurrence, not only patch this one.", "counts": "“the real goal is”, “going forward”, “so this never happens again”, “keep CI green”", "label": "Name the goal behind the goal", "level": "opener", "area": "ambition",
     "sources": ["anth-prompting-bp", "felix-ambitious"],
     "nudge": "Name the goal beyond the goal: what should be true after this lands, and whether the agent should keep it true instead of fixing one instance."},
    {"id": "hard_target", "why": "A number gives the agent something to measure against and tells you when to stop.", "counts": "“under 200 ms”, “within 2 minutes”, “zero flakes”, “10x faster”", "label": "Set a hard number to hit", "level": "opener", "area": "ambition",
     "sources": ["anth-success-criteria", "oai-reasoning-bp", "felix-ambitious"],
     "nudge": "Give a specific, hard number (200 ms, zero flakes, under 50 lines) and say it is reachable, instead of asking for 'faster' or 'better'."},
    {"id": "raw_material", "why": "Logs, traces, and real data let the agent find the actual cause instead of reasoning from your summary of it.", "counts": "“check the logs”, “pull the traces”, “a CPU profile”, “the crash reports”, “Datadog”, “Sentry”", "label": "Hand over the raw logs and data", "level": "opener", "area": "ambition",
     "sources": ["anth-cc-best-practices", "felix-ambitious"],
     "nudge": "Point the agent at the rawest material (logs, traces, crash reports, real data) instead of your summary of it."},
    {"id": "expert_method", "why": "Asking for the method a strong engineer would use gets real instruments, such as profiling or bisecting, instead of guesses.", "counts": "“what would a senior engineer do”, “benchmark it”, “git bisect”, “from first principles”", "label": "Ask how an expert would do it", "level": "opener", "area": "ambition",
     "sources": ["anth-multi-agent", "felix-ambitious"],
     "nudge": "Ask what a top professional would do here and which instruments they would use, then require those methods, not just their vocabulary."},
    {"id": "range_fields", "why": "Another discipline's view catches problems your own field's habits miss.", "counts": "“from a security perspective”, “other disciplines”, “bring in a designer”", "label": "Bring in another field's eyes", "level": "opener", "area": "ambition",
     "sources": ["felix-ambitious"],
     "nudge": "Bring in another field and its real methods (a designer's critique, a security review, an editor's pass), ideally as separate subagents."},
    {"id": "aim_high", "why": "Saying a hard target is reachable keeps the agent going past its first plausible answer.", "counts": "“keep going until it passes”, “it's doable”, “treat that as reachable”, “raise the bar”", "label": "Say the hard target is reachable", "level": "opener", "area": "ambition",
     "sources": ["anth-cc-best-practices", "felix-ambitious"],
     "nudge": "Give permission to aim high and to fail against an honest check: 'keep going until it passes, report real numbers even if the target is missed.'"},
    {"id": "outside_judge", "why": "The agent stops when your check passes, not when it believes it's done, so a claimed fix is something you can verify.", "counts": "“done when”, “passes if”, “acceptance criteria”, “write a failing test first”, “before and after numbers”", "label": "Say how you'll know it worked", "level": "opener", "area": "briefing",
     "sources": ["anth-cc-best-practices", "felix-ambitious"],
     "nudge": "Say what, other than the agent, proves it worked (a failing test turned green, before-and-after numbers, a browser repro) and what counts as a pass."},
    {"id": "scope_control", "why": "Stating the edges up front stops the agent from tidying, refactoring, or adding things you didn't ask for.", "counts": "“keep it minimal”, “the smallest change”, “out of scope”, “don't touch the reducer”, “keep the diff small”", "label": "Say what's in and out of scope", "level": "opener", "area": "briefing",
     "sources": ["anth-prompting-bp", "oai-codex-bp"],
     "nudge": "State the allowed scope and non-goals in the first prompt, so you are not correcting overreach after the diff exists."},
    {"id": "shipping_authority", "why": "Without a limit, the agent decides for itself whether to commit, push, or open a PR, and you end up undoing what it shipped.", "counts": "“investigate only”, “don't commit”, “don't push”, “open a draft PR”, “commit once it's green”", "label": "Say how far the agent can go", "level": "opener", "area": "briefing",
     "sources": ["anth-prompting-bp", "anth-cc-best-practices"],
     "nudge": "Say how far the agent may go (investigate, edit, commit, draft PR, merge) before it starts."},
    {"id": "task_context", "why": "The agent can't see your ticket, branch, or the bug you hit; naming them stops it from working on a guess.", "counts": "“PROJ-142”, “PR #812”, “on my branch”, “steps to reproduce”, “expected behavior”", "label": "Point at the ticket, branch, or repro", "level": "opener", "area": "briefing",
     "sources": ["anth-cc-best-practices", "oai-codex-bp"],
     "nudge": "Anchor the task: branch, ticket, repro steps, expected versus actual behavior."},
    {"id": "decompose", "why": "A request that hides several jobs gets shallow work on each; steps give you a result to check before the next one builds on it.", "counts": "“step by step”, “in three phases”, “first reproduce it, then fix it”, “break this down”", "label": "Break big asks into steps", "level": "opener", "area": "briefing",
     "sources": ["anth-prompting-bp", "pstack-sequence-units"],
     "nudge": "Split a multi-part request into ordered steps or phases, each with its own output, instead of one ask that bundles them."},
    {"id": "audience_format", "why": "Naming the reader and the shape gets a draft you can use instead of one you rewrite.", "counts": "“for a reviewer”, “for a non-technical PM”, “as a table”, “in bullets”, “under 150 words”", "label": "Say who it's for and what shape", "level": "opener", "area": "briefing",
     "sources": ["oai-prompting", "aif-cheatsheet"],
     "nudge": "Say who the output is for and the shape it should take (a table, five bullets, a PR description under 150 words)."},
    {"id": "role_framing", "why": "A concrete working role sets the depth and the standard the agent works to.", "counts": "“act as a reviewer”, “review this as a security engineer”, “think like a staff engineer”", "label": "Give the agent a working role", "level": "opener", "area": "briefing",
     "sources": ["anth-prompting-bp", "felix-ambitious"],
 "nudge": "Give the agent a working role that sets depth and audience (a reviewer reading a stranger's diff, an on-call engineer with ten minutes), not a bare 'you are an expert' label."},
    {"id": "task_type", "why": "Brainstorming wants range and analysis wants rigor; naming the kind of task tells the agent which.", "counts": "“this is a brainstorm”, “treat this as a spike”, “go wide”, “give me 20 ideas”", "label": "Say what kind of task it is", "level": "opener", "area": "briefing",
     "sources": ["anth-cc-best-practices", "oai-prompting"],
 "nudge": "Say what kind of task this is (analysis, research, draft, brainstorm, code change), so the agent knows where to be strict and where to range widely."},
    {"id": "targeted_iteration", "why": "Changing only the part that missed keeps what worked and tells you which change fixed it.", "counts": "“keep the rest”, “the rest looks good”, “same thing but shorter”, “close, just change the intro”", "label": "Fix the one part that missed", "level": "session", "area": "briefing",
     "sources": ["oai-prompting"],
 "nudge": "When output misses, name the one part that failed and what to change, and keep the rest, instead of re-asking the whole thing."},
    {"id": "structured_report", "why": "A fixed report shape tells a subagent when it's done and makes its results easy to check.", "counts": "“have each agent report back with sections”, “have each subagent return file and line evidence”, “list the obstacles you hit”", "label": "Ask agents for a set report shape", "level": "session", "area": "orchestration",
     "sources": ["anth-cc-best-practices", "anth-multi-agent", "skj-subagents"],
 "nudge": "When you delegate, spell out the report each subagent returns (fixed sections, file and line evidence, an obstacles list), so it knows when it is done."},
    {"id": "rewind_restart", "why": "Going back to before a wrong turn removes the bad path from the agent's context; piled-on corrections keep it there.", "counts": "“/rewind”, “go back to the last checkpoint”, “let's start over”, “scrap it and redo it”", "label": "Restart instead of piling on fixes", "level": "session", "area": "steering",
     "sources": ["anth-cc-best-practices", "cc-checkpointing"],
 "nudge": "When a turn goes wrong, rewind to before it or restart from a short summary and re-brief, instead of stacking corrections on a bad path."},
    {"id": "grounding", "why": "Permission to say 'I don't know' and a request for sources cut invented APIs and confident wrong answers.", "counts": "“don't guess”, “say if you don't know”, “only from these files”", "label": "Allow 'I don't know' and ask for sources", "level": "opener", "area": "checking",
     "sources": ["anth-reduce-hallucinations"],
 "nudge": "Build checking into the brief by saying 'I don't know' is acceptable, limiting answers to the sources you named, and asking for a citation behind each claim."},
    {"id": "challenge_assumptions", "why": "Testing your own theory first keeps a fix from being built on a wrong diagnosis.", "counts": "“poke holes in this”, “try to disprove it”, “challenge my assumptions”, “is that really the cause”", "label": "Test your own theory first", "level": "opener", "area": "checking",
     "sources": ["oai-codex-bp", "felix-ambitious", "pstack-attack-premise"],
     "nudge": "Hand over a belief to test: 'we think the cause is X; try to reproduce that from the raw data before fixing.'"},
    {"id": "evidence_demand", "why": "Agents state things confidently whether or not they checked; asking for proof catches the ones they didn't.", "counts": "“verify”, “prove it”, “reproduce it”, “show me”, “did you actually test this”, “look at the actual code”", "label": "Ask for proof", "level": "session", "area": "checking",
     "sources": ["anth-cc-best-practices", "pstack-prove-it-works"],
     "nudge": "Ask for evidence (the code path, a repro, a test run) before accepting a claim, and say which evidence counts."},
    {"id": "independent_review", "why": "A fresh reviewer reads the diff without the author's reasoning, so it catches what the author talked itself into.", "counts": "“get a second opinion”, “a fresh-eyes review”, “have another model review it”", "label": "Get a fresh reviewer on risky work", "level": "session", "area": "checking",
     "sources": ["anth-cc-best-practices", "anth-effective-agents"],
     "nudge": "Have a fresh agent or a different model review risky work from the diff and the brief, not from the author's summary."},
    {"id": "plan_first", "why": "A wrong plan costs one message to fix; a wrong diff costs a revert.", "counts": "“plan mode”, “make a plan first”, “don't code until the plan is approved”, “before you start”", "label": "Get a plan before any edits", "level": "session", "area": "steering",
     "sources": ["cc-common-workflows", "oai-codex-bp"],
     "nudge": "Ask for a plan, or use plan mode, before edits on anything multi-step, and correct the plan instead of the diff."},
    {"id": "context_management", "why": "Long threads lose early details; a handoff or a guided compaction keeps the rules that matter in view.", "counts": "“write a handoff”, “when you compact, keep the failing tests”, “start a fresh session”, “checkpoint”", "label": "Hand off or compact before the thread drifts", "level": "session", "area": "steering",
     "sources": ["anth-cc-best-practices", "cc-costs", "anth-context-eng"],
     "nudge": "Manage context on long sessions: say what a compaction must keep, start fresh sessions with a handoff, and checkpoint state."},
    {"id": "long_runs", "why": "A clear finish line lets the agent work unattended and stop at a point you can check.", "counts": "“run this overnight”, “work autonomously”, “keep going until done”, “while I'm away”, “/goal”, “/loop”", "label": "Hand off long runs with a finish line", "level": "session", "area": "steering",
     "sources": ["anth-cc-best-practices", "anth-effective-agents"],
     "nudge": "For work with a clear finish line, hand it off as a goal or loop run with a stopping condition, then verify what came back."},
    {"id": "delegation", "why": "Side work in subagents keeps the main thread focused on decisions instead of search output.", "counts": "“use subagents”, “in parallel”, “delegate this”, “fan out”, “a worktree each”", "label": "Split work across agents", "level": "session", "area": "orchestration",
     "sources": ["cc-subagents", "anth-multi-agent"],
     "nudge": "Split research, implementation, and review into subagents with structured reports, so the main thread keeps the decisions."},
    {"id": "model_choice", "why": "Matching the model to the job keeps hard work on a strong model and cheap work fast.", "counts": "“use haiku for this”, “switch to opus”, “use a cheaper model”, “reasoning effort”", "label": "Pick the model on purpose", "level": "session", "area": "orchestration",
     "sources": ["anth-choose-model", "oai-codex-bp", "oai-codex-prompting"],
     "nudge": "Pick the model and effort for the job on purpose: small fast models for extraction and scouting, the strongest for hard design."},
    {"id": "teach_once", "why": "A rule written down once stops the same correction from costing you a message in every new session.", "counts": "“add this to AGENTS.md”, “turn this into a skill”, “write a lint rule”, “remember this going forward”", "label": "Turn repeat corrections into rules", "level": "session", "area": "setup",
     "sources": ["cc-memory", "oai-codex-bp"],
     "nudge": "When you correct the same thing twice, encode it once: a line in AGENTS.md or CLAUDE.md, a skill, a lint, or a hook."},
    {"id": "guardrails", "why": "A hook or permission blocks a forbidden action every time; a reminder in a prompt only asks.", "counts": "“a pre-commit hook that blocks it”, “a stop hook”, “permission mode”, “allowed-tools”, “auto-approve”", "label": "Enforce hard rules with hooks", "level": "session", "area": "setup",
     "sources": ["anth-cc-best-practices", "cc-memory"],
     "nudge": "Enforce rules that must never be skipped with hooks and permission modes instead of reminders in the prompt."},
    {"id": "automation", "why": "Work that runs on a schedule happens without you remembering to start it.", "counts": "“run it headless”, “a cron job”, “a scheduled run”, “a nightly check”, “set up a GitHub action”", "label": "Put repeat work on a schedule", "level": "session", "area": "automation",
     "sources": ["anth-cc-best-practices", "cc-scheduled", "oai-codex-bp"],
     "nudge": "Move repeat work to scheduled, headless, or CI runs (code review, triage, nightly checks) instead of starting it by hand."},
    {"id": "share_setup", "why": "A setup you share stops teammates from rebuilding it and keeps everyone working the same way.", "counts": "“package this as a plugin”, “share it with my team”, “publish the skill”, “open source it”", "label": "Share your setup with the team", "level": "session", "area": "sharing",
     "sources": ["cc-plugins", "skj-agent-skills"],
     "nudge": "Package a setup you trust (skills, hooks, instructions) as a plugin or repo the team can install."},
]
AMBITION_DIMENSIONS = [d["id"] for d in SCORECARD if d["area"] == "ambition"]
LATE_CONSTRAINT_SIGNALS = ("scope_control", "outside_judge", "evidence_demand", "shipping_authority")
OPENER_MIN_WORDS = 8
SHORT_REFERENCE = re.compile(r"\b(this|that|it|same thing|keep going|continue)\b", re.I)
CAPS_TOKEN = re.compile(r"\b[A-Z]{2,}\b")

PASTED_LINE = re.compile(
    r"^\s*(import |export |const |let |var |function |return |class |def |if \(|for \(|[{}\])]|</?[A-Za-z]|at \S+ \("
    r"|\[\d{4}-\d\d-\d\d|\$ |> |\||#{1,6} |```|\d+\s*[|:]\s|[+-]{3} |@@ )"
    r"|[;{}]\s*$|=>|\*\*|[\u2500-\u257f]|^\s*[\w-]+:\s*['\"]"
)


FENCED_CODE = re.compile(r"```.*?(```|$)", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\[\$?([^\]]+)\]\([^)]*\)")
SKILL_REF = re.compile(r"\[\$[^\]]+\]")
URL_OR_PATH = re.compile(r"https?://\S+|(?:~|\.{1,2})?/[\w.@-]+(?:/[\w.@-]+)+")
SYMBOL = re.compile(r"[^\w\s]|_")
WORD = re.compile(r"\b[A-Za-z]{2,}\b")


def prose(text):
    """Keep only what the user typed: drop code, logs, links, paths, and pasted agent markdown."""
    text = FENCED_CODE.sub(" ", text)
    text = INLINE_CODE.sub(" ", text)
    text = LINK.sub(r"\1", text)
    text = SKILL_REF.sub(" ", text)
    text = URL_OR_PATH.sub(" ", text)
    return "\n".join(line for line in text.splitlines() if not (
        PASTED_LINE.search(line) or (len(line) > 20 and len(SYMBOL.findall(line)) / len(line) > 0.2))).strip()


def detect(text, emphasis_words):
    return detect_prose(prose(text), emphasis_words)


def detect_prose(body, emphasis_words):
    found = plain_signals(body)
    if emphasized(CAPS_TOKEN.findall(body), emphasis_words):
        found.add("caps_emphasis")
    return found


def plain_signals(body):
    """Every signal except caps_emphasis, which also depends on the stored vocabulary."""
    words = len(body.split())
    found = {name for name, pattern in SIGNAL_RE.items() if pattern.search(body)}
    if words <= 5:
        found.add("five_words_or_fewer")
    if words <= 25 and SHORT_REFERENCE.search(body):
        found.add("short_context_dependent")
    return found


def emphasized(caps, emphasis_words):
    return any(token.lower() in emphasis_words for token in caps)


def annotate_texts(texts):
    """Prose length, signals without caps_emphasis, and all-caps words per text, plus lowercase word counts for the stored vocabulary."""
    fields, lower = [], collections.Counter()
    for text in texts:
        body = prose(text)
        words = WORD.findall(body)
        lower.update(word for word in words if word.islower())
        fields.append((len(body.split()), sorted(plain_signals(body)), [word for word in words if word.isupper()]))
    return fields, lower


def annotate_rows(rows, pool):
    """Cache each human turn's prose length, signals, and all-caps words so queries skip prose extraction."""
    chunks = [rows[i:i + 400] for i in range(0, len(rows), 400)]
    lower = collections.Counter()
    for chunk, (fields, counts) in zip(chunks, pmap(pool, annotate_texts, [[r["text"] for r in c] for c in chunks])):
        lower.update(counts)
        for row, (prose_words, signals, caps) in zip(chunk, fields):
            row["prose_words"], row["signals"] = prose_words, signals
            if caps:
                row["caps"] = caps
            else:
                row.pop("caps", None)
    return lower


def emphasize(row, emphasis_words):
    signals = [s for s in row["signals"] if s != "caps_emphasis"]
    row["signals"] = sorted([*signals, "caps_emphasis"]) if emphasized(row.get("caps", ()), emphasis_words) else signals


def pmap(pool, function, chunks):
    return pool.map(function, chunks) if pool else map(function, chunks)


RULES_HASH = hashlib.sha256(json.dumps(
    [SIGNALS, PASTED_LINE.pattern, SHORT_REFERENCE.pattern, CAPS_TOKEN.pattern,
     *(p.pattern for p in (FENCED_CODE, INLINE_CODE, LINK, SKILL_REF, URL_OR_PATH, SYMBOL, WORD)),
     *(inspect.getsource(f) for f in (prose, detect_prose, plain_signals, emphasized, annotate_texts, emphasize))]
).encode()).hexdigest()[:16]


def load_vocab():
    db = connect()
    return set(meta_value(db, "vocab", [])) if db else set()


def text_from_blocks(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        block["text"] for block in content
        if isinstance(block, dict) and block.get("type") in {"input_text", "text"} and isinstance(block.get("text"), str)
    )


# Credentials are replaced before anything reaches the corpus, so the cache never stores a pasted secret.
SECRET_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)),
    ("api_key", re.compile(r"\bsk-(?:ant-|or-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("aws_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("google_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("assignment", re.compile(r"(?i)\b((?:api[_-]?key|secret|token|password|passwd|client[_-]?secret)\b\s*[:=]\s*)['\"]?[^\s'\"]{8,}['\"]?")),
]
REDACTIONS = [(pattern, r"\1[REDACTED:assignment]" if kind == "assignment" else f"[REDACTED:{kind}]")
              for kind, pattern in SECRET_PATTERNS]
SKILL_TAG = re.compile(r'<skill name="([^"]+)".*?</skill>', re.S)
COMMAND_TAG = re.compile(r"<command-name>/?([^<]+)</command-name>")
STRIP_TAG = re.compile(rf"<({'|'.join(map(re.escape, STRIP_TAGS))})\b.*?</\1>", re.S)
BLANK_LINES = re.compile(r"\n{3,}")


def redact(text):
    """Replace known credential shapes until nothing changes. One pass can stop at a quote inside a wrapped value,
    as in token=Some(\\"...\\"), and leave the secret after the marker; the next pass catches that tail."""
    while True:
        before = text
        for pattern, replacement in REDACTIONS:
            text = pattern.sub(replacement, text)
        if text == before:
            return text


def unwrap(raw):
    """The user's own words from a raw turn. Runs once at read time, because a stored turn can quote the marker."""
    return raw.split("## My request for Codex:", 1)[1] if "## My request for Codex:" in raw else raw


def clean(text):
    """Redact and strip injected tags. Cleaning a cleaned text changes nothing, so stored turns can be re-cleaned."""
    text = redact(text.replace("\x00", " "))
    if "<" in text:
        text = SKILL_TAG.sub(r"[$\1]", text)
        text = COMMAND_TAG.sub(r"[$\1]", text)
        text = STRIP_TAG.sub(" ", text)
    return BLANK_LINES.sub("\n\n", text).strip()


def clean_texts(texts):
    return [clean(text) for text in texts]


def admissible(text):
    return len(text) >= 2 and not text.lower().startswith(BLOCKED_STARTS) and text.lower() not in SLASH_NOISE


def to_iso(value):
    if isinstance(value, (int, float)):
        if value > 10_000_000_000:
            value /= 1000
        return datetime.datetime.fromtimestamp(value, datetime.UTC).isoformat()
    return value


def iter_jsonl(path, needles=()):
    """Parse each JSON line. With needles, a line holding none of them is skipped before it is decoded."""
    with path.open("rb") as handle:
        for line in handle:
            if line.startswith(b"{") and (not needles or any(needle in line for needle in needles)):
                with contextlib.suppress(json.JSONDecodeError):
                    yield json.loads(line.decode("utf-8", "replace"))


def mapping(value):
    """A JSON object, or an empty one when a record holds null, a list, or a scalar where an object belongs."""
    return value if isinstance(value, dict) else {}


def codex_files():
    return [p for root in (HOME / ".codex/sessions", HOME / ".codex/archived_sessions") if root.exists()
            for p in root.rglob("rollout-*.jsonl")]


def read_codex(path):
    session, cwd, spawned, turns = path.stem, "", False, []
    for item in iter_jsonl(path, (b'"session_meta"', b'"role":"user"')):
        payload = mapping(item.get("payload"))
        if item.get("type") == "session_meta":
            session, cwd = payload.get("id", session), payload.get("cwd", cwd)
            spawned = isinstance(payload.get("source"), dict) and "subagent" in payload["source"]
        elif item.get("type") == "response_item" and payload.get("type") == "message" and payload.get("role") == "user":
            turns.append(("codex", session, item.get("timestamp"), cwd, text_from_blocks(payload.get("content")), spawned))
    return turns


def claude_files():
    root = HOME / ".claude/projects"
    return list(root.rglob("*.jsonl")) if root.exists() else []


def read_claude(path):
    turns = []
    for item in iter_jsonl(path):
        message = mapping(item.get("message"))
        if item.get("type") == "user" and not item.get("isMeta") and message.get("role") == "user":
            turns.append(("claude", item.get("sessionId", path.stem), item.get("timestamp"), item.get("cwd", ""),
                          text_from_blocks(message.get("content")), bool(item.get("isSidechain"))))
    return turns


def pi_files():
    root = HOME / ".pi/agent/sessions"
    return [p for d in root.iterdir() if d.is_dir() for p in d.glob("*.jsonl")] if root.exists() else []


def read_pi(path):
    session, cwd, turns = path.stem, "", []
    for item in iter_jsonl(path, (b'"type":"session"', b'"role":"user"')):
        if item.get("type") == "session":
            session, cwd = item.get("id", session), item.get("cwd", cwd)
        elif item.get("type") == "message" and mapping(item.get("message")).get("role") == "user":
            turns.append(("pi", session, item.get("timestamp"), cwd, text_from_blocks(item["message"].get("content")), False))
    return turns


def opencode_files():
    return list((OPENCODE / "message").rglob("*.json")) if (OPENCODE / "message").exists() else []


def read_opencode(path):
    try:
        message = mapping(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):  # ValueError covers bad JSON and bytes that aren't UTF-8
        return []
    if message.get("role") != "user":
        return []
    texts = []
    for part_path in (OPENCODE / "part" / str(message.get("id"))).glob("*.json"):
        try:
            part = mapping(json.loads(part_path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            texts.append(part["text"])
    return [("opencode", message.get("sessionID"), mapping(message.get("time")).get("created"), "", "\n".join(texts), False)]


SOURCES = (("codex", codex_files, read_codex), ("claude", claude_files, read_claude), ("pi", pi_files, read_pi),
           ("opencode_message", opencode_files, read_opencode))
CURSOR_DBS = (HOME / "Library/Application Support/Cursor/User/globalStorage/state.vscdb",
              HOME / ".config/Cursor/User/globalStorage/state.vscdb",
              HOME / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb")
BUBBLE_TYPE = re.compile(rb'\{"_v":\d+,"type":(\d+)[,}]')
BUBBLE_BYTES = 50_000


def bubble_range(composer_id):
    return f"bubbleId:{composer_id}:", f"bubbleId:{composer_id};"


def cursor_composers(db):
    """Non-subagent composers as id -> (createdAt, workspace path, change signature)."""
    composers = {}
    with contextlib.closing(sqlite3.connect(f"file:{db}?mode=ro", uri=True)) as connection:
        for composer_id, created_at, updated_at, is_subagent, value in connection.execute(
                "select composerId, createdAt, lastUpdatedAt, isSubagent, value from composerHeaders"):
            if is_subagent:
                continue
            try:
                header = json.loads(value)
            except (TypeError, json.JSONDecodeError):
                header = {}
            # lastUpdatedAt is often null, so the bubble count and newest rowid (a REPLACE gets a new one) also mark a change.
            bubbles, newest = connection.execute("select count(*), max(rowid) from cursorDiskKV where key >= ? and key < ?",
                                                 bubble_range(composer_id)).fetchone()
            composers[composer_id] = (created_at, header.get("workspaceIdentifier", {}).get("uri", {}).get("fsPath", ""),
                                      [updated_at, bubbles, newest])
    return composers


def epoch_ms(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(value if value > 10_000_000_000 else value * 1000)
    if not isinstance(value, str):
        return None
    try:
        moment = datetime.datetime.fromisoformat(value)
    except ValueError:
        return None
    return round((moment if moment.tzinfo else moment.replace(tzinfo=datetime.UTC)).timestamp() * 1000)


def cursor_iso(ms):
    if ms is None:
        return None
    moment = datetime.datetime.fromtimestamp(ms // 1000, datetime.UTC) + datetime.timedelta(milliseconds=ms % 1000)
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def turn_times(headers, bubbles, created_at):
    """Epoch ms per user bubble id: its own createdAt, else its header's, else a stand-in that keeps header order."""
    times, previous = {}, None
    for position, header in enumerate(h for h in headers if isinstance(h, dict) and h.get("type") == 1):
        bubble_id = header.get("bubbleId")
        moment = epoch_ms(bubbles.get(bubble_id, {}).get("createdAt")) or epoch_ms(header.get("createdAt"))
        if previous is not None:
            # Forked conversations copy earlier bubbles within the same millisecond, sometimes out of order.
            moment = max(moment or 0, previous + 1)
        elif moment is None and created_at is not None:
            moment = created_at + position
        times[bubble_id] = previous = moment
    for bubble_id, bubble in bubbles.items():
        if bubble_id not in times:
            times[bubble_id] = epoch_ms(bubble.get("createdAt")) or created_at
    return times


def read_cursor(task):
    """User bubbles of the given composers as (rowid, row), so callers can restore table order."""
    db, composers = task
    found = []
    with contextlib.closing(sqlite3.connect(f"file:{db}?mode=ro", uri=True)) as connection:
        connection.text_factory = bytes
        for composer_id, created_at, cwd in composers:
            bubbles = {}
            for rowid, key, value in connection.execute("select rowid, key, value from cursorDiskKV where key >= ? and key < ?",
                                                        bubble_range(composer_id)):
                try:
                    kind = BUBBLE_TYPE.match(value)
                    if kind and kind[1] != b"1":
                        continue
                    bubble = json.loads(value)
                except (TypeError, ValueError):
                    continue
                if isinstance(bubble, dict) and bubble.get("type") == 1:
                    bubbles[key.decode().rsplit(":", 1)[1]] = (rowid, bubble)
            data = connection.execute("select value from cursorDiskKV where key = ?", (f"composerData:{composer_id}",)).fetchone()
            try:
                headers = json.loads(data[0]).get("fullConversationHeadersOnly") or []
            except (TypeError, ValueError, AttributeError):
                headers = []
            times = turn_times(headers, {bid: bubble for bid, (_, bubble) in bubbles.items()}, epoch_ms(created_at))
            for bubble_id, (rowid, bubble) in bubbles.items():
                turn = ("cursor", composer_id, cursor_iso(times[bubble_id]), cwd, bubble.get("text", ""), False)
                found += [(rowid, row) for row in admitted([turn])]
    return found


def admitted(turns):
    rows = []
    for source, session, timestamp, cwd, raw, spawned in turns:
        if isinstance(timestamp, bool) or not isinstance(timestamp, (str, int, float)):
            timestamp = None
        text = clean(unwrap(raw))
        if admissible(text):
            rows.append({"source": source, "session": session or "unknown", "timestamp": to_iso(timestamp), "cwd": cwd or "",
                         "words": len(text.split()), "spawned": spawned, "text": text})
    return rows


def parse_cursor(task):
    """Cursor's turns for one group of conversations, or None when its database can't be read, as parse_file does for files."""
    try:
        return read_cursor(task)
    except Exception:
        return None


def parse_file(task):
    """The file's admitted turns, or None when it can't be parsed, so one malformed file never stops a mine."""
    read, path = task
    try:
        return admitted(read(path))
    except Exception:
        return None


def signature(*paths):
    return [value for path in paths if path.exists() for value in (path.stat().st_size, path.stat().st_mtime_ns)]


def rank(row):
    """Which copy of a repeated text to keep, independent of the order sources are read in."""
    return bool(row.get("spawned")), not row.get("timestamp"), row.get("timestamp") or "", row["session"]


def row_key(row):
    """Long texts are one turn per tool. A short text is one turn per moment, and an undated one is one per session,
    so forked conversations that copy a turn with its timestamp still store it once."""
    digest = hashlib.sha256(row["text"].encode()).hexdigest()
    if len(row["text"]) > 100:
        return row["source"], digest
    return (row["source"], row["timestamp"], digest) if row["timestamp"] else (row["source"], row["session"], digest)


def user_harness(patterns):
    """Regexes from the config's harness_patterns: prompts a user's own tools write that no shared rule can know.

    A pattern that doesn't compile, or that matches empty text and so every prompt, is skipped with a warning.
    """
    usable = []
    for pattern in patterns:
        try:
            if not re.compile(pattern, re.I).search(""):
                usable.append(pattern)
                continue
            problem = "it matches empty text, so it would match every prompt"
        except (re.error, TypeError) as error:
            problem = str(error)
        if __name__ != "__mp_main__":  # worker processes re-import this file; only the command itself warns
            print(f"skipping harness pattern {pattern!r} in {CONFIG}: {problem}", file=sys.stderr)
    return re.compile("|".join(f"(?:{p})" for p in usable), re.I) if usable else None


USER_HARNESS = user_harness((read_config()).get("harness_patterns") or [])


def classify(rows):
    """Tag each row human, subagent, or harness so analysis reflects only what the user typed."""
    per_session = collections.Counter((r["source"], r["session"]) for r in rows)
    for row in rows:
        if row.get("spawned"):
            row["origin"] = "subagent"
        elif (HARNESS_CWD.search(row["cwd"]) or HARNESS_TEXT.search(row["text"])
              or (USER_HARNESS and USER_HARNESS.search(row["text"]))
              or (per_session[(row["source"], row["session"])] == 1 and TICKET_BRIEF.search(row["text"]))):
            row["origin"] = "harness"
        else:
            row["origin"] = "human"


def read_corpus(path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            with contextlib.suppress(json.JSONDecodeError):
                yield json.loads(line)


SCHEMA = """
create table if not exists turns (
    id integer primary key,
    key blob not null unique,  -- 16 bytes of sha256 over row_key()
    source text not null,
    session text not null,
    timestamp text,
    cwd text not null,
    words integer not null,
    spawned integer,  -- null for rows imported from older corpora, which never recorded it
    origin text not null,
    prose_words integer,
    caps text,
    text text,
    packed blob
);
create index if not exists turns_by_time on turns(timestamp);
create index if not exists turns_by_session on turns(source, session);
create table if not exists turn_signals (turn_id integer not null, signal text not null, primary key (turn_id, signal)) without rowid;
create table if not exists sources (path text primary key, signature text not null);
create table if not exists composers (id text primary key, signature text not null);
create table if not exists meta (key text primary key, value text not null);
"""
COLUMNS = ("source", "session", "timestamp", "cwd", "words", "spawned", "origin", "prose_words", "caps", "text", "packed")


def create(path):
    db = sqlite3.connect(path)
    db.execute("pragma journal_mode=wal")
    db.executescript(SCHEMA)
    return db


def connect():
    """Open corpus.db, importing an older install's files the first time. None when there is no corpus yet."""
    if not DB.exists() and LEGACY_CORPUS.exists():
        migrate()
    if not DB.exists():
        return None
    db = sqlite3.connect(DB)
    db.create_function("has_text", 2, lambda haystack, needle: needle in haystack.lower(), deterministic=True)
    return db


def meta_value(db, key, default=None):
    found = db.execute("select value from meta where key = ?", (key,)).fetchone()
    return json.loads(found[0]) if found else default


def write_meta(db, **values):
    db.executemany("insert or replace into meta values (?, ?)", [(key, json.dumps(value)) for key, value in values.items()])


def pack(text):
    """(text, None) when compressing wouldn't save space, else (None, compressed). No query reads text in SQL."""
    data = text.encode()
    packed = zlib.compress(data)
    return (None, packed) if len(packed) < len(data) else (text, None)


def key_text(row):
    return hashlib.sha256(json.dumps(row_key(row)).encode()).digest()[:16]


def redactions(texts):
    return collections.Counter(kind for text in texts if "[REDACTED:" in text for kind in re.findall(r"\[REDACTED:(\w+)\]", text))


class Turn(dict):
    """A stored turn. Compressed text is decoded on first read, because most queries never look at it."""
    __slots__ = ("packed",)

    def __missing__(self, key):
        if key != "text" or self.packed is None:
            raise KeyError(key)
        self["text"], self.packed = zlib.decompress(self.packed).decode(), None
        return self["text"]


def rows_from(db, where="1", params=()):
    """Turns as the dicts the analysis code reads, oldest first."""
    query = (f"select {', '.join(COLUMNS)}, (select group_concat(signal, ' ') from turn_signals where turn_id = turns.id) "
             f"from turns where {where} order by timestamp, id")
    for source, session, timestamp, cwd, words, spawned, origin, prose_words, caps, text, packed, signals in db.execute(query, params):
        row = Turn(source=source, session=session, timestamp=timestamp, cwd=cwd, words=words)
        row.packed = packed
        if spawned is not None:
            row["spawned"] = bool(spawned)
        if packed is None:
            row["text"] = text
        row["origin"] = origin
        if prose_words is not None:
            row["prose_words"], row["signals"] = prose_words, sorted(signals.split()) if signals else []
        if caps:
            row["caps"] = caps.split()
        yield row


def set_signals(db, turn_id, signals):
    db.execute("delete from turn_signals where turn_id = ?", (turn_id,))
    db.executemany("insert into turn_signals values (?, ?)", [(turn_id, signal) for signal in signals])


def insert(db, rows):
    for row in rows:
        text, packed = pack(row["text"])
        caps = " ".join(row.get("caps", ())) or None
        cursor = db.execute(f"insert into turns (key, {', '.join(COLUMNS)}) values ({', '.join('?' * (len(COLUMNS) + 1))})",
                            (key_text(row), row["source"], row["session"], row.get("timestamp"), row["cwd"], row["words"],
                             row.get("spawned"), row["origin"], row.get("prose_words"), caps, text, packed))
        db.executemany("insert into turn_signals values (?, ?)", [(cursor.lastrowid, s) for s in row.get("signals", ())])


def migrate():
    """Import an older install's corpus.jsonl and side files once, then rename each with a .migrated suffix."""
    manifest = json.loads(LEGACY_MANIFEST.read_text()) if LEGACY_MANIFEST.exists() else {}
    building = DB.with_name(DB.name + ".tmp")
    building.unlink(missing_ok=True)
    db = create(building)
    with db:
        rows = list(read_corpus(LEGACY_CORPUS))
        insert(db, rows)
        db.executemany("insert into sources values (?, ?)", [(p, json.dumps(s)) for p, s in manifest.get("files", {}).items()])
        db.executemany("insert into composers values (?, ?)", [(c, json.dumps(s)) for c, s in manifest.get("composers", {}).items()])
        meta = {"redacted": redactions(row["text"] for row in rows)}
        # The old manifest only described the corpus file it was written with; otherwise the next mine rebuilds.
        if manifest.get("corpus") == signature(LEGACY_CORPUS):
            meta.update({key: manifest[key] for key in ("clean", "rules", "upper", "lower") if key in manifest})
        if LEGACY_VOCAB.exists():
            meta["vocab"] = json.loads(LEGACY_VOCAB.read_text())
        if LEGACY_COVERAGE.exists():
            meta["coverage"] = json.loads(LEGACY_COVERAGE.read_text())
        write_meta(db, **meta)
    db.close()
    building.replace(DB)
    for path in (LEGACY_CORPUS, LEGACY_MANIFEST, LEGACY_VOCAB, LEGACY_COVERAGE):
        if path.exists():
            path.rename(path.with_name(path.name + ".migrated"))
    print(f"Imported {len(rows)} turns from {LEGACY_CORPUS} into {DB}; the old files now end in .migrated.", file=sys.stderr)


def readmit(rows, pool):
    """Re-clean stored rows under the current rules and drop any that no longer qualify."""
    texts = [row["text"] for row in rows]
    chunks = [texts[i:i + 1000] for i in range(0, len(texts), 1000)]
    kept = []
    for row, text in zip(rows, (text for out in pmap(pool, clean_texts, chunks) for text in out)):
        if admissible(text):
            row.update(text=text, words=len(text.split()))
            row.setdefault("cwd", "")
            kept.append(row)
    return kept


def run_jobs(jobs, pool):
    """Run (weight, function, argument) jobs, heaviest first, and return results in job order."""
    if not pool:
        return [function(argument) for _, function, argument in jobs]
    futures = {i: pool.submit(jobs[i][1], jobs[i][2]) for i in sorted(range(len(jobs)), key=lambda i: -jobs[i][0])}
    return [futures[i].result() for i in range(len(jobs))]


CLEAN_HASH = hashlib.sha256(json.dumps(
    [BLOCKED_STARTS, STRIP_TAGS, sorted(SLASH_NOISE), [pattern.pattern for _, pattern in SECRET_PATTERNS],
     *(p.pattern for p in (HARNESS_CWD, HARNESS_TEXT, TICKET_BRIEF, SKILL_TAG, COMMAND_TAG, STRIP_TAG, BLANK_LINES)),
     BUBBLE_TYPE.pattern.decode(), USER_HARNESS.pattern if USER_HARNESS else "",
     *(inspect.getsource(f) for f in (redact, unwrap, clean, admissible, to_iso, iter_jsonl, text_from_blocks, read_codex, read_claude,
                                      read_pi, read_opencode, epoch_ms, cursor_iso, turn_times, read_cursor, admitted, rank,
                                      row_key, classify, pack, key_text))]
).encode()).hexdigest()[:16]


def mine(args):
    DATA.mkdir(parents=True, exist_ok=True)
    db = connect() or create(DB)
    # Hold the write lock from the first read, so a second mine waits for this one and then sees what it wrote.
    db.execute("pragma busy_timeout = 3600000")
    db.execute("begin immediate")
    db.execute("drop index if exists signals_by_name")  # turn_signals is small enough to scan, so the index only cost space
    meta = {key: json.loads(value) for key, value in db.execute("select key, value from meta")}
    incremental = not args.full and meta.get("clean") == CLEAN_HASH and meta.get("rules") == RULES_HASH
    known_files = dict(db.execute("select path, signature from sources")) if incremental else {}
    known_composers = dict(db.execute("select id, signature from composers")) if incremental else {}
    coverage, files, jobs = {}, {}, []
    chatgpt = HOME / "Library/Application Support/com.openai.chat"
    coverage["chatgpt_encrypted_files_unread"] = sum(1 for _ in chatgpt.rglob("*.data")) if chatgpt.exists() else 0
    for name, list_files, read in SOURCES:
        paths = list_files()
        coverage[f"{name}_files"] = len(paths)
        for path in paths:
            files[str(path)] = signature(path, *([OPENCODE / "part" / path.stem] if read is read_opencode else []))
            if known_files.get(str(path)) != json.dumps(files[str(path)]):
                jobs.append((files[str(path)][0], parse_file, (read, path)))
    file_jobs = len(jobs)
    cursor_db = next((path for path in CURSOR_DBS if path.exists()), None)
    try:
        composers, cursor_failed = (cursor_composers(cursor_db) if cursor_db else {}), 0
    except Exception:
        composers, cursor_failed = {}, 1
    coverage["cursor_composers"] = len(composers)
    changed = sorted(((cid, created, cwd, sig) for cid, (created, cwd, sig) in composers.items()
                      if known_composers.get(cid) != json.dumps(sig)), key=lambda c: -c[3][1])
    work = sum(weight for weight, _, _ in jobs) + BUBBLE_BYTES * sum(c[3][1] for c in changed)
    workers = os.cpu_count() or 1
    # Starting worker processes costs more than it saves on a small incremental run.
    with (concurrent.futures.ProcessPoolExecutor(workers) if not incremental or work > 256_000_000
          else contextlib.nullcontext()) as pool, db:
        groups = min(len(changed), 4 * workers if pool else 1)
        for i in range(groups):
            group = changed[i::groups]
            jobs.append((BUBBLE_BYTES * sum(c[3][1] for c in group), parse_cursor, (cursor_db, [c[:3] for c in group])))
        results = run_jobs(jobs, pool)
        failed = [path for (_, _, (_, path)), rows in zip(jobs[:file_jobs], results[:file_jobs]) if rows is None]
        for (_, _, (_, group)), pairs in zip(jobs[file_jobs:], results[file_jobs:]):
            if pairs is None:
                cursor_failed += 1
                for composer_id, *_ in group:
                    composers.pop(composer_id, None)
        coverage["files_failed"] = len(failed) + cursor_failed
        # A failure stores no signature, so the next mine tries it again and counts it again.
        for path in failed:
            files.pop(str(path))
        parsed = [row for rows in results[:file_jobs] for row in rows or ()]
        parsed += [row for _, row in sorted((pair for pairs in results[file_jobs:] for pair in pairs or ()), key=lambda p: p[0])]

        fresh = {}
        for row in parsed:
            key = key_text(row)
            if key not in fresh or rank(row) < rank(fresh[key]):
                fresh[key] = row
        live_turns = {(r["source"], r["session"], r["timestamp"]) for r in fresh.values()}
        # A Cursor turn's time can move when its conversation is read again, so a composer that yields rows replaces its stored ones.
        live_composers = {(row["source"], row["session"]) for row in parsed if row["source"] == "cursor"}
        if incremental:
            # Only these fields decide whether a stored turn survives; text is read later for the few turns that change.
            previous = [(key, {"id": turn_id, "source": source, "session": session, "timestamp": timestamp,
                               "spawned": spawned, "origin": origin})
                        for key, turn_id, source, session, timestamp, spawned, origin in
                        db.execute("select key, id, source, session, timestamp, spawned, origin from turns")]
        else:
            previous = [(key_text(row), row) for row in readmit(list(rows_from(db)), pool)]
        imported = readmit([row for path in args.import_paths for row in read_corpus(Path(path))], pool)
        for key, row in previous + [(key_text(row), row) for row in imported]:
            if (row["source"], row["session"]) not in live_composers and (
                    row["source"], row["session"], row.get("timestamp")) not in live_turns and (
                    key not in fresh or rank(row) < rank(fresh[key])):
                fresh[key] = row

        if incremental:
            upper, lower, redacted = update_turns(db, fresh, previous, meta, pool)
        else:
            upper, lower, redacted = rewrite_turns(db, fresh, pool)
        vocab = sorted(word for word, count in upper.items() if lower[word] > count)
        emphasize_all(db, set(vocab))
        db.execute("delete from sources")
        db.executemany("insert into sources values (?, ?)", [(path, json.dumps(sig)) for path, sig in files.items()])
        db.execute("delete from composers")
        db.executemany("insert into composers values (?, ?)", [(cid, json.dumps(sig)) for cid, (_, _, sig) in composers.items()])
        coverage["corpus_turns"] = db.execute("select count(*) from turns").fetchone()[0]
        coverage["redacted"] = redacted
        coverage["rules"] = RULES_HASH
        coverage["by_origin"] = collections.Counter(origin for (origin,) in db.execute("select origin from turns order by timestamp, id"))
        coverage["mode"] = "incremental" if incremental else "full"
        coverage["files_parsed"], coverage["files_skipped"] = file_jobs, len(files) - file_jobs
        coverage["composers_parsed"], coverage["composers_skipped"] = len(changed), len(composers) - len(changed)
        coverage["mined_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        write_meta(db, clean=CLEAN_HASH, rules=RULES_HASH, upper=upper, lower=lower, vocab=vocab, redacted=redacted,
                   coverage=coverage)
    db.execute("pragma wal_checkpoint(truncate)")
    if not incremental:
        db.execute("vacuum")  # a full rewrite frees most pages; hand them back to the disk
    db.close()
    print(json.dumps({"corpus": str(DB), **coverage}, indent=2))


def rewrite_turns(db, fresh, pool):
    """Replace every stored turn with the merged set, annotating each human turn from scratch."""
    rows = sorted(fresh.values(), key=lambda r: r.get("timestamp") or "")
    classify(rows)
    human = [row for row in rows if row["origin"] == "human"]
    lower = annotate_rows(human, pool)
    upper = collections.Counter(word.lower() for row in human for word in row.get("caps", ()))
    for row in rows:
        if row["origin"] != "human":
            for field in ("prose_words", "signals", "caps"):
                row.pop(field, None)
    db.execute("delete from turn_signals")
    db.execute("delete from turns")
    insert(db, rows)
    return upper, lower, redactions(row["text"] for row in rows)


def update_turns(db, fresh, previous, meta, pool):
    """Apply an incremental merge: drop superseded turns, write new ones, and reclassify the sessions they touch.

    The vocab counters always equal the sum over human turns, so they move only for turns that start or stop being human.
    """
    stored = {id(row) for _, row in previous}
    kept = {id(row) for row in fresh.values()}
    dropped = {key: row for key, row in previous if id(row) not in kept}
    new = sorted(((key, row) for key, row in fresh.items() if id(row) not in stored), key=lambda kr: kr[1].get("timestamp") or "")
    before = {row["id"]: (caps, text if packed is None else zlib.decompress(packed).decode()) for row in dropped.values()
              for caps, text, packed in db.execute("select caps, text, packed from turns where id = ?", (row["id"],))}
    deleted = [row for key, row in dropped.items() if key not in fresh]
    reused = {key: dropped[key] for key, _ in new if key in dropped}

    neighbors, gone = [], {row["id"] for row in dropped.values()}
    for source, session in {(row["source"], row["session"]) for row in dropped.values()} | {(r["source"], r["session"]) for _, r in new}:
        for turn_id, cwd, spawned, origin, caps, text, packed, words in db.execute(
                "select id, cwd, spawned, origin, caps, text, packed, words from turns where source = ? and session = ?",
                (source, session)):
            if turn_id not in gone:
                neighbors.append({"id": turn_id, "source": source, "session": session, "cwd": cwd, "spawned": spawned,
                                  "words": words, "text": text if packed is None else zlib.decompress(packed).decode(),
                                  "was": origin, "old_caps": caps})
    for key, row in new:
        if key in reused:
            row.update(id=reused[key]["id"], was=reused[key]["origin"], old_caps=before[reused[key]["id"]][0])
        else:
            row.update(id=None, was=None, old_caps=None)
    group = [row for _, row in new] + neighbors
    classify(group)

    upper, lower = collections.Counter(meta["upper"]), collections.Counter(meta["lower"])
    entering = [row for row in group if row["origin"] == "human" and row["was"] != "human"]
    leaving = [row for row in group if row["was"] == "human" and row["origin"] != "human"]
    leaving_caps = [row["old_caps"] for row in leaving]
    leaving_texts = [row["text"] for row in leaving]
    for row in deleted:
        if row["origin"] == "human":
            leaving_caps.append(before[row["id"]][0])
            leaving_texts.append(before[row["id"]][1])
    lower += annotate_rows(entering, pool)
    upper.update(word.lower() for row in entering for word in row.get("caps", ()))
    lower -= annotate_texts(leaving_texts)[1]
    upper -= collections.Counter(word.lower() for caps in leaving_caps if caps for word in caps.split())

    gone_ids = json.dumps([row["id"] for row in deleted])
    db.execute("delete from turn_signals where turn_id in (select value from json_each(?))", (gone_ids,))
    db.execute("delete from turns where id in (select value from json_each(?))", (gone_ids,))
    for row in group:
        if row["origin"] != "human":
            for field in ("prose_words", "signals", "caps"):
                row.pop(field, None)
    insert(db, [row for _, row in new if row["id"] is None])
    for _, row in new:
        if row["id"] is not None:
            text, packed = pack(row["text"])
            db.execute("update turns set session = ?, timestamp = ?, cwd = ?, spawned = ?, origin = ?, text = ?, packed = ? where id = ?",
                       (row["session"], row.get("timestamp"), row["cwd"], row.get("spawned"), row["origin"], text, packed, row["id"]))
    for row in neighbors:
        if row["origin"] != row["was"]:
            text, packed = pack(row["text"])
            db.execute("update turns set origin = ?, text = ?, packed = ? where id = ?", (row["origin"], text, packed, row["id"]))
    for row in entering + leaving:
        if row["id"] is not None:
            db.execute("update turns set prose_words = ?, caps = ? where id = ?",
                       (row.get("prose_words"), " ".join(row.get("caps", ())) or None, row["id"]))
            set_signals(db, row["id"], row.get("signals", ()))
    redacted = collections.Counter(meta.get("redacted", {}))
    redacted += redactions(row["text"] for _, row in new if row["id"] is None)
    redacted -= redactions(before[row["id"]][1] for row in deleted)
    return upper, lower, redacted


def emphasize_all(db, emphasis_words):
    """Mark caps_emphasis on exactly the human turns whose all-caps words are in the current vocab."""
    want = {turn_id for turn_id, caps in db.execute("select id, caps from turns where origin = 'human' and caps is not null")
            if emphasized(caps.split(), emphasis_words)}
    have = {turn_id for (turn_id,) in db.execute("select turn_id from turn_signals where signal = 'caps_emphasis'")}
    db.executemany("delete from turn_signals where turn_id = ? and signal = 'caps_emphasis'", [(i,) for i in have - want])
    db.executemany("insert into turn_signals values (?, 'caps_emphasis')", [(i,) for i in want - have])


def load(args, max_words=None, signal=None):
    """Turns matching the filters, oldest first. Filters, a word cap, and a signal run in SQL."""
    db = connect()
    if not db:
        sys.exit(f"No corpus at {DB}. Run: convo.py mine")
    stale = meta_value(db, "coverage", {}).get("rules") != RULES_HASH
    if stale:
        print("signal rules changed since the last mine; recomputing (slow). Run: convo.py mine", file=sys.stderr)
    if meta_value(db, "clean") != CLEAN_HASH:
        print("turn cleaning rules changed since the last mine; the stored turns are out of date. Run: convo.py mine", file=sys.stderr)
    origins, sources = args.origin.split(","), args.source.split(",") if args.source else []
    clauses, params = [f"origin in ({', '.join('?' * len(origins))})"], [*origins]
    if args.since:
        clauses.append("substr(timestamp, 1, 10) >= ?")
        params.append(args.since)
    if args.until:
        clauses.append("ifnull(substr(timestamp, 1, 10), '') <= ?")
        params.append(args.until)
    if sources:
        clauses.append(f"source in ({', '.join('?' * len(sources))})")
        params += sources
    if args.cwd:
        clauses.append("has_text(cwd, ?)")
        params.append(args.cwd.lower())
    if max_words is not None:
        clauses.append("words <= ?")
        params.append(max_words)
    if signal and not stale:
        clauses.append("id in (select turn_id from turn_signals where signal = ?)")
        params.append(signal)
    rows = list(rows_from(db, " and ".join(clauses), params))
    if stale:
        human = [row for row in rows if row["origin"] == "human"]
        with concurrent.futures.ProcessPoolExecutor(os.cpu_count()) as pool:
            annotate_rows(human, pool)
        emphasis_words = set(meta_value(db, "vocab", []))
        for row in rows:
            if row["origin"] == "human":
                emphasize(row, emphasis_words)
            else:
                row.pop("signals", None)
    return rows


def parse_time(value):
    try:
        return datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def quantile(values, fraction):
    return sorted(values)[min(int(len(values) * fraction), len(values) - 1)] if values else 0


def skill_mentions(text):
    return re.findall(r"\[\$([^\]]+)\]", text) + re.findall(r"^/([a-z][\w:-]+)(?=\s|$)", text)


Z95 = statistics.NormalDist().inv_cdf(0.975)


def wilson(k, n, z=Z95):
    """95% Wilson score interval for k successes in n trials; stays sensible near 0% and with small n."""
    if not n:
        return 0.0, 1.0
    p = k / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def newcombe(k1, n1, k2, n2):
    """95% interval for the difference of two proportions (Newcombe's hybrid score method)."""
    p1, p2 = k1 / n1, k2 / n2
    (l1, u1), (l2, u2) = wilson(k1, n1), wilson(k2, n2)
    return p1 - p2 - math.hypot(p1 - l1, u2 - p2), p1 - p2 + math.hypot(u1 - p1, p2 - l2)


def two_proportion_p(k1, n1, k2, n2):
    pooled = (k1 + k2) / (n1 + n2)
    if pooled in (0, 1):
        return 1.0
    z = abs(k1 / n1 - k2 / n2) / math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    return 2 * (1 - statistics.NormalDist().cdf(z))


def bh_adjust(pvalues):
    """Benjamini-Hochberg adjusted p-values, so testing many habits at once doesn't manufacture changes."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [1.0] * len(pvalues), 1.0
    for rank in range(len(pvalues), 0, -1):
        i = order[rank - 1]
        running = min(running, pvalues[i] * len(pvalues) / rank)
        adjusted[i] = running
    return adjusted


def proportion(k, n):
    low, high = wilson(k, n)
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "low": round(low, 4), "high": round(high, 4)}


def pct(count, total):
    return round(100 * count / total, 1) if total else 0


def stats(args):
    rows = load(args, max_words=LARGE_PASTE_WORDS)
    if not rows:
        sys.exit("No turns match the filters.")
    counts, monthly = collections.Counter(), collections.defaultdict(collections.Counter)
    hours, days, sessions, workspaces = collections.Counter(), collections.Counter(), collections.defaultdict(list), collections.Counter()
    session_signals = collections.defaultdict(set)
    for row in rows:
        month = (row.get("timestamp") or "")[:7]
        sessions[(row["source"], row["session"])].append(row)
        if row["cwd"]:
            workspaces["/".join(Path(row["cwd"]).parts[-2:])] += 1
        moment = parse_time(row.get("timestamp"))
        if moment:
            local = moment.astimezone()
            hours[local.hour] += 1
            days[local.date().isoformat()] += 1
        monthly[month]["total"] += 1
        found = set(row.get("signals", ()))
        counts.update(found)
        monthly[month].update(found)
        session_signals[(row["source"], row["session"])] |= found

    turns = [len(v) for v in sessions.values()]
    durations = []
    for items in sessions.values():
        times = [t for t in (parse_time(i.get("timestamp")) for i in items) if t]
        if len(times) >= 2:
            minutes = (max(times) - min(times)).total_seconds() / 60
            if minutes <= 24 * 60:
                durations.append(minutes)
    late = sum(c for h, c in hours.items() if h >= 22 or h < 4)
    weekend = sum(c for d, c in days.items() if datetime.date.fromisoformat(d).weekday() >= 5)
    words = [r["words"] for r in rows]

    print(json.dumps({
        "filters": {k: getattr(args, k) for k in ("since", "until", "source", "cwd", "origin")},
        "turns": len(rows),
        "sessions": len(sessions),
        "date_range": [min(dated), max(dated)] if (dated := [r["timestamp"] for r in rows if r.get("timestamp")]) else None,
        "by_source": collections.Counter(r["source"] for r in rows),
        "words_per_turn": {"median": statistics.median(words), "p90": quantile(words, 0.9)},
        "signal_rates_pct": {k: pct(v, len(rows)) for k, v in sorted(counts.items())},
        "session_shape": {
            "turns_median": statistics.median(turns), "turns_p90": quantile(turns, 0.9),
            "duration_min_median": round(statistics.median(durations), 1) if durations else None,
            "duration_min_p90": round(quantile(durations, 0.9), 1) if durations else None,
            "with_rework_pct": pct(sum("agent_rework" in s for s in session_signals.values()), len(sessions)),
            "with_repeated_constraint_pct": pct(sum("repeated_constraint" in s for s in session_signals.values()), len(sessions)),
            "with_shipping_pct": pct(sum("shipping_action" in s for s in session_signals.values()), len(sessions)),
        },
        "work_time": {"active_days": len(days), "late_night_10pm_4am_pct": pct(late, sum(hours.values())),
                      "weekend_pct": pct(weekend, sum(days.values())), "top_hours_local": hours.most_common(6)},
        "top_skills": collections.Counter(s for r in rows for s in skill_mentions(r["text"])).most_common(25),
        "top_workspaces": workspaces.most_common(15),
        "monthly_pct": {m: {"total": v["total"], **{k: pct(v[k], v["total"]) for k in ("scope_control", "evidence_demand", "agent_rework", "repeated_constraint", "agent_orchestration")}}
                        for m, v in sorted(monthly.items()) if m},
    }, indent=2, default=dict))


def search(args):
    pattern = re.compile(args.regex or "", re.I)
    # Neighbors shown as context can be any turn of the session, so only a context-free search narrows in SQL.
    rows = load(args) if args.context else load(args, max_words=args.max_words, signal=args.signal)

    def hit(row):
        if row["words"] > args.max_words or not pattern.search(row["text"]):
            return False
        return not args.signal or args.signal in row.get("signals", ())

    hits = [i for i, r in enumerate(rows) if hit(r)]
    if args.sample:
        random.Random(args.seed).shuffle(hits)
    else:
        hits.sort(key=lambda i: rows[i].get("timestamp") or "", reverse=True)
    by_session = collections.defaultdict(list)
    if args.context:
        for i, row in enumerate(rows):
            by_session[(row["source"], row["session"])].append(i)
        for indices in by_session.values():
            indices.sort(key=lambda i: rows[i].get("timestamp") or "")
    def trim(text):
        return text if len(text) <= args.chars else text[: args.chars] + " …"

    # Count sessions over every hit, not the shown ones, so a capped search never undercounts.
    sessions = len({(rows[i]["source"], rows[i]["session"]) for i in hits})
    print(json.dumps({"matches": len(hits), "sessions": sessions, "shown": min(len(hits), args.limit)}))
    for i in hits[: args.limit]:
        row = rows[i]
        result = {k: row[k] for k in ("source", "session", "timestamp", "cwd")}
        result["text"] = trim(row["text"])
        if args.signal in SIGNAL_RE:
            found = SIGNAL_RE[args.signal].search(prose(row["text"]))
            result["match"] = found.group(0) if found else None
        if args.context:
            ordered = by_session[(row["source"], row["session"])]
            at = ordered.index(i)
            result["before"] = [trim(rows[j]["text"]) for j in ordered[max(0, at - args.context): at]]
            result["after"] = [trim(rows[j]["text"]) for j in ordered[at + 1: at + 1 + args.context]]
        print(json.dumps(result, ensure_ascii=False))


def sessions_in_order(rows):
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[(row["source"], row["session"])].append(row)
    for turns in grouped.values():
        turns.sort(key=lambda r: r.get("timestamp") or "")
    return grouped


CORRECTIONS = ("agent_rework", "repeated_constraint")


def session_units(rows):
    """One unit per session: its first real message, the signals found there and anywhere, and whether the agent was corrected later.

    `corrected` is None when fewer than two turns follow the first message, since a short session can't show a correction either way.
    """
    units, late = [], collections.Counter()
    for turns in sessions_in_order(r for r in rows if r["words"] <= LARGE_PASTE_WORDS).values():
        detected = [(turn, set(turn.get("signals", ()))) for turn in turns]
        first = next(((t, s) for t, s in detected if t.get("prose_words", t["words"]) >= OPENER_MIN_WORDS), None)
        if not first:
            continue
        opened_at = first[0].get("timestamp") or ""
        after = [s for t, s in detected if (t.get("timestamp") or "") > opened_at]
        later = set().union(*after)
        units.append({"opener": first[0], "found": {"opener": first[1], "session": set().union(*(s for _, s in detected))},
                      "turns": detected, "corrected": bool(later & set(CORRECTIONS)) if len(after) >= 2 else None})
        for name in LATE_CONSTRAINT_SIGNALS:
            if name in first[1]:
                late[f"{name}:upfront"] += 1
            elif name in later:
                late[f"{name}:late"] += 1
    return units, late


def started(unit):
    return (unit["opener"].get("timestamp") or "")[:10]


def too_few(a, b):
    """Two shares too small to test: under 10 sessions on either side, or under 5 hits between them."""
    return min(a["n"], b["n"]) < 10 or a["k"] + b["k"] < 5


def payoff(units, name):
    """How often the agent was corrected after a first message that showed the habit, against one that didn't."""
    judged = [unit for unit in units if unit["corrected"] is not None]
    did = [unit["corrected"] for unit in judged if name in unit["found"]["opener"]]
    did_not = [unit["corrected"] for unit in judged if name not in unit["found"]["opener"]]
    result: dict = {"with": proportion(sum(did), len(did)), "without": proportion(sum(did_not), len(did_not))}
    if not too_few(result["with"], result["without"]):
        result["p"] = two_proportion_p(sum(did), len(did), sum(did_not), len(did_not))
    return result


def window_change(lately, earlier):
    """Lately against Before for one habit: None with an empty window, no test when the counts are too few."""
    if not (lately["n"] and earlier["n"]):
        return None
    if too_few(lately, earlier):
        return {"verdict": "too few to tell"}
    low, high = newcombe(lately["k"], lately["n"], earlier["k"], earlier["n"])
    return {"points": round(100 * (lately["rate"] - earlier["rate"]), 1), "low": round(100 * low, 1),
            "high": round(100 * high, 1), "p": two_proportion_p(lately["k"], lately["n"], earlier["k"], earlier["n"])}


def score(args):
    units, late = session_units(load(args, max_words=LARGE_PASTE_WORDS))
    if not units:
        sys.exit("No sessions match the filters.")

    today = datetime.datetime.now(datetime.UTC).date()
    recent_since = (today - datetime.timedelta(days=args.recent_days)).isoformat()
    before_since = (today - datetime.timedelta(days=args.recent_days + args.baseline_days)).isoformat()
    # A session dated after today comes from a wrong clock, so it counts toward no window or month.
    recent = [unit for unit in units if recent_since <= started(unit) <= today.isoformat()]
    before = [unit for unit in units if before_since <= started(unit) < recent_since]
    months = sorted({started(unit)[:7] for unit in units if started(unit) and started(unit)[:7] <= today.isoformat()[:7]})[-args.trend_months:]
    by_month = {month: [unit for unit in units if started(unit)[:7] == month] for month in months}

    def count(group, name, level):
        return sum(name in unit["found"][level] for unit in group)

    def excerpt(turn):
        return {"timestamp": turn["timestamp"], "session": turn["session"], "text": prose(turn["text"])[:400]}

    def example_turns(name, level):
        for unit in sorted(units, key=started, reverse=True):
            candidates = [(unit["opener"], unit["found"]["opener"])] if level == "opener" else unit["turns"]
            for turn, found in candidates:
                if name in found and 15 <= turn.get("prose_words", turn["words"]) <= 150:
                    yield turn
                    break

    dimensions = []
    for dimension in SCORECARD:
        name, level = dimension["id"], dimension["level"]
        lately, earlier = proportion(count(recent, name, level), len(recent)), proportion(count(before, name, level), len(before))
        change = window_change(lately, earlier)
        examples = []
        for turn in example_turns(name, level):
            examples.append(excerpt(turn))
            if len(examples) == 2:
                break
        dimensions.append({**dimension, "lately": lately, "before": earlier, "change": change,
                           "all_time": proportion(count(units, name, level), len(units)),
                           "monthly": [{"month": m, "k": count(by_month[m], name, level), "n": len(by_month[m])} for m in months],
                           "examples": examples})
    for d in dimensions:
        if d["level"] == "opener":
            d["payoff"] = payoff(units, d["id"])
    judged = [d["payoff"] for d in dimensions if "p" in d.get("payoff", {})]
    for result_payoff, q in zip(judged, bh_adjust([j["p"] for j in judged])):
        fewer = result_payoff["with"]["rate"] < result_payoff["without"]["rate"]
        result_payoff["verdict"] = ("holds up" if q < 0.05 else "a hint, not proof" if result_payoff["p"] < 0.05
                                    else "no clear difference")
        result_payoff["direction"] = "fewer corrections" if fewer else "more corrections"
    tested = [d for d in dimensions if d["change"] and "p" in d["change"]]
    for d, q in zip(tested, bh_adjust([d["change"]["p"] for d in tested])):
        direction = "up" if d["change"]["points"] > 0 else "down"
        d["change"]["q"] = q
        d["change"]["verdict"] = direction if q < 0.05 else f"maybe {direction}" if d["change"]["p"] < 0.05 else "no clear change"

    ambition = set(AMBITION_DIMENSIONS)
    plain = [unit["opener"] for unit in recent if not unit["found"]["opener"] & ambition
             and 15 <= unit["opener"].get("prose_words", unit["opener"]["words"]) <= 120]
    repeated = [unit for unit in units if "repeated_constraint" in unit["found"]["session"]]
    result = {
        "sessions": len(units),
        "first_session": min((started(unit) for unit in units if started(unit)), default=None),
        "windows": {"lately": {"since": recent_since, "sessions": len(recent)},
                    "before": {"since": before_since, "until": recent_since, "sessions": len(before)}},
        "dimensions": dimensions,
        "teach_once": proportion(sum("teach_once" in unit["found"]["session"] for unit in repeated), len(repeated)),
        "late_constraints": {
            name: proportion(late[f"{name}:late"], late[f"{name}:upfront"] + late[f"{name}:late"])
            for name in LATE_CONSTRAINT_SIGNALS
        },
        "recent_plain_openers": [excerpt(t) for t in random.Random(args.seed).sample(plain, min(3, len(plain)))],
    }
    if args.cards:
        print(cards_markdown(result, args.cards.split(",")))
    else:
        print(scorecard_markdown(result, args.definitions) if args.markdown else json.dumps(result, indent=2, ensure_ascii=False))


AREAS = {"briefing": "How you brief", "ambition": "How high you aim", "checking": "How you check the work",
         "steering": "How you steer", "orchestration": "How you split the work", "setup": "How you set up your tools",
         "automation": "How you set up your tools", "sharing": "How you set up your tools"}
LATE_NAMES = {"scope_control": "What's in and out of scope", "outside_judge": "How you'll know it worked",
              "evidence_demand": "What proof you want", "shipping_authority": "How far the agent can go"}


def interval(share):
    return f"{share['k']} of {share['n']}, {round(100 * share['rate'])}% ({round(100 * share['low'])}-{round(100 * share['high'])}%)" \
        if share["n"] else "no sessions"


def sparkline(monthly):
    if sum(m["k"] for m in monthly) < 5:
        return "too few to chart"
    rates = [m["k"] / m["n"] if m["n"] >= 10 else None for m in monthly]
    peak = max((r for r in rates if r is not None), default=None)
    if not peak:
        return "too few to chart"
    return "".join("·" if r is None else "▁▂▃▄▅▆▇█"[min(7, int(8 * r / peak))] for r in rates)


def change_text(change):
    if not change:
        return "not enough data"
    if change["verdict"] == "too few to tell":
        return "too few to tell"
    spread = f"{change['low']:+.1f} to {change['high']:+.1f} pts"
    if change["verdict"] == "no clear change":
        return f"no clear change ({spread})"
    return f"{change['verdict']} {abs(change['points']):.1f} pts ({spread})"


def ordered(dimensions):
    return [d for area in AREAS for d in sorted((d for d in dimensions if d["area"] == area), key=lambda d: -(d["lately"]["rate"] or 0))]


CHANGE_WORDS = {"up": "a confirmed rise", "down": "a confirmed drop", "maybe up": "might be rising, not confirmed yet",
                "maybe down": "might be falling, not confirmed yet", "no clear change": "no clear change",
                "too few to tell": "too few to tell"}


def payoff_text(result_payoff):
    did, did_not = result_payoff["with"], result_payoff["without"]
    if did["n"] >= 10 and not did_not["n"]:
        return (f"Every judged session opened this way ({did['n']}), so there's nothing to compare it against.")
    if did["n"] < 10:
        return (f"Too few of your sessions opened this way ({did['n']}) to tell whether it changes how often the agent needs "
                "correcting.")
    sentence = (f"When your first message did it, the agent needed correcting later in {did['k']} of {did['n']} sessions "
                f"({round(100 * did['rate'])}%), against {round(100 * did_not['rate'])}% when it didn't.")
    if "verdict" not in result_payoff:
        return f"{sentence} Those counts are too few to tell."
    if result_payoff["verdict"] == "holds up":
        return f"{sentence} That difference holds up, but it shows a link, not that the habit caused it."
    if result_payoff["verdict"] == "a hint, not proof":
        return f"{sentence} That's a hint, not proof, and it would show a link, not that the habit caused it."
    return f"{sentence} That gap could be chance."


def cards_markdown(result, ids):
    """Plain-language cards for chosen habits: what it is, why it should help, and what your history shows."""
    by_id = {d["id"]: d for d in result["dimensions"]}
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        sys.exit(f"Unknown habit: {', '.join(unknown)}. Scorecard habits: {', '.join(d['id'] for d in SCORECARD)}.")
    cards = []
    for d in (by_id[i] for i in ids):
        where = "your first message" if d["level"] == "opener" else "a conversation"
        lately, before = d["lately"], d["before"]
        trend = CHANGE_WORDS[d["change"]["verdict"]] if d["change"] else "not enough data to compare"
        before_days = (datetime.date.fromisoformat(result["windows"]["before"]["until"])
                       - datetime.date.fromisoformat(result["windows"]["before"]["since"])).days
        lines = [f"### {d['label']}", "",
                 f"**What it is.** In {where}, you write things like {d['counts']}.", "",
                 f"**Why it should help.** {d['why']}", "",
                 f"**For you.** You did it in {lately['k']} of your last {lately['n']} sessions, against {before['k']} of "
                 f"{before['n']} in the {before_days} days before that ({trend})."]
        if "payoff" in d:
            lines[-1] += " " + payoff_text(d["payoff"])
        cards.append("\n".join(lines))
    return "\n\n".join(cards)


def source_links(ids, table=False):
    """Markdown links to a habit's sources by title, with pipes escaped when the links sit in a table cell."""
    links = [f"[{GUIDES[i]['title']}]({GUIDES[i]['url']})" for i in ids]
    return ", ".join(link.replace("|", "\\|") if table else link for link in links)


def scorecard_markdown(result, definitions=False):
    """The scorecard with counts, intervals, and trends, so reports quote numbers instead of retyping them."""
    lately, before = result["windows"]["lately"], result["windows"]["before"]
    months = [m["month"] for m in result["dimensions"][0]["monthly"]]
    lines = [
        "**How to read this**", "",
        "- Each line is a habit that the public guides listed in the know-thyself guide recommend. The cells count the sessions "
        "where you did it, so higher is better. "
        f"**Lately** is since {lately['since']} ({lately['sessions']} sessions); "
        f"**Before** is {before['since']} to {before['until']} ({before['sessions']} sessions).",
        "- Lines marked * look only at the first message of each session. The rest look at everything you typed in the session.",
        "- Each cell reads as count, rate, and in brackets the 95% range: the rates these counts are consistent with. "
        "Small counts give wide ranges, so read the range before the rate.",
        "- **Change** says up or down when the difference holds even after allowing for checking every habit at once. "
        "Maybe up or maybe down means it would pass on its own but not across all of them. Otherwise it says no clear change, "
        "or too few to tell when either window has under 10 sessions or the two have under 5 between them.",
        f"- **Trend** runs {months[0]} to {months[-1]}, one mark per month, scaled to that line's highest monthly rate. "
        "· marks a month with under 10 sessions." if months else "- **Trend** is empty because no session has a date.",
        "- Counts come from matching what you wrote, so they are a floor. You may do the thing in words the matcher misses.", "",
        "| | Habit that helps | Lately | Before | Change | Trend |", "|---|---|---|---|---|---|"]
    shown = None
    for d in ordered(result["dimensions"]):
        group = AREAS[d["area"]]
        star = " *" if d["level"] == "opener" else ""
        lines.append(f"| {'' if group == shown else group} | {d['label']}{star} | {interval(d['lately'])} | "
                     f"{interval(d['before'])} | {change_text(d['change'])} | {sparkline(d['monthly'])} |")
        shown = group
    since = f" since {result['first_session']}" if result["first_session"] else ""
    lines += ["", f"**Things you add after the agent has started.** Across all {result['sessions']} sessions{since}, each row counts the sessions where it came up at all, and how many of those "
              "added it after the first message.", "",
              "| What you added | Added after the first message |", "|---|---|"]
    lines += [f"| {LATE_NAMES[name]} | {interval(share)} |" for name, share in result["late_constraints"].items()]
    teach = result["teach_once"]
    rate = f"{round(100 * teach['rate'])}%, 95% range {round(100 * teach['low'])}-{round(100 * teach['high'])}%" if teach["n"] else "no sessions"
    lines += ["", f"**Teach once.** You repeated a correction in {teach['n']} sessions and turned it into a lasting rule "
              f"(an instructions file line, a skill, a hook, or a lint) in {teach['k']} of them ({rate})."]
    if definitions:
        lines += ["", "**What each line counts**", "",
                  "A session is one conversation with an agent. It counts once toward a line if anything you typed in it "
                  "reads like the examples (only your first message, for lines marked *), no matter how many times you said it.", "",
                  "| Habit that helps | Counted when you write things like | Where it comes from |", "|---|---|---|"]
        lines += [f"| {d['label']}{' *' if d['level'] == 'opener' else ''} | {d['counts']} | {source_links(d['sources'], table=True)} |"
                  for d in ordered(result["dimensions"])]
    return "\n".join(lines)

def paths(_args):
    connect()
    print(json.dumps({"data": str(DATA), "data_from": DIRS["data"][1], "reports": str(REPORTS), "reports_from": DIRS["reports"][1],
                      "config": str(CONFIG), "config_exists": CONFIG.exists(), "corpus": str(DB),
                      "corpus_exists": DB.exists()}, indent=2))


def show_coverage(_args):
    db = connect()
    if not db:
        sys.exit(f"No corpus at {DB}. Run: convo.py mine")
    print(json.dumps(meta_value(db, "coverage", {}), indent=2))


def latest_reports():
    """The newest report of each kind, by its date and then its -2, -3 suffix, as {kind: {path, date, days_ago}} or None."""
    today = datetime.date.today()  # report names use the local date
    latest = {}
    for kind, suffixes in REPORT_KINDS.items():
        found = []
        for path in REPORTS.glob("*.md") if REPORTS.exists() else ():
            named = re.fullmatch(rf"(\d{{4}}-\d{{2}}-\d{{2}})-(?:{'|'.join(suffixes)})(?:-(\d+))?\.md", path.name)
            if named:
                found.append((named.group(1), int(named.group(2) or 1), path))
        if found:
            day, _, path = max(found)
            latest[kind] = {"path": str(path), "date": day, "days_ago": (today - datetime.date.fromisoformat(day)).days}
        else:
            latest[kind] = None
    return latest


def context(args):
    """One start for every run: refresh a stale corpus, then print the profile, the latest reports, and what to do first."""
    directives, mined = [], None
    db = connect()
    if not db:
        directives.append("NO_CORPUS: run `convo.py setup` and tell the user the first mine reads their whole history, "
                          "which can take a few minutes. Then run context again.")
    else:
        coverage = meta_value(db, "coverage", {})
        mined_at = parse_time(coverage.get("mined_at"))
        age = (datetime.datetime.now(datetime.UTC) - mined_at).total_seconds() / 3600 if mined_at else None
        stale = age is None or age > STALE_HOURS or coverage.get("rules") != RULES_HASH or meta_value(db, "clean") != CLEAN_HASH
        db.close()
        if stale and not args.no_mine:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "mine"], capture_output=True, text=True)
            mined = {"ok": result.returncode == 0, "why": "over a day old" if age is None or age > STALE_HOURS else "rules changed"}
            if result.returncode:
                directives.append(f"MINE_FAILED: tell the user the corpus was last mined {coverage.get('mined_at') or 'at an unknown time'}, and why: "
                                  f"{result.stderr.strip()[-300:]}")
        elif stale:
            directives.append("STALE_CORPUS: run `convo.py mine` before counting anything.")
    profile = {"path": str(PROFILE), "exists": PROFILE.exists(), "text": PROFILE.read_text() if PROFILE.exists() else None}
    if not profile["exists"]:
        directives.append("NO_PROFILE: don't block on it. Do what was asked, then offer `init` once, at the end of the reply.")
    db = connect()
    coverage = meta_value(db, "coverage", {}) if db else {}
    if db:
        db.close()
    print(json.dumps({"directives": directives, "mined": mined,
                      "corpus": {"path": str(DB), "mined_at": coverage.get("mined_at"), "turns": coverage.get("corpus_turns"),
                                 "by_origin": coverage.get("by_origin")} if db else None,
                      "reports_dir": str(REPORTS), "latest_reports": latest_reports(), "profile": profile}, indent=2))


def lint_reply(args):
    import lint
    lint.run(args, PROFILE)


def export(args):
    """Write every turn, in every origin, as one JSON line, so the corpus can leave SQLite."""
    db = connect()
    if not db:
        sys.exit(f"No corpus at {DB}. Run: convo.py mine")
    count = 0
    with open(args.jsonl, "w", encoding="utf-8") as out:
        for row in rows_from(db):
            out.write(json.dumps({**row, "text": row["text"]}, ensure_ascii=False) + "\n")
            count += 1
    print(json.dumps({"exported": count, "path": str(Path(args.jsonl).resolve())}))


def setup(args):
    """Write the config, then mine and check in a fresh process that reads it."""
    config = read_config()
    for key, value in (("data_dir", args.data_dir), ("reports_dir", args.reports_dir)):
        if value:
            config[key] = str(Path(value).expanduser().resolve())
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")
    dirs = resolve_dirs()
    data, reports = dirs["data"][0], dirs["reports"][0]
    data.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    script = str(Path(__file__).resolve())
    mined = subprocess.run([sys.executable, script, "mine", *[f"--import={p}" for p in args.import_paths]],
                           capture_output=True, text=True)
    checked = subprocess.run([sys.executable, script, "check"], capture_output=True, text=True)
    coverage = json.loads(mined.stdout) if mined.returncode == 0 else {}
    print(json.dumps({"config": str(CONFIG), "data": str(data), "reports": str(reports),
                      "mine": {k: coverage.get(k) for k in ("mode", "corpus_turns", "by_origin")} if coverage else mined.stderr[-2000:],
                      "check": (checked.stdout.strip().splitlines() or [checked.stderr.strip()])[-1]}, indent=2))
    sys.exit(mined.returncode or checked.returncode)


def compare(args):
    """Whether a habit, and how often the agent needed correcting, changed after a date: since the date against the same span before it."""
    labels = {d["id"]: d["label"] for d in SCORECARD}
    if args.habit not in labels:
        sys.exit(f"Unknown habit: {args.habit}. Scorecard habits: {', '.join(labels)}.")
    today = datetime.datetime.now(datetime.UTC).date()
    chosen = {"habit": args.habit, "started": args.since}
    args.since = None
    level = next(d["level"] for d in SCORECARD if d["id"] == chosen["habit"])
    began = datetime.date.fromisoformat(chosen["started"])
    window = max((today - began).days, 30)
    window_start = (began - datetime.timedelta(days=window)).isoformat()
    units, _ = session_units(load(args, max_words=LARGE_PASTE_WORDS))
    since = [unit for unit in units if chosen["started"] <= started(unit) <= today.isoformat()]
    before = [unit for unit in units if window_start <= started(unit) < chosen["started"]]

    def compare(after, earlier):
        result = {"since": after, "before": earlier}
        if after["k"] + earlier["k"] < 10:
            result["verdict"] = "too few to tell"
        elif after["n"] and earlier["n"]:
            low, high = newcombe(after["k"], after["n"], earlier["k"], earlier["n"])
            p_value = two_proportion_p(after["k"], after["n"], earlier["k"], earlier["n"])
            direction = "up" if after["rate"] > earlier["rate"] else "down"
            result.update(points=round(100 * (after["rate"] - earlier["rate"]), 1), low=round(100 * low, 1),
                          high=round(100 * high, 1), p=p_value,
                          verdict=direction if p_value < 0.05 else "too early to tell" if after["n"] < 20 else "no clear change")
        else:
            result["verdict"] = "too early to tell"
        return result

    def judged(group):
        return [unit for unit in group if unit["corrected"] is not None]

    checkin = {
        "habit_id": chosen["habit"],
        "label": labels[chosen["habit"]],
        "since": chosen["started"],
        "days_since": (today - began).days,
        "compared_with": {"since": window_start, "until": chosen["started"]},
        "habit": compare(proportion(sum(chosen["habit"] in u["found"][level] for u in since), len(since)),
                         proportion(sum(chosen["habit"] in u["found"][level] for u in before), len(before))),
        "corrected": compare(proportion(sum(u["corrected"] for u in judged(since)), len(judged(since))),
                             proportion(sum(u["corrected"] for u in judged(before)), len(judged(before)))),
    }
    print(compare_markdown(checkin) if args.markdown else json.dumps(checkin, indent=2))


def share_text(share, unit):
    if not share["n"]:
        return f"no {unit}"
    return f"{share['k']} of {share['n']} {unit} ({round(100 * share['rate'])}%, range {round(100 * share['low'])}-{round(100 * share['high'])}%)"


def compare_markdown(checkin):
    habit, corrected = checkin["habit"], checkin["corrected"]
    opener = next(d["level"] for d in SCORECARD if d["id"] == checkin["habit_id"]) == "opener"
    window = checkin["compared_with"]
    days = (datetime.date.fromisoformat(window["until"]) - datetime.date.fromisoformat(window["since"])).days
    lines = [f"**{checkin['label']}, since {checkin['since']}.**"]
    if not habit["since"]["n"]:
        lines.append("There are no sessions since then yet, so there's nothing to compare.")
        return "\n\n".join(lines)
    lines.append(f"Since then, you did it{' in your first message' if opener else ''} in {share_text(habit['since'], 'sessions')}, "
                 f"against {share_text(habit['before'], 'sessions')} in the {days} days before ({habit['verdict']}).")
    if corrected["since"]["n"]:
        lines.append(f"The agent needed correcting later in {share_text(corrected['since'], 'sessions')} since, against "
                     f"{share_text(corrected['before'], 'sessions')} before ({corrected['verdict']}).")
    return "\n\n".join(lines)

def check(_args):
    """Run every labeled fixture through detect(); exit 1 on any mismatch."""
    emphasis_words = load_vocab()
    failures, total, skipped = [], 0, 0
    for fixture in read_corpus(FIXTURES):
        if fixture["signal"] == "caps_emphasis" and not emphasis_words:
            skipped += 1
            continue
        total += 1
        if (fixture["signal"] in detect(fixture["text"], emphasis_words)) != fixture["expect"]:
            failures.append(fixture)
    for fixture in failures:
        print(json.dumps(fixture, ensure_ascii=False))
    print(f"{total - len(failures)}/{total} fixtures pass"
          + (f"; {skipped} caps_emphasis fixtures skipped until mine builds the vocabulary" if skipped else ""))
    sys.exit(1 if failures else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    mine_parser = commands.add_parser("mine")
    mine_parser.set_defaults(run=mine)
    mine_parser.add_argument("--import", dest="import_paths", action="append", default=[],
                             help="merge an older JSONL corpus (an export, or normalized_prompts.jsonl)")
    mine_parser.add_argument("--full", action="store_true", help="re-read every source instead of only new or changed ones")
    commands.add_parser("signals").set_defaults(run=lambda _a: print(json.dumps({**SIGNALS, **DERIVED_SIGNALS}, indent=2)))
    commands.add_parser("check").set_defaults(run=check)
    commands.add_parser("paths").set_defaults(run=paths)
    context_parser = commands.add_parser("context")
    context_parser.set_defaults(run=context)
    context_parser.add_argument("--no-mine", action="store_true", help="report a stale corpus instead of refreshing it")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import lint
    lint_parser = commands.add_parser("lint")
    lint_parser.set_defaults(run=lint_reply)
    lint.add_arguments(lint_parser)
    commands.add_parser("coverage").set_defaults(run=show_coverage)
    export_parser = commands.add_parser("export")
    export_parser.set_defaults(run=export)
    export_parser.add_argument("--jsonl", required=True, metavar="PATH", help="file to write, one turn per line")
    compare_parser = commands.add_parser("compare")
    compare_parser.set_defaults(run=compare, until=None, source=None, cwd=None, origin="human")
    compare_parser.add_argument("habit", help="scorecard habit id, such as outside_judge; an unknown id prints the list")
    compare_parser.add_argument("--since", required=True, help="the date a change started, YYYY-MM-DD")
    compare_parser.add_argument("--markdown", action="store_true", help="print the comparison in plain words")
    setup_parser = commands.add_parser("setup")
    setup_parser.set_defaults(run=setup)
    setup_parser.add_argument("--data-dir", help=f"where the corpus lives (default {DEFAULT_DATA})")
    setup_parser.add_argument("--reports-dir", help="where reports are written (default <data dir>/reports)")
    setup_parser.add_argument("--import", dest="import_paths", action="append", default=[],
                              help="merge an older corpus or normalized_prompts.jsonl into the first mine")
    for name, run in (("stats", stats), ("search", search), ("score", score)):
        sub = commands.add_parser(name)
        sub.set_defaults(run=run)
        sub.add_argument("--since")
        sub.add_argument("--until")
        sub.add_argument("--source", help="comma list: codex,claude,pi,cursor,opencode")
        sub.add_argument("--cwd", help="substring of the session working directory")
        sub.add_argument("--origin", default="human", help="comma list: human,subagent,harness")
        if name == "score":
            sub.add_argument("--recent-days", type=int, default=60)
            sub.add_argument("--baseline-days", type=int, default=180, help="length of the Before window, ending where Lately starts")
            sub.add_argument("--trend-months", type=int, default=6, help="months shown in the trend")
            sub.add_argument("--definitions", action="store_true", help="with --markdown, add what each line counts")
            sub.add_argument("--cards", help="comma list of habit ids to render as plain-language cards")
            sub.add_argument("--markdown", action="store_true", help="print the full scorecard as tables instead of JSON")
            sub.add_argument("--seed", type=int, default=7)
        if name == "search":
            sub.add_argument("--regex")
            sub.add_argument("--signal", choices=sorted({*SIGNALS, *DERIVED_SIGNALS}))
            sub.add_argument("--limit", type=int, default=25)
            sub.add_argument("--chars", type=int, default=600)
            sub.add_argument("--max-words", type=int, default=LARGE_PASTE_WORDS)
            sub.add_argument("--context", type=int, default=0, help="neighboring turns from the same session")
            sub.add_argument("--sample", action="store_true", help="random sample instead of newest first")
            sub.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
