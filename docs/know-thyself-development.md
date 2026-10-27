# Development

You're changing know-thyself's code, signal rules, instructions, or docs, or reviewing someone's change, and you need to know what the change must keep and which check proves it. A change has to keep the contract below, and the test layers after it say which check proves each part and what no check covers. Commands and paths are in [the reference](know-thyself-reference.md), and running the repository's checks, `scripts/check.sh` and CI, is in [the README](../README.md#checks).

## The contract a change must keep

Most reviews come down to whether a change keeps these.

1. **Nothing leaves the machine.** `convo.py` imports only the standard library, opens the Cursor database read-only, and writes only to its config file, data directory, reports directory, and the file you name for `export`. A change that adds a network call or a third-party package breaks the promise [the guide](know-thyself.md) makes.
2. **The corpus is data, not cache.** `mine` keeps every stored turn whose source file has gone, even with `--full`, because once a tool deletes its own copy of a conversation, nothing could bring those turns back. The exceptions are a Cursor conversation that changed, whose new turns replace its stored ones, and, on a full mine (`--full`, or any mine after `CLEAN_HASH` or `RULES_HASH` changed), any stored turn the current cleaning rules no longer admit. `mine` also applies its changes in one SQLite transaction that takes the write lock before its first read, so a crash can't leave half a corpus, and a second mine waits for the first and then works from what it wrote.
3. **Known credential formats never reach disk.** Every turn passes through `redact()` inside `clean()` before it's stored, so the corpus never holds a pasted key in a shape `SECRET_PATTERNS` recognizes, though one in an unfamiliar format is stored as typed. A new history source has to go through `admitted()` to get this. `redact()` repeats its patterns until the text stops changing, because one pass can stop at a quote inside a wrapped value such as `token=Some(\"…\")` and leave the secret after the marker. Turns brought over from an older version's files were cleaned by that version, and the next `mine` cleans them again whenever the cleaning rules have changed since.
4. **Signals see only what the user typed.** Every rule runs on `prose()`, which strips code, logs, links, paths, and pasted agent markdown first. A rule that reads raw text would count pasted logs as your habits.
5. **Analysis defaults to the human.** Queries read only turns tagged `human` unless `--origin` says otherwise, so subagent and scripted turns never inflate a rate.
6. **The scorecard compares the user with their earlier self.** Change verdicts come from the Lately and Before windows with a multiple-testing correction, card payoffs set the user's sessions with a habit against their sessions without it, and `compare` sets the span after a date against the span before it. There's no composite grade or outside benchmark. The hard gates in `skills/know-thyself/evals/JUDGE.md` fail any output that reports either.
7. **Nothing identifies the owner, and every cited source is listed once.** Sources live in `skills/know-thyself/references/sources.json`, which practices, scorecard lines, hand-over tools, and the guide's source list all draw on. The package validator enforces both, as described below.

## Where each step lives in `convo.py`

A mine and a query each run through a short chain of functions, so most changes touch one step of it.

1. **Reading.** `mine()` lists each source's files and Cursor's conversations, compares their signatures with the stored ones, and parses the changed ones with `read_codex()`, `read_claude()`, `read_pi()`, `read_opencode()`, and `read_cursor()`. `parse_file()` wraps the four file readers, so a file that raises adds no turns and counts in `files_failed` instead of stopping the mine.
2. **Cleaning.** Every turn passes through `admitted()`, which runs `unwrap()` to cut a Codex prompt down to the text after `## My request for Codex:`, then `clean()`, including `redact()`, and then `admissible()`, so a turn is redacted before anything decides whether to keep it. `unwrap()` runs only on raw turns, and `clean()` changes nothing when it runs again on a stored turn, so a full mine never cuts text out of a stored turn that quotes the marker, including one whose source file is gone.
3. **Merging.** `row_key()` finds duplicates (a turn over 100 characters by its text within a tool, a shorter one by its text and timestamp, or by its text and session when it has no timestamp) and `rank()` picks which copy wins (one that isn't a subagent's, then one with a timestamp, then the earliest timestamp, then the lowest session id), and the result is merged with the stored turns, which `readmit()` cleans again on a full mine, as it does every `--import` file.
4. **Writing.** `rewrite_turns()` on a full mine, or `update_turns()` on an incremental one, writes the turns, calling `classify()` for origin and `annotate_rows()` for each human turn's `prose()` length and signals.
5. **Querying.** Every query reads through `load()`. `score()` builds one unit per session with `session_units()` and tests the shares with `wilson()`, `newcombe()`, `two_proportion_p()`, and `bh_adjust()`. `window_change()` and `payoff()` ask `too_few()` first and skip the test for counts too small to tell, leaving no p-value, so `bh_adjust()` corrects only across the lines that were tested.

## Where each rule lives in the skill

The skill keeps each rule in one file, so changing a behavior is a one-file edit, and an agent reads only `SKILL.md`, the voice file, and the file its mode points to, plus `references/practices.md` and `references/sources.json` in coaching. All of them are under `skills/know-thyself/`.

| File | Holds |
| --- | --- |
| `SKILL.md` | The corpus, the commands, the freshness step, the mode table with the one file each mode reads, and the guardrails every mode needs, which are traced numbers, verbatim quotes, privacy, approval before live configuration, and report naming |
| `references/voice.md` | How every reply and report sounds, how to word what the numbers show, and what the coverage sentence says |
| `references/mirror.md` | Gathering, the report's sections, the reply's shape, the offers, going deeper, and the version to share, which only a mirror needs |
| `references/coach.md` | Gathering, the score JSON, choosing what to say, the before and after, the report and reply, the hand-over tools, and the Sources section, which only coaching needs |
| `references/lookups.md` | The Trend and Recall steps |
| `references/lessons.md` | The Lessons steps and the shape of its reply |
| `references/practices.md` | The practices coaching draws on, each with its sources |
| `references/sources.json` | Every source the skill cites |
| `references/signal-fixtures.jsonl` | Labeled examples for the signal rules |

The voice file and each mode's file end on a Done when list whose items a reader can answer yes or no. The lists cover what `skills/know-thyself/evals/grade.py` checks and what it can't, so a change to a behavior changes its Done when item in the same commit.

## How rule changes reach stored data

`mine` stores each human turn's signals in the corpus so queries stay fast. Two hashes decide when that stored work is stale. `CLEAN_HASH` covers cleaning, redaction, origin tagging including the `harness_patterns` in your config that `user_harness()` accepts (it skips, with a warning, any that fails to compile or matches empty text), the source parsers, the dedupe in `row_key()` and `rank()`, and how a turn is stored, through `pack()` and `key_text()`, and `RULES_HASH` covers `SIGNALS`, `prose()`, and the signal helpers. Both hash source text. `RULES_HASH` takes the `SIGNALS` patterns, the patterns `prose()` strips with, the `SHORT_REFERENCE`, `CAPS_TOKEN`, and `WORD` patterns, and the full source of `prose()`, `detect_prose()`, `plain_signals()`, `emphasized()`, `annotate_texts()`, and `emphasize()`, and `CLEAN_HASH` likewise takes the full source of `clean()`, `classify()`, the readers, and the other functions it lists. So even a comment or whitespace edit inside one of those functions forces a full re-mine, while a comment beside a `SIGNALS` pattern doesn't, because only the patterns themselves are hashed.

When either hash differs from the one stored in the `meta` table of `corpus.db`, the next `mine` re-reads every source instead of only changed ones. When `RULES_HASH` has changed, every `stats`, `score`, `compare`, and `search` until then prints `signal rules changed since the last mine; recomputing (slow). Run: convo.py mine` to stderr and recomputes signals in memory without saving them. When `CLEAN_HASH` has changed, for example after you edit `harness_patterns`, they print `turn cleaning rules changed since the last mine; the stored turns are out of date. Run: convo.py mine` and read the stored turns as they are, because only a mine cleans them again. Running `mine` once stores the current hashes, which ends both warnings.

## Test layers

### Signal fixtures

`skills/know-thyself/references/signal-fixtures.jsonl` holds one labeled example per line, with `signal`, `expect` (whether the rule should fire), and `text`. `convo.py check` runs each text through the same detection the corpus uses and fails on any mismatch. `caps_emphasis` depends on your own lowercase vocabulary, which a mine stores in `corpus.db`, so until there is one, `check` skips that signal's fixtures and says how many it skipped. The same dependence means those fixtures can pass on one machine and fail on another.

To change a rule, work in this order.

1. **Find the case.** Run `convo.py search --signal <id> --sample --limit 8` and read each hit's `match` field to find a false positive or a miss.
2. **Write the failing fixture.** Add the case to the fixtures file with the expectation you want, then run `convo.py check` and watch it fail. Use invented text, never a line from your corpus.
3. **Change the rule.** Edit the pattern in `SIGNALS` in `convo.py` until `check` passes, then run `scripts/check.sh`.
4. **Refresh the corpus.** Run `convo.py mine`, which re-reads everything because `RULES_HASH` changed.

Adding a scorecard line takes more than a rule. The entry in `SCORECARD` needs an `id` that matches a signal, a `level` of `opener` or `session`, an `area` listed in `AREAS`, a `label`, a `why` that cards print as the reason it should help, a `nudge`, `counts` with example phrases in curly quotes that its own rule detects, and `sources`, a list of ids from `references/sources.json` naming the public guides that recommend the habit. `references/practices.md` needs a practice tagged with the id. The prose that names 30 lines, in the guide, the reference, the scorecard guide, and `references/coach.md`, needs updating too.

Adding a practice to `references/practices.md` needs a source as well. End the bullet with up to three reference-style links whose ids are defined under the file's Sources heading, primary docs first, and when a source is new, add it to `references/sources.json` and to the list in `docs/know-thyself.md` in the same change, because the validator fails when the three disagree. Advice that no public guide gives is marked "(this skill's own advice)" instead of borrowing a link that doesn't say it.

