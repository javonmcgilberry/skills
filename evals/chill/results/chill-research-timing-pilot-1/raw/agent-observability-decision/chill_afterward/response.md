Build a lightweight lifecycle and decision layer based on Ax’s model, and connect it to existing tools for transcript capture, search, replay, source tracking, memory, tracing, experiments, and cost tracking. Don’t rebuild capabilities that already exist [AX-LIFECYCLE] [REUSE].

The team’s differentiated layer should connect:

1. Session evidence to a proposed change.
2. Human approval to the exact version of that change.
3. That version to later sessions that qualified for it, including records of which sessions actually received it.
4. Those exposures to measurable outcomes.
5. Those outcomes to a decision to keep, revise, or roll back the change [AX-LIFECYCLE].

Track tests and CI results, user corrections, retries, completion time, monetary cost, and later edits or reversions [OUTCOMES]. These signals help uncover patterns and identify what deserves investigation, but search results and linked sessions show correlation, not proof that a change worked [CAUSALITY].

Before saying an intervention helped, show that the exact approved version was available before the agent made the relevant decision, identify which eligible sessions actually received it, and compare their outcomes with a suitable group that received no intervention or a different one. That comparison also needs to account for other plausible causes of the result [CAUSALITY] [AX-LIFECYCLE]. Without clear timing, version identity, exposure records, and a credible comparison, describe the result as an association rather than an improvement.

Ax uses AGPL, and two other reviewed projects have unusual reuse restrictions. Legal review is required before copying or operating affected code [LICENSE]. Reuse integrations and ideas where legally allowed, but build the lifecycle links and decision workflow as the team’s own differentiated layer.