Build the intervention evaluation loop, and reuse the rest. Existing tools already handle transcripts, search, replay, tracing, memory, experiment assignment, source tracking, and cost accounting, so rebuilding those pieces would add infrastructure without answering whether an approved change helped [EXISTING-TOOLS-2026].

**Build the part that connects changes to results**

Create a small control plane that records:

1. **The intervention:** Link the supporting session evidence to a proposed change, its human approval, and the exact approved version.

2. **Eligibility and exposure:** Record which later sessions qualified for the intervention, whether they actually received it, and whether it was available before the relevant agent decision.

3. **Outcomes:** Join each session to tests and CI results, user corrections, retries, completion time, cost, and later edits or reversions. Keep several measures because no single signal proves success [OUTCOME-SIGNALS-2026].

4. **The decision:** Compare exposed sessions with a suitable control or alternative group, account for meaningful differences between the groups, and record whether the team keeps, revises, or rolls back the intervention [CAUSAL-EVIDENCE-2026] [AX-LIFECYCLE-2026].

Prefer randomized assignment among eligible sessions when practical. Otherwise, preserve enough context to build a credible comparison and explain the remaining uncertainty. Search hits, similar sessions, and improvements that happened afterward are useful clues, but they only show correlation [CAUSAL-EVIDENCE-2026].

**Reuse commodity capabilities**

Integrate existing storage, tracing, replay, search, memory, experiment assignment, and cost systems through stable IDs and events. The new service should own intervention versions, approvals, eligibility rules, exposure records, outcome joins, and final decisions. A memory benchmark can help choose a retrieval system, but it cannot establish intervention effectiveness because it measures synthetic retrieval accuracy rather than exposure and real task outcomes [MEMORY-BENCHMARK-2026].

**Handle licensing before choosing an implementation**

Ax contains the right lifecycle idea, but its code is AGPL licensed, and two other reviewed projects have unusual reuse restrictions. Do not copy their code or operate affected code as a network service until legal approves that use [LICENSE-REVIEW-2026]. The safer default is to implement the narrow decision loop independently and integrate approved tools through their supported interfaces. You can reuse the architectural idea of a versioned intervention lifecycle without adopting restricted implementation code [LICENSE-REVIEW-2026].

The call is to build a thin, owned intervention control plane and reuse every mature observability capability around it. Only reconsider a broader build if the existing tools cannot provide reliable session IDs, timestamps, experiment assignment, or exportable outcome data.