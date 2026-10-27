# Lock In and Brrr

Lock In figures out what you're actually building. Brrr builds it.

They work well together, but you don't have to use both every time. If the request is already clear, start with Brrr. If a product or technical decision could send the work in a different direction, start with Lock In.

## Choose the starting point

Start with Lock In when the request still leaves room for different product behavior, architecture, scope, or definitions of done. It reads the relevant code and evidence, then asks about one meaningful decision at a time. Even when the answer looks obvious, it checks its interpretation with you before writing the final brief.

```text
uncertain request -> Lock In -> approved brief -> Brrr -> verified implementation
```

Start with Brrr when the request, ticket, plan, or specification already says what needs to change and how you'll know it works.

```text
clear request -> Brrr -> verified implementation
```

Sometimes a clear task stops being clear once the code is open. Brrr can make routine implementation decisions, but it pauses and returns to Lock In if a discovery would change the approved scope, architecture, behavior, or definition of done.

Lock In keeps the resulting brief in draft until you approve the whole thing. Answering one of its questions settles that decision; it does not approve the brief for you.

## How Lock In was tested

The Lock In eval runs the same four requests against the version before mandatory checkpoints and the current skill. The cases cover a fully specified edit, an ambiguous cleanup request, a request whose facts are already available, and a publication decision with real safety consequences.

The current skill scored 100 out of 100 on all four cases. The earlier version averaged 85. The grader checks for one direct question, an explicit recommendation, evidence from the case, and the absence of a completed brief before confirmation.

```sh
cd evals/lock-in
npm test
npm run validate
npm run eval -- --run-id <new-run-id>
npm run grade -- --run-id <new-run-id>
```

[Read the rubric](../evals/lock-in/rubric.md) or [see the completed A/B result](../evals/lock-in/results/lock-in-checkpoint-ab-2026-07-31-v2/result.md). This is a focused behavior check, so a new model or a different class of task should get a fresh run before changing the skill around it.

## How Brrr was tested

The Brrr routing eval covers six boundaries: clear work, an unapproved brief, a discovery that changes the contract, an ordinary implementation choice, work that has grown beyond one lightweight agent, and implementation without publication permission.

Both the initial and current skills scored 100 out of 100 in the completed routing run. The current wording makes those boundaries explicit, but this run shows preserved behavior rather than an improvement over the initial version.

The end-to-end case starts with an approved brief and a failing test in a small fixture repository. Brrr reproduced the failure, fixed the code, passed the focused test, updated the brief with compact evidence, and left the changes uncommitted. It scored 100 out of 100.

```sh
cd evals/brrr
npm test
npm run validate
npm run eval -- --run-id <new-routing-run-id>
npm run grade -- --run-id <new-routing-run-id>
npm run e2e -- --run-id <new-e2e-run-id>
```

[Read the rubric](../evals/brrr/rubric.md), [see the routing result](../evals/brrr/results/brrr-routing-ab-2026-07-31-v2/result.md), or [see the end-to-end result](../evals/brrr/results/brrr-e2e-2026-08-01-v2/result.md).

## How progress is recorded

Lock In writes one brief with the decisions, scope, acceptance criteria, implementation steps, tests, approval status, and an execution checklist. Brrr updates that same checklist with what changed and which verification passed.

Small tasks can stay in the agent's task plan. If the job grows, Brrr moves the current decisions and progress into a file-backed brief once, then continues there. A ticket or specification stays untouched when it is the official record; Brrr creates one linked execution note instead of using it as a running log.

## Boundaries

Brrr is meant for one primary agent working from one clear contract. Move to a heavier workflow if the job splits into independent workstreams, reaches a high-risk system outside the approved scope, or needs coordinated testing across environments.

Brrr can implement and test the change. It still asks before committing, pushing, opening or merging a pull request, releasing anything, or changing an external system.

## Install

```sh
npx skills@latest add javonmcgilberry/skills --skill lock-in
npx skills@latest add javonmcgilberry/skills --skill brrr
```

Install either skill by itself or use them as a pair. Brrr reaches for Lock In only when the work still needs approval or a decision that could change the result.
