---
name: fresh-eyes
description: Overhaul a repository's Markdown docs so a newcomer can learn the system from the docs alone, checked claim by claim against the code, guarded by a rerunnable docs check, and proven by a cold reader. Use for /fresh-eyes, a docs overhaul or accuracy audit, refreshing docs after code changes, or making sibling repositories' docs match.
---

# Fresh eyes

Docs pass when a stranger, reading only the Markdown, answers the newcomer questions correctly as judged against the code. Everything here serves that test. The code is the only source of truth. Another doc is never evidence.

You coordinate. Writers, cold readers and checkers are subagents, briefed from [prompts.md](prompts.md). Route their models by the session's policy, a strong model for writing and checking and a small one for the cold reader, since a newcomer is the point.

Choose the branch first. A repository whose tracked docs check exists (`scripts/docs-check.mts` or its adapted path) has had an overhaul, so take [Refresh](#refresh). Any other repository takes the full Steps.

## Steps

1. **Set up.** Read each repository's `AGENTS.md`, `CLAUDE.md`, `README.md` and its PR conventions. Make a worktree per repository from the default branch, never the operator's checkout. Link `node_modules` if checks need it. Add `.audit/` to `$(git rev-parse --git-common-dir)/info/exclude`, so the trail stays local. Run the repository's full check and record that it was green. Copy the steps of this skill into `.audit/docs.todo.md`, with `skip: <reason>` for any you drop.
   Done when each worktree is green, excluded, and has its trail.

2. **Fix the questions.** Write 10 to 12 newcomer questions now, before anyone rewrites, so the test cannot be shaped around the new pages. Start from [questions.md](questions.md). For sibling repositories, write one set with a provider placeholder.
   Done when `.audit/questions.md` exists and nothing is rewritten yet.

3. **Build the lever.** Copy [lever/docs-check.mts](lever/docs-check.mts) and its test into `scripts/`, adapt it to the repository (the excluded history files, its package manager), and wire it into the repository's check script. Add a CI workflow without path filters that runs only Node, because a renamed code file breaks docs as surely as an edited doc does. Run it on the untouched docs. Its first findings are the audit's first leads.
   Done when the seeded test passes, the real run lists real problems, and the lever is committed on its own.

4. **Design the information architecture.** Write `.audit/docs.ia.md` from [ia.md](ia.md): readers, one owner page per fact, the README shape, and each existing file's fate (keep, rewrite, merge into X, delete). Decide a fate with evidence, for example a page naming test files that no longer exist is deleted. Design once for sibling repositories, and keep every page path and section order the same unless a provider truly differs.
   Done when every tracked `.md` has a fate.

5. **Audit and rewrite.** One writer per worktree, never two writers on one filesystem. The writer logs every factual claim in `.audit/docs.audit.tsv` (file, line, claim, verdict, evidence, fix) and then rewrites to the IA. Rules in agent files (`AGENTS.md`, `CLAUDE.md`, personas) keep their meaning unless code disproves them, and every change goes into `.audit/docs.rule-changes.md`.
   Done when every claim has a verdict with a code path and the check passes.

6. **Review the writer, not its summary.** Run `git status` and `git log` yourself. Writers' editor hooks leave uncommitted reformatting of Markdown the repository never formats, so discard that churn. Read the README. Verify in code any security or data claim the writer raised, and check the counterpart repository for the same defect.
   Done when the tree is clean and every claim you will repeat is one you saw in code.

7. **Cold read.** Export only the tracked Markdown into a scratch directory, so the reader cannot open code. A fresh reader answers the questions from that export. A separate checker grades each answer against the code (correct 1, partly 0.5, wrong 0), says whether the docs or the reader caused each error, and returns a fix list of real doc defects only.
   Done when you have a score and a fix list per repository.

8. **Fix and read again.** Give both fix lists to one fresh writer. For siblings, that one writer owns both worktrees, so shared tables stay byte-identical. Then export again and run a second cold read. Repeat while the score rises and real defects remain.
   Done when the last checker's fix list is applied and the score is recorded before and after.

9. **Stress-test the design.** As coordinator, read the whole set as a newcomer and write `.audit/design-stress-test.md`. Say where the architecture is the right tradeoff, where it is not ("this does X, maybe it should have done Y"), and what to change. Cover parity between siblings. Check each claim in code before you write it, because a read-back confidently states things the code contradicts.
   Done when every item names its evidence.

10. **Hand back.** Run the full check in every worktree, confirm the operator's checkouts are unchanged, and confirm no commit credits an agent. Push and open draft PRs only with the operator's go-ahead, in the repository's PR shape. Name security gaps there by category only, and give the details to the operator for Security. Report the counts, the files merged or deleted, the rule changes, the scores, the lever's result, and the stress test's decisions for the operator. Write the audited commit to `.audit/docs.baseline` and keep `.audit/questions.md`, so a later refresh starts from them.

## Refresh

A refresh keeps the layout and audits only what the code changed since the last pass. Set up as in step 1, in a worktree with the trail excluded.

1. **Find the baseline.** Use the commit in `.audit/docs.baseline`. Without one, use the last commit that changed `docs/reference.md`, and tell the operator that is the baseline you chose.
   Done when you have one commit and `git diff --name-only <baseline>..origin/<default>` lists the changed files.

2. **Run the lever.** Run the docs check on the default branch's head. Each failure is a defect to fix, and its file is in scope.
   Done when every failure is listed.

3. **Find the claims the change reaches.** With `.audit/docs.audit.tsv`, take every claim whose evidence path changed. Without it, search the docs for each changed file's path, and for each script, env key, route, export and port the diff adds, renames or removes. Add the pages that own the changed behavior per `.audit/docs.ia.md` or the README's To / Read table, since new behavior has no claim yet.
   Done when each changed file maps to its claims, or is marked as having none with a reason.

4. **Audit and fix.** One writer checks each claim in scope against the code, appends the verdicts to the audit log, and fixes the docs within the existing layout. Changing a page's job or adding a page needs the operator's go-ahead, because that is an overhaul decision. Then review the writer as in step 6.
   Done when every claim in scope has a verdict and the check passes.

5. **Cold read what moved.** Pick the stored questions whose answers touch the changed pages, using `.audit/questions.md` or, without it, a fresh set from [questions.md](questions.md) written before the fixes. Run step 7 on just those, and apply the checker's fixes as in step 8.
   Done when every picked question scores correct, or each remaining gap is reported.

6. **Hand back** as in step 10. Skip the stress test unless the change altered the architecture. Report the baseline, the files in scope, the claims checked and fixed, and the scores.

## Lever rules

The check must fail on what drifts: a repository path in code that does not exist, a relative link or anchor that does not resolve, a link that leaves the repository, and a script or package filter the manifests do not define. Gitignored paths and placeholders like `<site-id>` pass.

Prove each rule with a seeded break that fails on the check without that rule. A link that leaves the repository and re-enters at a real file is the seed for the escape rule, because a missing target fails for the wrong reason. After renaming the check, seed a dead path in a real doc and see it fail, because a self-run guard keyed on the file name goes quietly inert.

## Writing rules

Every page opens with its reader and its job. Diagrams are Mermaid. Examples come from real files or real runs. Env keys appear by name, never value. Follow the operator's prose style, and enforce the repository's own lint on code it ships.
