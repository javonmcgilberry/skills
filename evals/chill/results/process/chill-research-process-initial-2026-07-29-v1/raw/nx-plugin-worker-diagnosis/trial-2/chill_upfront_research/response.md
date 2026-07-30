This proves Nx failed during startup, before Jest ran. It does not prove that any package test, TypeScript code, or product behavior failed because the output contains no Jest banner, test name, assertion, or diagnostic [FAILURE-TRACE-2026] [JEST-FAILURE-CATALOG-2026].

Use this verification sequence:

1. **Check the runtime.** Run `node --version` and confirm the repository-pinned Node 22 is active. Plugin initialization failures on an unsupported Node version are environment failures, so don't change product code based on them [NODE-POLICY-2026].

2. **Check worktree dependencies.** Confirm `node_modules` exists and links to the main checkout's installation. `NODE_PATH` alone may not work because repository scripts expect binaries under the worktree's own `node_modules` path. If this branch changes the lockfile or dependencies, don't assume the shared installation is valid [WORKTREE-DEPS-2026].

3. **Reset Nx and retry exactly.** Run `npx nx reset`, then rerun the same focused command with the same flags. Changing the target or widening to the whole repository would make the comparison less useful [NX-RUNBOOK-2026].

4. **Handle sandbox blocking directly.** If worker startup is still blocked by sandbox restrictions, rerun that same focused command with the required approval outside the restriction. If it still fails there, report it as an unresolved Nx initialization problem with the Node version and dependency-link details, rather than calling it a test failure [NX-RUNBOOK-2026].

The same target passing 14 tests in the main checkout makes a worktree environment problem the leading diagnosis, but it doesn't prove both checkouts have identical dependencies or configuration [MAIN-CHECKOUT-PASS-2026]. Don't delete `node_modules`, remove the lockfile, reinstall everything, or make unrelated repairs; that advice comes from an outdated generic guide and is no longer the first response for this failure [REINSTALL-GUIDE-2023].