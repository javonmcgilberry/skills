Build a thin intervention lifecycle layer on top of existing observability tools. Reuse their transcript capture, search, replay, source tracking, memory, tracing, experiment, and cost tracking instead of rebuilding those capabilities [REUSE].

The differentiated layer should connect:

1. Session evidence and the proposed change.
2. Human approval and the exact intervention version.
3. Which later sessions were eligible and actually exposed.
4. Outcomes for those sessions.
5. A recorded decision to keep, revise, or roll back the intervention [AX-LIFECYCLE].

Tests and CI results, user corrections, retries, completion time, monetary cost, and later edits or reversions are all useful outcome signals [OUTCOMES]. Search results and linked sessions can help the team find promising patterns, but they only show correlation [CAUSALITY].

Before claiming an intervention helped, prove that the exact version was available before the relevant agent decision, record which sessions were exposed, and compare outcomes in a way that addresses plausible confounders [CAUSALITY]. Without that timing and comparison, the evidence is useful for investigation but isn't proof of impact.

Ax is AGPL, and two other reviewed projects have unusual reuse restrictions. Get legal review before copying or operating any affected code [LICENSE]. The team should reuse compatible infrastructure, while building its own intervention lifecycle and causal evidence layer unless legal review clears a specific implementation.