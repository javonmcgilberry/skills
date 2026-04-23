---
name: no-directors-commentary
description: "Strips AI narration from comments, JSDoc, PR and commit text, and READMEs: PR/file meta, process stories, chat-preamble, migration bookkeeping, redundant docstrings. In the same pass, flags as any, double casts, @ts-ignores, and no-op try/catch. For review and cleanup."
---

# No Director's Commentary

Text describes the thing. It does not describe itself, its structure, or its history.

AI coding agents leak a predictable set of narration patterns into the code and prose they ship:

- JSDoc that just restates the function signature (`/** Gets a user by id */` on `getUserById`)
- Comments that English-ify the next line (`// Increment the counter` above `counter++`)
- Section-banner comments (`// ============ AUTH ============`) splitting up a file
- Generic placeholder TODOs (`// TODO: Add error handling`)
- Meta-framing in PR descriptions and commits (`"This PR adds..."`, `"This commit fixes..."`)
- Chat-preamble leaking into delivered artifacts (`"Here's the implementation..."`, `"I've added..."`)
- Tour-guide and chatty **marketing** or essay READMEs and long JSDoc (`"Let me walk you through..."`) — not the same as signposting in a runbook; see [Calibration by surface](#calibration-by-surface) under Step 1
- Before/after comparison tables in PR bodies (`| Before | After |`)
- Transition / migration narration (`"Ported from..."`, `"After the migration..."`)
- Invented prior history when no predecessor actually existed
- **Code hygiene in the same diff:** `as any` and double casts to silence types, throwaway `@ts-expect-error` / `@ts-ignore`, try/catch that only logs and rethrows on internal paths, null checks the type system already made impossible, and one-off abstractions that the rest of the file does not use

Narration is the text talking _about_ the work instead of doing it; the code items are machinery that _looks_ safe or clever without helping. Treat both in one review pass.

A reader six months from now should not need archaeology to understand the code, and should not have to wade through narration about the text to get to the content. If a line only exists because of context from a transition or the text's own existence, it doesn't belong.

## Workflow

When invoked — either proactively while writing, or reactively while reviewing:

### Step 1 — Identify the surface

Which of these is the copy landing on?

- File-level JSDoc blocks
- Inline code comments
- README prose
- PR descriptions (not just commit subjects)
- Submission / pitch / proposal docs
- Runbooks and demos
- User-facing UI strings
- Error messages
- Test fixture comments

### Calibration by surface

The targets are the same (narration that **replaces** substance, template junk, meta handoffs), but **strictness** is not:

| Stricter (cut hard)                          | Lighter (keep useful signposting)                                                                           |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `//` and JSDoc next to code                  | **Runbooks**, install how-tos, **procedural** READMEs                                                       |
| PR / commit **bodies**                       | Numbered steps, “when to re-run,” “run the following” where it orients a cold reader                        |
| API docs where the signature already says it | A line of **operational** context (prereq, effect of a flag) that isn’t restating the command line for line |

A cold reader landing on a how-to **needs** steps and, often, a short _why_ or _when_ (e.g. re-generate when atoms change). That is not the same class as **process provenance** (“validated against our synthesis…”), **chat-preamble** (“here’s the implementation…”), or **line-for-line** English-ification of the next line of code. **Do not** greedily compress every “warm” sentence in a runbook — that’s out of scope and makes handoffs worse.

Commit messages: a one-liner is enough. Long commit **bodies** and diary-style handoffs get the stricter pass.

### Step 2 — Scan for banned patterns

If there's a diff, run the greps in [Pre-commit sweep](#pre-commit-sweep). If you're drafting from scratch, scan the prose against the [Banned patterns](#banned-patterns) categories. **Apply [Calibration by surface](#calibration-by-surface) before rewriting** — a grep hit in a runbook is often a false positive. Every remaining hit is a candidate for rewriting.

### Step 3 — Rewrite

For each hit, answer:

1. What does this code or file DO right now?
2. Why is it structured this way? (Only if still relevant — not migration lore, and not "because a lint or audit said so" unless that rule is a real, ongoing contract for callers.)
3. What should a reader new to the file need, without migration or process backstory?

[How to rewrite](#how-to-rewrite); [references/rewrite-examples.md](references/rewrite-examples.md) for before/after examples.

### Step 4 — Self-check

Before shipping, run the [Self-check](#self-check-before-shipping) list. If any of those phrases slipped back in, rewrite again.

## Banned patterns

### 1. Meta-narration — text referring to itself

The text announces its own existence, location, or role instead of delivering the content. The PR description IS the PR; the file IS the file; the section IS the section — prefixing them with "this PR" / "this file" / "this section" adds nothing.

- `"This PR adds retry with jitter"` → just `"Adds retry with jitter"`
- `"This commit fixes the null check"` (in the commit message itself)
- `"This file contains the routing logic"` (at the top of the file)
- `"This section covers authentication"` (right under `## Authentication`)
- `"This function handles token refresh"` (JSDoc on a function named `refreshToken`)
- `"In what follows we'll describe..."` / `"As mentioned above..."` / `"Earlier we discussed..."`
- `"This document describes..."` (at the top of a document)
- **Process and provenance** — how _this_ deliverable was produced, vetted, or signed off (not a `## References` list to others’ work).
  - e.g. `"Validated against…"`, `"Synthesis of our…"`, `"Culmination of…"` as _our_ story
- **Keep:** license line, one spec link, `See CONTRIBUTING` when that is the pointer — not _our_ audit narrative.
- **Citations and bibliographies (keep)** — `## References` / `## Further reading` with **third-party** links (pattern lists, papers, public vendor spec pages). **Strip** handoff process lines on the work — “we validated…”, “our audits…”, “synthesis of our work on it…” — not the outward links.

### 2. Self-important framing in docs, comments, and JSDoc

Words whose only job is to tell the reader that the next sentence matters. If the sentence matters, say the sentence. If it doesn't, delete it.

- `"Note that..."` / `"It's worth noting that..."` / `"It's important to note that..."` (discourse **hedging** in prose)
- `"Importantly,"` / `"Crucially,"` / `"Significantly,"`
- `"Obviously,"` / `"Clearly,"` / `"As you can see..."`

**Runbooks and how-tos:** `Note:` as a **label** for a real constraint or prerequisite (`Note: re-run when atoms change`, `Note: dry-run first`) is not the same as hedging — keep the substance; only cut it if the line is empty throat-clearing.

### 3. Redundant restatement — the canonical AI code-slop pattern

This is the #1 tell that code was agent-generated. The comment restates what the code already says. Takes up space, adds no information, rots the moment the code changes.

#### 3a. JSDoc that restates the signature

AI's most persistent sin. Given a function named `getUserById(id: string): User`, the model will happily produce:

```ts
/**
 * Gets a user by their ID
 * @param {string} id - The ID of the user
 * @returns {Object} The user object
 */
function getUserById(id: string): User { ... }
```

Every character is redundant with the signature. Delete the entire block, or replace it with a `why` that the signature doesn't convey (constraint, invariant, gotcha, caller contract).

- `/** Refreshes the token. */` on `refreshToken()` → delete
- `/** Validates the input */` on `validateInput()` → delete
- `/** Gets the config value */` on `getConfigValue()` → delete

Keep JSDoc only when the signature is genuinely ambiguous, or when it carries information the signature cannot: non-obvious constraints, thread-safety, side effects, rate-limit behavior.

#### 3b. Inline comments that English-ify the next line

- `// Increment the counter` above `counter++`
- `// Get the user by id` above `const user = getUserById(id)`
- `// Return the result` above `return result`
- `// Loop over items` above `for (const item of items)`
- `// Set the flag to true` above `this.isReady = true`

If the comment can be reproduced by reading the line below it, delete the comment. If intent is non-obvious, write _why_ — not _what_.

#### 3c. Section-banner comments

AI loves to impose structure on files by inserting ASCII-art banners. They're a code-smell signal, not documentation — if a file needs visual section breaks, that's a hint the file should be split.

- `// ================== AUTH ==================`
- `// ---------- Helpers ----------`
- `// ##########################################`
- `// # Routes #`
- `// ##########################################`

Delete banners. If the file is long enough that sections actually help, extract a module.

#### 3d. Generic placeholder TODOs

AI scatters vague TODOs as implementation cover. They never get addressed because there's no concrete unlock described.

- `// TODO: Add error handling`
- `// TODO: Implement this`
- `// TODO: Handle edge cases`
- `// TODO: Add validation`
- `// TODO: Add tests`

Either make the TODO concrete (what specifically is missing, what triggers it, what unblocks it) or delete it:

- `// TODO: Handle 429 response — currently throws, should retry with backoff when <Header> is present.`
- `// TODO: Add idempotency key when <migration> lands; see TICKET-123.`

A TODO that doesn't tell you what would complete it is a TODO that won't get completed.

### 4. Reader-addressing and chat-preamble artifacts

Agent chat output leaking into delivered artifacts. The most common symptom: AI writes a PR description, commit message, or README as if it's still replying to a chat prompt — explanatory preamble, first-person narration, meta commentary about what it just did.

#### 4a. Chat-preamble leaking into deliverables

Canonical tell that an AI reply got pasted verbatim into a commit body, PR description, or README without editing.

- `"Here's the implementation..."` / `"Here is the updated file..."`
- `"I've added..."` / `"I've implemented..."` / `"I've updated..."` / `"I've made the changes..."`
- `"I've refactored <X> to..."`
- `"As requested, I..."`
- `"Hope this helps!"` / `"Let me know if you'd like me to..."`
- `"The changes above..."` / `"The code below..."`

These are conversational glue. Delete the preamble, keep the change description. A PR body should describe the change, not describe the AI's act of making it.

#### 4b. Reader-addressing in docs

Talking TO the reader, or narrating the document's own navigation, instead of delivering the content. Appears most in AI-generated READMEs and long-form JSDoc.

- `"Dear reader..."` / `"If you're reading this..."`
- `"Let me explain..."` / `"Let me walk you through..."` / `"Now I'll describe..."`
- `"You might wonder why..."` / `"You might be asking yourself..."`
- `"Before we dive in..."` / `"Without further ado..."`
- `"First, let's look at..."` / `"Next, we'll consider..."`

### 5. Temporal / transition narration

Text that narrates what the system used to be, what it replaced, or how a migration moved. Spec-style process provenance belongs under §1, not here.

#### 5a. Transition narration

Drop any "ported from", "simplified from", "was tightly coupled to", "X is now Y":

- `"Ported from <old-path>"`
- `"Simplified from the old <feature> pipeline"`
- `"This used to duplicate the types across a package boundary"`
- `"After the migration, the system runs as..."`
- `"Not ported in this pass — <state> lives in the retired <component>"`
- `"The old <helper> is gone — <thing> now..."`

#### 5b. Invented prior history

If the prior version didn't exist, don't invent it. Especially dangerous in submission docs and READMEs where a "problem statement" can drift into fictional backstory:

- `"The old <product> shipped <thing> on day 1"` (when no prior product existed)
- `"<Product> used to publish via <some flow>"`
- `"Replaces the <old thing> with a <new thing>"` (if this is aspirational framing, not real history)
- `"We used to ship X, now we ship Y"` (if "we" never shipped X)

#### 5c. Comparative framing

Before/after tables, "vs the old X" sections, "changed since the migration":

- `## What changed vs the pre-migration build`
- `| Before | After |` comparison tables
- `"Before: <old stack>. After: <new stack>."`

#### 5d. References to deleted or legacy things

If something was removed, stop referring to it:

- Path references to removed directories
- Framework names no longer in use (unless documenting what the app explicitly does NOT use)
- `"The <component> still..."` / `"The <component> used to..."` when that component is gone
- `"Mirrors <old-path>/<old-file>"` when that file no longer exists

### 6. Code hygiene (non-narration slop)

The same diffs often mix both. Fix the type or the call site instead of papering over errors, and match the file’s style.

#### 6a. Type workarounds

- `as any` to bypass errors
- `as unknown as T` (double cast)
- `@ts-expect-error` / `@ts-ignore` / `// @ts-nocheck` to hide a mistake that should be fixed
- Casts and assertions that duplicate what strict types already express

#### 6b. Defensive overcoding

- `try`/`catch` in trusted call paths that only rethrow, log, or return `undefined` with no recovery
- Redundant `null` / `undefined` checks when a parameter is already validated or typed as non-optional
- Extra type guards in contexts where the type is already narrowed

#### 6c. Style drift in the file

- Local names or patterns that do not match sibling functions in the same module
- Formatting that disagrees with the file (when the file is consistent)
- Thin wrappers and indirection the rest of the file does not use

**What stays:** real error boundaries (I/O, user input, RPC), `catch` that maps errors to a result type, and guards that encode a protocol the type system cannot see.

## What IS allowed

### Describing current behavior

- `"Cache is held on ctx.scratch so multiple tools in one agent turn share the insights"`
- `"Every handler takes Ctx as its first argument; none import clients directly"`
- `"<External service> endpoints sit outside the narrow <Client> surface, so they go through ctx.<service>.apiCall"`

### Describing design decisions that are currently active

- `"Stateless orchestrator: builds an output from inputs, persists via ctx.db"`
- `"Fallback chain: primary source → secondary source → static heuristics"`

The test: is this design STILL the design? Yes → keep. No → rewrite.

### Comments that point at non-obvious intent

Code comments that explain _why_ — constraints, invariants, trade-offs, gotchas — are load-bearing and stay.

- `"Caller may pass a frozen ref; clone before mutating."` (not `"Clone the ref"`)
- `"Retry up to 3x; <upstream> returns 503 under burst load."` (not `"Retry 3 times"`)
- `"Leading slash required — the router strips trailing slashes and a bare '' collides with the index route."`

If the comment can be reproduced by reading the line below it, delete it instead.

### Error messages that say what went wrong

Concrete, specific, actionable.

- `"Token expired at <ts>; request a new one via /auth/refresh."`
- `"Invalid <field>: expected <shape>, got <shape>."`
- Not: `"An important error has occurred."` / `"Something went wrong."`

### PR and commit descriptions that describe the change directly

Drop the self-reference prefix; lead with the verb.

- `"Adds retry with jitter to `fetchX` to handle 429s."` (not `"This PR adds..."`)
- `"Fixes null check in <component> when <state> is empty."` (not `"In this commit we fix..."`)
- `"Adds <feature> behind <flag>; default off."`

### The problem space the product actually solves

State the current pain in present-day terms. No fictional predecessor unless it is a documented fact the reader needs.

- `"Users spend hours on <manual workflow> ... <gap> falls on the user, in whatever ad-hoc notes they scrape together, with no review affordance"`

### TODO markers that point at a concrete unlock

Narrow and actionable — who unblocks, what changes, or which ticket.

- `"Add a <feature> behind a <gate> when <condition> is met; see <TICKET>."`
- `"When <dependency> ships, replace this fallback with a <better path> (blocked until then)."`

### Runbooks, install docs, and procedural READMEs

- Numbered steps, “run the following,” and a **one-line when/why** (when to re-run, what the command affects) so a cold reader can execute safely
- Operational callouts that are **facts** (prereqs, flags, order-dependent steps) — not process stories about how the doc was written

Still cut: chat-preamble (“here’s the implementation…”), **this PR** in a paste that should be a changelog, and **provenance** (“validated against three passes…”) where it vouches for the **doc** instead of instructing the reader.

### Bibliographies and third-party source lists

- Outward link lists (aislop, cc-polymath, Wikipedia, papers, public vendor agent-skills docs)
- Adjacent topics you do not own (e.g. deprecated-API) as optional reading

Strip process lines that only describe a file’s or a team’s internal vetting on the work — not the reference list.

### Domain terms that happen to match banned words

Third-party vocabulary is fine even when it echoes banned words:

- `"bot token"` if the platform's docs call it that
- `"legacy token"` if the platform's docs call it that
- `"migration"` as a database term (schema migration, DB migration) — not "migration" meaning "our codebase transition"
- `"note"` as a product noun (Notes app) — not as framing ("Note that...")
- A runbook line starting with `Note:` when it states a **constraint** — that is a label, not the `"Note that..."` hedge in §2

## Pre-commit sweep

Point each `grep` at the diff so you only see **new** text:

```bash
DRAFTS=$(git diff main...HEAD)   # or: git diff --cached

# 1. Meta + process/provenance (^\+ = additions only)
echo "$DRAFTS" | grep -Ei '^\+.*(this (pr|commit|file|document|section|change|function|class|module|handler) (adds|does|contains|covers|handles|is responsible|describes)|in what follows|as mentioned above|earlier we |this document describes)'
echo "$DRAFTS" | grep -Ei '^\+.*(validated against|a synthesis of|synthesi[sz]ed from|culmination of|grounded in (independent |the )?research|per .* (guidance|best practices|authoring)|parallel (audit|run)s?|Composer [0-9]|N parallel|what got cut during|as part of the (audit|review)|how (it|th(e|is) (work|addition|file|package|repo)) was (written|vetted|built|develop))'

# 2. Self-important (comment / markdown line shapes; comma after Clearly/Obviously reduces false positives in code)
echo "$DRAFTS" | grep -Ei '^\+.*(//|#|/\*|\* |>\s|///).*\b(Note that|It\x27s worth noting|It is worth noting|important to note|As you can see|Remember that|Keep in mind)\b'
echo "$DRAFTS" | grep -Ei '^\+.*(//|#|/\*|\* |>\s|///).*(Importantly,|Crucially,|Significantly,|Obviously,|Clearly,)'

# 3a--d. Redundant / banners / TODO
echo "$DRAFTS" | grep -Ei '^\+[[:space:]]*//[[:space:]]*(Increment( the)?|Decrement( the)?|Loop over|Get the|Set the|Return the|Process each)'
echo "$DRAFTS" | grep -E '^\+.*(//|#|/\*).*(={4,}|-{4,}|#{4,}|\*{4,})'
echo "$DRAFTS" | grep -Ei '^\+.*TODO:.*(add (error handling|validation|tests?)|handle edge|implement( this| that)?)'

# 3e. Mega-docstring: if many * @param / * @returns in one hunk, open the file (see self-check)

# 4a. Chat-preamble (pipe through ^\+ first; second grep matches apostrophe patterns)
echo "$DRAFTS" | grep -Ei '^\+' | grep -Ei "here( is|'s) (the|an|your) (implementation|updated|changes|code|file)|\bi('ve| have) (added|implemented|updated|refactored|created|made)\b|as requested,? i|hope this helps|let me know if|the changes (above|below)|the code below"

# 4b. Reader-addressing
echo "$DRAFTS" | grep -Ei '^\+.*(dear reader|let me (explain|walk you through)|if you.re reading|before we dive in|without further ado|you might (wonder|be asking)|first, let.s look|next, we.ll (consider|look))'

# 5. Transition (phrase-bounded; avoids matching "imported")
echo "$DRAFTS" | grep -Ei '^\+.*(ported from|simplified from|not ported|in this pass|this phase( |:|[,.]|$)|lives in the retired|was tightly coupled|used to (live|duplicate|be)|after the migration|before the migration|during the migration|the old (handler|version|path|component|helper|codebase)\b|we used to (ship|have|rely))'

# 5c. Comparative (review: tables are sometimes legitimate)
echo "$DRAFTS" | grep -Ei '^\+.*(\| Before \| After \||changed vs the pre-migration|vs\.? the (old|previous) (build|version|stack)\b)'

# 6. Type suppressions (validate before deleting)
echo "$DRAFTS" | grep -Ei '^\+.*(\bas any\b|as unknown as|@ts-(expect-error|ignore|nocheck)\b)'
```

**How to read hits:** Candidates, not verdicts. Provenance-style patterns can match **inside a reference URL or title** (e.g. _validated_ in an article about validation) or in **bibliography lines** that only point outward — if the hunk is under `## References` / `## Further reading` and the line is a **third-party** link, keep it. A hit means “author is telling the story of the vetting on the change,” not “citation of someone else’s article.” **Migration** can hit runbooks. **`as any` / `@ts-ignore`:** re-read before deleting. **Security copy** (“validated input”) can match _validated_ — context wins.

**One-liner** (broad; review every line):

```bash
git diff main...HEAD | grep -Ei '^\+.*(this (pr|commit|file) (adds|does|contains)|this document describes|I.ve (added|implemented|updated)|I have (added|implemented|updated)|i have (added|implemented|updated)|ported from|simplified from|after the migration|in this pass|not ported|validated against|a synthesis of|culmination of|synthesi[sz]ed from|as mentioned above|let me walk|Note that,|Composer [0-9])'
```

State what the thing **is** or **does** — not the signing-off story, except a license line or a single external spec link when that is the whole point of the line.

## How to rewrite

When you catch yourself writing narration instead of content, rewrite by answering:

1. What does this code or file DO right now?
2. Why is it structured this way? (Only if still relevant — not "because we migrated from X" or "because an audit said so.")
3. What should a reader new to the file need, without migration or process backstory?

For worked rewrites, see [references/rewrite-examples.md](references/rewrite-examples.md).

## Self-check before shipping

If you catch yourself about to write any of these, stop and rewrite so the text says the thing directly.

**Redundant restatement (canonical AI tell):**

- JSDoc whose summary is the function name in prose (e.g., `/** Gets a user by id */` on `getUserById`)
- A comment that just English-ifies the line below it (e.g., `// increment counter` above `counter++`)
- Section-banner comments (`// ============ AUTH ============`)
- Generic TODOs without specificity (`// TODO: Add error handling`)

**Chat-preamble leaking into deliverables (canonical AI tell):**

- "Here's the implementation..." / "Here is the updated..."
- "I've added..." / "I've implemented..." / "I've updated..." / "I've refactored..."
- "As requested..." / "Hope this helps!" / "Let me know if..."
- "The changes above..." / "The code below..."

**Meta-narration (text about itself):**

- "This PR / commit / file / section / document / function..."
- "In what follows..." / "As mentioned above..." / "Earlier we discussed..."
- "This document describes..." / "This file contains..."

**Process and provenance (framing the vetting) — not the same as a `## References` list:**

- "Validated against _our_…" / "Culmination of _this_…" / "N parallel _our_…" (in the handoff text, not a bibliography line)
- A vendor link in References for reader use is fine; a sentence that only justifies a README’s layout with internal process is not

**Self-important framing:**

- "Note that..." / "It's worth noting that..." / "It's important to note that..."
- "Importantly," / "Crucially," / "Significantly,"
- "Obviously," / "Clearly," / "As you can see..."

**Reader-addressing / fourth-wall:**

- "Dear reader..." / "If you're reading this..."
- "Let me explain..." / "Let me walk you through..."
- "You might wonder..." / "You might be asking yourself..."
- "Before we dive in..." / "Without further ado..."

**Temporal / transition narration:**

- "was tightly coupled to..." / "used to live in..." / "simplified from the old..."
- "after the migration..." / "before the migration..."
- "the old version..." / "we used to..."
- "Ports <old path> to <new shape>..." / "The old <product> did X"
- `| Before | After |` tables in PR descriptions

**Code hygiene:**

- `as any` / `as unknown as` / wide `@ts-ignore` instead of a real type fix
- `try`/`catch` on internal calls that only log and rethrow
- Extra null checks where the value is already non-optional; redundant guards after a narrow
- New helpers that wrap a single call when the file is otherwise direct

If a line survives only because of one of the above framings, delete or rewrite until the text describes the thing on its own terms. If a line is a type escape hatch, either fix the types or keep it with a one-line reason another engineer will need.
