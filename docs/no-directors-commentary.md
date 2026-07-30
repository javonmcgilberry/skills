# no-directors-commentary

> Text describes the thing. It does not describe itself, its structure, or its history.

No Director's Commentary catches the stuff agents leave behind when they narrate their own work: comments that restate the code, PR copy that begins with "Here's what I changed," vague TODOs, and migration stories that belong in a ticket.

It also flags code cleanup tricks such as `as any` used to silence types, try/catch blocks that do nothing, and helpers that only exist to look defensive.

Read the [skill](../skills/no-directors-commentary/SKILL.md) or jump straight to the [before-and-after examples](../skills/no-directors-commentary/references/rewrite-examples.md).

## Install

Install it from [javonmcgilberry/skills](https://github.com/javonmcgilberry/skills):

```sh
npx skills@latest add javonmcgilberry/skills --skill no-directors-commentary
```

Or copy it:

```sh
git clone https://github.com/javonmcgilberry/skills.git
cp -r skills/no-directors-commentary ~/.cursor/skills/
```

Or symlink it so the repo stays the source of truth:

```sh
git clone https://github.com/javonmcgilberry/skills.git ~/skills
cd ~/skills
./bin/link-skill.sh no-directors-commentary
```

## Package layout

```text
skills/no-directors-commentary/
├── SKILL.md
└── references/
    └── rewrite-examples.md
```

## References

These sources cover many of the same patterns from different angles.

### Documented AI code and review patterns

- [heavykenny/aislop rules](https://github.com/heavykenny/aislop/blob/main/docs/rules.md) - trivial and narrative comments, TODO stubs
- [rand/cc-polymath anti-slop code patterns](https://github.com/rand/cc-polymath/blob/main/skills/anti-slop/references/code-patterns.md) - obvious comments, docstrings, banners, mega-docstrings
- [flamehaven01/AI-SLOP-Detector patterns](https://github.com/flamehaven01/AI-SLOP-Detector/blob/main/docs/PATTERNS.md) - empty functions, placeholder docs, inflated comments
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

- [heavykenny/aislop](https://github.com/heavykenny/aislop) - lint rules with a code focus
- [flamehaven01/AI-SLOP-Detector](https://github.com/flamehaven01/AI-SLOP-Detector) - static checks for empty handlers and placeholder docs
- [humanizer](https://github.com/tenequm/skills) - long-form prose cleanup for essays and articles
