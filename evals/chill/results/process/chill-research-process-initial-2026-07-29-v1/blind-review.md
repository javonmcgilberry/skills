# Blind review packet

Score the labeled candidates before opening blind-map.json.
The deterministic score is included to keep prose preferences from overriding research quality.

## hubspot-local-dev-architecture trial 1
### Candidate B

Run only the Vite client locally with `pnpm dev`, configured to call the development API on `wfdev.io`. Keep the API, database, OAuth exchange, callback handling, and provider credentials hosted because that is the current supported daily workflow [DEV-ARCH-2026] [TEAM-LOOP-2026].

OAuth should begin through the hosted API and return to the registered HTTPS callback on `wfdev.io`. Client secrets, refresh tokens, and database credentials must remain server side and must never appear in Vite variables or browser code [OAUTH-BOUNDARY-2026] [SECURITY-REVIEW-2026].

No tunnel or local database is required for ordinary UI work. The 2024 full local guide predates the shared hosted backend, so its local API, Postgres, callback, and tunnel setup is historical rather than current guidance [FULL-LOCAL-SETUP-2024].

Use a broader isolated environment only when changing API contracts, authentication or server behavior, persistence, migrations, or the callback handler itself [DEV-ARCH-2026] [TEAM-LOOP-2026]. Schema work needs an isolated database for forward and rollback migration testing [MIGRATION-TESTING-2026], while a tunnel is justified specifically when a modified local callback handler must receive provider traffic [OAUTH-BOUNDARY-2026].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

### Candidate A

Run only the Vite client locally with `pnpm dev`, configured to call the existing `wfdev.io` development API. Keep the API, database, OAuth flow, callbacks, and confidential credentials hosted. That is the current supported daily setup, and it gives you a fast frontend loop without recreating production infrastructure [DEV-ARCH-2026] [TEAM-LOOP-2026].

- **OAuth:** Start authorization through the hosted API. The registered HTTPS callback, client secret, and token exchange stay on `wfdev.io` [OAUTH-BOUNDARY-2026].
- **Secrets:** Never put provider secrets, refresh tokens, or database credentials in Vite variables or browser code. The client should receive only public configuration [SECURITY-REVIEW-2026].
- **Database:** Use the hosted development database for ordinary work. UI changes don't need local Postgres or migration replay [TEAM-LOOP-2026].
- **Tunnel:** You don't need one for frontend development. Use a tunnel only when testing a changed OAuth callback handler that must receive provider traffic on your machine [OAUTH-BOUNDARY-2026].

The 2024 guide that runs the client, API, Postgres, and OAuth callback locally is stale because it predates the shared `wfdev.io` backend. It remains useful only as historical migration guidance, not as the normal workflow [FULL-LOCAL-SETUP-2024].

Use a broader local or isolated server environment when the task crosses the frontend boundary by changing server behavior, an API contract, authentication, persistence, database migrations, or provider callback handling [DEV-ARCH-2026] [TEAM-LOOP-2026]. For schema changes specifically, create an isolated database and test both forward and rollback migrations before deploying to hosted development [MIGRATION-TESTING-2026].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

## hubspot-local-dev-architecture trial 2
### Candidate A

Run only the Vite client locally with `pnpm dev`, configured to call the existing development API on `wfdev.io`. Keep the API, database, OAuth installation, and provider integrations hosted, since that is the supported daily workflow for ordinary extension changes [DEV-ARCH-2026] [TEAM-LOOP-2026].

- OAuth authorization can begin in the local browser, but the registered HTTPS callback, client secret, and token exchange should remain on `wfdev.io` [OAUTH-BOUNDARY-2026].
- Provider secrets, refresh tokens, and database credentials must stay out of Vite environment variables and browser code. Local configuration should contain only public values such as the hosted API URL [SECURITY-REVIEW-2026].
- Use the hosted development database for routine work. Create an isolated database and test forward and rollback migrations only when changing persistence or schema behavior [MIGRATION-TESTING-2026].
- No tunnel is required for frontend development. Use one only when intentionally running a modified OAuth callback handler locally so the provider can reach it [OAUTH-BOUNDARY-2026].

