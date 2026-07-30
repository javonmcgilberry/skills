Run only the Vite client locally with `pnpm dev`, configured to call the existing `wfdev.io` development API. Keep the API, database, OAuth flow, callbacks, and confidential credentials hosted. That is the current supported daily setup, and it gives you a fast frontend loop without recreating production infrastructure [DEV-ARCH-2026] [TEAM-LOOP-2026].

- **OAuth:** Start authorization through the hosted API. The registered HTTPS callback, client secret, and token exchange stay on `wfdev.io` [OAUTH-BOUNDARY-2026].
- **Secrets:** Never put provider secrets, refresh tokens, or database credentials in Vite variables or browser code. The client should receive only public configuration [SECURITY-REVIEW-2026].
- **Database:** Use the hosted development database for ordinary work. UI changes don't need local Postgres or migration replay [TEAM-LOOP-2026].
- **Tunnel:** You don't need one for frontend development. Use a tunnel only when testing a changed OAuth callback handler that must receive provider traffic on your machine [OAUTH-BOUNDARY-2026].

The 2024 guide that runs the client, API, Postgres, and OAuth callback locally is stale because it predates the shared `wfdev.io` backend. It remains useful only as historical migration guidance, not as the normal workflow [FULL-LOCAL-SETUP-2024].

Use a broader local or isolated server environment when the task crosses the frontend boundary by changing server behavior, an API contract, authentication, persistence, database migrations, or provider callback handling [DEV-ARCH-2026] [TEAM-LOOP-2026]. For schema changes specifically, create an isolated database and test both forward and rollback migrations before deploying to hosted development [MIGRATION-TESTING-2026].