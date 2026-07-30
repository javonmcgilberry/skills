The result proves Nx failed during plugin initialization, before Jest started. It does not prove that any test, assertion, TypeScript check, Jest configuration, or product code failed, and it also does not prove the tests would pass once Nx starts. [FAILURE-TRACE-2026]

Use this smallest verification sequence:

1. Record the exact command, working directory, full error, and `node --version`. The repository requires its pinned Node 22 runtime, so a startup failure under a newer unsupported version is environment evidence. [NODE-POLICY-2026]

2. Check the worktree dependency setup. If `node_modules` is absent, link it to the main checkout because repository scripts resolve binaries through the worktree path. If the branch changes the lockfile or dependencies, treat the shared installation as potentially stale. [WORKTREE-DEPS-2026]

3. Run `npx nx reset`, then retry the exact focused command with the same target and flags. Changing the test scope would make the comparison inconclusive. [NX-RUNBOOK-2026]

4. If worker startup remains blocked by sandbox restrictions, run that same focused command outside the restriction with the required approval. Do not replace it with the full repository test suite. [NX-RUNBOOK-2026]

A passing comparison in the main checkout points toward a worktree environment problem, but it cannot prove the branch tests pass because the two checkouts may differ in dependencies or configuration. [MAIN-CHECKOUT-PASS-2026] Avoid deleting `node_modules`, deleting the lockfile, reinstalling everything, or changing product code at this stage; that advice is archived and is no longer the first response to this failure. [REINSTALL-GUIDE-2023]