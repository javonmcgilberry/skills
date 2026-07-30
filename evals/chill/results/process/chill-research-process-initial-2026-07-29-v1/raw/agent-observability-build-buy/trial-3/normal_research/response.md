Build the intervention-to-outcome decision layer and reuse the surrounding observability infrastructure. That layer is the differentiator because it connects an approved change to actual exposure and later results, while transcript storage, tracing, replay, search, memory, experiment assignment, and cost accounting are already commodity capabilities [AX-LIFECYCLE-2026] [EXISTING-TOOLS-2026].

**Build the decision loop**

Create a small service and data model that records:

1. **Intervention provenance.** Link the evidence from earlier sessions to a proposed intervention, its human approval, and the immutable version that was approved.

2. **Eligibility and exposure.** Record which later sessions were eligible, which intervention version was available before each relevant decision, and whether the agent actually received it. Availability alone doesn't establish exposure [CAUSAL-EVIDENCE-2026].

3. **Outcome evaluation.** Join exposed sessions to tests and CI, user corrections, retries, completion time, monetary cost, and later edits or reversions. Evaluate several signals together because no single metric proves improvement [OUTCOME-SIGNALS-2026].

4. **Decision state.** Produce an auditable keep, revise, or rollback recommendation for each intervention version. Preserve the comparison group and relevant task context so that the result can be reproduced [AX-LIFECYCLE-2026] [OUTCOME-SIGNALS-2026].

**Reuse existing tools**

Integrate existing systems for transcript capture, search, replay, source tracking, memory, tracing, experiment assignment, and cost accounting [EXISTING-TOOLS-2026]. Keep their native identifiers and store references in the decision layer instead of copying all their data into another platform. The older proposal to rebuild everything is superseded, predates the current tool inventory, and contains no build-versus-reuse analysis [BUILD-EVERYTHING-2024].

A memory retrieval benchmark can help select a memory provider, but it cannot support the intervention claim because it doesn't track approval, exposure, real task outcomes, or licensing [MEMORY-BENCHMARK-2026].

**Evidence required before claiming improvement**

The strongest design randomly assigns eligible sessions to the approved intervention or a control, stratified by task type and other important context. If randomization isn't practical, use a staged rollout or matched comparison and explicitly address plausible confounders such as model version, task difficulty, tool availability, and concurrent prompt changes.

Do not claim success from search hits, similar sessions, before-and-after charts, or temporal proximity. Those establish correlation at most. The claim requires proof that the exact approved version preceded the relevant decision, a complete eligible population, verified exposure, an appropriate comparison group, and better downstream outcomes without offsetting regressions [CAUSAL-EVIDENCE-2026]. Treat the intervention version as the unit of evaluation, since aggregating multiple revisions would make the result impossible to attribute.

**Licensing boundary**

Ax provides a useful lifecycle design, but it is AGPL-licensed, and two other reviewed projects have unusual reuse restrictions. Legal review is required before copying their code or operating affected code as a network service [LICENSE-REVIEW-2026]. Use compatible integrations where approved, and implement the decision layer independently from the documented architectural concepts unless legal explicitly approves code reuse.

The practical boundary is clear: reuse commodity telemetry and experimentation products, then build a license-safe, vendor-neutral control plane that versions interventions, verifies exposure, evaluates controlled outcomes, and drives keep, revise, or rollback decisions.