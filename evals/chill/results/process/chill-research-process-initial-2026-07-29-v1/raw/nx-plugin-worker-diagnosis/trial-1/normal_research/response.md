This proves Nx failed during plugin initialization, before Jest started. It does not prove that any test, TypeScript code, or product behavior is broken [FAILURE-TRACE-2026].

Use this verification sequence:

1. **Check Node.** Record `node --version` and confirm the repository-pinned Node 22 runtime is active. Plugin startup under an unsupported newer runtime is environment evidence, not a test failure [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm the worktree’s `node_modules` links to the main checkout’s installation. `NODE_PATH` alone is insufficient because repository scripts invoke binaries through the worktree path. If the branch changes dependencies or the lockfile, treat the shared installation as potentially stale [WORKTREE-DEPS-2026].

3. **Reset Nx and retry unchanged.** Run `npx nx reset`, then rerun the exact focused command with the same target and flags [NX-RUNBOOK-2026].

4. **Compare with the main checkout.** The same target already passed 14 tests there, which points toward a worktree-specific environment problem, though it does not prove both environments are identical [MAIN-CHECKOUT-PASS-2026].

If the focused command remains blocked by sandbox restrictions, rerun that same command with the required approval outside the restriction. Do not substitute a repository-wide test, change product code, delete the lockfile, or reinstall everything; the current runbook keeps the test comparable, while the destructive reinstall advice is archived and predates this setup [NX-RUNBOOK-2026] [REINSTALL-GUIDE-2023]. If it still cannot reach Jest, report the test result as unverified due to Nx worker startup failure, not as a package-test failure.