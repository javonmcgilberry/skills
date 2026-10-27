# No Director's Commentary

> Text describes the thing. It does not describe itself, its structure, or its history.

You've installed No Director's Commentary, or you're deciding whether to, and you want to know what it will cut from your agent's output and what it will leave alone. It catches the stuff agents leave behind when they narrate their own work, and it keeps the lines a reader needs, so the review pass shortens text without stripping its substance. Install it with the commands in [the README](../README.md#install), and read the [skill](../skills/no-directors-commentary/SKILL.md) or jump straight to the [before-and-after examples](../skills/no-directors-commentary/references/rewrite-examples.md).

## What it flags

The skill sorts what it removes into six numbered categories, and the first five are narration, text talking about the work instead of doing it.

1. **Meta-narration.** PR copy that opens "This PR adds", a document that says "this document describes", and lines that vouch for the doc's own vetting.
2. **Self-important framing.** "Note that", "It's worth noting", and "As you can see" used as throat-clearing in docs, comments, and JSDoc.
3. **Redundant restatement.** JSDoc that repeats the signature, comments that put the next line into English, section banners, and TODOs like `// TODO: Add error handling` that never say what would finish them.
4. **Reader-addressing and chat preamble.** "Here's the implementation" and "I've added" pasted into a commit or PR, and tour-guide prose such as "Let me walk you through".
5. **Temporal and transition narration.** "Ported from", "After the migration", invented prior history, before-and-after tables, and references to code that no longer exists.

The sixth category is code hygiene, which it reviews in the same pass because the same diffs mix both. It flags `as any` and double casts that silence the type checker, `@ts-ignore` and `@ts-expect-error` hiding a real mistake, try/catch on trusted paths that only rethrows, logs, or returns `undefined` with no recovery, null checks and type guards the types already rule out, and thin wrappers the rest of the file doesn't use.

On a diff it starts with the grep commands in its Pre-commit sweep section, and each hit is a candidate to reread rather than a verdict.

## What it keeps

The skill's "What IS allowed" section protects these, so a cleanup doesn't remove information along with the narration.

- Comments that describe current behavior or a design decision that's still the design.
- Comments that explain why, such as a constraint, an invariant, or a gotcha the next line can't show.
- Error messages that say what went wrong and what to do.
- PR and commit text that leads with the verb and describes the change.
- TODOs that name a concrete unlock, such as a ticket, a dependency, or a condition.
- Runbook and install steps, including a one-line note on when to rerun something or what a flag affects.
- Reference lists of third-party links, and domain words that only look like banned ones, such as a schema "migration" or a platform's "legacy token".

How hard it cuts depends on where the text lands. Comments next to code, PR and commit bodies, and API docs get the strict pass, while runbooks and procedural READMEs keep their signposting, because a cold reader running a how-to needs the steps and a short why.

## Package layout

```text
skills/no-directors-commentary/
├── SKILL.md
└── references/
    └── rewrite-examples.md
```

`SKILL.md` holds the workflow, the six categories, what's allowed, the pre-commit greps, and a self-check list. `references/rewrite-examples.md` has before-and-after rewrites for the five narration categories.

## References

These sources cover many of the same patterns from different angles.

### Documented AI code and review patterns

- [heavykenny/aislop rules](https://github.com/heavykenny/aislop/blob/main/docs/rules.md), on trivial and narrative comments and TODO stubs
- [rand/cc-polymath anti-slop code patterns](https://github.com/rand/cc-polymath/blob/main/skills/anti-slop/references/code-patterns.md), on obvious comments, docstrings, banners, and mega-docstrings
- [flamehaven01/AI-SLOP-Detector patterns](https://github.com/flamehaven01/AI-SLOP-Detector/blob/main/docs/PATTERNS.md), on empty functions, placeholder docs, and inflated comments
- [avifenesh/agentsys slop patterns](https://github.com/avifenesh/agentsys/blob/main/docs/reference/SLOP-PATTERNS.md)
- [Rohan, "How I built a tool that detects AI slop in codebases" (2026)](https://dev.to/rohan_san_54b7ab7e50faa83/how-i-built-a-tool-that-detects-ai-slop-in-codebases-and-what-patterns-i-found-gmc)
- [Grizzly Peak, "The Annoying Things Copilot Still Inserts" (2026)](https://www.grizzlypeaksoftware.com/articles/p/the-annoying-things-copilot-still-inserts-and-how-to-kill-them-permanently-rSK6Ib)
- [TechDebt.works on AI-generated tech debt](https://techdebt.works/ai-slop/)
- [Fourteen patterns AI code generators get wrong](https://dev.to/radpdx/14-patterns-ai-code-generators-get-wrong-and-how-to-catch-them-45l9)
- [Lambda Curry on avoiding AI slop in pull requests](https://www.lambdacurry.dev/blog/how-to-avoid-ai-slop-in-your-pull-requests)
- [Copilot best practices](https://cursor-alternatives.com/blog/ai-coding-best-practices-for-github-copilot/)

### AI prose

- [Wikipedia's signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Juzek and Ward, "Why does ChatGPT 'delve' so much?" (2025)](https://aclanthology.org/2025.coling-main.426.pdf)
- [The Verge on Wikipedia's AI slop guide (2026)](https://www.theverge.com/news/865627/wikipedia-ai-slop-guide-anthropic-claude-skill)

### Stale and incorrect APIs

- [Tian Pan on the deprecated API trap (2026)](https://tianpan.co/blog/2026-04-17-deprecated-api-trap-ai-coding-agents)
- [Pithy Cyborg on why assistants suggest deprecated APIs](https://www.pithycyborg.com/why-do-ai-coding-assistants-keep-suggesting-deprecated-apis/)

### Agent skill packaging

- [Anthropic skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic agent skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

### Related tools

- [heavykenny/aislop](https://github.com/heavykenny/aislop), lint rules with a code focus
- [flamehaven01/AI-SLOP-Detector](https://github.com/flamehaven01/AI-SLOP-Detector), static checks for empty handlers and placeholder docs
- [humanizer](https://github.com/tenequm/skills), long-form prose cleanup for essays and articles
