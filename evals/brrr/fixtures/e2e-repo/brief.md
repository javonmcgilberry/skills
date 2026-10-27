# Normalize repeated whitespace

Approval: Approved

## Outcome

`normalizeName` trims surrounding whitespace and replaces every internal whitespace run with one ordinary space.

## Acceptance criteria

- `normalizeName("  Ada   Lovelace  ")` returns `"Ada Lovelace"`.
- The existing focused test passes.
- The implementation remains local to `src/normalize-name.mjs`.
- The work is not committed or published.

## Execution

- [ ] Reproduce the failing test, implement the behavior, and record the passing verification.

## Verification

Run `npm test`.
