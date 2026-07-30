# My Agent Skills

These are the agent skills I use across Cursor, Claude Code, Codex, and anything else that reads `SKILL.md`. Take what helps. Change what doesn't.

## Skills

### Chill

Chill rewrites dense answers in plain language without sanding off the facts, caveats, or next steps. I usually run it after research or planning, once the real work is done.

I landed on that timing after testing both approaches. With Chill loaded upfront, agents searched more and made more tool calls, but their research wasn't any better.

> Note: Chill grew out of Dillon Mulroy's tiny `/bro` prompt ([original prompt](https://x.com/dillon_mulroy/status/2075751761462051181?s=20), [follow-up](https://x.com/dillon_mulroy/status/2079238358358778142), [example in use](https://x.com/dillon_mulroy/status/2079257150824620312)). I loved how natural it sounded. Chill adds one guardrail: simplify the language without dropping the meaning.

```sh
npx skills@latest add javonmcgilberry/skills --skill chill
```

[Guide and evaluation results](docs/chill.md) | [Skill source](skills/chill/SKILL.md)

### No Director's Commentary

No Director's Commentary cleans up the little signs that an agent wrote something and forgot to read it back. It catches obvious comments, pasted chat intros, unnecessary history, generic TODOs, and documentation that talks about itself.

```sh
npx skills@latest add javonmcgilberry/skills --skill no-directors-commentary
```

[Guide](docs/no-directors-commentary.md) | [Skill source](skills/no-directors-commentary/SKILL.md)

## Repository layout

```text
skills/  Installable skill packages
docs/    Guides and research
evals/   Reproducible evaluation fixtures, graders, and results
bin/     Local installation helpers
```

## Installing manually

If you don't use the `skills` CLI, clone the repo and copy whichever folder you want into your agent's skills directory.

- Cursor: `~/.cursor/skills/`
- Claude Code: `~/.claude/skills/`
- Codex CLI: `~/.codex/skills/`
- Anywhere else: wherever your agent loads skills from

```sh
git clone https://github.com/javonmcgilberry/skills.git

cp -r skills/chill ~/.codex/skills/
cp -r skills/no-directors-commentary ~/.cursor/skills/
cp -r skills/no-directors-commentary ~/.claude/skills/
cp -r skills/no-directors-commentary ~/.codex/skills/
```

You can also symlink a skill so edits in the repo show up in every runtime:

```sh
git clone https://github.com/javonmcgilberry/skills.git ~/skills
cd ~/skills
./bin/link-skill.sh no-directors-commentary
```

`link-skill.sh` makes the repository copy the source of truth. Pass any directory name from `skills/`.
