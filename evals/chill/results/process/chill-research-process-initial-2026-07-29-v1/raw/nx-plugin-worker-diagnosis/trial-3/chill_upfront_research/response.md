This proves Nx failed during startup, before Jest ran. It does not prove that any test, TypeScript code, or product behavior is broken because the output contains no Jest banner, test name, assertion result, or diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this verification sequence:

1. **Check the environment.** Confirm the worktree is using the repository-pinned Node 22 runtime [NODE-POLICY-2026]. Verify `node_modules` exists in the worktree and links to the main checkout installation. If the branch changes dependencies or the lockfile, treat that shared installation as potentially stale [WORKTREE-DEPS-2026].

2. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags [NX-RUNBOOK-2026].

3. **Handle execution restrictions narrowly.** If worker startup is still blocked by the sandbox, run that same focused command with the required approval outside the restriction. Do not replace it with repository-wide tests [NX-RUNBOOK-2026].

4. **Report the remaining uncertainty honestly.** The same target passing 14 tests in the main checkout points toward a worktree environment problem, but it does not prove the worktree has matching dependencies or that the branch itself passes [MAIN-CHECKOUT-PASS-2026]. If the focused command still cannot start, record verification as blocked rather than calling the tests failed or passed.

Do not delete `node_modules` or the lockfile as a first step. That advice comes from an archived guide that predates this Nx and worktree setup [REINSTALL-GUIDE-2023].