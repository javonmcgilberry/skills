---
name: know-thyself
description: "Mirror how the user works with AI coding agents, from their conversation history. Use when they ask about themselves (\"tell me about myself\", \"how do I work\", \"let's do a run\"), ask for coaching, ask whether a habit changed since a date or what they decided about something, want repeated corrections turned into rules, want a write-up for their team or lead, or want to set up their profile."
metadata:
  version: "0.6.0"
---

# Know thyself

The corpus holds every user turn from five local AI tools, and `scripts/convo.py` builds, measures, searches, and checks it, as `references/cli.md` lists. A claim is **traced** when you can point to the output it came from.

## Setup

1. **Context.** Run `python3 <skill dir>/scripts/convo.py context` once per session and follow its directives first. It refreshes the corpus and prints the profile. If it fails, say so and read `ME.md` from the data directory `paths` prints.
2. **Playbook.** Read the command's file below in full.
3. **Floor.** Read `references/voice.md` right before writing.
4. **Lint.** Write the draft reply to a temporary file, run `convo.py lint --mode <mode> [<report>] --reply <file>`, and fix every finding until it passes.

## Commands

| Command | Asked for | Playbook |
|---|---|---|
| mirror | the default: how they work, "let's do a run" | `references/mirror.md` |
| coach | "coach me on…", only when asked | `references/coach.md` |
| trend | whether a habit changed since a date | `references/lookups.md` |
| recall | what they said or decided about a topic | `references/lookups.md` |
| lessons | turning a repeated correction into a rule | `references/lessons.md` |
| share, lead | a write-up for their team, or for a manager or director | `references/audiences.md` |
| init | "set me up", or accepting the offer `NO_PROFILE` adds | `references/init.md` |

Routing:

- **Nothing to go on**, as in "know thyself" alone: follow `references/routing.md`.
- **A request about themselves** runs mirror.
- **Two commands fit:** ask once which. A run is finished when its files' **Done when** lists hold.

## Guardrails for every command

1. **The profile wins.** Use the profile's name and framing, and never name anything under its Keep out heading.
2. **Traced.** Every claim about the user carries a traced number, copied exactly, or a verbatim dated quote, and anything else is labeled inference. Signals are word matches that drift, so before a rate backs a claim, read `search --signal <id> --sample --limit 8` and drop it when fewer than six of the eight `match` fields are real.
3. **Verbatim.** Copy a quote character for character from search output, with the date its line shows, cutting only with "…". Paraphrase outside quotation marks.
4. **Privacy.** Quote short fragments without credentials, customer data, or personal details, and keep the user's name and paths out of skill files.
5. **Live configuration.** Propose edits to agent instructions and skills as diffs, applied after approval.
6. **Reports.** Write each report as a new file in the reports directory, adding `-2`, `-3` when its name is taken.
