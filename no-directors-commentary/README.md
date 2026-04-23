# no-directors-commentary

> Text describes the thing. It does not describe itself, its structure, or its history.

Pulls chatty AI habits out of JSDoc, `//` comments, PR and commit text, and READMEs: restating the obvious, talking about the PR or file instead of the change, hedges like "Note that", pasted chat intros ("Here's the code…"), and migration stories that belong in a ticket. It also trims the other common agent junk in code: `as any` to silence types, try/catch that does nothing useful, and helpers that only exist to look "defensive." Rulebook and greps: [`SKILL.md`](SKILL.md). Before/after edits: [`references/rewrite-examples.md`](references/rewrite-examples.md).

## Install

Repo: [javonmcgilberry/skills](https://github.com/javonmcgilberry/skills).

`npx`:

```sh
npx skills@latest add javonmcgilberry/skills/no-directors-commentary
```

Copy:

```sh
git clone https://github.com/javonmcgilberry/skills.git
cp -r skills/no-directors-commentary ~/.cursor/skills/
```

Symlink (repo stays the source of truth):

```sh
git clone https://github.com/javonmcgilberry/skills.git ~/skills
cd ~/skills
./bin/link-skill.sh no-directors-commentary
```

## Layout

```
no-directors-commentary/
├── README.md
├── SKILL.md
└── references/
    └── rewrite-examples.md
```

## References

External write-ups and tools (overlapping patterns; not duplicated in the package rule text).

**Documented AI code and review patterns**

- [heavykenny/aislop — rules](https://github.com/heavykenny/aislop/blob/main/docs/rules.md) — trivial and narrative comments, TODO stubs
- [rand/cc-polymath — anti-slop code patterns](https://github.com/rand/cc-polymath/blob/main/skills/anti-slop/references/code-patterns.md) — obvious comments, docstrings, banners, mega-docstrings
- [flamehaven01/AI-SLOP-Detector — PATTERNS](https://github.com/flamehaven01/AI-SLOP-Detector/blob/main/docs/PATTERNS.md) — empty functions, placeholder docs, inflated comments
- [avifenesh/agentsys — SLOP-PATTERNS](https://github.com/avifenesh/agentsys/blob/main/docs/reference/SLOP-PATTERNS.md)
- [Rohan, dev.to — “How I built a tool that detects AI slop in codebases” (2026)](https://dev.to/rohan_san_54b7ab7e50faa83/how-i-built-a-tool-that-detects-ai-slop-in-codebases-and-what-patterns-i-found-gmc)
- [Grizzly Peak — “The Annoying Things Copilot Still Inserts” (Larson, 2026)](https://www.grizzlypeaksoftware.com/articles/p/the-annoying-things-copilot-still-inserts-and-how-to-kill-them-permanently-rSK6Ib)
- [TechDebt.works — AI slop: AI-generated tech debt](https://techdebt.works/ai-slop/)
- [dev.to — “14 patterns AI code generators get wrong”](https://dev.to/radpdx/14-patterns-ai-code-generators-get-wrong-and-how-to-catch-them-45l9)
- [Lambda Curry — “How to avoid AI slop in your pull requests”](https://www.lambdacurry.dev/blog/how-to-avoid-ai-slop-in-your-pull-requests)
- [cursor-alternatives.com — Copilot best practices (2026)](https://cursor-alternatives.com/blog/ai-coding-best-practices-for-github-copilot/)

**AI prose (non-code) — hedging, voice, “signs of AI” lists**

- [Wikipedia — Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [Juzek & Ward, 2025 — “Why does ChatGPT ‘delve’ so much?” (PDF)](https://aclanthology.org/2025.coling-main.426.pdf)
- [The Verge — Wikipedia’s AI slop guide (2026)](https://www.theverge.com/news/865627/wikipedia-ai-slop-guide-anthropic-claude-skill)

**Staleness and wrong APIs (correctness, not “voice” — out of scope for the prose/comment pass; useful adjacent reading)**

- [Tian Pan — The deprecated API trap (2026)](https://tianpan.co/blog/2026-04-17-deprecated-api-trap-ai-coding-agents)
- [Pithy Cyborg — Why assistants suggest deprecated APIs](https://www.pithycyborg.com/why-do-ai-coding-assistants-keep-suggesting-deprecated-apis/)

**Agent skill packaging (file layout, not “our validation”)**

- [Anthropic — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Agent skills overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

**Related tools (shippable lints, not just prose review)**

- [heavykenny/aislop](https://github.com/heavykenny/aislop) — lint rules, code focus
- [flamehaven01/AI-SLOP-Detector](https://github.com/flamehaven01/AI-SLOP-Detector) — static checks for empty handlers and placeholder docs
- [humanizer](https://github.com/tenequm/skills) — long-form prose cleanup (essays, articles); use **no-directors-commentary** (above) for code and review copy
