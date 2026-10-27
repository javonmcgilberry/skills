# Coach

Coach runs only when the user asks for it, with requests like "coach me on how I start tasks", "how can I get better at reviewing", or "score my prompts". Everything it says bears on what was asked, so a finding outside the request stays out, however striking it is.

Every step and every change in the rewrite rests on a practice in `references/practices.md`. Look up the practice for each habit, card, or step by the habit's backticked id, such as `outside_judge`, or by its numbered section. Suggest only what a practice supports. When the user asks for something a practice advises against, even often, offer the practice's version instead, so an open-ended "keep going until it's all done" becomes "keep going until this check passes".

## Gather

1. **The numbers.** Run `score` for the JSON, and `stats` and `coverage` for coverage, as `references/voice.md` describes it.
2. **The person.** Read about 120 recent turns with `search --since <90 days ago> --sample --limit 120 --chars 500`, adding a `--regex` or `--signal` filter when the request names one part of their work, and 30 more with `--context 2` around corrections (`--signal agent_rework`). Note what recurs in their own words about the part of their work they asked about, such as how they start tasks, what they correct, and how they talk to agents.
3. **The proof.** Run the eight-sample check in the guardrails on each habit you plan to mention.

## What the score JSON holds

- **`windows`** holds Lately (the last 60 days) and Before (the 180 days before that), each with its session count.
- **`dimensions`** holds each habit's `label`, what it `counts`, its `level` (`opener` looks at the first message of eight or more words, `session` at every turn), `lately` and `before` as `k` of `n` with a 95% range (`low`, `high`), the `change` in points with its range and a `verdict`, six months of `monthly` counts, and two recent examples. The verdicts are up, down, maybe up, maybe down, no clear change, and too few to tell, and up and down survive the correction for checking every tested habit at once. Too few to tell comes with no points or range, because a window had under 10 sessions or the two had under 5 hits between them. `change` is null when a window has no sessions at all, so say there's nothing to compare yet.
- **`late_constraints`** and **`teach_once`** read as `references/voice.md` explains them.
- **`recent_plain_openers`** holds recent first messages to rewrite as a worked example.

## Choose what to say

- **Strengths.** Habits with high Lately counts, anything marked up or maybe up, and patterns you saw while reading that the numbers don't capture.
- **Growth.** Anything marked down or maybe down, habits that matter for their work and are confidently rare (a high end of the range near zero, like 0 of 150, shown as a range of 0 to 2%), the constraints that most often arrive late, and the teach-once share. Prefer what you saw in their words over what only a rate shows.
- **Cards.** At most three habits that bear on the request, rendered with `score --cards <id>,<id>`. Pick the ones tied to their corrections or to what you saw while reading, and prefer habits whose payoff for them holds up or hints at a gap over habits with no data or too few to tell. Give cards only to habits their work needs. Paste `score --markdown` with all 30 habits only when they ask for it, as in "show me all the habits".
- **Next steps.** Tie each step to one of those findings, draw its practice from `references/practices.md`, and hand over a tool from the list below when it fits. Raise the outcome, the standard, or the perspective rather than the size.
- **Lessons.** When most repeated corrections never became rules, offer to run Lessons and name the correction you'd start with.

## The before and after

Every coaching run shows one of their real first messages next to a better version of it, so the advice lands on their own words.

1. **Pick the prompt.** Choose a recent first message that bears on what they asked, from `recent_plain_openers` or from your reading. Prefer an ordinary one over their best brief. Quote it verbatim, cut to about 60 words if longer, with other people's names removed as well.
2. **Rewrite it.** Keep the same job and their voice. Make it as long as it needs to be and no longer, usually a few sentences.
3. **Check every change against the guidance.** Test each change against these rules from `references/practices.md`, and drop any change no rule supports.
   - It leads with the outcome they want, and lists steps only when the process itself matters ("Lead with the outcome").
   - It adds only detail that changes the result, with no template filled in for its own sake ("Add detail only when it changes the answer").
   - It says what done looks like, so the agent can check its own work and knows when to stop ("Done-check", "Define done before it starts").
   - It uses always, never, and must only for rules that truly can't bend, and states each boundary once ("Save absolute words for real invariants").
   - It names the boundaries that matter, which are scope, what must stay unchanged, and how far the agent may go ("Constraints").
   - It asks for the fuller version by name, with the specifics, only when they wanted more than the smallest thing that works ("Method").
   - It adds nothing on Anthropic's list of old advice, so no capitals or IMPORTANT for emphasis, no "think hard", no bare "keep going until done", and no "you are an expert" label ("Method", "Write rules plainly").
