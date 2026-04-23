# My Agent Skills

My skills for coding agents — pulled straight from the directories my agents load from. Cursor, Claude Code, Codex, anything that reads `SKILL.md` will pick them up.

Each skill is one folder with one markdown file. Take whatever's useful.

## Writing & communication

Skills that fix how agents write.

- **no-directors-commentary** — Strips the common AI-generated narration patterns from agent output: redundant JSDoc that restates the function signature, section-banner comments, generic TODO placeholders, meta-framing ("this PR adds..."), chat-preamble leaking into PR bodies ("here's the implementation..."), reader-addressing, and transition-era history. Use when reviewing agent-generated code, JSDoc, PR descriptions, commit messages, or docs.
  ```
  npx skills@latest add javonmcgilberry/skills/no-directors-commentary
  ```

## Installing manually

If you don't use the `skills` CLI, clone the repo and copy the folder you want into your agent's skills directory.

- Cursor: `~/.cursor/skills/`
- Claude Code: `~/.claude/skills/`
- Codex CLI: `~/.codex/skills/`
- Anywhere else: wherever your agent loads skills from

```sh
git clone https://github.com/javonmcgilberry/skills.git

cp -r skills/no-directors-commentary ~/.cursor/skills/
cp -r skills/no-directors-commentary ~/.claude/skills/
cp -r skills/no-directors-commentary ~/.codex/skills/
```

Or symlink so edits to the repo propagate to every runtime instantly:

```sh
git clone https://github.com/javonmcgilberry/skills.git ~/skills
cd ~/skills
./bin/link-skill.sh no-directors-commentary
```

`link-skill.sh` creates a chain: `runtime → ~/.agents/skills/<skill> → repo`. Edit the file in the repo once, every agent picks up the change. Pass any skill directory name from this repo.
