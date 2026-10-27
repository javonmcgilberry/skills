---
name: know-thyself
description: "Mirror how the user works with AI coding agents, from their conversation history. Use when they ask about themselves (\"tell me about myself\", \"how do I work\", \"let's do a run\"), ask for coaching, ask whether a habit changed since a date or what they decided about something, or want repeated corrections turned into rules."
metadata:
  version: "0.5.0"
---

# Know thyself

The corpus holds every prompt the user typed into a local AI tool, and `scripts/convo.py` builds, measures, and searches it. Numbers and quoted text come only from its output, and a claim is **traced** when you can point to the output it came from.

```sh
S="python3 <skill dir>/scripts/convo.py"
$S paths       # where data, reports, and config live
$S setup       # first run
$S coverage    # mined_at, files read and unread per tool
$S mine        # refresh
$S stats       # date range, turns per tool, rhythm, workspaces
$S score       # scorecard JSON; --cards id,id; --markdown
$S compare     # <habit> --since YYYY-MM-DD; --markdown
$S search      # --regex RE | --signal NAME, --context N, --sample, --limit N, --chars N
$S check       # references/signal-fixtures.jsonl against the signal rules
# stats, score, and search filter by --since --until YYYY-MM-DD, --source codex,pi, --cwd SUBSTR, --origin human
```

Run `setup` when `paths` reports no corpus, and otherwise `mine` when `coverage` shows `mined_at` over a day old.

## Choose a mode

| Mode | Asked for | Read in full first |
|---|---|---|
| Mirror | the default, for "let's do a run", how they work, what they're good or bad at, or anything without another clear mode | `references/mirror.md` |
| Coach | only when asked, as in "coach me on…" or "score my prompts" | `references/coach.md` |
| Trend | whether a habit changed since a date | `references/lookups.md` |
| Recall | what they said or decided about a topic | `references/lookups.md` |
| Lessons | turning a repeated correction into a rule | `references/lessons.md` |

A run is finished when every item on its mode's **Done when** list is true, and a request spanning modes reads each mode's file.

## Guardrails for every mode

1. **Voice.** Read `references/voice.md` before writing any reply or report.
2. **Traced.** Every claim about the user carries a traced number, copied exactly, or a verbatim dated quote, and anything else is labeled inference. Signals are word matches that drift, so before a rate backs a claim, read `search --signal <id> --sample --limit 8` and drop it when fewer than six of the eight `match` fields are real.
3. **Verbatim.** Copy a quote character for character from search output, with the date its line shows, cutting only with "…". Paraphrase outside quotation marks.
4. **Privacy.** Quote short fragments, leaving out credentials, tokens, customer data, and personal details, and keep the user's name and paths out of skill files.
5. **Live configuration.** Propose edits to global agent instructions and skills as diffs, applying each only after the user approves it.
6. **Reports.** Write each report as a new file in the `reports` directory from `paths`, adding `-2`, `-3` when its name is taken.
