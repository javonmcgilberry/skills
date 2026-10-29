# What to run next

Read this when the user calls the skill with nothing else to go on, as in "know thyself" or "what can you do". They're asking what to do, so lead with two or three picks for them, each with a one-line reason drawn from what `context` printed, followed by the full list of commands in `SKILL.md`. Never run a command they haven't picked.

Reason from the `context` output. There is no score to follow.

- **No mirror yet** (`latest_reports.mirror` is null): a mirror first, since every other command builds on knowing how they work.
- **A mirror older than 30 days:** a fresh mirror, which will also say what changed since that one.
- **A recent mirror and no coaching since:** coaching on the friction that mirror named, quoting its heading so they can see why.
- **A recent mirror whose friction section names a correction that repeats:** Lessons on that correction.
- **`NO_PROFILE`:** `init`, with one line on why: later runs will know their role, their audience, and what never to quote.
- **A team or lead version older than the latest mirror:** a fresh one, so what they share matches how they work now.
- **They mentioned a manager, a director, or a review:** the version for their lead in `references/audiences.md`.

Write each pick as the exact words they could paste, such as "let's do a run" or "coach me on how I verify agent work".

## Done when

- The reply leads with two or three picks, each with a reason taken from the `context` output, then lists every command.
- Nothing ran that the user didn't pick.
