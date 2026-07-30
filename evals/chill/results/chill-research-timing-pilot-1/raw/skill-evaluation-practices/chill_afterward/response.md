The smallest credible setup is a separate eval project with 8 to 12 realistic prompts the skill hasn’t seen, a no-skill control, exact rule checks, and one blind human comparison. That’s enough to see whether the skill helps on those cases, but it isn’t enough to claim broad reliability without more representative cases and repeated runs. [ANTHROPIC] [OPENAI]

1. **Build a small test set.** Include common communication requests plus a few prompts where the skill shouldn’t activate. Hide the expected qualities from the runtime agent, and grade the final answer without requiring exact wording or one specific approach. [VERCEL-DESIGN] [ANTHROPIC]

2. **Compare with and without the skill.** Run the same model and prompts both ways, saving every output and transcript. This shows whether the skill actually improves the result instead of merely producing something acceptable. [SKILL-CREATOR] [VERCEL-DESIGN]

3. **Use exact checks for exact rules, and people for judgment calls.** Give stable IDs to rules covering forbidden phrases, required structure, length limits, and correct activation. Score activation separately from rule compliance. Then have a human blindly compare outputs for clarity, naturalness, tone, and overall preference. [VERCEL-DESIGN] [VERCEL-EVAL] A model grader can help later at larger scale, but it shouldn’t be the only subjective judge because model judges can be biased by answer position and length. [OPENAI]

Vercel’s work contributes the core evaluation pattern: unseen test cases, hidden expectations, no-skill controls, stable rule IDs, separate activation and compliance scores, and a mix of executable checks, model grading, and human review. It also shows how real production failures can become future regression cases. [VERCEL-DESIGN] [VERCEL-EVAL]

Keep the runtime skill lean. Put prompts, hidden expectations, graders, control settings, transcripts, outputs, scores, and review notes in the separate eval project. Add production failures there as regression fixtures instead of making the runtime skill larger. [VERCEL-EVAL]

This pilot can tell you whether the skill looks useful enough to keep developing and which rules fail most often. It cannot support reliability claims across domains, models, prompt styles, or repeated runs; that would require broader representative coverage, isolated execution, and repeated trials. [ANTHROPIC] [OPENAI]