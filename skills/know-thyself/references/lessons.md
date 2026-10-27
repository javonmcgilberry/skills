# Lessons

Lessons turns a correction the user keeps repeating into a rule, check, or instruction line, so they stop making it.

1. **Find the corrections.** Over the window, search `--signal repeated_constraint`, `--signal agent_rework`, and `--signal overengineering` with `--context 2`, and run `score` to read `late_constraints`.
2. **Cluster by expectation.** Group the hits by the expectation the agent violated, whatever the wording.
3. **Keep what repeats.** Keep a cluster only when it spans three or more sessions on different days.
4. **Pick the most structural fix.** For each kept cluster, propose the most structural fix that works, in this order, a lint or check, a script, a skill edit, and last a line in the global agent instructions file (`AGENTS.md`, `CLAUDE.md`, or equivalent). Write the exact diff and count its evidence.
5. **Reply.** Give one numbered item per kept cluster, most sessions first, each with the expectation in one sentence, its evidence count in sessions and days, one verbatim dated quote, and the diff in a code block. Close by asking which fixes to apply, then apply the approved ones.

## Done when

- Every kept cluster spans three or more sessions on different days.
- Each kept cluster has an exact diff and its evidence count.
- Each fix is the most structural one in the order of step 4 that would work.
- The reply has the shape in step 5.
- Nothing was applied before the user approved it.
- Every item of the Done when list in `references/voice.md` holds.
