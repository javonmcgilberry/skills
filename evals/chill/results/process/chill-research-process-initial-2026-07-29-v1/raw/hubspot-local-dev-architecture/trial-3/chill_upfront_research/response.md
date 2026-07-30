Run only the Vite client locally with `pnpm dev`, configured to call the hosted development API on `wfdev.io`. Keep the API, development database, OAuth installation, callback handler, token exchange, and provider credentials hosted. That’s the supported daily setup for ordinary extension and UI work [TEAM-LOOP-2026] [DEV-ARCH-2026].

Never put client secrets, refresh tokens, or database credentials in Vite variables or browser code. The client should receive public configuration only [SECURITY-REVIEW-2026].

You don’t need a tunnel for normal development. OAuth should continue using the registered HTTPS callback on `wfdev.io`; the local client can start authorization through the hosted API [OAUTH-BOUNDARY-2026].

Use a broader local or isolated server environment only when changing server behavior, an API contract, authentication, persistence, database migrations, or the OAuth callback itself [DEV-ARCH-2026] [TEAM-LOOP-2026]. Schema work needs an isolated database for forward and rollback migration tests, while callback-handler work needs a tunnel so the provider can reach the developer machine [MIGRATION-TESTING-2026] [OAUTH-BOUNDARY-2026].

Ignore the 2024 full-local guide for day-to-day work. It predates the shared `wfdev.io` backend and is retained only for historical migration scenarios [FULL-LOCAL-SETUP-2024].