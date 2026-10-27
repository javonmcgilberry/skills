# Information architecture

Copy this into `.audit/docs.ia.md` and fill it from the repository. Adjust a page only with evidence, and record why.

## Readers

Name each reader and what they want. A typical set:

- **New engineer.** What it is, how data moves, how to run it.
- **Feature author.** The contract a change must keep, the code entry points, the test layers.
- **Reviewer.** The contract and the checks that prove it.
- **Release owner or on-call.** Releases, versions, rollback, debug by boundary.
- **Agent.** Precise rules, commands and boundaries, without restated prose.

## Pages

Each fact has exactly one owner page. Other pages link to it and give at most one orienting sentence.

| Page | Owns |
| --- | --- |
| `README.md` | What it is and for whom, At a glance, How it works, Limits, Where to read next |
| `docs/local-development.md` (or the repository's existing setup page) | Clone to a running system, env sourcing by item name, daily work, troubleshooting |
| `docs/architecture.md` | Ownership of each part, a Mermaid sequence diagram per flow, stored state, where the code starts, debug by boundary, and a parity table for siblings |
| A contract and testing page | The rules a change must keep, and every test layer with what it does not cover |
| `docs/reference.md` | Lookup without explanation: every script, address, env key by file (with which are secret), route, table, CI workflow, the docs check |
| `docs/glossary.md` | Each word once. Siblings use the same term for a shared concept, with an "also called" line |
| Release page (often the deployable's README) | Release, version selection, promotion, rollback of a live release, recovery |
| Agent files | Rules, accurate and non-duplicative. Commands an agent runs, then links |

Keep a page at its existing path when other pages, agent files or other repositories link it. Delete a page whose facts are stale, after moving the true ones to their owner. History files (changelogs) get factual fixes only and are excluded from the lever.

## README shape, in this order

1. Title, then two or three sentences on what it is and who it is for.
2. `## At a glance`. A map of the parts with their paths and local addresses, then the few commands that reach a running system.
3. `## How it works`. One Mermaid flowchart, then a short paragraph per group of arrows.
4. `## Limits`. What it does not do or guarantee, each with its consequence.
5. `## Where to read next`. "Start with the path for your role." A bullet per role. Then "Or look a topic up here." and a `| To | Read |` table.

## Siblings

When repositories implement the same thing for different providers, write one IA for all of them. Same paths, same headings, same section order. Each architecture page carries one byte-identical table with the columns Concern, each sibling, and Why it differs. A row with no provider reason says so, rather than inventing one. Check the table with `diff` after every writer.
