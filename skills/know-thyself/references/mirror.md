# Mirror

A mirror reflects how the user works, from what they typed, so it describes and gives no advice. It covers how they work, what they're good at, where friction shows up, and what's changed, each as a pattern backed by a traced count and a verbatim dated quote. Cards, the scorecard, next steps, and links belong to Coach, so a mirror leaves them to an offer. A default run reads about 150 turns and finishes in under three minutes.

## Gather

1. **The numbers.** Run `stats` for the date range, turns per tool, turn and session length, working hours, the most used skills, and the busiest workspaces, and `coverage`. Run `score` and read `late_constraints` and `teach_once`, as `references/voice.md` explains them.
2. **The person.** Read about 120 recent turns with `search --since <90 days ago> --sample --limit 120 --chars 500`, and about 30 around corrections with `search --signal agent_rework --sample --limit 30 --context 2`, yourself. Note what recurs in their own words, such as how they start work, what they correct, what they care about, and how they talk to agents. Look past how they write prompts to how they plan, review, decide, and recover when something goes wrong, so the mirror shows the whole engineer.
3. **The words.** Note the compact words they reach for, terms that carry a whole instruction, like "tautological" or "source of truth". Start from `search --regex '<the pattern below>' --sample --limit 40 --chars 300`, add any shorthand of their own that recurred in step 2, and keep a word only when they typed it themselves rather than pasted it and it passes the check in step 4.

   ```text
   \b(tautolog\w*|invariants?|load[- ]bearing|blast radius|idempoten\w*|irreducible|essential complexity|chesterton|first principles|steel ?man\w*|pre-?mortem|(one|two)[- ]way doors?|goodhart|mise en place|yak[- ]shav\w*|bikeshed\w*|foot ?guns?|code smells?|north star|source of truth|paved path|golden path|escape hatch\w*|happy path|leaky abstraction\w*|ubiquitous language|separation of concerns|least privilege|defense in depth)\b
   ```

4. **The check.** Keep a pattern only when what you read and the counts agree, and every rate behind it passed the eight-sample check in the guardrails. Take a pattern's session count from the `sessions` field on the first line `search` prints, which counts every match, since `--limit` caps the hits shown.
5. **What changed.** Find the latest earlier mirror report in the reports directory, named `*-mirror.md`, or `*-profile.md` when an older version wrote it, and compare its themes with what you found now. Compare rates only with reports made by the same `convo.py` rules.

## The report

Write `YYYY-MM-DD-mirror.md` with these sections in order.

1. **The short version.** One sentence that captures how they work in a plain image, then their strongest pattern and where friction shows up most, each as a bold lead sentence with two or three sentences of evidence.
2. **How you work.** Three to five paragraphs on their working style, each a pattern with its evidence, using what `stats` shows about rhythm, tools, and session shape. One paragraph says what they seem to care about most, in their own words, and one names the words they lean on when any held up in the words step of Gather.
3. **What you're good at.** Three to six strengths.
4. **Where friction shows up.** Three to six places where work slows or needs correcting, described as what happens and when, using `late_constraints` and `teach_once` counts where they fit.
5. **What's changed.** Themes compared with the latest earlier report, and any habit `score` marks up or down, in plain words. With no earlier report, say this is the first one.
6. **What this covers.** Plain sentences on coverage, as `references/voice.md` describes it, and on what was set aside and why.
7. **Where you could go from here.** The offers below, as the report's last list.

## The reply

Build the chat reply to scan, in this order.

1. **One opening sentence** that captures how they work in a plain image, like "You work with agents like a lead engineer running a fast team, setting the bar and checking the work before it ships."
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
- "Make a version I can share" or "Help me explain how I work to my lead", which write the versions in `references/audiences.md`.
- "Set me up", only when `context` printed `NO_PROFILE`, which runs Init so later runs know who they are.

## Go deeper

When the user asks to go deeper, read 300 or more human turns across the whole history with `search --sample --limit 300 --chars 400`, split across Haiku subagents that each take one search slice and one question and return recurring patterns with dated quotes. For each candidate pattern, pull confirming and disconfirming turns with `--signal` or `--regex` searches and `--context 2`, and keep it only when both hold up. Write the result as a new mirror report and reply in the shape above.

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
- Every item of the Done when list in `references/voice.md` holds for the reply and the report.
