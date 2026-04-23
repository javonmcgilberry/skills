# Rewrite Examples

Before/after rewrites for each category in [SKILL.md](../SKILL.md).

When you catch yourself writing narration instead of content, rewrite by answering:

1. What does this code or file DO right now?
2. Why is it structured this way? (Only answer if the answer is STILL relevant, not "because we migrated from X.")
3. What should a reader new to this file need, without migration or process backstory?

## Meta-narration

### README that narrates process instead of the tool

**Before:**

> A synthesis of public write-ups on AI code patterns, validated against three parallel research passes to cut patterns that do not show up in real agent output.

**After:**

> Strips common AI-style narration from code comments, JSDoc, PRs, and READMEs. See `SKILL.md` for rules and `references/rewrite-examples.md` for rewrites.

### PR description that prefaces itself

**Before:**

> This PR adds a retry with jitter to `fetchX`. In this change we also bump the timeout from 5s to 15s because we were seeing 429s and timeouts in staging. It's worth noting that this fixes the flakiness observed last week.

**After:**

> Adds retry with jitter to `fetchX` and bumps the timeout from 5s to 15s. Handles 429s and intermittent timeouts from `<upstream>` under burst load.

## Redundant restatement

### Inline comments that English-ify the code

**Before:**

```ts
// Increment the counter
counter++;

// Loop over the items
for (const item of items) {
  // Process each item
  process(item);
}
```

**After:**

```ts
counter++;

for (const item of items) {
  process(item);
}
```

If intent is non-obvious, replace with a _why_ comment:

```ts
// `counter` tracks retries for the backoff calculation — not total attempts.
counter++;
```

### Redundant JSDoc (canonical AI pattern)

**Before:**

```ts
/**
 * Gets a user by their ID
 * @param {string} id - The ID of the user
 * @returns {Object} The user object
 */
export function getUserById(id: string): User {
  return db.users.findOne({ _id: id });
}
```

**After:**

```ts
export function getUserById(id: string): User {
  return db.users.findOne({ _id: id });
}
```

The signature already says everything the JSDoc said. Delete the block. If the function has a non-obvious constraint, keep only that:

```ts
/** Throws if <id> doesn't exist — caller must handle or pre-check. */
export function getUserById(id: string): User {
  return db.users.findOne({ _id: id });
}
```

### Mega-docstring bloat on a one-liner

**Before:**

```ts
/**
 * Formats a date in ISO 8601 format.
 *
 * @param {Date} date - The date to format. Must be a valid Date object,
 *   otherwise an Invalid Date string will be returned by the native
 *   toISOString() method.
 * @returns {string} The ISO 8601 formatted date string in UTC,
 *   following the pattern YYYY-MM-DDTHH:mm:ss.sssZ.
 * @throws {TypeError} If the input is not a Date object.
 * @example
 *   formatDate(new Date('2024-01-15T10:30:00Z'))
 *   // Returns: '2024-01-15T10:30:00.000Z'
 */
function formatDate(date: Date): string {
  return date.toISOString();
}
```

**After:**

```ts
function formatDate(date: Date): string {
  return date.toISOString();
}
```

The docstring was 15 lines documenting a 1-line call-through to a well-known native method. Delete it. Reserve mega-docstrings for exported public APIs where the metadata gets consumed by tooling.

### Generic TODO placeholder

**Before:**

```ts
async function chargeCard(card: Card, amount: number) {
  // TODO: Add error handling
  // TODO: Add validation
  return stripe.charges.create({ source: card.id, amount });
}
```

**After:** delete the useless TODOs, or replace with something concrete:

```ts
async function chargeCard(card: Card, amount: number) {
  // TODO: Map Stripe's `card_declined` to a domain-specific
  // DeclinedError so callers can distinguish from network failures.
  // See TICKET-4521.
  return stripe.charges.create({ source: card.id, amount });
}
```

## Self-important framing

### JSDoc that hedges instead of saying the thing

**Before:**

```ts
/**
 * Refreshes the token. Note that this function is idempotent,
 * so callers can safely retry on failure.
 */
```

**After:**

```ts
/**
 * Idempotent; callers may retry on failure. The refresh token
 * is rotated on every successful call — store the returned value.
 */
```

The "Note that" is the tell. Drop it and lead with the fact. Same goes for `"Importantly,"`, `"It's worth noting that..."`, `"Clearly,"` — any word whose only job is to tell the reader the next sentence matters.

## Reader-addressing and chat-preamble

### Walkthrough-style docs

**Before:**

> Let me walk you through how this handler works. First, it validates the payload, then dispatches to the right sub-handler.

**After:**

> Handler validates the payload, then dispatches to the matching sub-handler.

Drop the `"Let me walk you through"` preamble and the `"First... then..."` tour-guide cadence. The content of both versions is identical; the "After" just says it.

### Chat-preamble leaking into a commit body

**Before:**

> Here's the updated authentication flow. I've added a retry mechanism with exponential backoff to the `fetchToken` function, and I've also updated the error handling to properly propagate 429 responses. Hope this helps! Let me know if you'd like me to adjust anything.

**After:**

> Adds retry with exponential backoff to `fetchToken`. Propagates 429 responses instead of swallowing them.

## Transition narration

### File-level JSDoc narrating the port

**Before:**

```ts
/**
 * Thread handler. Ports <old-path>/threadHandler.ts to a new event
 * shape — no more <old-wrapper>, the HTTP webhook delivers the
 * event type directly.
 *
 * The old handler used `<legacy-method>` for incremental chunks.
 * The new shape doesn't have that affordance, so we send once with
 * the full answer.
 */
```

**After:**

```ts
/**
 * Thread handler — responds to `thread_started` and
 * `thread_context_changed` events. Sets the thread title + suggested
 * prompts and posts the opening message.
 */
```
