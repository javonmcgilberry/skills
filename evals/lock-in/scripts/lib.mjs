import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  ".."
);

export function parseArguments(values) {
  const parsed = new Map();
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    const value = values[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error(`Expected --name value, received: ${values.join(" ")}`);
    }
    parsed.set(key.slice(2), value);
  }
  return parsed;
}

export function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

export async function loadProject() {
  const fixtures = JSON.parse(
    await readFile(path.join(projectRoot, "fixtures.json"), "utf8")
  );
  const cases = await Promise.all(
    fixtures.cases.map(async relativePath =>
      JSON.parse(await readFile(path.join(projectRoot, relativePath), "utf8"))
    )
  );
  const skills = {
    "pre-checkpoint": await readFile(
      path.join(projectRoot, "baselines", "pre-checkpoint", "SKILL.md"),
      "utf8"
    ),
    current: await readFile(
      path.resolve(projectRoot, "..", "..", "skills", "lock-in", "SKILL.md"),
      "utf8"
    )
  };
  return { fixtures, cases, skills };
}

export function buildPrompt(evalCase) {
  return [
    "Request:",
    evalCase.request,
    "",
    "Evidence packet:",
    ...evalCase.evidence.map(item => `- ${item}`)
  ].join("\n");
}

export function developerInstructions(skill) {
  return [
    "Use the supplied Lock In skill to respond to the request.",
    "The evidence packet is complete. Do not use tools or ask for facts already present in it.",
    "Return only the next user-facing message required by the skill, then stop.",
    "Do not mention this evaluation.",
    "",
    skill
  ].join("\n");
}

export function scoreResponse(evalCase, answer) {
  const questionCount = answer.match(/\?/gu)?.length ?? 0;
  const lower = answer.toLowerCase();
  const matchedTerms = evalCase.expected_terms.filter(term =>
    lower.includes(term.toLowerCase())
  );
  const asksDiscoverableFact = evalCase.forbidden_question_terms.some(term =>
    lower.includes(term.toLowerCase())
  );
  const prematureBrief = /^#{1,3} (outcome|current behavior|decisions|scope|acceptance criteria|implementation units|execution|verification|open blockers)/imu.test(
    answer
  );
  const checks = {
    has_checkpoint: questionCount > 0,
    asks_one_question: questionCount === 1,
    gives_recommendation: /\brecommend(?:ation|ed|ing)?\b/iu.test(answer),
    avoids_premature_brief: !prematureBrief,
    grounds_question_in_evidence:
      matchedTerms.length >= evalCase.minimum_expected_terms,
    avoids_discoverable_fact_question: !asksDiscoverableFact
  };
  const rawScore =
    (checks.has_checkpoint ? 30 : 0) +
    (checks.asks_one_question ? 15 : 0) +
    (checks.gives_recommendation ? 20 : 0) +
    (checks.avoids_premature_brief ? 20 : 0) +
    (checks.grounds_question_in_evidence ? 15 : 0) -
    (checks.avoids_discoverable_fact_question ? 0 : 20);
  return {
    score: Math.max(0, rawScore),
    question_count: questionCount,
    matched_terms: matchedTerms,
    checks
  };
}
