Build a thin lifecycle and decision layer modeled on Ax, then integrate existing tools for transcript capture, search, replay, source tracking, memory, tracing, experiments, and cost tracking instead of rebuilding those capabilities [AX-LIFECYCLE] [REUSE].

The differentiated layer should connect:

1. Session evidence to a proposed intervention.
2. Human approval to an exact intervention version.
3. That version to eligible later sessions and exposure records.
4. Exposure to outcomes.
5. Outcomes to a keep, revise, or rollback decision [AX-LIFECYCLE].

Use tests and CI, user corrections, retries, completion time, monetary cost, and later edits or reversions as outcome signals [OUTCOMES]. These are useful evidence for finding patterns and deciding what to investigate, but search hits and linked sessions establish correlation only [CAUSALITY].

Before claiming an intervention helped, prove that the exact approved version was available before the relevant agent decision, show which eligible sessions were actually exposed to it, and compare outcomes against an appropriate unexposed or alternative group while addressing plausible confounders [CAUSALITY] [AX-LIFECYCLE]. Without intervention timing, version identity, exposure records, and a credible comparison, the team should describe the result as an association rather than an improvement.

Ax uses AGPL, and two other reviewed projects have unusual reuse restrictions. Legal review is required before copying or operating affected code [LICENSE]. Reuse integrations and concepts where legally permitted, but build the lifecycle linkage and decision workflow as the team's own differentiated layer.