### Package validator

`skills/know-thyself/scripts/validate_skill.py` prints PASS or FAIL per rule and exits 1 on any failure.

| Rule | What it guards |
| --- | --- |
| `SKILL.md` frontmatter has `name` and `description` | The skill's name and its trigger description can't go missing |
| `SKILL.md` stays within 500 words | The entry file stays short, so detail lives in `references/`, which an agent reads only for the mode it needs |
| Every backticked `references/`, `scripts/`, `evals/`, or `samples/` path in `SKILL.md` exists, and every file in `references/` is named somewhere | An agent never follows a dead route, and no reference is orphaned |
| `mirror.md`, `coach.md`, `lookups.md`, `lessons.md`, and `voice.md` each end on a Done when heading | Every mode ends its work on a checklist, which is what keeps a run from stopping early |
| Eval cases have unique ids, a known mode, a prompt, and an `expect`, any `report` they name is a known mode, and the cases cover the mirror and coach modes | The behavioral evals stay runnable, and the default mode and the opt-in coaching are always tested |
| The rewritten sample opener hits seven expected signals and the plain one hits no ambition signal | The worked example in `samples/` really demonstrates what the scorecard measures |
| Signal fixtures pass, with the `caps_emphasis` ones skipped when there's no vocabulary | Rule changes don't silently break labeled cases |
| Wilson and Newcombe intervals match known reference values, and the Benjamini-Hochberg adjustment matches a fixed expected result | The ranges and verdicts in the scorecard are computed correctly |
| The trend survives months under 10 sessions and scales to the line's peak | A line made only of quiet months prints "too few to chart" instead of failing, and the peak month gets the tallest mark |
| Every example phrase in a scorecard definition is detected by its own line | `--definitions` and cards never promise a phrase the line doesn't count |
| Every scorecard line has a `label`, a `why`, and `counts` | A card never prints an empty heading, reason, or example list |
| A credential inside a wrapped value like `token=Some(\"…\")` is fully redacted, and redacting again changes nothing | No secret tail survives after a redaction marker |
| Cleaning a stored turn that quotes the Codex marker again changes nothing | A full mine can't cut text out of turns whose source files are gone |
| A typed message opening "you have explicit approval" is kept while injected `<task-notification>` text is dropped | The injected-text filter can't silently discard your own approvals |
| `compare` survives an empty span before the date, and a card survives a habit every judged session showed | An empty side of a comparison prints a plain phrase instead of crashing the reply |
| A scorecard line with under 10 sessions in either window, or under 5 hits between them, gets no test and reads "too few to tell" | Tiny windows can't produce a confident up or down, while a line with enough data is still tested |
| A card payoff with under 5 corrected sessions between its two sides gets no test and says the counts are too few to tell | A sparse payoff can't claim a gap holds up, while one with enough data is still tested |
| A Codex file with null payloads and an object for a timestamp, a non-UTF-8 OpenCode file, parse without raising, and a reader that raises makes `parse_file()` return None | One malformed record or file costs only its own turns, never the whole mine, and each failed file is what `files_failed` counts |
| A Cursor database that can't be read makes `parse_cursor()` return None | A bad Cursor read costs only its own turns and counts in `files_failed`, never the whole mine |
| Sessions dated after today count toward no Lately window, `compare` span, or trend month | A wrong clock can't inflate the latest numbers or add a month from the future |
| A short turn repeated in another undated session is kept in both, a dated short turn copied into another session is stored once, and a dated copy outranks an undated one | Dedupe merges forked copies without folding together the same short reply from separate sessions |
| A harness pattern that fails to compile, isn't a string, or matches empty text is skipped with a warning, while a good one is kept | One bad config entry neither crashes every command nor tags every prompt as harness |
| `score` warns on stderr, naming `mine`, when the stored cleaning hash is older than the code's | Stale turns after a cleaning or `harness_patterns` change don't pass silently |
| `score`, `score --markdown`, and `stats` survive a corpus whose sessions have no timestamps | Undated history prints a null `first_session` or `date_range` and a note that the trend is empty instead of crashing |
| Every scorecard line has a tagged practice, and every practice tag names a scorecard line | Coaching advice and measurement stay linked both ways |
| No text file in `skills/know-thyself/` and no `docs/know-thyself*.md` page contains the home directory name (unless it's a generic account such as `runner` or `root`), a word from `git config user.name`, or a term from `.private-terms`, except the repository's slug from its origin remote inside an install command | The skill and its docs can be published without naming their owner |
| `docs/know-thyself.md` has a Credits section with bold names | The credit for the article behind the ambition lines stays in place |
| Every entry in `sources.json` has a unique id, a title, a publisher, and an https url | A source can't be listed twice or point at a plain-http page |
| Every link id in `practices.md` is in `sources.json`, has a definition under Sources, and that definition's url matches `sources.json` | A practice never cites a source the list doesn't have, or links it somewhere else |
| Every scorecard line has at least one source, and every one of its source ids is in `sources.json` | Coaching can always say where a habit's advice comes from |
| `coach.md` has its Tools you can hand over section, every source id a tool there lists is in `sources.json`, and every source in `sources.json` is cited by a practice, a line, or a tool | The list holds only what the skill cites |
| The list under Where the advice comes from in `docs/know-thyself.md` matches `sources.json` exactly | Readers see the same sources the skill uses |
| A rendered card has its For you paragraph and no Where this comes from line | Sources appear once, at the end of coaching, instead of on every card |

`.private-terms` sits at the repository root, is gitignored, and holds one term per line, such as an employer, product, or ticket prefix. Lines starting with `#` are comments. The identity scan covers every Markdown, Python, JSON, JSONL, text, TOML, YAML, and extensionless file under `skills/know-thyself/`, including gitignored ones, except under `.cache`, `reports`, `__pycache__`, and `.ruff_cache`, plus every `docs/know-thyself*.md` page. The repository is public under its owner's account, so the slug that `git remote get-url origin` names may appear in `npx skills@latest add <slug>` and `git clone https://github.com/<slug>.git`, and nowhere else.

### Docs check

`scripts/docs_check.py` checks every tracked Markdown file in the repository, so it covers these pages and the skill's own files too. Among its rules, it runs `convo.py <command> --help` to fail any command or flag a page names that the CLI doesn't define. [The README](../README.md#checks) owns its full rule list and its tests.

### Behavioral evals

`skills/know-thyself/evals/cases.json` holds prompts users really type, for comparing one version of the skill against another or against no skill. Each case names its mode, a prompt, and what a good answer looks like in `expect`, the mirror and coach cases name the report they should write, and the mirror cases add a time limit. `skills/know-thyself/evals/grade.py` runs the yes-or-no checks on one reply and its report, such as no persona opening, no advice or links in a mirror, the report's path before three to five quoted offers at its end, a before and after in coaching with sources only in a final Sources section, and every dated quote found in what the user typed within a day of that date, and it lists each "k of n" count the scorecard doesn't hold, all against the frozen corpus that `KNOW_THYSELF_DATA_DIR` points at. `skills/know-thyself/evals/JUDGE.md` is the protocol around them, with the hard gates, the grader, and a pairwise judge that compares old and new chat replies in both orders, checked for position bias, on questions of taste only. They need a live agent and a real corpus, so they run by hand and never in `scripts/check.sh` or CI.

## What none of these cover

- **The source parsers on real formats.** Only one small Codex file and one OpenCode file, both written to test bad input, go through the readers. No test feeds well-formed Claude Code, Pi, or Cursor history, so a format change in one of those tools shows up only as fewer turns from that tool in the `by_source` counts of `stats`. A reader that raises is counted in `files_failed`, because `parse_file()` wraps the file readers and `parse_cursor()` wraps Cursor's.
- **Mining logic.** Incremental reuse, retention of pruned turns, the merge that applies `row_key()` and `rank()`, imports, the mine lock, the move from older files to `corpus.db`, and `export` have no tests, so a regression there could lose history without failing a check. Only the key and the ranking themselves are checked, on fixed rows.
- **Origin tagging and redaction.** The harness patterns have no fixtures, including for whether a personal `harness_patterns` entry tags the turns it should, and the credential patterns have only the one wrapped-value case, so a missed secret format or a misfiled human turn passes every check.
- **Query output on real data.** `score` and `compare` run only on a few synthetic sessions built for the edge cases above, `stats` runs once, on an undated session, and `search` never runs, so a wrong number or a broken sentence on a real corpus passes. Beyond those cases, only two edge cases of the `compare` sentences and the card payoff text are rendered, on fixed inputs, along with the statistics helpers, the trend marks, and detection on fixed texts.
- **`caps_emphasis` fixtures in CI.** CI never mines, so it has no vocabulary and skips them while running the rest. Run `scripts/check.sh` locally after a mine before merging a change to `caps_emphasis` or `prose()`.
- **Whether a rule matches real habits.** Fixtures prove a rule does what its author intended on the cases written down. Only reading samples shows whether it fits how people really write.
- **Whether the docs are true.** The docs check proves that named paths, links, commands, and flags exist, but not that the prose around them is correct.
