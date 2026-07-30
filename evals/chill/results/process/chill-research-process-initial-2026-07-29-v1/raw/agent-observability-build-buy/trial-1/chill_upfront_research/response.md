Build the intervention decision loop, and reuse the rest. The valuable product is the system that connects an approved change to later agent behavior and supports a keep, revise, or roll back decision. Transcript storage, tracing, replay, search, memory, experiment assignment, source tracking, and cost accounting already exist and should stay in the current toolchain [EXISTING-TOOLS-2026].

**Build**

Create a small control plane and evidence model covering:

1. **Intervention history.** Store the suggestion, supporting session evidence, approval record, exact approved version, intended audience, and activation time.

2. **Eligibility and exposure.** Record which later sessions qualified, which version each session was assigned, and whether the agent actually received it. Availability alone doesn't count as exposure.

3. **Outcome evaluation.** Join exposed and comparison sessions to tests, CI results, user corrections, retries, completion time, cost, and later reversions. No single metric proves improvement, so define a primary outcome plus guardrails before evaluating the results [OUTCOME-SIGNALS-2026].

4. **Decision workflow.** Present the evidence for keeping, revising, or rolling back the intervention. This versioned lifecycle is the useful idea in Ax because it closes the gap between noticing a problem and testing whether a specific approved fix worked [AX-LIFECYCLE-2026].

**Reuse**

Integrate existing systems through stable IDs and APIs. Let the tracing product remain the source of session events, the transcript system own conversation data, the experiment platform handle assignment, and the cost system calculate spend. Copy only the references needed for evaluation, such as session ID, trace ID, intervention version, assignment, exposure, and outcome pointers. Rebuilding these systems would duplicate commodity infrastructure without creating the decision loop the team actually needs [EXISTING-TOOLS-2026].

The older all_in_one proposal should be rejected because it predates the current tool inventory and offers no build_versus_reuse analysis [BUILD-EVERYTHING-2024]. The memory benchmark also shouldn't drive this decision because it measures synthetic retrieval accuracy, not intervention exposure or real task outcomes [MEMORY-BENCHMARK-2026].

**Evidence required before claiming improvement**

Search matches, similar sessions, and “performance improved after deployment” are useful clues, but they show correlation. Before making a causal claim, the team must prove that the exact approved version existed before the relevant agent decision, identify eligible sessions and actual exposure, and compare them with a suitable unexposed or alternative group while accounting for plausible differences such as task mix, model version, tools, user population, and concurrent releases [CAUSAL-EVIDENCE-2026].

Random assignment among eligible sessions is the cleanest design when practical. If randomization isn't possible, use a staged rollout or matched comparison and describe the result as observational, with the remaining uncertainty stated plainly. Preserve the intervention version, exposure record, comparison group, and session context so the analysis can be reproduced [OUTCOME-SIGNALS-2026].

**Licensing**

Do not copy Ax code or deploy it as a network service until legal approves that use. Ax is AGPL licensed, and two other reviewed projects carry unusual reuse restrictions [LICENSE-REVIEW-2026]. The low_risk path is to use the lifecycle as an architectural idea, build an independent implementation owned by the team, and connect it to tools whose licenses already permit the intended deployment. A direct Ax integration or deployment is still possible, but only after legal confirms the obligations and the team intentionally accepts them [LICENSE-REVIEW-2026].

The call is to build a narrow intervention and outcome control plane, reuse every commodity observability component, and withhold improvement claims until versioned exposure and credible comparison evidence exist.