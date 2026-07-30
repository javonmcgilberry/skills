The smallest credible evaluation is a separate pilot with a handful of representative, unseen tasks, each run once with the skill and once without it. Keep the runtime skill lean, and put the fixtures, expected outcomes, graders, transcripts, and results in a separate evaluation project.

**Pilot design**

Use 6-10 realistic cases that cover the skill’s main behavior and a few common failure modes. Hide the expected results from the agent, run every case in an isolated environment, and grade the final response without requiring one exact wording or process [ANTHROPIC]. Save both outputs and transcripts, then compare the skill against a no-skill baseline so you can tell whether the skill actually improves anything [SKILL-CREATOR].

Vercel’s main contribution is a useful evaluation structure: test whether the skill activates separately from whether the response follows its rules, use stable rule IDs, keep fixtures and expected changes hidden, include no-skill controls, and score rule compliance separately from similarity to strong shipped work [VERCEL-DESIGN]. For a simple communication skill, adopt that structure without copying the scale of Vercel’s program.

**Deterministic checks**

Use executable checks for requirements that have one clear answer [VERCEL-EVAL] [OPENAI]. These might verify that required content remains present, prohibited phrases are absent, source markers are preserved exactly, and the response stays within an explicit length or format constraint. Give every check a stable rule ID so failures remain comparable as the skill changes [VERCEL-DESIGN].

**Human judgment**

Use blind human comparison for qualities that depend on interpretation: clarity, naturalness, concision, whether the meaning changed, and whether the rewrite sounds appropriate for its audience [SKILL-CREATOR]. A model grader can help summarize these qualities, but it shouldn’t be the sole judge because model graders can favor particular positions or more verbose answers [OPENAI]. Combining executable checks, model grading, and human review follows Vercel’s broader approach [VERCEL-EVAL].

**Where artifacts belong**

The runtime skill should contain only the instructions needed during normal use. Put test fixtures, hidden expectations, grading code, baseline outputs, transcripts, score summaries, and failure cases in a separate evaluation project. When real failures appear, add sanitized versions as future evaluation cases rather than expanding the runtime skill with evaluation machinery [VERCEL-EVAL].

This pilot can show whether the skill produces a visible improvement on the selected cases and expose obvious regressions. It can’t support strong reliability claims, broad generalization claims, or precise success rates because those require more representative coverage and repeated trials [ANTHROPIC]. The right first decision is whether the skill consistently beats the no-skill baseline without losing required meaning; expand the suite only after real failures reveal missing coverage.