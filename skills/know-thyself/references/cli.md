# convo.py

`scripts/convo.py` builds, measures, and searches the corpus, and checks what the skill writes. Numbers and quoted text come only from its output.

```sh
S="python3 <skill dir>/scripts/convo.py"
$S context     # start of every run: refreshes a stale corpus, prints the profile, latest reports, and directives
$S lint        # --mode MODE [REPORT.md] [--reply FILE]; exits 1 with what to fix
$S paths       # where data, reports, and config live
$S setup       # first run
$S coverage    # mined_at, files read and unread per tool
$S mine        # refresh by hand; context does it when the corpus is over a day old
$S stats       # date range, turns per tool, rhythm, workspaces
$S score       # scorecard JSON; --cards id,id; --markdown
$S compare     # <habit> --since YYYY-MM-DD; --markdown
$S search      # --regex RE | --signal NAME, --context N, --sample, --limit N, --chars N
$S check       # references/signal-fixtures.jsonl against the signal rules
```

`stats`, `score`, and `search` filter by `--since` and `--until` (YYYY-MM-DD), `--source codex,pi`, `--cwd SUBSTR`, and `--origin human`.

`context` prints JSON with these keys.

- **`directives`** are what to do before anything else: `NO_CORPUS` (run `setup`), `STALE_CORPUS` (run `mine`; printed only under `--no-mine`, since otherwise `context` mines itself), `MINE_FAILED` (say the corpus is older than a day and why), and `NO_PROFILE` (offer `init` once at the end of the reply, never block on it).
- **`profile`** holds the path of `ME.md` and its text, which every mode reads before writing.
- **`latest_reports`** gives the newest `mirror`, `coach`, `share`, and `lead` report, each with its path, date, and days since, or null.
- **`corpus`** gives when it was mined and how many turns it holds by origin.
