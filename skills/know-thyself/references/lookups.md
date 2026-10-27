# Trend and Recall

Trend and Recall answer one question each. They reply in a few sentences, write no report, and coach only when asked.

## Trend

1. **Rule out a shift in mix.** Run `stats` with `--since` and `--until` on each side and compare `by_source` and `top_workspaces`, so a change in tools or projects isn't read as a change in habit.
2. **Measure.** For one habit since a date, paste `compare <habit> --since <date> --markdown` and give its verdict. For two closed periods, run `score` with `--since` and `--until` on each side and compare the habit's `all_time` shares.
3. **Confirm in their words.** Read `search --signal <id> --sample` hits from both windows and check that the change shows up in what they typed.

### Done when

- The reply gives the habit's count on both sides, as `k` of `n`, and the verdict the script gives.
- It says how a shift in tools or projects was ruled out, or that one explains the change.
- Samples from both windows were read.
- Every item of the Done when list in `references/voice.md` holds.

## Recall

Search with topic regexes and `--context 3`, narrowing by `--cwd` or dates when the request implies them. Answer in plain sentences with what was decided and on what date, then list where each decision came from (source, session id, and timestamp) as a short list under the answer.

### Done when

- Each decision has its date in the sentence, and its source, session id, and timestamp in the list under the answer.
- When decisions conflict, the latest comes first, followed by what changed.
- Every item of the Done when list in `references/voice.md` holds.
