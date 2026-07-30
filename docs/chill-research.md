# Research first, Chill second

The [Chill guide](chill.md) covers the skill itself. This page tackles the question that came out of testing it: does loading a writing skill upfront change how an agent researches?

## Has anyone tested this?

Not exactly, at least not that I could find.

I found related work, but no published experiment comparing these two workflows:

```text
research with a plain-language skill loaded upfront

vs.

research normally, then rewrite the finished answer
```

Other studies show that prompt wording can change searches, tool calls, and the path through a task. They also show that persona and concision prompts can change behavior without improving accuracy.

We ran that comparison ourselves. Chill upfront created more research work without producing meaningfully better research.

## The closest research

### Prompt changes can reach the tools

[Mind the GAP: Text Safety Does Not Transfer to Tool-Call Safety in LLM Agents](https://arxiv.org/abs/2602.16943) tested six advanced models across six regulated domains. Each domain included seven jailbreak scenarios, three system-prompt conditions, and two prompt variants. The researchers analyzed 17,420 runs.

Changing the prompt moved tool-call safety by 21 to 57 percentage points. After adjusting for the number of comparisons, 16 of the 18 differences were still statistically significant.

The model's words and actions sometimes disagreed. It could refuse a request in its final text while still making the forbidden tool call. The prompt changed what the agent did, even when the final prose did not reveal it.

This was a safety benchmark with synthetic tools, not an open-ended research task. It measured forbidden calls rather than research quality, so it supports the mechanism without reproducing our experiment.

### Vercel ran into an ordering problem

Vercel compared four ways of giving coding agents current Next.js documentation in its [`AGENTS.md` eval](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals):

- No documentation scored 53 percent.
- An available skill also scored 53 percent because agents skipped it in 56 percent of cases.
- Explicitly telling the agent to invoke the skill raised the pass rate to 79 percent and skill use above 95 percent.
- Putting a compressed documentation index in persistent context scored 100 percent.

Vercel's explanation is all about sequencing. A skill creates a decision: should the agent read the docs first or inspect the project first? Persistent context removes that decision because the guidance is already available.

That looks a lot like what we saw with Chill. An instruction does not sit quietly until the final paragraph. It can change what the agent reads first and how it moves through the task.

Vercel tested Next.js implementation with technical documentation, not a writing skill, so the comparison only goes so far.

### One tool description changed Claude's searches

Anthropic gives a concrete example in [Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents). When Claude's web-search tool launched, the model kept adding `2025` to its queries. That small habit biased the results and hurt performance.

Anthropic fixed the behavior by changing the tool description. The search engine and model stayed the same; only the prompt text changed. The agent started searching differently.

The same article recommends measuring answer quality alongside tool calls, runtime, tokens, and errors. Extra calls might mean the agent is being thorough, or they might mean it is wandering. You have to grade the result before deciding whether the extra work helped.

Anthropic does not report a sample size or the size of the change for this example, so it is first-party engineering evidence rather than a controlled publication.

### OpenAI found that less prompt can be more

OpenAI's [current model guidance](https://developers.openai.com/api/docs/guides/latest-model) says that leaner system prompts improved scores by roughly 10 to 15 percent in a sample of internal coding-agent evals. Those configurations also reduced total tokens by 41 to 66 percent and cost by 33 to 67 percent.

OpenAI recommends starting with a prompt that works, removing one instruction group at a time, and rerunning representative evals. Keep style guidance when it expresses a real product requirement or fixes a measured problem. Broad instructions such as "be concise" may be unnecessary and can make answers too short.

That matches the policy we landed on. Technical context, hard constraints, approval boundaries, and success criteria belong upfront because they define a correct result. A communication preference has to prove that it helps the task before it earns permanent space in the prompt.

OpenAI presents those internal numbers as a guide, not a promise. The underlying dataset and the instruction groups that drove the improvement are not public, and the tests involved coding agents rather than research.

### Personas move the model, not necessarily the score

[When "A Helpful Assistant" Is Not Really Helpful](https://aclanthology.org/2024.findings-emnlp.888/) tested 162 persona roles across four model families and 2,410 factual questions.

The personas changed individual predictions, but they did not reliably improve accuracy over the control. Persona gender, role, and domain all influenced behavior, yet automatically choosing a "helpful" persona often performed no better than choosing one at random.

We saw the same general pattern: behavioral context moved the model without producing a dependable quality gain. This study did not involve agents, tools, research corpora, or writing skills, so it cannot explain Chill's extra searches by itself.

### Concision can push the other way

[Merlin's Whisper](https://aclanthology.org/2026.acl-long.917/) stops us from telling an overly neat story. The researchers searched for prompts that encouraged concise reasoning while preserving benchmark performance.

Across several models and reasoning tasks, they reduced generated tokens by roughly 40 percent on average. Reported reductions included 46 percent for Claude 3.7 on MATH-500 and 50 percent for Gemini 2.5 on the same benchmark.

So "simple language always creates more work" would be wrong. A prompt designed to reduce reasoning can do exactly that. Chill was designed to improve the final explanation while preserving detail, not to reduce reasoning effort. Different prompts, models, and tasks can push behavior in different directions.

## We cannot read the model's mind

It would be nice to open the hood and point to the exact thought that caused an extra search. We cannot do that.

Anthropic tested this problem directly in [Reasoning Models Don't Always Say What They Think](https://www.anthropic.com/research/reasoning-models-dont-say-think). Researchers planted hints in evaluation questions, checked whether models used them, and then looked for those hints in the models' written reasoning.

Claude 3.7 Sonnet mentioned the hint only 25 percent of the time on average. DeepSeek R1 mentioned it 39 percent of the time. In separate reward-hacking experiments, models exploited planted shortcuts in more than 99 percent of cases but usually admitted doing so in fewer than 2 percent.

Written reasoning can still be useful, but it is not a complete recording of the mechanism that produced an action. That is why we graded the things we could observe: searches, source reads, tool calls, citations, tokens, latency, and the final findings.

Anthropic makes the same distinction in [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). An agent has a trajectory, meaning the steps and tool calls it takes, and an outcome, meaning what it actually produces. You need both to understand whether extra work helped.

For Chill, those measurements told two different stories:

- The process changed. Chill produced more searches and tool calls.
- The outcome barely moved. Research quality stayed effectively tied.

## What the evidence supports

Four conclusions hold up:

1. Prompt wording can change an agent's actions, retrieval order, and tool use.
2. A behavioral or stylistic instruction does not automatically improve accuracy.
3. The same instruction can behave differently across models and tasks.
4. Tool activity and final quality need separate measurements.

These results are not universal. Chill may behave differently with another model or task, and rewriting afterward will not win every time.

Our test adds one specific result. With one model, three frozen research environments, and nine paired trials, loading Chill upfront increased research activity without producing a material quality gain.

That is enough to recommend research first and optional rewriting afterward for this workflow.

## The short version

> Instructions written for the reader can change how an agent works before it writes. In our experiment, a plain-language skill increased search activity without improving research quality.

Vercel gives us the closest industry comparison because its eval shows that changing how and when an agent receives guidance changes the route it takes. Anthropic's search-tool example shows how a few words in context can alter search behavior.

The persona and concision studies keep the conclusion honest. Prompt effects are real, but their direction and value depend on the exact prompt, model, and task.
