Build a thin intervention evaluation layer and reuse the existing observability stack. The differentiated capability is the decision loop from observed problem to approved change to measured downstream effect, while transcript storage, tracing, replay, search, memory, experiment assignment, and cost accounting are already commodity capabilities [EXISTING-TOOLS-2026].

**Build the intervention control plane**

Create a versioned, auditable record that connects:

1. Session evidence and the diagnosed problem.
2. A proposed intervention, such as a prompt, policy, tool, memory, or workflow change.
3. Human approval of one exact, immutable version.
4. The sessions eligible to receive that version.
5. Actual exposure, including whether and when the agent received it.
6. Later outcomes and the resulting keep, revise, or rollback decision.

That lifecycle is the useful architectural idea in Ax because it connects observation to evaluation of a specific intervention [AX-LIFECYCLE-2026]. Build the domain model, approval workflow, exposure ledger, outcome joins, evaluation logic, and decision UI around it.

**Reuse commodity infrastructure**

Integrate existing tools for transcripts, search, replay, source tracking, tracing, memory, assignment, and cost data [EXISTING-TOOLS-2026]. Keep those systems as systems of record and store stable references in the intervention ledger. A thin adapter layer is justified; another telemetry store, trace viewer, replay engine, or generic dashboard is not.

Ignore the older all_in_one proposal. It is explicitly superseded, predates the current inventory, and provides no build_versus_reuse analysis [BUILD-EVERYTHING-2024]. The memory benchmark also should not drive this decision because it measures synthetic retrieval accuracy without tracking intervention versions, exposure, real task outcomes, or licensing [MEMORY-BENCHMARK-2026].

**Evidence required before claiming improvement**

A credible claim needs more than similar sessions appearing after an intervention. Search results and temporal associations establish correlation only [CAUSAL-EVIDENCE-2026]. For every evaluation, preserve:

- The exact approved intervention version and approval time.
- Eligibility rules and relevant task context.
- Assignment to intervention, control, or an alternative.
- Verified exposure before the decision the intervention could affect.
- Outcomes for both exposed and comparable unexposed sessions.
- Plausible confounders such as task difficulty, model version, tool availability, operator, and concurrent changes.

Use randomized assignment when practical. Otherwise, define a defensible comparison group before examining results and adjust or stratify for the recorded confounders. Measure several downstream signals, including tests and CI, user corrections, retries, completion time, cost, and later edits or reversions, because no single signal proves success [OUTCOME-SIGNALS-2026]. The product should report effect sizes, uncertainty, sample size, and guardrail regressions rather than issuing an unsupported “improved” label.

**Licensing boundary**

Do not copy Ax or the other reviewed implementations into a proprietary service until counsel approves the exact reuse model. Ax is AGPL, and two other candidates have unusual restrictions; copying their code or operating affected code as a network service requires legal review [LICENSE-REVIEW-2026]. Use their architectural ideas, write the intervention layer independently, and integrate compatible tools through documented APIs. If legal approves an AGPL deployment, isolate it behind a clear service boundary and comply with the resulting source obligations.

The resulting product should own intervention provenance, approval, exposure, causal evaluation, and rollback decisions. Everything concerned only with collecting, finding, replaying, or visualizing agent activity should come from existing tools.