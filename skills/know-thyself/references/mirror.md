# Mirror

A mirror reflects how the user works, from what they typed, so it describes and gives no advice. It covers how they work, what they're good at, where friction shows up, and what's changed, each as a pattern backed by a traced count and a verbatim dated quote. Cards, the scorecard, next steps, and links belong to Coach, so a mirror leaves them to an offer. A default run reads about 150 turns and finishes in under three minutes.

## Gather

1. **The numbers.** Run `stats` for the date range, turns per tool, turn and session length, working hours, the most used skills, and the busiest workspaces, and `coverage`. Run `score` and read `late_constraints` and `teach_once`, as `references/voice.md` explains them.
2. **The person.** Read about 120 recent turns with `search --since <90 days ago> --sample --limit 120 --chars 500`, and about 30 around corrections with `search --signal agent_rework --sample --limit 30 --context 2`, yourself. Note what recurs in their own words, such as how they start work, what they correct, what they care about, and how they talk to agents.
3. **The check.** Keep a pattern only when what you read and the counts agree, and every rate behind it passed the eight-sample check in the guardrails. Take a pattern's session count from the `sessions` field on the first line `search` prints, which counts every match, since `--limit` caps the hits shown.
4. **What changed.** Find the latest earlier mirror report in the reports directory, named `*-mirror.md`, or `*-profile.md` when an older version wrote it, and compare its themes with what you found now. Compare rates only with reports made by the same `convo.py` rules.

## The report

Write `YYYY-MM-DD-mirror.md` with these sections in order.

1. **The short version.** One sentence that captures how they work in a plain image, then their strongest pattern and where friction shows up most, each as a bold lead sentence with two or three sentences of evidence.
2. **How you work.** Three to five paragraphs on their working style, each a pattern with its evidence, using what `stats` shows about rhythm, tools, and session shape.
3. **What you're good at.** Three to six strengths.
4. **Where friction shows up.** Three to six places where work slows or needs correcting, described as what happens and when, using `late_constraints` and `teach_once` counts where they fit.
5. **What's changed.** Themes compared with the latest earlier report, and any habit `score` marks up or down, in plain words. With no earlier report, say this is the first one.
6. **What this covers.** Plain sentences on coverage, as `references/voice.md` describes it, and on what was set aside and why.
7. **Where you could go from here.** The offers below, as the report's last list.

## The reply

Build the chat reply to scan, in this order.

1. **One opening sentence** that captures how they work in a plain image, like "You work with agents like a lead engineer running a fast team you don't fully trust yet."
2. **What you're good at** and **Where friction shows up**, each a bold lead sentence followed by two or three sentences with a count or a dated quote behind them. Add **What's changed** the same way when something rose or fell.
3. **Where the full report is**, as its own short paragraph that gives the report's absolute path in backticks, starting from `/` with `~` expanded so it opens with a click, names what it holds that the reply doesn't, and offers to show any part of it here. For example, "Your full report is saved at `/home/ana/.local/share/know-thyself/reports/2026-01-05-mirror.md`. It adds how your week and tools break down and more of your own words, and I can show any section here if you'd rather not open it."
4. **The offers**, introduced with "You can also ask me:", the same ones the report ends with, followed by one plain sentence on coverage, as `references/voice.md` describes it, written as prose so the offers stay the reply's last list.

## Offers

Write three to five follow-ups the user could paste, drawn from what this run found for this person. Each is one list item that opens with the quoted request, in this shape.

```markdown
- "<What they'd ask, naming a finding from this run>: <the pattern behind it, in their words>."
```

Draw them from these kinds, naming the finding, habit, topic, or correction this run turned up.

- Coaching on a named finding, which runs Coach.
- A trend check on a named habit since a date, which runs Trend.
- Recall on a topic that came up while reading, which runs Recall.
- Lessons for a correction that repeats across sessions, which runs Lessons.
- Going deeper, worded to say what it reads, like `- "Go deeper" and I'll read your whole history, not just the last few months.`
- "Make a version I can share", which writes the shareable version below.

## Go deeper

When the user asks to go deeper, read 300 or more human turns across the whole history with `search --sample --limit 300 --chars 400`, split across Haiku subagents that each take one search slice and one question and return recurring patterns with dated quotes. For each candidate pattern, pull confirming and disconfirming turns with `--signal` or `--regex` searches and `--context 2`, and keep it only when both hold up. Write the result as a new mirror report and reply in the shape above.

## A version to share

Make it only when asked, for example "make a version I can share". Gather as above if no mirror report from today exists, then write `YYYY-MM-DD-shareable.md`.

It covers their working style in a few paragraphs, what they're good at, the tools and workflow they use day to day, and what's changed, in general terms. It leaves out quotes, ticket and repo names, and coworkers' names, and leaves out friction unless the user names what they're happy to share. It closes with a short note that the skill reads their own history on their machine and that its advice comes from the public guides listed in the "Where the advice comes from" section of the know-thyself guide.

The reply gives the path and says the user should read it and edit anything they'd rather keep private before anyone else sees it.

## Done when

- The report is a new `YYYY-MM-DD-mirror.md` with the seven sections in order.
- A default run finished in under three minutes.
- The reply opens with one sentence about how they work, then what they're good at and where friction shows up.
- Every pattern passed the check in Gather, and its session count is a search's `sessions` field.
- The reply gives the report's absolute path in backticks before the offers.
- The reply and the report end with the same three to five offers, each one list item opening with a quoted request drawn from this run.
- The go-deeper offer says what it reads.
- The reply's coverage sentence comes after the offers, as prose.
- Neither the reply nor the report holds advice, a card, the scorecard, or a link.
- A version to share is written only when asked, and its reply tells the user to read and edit it before anyone else sees it.
- Every item of the Done when list in `references/voice.md` holds for the reply and the report.
