# Audiences

The audience decides what a good write-up looks like, the way a reader decides what a page is for. Choose it from who will read this piece, not from who the user is, and check it against "Who reads it" in the profile.

- **You.** The user reads it to recognize themselves and learn something. That's the mirror in `references/mirror.md`, with their own words, counts, and friction.
- **Your team.** Teammates read it to work well with them. They want working style, tools, and habits, in general terms, with no quotes and no friction unless the user names what they're happy to share. This is `share`.
- **Your lead.** A manager or director reads it to understand how this person works, the way they'd ask "how do you work?". They want the approach, the strengths, what the person is working on, and how they use AI agents, written in the first person so the user can send it as their own answer. This is `lead`.

Write a version for your team or your lead only when asked, for example "make a version I can share" or "help me explain how I work to my director".

## Gather

Use today's mirror report if one exists, and run the mirror's Gather steps first if not. A version for others draws only on patterns the mirror already traced, so it never makes a claim the mirror couldn't back.

## For your team

Write `YYYY-MM-DD-shareable.md` in the first person, with these sections in order.

1. **How I work.** A few paragraphs on working style.
2. **What I'm good at.** Three to five strengths.
3. **My tools and workflow.** The agents, tools, and routines they use day to day.
4. **What's changed.** In general terms.
5. **About this summary.** A short note that the skill read their own history on their machine, and that its advice comes from the public guides the know-thyself guide lists.

## For your lead

Write `YYYY-MM-DD-lead.md` in the first person, as an answer they could send, with these sections in order.

1. **How I work.** How they take a problem from vague to shipped, in two or three paragraphs.
2. **Where I'm strongest.** Three strengths, each with a count and its denominator, such as "in 41 of my last 120 sessions".
3. **What I'm working on.** One or two growth areas, taken only from friction the user agrees to share. Ask which before writing this section, and leave it out if they'd rather not.
4. **How I work with AI agents.** How they brief, check, and correct agents, in plain words a non-engineer can follow.
5. **About this summary.** The same note as the team version.

## Both versions

- Leave out quotes, file paths, links, ticket and repository names, coworkers' names, and everything in the profile's Keep out list.
- Counts keep their denominators, and every one traces to the mirror.
- The reply gives the path and tells the user to read and edit it before anyone else sees it.

## Done when

- The file is a new `YYYY-MM-DD-shareable.md` or `YYYY-MM-DD-lead.md` with its sections in order.
- It holds no quote, path, link, or Keep out term, and `lint --mode share` or `lint --mode lead` passes.
- The lead version's growth section covers only what the user agreed to share.
- The reply tells the user to read and edit it before anyone else sees it.
- Every item of the Done when list in `references/voice.md` holds, read for the first person and with no quotes.
