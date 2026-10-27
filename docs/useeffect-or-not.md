# useEffect or Not

For anyone reviewing or refactoring React code that uses `useEffect`: the skill decides, effect by effect, whether it should stay, go, or be repaired.

## When to use it

Reach for it when an effect derives or mirrors state, relays an event, resets state, fetches data, subscribes to a store, reconciles two owners of the same data, or trips a React Compiler effect rule. An effect earns its place when it connects React to a system React doesn't control. When you can't name that system, the work usually belongs in render, an event handler, or another owner.

## What you get

For every effect, a classification (`remove`, `keep`, or `repair`), the owner or external system behind it, the smallest replacement or fix, and the cases verified, such as initial render, remounts, cleanup, and stale async work. When asked to refactor, it makes the smallest change that keeps behavior the same.

## Install

```sh
npx skills@latest add javonmcgilberry/skills --skill useeffect-or-not
```

Other ways to install are in [the README](../README.md#install). The skill's instructions are in [skills/useeffect-or-not/SKILL.md](../skills/useeffect-or-not/SKILL.md), with its pattern catalog and React references beside it.
