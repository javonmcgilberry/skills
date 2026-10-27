# Lock In

For anyone about to hand an agent a request that isn't settled yet: Lock In turns it into one brief you can approve before any code is written.

## When to use it

Reach for it when a request is ambiguous, spans real product or technical choices, or needs evidence from the repository or its docs before anyone should start building. It investigates, asks only the questions whose answers change the implementation, and finishes with a single executable brief.

## What you get

An approval-ready brief: the outcome, the decisions it settled and why, the scope, and how to tell the work is done. When you approve it, hand it to [Brrr](brrr.md) to build.

## Install

```sh
npx skills@latest add javonmcgilberry/skills --skill lock-in
```

Other ways to install are in [the README](../README.md#install). The skill's instructions are in [skills/lock-in/SKILL.md](../skills/lock-in/SKILL.md).
