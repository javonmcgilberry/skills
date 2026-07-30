Use a split setup: run only the Vite client locally with `pnpm dev`, configured to call the development API on `wfdev.io`. Keep the API, OAuth flow, credentials, and database hosted. That is the current supported daily workflow and gives frontend work a fast loop without rebuilding production infrastructure locally. [DEV-ARCH-2026] [TEAM-LOOP-2026]

**OAuth and secrets**

Start authorization through the hosted API and keep the registered HTTPS callback on `wfdev.io`. The hosted server must perform the token exchange and hold provider secrets, refresh tokens, and database credentials. Vite variables and browser code should contain public configuration only. [OAUTH-BOUNDARY-2026] [SECURITY-REVIEW-2026]

**Database**

Use the hosted development database for ordinary extension work. Don't run Postgres containers or replay migrations for UI changes. For a schema change, create an isolated database and test both forward and rollback migrations before updating the hosted development environment. [TEAM-LOOP-2026] [MIGRATION-TESTING-2026]

**Tunnel**

No tunnel is needed for the normal workflow because provider traffic goes to the existing `wfdev.io` callback. Use one only when testing a changed callback handler that must receive provider requests on your machine. [OAUTH-BOUNDARY-2026]

The 2024 full local guide is stale because it predates the shared `wfdev.io` backend. Its local API, database, callback, and tunnel setup is historical guidance, not the default architecture. [FULL-LOCAL-SETUP-2024]

A broader local environment is justified when the task changes server behavior, an API contract, authentication, persistence, or the provider callback. For ordinary client work, keep the production shaped pieces hosted. [DEV-ARCH-2026] [TEAM-LOOP-2026]