The 2024 full local guide is stale because it predates the shared `wfdev.io` backend, so its local API, Postgres, callback, and tunnel setup should not define the current workflow [FULL-LOCAL-SETUP-2024]. A broader local environment is justified only when the task changes server behavior, an API contract, authentication or callback handling, persistence, or database migrations [DEV-ARCH-2026] [TEAM-LOOP-2026].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

### Candidate B

Use a split setup: run only the Vite client locally with `pnpm dev`, configured to call the development API on `wfdev.io`. Keep the API, OAuth flow, credentials, and database hosted. That is the current supported daily workflow and gives frontend work a fast loop without rebuilding production infrastructure locally. [DEV-ARCH-2026] [TEAM-LOOP-2026]

**OAuth and secrets**

Start authorization through the hosted API and keep the registered HTTPS callback on `wfdev.io`. The hosted server must perform the token exchange and hold provider secrets, refresh tokens, and database credentials. Vite variables and browser code should contain public configuration only. [OAUTH-BOUNDARY-2026] [SECURITY-REVIEW-2026]

**Database**

Use the hosted development database for ordinary extension work. Don't run Postgres containers or replay migrations for UI changes. For a schema change, create an isolated database and test both forward and rollback migrations before updating the hosted development environment. [TEAM-LOOP-2026] [MIGRATION-TESTING-2026]

**Tunnel**

No tunnel is needed for the normal workflow because provider traffic goes to the existing `wfdev.io` callback. Use one only when testing a changed callback handler that must receive provider requests on your machine. [OAUTH-BOUNDARY-2026]

The 2024 full local guide is stale because it predates the shared `wfdev.io` backend. Its local API, database, callback, and tunnel setup is historical guidance, not the default architecture. [FULL-LOCAL-SETUP-2024]

A broader local environment is justified when the task changes server behavior, an API contract, authentication, persistence, or the provider callback. For ordinary client work, keep the production shaped pieces hosted. [DEV-ARCH-2026] [TEAM-LOOP-2026]

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 100
- Qualitative omissions or unsupported additions:

## hubspot-local-dev-architecture trial 3
### Candidate A

Run only the Vite client locally with `pnpm dev`, configured to call the existing development API on `wfdev.io`. Keep the API, development database, OAuth exchange, provider callback, and credentials hosted, which preserves the supported fast loop without duplicating production infrastructure [DEV-ARCH-2026] [TEAM-LOOP-2026].

The browser should receive only public configuration. Provider secrets, refresh tokens, and database credentials must stay out of Vite environment variables and browser code [SECURITY-REVIEW-2026]. Authorization can begin from the local client, but the registered HTTPS callback and token exchange remain on `wfdev.io`, so ordinary extension work needs neither a local callback nor a tunnel [OAUTH-BOUNDARY-2026].

Use a broader local environment only when the task changes server behavior, an API contract, authentication, persistence, or the OAuth callback implementation [DEV-ARCH-2026] [TEAM-LOOP-2026]. Schema changes specifically require an isolated database with forward and rollback migration testing [MIGRATION-TESTING-2026]. A tunnel becomes necessary only when a changed callback handler must receive provider traffic on the developer machine [OAUTH-BOUNDARY-2026].

The 2024 full-local guide is stale because it predates the shared `wfdev.io` backend, while the production deployment checklist concerns release controls rather than development architecture [FULL-LOCAL-SETUP-2024] [PRODUCTION-DEPLOY-2026].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 93.571
- Qualitative omissions or unsupported additions:

### Candidate B

Run only the Vite client locally with `pnpm dev`, configured to call the hosted development API on `wfdev.io`. Keep the API, development database, OAuth installation, callback handler, token exchange, and provider credentials hosted. That’s the supported daily setup for ordinary extension and UI work [TEAM-LOOP-2026] [DEV-ARCH-2026].

Never put client secrets, refresh tokens, or database credentials in Vite variables or browser code. The client should receive public configuration only [SECURITY-REVIEW-2026].

You don’t need a tunnel for normal development. OAuth should continue using the registered HTTPS callback on `wfdev.io`; the local client can start authorization through the hosted API [OAUTH-BOUNDARY-2026].

