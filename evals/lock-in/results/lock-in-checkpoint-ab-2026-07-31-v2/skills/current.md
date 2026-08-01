---
name: lock-in
description: Investigate a proposed code change, resolve decisions that materially affect its implementation, and produce one approval-ready executable brief. Use when a request is ambiguous, spans meaningful product or technical choices, needs repository or documentation evidence, or should be clarified before implementation begins.
---

# Lock In

Turn an uncertain request into one implementation contract. Finish when the user can approve the brief without needing to reinterpret it.

## Establish the source of truth

1. Read the user request, referenced artifacts, repository instructions, and current working-tree state.
2. Inspect the code and documentation that determine current behavior. Verify external facts against primary sources when they affect the decision.
3. Reuse a user-provided spec or the repository's established planning location. Create one brief instead of parallel planning documents.

## Resolve uncertainty

Separate facts, user-confirmed decisions, inferred decisions, and open decisions. Look up facts instead of asking the user for information the available sources can answer.

Build a decision inventory before writing the final brief. For each decision, record:

- What is being decided.
- Whether the user confirmed it, the evidence implies it, or it remains open.
- The recommended answer and the consequence of choosing it.

Ask about open decisions one at a time, starting with the decision that would change the work most. State the recommendation plainly with "I recommend," then end the checkpoint with exactly one direct question. Keep skill narration out of the message. Wait for the user's answer before continuing and record each answer so it is settled once.

Every Lock In run must include a user checkpoint before the final brief is written. When no open decision remains, show the inferred decisions in a compact summary, state the recommended contract, and end with exactly one direct confirmation question. Do not treat research, silence, or the absence of objections as confirmation.

## Write the brief

Keep the brief proportional to the work. Include:

- **Outcome:** The observable result.
- **Current behavior:** The relevant behavior and evidence.
- **Decisions:** Confirmed product and technical choices with short reasoning.
- **Scope:** The repositories, systems, and behaviors owned by this change.
- **Acceptance criteria:** Verifiable completion conditions.
- **Implementation units:** Dependency-ordered slices with clear boundaries.
- **Execution:** An unchecked list mirroring the implementation units so `$brrr` can record progress in place.
- **Verification:** Focused tests, end-to-end checks, and regression coverage required.
- **Open blockers:** Only unresolved matters that prevent safe execution.
- **Approval:** Mark the brief `Draft` until the user approves it, then record `Approved` with the approval date.

Use exact file paths, commands, identifiers, and links when they help the executor act without rediscovery. Keep implementation details open when the code should determine them during execution.

Record decisions in the brief's **Decisions** section. Reserve a separate ADR for a durable architectural choice when the repository already has an ADR convention, then link that ADR from the brief rather than repeating it.

## Hand off

After the user confirms the decision inventory, review the brief for contradictions, duplicated requirements, speculative work, and decisions the user has already settled. Confirm that its execution checklist and acceptance criteria describe the same work.

Present the brief with **Approval** set to `Draft` and ask the user to approve or revise it. Mark it `Approved` only after an explicit approval response. Approval of an individual decision does not approve the whole brief.

Only inspect sources and create or update the canonical brief. Leave implementation and publication to the execution stage.

## Deferred / Open Questions

### From 2026-07-31 review

- **ADR ownership** - Decisions (P2, coherence, confidence 100)

  The boundary is unclear about whether Lock In may create an ADR or should only reference an existing ADR. Settle this before a Lock In brief needs to introduce a durable architectural decision.
