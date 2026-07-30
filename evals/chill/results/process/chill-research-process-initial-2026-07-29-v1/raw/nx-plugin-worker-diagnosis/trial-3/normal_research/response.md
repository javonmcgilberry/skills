`Failed to start plugin worker` proves Nx failed during initialization, before Jest started. It does not prove that any test, TypeScript compilation, or product code failed, because the output contains no Jest banner, test path, assertion, or compiler diagnostic [FAILURE-TRACE-2026].

Use this verification sequence:

1. **Check the runtime.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin initialization failures under newer unsupported versions are environment evidence, not test evidence [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree has `node_modules`, normally linked to the main checkout. `NODE_PATH` alone may be insufficient because repository scripts invoke binaries through the worktree's `node_modules`; if the branch changed dependencies or the lockfile, treat the shared installation as potentially stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact package test command with the same target and flags. Keeping it identical makes the result comparable [NX-RUNBOOK-2026].

4. **If worker startup remains blocked, rerun that same focused command outside the sandbox with the required approval.** Do not replace it with a repository-wide test, reinstall everything, delete caches manually, or change product code [NX-RUNBOOK-2026].

A passing run in the main checkout, such as the recorded 14-test pass, strengthens the diagnosis that the worktree environment is the immediate problem, but it does not prove the worktree has equivalent dependencies or configuration [MAIN-CHECKOUT-PASS-2026]. If the focused command still cannot start after the approved retry, report the tests as unverified due to Nx worker startup failure, not as failing tests.