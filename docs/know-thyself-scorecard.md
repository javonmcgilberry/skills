# Reading the scorecard

Reading what `convo.py score --markdown`, `score --cards`, and `compare` print comes down to what each cell counts and how sure it is, which is how you tell a real change from noise, whether you read your own numbers or an agent quotes them in a mirror or coaching report. Flags and defaults are in [the reference](know-thyself-reference.md).

The scorecard compares you with your earlier self and nothing else. It never grades you against other people or an outside target, and it calls a habit up or down only after the change holds up against chance.

Each line, in the column headed **Habit that helps**, is a habit that the public guides listed in [the guide](know-thyself.md#where-the-advice-comes-from) recommend, so higher is better. The cells count how often you showed it, which is what the first bullet under **How to read this** in the printed scorecard says too.

## What gets counted

**A session** is one conversation in one tool, identified by its source and session id. By default only turns tagged `human` count, so subagent threads and scripted prompts stay out. Every tool counts, Cursor included, because each Cursor message carries its own time, or a stand-in that keeps Cursor's order, so the first message and the turns after it can be told apart. Turns over 2,000 words are dropped as pasted material. A turn over 100 characters whose exact text already appeared in the same tool is stored once, keeping a copy that isn't a subagent's, then one that has a time, then the earliest, so a long brief you paste unchanged into several sessions counts only toward the first. A shorter turn is merged only with a copy in the same tool at the same time, so a conversation forked with its timestamps keeps one copy, and a shorter turn with no time is merged only within its own session, so an undated "go ahead" typed in two sessions counts in both.

**The first message** is the first turn in the session with at least eight words left after code, logs, links, and paths are stripped. A session with no such turn isn't counted at all, so a conversation made only of "yes" and "go ahead" never dilutes your rates. The date of that first message decides which window the session falls in.

Lines marked * look only at the first message, because they measure how you brief (naming the goal, the scope, the finish line), and a brief only helps if it comes first. The other lines look at everything you typed in the session, because habits like asking for proof or rewinding a bad turn happen mid-conversation. Either way a session counts once toward a line, no matter how many times you said the thing.

## Lately and Before

**Lately** covers the last 60 days up to today, counted back from today in UTC. **Before** covers the 180 days before that. A session dated after today, which only a wrong clock produces, counts toward neither window. `--recent-days` and `--baseline-days` change the lengths. Both windows are anchored to today, and `--since` and `--until` only drop turns dated outside them, so a session that crosses a filter date is scored from its turns inside the range, and running `score --until` with a date more than 60 days ago leaves Lately empty and every Change cell reads "not enough data". To ask whether one habit changed after a date, use [`compare`](#checking-a-change-with-compare). To compare two closed periods, run `score` twice with `--since` and `--until` on each side and compare the `all_time` share of each line in the JSON.

## Counts and 95% ranges

Each Lately and Before cell reads as count, rate, and range. The cell below is an example with invented values.

```text
31 of 140, 22% (16-30%)
```

That means 31 of 140 sessions showed the habit, which is 22%, and the true rate behind these counts plausibly sits anywhere from 16% to 30%. The range is a Wilson score interval, which stays honest near 0% and with small counts, where a plain percentage misleads. A cell of "0 of 140, 0% (0-3%)" says the habit is confidently rare, while "0 of 6, 0% (0-39%)" says almost nothing. Read the range before the rate. A window with no sessions prints "no sessions".

## Change

The Change cell gives the difference in points between the Lately and Before rates, with a 95% range for that difference. The cell below is an example with invented values.

```text
maybe up 8.5 pts (+1.3 to +16.6 pts)
```

The verdict comes from a two-proportion test on each line with enough data, and then a Benjamini-Hochberg correction across those lines, up to all 30, because checking that many habits at once would otherwise turn up a "significant" change or two by chance alone. A line is left out of both when either window has fewer than 10 sessions or the two windows have fewer than 5 sessions between them that showed the habit, because counts that small can't tell a real change from noise.

- **up** or **down** means the change survives the correction, with an adjusted p-value under 0.05.
- **maybe up** or **maybe down** means it would pass on its own (p under 0.05) but not across all the tested lines. The example above is one of these, which is why its range excludes zero while the verdict still hedges. The range isn't corrected, and the verdict is.
- **no clear change** means it doesn't pass even on its own.
- **too few to tell** means the line was left out of the test, so the cell has no range and the JSON has no p-value.
- **not enough data** means one of the windows has no sessions.

Only up and down are firm enough to say "this rose" or "this fell". For a maybe, say it might be rising or falling and that the data can't confirm it yet.

## Trend

The trend shows one mark per month for the last six months that have sessions, up to the current month (`--trend-months` changes that), so a month after the current one, which only a wrong clock produces, gets no mark. Each mark is the month's rate scaled against the highest monthly rate on that line, from ▁ up to █, so a line's peak month is always █ even if the habit is rare. A month with under 10 sessions prints · instead of a guess. The line prints "too few to chart" when fewer than 5 sessions across the shown months show the habit, or when no month with 10 or more sessions shows the habit. The trend below is an example with invented values.

```text
▄·▆▆▇█
```

## Why there is no best month

A single month holds a few dozen sessions, so its rate swings a lot by chance. Picking the best of six such months picks the luckiest one, and measured against that, almost every later month looks like a decline even when nothing changed. So the scorecard bases every verdict on two long windows and their ranges, and uses months only for the trend marks, where a quiet month shows as · rather than a number.

## Why counts are a floor

Every line is a set of word patterns run against what you typed, after code, logs, links, paths, and pasted agent text are removed. If you do the thing in words the patterns don't know, it doesn't count, so a low count means "rarely in these words", and a zero isn't proof you never do it. Patterns can also match by accident. Before a rate backs a claim, read a sample with `convo.py search --signal <id> --sample --limit 8` and check each hit's `match` field. `score --markdown --definitions` lists the example phrases behind every line and links the guides each line comes from.

## The two tables after the scorecard

Both tables cover every session the filters allow, including sessions outside the two windows.

**Things you add after the agent has started.** For four constraints (scope, how you'll know it worked, what proof you want, and how far the agent can go), each row counts the sessions where the constraint came up in the first message or after it, and how many of those added it only after the first message. A high share means you tend to discover that constraint mid-task, which is the case for putting it in the first message.

**Teach once.** Of the sessions where you repeated a correction, this counts how many also asked for a lasting rule, such as an instructions file line, a skill, a hook, or a lint. A low share means corrections keep getting retyped instead of encoded.

## Habit cards

`score --cards outside_judge,scope_control` prints one card per line id instead of the tables, which is what a coaching reply quotes. Coaching shows at most three cards, picked for what you asked about, and pastes the full 30-line scorecard only when you ask to see all the habits. A mirror shows no cards and no scorecard, because it describes how you work in its own words.

Each card says what the habit is, with the line's example phrases, why it should help, and what your history shows. Cards don't print sources. The guides behind each line stay in the `sources` field of the JSON, with titles and links in `skills/know-thyself/references/sources.json`, and a coaching reply lists the ones its suggestions relied on in a Sources section at the end. The **For you** paragraph gives the Lately and Before counts from the scorecard, with the Change verdict in plain words, so up reads "a confirmed rise", maybe up reads "might be rising, not confirmed yet", and so on.

Cards for lines marked * add how often the agent needed correcting later in sessions whose first message showed the habit, against sessions whose first message didn't. A session counts toward this only when at least two turns follow its first message, and it counts as corrected when a later turn reads like a correction or a repeated instruction (the `agent_rework` and `repeated_constraint` signals). It uses every session the filters allow, not the two windows. When fewer than 10 such sessions showed the habit, the card says too few of your sessions opened that way to tell, and when every judged session showed it, the card says there's nothing to compare it against. When fewer than 10 didn't show it, or the two sides have fewer than 5 corrected sessions between them, the card gives both rates and closes with "Those counts are too few to tell.", because the test leaves that line out by the same rule as the Change cell. Otherwise the closing words come from a two-proportion test with a Benjamini-Hochberg correction across the lines marked * that were tested, as follows.

- **"That difference holds up, but it shows a link, not that the habit caused it."** means the gap survives the correction.
- **"That's a hint, not proof, and it would show a link, not that the habit caused it."** means it would pass on its own but not across all the tested lines.
- **"That gap could be chance."** means it doesn't pass even on its own.

The card says link and not cause because the sessions where you name a finish line may be different work from the ones where you don't, so the work itself could explain the gap.

## Checking a change with `compare`

`compare <habit> --since <date>` answers "did this help since I started doing it". It sets the sessions from that date through today, leaving out any dated after today, against the same number of days just before it, never fewer than 30, and reports two rows, one for how often the habit showed (in the first message, for lines marked *) and one for how often the agent needed correcting later, counted as in the cards. It always reads human turns from every tool. The output below is an example with invented values.

```text
**Say how you'll know it worked, since 2025-04-01.**

Since then, you did it in your first message in 14 of 48 sessions (29%, range 18-43%), against 7 of 70 sessions (10%, range 5-19%) in the 45 days before (up).

The agent needed correcting later in 11 of 30 sessions (37%, range 22-54%) since, against 19 of 44 sessions (43%, range 30-58%) before (no clear change).
```

Each row is tested on its own, with no multiple-testing correction. That suits one habit you picked before looking, but it also means an up here rests on the same test that the scorecard, checking up to 30 lines at once, might only call maybe up.

- **up** or **down** means the change passes a two-proportion test (p under 0.05).
- **too few to tell** means fewer than 10 sessions across both spans showed it.
- **too early to tell** means it doesn't pass and the span since the date has fewer than 20 sessions, or one span has none.
- **no clear change** means it doesn't pass with 20 or more sessions since the date.

## How this differs from `stats`

`stats` reports plain percentages, mostly per turn, with no ranges and no test, so its numbers describe levels and never support "rising" or "falling". Use `score` for anything about change.
