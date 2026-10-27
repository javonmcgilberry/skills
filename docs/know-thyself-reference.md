# Reference

You already know what know-thyself does and need an exact command, flag, path, setting, or table, so everything here is lookup. New readers start with [the guide](know-thyself.md), and [the scorecard guide](know-thyself-scorecard.md) explains how to read what `score` prints.

Every command runs the same script, and every example below assumes you're at the repository root.

```sh
python3 skills/know-thyself/scripts/convo.py <command> [flags]
```

## Commands

Only `setup`, `mine`, and `export` write anything. The others read the corpus and print, so they're safe to run as often as you like. The one exception is the first command to open a data directory an older version left behind, which converts it to `corpus.db` as [Moving from older files](#moving-from-older-files) describes.

| Command | What it does | Writes |
| --- | --- | --- |
| `setup` | Writes the config file, keeping any keys already in it, creates the data and reports directories, runs `mine` and then `check` in fresh processes, and prints the resolved locations with a short result for each step. It runs `check` even when `mine` fails and exits nonzero if either step failed. | Config file, data directory, reports directory |
| `mine` | Reads every history source it can find, cleans and tags each turn, merges the result into `corpus.db` in one transaction, and prints the coverage summary as JSON | `corpus.db` |
| `stats` | Prints behavior metrics as JSON with the keys `filters`, `turns`, `sessions`, `date_range` (null when no matching turn has a date), `by_source`, `words_per_turn`, `signal_rates_pct` (percent of turns), `session_shape`, `work_time`, `top_skills`, `top_workspaces`, and `monthly_pct`. Each month in `monthly_pct` gives its turn `total` and the percent of turns showing `scope_control`, `evidence_demand`, `agent_rework`, `repeated_constraint`, or `agent_orchestration`, and no other signal, so a monthly trend for any other line has to come from `score`. | Nothing |
| `score` | Prints the scorecard as JSON, as Markdown tables with `--markdown`, or as plain-language cards for chosen habits with `--cards` | Nothing |
| `compare` | Prints whether one habit, and how often the agent needed correcting, changed after a date, as JSON or as sentences with `--markdown` | Nothing |
| `search` | Prints matching turns, newest first or as a random sample, one JSON object per line | Nothing |
| `signals` | Prints every signal name with the regular expression or description behind it | Nothing |
| `check` | Runs every labeled fixture against the signal rules and exits 1 on any mismatch. Until a mine has built the vocabulary, it skips the `caps_emphasis` fixtures and says how many it skipped. | Nothing |
| `coverage` | Prints the summary the last `mine` stored, with files found per source, what was parsed or reused, redactions, and when it ran | Nothing |
| `export` | Writes every turn, in every origin, to the file `--jsonl` names, one JSON object per line, and prints the count and the path | The named file |
| `paths` | Prints where data, reports, config, and `corpus.db` live, and which setting chose the data and reports locations | Nothing |

When the signal rules in `convo.py` differ from the ones the last mine stored, as after an update that changes them, `stats`, `score`, `compare`, and `search` print `signal rules changed since the last mine; recomputing (slow). Run: convo.py mine` to stderr and recompute signals in memory on every run until a mine stores them.

`stats`, `score`, and `compare` ignore turns over 2,000 words, because those are almost always pasted material rather than something you typed. `search` applies the same limit through `--max-words`.

### Filters

`stats`, `score`, and `search` share these flags. `compare` takes none of them and always reads human turns from every source.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--since YYYY-MM-DD` | none | Keep turns dated on or after this day, compared against the first ten characters of the stored timestamp, which drops undated turns |
| `--until YYYY-MM-DD` | none | Keep turns dated on or before this day, and undated turns |
| `--source` | all | Comma list of `codex`, `claude`, `pi`, `cursor`, `opencode` |
| `--cwd` | none | Keep turns whose working directory contains this text, ignoring case |
| `--origin` | `human` | Comma list of `human`, `subagent`, `harness` |

### `score`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--recent-days` | 60 | Length of the Lately window, counted back from today in UTC |
| `--baseline-days` | 180 | Length of the Before window, which ends where Lately starts |
| `--trend-months` | 6 | How many of the most recent months with sessions, up to the current month, get a trend mark |
| `--markdown` | off | Print the scorecard as tables instead of JSON |
| `--definitions` | off | With `--markdown`, add a table of the example phrases each line counts and the guides it comes from |
| `--cards` | none | Comma list of line ids to print as cards instead of the scorecard. It wins over `--markdown`, and an id that isn't one of the 30 lines exits with an error. |
| `--seed` | 7 | Seed for picking up to three `recent_plain_openers`, so repeated runs pick the same ones |

