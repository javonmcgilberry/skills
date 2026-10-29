# Practices

Practices follow the life of one task. A backticked id names the scorecard dimension that measures the habit. Each practice ends with links to the public guides it comes from, and the links are listed under Sources at the bottom with the same ids as `references/sources.json`. A part marked "(this skill's own advice)" has no outside source.

## 1. Before the first prompt

- **Pick where the work runs.** Stay interactive while the shape is unclear, and go unattended once a machine can check the finish line and the task has worked reliably by hand. ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Pick the model and effort on purpose.** Small, fast models handle extraction, classification, and simple subagent jobs. Save the strongest model and high effort for design calls, ambiguous inputs, and stubborn bugs. (`model_choice`) ([Claude Code best practices][anth-cc-best-practices], [OpenAI reasoning best practices][oai-reasoning-bp], [A practical guide to building agents][oai-practical-guide])
- **Turn on only what the task needs.** Ask for a plan first, or use plan mode, when a change is complex or ambiguous, and send side work whose long output you don't need in the main thread to a subagent. ([Codex best practices][oai-codex-bp], [Claude Code subagents][cc-subagents])
- **Load narrow, clean context.** Point at the files, the ticket, and the raw logs or data, and leave the rest out. Anything newer than the model's training or private to your team needs a source you supply. (`task_context`, `raw_material`) ([Claude Code best practices][anth-cc-best-practices], [OpenAI prompt engineering][oai-prompt-eng], [Effective context engineering][anth-context-eng])
- **Expect variation and confident mistakes.** Runs differ, and a wrong answer sounds as sure as a right one, so plan the check before you start. ([OpenAI prompt engineering][oai-prompt-eng], [Reduce hallucinations][anth-reduce-hallucinations], [AI Fluency cheat sheet][aif-cheatsheet])

## 2. Brief it

A brief is a message to a capable colleague who just walked in and lacks your context, so it says what they would need to know to do the job well. ([Claude prompting best practices][anth-prompting-bp])

