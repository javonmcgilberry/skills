# Init

`init` writes the user's profile, `ME.md` in the data directory that `context` names. It holds what their conversations can't show: who they are at work, what they want from this skill, who will read what it writes, and what must never be quoted or shared. Every mode reads the profile through `context` before it writes anything, so the user says each of these things once.

Run it when the user asks ("set me up", "get to know me"), when they accept the offer a `NO_PROFILE` directive adds, or when they say something in the profile is out of date.

## Step 1: Load what exists

Read the `profile` that `context` printed.

- **No profile:** explore, interview, and write it.
- **A profile exists:** ask what's stale or missing, and leave confirmed sections alone unless they change them.

Never overwrite the file silently. Show what changes before writing it.

## Step 2: Explore before asking

Run `stats` and read the busiest workspaces, the tools, and the hours, so you don't ask what their history already shows. Treat what you find as a guess to confirm, never as their answer.

## Step 3: Interview, once

Ask in one message, with your guesses filled in for them to correct, and only what the history can't answer.

1. **Who you are at work.** Role, team, and the kind of work they do most, such as frontend, infrastructure, or research.
2. **What you want from this.** For example to understand how they work, to get better at a part of it, or to explain how they work to someone else.
3. **Who reads it.** Only them, their team, or their lead or manager, which decides what a version to share may contain.
4. **Keep out.** Names, repositories, customers, projects, or topics never to quote or name in anything this skill writes.
5. **How to talk to you.** The name to use, and anything about tone, such as blunt or gentle.

Take an empty answer as an answer and leave that section out, rather than asking again.

## Step 4: Write ME.md

```markdown
# <the name they gave>

## Who you are at work
<role, team, and the work they do most, in their words>

## What you want from this
<the goal they named>

## Who reads it
<only me / my team / my lead, and what each may see>

## Keep out
- <one term per line, exactly as it should be matched>

## How to talk to you
<name and tone>
```

Keep each section to a few plain sentences in their words. `lint` checks every reply and report against the Keep out list, so each item there is one short term, such as a repository or a person's name, and not a sentence.

## Step 5: Resume

Tell them where the file is, that they can edit it any time, and that `init` updates it. If another request led here, go back and finish it, reading the new profile first.

## Done when

- `ME.md` exists in the data directory, with only the sections the user answered.
- The interview asked once, with guesses from `stats` for them to correct.
- Each Keep out item is one short term.
- Nothing in an existing profile changed without the user seeing the change first.
