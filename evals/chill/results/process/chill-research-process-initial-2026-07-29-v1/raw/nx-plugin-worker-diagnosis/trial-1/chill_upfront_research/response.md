This proves Nx failed during startup, before Jest ran. It does not prove that any test, TypeScript code, or product behavior is broken, because there’s no Jest banner, failing test name, assertion output, or TypeScript diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this smallest verification sequence:

1. **Check Node.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin initialization failures under unsupported Node versions are environment failures, not test results [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree has `node_modules` linked to the main checkout. `NODE_PATH` alone isn’t enough because repository scripts use binaries under the worktree’s own `node_modules` path. Also check whether the branch changed the lockfile or dependencies, since that can make the shared install stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags. Changing or widening the test command would make the comparison less useful [NX-RUNBOOK-2026].

4. **Remove the execution restriction if needed.** If the same command still cannot start the worker because of sandbox restrictions, request approval and run that same focused command outside the sandbox. Don’t substitute a repository-wide test [NX-RUNBOOK-2026].

The matching target already passed 14 tests in the main checkout, which strongly points to the worktree environment as the immediate cause, though it doesn’t prove both checkouts have identical dependencies and configuration [MAIN-CHECKOUT-PASS-2026]. Don’t delete `node_modules`, remove the lockfile, reinstall everything, or change product code at this stage. That old reinstall advice predates the current worktree setup and is no longer the first response to this failure [REINSTALL-GUIDE-2023].