- **Lead with the outcome.** Start with the result you need and what good looks like, not a list of steps, and describe a process only when the process itself matters, so the agent has room to find the approach. Newer models can do worse when a prompt over-specifies the route. ([GPT-5.6 Sol prompting guidance][oai-sol-prompting], [Rethinking prompts for GPT-6 Astra][oai-astra-skills], [ChatGPT and Codex prompting][oai-prompting])
- **Add detail only when it changes the answer.** A short prompt is often enough. For bigger work, include the goal, the context, the output, and the boundaries only where each one helps, with no fixed template to fill in. ([ChatGPT and Codex prompting][oai-prompting], [Claude Code best practices][anth-cc-best-practices])
- **Define done before it starts.** Say what finished means, including running, checking, and fixing what fails when that's part of the job. The Sol guidance asks for success criteria and stopping conditions, and the Astra post adds that a careful model may stop after a first pass unless done is spelled out. ([GPT-5.6 Sol prompting guidance][oai-sol-prompting], [Rethinking prompts for GPT-6 Astra][oai-astra-skills])
- **Save absolute words for real invariants.** Use always, never, and must only for rules that truly can't bend, like safety or required fields, and give a decision rule for judgment calls. State each boundary once. The Sol guidance warns that repeated "ask first" language causes approval requests for safe actions, and the Astra post warns that strong boundary language can stop work you'd be happy to see continue. ([GPT-5.6 Sol prompting guidance][oai-sol-prompting], [Rethinking prompts for GPT-6 Astra][oai-astra-skills])
- **Role.** Give a working role that sets depth and audience, such as a reviewer reading a stranger's diff, and ask the model to do what that role does. A bare "you are an expert" label changes the vocabulary more than the method. (`role_framing`) ([Claude prompting best practices][anth-prompting-bp], [OpenAI prompt engineering][oai-prompt-eng], [How to be more ambitious][felix-ambitious])
- **Context.** Say what the model can't see, like the branch, the ticket, the files that matter, and what you tried. Most generic output traces back to a gap here. (`task_context`) ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Task.** Use a direct verb, such as fix, compare, or draft, because "can you suggest changes" gets suggestions while "change this function" gets the change. ([Claude prompting best practices][anth-prompting-bp])
- **Precise words.** A word with a settled meaning, like tautological for a test that restates the code or invariant for a rule that must always hold, carries a whole instruction, and the agent tends to reuse it in its own reasoning. ([Shipping thousands of PRs a month][prs-at-scale-talk])
- **Constraints.** State the scope, the non-goals, and how far the agent may go, from investigate up to merge. (`scope_control`, `shipping_authority`) ([Codex best practices][oai-codex-bp], [Claude prompting best practices][anth-prompting-bp], [ChatGPT and Codex prompting][oai-prompting])
- **Output format.** Name the shape and the reader, such as a PR description under 150 words for a reviewer. (`audience_format`) ([Claude prompting best practices][anth-prompting-bp], [ChatGPT and Codex prompting][oai-prompting], [AI Fluency cheat sheet][aif-cheatsheet])
- **Examples.** When the shape or tone matters, show three to five varied examples of the output you want, because examples steer format and tone more reliably than a description does. ([Claude prompting best practices][anth-prompting-bp])
- **Goal beyond the goal.** Say what should stay true after this lands, and why, with a hard number when one exists, like p95 under 200 ms. (`altitude`, `hard_target`) ([Claude prompting best practices][anth-prompting-bp], [Define success criteria][anth-success-criteria], [How to be more ambitious][felix-ambitious])
- **Method.** Ask what a top practitioner would do, such as bisecting or profiling first, and say "be ambitious" when you want more than the smallest thing that works. Tie any "keep going" to a check that must pass, because a bare "keep going until done" is on Anthropic's list of old advice you can stop following, as more likely to cause over-work than to fix a stall. (`expert_method`, `aim_high`) ([Claude Code best practices][anth-cc-best-practices], [How to be more ambitious][felix-ambitious])
- **Done-check.** Say what proves it worked besides the agent's word, like a failing test that turns green. (`outside_judge`) ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp], [How to be more ambitious][felix-ambitious])
- **Grounding.** Say "I don't know" is an acceptable answer, limit answers to the files you supplied, and ask for a file and line behind each claim. (`grounding`) ([Reduce hallucinations][anth-reduce-hallucinations], [Claude prompting best practices][anth-prompting-bp], [ChatGPT and Codex prompting][oai-prompting])

