# Evaluation rubric

Research process, research quality, and communication are reported separately.

## Research process

Process metrics come from completed command events in the Codex trace:

- Research tool calls
- List, search, and read actions
- Search queries
- Unique sources opened
- Source-open order and repeated reads
- Relevant-source recall
- Distractor-source rate
- Interface violations
- Paired source-set overlap

More activity is not automatically better. It matters only when it discovers better evidence or improves the result.

## Research quality

Each candidate receives up to 100 points:

- Critical expected findings: 40
- Preferred-source citation recall: 15
- Citation precision: 10
- Absence of contradicted or unsupported claims: 20
- Preserved limitations and uncertainty: 10
- Requested decision: 5

Expected findings and claim checks use stable IDs in each case's `expected.json`. The final grader was audited against the answers after preliminary patterns incorrectly treated negated warnings as forbidden recommendations. The corrected checks are punctuation tolerant and the focused tests reproduce the final scores.

## Communication

The internal review scores:

- Clarity
- Natural language
- Concision without dilution

Answers are labeled before scoring and the arm map is stored separately. This review is still internal rather than an independent human study. The reviewer also inspected labeled answers while correcting the deterministic grader, so the report does not claim perfect blinding.

Communication cannot compensate for a missing critical fact, invalid citation, or unsupported claim.