4. **Say what changed.** Two to four bullets, each naming one change and why it helps, in plain words, with the practice it applies.

## The report

Write `YYYY-MM-DD-coach.md` with these sections in order, scoped to what was asked.

1. **The short version.** Two short paragraphs on what their conversations show about what they asked, the strongest thing they already do there, and the one change that would help most.
2. **What this covers.** One sentence on coverage.
3. **What's working.** Two or three strengths that bear on the request.
4. **What gets in the way.** Two or three, the same way.
5. **The habits that matter here.** The cards, pasted unchanged, each followed by one sentence that ties it to something you saw in their turns. When they ask to see all the habits, paste `score --markdown` after the cards.
6. **Before and after.** The quoted message under a bold **Before**, the rewrite under a bold **After**, then **What changed** with its bullets.
7. **What to try next.** Numbered, most valuable first, three at most. Each item names the problem it fixes, the habit or tool, and how to start tomorrow, as an if-then plan in their words. When a template fixes a measured problem, hand it over in a code block, written for this person. End every item with one line, `**Why:**` plus one plain sentence on the mechanism that names no source. Close by saying they can ask later whether it helped since today, which `compare` answers.

   ```markdown
   **Why:** A check the agent can run lets it stop when the work passes instead of when it looks done.
   ```

8. **Sources**, as the section below describes.

## The reply

The chat reply is the coaching itself. It opens straight with what you found about what they asked, gives one sentence per card with its numbers, then the before and after under the same bold **Before**, **After**, and **What changed** labels as the report, then the next steps, each with its if-then plan and its plain **Why:** line. It ends with the same `## Sources` section as the report, then the report's path.

## Tools you can hand over

Hand one over only when the evidence shows the problem it solves. Each tool lists the ids in `references/sources.json` of the guides it comes from.

- **A task contract** for constraints that arrive late. Outcome, how to reproduce, source of truth and branch, allowed scope, what must stay true, non-goals, proof required, how far the agent may go. Sources: `oai-codex-bp`, `oai-prompting`, `anth-cc-best-practices`.
- **A correction format** for heated or repeated corrections. What I saw, what rule it broke, the smallest change I want, what not to touch, how you'll prove it. The format is this skill's own. The guides it builds on say to ask for the specific change you want and to fold what you learned into one new prompt. Sources: `oai-prompting`, `anth-cc-best-practices`.
- **A state ledger** for long sessions. Branch, allowed files, current theory, verified facts, open risks, last passing check, next step, updated at each milestone. Sources: `anth-prompting-bp`, `anth-context-eng`, `oai-codex-bp`.
- **An evidence receipt** for "are you sure" loops. Verified now, inferred, not checked, changed. Sources: `anth-cc-best-practices`, `oai-prompting`.
- **A deeper brief** for work worth doing well. Ask what a top practitioner would do that you didn't ask for, what raw material they'd start from, which tools they'd use, and what outside check would prove it. Then rewrite the request to ask for that, better rather than bigger. Sources: `felix-ambitious`.
- **A rule, skill, or hook** for a correction repeated across sessions. Draft the exact line or file. Sources: `oai-codex-bp`, `anth-cc-best-practices`, `pstack-encode-lessons`.

## Sources

The reply and the report link sources in one place, their final section, headed `## Sources`. It lists at most five entries, only sources a step or the rewrite relied on, taken from the practice each one applies in `references/practices.md`, the habit's `sources` in the `score` JSON (cards print none), or the tool it hands over, each cited by that practice, habit, or tool, with its title and link copied from `references/sources.json`. Each entry is one list item with the linked title and one line on what it says and which step relied on it.

```markdown
## Sources

- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices). Says to give the agent a check it can run, which the first step relies on.
```

## Done when

- The report is a new `YYYY-MM-DD-coach.md` with the eight sections in order, and every finding in it and the reply bears on what was asked.
- At most three cards, pasted unchanged, each tied to something seen in their turns, and every habit mentioned passed the eight-sample check.
- The reply shows one real first message, verbatim, under a bold **Before**, the rewrite under a bold **After**, and two to four bullets under a bold **What changed**, and every change in the rewrite passes a rule in step 3 of the before and after.
- At most three next steps, each tied to a finding, with an if-then plan and a `**Why:**` sentence, and each resting on a practice in `references/practices.md`.
- Sources, linked or named, appear only in the final `## Sources` section of the reply and the report, which lists at most five entries, each cited by the practice, habit, or tool a step or the rewrite relied on, with its title and link from `references/sources.json`.
- Every item of the Done when list in `references/voice.md` holds for the reply and the report.