**Shift the strategy by task type.** Say which kind of task it is, then tighten and loosen to match, as in the table below (this skill's own advice). The guides back the parts, such as leaving an exploratory prompt loose and asking research to verify across sources. (`task_type`) ([Claude Code best practices][anth-cc-best-practices], [Claude prompting best practices][anth-prompting-bp])

| Task type | Tighten | Leave loose |
| --- | --- | --- |
| Analysis | Criteria, the standard, how to treat ambiguity | Phrasing |
| Research | The question, boundaries, source freshness, citations | How findings get synthesized |
| Drafting | Audience, tone, length, format | Word choice |
| Brainstorming | The goal and one or two guardrails | Volume and range, judged afterward |
| Code change | Scope, the done-check, patterns to follow | The approach inside an agreed plan |

## 3. Decompose

- **Split work that hides in one sentence.** "Move us off the old logger" is really four jobs. Inventory the call sites, pick the replacement API, convert one package, then convert the rest, checking the result after each. (`decompose`) ([Claude prompting best practices][anth-prompting-bp], [Building effective agents][anth-effective-agents], [pstack, Sequence work into verifiable units][pstack-sequence-units])
- **Verify the shared foundation first.** When release notes and a migration guide both come from one reading of the diff, confirm that reading first, or one misread spreads into both. ([Building effective agents][anth-effective-agents], [pstack, Sequence work into verifiable units][pstack-sequence-units])
- **Keep dependent steps in one session.** Reproduce, diagnose, and fix each need what the last step found, so they share a thread. Split off a step only when it stands alone or the thread is losing early detail. ([Claude Code subagents][cc-subagents], [Codex best practices][oai-codex-bp], [How Claude Code works][cc-how-it-works])

## 4. Iterate on the brief

- **Read a miss as a diagnosis.** Each kind of bad output points at the part of the brief that failed. ([Claude Code best practices][anth-cc-best-practices], [Reduce hallucinations][anth-reduce-hallucinations])

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Generic or off-base | Thin context | Add what the model couldn't see |
| Answers the wrong question | Vague task verb | Sharpen it to one instruction |
| Wrong length, tone, or shape | Missing constraint or format | State it |
| Invented facts or APIs | No grounding | Limit to sources, ask for citations |
| Edits files you didn't expect | Missing scope | Name allowed files and non-goals |
| Close, but one part misses | Nothing in the brief | Revise that part only |

- **Change one thing per round.** Review the result and ask for the specific change you want while keeping the rest, because rewriting the whole prompt throws away what worked. (`targeted_iteration`) ([ChatGPT and Codex prompting][oai-prompting])
- **Stop correcting when rounds go flat.** After two corrections that didn't land, stop piling on more and start over with one better prompt that folds in what you learned, and stop the task outright if it's doing work you no longer need. ([Claude Code best practices][anth-cc-best-practices], [ChatGPT and Codex prompting][oai-prompting])

## 5. Steer a long session

- **Scope before it runs.** Get a plan in read-only mode and read all of it. Fixing a plan costs one message, and fixing a diff costs a revert. (`plan_first`) ([Claude Code common workflows][cc-common-workflows], [Codex best practices][oai-codex-bp])
- **Have it interview you into a spec.** When you haven't thought a feature through, ask the agent to interview you until it could write the spec, save it to a file, and build from that file in a fresh session, so the build starts with clean context and a written definition of done. ([Claude Code best practices][anth-cc-best-practices])
- **Watch the first minute.** Press Esc the moment the agent drifts, since it stops mid-action and keeps everything up to that point, so you can redirect without losing work, and watch the first few runs of anything new before trusting it unattended. ([Claude Code best practices][anth-cc-best-practices])
- **Rewind instead of arguing forward.** Return to the checkpoint before the bad turn and re-brief, since stacked corrections keep the wrong path in context. (`rewind_restart`) ([Claude Code best practices][anth-cc-best-practices], [Claude Code checkpointing][cc-checkpointing])
- **Direct the compaction.** Tell the summary to keep the branch, failing tests, and decisions, or it may drop what the next hour needs. (`context_management`) ([Claude Code costs][cc-costs], [How Claude Code works][cc-how-it-works], [Effective context engineering][anth-context-eng])
- **Restart from a summary when rules fade.** Have the agent write the state and open questions to a file, then start fresh with that. (`context_management`) ([Claude prompting best practices][anth-prompting-bp], [Claude Code best practices][anth-cc-best-practices], [Effective context engineering][anth-context-eng])
- **Hand off once done is checkable.** When you can describe done better than the steps, run a goal or loop whose condition the transcript can prove, like test output, with a cap on how long it runs. (`long_runs`) ([Claude Code best practices][anth-cc-best-practices], [Building effective agents][anth-effective-agents])

## 6. Orchestrate

- **Delegate when the journey doesn't matter.** Send self-contained side work, such as research, broad searches, and test runs, to subagents that return a summary, so the main agent stays on the core problem. Anthropic now lists protecting the context window as old advice, and keeps subagents for parallel work, noisy output, and fresh review, each of which costs extra tokens. (`delegation`) ([Claude Code subagents][cc-subagents], [Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Brief a subagent like a stranger.** It starts without your conversation history or the files you've read. It can find and invoke project skills on its own, and listing them in its skills field preloads their full text. Give it these five things. ([Claude Code subagents][cc-subagents], [Anthropic multi-agent research system][anth-multi-agent], [Introduction to subagents course][skj-subagents])
  - The objective, in one sentence.
  - The exact files or scope.
  - The tools it may use, read-only unless it must edit.
  - A report with fixed sections, which tells it when it's done. (`structured_report`)
  - A section for obstacles and workarounds, so you don't rediscover them.
- **Write the description to steer the handoff.** The main agent reads it to decide when to launch and what to say, so "always name the files to review" yields focused briefs. ([Claude Code subagents][cc-subagents])
- **Hand test runs to a subagent.** A full test run is long output the main thread doesn't need, so let a subagent run it and ask it to return the failing tests and their errors, since a bare "tests failed" hides what you need. ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Skip subagents in three cases.**
  - Expert personas, because handing the same task to a subagent doesn't make the answer better. ([Claude Code best practices][anth-cc-best-practices])
  - Chains where each step needs the last one's findings, since detail gets lost at handoffs. ([Claude Code subagents][cc-subagents], [Anthropic multi-agent research system][anth-multi-agent])
  - Small jobs, where a fresh subagent spends longer gathering context than the work takes. ([Claude prompting best practices][anth-prompting-bp], [Claude Code best practices][anth-cc-best-practices])
- **Parallelize only independent work.** Give each writer its own worktree, or they overwrite each other. ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Keep the decision.** Judge each step by reversibility, cost of error, and who answers for it. Approving, merging, and anything irreversible stay with a person. ([Claude prompting best practices][anth-prompting-bp], [Claude Code best practices][anth-cc-best-practices], [A practical guide to building agents][oai-practical-guide])
- **Bring in another lens.** For work with stakes, add a reviewer with a different job, such as security, doing what that role really does. (`range_fields`) ([How to be more ambitious][felix-ambitious])

## 7. Check the output

- **Check against your request, the sources, and your field's standards.** Trace specific claims to the file or doc, because polish proves nothing. (`evidence_demand`) ([Reduce hallucinations][anth-reduce-hallucinations], [ChatGPT and Codex prompting][oai-prompting])
- **Check completeness separately.** An accurate answer can still skip what matters, often in the hardest file, so check every requirement against the spec. ([Claude Code best practices][anth-cc-best-practices], [ChatGPT and Codex prompting][oai-prompting])
- **Know the failure signatures.** Watch for unsourced precise numbers, functions that don't exist, claims about code nobody opened, and answers that change from one run to the next. (`challenge_assumptions`) ([Reduce hallucinations][anth-reduce-hallucinations], [Claude prompting best practices][anth-prompting-bp])
- **Verify in proportion to how little you watched.** A supervised edit needs a glance. An overnight or CI run needs the diff read before the summary, the tests, each claim re-checked, and its exit code. ([Claude Code best practices][anth-cc-best-practices], [Claude Code in Action][skj-cc-in-action])
- **Make tests a gate.** A hook that refuses to end the turn on red beats trusting "tests pass," and it should confirm no test was loosened. (`outside_judge`) ([Claude Code best practices][anth-cc-best-practices], [Claude prompting best practices][anth-prompting-bp])
- **Get a cold review on risky work.** A fresh agent reviewing from the brief and diff catches what the author rationalized. (`independent_review`) ([Claude Code best practices][anth-cc-best-practices])
- **Tell the reviewer what to skip.** Ask it to check the diff against the spec and report only gaps that affect correctness, skipping style, because a reviewer asked to find problems always finds some, and fixing every finding adds layers and tests nobody needs. ([Claude Code best practices][anth-cc-best-practices])
- **Decide in advance what a human signs off.** Customer-facing work, irreversible steps, security changes, regulated or private data, and money-driving numbers all get a person first. ([Claude Code best practices][anth-cc-best-practices], [A practical guide to building agents][oai-practical-guide])

## 8. Teach it once

- **Treat a wrong action as a bug report against the instructions file.** The second time you correct something, have the agent add the rule to AGENTS.md or CLAUDE.md. (`teach_once`) ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp], [pstack, Encode Lessons in Structure][pstack-encode-lessons])
- **Put each rule where it belongs.** Always-on conventions go in the instructions file, task procedures in a skill, and never-skip rules in a hook. Keep the file short, because every line competes for attention. ([Claude Code best practices][anth-cc-best-practices], [Claude Code memory][cc-memory], [Codex best practices][oai-codex-bp])
- **Write rules you can check.** "New handlers go in src/routes, one per file" works, and "follow good structure" can't be verified. ([Claude Code memory][cc-memory])
- **Name the replacement when you ban something.** "Use the shared logger, not console.log" closes the gap a bare ban leaves. ([Claude prompting best practices][anth-prompting-bp], [Claude Code best practices][anth-cc-best-practices])
- **Write rules plainly, without capitals.** Anthropic puts IMPORTANT and ALL CAPS on its list of old advice you can stop following, because current models follow a plainly worded line and piled-on emphasis makes them over-apply the rule. Turn a rule that can't bend into a hook, and shorten a file where lines get lost. ([Claude Code best practices][anth-cc-best-practices], [Claude prompting best practices][anth-prompting-bp])
- **Move hard rules to enforcement.** A pre-tool hook can block a push to main, and exit code 2 blocks while exit code 1 doesn't. (`guardrails`) ([Claude Code hooks guide][cc-hooks-guide], [Claude Code hooks reference][cc-hooks])
- **Match the permission mode to the job.** Auto mode is a classifier judging each action rather than a hard rule, so it can be wrong. Pair it with a test hook, give unattended jobs an allowlist, and keep approvals tight until you trust the repo. (`guardrails`) ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Give the agent a way to verify.** Claude Code bundles a verify skill that builds and runs your app to confirm a change does what it should. Write one for your project that also runs the tests and reports pass or fail with evidence (this skill's own advice), and keep it sharp as shared infrastructure, because it lets the agent finish without you relaying what you see. ([Claude Code skills][cc-skills], [Claude Code in Action][skj-cc-in-action], [Shipping thousands of PRs a month][prs-at-scale-talk])
- **Prefer checks a script runs.** Where a script can decide pass or fail, use it instead of a model's judgment, since in the OpenComputer study hard-coded verifiers agreed with human graders more closely than an LLM judge did. ([OpenComputer][paper-opencomputer])
- **Fix the environment, not the agent.** When several agents make the same mistake, change the codebase so the mistake is hard to make, with a lint rule, a narrower type, or one obvious place for each kind of code, so the rule meets the agent at the right moment instead of sitting in its context. Read a sample of agent work regularly to spot these, beyond the diffs you're asked to review. (`guardrails`) ([Shipping thousands of PRs a month][prs-at-scale-talk], [Harness engineering][oai-harness-eng], [pstack, Encode Lessons in Structure][pstack-encode-lessons])
- **Distill lessons from many sessions together.** Reading many past sessions side by side shows the lesson that repeats, which one session hides. In the Trace2Skill study, skills distilled this way from many runs carried over to other model sizes and families. ([Shipping thousands of PRs a month][prs-at-scale-talk], [Trace2Skill][paper-trace2skill])
- **Write skills that trigger and stay small.** Describe what it does and when, in words you type, keep each skill to one job, and push detail into reference files and scripts. When each run rebuilds the same tooling, move it into a script the skill calls, and leave the agent only the judgment calls. ([Skill authoring best practices][anth-skills-best], [Codex best practices][oai-codex-bp], [Shipping thousands of PRs a month][prs-at-scale-talk])

## 9. Automate and share

- **Automate the prompt you keep retyping.** Dependency audits, PR triage, and nightly checks belong in scheduled, headless, or CI runs once they work by hand. Pass headless runs their tools explicitly, cap turns, and ask for JSON. (`automation`) ([Claude Code best practices][anth-cc-best-practices], [Claude Code headless][cc-headless], [Codex best practices][oai-codex-bp])
- **Find where you're the relay.** Each time you paste an error, a screenshot, or a chat thread into the session, ask how the agent could fetch it itself, through a tool, a connector, or a scheduled job. (`automation`) ([Shipping thousands of PRs a month][prs-at-scale-talk])
- **Queue findings before fixing them.** Have a recurring job append what it finds to a file you read every few days, because findings seen together often share one cause that fixing each on arrival would miss. ([Shipping thousands of PRs a month][prs-at-scale-talk])
- **Let bots comment, not approve.** Automated PR review posts findings, and a person makes the merge call. ([Claude Code Code Review][cc-code-review])
- **Share what works.** Package trusted skills, hooks, and instructions as a versioned plugin or repo the team installs. (`share_setup`) ([Claude Code plugins][cc-plugins], [Codex best practices][oai-codex-bp])
- **Read a plugin before installing it.** Its code runs with your privileges and its hooks stack with your own. ([Claude Code plugins][cc-plugins], [Claude Code hooks guide][cc-hooks-guide], [Equipping agents with Agent Skills][anth-agent-skills-eng])

## 10. Judgment about data and access

- **Know the data rules before you paste.** Check what your organization allows first (this skill's own advice), and be deliberate about which tools you use and how your tool handles data and sensitive code. ([AI Fluency, Diligence][aif-diligence], [Claude Code security][cc-security])
- **Grant the least access that works.** Research gets read-only tools, and unattended jobs push only to their own branches. ([Claude Code best practices][anth-cc-best-practices], [Codex best practices][oai-codex-bp])
- **Keep workstreams apart.** Clear the session between unrelated tasks, and prune memory files when instructions go stale or conflict. ([Claude Code best practices][anth-cc-best-practices], [Claude Code memory][cc-memory])
- **Describe the workflow honestly.** Say what the tool did, what you did, and how you checked it, since "fully automated" is the claim the first miss disproves. ([Writing an AI diligence statement][aif-diligence-statement], [AI Fluency, Diligence][aif-diligence])

## Sources

[anth-cc-best-practices]: https://code.claude.com/docs/en/best-practices
[cc-memory]: https://code.claude.com/docs/en/memory
[cc-skills]: https://code.claude.com/docs/en/skills
[cc-subagents]: https://code.claude.com/docs/en/sub-agents
[cc-hooks-guide]: https://code.claude.com/docs/en/hooks-guide
[cc-hooks]: https://code.claude.com/docs/en/hooks
[cc-headless]: https://code.claude.com/docs/en/headless
[cc-common-workflows]: https://code.claude.com/docs/en/common-workflows
[cc-checkpointing]: https://code.claude.com/docs/en/checkpointing
[cc-plugins]: https://code.claude.com/docs/en/plugins
[cc-code-review]: https://code.claude.com/docs/en/code-review
[cc-costs]: https://code.claude.com/docs/en/costs
[cc-how-it-works]: https://code.claude.com/docs/en/how-claude-code-works
[cc-security]: https://code.claude.com/docs/en/security
[anth-prompting-bp]: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
[anth-reduce-hallucinations]: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
[anth-success-criteria]: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
[anth-skills-best]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[anth-effective-agents]: https://www.anthropic.com/research/building-effective-agents
[anth-context-eng]: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
[anth-multi-agent]: https://www.anthropic.com/research/multi-agent-research-system
[anth-agent-skills-eng]: https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
[skj-cc-in-action]: https://anthropic.skilljar.com/claude-code-in-action
[skj-subagents]: https://anthropic.skilljar.com/introduction-to-subagents
[aif-cheatsheet]: https://www-cdn.anthropic.com/4396730ed190e691a3712cf2fd6bfe35509deca2.pdf
[aif-diligence]: https://www-cdn.anthropic.com/34612aacbf37f6aa12140fc0a1aa216b63263aac.pdf
[aif-diligence-statement]: https://academy.claude.com/tutorials/writing-an-ai-diligence-statement
[oai-prompt-eng]: https://developers.openai.com/api/docs/guides/prompt-engineering
[oai-reasoning-bp]: https://developers.openai.com/api/docs/guides/reasoning-best-practices
[oai-codex-bp]: https://learn.chatgpt.com/guides/best-practices
[oai-prompting]: https://learn.chatgpt.com/docs/prompting
[oai-sol-prompting]: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md
[oai-astra-skills]: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
[oai-practical-guide]: https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
[felix-ambitious]: https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/
[pstack-sequence-units]: https://github.com/michael-denyer/pstack-claude/blob/HEAD/plugins/pstack/skills/principle-sequence-verifiable-units/SKILL.md
[pstack-encode-lessons]: https://github.com/michael-denyer/pstack-claude/blob/HEAD/plugins/pstack/skills/principle-encode-lessons-in-structure/SKILL.md
[prs-at-scale-talk]: https://www.youtube.com/watch?v=MN9dGgmLyso
[oai-harness-eng]: https://openai.com/index/harness-engineering/
[paper-trace2skill]: https://www.1kpapers.com/papers/trace2skill-distill-trajectory-local-lessons-into-transferable-agent-skills
[paper-opencomputer]: https://www.1kpapers.com/papers/opencomputer-verifiable-software-worlds-for-computer-use-agents