Use a broader local or isolated server environment only when changing server behavior, an API contract, authentication, persistence, database migrations, or the OAuth callback itself [DEV-ARCH-2026] [TEAM-LOOP-2026]. Schema work needs an isolated database for forward and rollback migration tests, while callback-handler work needs a tunnel so the provider can reach the developer machine [MIGRATION-TESTING-2026] [OAUTH-BOUNDARY-2026].

Ignore the 2024 full-local guide for day-to-day work. It predates the shared `wfdev.io` backend and is retained only for historical migration scenarios [FULL-LOCAL-SETUP-2024].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

## nx-plugin-worker-diagnosis trial 1
### Candidate A

This proves Nx failed during startup, before Jest ran. It does not prove that any test, TypeScript code, or product behavior is broken, because there’s no Jest banner, failing test name, assertion output, or TypeScript diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this smallest verification sequence:

1. **Check Node.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin initialization failures under unsupported Node versions are environment failures, not test results [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree has `node_modules` linked to the main checkout. `NODE_PATH` alone isn’t enough because repository scripts use binaries under the worktree’s own `node_modules` path. Also check whether the branch changed the lockfile or dependencies, since that can make the shared install stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags. Changing or widening the test command would make the comparison less useful [NX-RUNBOOK-2026].

4. **Remove the execution restriction if needed.** If the same command still cannot start the worker because of sandbox restrictions, request approval and run that same focused command outside the sandbox. Don’t substitute a repository-wide test [NX-RUNBOOK-2026].

The matching target already passed 14 tests in the main checkout, which strongly points to the worktree environment as the immediate cause, though it doesn’t prove both checkouts have identical dependencies and configuration [MAIN-CHECKOUT-PASS-2026]. Don’t delete `node_modules`, remove the lockfile, reinstall everything, or change product code at this stage. That old reinstall advice predates the current worktree setup and is no longer the first response to this failure [REINSTALL-GUIDE-2023].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

### Candidate B

This proves Nx failed during plugin initialization, before Jest started. It does not prove that any test, TypeScript code, or product behavior is broken [FAILURE-TRACE-2026].

Use this verification sequence:

1. **Check Node.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin startup under an unsupported newer runtime is environment evidence, not a test failure [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree’s `node_modules` links to the main checkout’s installation. `NODE_PATH` alone is insufficient because repository scripts invoke binaries through the worktree path. If the branch changes dependencies or the lockfile, treat the shared installation as potentially stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact focused command with the same target and flags [NX-RUNBOOK-2026].

4. **Compare with the main checkout.** The same target already passed 14 tests there, which points toward a worktree-specific environment problem, though it does not prove both environments are identical [MAIN-CHECKOUT-PASS-2026].

If the focused command remains blocked by sandbox restrictions, rerun that same command with the required approval outside the restriction. Do not substitute a repository-wide test, change product code, delete the lockfile, or reinstall everything; the current runbook keeps the test comparable, while the destructive reinstall advice is archived and predates this setup [NX-RUNBOOK-2026] [REINSTALL-GUIDE-2023]. If it still cannot reach Jest, report the test result as unverified due to Nx worker startup failure, not as a package-test failure.

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 95
- Qualitative omissions or unsupported additions:

## nx-plugin-worker-diagnosis trial 2
### Candidate A

This proves Nx failed during startup, before Jest ran. It does not prove that any package test, TypeScript code, or product behavior failed because the output contains no Jest banner, test name, assertion, or diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this verification sequence:

1. **Check the runtime.** Run `node --version` and confirm the repository-pinned Node 22 is active. Plugin initialization failures on an unsupported Node version are environment failures, so don't change product code based on them [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm `node_modules` exists and links to the main checkout's installation. `NODE_PATH` alone may not work because repository scripts expect binaries under the worktree's own `node_modules` path. If this branch changes the lockfile or dependencies, don't assume the shared installation is valid [WORKTREE-DEPS-2026].

3. **Reset Nx and retry exactly.** Run `npx nx reset`, then rerun the same focused command with the same flags. Changing the target or widening to the whole repository would make the comparison less useful [NX-RUNBOOK-2026].

4. **Handle sandbox blocking directly.** If worker startup is still blocked by sandbox restrictions, rerun that same focused command with the required approval outside the restriction. If it still fails there, report it as an unresolved Nx initialization problem with the Node version and dependency-link details, rather than calling it a test failure [NX-RUNBOOK-2026].

The same target passing 14 tests in the main checkout makes a worktree environment problem the leading diagnosis, but it doesn't prove both checkouts have identical dependencies or configuration [MAIN-CHECKOUT-PASS-2026]. Don't delete `node_modules`, remove the lockfile, reinstall everything, or make unrelated repairs; that advice comes from an outdated generic guide and is no longer the first response for this failure [REINSTALL-GUIDE-2023].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 100
- Qualitative omissions or unsupported additions:

### Candidate B

The result proves Nx failed during plugin initialization, before Jest started. It does not prove that any test, assertion, TypeScript check, Jest configuration, or product code failed, and it also does not prove the tests would pass once Nx starts. [FAILURE-TRACE-2026]

Use this smallest verification sequence:

1. Record the exact command, working directory, full error, and `node --version`. The repository requires its pinned Node 22 runtime, so a startup failure under a newer unsupported version is environment evidence. [NODE-POLICY-2026]

2. Check the worktree dependency setup. If `node_modules` is absent, link it to the main checkout because repository scripts resolve binaries through the worktree path. If the branch changes the lockfile or dependencies, treat the shared installation as potentially stale. [WORKTREE-DEPS-2026]

3. Run `npx nx reset`, then retry the exact focused command with the same target and flags. Changing the test scope would make the comparison inconclusive. [NX-RUNBOOK-2026]

4. If worker startup remains blocked by sandbox restrictions, run that same focused command outside the restriction with the required approval. Do not replace it with the full repository test suite. [NX-RUNBOOK-2026]

A passing comparison in the main checkout points toward a worktree environment problem, but it cannot prove the branch tests pass because the two checkouts may differ in dependencies or configuration. [MAIN-CHECKOUT-PASS-2026] Avoid deleting `node_modules`, deleting the lockfile, reinstalling everything, or changing product code at this stage; that advice is archived and is no longer the first response to this failure. [REINSTALL-GUIDE-2023]

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 100
- Qualitative omissions or unsupported additions:

## nx-plugin-worker-diagnosis trial 3
### Candidate B

`Failed to start plugin worker` proves Nx failed during initialization, before Jest started. It does not prove that any test, TypeScript compilation, or product code failed, because the output contains no Jest banner, test path, assertion, or compiler diagnostic [FAILURE-TRACE-2026].

Use this verification sequence:

1. **Check the runtime.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin initialization failures under newer unsupported versions are environment evidence, not test evidence [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree has `node_modules`, normally linked to the main checkout. `NODE_PATH` alone may be insufficient because repository scripts invoke binaries through the worktree's `node_modules`; if the branch changed dependencies or the lockfile, treat the shared installation as potentially stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags. Keeping it identical makes the result comparable [NX-RUNBOOK-2026].

4. **If worker startup remains blocked, rerun that same focused command outside the sandbox with the required approval.** Do not replace it with a repository-wide test, reinstall everything, delete caches manually, or change product code [NX-RUNBOOK-2026].

A passing run in the main checkout, such as the recorded 14-test pass, strengthens the diagnosis that the worktree environment is the immediate problem, but it does not prove the worktree has equivalent dependencies or configuration [MAIN-CHECKOUT-PASS-2026]. If the focused command still cannot start after the approved retry, report the tests as unverified due to Nx worker startup failure, not as failing tests.

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 100
- Qualitative omissions or unsupported additions:

### Candidate A

This proves Nx failed during startup, before Jest ran. It does not prove that any test, TypeScript code, or product behavior is broken because the output contains no Jest banner, test name, assertion result, or diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this verification sequence:

1. **Check the environment.** Confirm the worktree is using the repository-pinned Node 22 runtime [NODE-POLICY-2026]. Verify `node_modules` exists in the worktree and links to the main checkout installation. If the branch changes dependencies or the lockfile, treat that shared installation as potentially stale [WORKTREE-DEPS-2026].

2. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags [NX-RUNBOOK-2026].

3. **Handle execution restrictions narrowly.** If worker startup is still blocked by the sandbox, run that same focused command with the required approval outside the restriction. Do not replace it with repository-wide tests [NX-RUNBOOK-2026].

4. **Report the remaining uncertainty honestly.** The same target passing 14 tests in the main checkout points toward a worktree environment problem, but it does not prove the worktree has matching dependencies or that the branch itself passes [MAIN-CHECKOUT-PASS-2026]. If the focused command still cannot start, record verification as blocked rather than calling the tests failed or passed.

Do not delete `node_modules` or the lockfile as a first step. That advice comes from an archived guide that predates this Nx and worktree setup [REINSTALL-GUIDE-2023].

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 100
- Qualitative omissions or unsupported additions:

## agent-observability-build-buy trial 1
### Candidate A

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

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.571
- Qualitative omissions or unsupported additions:

### Candidate B

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

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.571
- Qualitative omissions or unsupported additions:

## agent-observability-build-buy trial 2
### Candidate B

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

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.333
- Qualitative omissions or unsupported additions:

### Candidate A

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

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.571
- Qualitative omissions or unsupported additions:

## agent-observability-build-buy trial 3
### Candidate A

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

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.571
- Qualitative omissions or unsupported additions:

### Candidate B

Build the intervention-to-outcome control plane, and reuse the rest. Existing tools already handle transcripts, search, replay, tracing, memory, experiment assignment, source tracking, and cost accounting, so rebuilding those would add infrastructure without answering whether an approved change helped later work [EXISTING-TOOLS-2026].

**Build the decision loop**

Create a small service that records:

1. **Evidence and proposal.** Link observed session evidence to a proposed intervention, such as a prompt, policy, tool, or memory change.
2. **Approval and version.** Store the exact approved content, version, approver, target population, and activation time.
3. **Eligibility and exposure.** Record every later session that qualified, whether it actually received the intervention, and which version it received.
4. **Evaluation and decision.** Compare outcomes, then record a keep, revise, or rollback decision.

That lifecycle is the useful part of Ax's design because it connects an observed problem, human approval, actual exposure, later outcomes, and a final decision [AX-LIFECYCLE-2026].

**Reuse commodity capabilities**

Integrate existing systems for session storage, replay, search, tracing, memory, experiments, CI results, and cost data [EXISTING-TOOLS-2026]. Your service should keep stable IDs and links into those systems instead of copying all their data. The UI only needs to show the intervention history, evidence links, exposure coverage, outcome comparison, and decision status.

**Evidence required to claim improvement**

A before-and-after chart isn't enough. Before saying an intervention worked, you need to prove that the exact approved version was available before the relevant decision, identify all eligible sessions and their real exposure, and compare exposed sessions with a suitable unexposed or alternative group while dealing with plausible confounders [CAUSAL-EVIDENCE-2026].

Use randomized assignment when practical. Otherwise, define the comparison group and relevant context up front, then be explicit about the weaker causal confidence. Track several outcomes, including tests or CI, user corrections, retries, completion time, cost, and later edits or reversions, because no single metric proves success [OUTCOME-SIGNALS-2026]. Preserve the intervention version, exposure record, comparison assignment, and context so the result can be audited or reproduced [OUTCOME-SIGNALS-2026].

Do not treat retrieval benchmarks as evidence that interventions improve real work. The available memory benchmark measures synthetic retrieval accuracy but does not track approvals, exposure, real task outcomes, or licensing [MEMORY-BENCHMARK-2026].

**Licensing**

Do not copy Ax code or deploy it as a network service without legal approval because it is AGPL-licensed. Two other reviewed projects also carry unusual reuse restrictions [LICENSE-REVIEW-2026]. Use the lifecycle as an architectural idea, implement your own narrow control plane, and connect to existing products only through legally approved integrations. That gives you the differentiated capability without making restricted code part of your platform.

The call is to build the versioned approval, exposure, evaluation, and rollback loop, while reusing every commodity observability capability around it.

Review fields:

- Clarity: /5
- Natural language: /5
- Concision without dilution: /5
- Deterministic research score: 98.333
- Qualitative omissions or unsupported additions:
