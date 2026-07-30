Build the intervention evaluation layer and reuse the rest of the observability stack. Existing tools already cover transcripts, search, replay, tracing, source tracking, memory, experiment assignment, and cost accounting, so rebuilding them would spend effort without answering whether an approved change improved later work [EXISTING-TOOLS-2026].

**Build the decision loop**

Create a small service with a versioned record for:

1. **Evidence and proposal.** Link problematic sessions to a proposed prompt, policy, memory, tool, or workflow change.

2. **Approval and versioning.** Record who approved the exact immutable intervention version, when it became active, its target population, and its success and rollback criteria.

3. **Eligibility and exposure.** For every later session, record whether it was eligible, which intervention version was available before the relevant decision, whether the agent actually received it, and why it was assigned.

4. **Outcome evaluation.** Join exposed and comparison sessions to tests, CI, user corrections, retries, completion time, cost, and later edits or reversions. No single signal is sufficient, so retain the task, model, agent configuration, repository state, and other context needed to interpret the result [OUTCOME-SIGNALS-2026].

5. **Disposition.** Produce a keep, revise, or rollback decision with the supporting analysis. This versioned path from evidence through approval, exposure, outcomes, and disposition is the differentiated lifecycle worth adopting from Ax's design [AX-LIFECYCLE-2026].

Prefer randomized assignment among eligible sessions when it is safe. Otherwise use a clearly defined concurrent control or alternative intervention and account for differences such as task type, difficulty, model version, and repository state. Search matches, similar sessions, before and after charts, and temporal proximity are useful for finding candidates, but they only establish correlation. An improvement claim requires proof that the exact intervention preceded the decision, identification of eligible and actually exposed sessions, an appropriate comparison group, and treatment of plausible confounders [CAUSAL-EVIDENCE-2026].

**Reuse commodity capabilities**

Integrate existing systems through stable IDs and adapters. Let them remain authoritative for transcripts, traces, replay, retrieval, experiment assignment, CI results, and cost. The new layer should store references, intervention metadata, exposure events, outcome joins, and decisions. A memory benchmark cannot substitute for this evaluation because retrieval accuracy on synthetic questions does not measure approved interventions, real exposure, or downstream task outcomes [MEMORY-BENCHMARK-2026].

Ignore the older all in one proposal: it predates the current tool inventory, recommends duplicating every capability, and contains no build versus reuse analysis [BUILD-EVERYTHING-2024].

**Resolve licensing before implementation**

Ax is AGPL licensed, and two other reviewed projects have unusual reuse restrictions. Do not copy their code or deploy affected code as a network service until legal approves the intended use [LICENSE-REVIEW-2026]. The practical default is to implement the lifecycle independently from the documented architectural idea, use compatible integrations where permitted, and keep provenance for every dependency and copied asset. If legal approves an AGPL deployment and its obligations fit the product model, reuse becomes viable; otherwise preserve the architecture while writing a small original implementation.

The team should own the intervention registry, eligibility and exposure ledger, outcome attribution, and decision workflow. Everything that captures, searches, replays, traces, remembers, assigns experiments, or counts cost should stay in existing tools.