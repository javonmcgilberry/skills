---
name: useeffect-or-not
description: Review or refactor React code that uses useEffect. Use for derived or mirrored state, event-driven work, resets, fetching, subscriptions, React Compiler effect violations, and store or React Query ownership. Keep effects that synchronize React with an external system.
---

# useEffect or not

An effect connects React to a system React does not control. If you cannot name
that system, the work probably belongs in render, an event, or another owner.

## Review workflow

1. Read the effect, its cleanup, every dependency, and the code that changes
   those dependencies.
2. Name the owner: React, the action that caused the work, or an external
   system.
3. Load [references/pattern-catalog.md](references/pattern-catalog.md) when the
   effect derives or copies state, relays an action, resets state, fetches data,
   subscribes to a store, reconciles owners, or initializes the application.
4. Load [references/react-sources.md](references/react-sources.md) when the
   decision depends on React API behavior.
5. Classify the effect as `remove`, `keep`, or `repair`.
6. When refactoring, make the smallest change that preserves behavior. Remove
   state, refs, callbacks, imports, and suppressions that no longer have a job.
7. Verify the cases that can change the decision: initial render, later owner
   updates, the causing action, identity changes, remounts, cleanup, and stale
   async work.

## Classification

- `remove`: Name the React, event, query, router, or store owner. Move the work
  there without adding another source of truth.
- `keep`: Name the external system. Confirm that setup is repeatable, every
  reactive input is represented, cleanup undoes the same resource, and old
  async work cannot commit stale results.
- `repair`: Keep the external synchronization, but fix its dependencies,
  cleanup, repeatability, race handling, or ownership boundary.

## Review output

For every effect, report:

- its classification and trigger;
- its owner or external system;
- the smallest replacement or repair;
- the behavior verified and anything left unverified.

The review is complete when every effect has a named owner, a concrete outcome,
and verification that matches the relevant lifecycle.
