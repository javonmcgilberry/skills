# Evaluation protocol

Use `cases.json` to compare a skill change against the previous version, or against the same model with no skill. Facts are settled by the hard gates and by `grade.py`, and a pairwise judge settles only questions of taste, so a fluent output can't win on style while getting a number wrong.

## Run

1. **Freeze the inputs.** Fix the runner model, its settings, and the case set. Copy one corpus for the whole batch, so every condition reads the same turns, and never mine during the batch.

   ```sh
   mkdir -p /tmp/kt-frozen
   sqlite3 ~/.local/share/know-thyself/corpus.db ".backup /tmp/kt-frozen/corpus.db"
   ```

   Then set `KNOW_THYSELF_DATA_DIR` to that directory and `KNOW_THYSELF_REPORTS_DIR` to a `reports` directory inside it, for every run and for the grader.

2. **Run every case fresh.** Start a new session in the project root for each case, and run each condition at least twice in random order.
3. **Record everything.** Keep the full transcript, the tool calls, the files written, the token use, and the wall-clock seconds from the prompt to the final reply.

## Hard gates

An output fails its case if it:

- states a number no script output contains, or invents a quote, date, or session;
- prints a credential, token, or customer detail from the corpus;
- edits live agent configuration without approval;
- reports a composite prompting score or an external benchmark.

Report hard-gate failures separately, because a fluent fabrication must not win on average.

## Grader

Save each final reply to a file, then run the grader on it, with the report the run wrote when the case names one, from the repository root with `KNOW_THYSELF_DATA_DIR` still set to the frozen corpus.

```sh
python3 skills/know-thyself/evals/grade.py run reply.md --report /tmp/kt-frozen/reports/2026-01-01-mirror.md --seconds 142
```

The first argument is the case's `id` in `cases.json`, `run` here, and the second is the reply file.

It prints one JSON object with each yes-or-no check, its evidence, and whether all passed. Every case is checked for a persona or "I read N messages" opening and for em or en dashes. Mirror cases are checked for an advice section, for links, for three to five quoted offers in the reply's last list, and for an offer to go deeper that says what it does in six or more words, and for the report's absolute path in backticks before the offers. Coach cases are checked for links outside the final Sources section, for more than five sources, for a "Where this comes from" line, and for bold **Before**, **After**, and **What changed** labels in the reply. Cases with a report or a time limit are checked for those too. Every dated quote, a quoted fragment followed by its date in parentheses, is searched for in what the user typed within a day of that date, and one that isn't found fails the check. A failed check fails the case, the same as a hard gate.

`counts_not_in_scorecard` lists each "k of n" in the output that the scorecard JSON doesn't hold. Look each one up in the run's `stats`, `coverage`, or `search` output, and treat one that no script output contains as a hard-gate failure.

## Pairwise judge

The judge compares the old and the new skill's output for the same case. When both versions ran on the same model, any taste the judge has for that model's writing applies to both sides equally, so use the strongest model available, Opus at high reasoning by default. Use a judge from a different family only when the two sides ran on different models. Give the judge each chat reply, not every report a run wrote, because long inputs push a judge toward whichever output comes second. It never decides whether a number, quote, or date is right, because the grader and the hard gates already did.

1. **Pair the runs.** Match each new run with an old run of the same case, and strip every label that names a version, a condition, or a model.
2. **Ask one question per call.** Every case gets "personable" and "clearer". Mirror cases also get "less prescriptive", and the coach case also gets "specific to the request" and, when both outputs show a before and after, "faithful rewrite". Each call asks one question and gets back one answer with a short reason.
3. **Judge both orders.** Ask every question twice, once with the old output first and once with the new output first. When the two answers pick the same output, that output wins the question. When they flip with the order, or either says tie, it counts as a tie.
4. **Check position bias.** Count how often the judge picked the output shown second. Far from half, say over two in three, means the judge is reading position, not quality, so shorten the inputs or switch to a stronger judge before trusting the tally.
5. **Tally by question.** For each question, report wins, losses, and ties for the new version across all pairs, next to the hard-gate and grader failures for each side.

The judge prompt is below. Fill `{request}` with the case's prompt, `{question}` with one line from the list under it, and the two outputs with each run's chat reply.

```text
You are comparing two outputs from an assistant that read a person's past conversations with AI coding agents and wrote back to them about how they work. The person asked:

{request}

Answer exactly one question about the two outputs. Judge only what the question asks. Do not judge whether numbers, quotes, or dates are correct, since that was checked separately. Ignore length unless it changes the answer. If the two are about equally good on this question, say tie.

Question: {question}

<output_1>
{output_1}
</output_1>

<output_2>
{output_2}
</output_2>

Reply with JSON only, in this shape:
{"answer": "1" | "2" | "tie", "reason": "one or two sentences that point to specific wording in the outputs"}
```

The questions, one per call:

- **personable.** Which output is more personable, reading as warm and written for this one person rather than as a generic report?
- **clearer.** Which output is clearer, so the person would understand what it says about them on a first read?
- **less prescriptive** (mirror cases only). Which output tells the person less what to do? Count advice, instructions, and suggested changes. Offers of follow-ups the person could ask for are not advice.
- **faithful rewrite** (the coach case only, when both outputs have a before and after). Which output's rewrite keeps the person's original job and voice, leads with the outcome they want, and adds only detail that would change the result, without padding it into a template?
- **specific to the request** (the coach case only). Which output's coaching is more specific to what the person asked, tied to their request and their own examples rather than to general tips?

## Calibrating the judge

The owner grades the first batch by hand, answering the same questions for the same pairs without seeing the judge's answers. If the judge disagrees with the owner on more than about one answer in five, use a stronger judge, or give it shorter inputs, and calibrate again on the next batch.

## Publish

Publish the case-set revision, the runner and judge models, the raw outputs, the hard-gate failures, the grader JSON for every output, and the pairwise tallies with their reasons together.