The JSON has `sessions`, `first_session`, `windows`, `dimensions`, `teach_once`, `late_constraints`, and `recent_plain_openers`. Each entry in `dimensions` carries the line's `id`, `label`, `why`, `counts`, `nudge`, `level`, `area`, and `sources`, its `lately`, `before`, and `all_time` shares, `change`, `monthly` counts, up to two `examples`, and, for lines that look at the first message, a `payoff`. The `id` is what `--cards` and `compare` take, and `sources` lists the ids of the guides the line comes from. `first_session` is null when no session has a date, and the Lately count in `windows` leaves out sessions dated after today. [The scorecard guide](know-thyself-scorecard.md) explains each one.

`lately`, `before`, and `all_time` each hold `k`, `n`, `rate`, `low`, and `high`, where `low` and `high` are a Wilson 95% range as fractions, and `all_time` covers every session the filters allow. `change` is null when either window is empty. When either window has under 10 sessions, or the two have under 5 sessions between them that showed the habit, it holds only a `verdict` of `too few to tell`, and the line stays out of the Benjamini-Hochberg correction. Otherwise it holds `points`, `low`, and `high` (a Newcombe range, in percentage points), `p`, `q` (after the correction across the lines that were tested), and `verdict`. Each `monthly` entry has `month`, `k`, and `n`. `payoff` holds `with` and `without` shares, and adds `p`, `verdict`, and `direction` only when at least 10 judged sessions showed the habit, at least 10 didn't, and at least 5 of them needed correcting between the two sides.

A card from `--cards` has three paragraphs under the line's label. **What it is** quotes the example phrases, **Why it should help** gives the line's `why`, and **For you** gives the Lately and Before counts with the Change verdict and, for lines that look at the first message, the payoff. Cards print no sources. The line's `sources` stay in the JSON, so a coaching reply can list the ones its suggestions used in a Sources section at the end.

