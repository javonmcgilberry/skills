# Chill research-process result

## Verdict

Use normal research first, then invoke Chill only when the completed explanation needs rewriting.

Chill upfront materially changed the research process: it produced more research tool calls and far more searches. That additional work did not produce a material improvement in facts, citations, source selection, or recommendations.

## Research process

| Metric | Normal research | Chill upfront | Result |
| --- | ---: | ---: | --- |
| Total research tool calls | 73 | 94 | Chill used 21 more calls |
| Mean tool calls per candidate | 8.11 | 10.44 | 28.6 percent median paired increase |
| Total searches | 6 | 23 | Chill searched 17 more times |
| Unique source reads across candidates | 58 | 62 | 4 additional reads |
| Mean relevant-source recall | 93.6 percent | 100 percent | Median paired difference was 0 |
| Mean distractor rate | 7.5 percent | 7.1 percent | Median paired difference was 0 |
| Median paired source-set overlap | 87.5 percent | 87.5 percent | The arms usually read the same evidence |
| Interface violations | 0 | 0 | Every candidate stayed within the research interface |

The precommitted process threshold required at least a 20 percent median change in tool calls or sources opened, in the same direction in 7 of 9 pairs. Tool calls increased by a median 28.6 percent in 8 of 9 pairs, coherently across all three cases. That is a material observable process change.

The source differences were much smaller than the activity difference. Chill agents searched more, but they usually ended up reading the same documents.

## Research quality

| Metric | Normal research | Chill upfront |
| --- | ---: | ---: |
| Mean deterministic score | 97.14 | 97.80 |
| Median deterministic score | 98.57 | 98.33 |
| Median paired score difference | 0 | 0 |
| Critical failures | 0 | 0 |

The mean difference was 0.66 points in Chill's favor, while the median paired difference was zero and pair directions were mixed. This is below the predefined 5-point material threshold. Chill upfront did not improve or damage research quality in a reliable way.

## Communication

| Metric | Normal research | Chill upfront |
| --- | ---: | ---: |
| Total words | 2,797 | 2,802 |
| Mean words | 310.8 | 311.3 |
| Internal clarity score | 4.93 | 4.93 |
| Internal natural-language score | 4.70 | 4.77 |
| Internal concision score | 4.70 | 4.63 |

Communication was effectively tied. Chill was slightly more natural in the internal review and slightly less concise. The five-word aggregate length difference is not meaningful.

The earlier fixed-evidence pilots were also inconsistent: one legacy screen made Chill upfront shorter, while the newer three-case synthesis pilot made both Chill workflows longer. Together, the evidence does not support loading Chill upfront for a reliable communication benefit.

## Runtime and recorded usage

| Metric | Normal research | Chill upfront |
| --- | ---: | ---: |
| Mean duration | 49.6 seconds | 48.0 seconds |
| Recorded input tokens | 1,614,337 | 1,239,272 |
| Recorded cached input tokens | 1,310,208 | 999,680 |
| Recorded output tokens | 13,475 | 13,225 |
| Recorded reasoning tokens | 2,263 | 3,044 |

The recorded token fields include cached Codex context and are not a direct measure of research quality. Chill used more recorded reasoning tokens, but the content of private reasoning was not available or graded.

## Stopping decision

The initial suite completed 18 calls:

- 3 cases
- 3 paired trials per case
- 2 arms

The material process threshold was met, so the predefined protocol says to stop. The reserved twelve-call holdout round was not run. Total new candidate calls: 18.

## Evidence integrity

The preliminary deterministic grader produced false failures because some patterns matched correct negated warnings such as "do not delete the lockfile." Other patterns missed a required idea when it crossed a sentence boundary or used a curly apostrophe.

Those patterns were corrected and the same saved candidates were regraded without new model calls. The final result has zero critical failures in both arms. The research-process result did not depend on those text patterns because it comes directly from recorded command traces.

The qualitative review used anonymized candidate labels, but the reviewer had already inspected labeled answers while auditing the grader. It is reported as an internal review, not a fully blind independent judgment.

## Limits

This result applies to one model, one reasoning effort, three local research corpora, and nine paired trials. The local interface approximates source research but is not the public internet.

The experiment cannot show that Chill never changes quality. It shows that, in these cases, Chill reliably increased research activity without delivering a better result. Under the predefined decision rule, that supports normal research followed by optional Chill rewriting.
