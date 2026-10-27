---
name: brrr
description: Execute a clear coding request, approved brief, plan, spec, or ticket with one primary agent, visible incremental progress, focused verification, and a final self-review. Use for everyday implementation when the desired outcome and acceptance criteria are already clear and Compound Engineering's multi-agent review and shipping workflow would add unnecessary weight.
---

# Brrr

Complete the requested work with a lightweight, evidence-driven execution loop. Preserve quality while keeping orchestration small.

## Start from the contract

1. Read the request and any referenced brief, plan, ticket, or spec completely.
2. Inspect repository instructions, the working tree, and the code paths that own the behavior.
3. Confirm that the outcome and acceptance criteria are executable. Invoke `$lock-in` first when a material product or technical decision remains unresolved.

Use an existing file-backed brief or plan as the source of truth. For short work without one, create a task plan with the plan tool. For work likely to cross sessions, create a compact brief in the repository's established planning location before implementation. Keep one progress surface rather than copying state between documents.

## Keep durable state

When the source of truth is file-backed, maintain its **Execution** checklist as work progresses. For each meaningful unit, record only:

- Its status.
- The behavior or evidence produced.
- The verification command and result.
- A decision that changed the agreed implementation, when one occurred.

Add implementation discoveries to the existing **Decisions** section. Reserve an ADR for a durable architectural choice when the repository already has an ADR convention, then link it from the brief. Keep raw command output, narration, and routine edits out of the record.

## Execute

1. For bugs, reproduce the failure through the closest practical end-user path before changing code.
2. Implement the smallest complete unit that advances an acceptance criterion.
3. Update the task status after each meaningful unit and write its compact evidence to the active progress surface.
4. Send concise commentary at meaningful checkpoints: what was proven, what changed, what passed, and what comes next.
5. Continue until every in-scope acceptance criterion is satisfied or a concrete blocker requires the user.

Keep execution in the primary agent. Delegate only when the user explicitly requests parallel work.

## Verify

Use `$run-tests-on-request` for every automated test run. Treat invoking `$brrr` as an explicit request to run the verification required by the accepted contract.

Run focused checks while implementing and the complete relevant verification once after the implementation stabilizes. Distinguish failures caused by the change from unrelated baseline failures, and fix failures caused by the change before continuing.

## Review

Read the final diff as a reviewer. Compare it against the acceptance criteria, remove unnecessary complexity, confirm user changes remain intact, and run the verification affected by cleanup once more.

Finish with:

- The outcome delivered.
- The files changed.
- The verification that passed or failed.
- Any remaining blocker or separately scoped follow-up.

Treat commits, pushes, pull requests, merges, releases, and external mutations as a separate publication stage that requires explicit authorization.