`skills/know-thyself/references/sources.json` lists every public guide the skill cites, each with `id`, `title`, `publisher`, and `url`. Scorecard lines name them by id in `sources`, `skills/know-thyself/references/practices.md` links them by the same ids, and [the guide](know-thyself.md#where-the-advice-comes-from) lists them all. `convo.py` reads the file once when it starts.

### `compare`

| Argument | Default | Meaning |
| --- | --- | --- |
| habit | required | One scorecard line's `id`, such as `outside_judge`. Any other name exits with an error that lists the 30 scorecard ids. |
| `--since YYYY-MM-DD` | required | The day a change started. Sessions from that day to today are set against the same number of days just before it, never fewer than 30. |
| `--markdown` | off | Print a heading and up to two sentences instead of JSON |

The JSON has `habit_id`, `label`, `since`, `days_since`, `compared_with` (the earlier span's `since` and `until`), and `habit` and `corrected`. Each of those two holds `since` and `before` shares and a `verdict`, plus `points`, `low`, `high`, and `p` when there were enough sessions to test. [The scorecard guide](know-thyself-scorecard.md#checking-a-change-with-compare) explains the verdicts.

### `search`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--regex` | none | Case-insensitive pattern matched against the stored text of each turn |
| `--signal` | none | Keep only turns that carry this signal; `signals` lists the names |
| `--limit` | 25 | How many matches to print |
| `--chars` | 600 | Cut each printed text after this many characters |
| `--max-words` | 2000 | Skip turns longer than this many words |
| `--context` | 0 | Also print this many turns before and after each match from the same session |
| `--sample` | off | Shuffle matches instead of listing newest first |
| `--seed` | 7 | Seed for `--sample` |

The first line counts the matches and the sessions they fall in, over every match rather than only the ones shown, and each following line is one match. With `--signal`, a `match` field shows the exact words the rule matched, which is what you read to judge a false positive. Derived signals such as `caps_emphasis` have no `match`. The block below is an example with invented values.

```json
{"matches": 41, "sessions": 17, "shown": 1}
{"source": "codex", "session": "a1b2c3", "timestamp": "2025-03-04T15:20:11Z", "cwd": "/home/dev/shop", "text": "Fix the flaky cart test. Done when it passes ten runs in a row.", "match": "Done when"}
```

### `mine`, `setup`, and `export`

| Command | Flag | Meaning |
| --- | --- | --- |
| `mine` | `--full` | Re-read every source instead of only new or changed ones. Turns already in the corpus whose source files are gone are still kept, but each stored turn is cleaned again under the current rules and dropped if it no longer qualifies. A mine is also full without the flag whenever the cleaning or signal rules have changed. |
| `mine` | `--import PATH` | Merge a JSON-lines corpus whose rows have at least `source`, `session`, `timestamp` (null allowed), and `text`, as [Export rows](#export-rows) do, such as an `export --jsonl` file or a `normalized_prompts.jsonl` file. Repeat the flag for several files. Imported turns are cleaned and redacted again under the current rules, dropped if they no longer qualify, and tagged for origin again. |
| `setup` | `--data-dir PATH` | Save this data directory in the config file as an absolute path |
| `setup` | `--reports-dir PATH` | Save this reports directory in the config file as an absolute path |
| `setup` | `--import PATH` | Pass the file to the first `mine` as `--import` |
| `export` | `--jsonl PATH` | Required. The file to write, replacing it if it exists. |

`setup` doesn't move an existing corpus, install the skill anywhere, or schedule later mines. Pointing `--data-dir` somewhere new makes the next mine start an empty `corpus.db` there, so turns whose source files are gone stay behind in the old one. To move them, run `convo.py export --jsonl FILE` while the old location is still in effect, then `convo.py setup --data-dir DIR --import FILE` with the new directory and the exported file.

## Where data and config live

Each location is resolved when the script starts. For the data and reports directories an environment variable wins, then the config file, then the default. The config file itself moves only with `XDG_CONFIG_HOME`.

| What | Default | Environment variable | Config key |
| --- | --- | --- | --- |
| Config file | `~/.config/know-thyself/config.json` | `XDG_CONFIG_HOME` replaces `~/.config` | none |
| Data directory | `~/.local/share/know-thyself/` | `KNOW_THYSELF_DATA_DIR`, and `XDG_DATA_HOME` replaces `~/.local/share` in the default | `data_dir` |
| Reports directory | `reports/` inside the data directory | `KNOW_THYSELF_REPORTS_DIR` | `reports_dir` |

The config file is JSON. If it isn't valid JSON, or doesn't hold an object, every command stops and names the file, because guessing would quietly move your data directory. `setup` writes `data_dir` or `reports_dir` into it when you pass `--data-dir` or `--reports-dir`, and leaves other keys alone. The only other key the script reads is `harness_patterns`, a list of regular expressions for prompts your own tools write in your name. `mine` tags a turn `harness` when its text matches one, ignoring case and anywhere in the text unless the pattern is anchored. Each pattern is compiled on its own, and one that fails to compile, isn't a string, or matches empty text (and so would match every prompt) is skipped, with a warning on stderr that names it and the problem. The config is read whenever the script starts, so that warning prints on every command until you fix the pattern. The patterns stay in your config and never enter the repository, and changing them makes the next `mine` re-read every source and re-tag every turn. Until that mine runs, `stats`, `score`, `compare`, and `search` warn on stderr that the stored turns are out of date and tell you to run `mine`. The block below is an example config with invented values.

```json
{
  "reports_dir": "/home/dev/notes/coaching",
  "harness_patterns": ["^Nightly digest:", "^Release checklist for "]
}
```

`paths` shows the result. `data_from` and `reports_from` say `default`, the name of the environment variable, or the config file path. The block below is an example with invented values.

```json
{
  "data": "/home/dev/.local/share/know-thyself",
  "data_from": "default",
  "reports": "/home/dev/notes/coaching",
  "reports_from": "KNOW_THYSELF_REPORTS_DIR",
  "config": "/home/dev/.config/know-thyself/config.json",
  "config_exists": true,
  "corpus": "/home/dev/.local/share/know-thyself/corpus.db",
  "corpus_exists": true
}
```

## Files in the data directory

| File | Written by | Holds |
| --- | --- | --- |
| `corpus.db` | `mine` | The SQLite corpus, holding every turn, the signals found in each, what the last mine saw, and the stored vocabulary |
| `*.migrated` | The first command that opens the corpus after an upgrade | An older version's files, renamed once their contents are in `corpus.db` and never read again |
| `reports/` | your agent | Reports, which the skill's instructions name `YYYY-MM-DD-<mode>.md`, such as `-mirror.md`, `-coach.md`, or `-shareable.md`, adding `-2` when that name is taken so no report is overwritten, unless the reports directory is set elsewhere |

`mine` applies all its changes in one SQLite transaction, so an interrupted run leaves the previous corpus whole. It takes the corpus's write lock before it reads anything, so a second `mine`, or the one a `setup` starts, waits up to an hour for the first to finish and then runs on what it wrote, and fails with a database-locked error if the wait runs out.

### Tables in `corpus.db`

- `turns` holds one row per turn with `source`, `session`, `timestamp`, `cwd`, `words`, `spawned`, and `origin`, and for human turns `prose_words` (words left after code, logs, links, and paths are removed) and `caps` (the all-caps words). A turn's text is compressed with zlib into `packed`, or kept in `text` when compressing wouldn't make it smaller, which in practice means short turns. No query reads text in SQL, and `rows_from()` decompresses a turn's text only when the code first reads it, so `score` decodes only the turns it quotes as examples and plain openers, unless the signal rules changed since the last mine, when it decodes every human turn to recompute them. `key` is the first 16 bytes of a SHA-256 over the turn's dedupe key.
- `turn_signals` holds one row per human turn and signal found in it. It's small enough that a `--signal` filter scans it without an index.
- `sources` and `composers` hold the size and modification time of every source file and a change signature for every Cursor conversation, so the next mine can skip what hasn't changed.
- `meta` holds the rule hashes (`clean` and `rules`), the `vocab` that lets `caps_emphasis` tell emphasis from acronyms (words you've typed in all caps that you type in lowercase more often, built from the `upper` and `lower` counts), the running `redacted` counts, and the `coverage` summary.

A full mine ends with `VACUUM`, so the file shrinks back after a rewrite.

### Moving from older files

Older versions kept `corpus.jsonl`, `manifest.json`, `vocab.json`, and `coverage.json` in the data directory. When `corpus.db` doesn't exist and `corpus.jsonl` does, the first command that opens the corpus builds `corpus.db.tmp` from those files, renames it to `corpus.db`, adds `.migrated` to each old file's name, and prints the number of imported turns to stderr. When the old manifest still matched the old corpus file, its hashes come along, so the next `mine` stays incremental unless the cleaning or signal rules have changed since. Otherwise the next `mine` re-reads every source.

### Export rows

Each line `export --jsonl` writes has `source`, `session`, `timestamp`, `cwd`, `words`, `spawned`, `text`, and `origin`, oldest first. Human turns also carry `prose_words`, `signals`, and, when there are any, `caps`. `spawned` is missing for a turn imported from a file that never recorded it. `mine --import` reads this format back. The row below is an example with invented values.

```json
{"source": "pi", "session": "s-0193", "timestamp": "2025-05-12T09:41:07Z", "cwd": "/home/dev/shop", "words": 14, "spawned": false, "text": "Keep the diff small and don't touch the payment form. Investigate only for now.", "origin": "human", "prose_words": 14, "signals": ["research_action", "scope_control", "shipping_authority"]}
```

### Coverage keys

`coverage` prints the summary the last mine stored, and `mine` prints the same object with `corpus` added.

- `codex_files`, `claude_files`, `pi_files`, and `opencode_message_files` count the files found per source.
- `cursor_composers` counts Cursor conversations that aren't marked as subagents, and `chatgpt_encrypted_files_unread` counts ChatGPT desktop files that were found and not read.
- `corpus_turns`, `by_origin`, and `redacted` describe the corpus, with `redacted` counting each kind of credential that was replaced.
- `mode` is `incremental` or `full`, and `files_parsed`, `files_skipped`, `composers_parsed`, and `composers_skipped` say how much of it was reused.
- `files_failed` counts the parsed Codex, Claude Code, Pi, and OpenCode files that raised an error. Each adds no turns and the mine carries on. Its signature isn't stored, so every later mine tries it again and counts it again until it parses.
- `rules` is the hash of the signal rules, and `mined_at` is the UTC time of the run.

## History sources

| Tool | Where it looks | What it reads |
| --- | --- | --- |
| Codex | `~/.codex/sessions` and `~/.codex/archived_sessions`, every `rollout-*.jsonl` below them | User messages. A session whose metadata names a subagent source is tagged `subagent`. |
| Claude Code | `~/.claude/projects`, every `*.jsonl` below it | User messages that aren't meta messages. Sidechain turns are tagged `subagent`. |
| Pi | `~/.pi/agent/sessions`, the `*.jsonl` files one directory down | User messages. None are tagged `subagent`, because the script reads no subagent marker from Pi. |
| OpenCode | `~/.local/share/opencode/storage`, each user message file with the text parts stored for it | User messages. This path is fixed and ignores `XDG_DATA_HOME`. None are tagged `subagent`, because the script reads no subagent marker from OpenCode. |
| Cursor | The first of `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`, `~/.config/Cursor/User/globalStorage/state.vscdb`, and `~/AppData/Roaming/Cursor/User/globalStorage/state.vscdb` that exists, opened read-only | User messages. Conversations Cursor marks as subagents are skipped entirely, so they appear under no origin. Each message in Cursor's list takes the time Cursor stored for it, moved to just after the message before it when it's missing or not later, and the first message without one takes the conversation's creation time, so turns keep Cursor's order. A message missing from that list keeps its own time, or the conversation's creation time. When a changed conversation is read again, its new turns replace the stored ones. |
| ChatGPT desktop | `~/Library/Application Support/com.openai.chat` | Nothing. It counts the `*.data` files there and reports them as unread. |

Before tagging, `mine` drops a turn whose cleaned text is under two characters, is exactly `/model`, `/status`, `/context`, `/help`, or `init`, or opens with an injected-instruction prefix such as `# AGENTS.md instructions`, `<permissions instructions>`, or `<task-notification>`. It also cuts tagged blocks such as `<environment_context>` and `<system-reminder>` out of the text. A raw turn holding `## My request for Codex:` keeps only what follows the first one, which is where Codex puts what you typed, and this happens once, when the turn is first read, so a stored turn that quotes the marker is never cut again. A record with the wrong shape, such as a null where a message belongs, is skipped, a timestamp that's neither text nor a number is stored as missing, and a line or OpenCode file that isn't valid JSON is skipped without a count, and a Codex, Claude Code, Pi, or OpenCode file whose reader raises adds no turns and counts in `files_failed`. The exact lists are `BLOCKED_STARTS`, `STRIP_TAGS`, and `SLASH_NOISE` in `convo.py`.

A turn that isn't `subagent` is tagged `harness` when its working directory starts with `/tmp/`, `/private/tmp/`, or `/var/folders/`, or contains `.scratch` or `autoresearch`. It's also `harness` when its text opens like a scripted prompt, such as `task:`, a heartbeat, a "reply ok" smoke test, or any "You are a", "You are an", or "You are the", which catches a message of yours that opens "You are a senior engineer" too. A few operator phrases count anywhere in the text, such as `(operator:`, "the user authorized", and "user asleep". The same goes for the only turn in a session when it opens with a ticket heading like `# ABC-123:`, and for any turn that matches one of your `harness_patterns`. Everything else is `human`. The exact rules are `HARNESS_CWD`, `HARNESS_TEXT`, and `TICKET_BRIEF` in `convo.py`.

## Checks

[The README](../README.md#checks) owns the repository-wide checks, `scripts/check.sh` and CI. These two commands are know-thyself's own, and `scripts/check.sh` runs the first.

| Command | What it runs |
| --- | --- |
| `python3 skills/know-thyself/scripts/validate_skill.py` | The package validator, which also runs `convo.py check` |
| `python3 skills/know-thyself/scripts/convo.py check` | The signal fixtures alone, skipping the `caps_emphasis` ones until a mine has built the vocabulary |

CI never mines, so it has no vocabulary, and `check` runs every fixture there except the `caps_emphasis` ones. [Development](know-thyself-development.md#test-layers) says what each check guards.
