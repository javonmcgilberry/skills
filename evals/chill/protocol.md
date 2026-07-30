# Research-process protocol

## Question

Does loading Chill before a research task change how the agent researches, and does any change improve the final research?

Private reasoning is outside scope. The experiment uses observable tool traces and final outputs.

## Primary arms

`normal_research` receives the task and common research instructions.

`chill_upfront_research` receives the same task and common instructions plus the exact frozen Chill skill and an invocation bridge.

Every candidate starts in a fresh Codex session. The model, reasoning effort, corpus, research interface, task, and common instructions are identical within each pair. Arm order and corpus order are reproducibly randomized.

## Cases

The initial suite has three sanitized research tasks:

1. Choose the local-versus-hosted architecture for a HubSpot Designer extension.
2. Diagnose an Nx plugin-worker startup failure without mistaking it for a test failure.
3. Make an agent-observability build-versus-reuse decision.

Each frozen corpus contains current relevant sources, plausible distractors, and stale or conflicting guidance. Hidden expectations and stable rule IDs remain outside the candidate workspace.

Candidates can use only:

```sh
node research.mjs list
node research.mjs search "search terms"
node research.mjs read SOURCE-ID
```

The trace records every command. Direct file access or another research tool is an interface violation.

## Run size

The initial suite contains:

- 3 cases
- 3 trials per case
- 2 arms
- 18 candidate calls

A twelve-call holdout round was reserved for a mixed initial result. The initial result crossed the precommitted material-process threshold coherently across the cases, so the holdout round was not run.

## Measurements

Research process:

- Tool calls and searches
- Sources opened and their order
- Repeated reads
- Relevant-source recall
- Distractor rate
- Paired source-set overlap
- Latency and recorded token usage

Research outcome:

- Critical expected findings
- Relevant citations
- Unsupported or contradicted claims
- Preserved limitations
- The requested decision

Communication remains secondary. It is reviewed separately so prose preferences cannot offset missing research.

## Stopping rule

A material quality effect requires a median paired score difference of at least 5 points in the same direction in at least 7 of 9 pairs, or at least 2 additional critical failures in one arm.

A material process change requires a median difference of at least 20 percent in tool calls or sources opened in the same direction in at least 7 of 9 pairs, or at least a 10 percentage-point difference in relevant-source recall or distractor rate.

The initial run recorded a median 28.6 percent increase in tool calls with Chill upfront, in the same direction in 8 of 9 pairs and coherently across all three fixtures. It therefore met the process stopping rule. Quality did not meet its material threshold.

## Decision rule

When Chill changes the process without improving the outcome, use normal research by default and apply Chill afterward only when the completed explanation needs help.
