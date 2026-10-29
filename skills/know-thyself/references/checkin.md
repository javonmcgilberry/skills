# Check-in

A check-in looks at the last two weeks against the user's own longer record, the way a fortnightly one-on-one with themselves would. Like the mirror it describes and gives no advice. Unlike the mirror it's short, it runs often, and it answers one question: what moved lately. The mirror's own "What's changed" compares one portrait with the last; a check-in compares a fortnight with the months before it.

## Gather

1. **The window.** Run `stats --since <14 days ago>`. With 10 or more sessions, use 14 days. With fewer, use 30 days and say so in the reply, and with fewer than 10 in 30 days, say there's too little recent work to compare and stop there.
2. **The comparison.** Run `score --recent-days <the window> --baseline-days 180`. Each habit's `change.verdict` says what moved. Keep only habits marked up or down, and run the eight-sample check in the guardrails on each before it backs a claim. Habits marked maybe up or maybe down are worth one sentence, worded as `references/voice.md` says.
3. **The moments.** For each habit that moved, read `search --signal <id> --since <window start> --sample --limit 8` and pick the one turn that shows it best, quoted with its date. Read about 30 more recent turns with `search --since <window start> --sample --limit 30 --chars 400` for anything the counts don't capture, such as a new tool, a new kind of work, or a run of corrections.
4. **The last check-in.** Read the newest `checkin` report `context` printed, if any, and note what held, what slipped back, and what's new since.

## The report

Write `YYYY-MM-DD-checkin.md` with these sections in order.

1. **The short version.** One sentence on how the fortnight went, then the clearest move up and the clearest move down, each with its count on both sides.
2. **What moved.** Each habit marked up or down, as a short paragraph with both counts, the verdict in plain words, and its dated quote.
3. **What held.** In a sentence or two, the strengths from the latest mirror that are still there.
4. **In your words.** Two or three dated quotes from the window that show the fortnight, each with a sentence on what it shows.
5. **Since your last check-in.** What held, what slipped back, and what's new. With no earlier check-in, say this is the first one.
6. **What this covers.** The window, the sessions in it and in the baseline, and coverage as `references/voice.md` describes it.

## The reply

A few short paragraphs: the opening sentence, what moved up and down with one count and one quote each, the report's absolute path in backticks, and at most two offers, such as coaching on something that slipped or a trend check on something that moved. End with one plain sentence on the window and coverage.

## Done when

- The report is a new `YYYY-MM-DD-checkin.md` with the six sections in order.
- The window is 14 days, or 30 when 14 held fewer than 10 sessions, and the reply says which.
- Every habit said to move carries the verdict `score` gave, its counts on both sides, and passed the eight-sample check.
- The reply has at most two offers and no advice.
- Every item of the Done when list in `references/voice.md` holds.
