# What to run next

Read this when the user calls the skill with nothing else to go on, as in "know thyself", or asks what it can do. Lead with two or three picks for them, each with a one-line reason drawn from what `context` printed, then show What you can do below. Never run a command they haven't picked.

## Picks

Reason from the `context` output. There is no score to follow.

- **No mirror yet** (`latest_reports.mirror` is null): a mirror first, since every other command builds on knowing how they work.
- **They mention a new model:** a fresh mirror, since habits built for an older model are what to look for.
- **A mirror older than 30 days:** a fresh mirror, which will also say what changed since that one.
- **A recent mirror and no check-in in the last 14 days:** a check-in on what moved lately.
- **A recent mirror and no coaching since:** coaching on the friction that mirror named, quoting its heading so they can see why.
- **A recent mirror whose friction section names a correction that repeats:** Lessons on that correction.
- **`NO_PROFILE`:** `init`, with one line on why: later runs will know their role, their audience, and what never to quote.
- **A team or lead version older than the latest mirror:** a fresh one, so what they share matches how they work now.
- **They mentioned a manager, a director, or a review:** the version for their lead in `references/audiences.md`.

Write each pick as the exact words they could paste.

## What you can do

Show this list as written, after the picks, so they can see everything in one place.

- **"Tell me about myself"** or **"let's do a run"**: a portrait of how you work, what you're good at, where friction shows up, and what's changed, from your own conversations.
- **"How have I been doing the last two weeks?"**: a check-in on what moved lately against your own longer record.
- **"Coach me on how I start tasks"**: coaching on the part of your work you name, with one of your real prompts rewritten.
- **"Has delegating changed since August?"**: whether one habit changed after a date, with counts on both sides.
- **"What did I decide about flaky tests?"**: what you said or decided about a topic, with when and where.
- **"Stop me repeating the same correction"**: rules, checks, or instruction lines drafted from corrections you keep making, applied only if you approve.
- **"Make a version I can share"** or **"Help me explain how I work to my lead"**: a first-person write-up for your team or your manager, with nothing private in it.
- **"Set me up"**: a short interview that saves who you are, who reads what, and what never to quote, so every later run knows.

Everything is read from the history on this machine, and nothing leaves it unless you share a write-up yourself.

## Done when

- The reply leads with two or three picks, each with a reason taken from the `context` output, then shows What you can do.
- Nothing ran that the user didn't pick.
