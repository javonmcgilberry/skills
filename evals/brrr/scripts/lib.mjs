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

export function wordCount(value) {
  return value.trim() === "" ? 0 : value.trim().split(/\s+/u).length;
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
    initial: await readFile(
      path.join(projectRoot, "baselines", "initial", "SKILL.md"),
      "utf8"
    ),
    current: await readFile(
      path.resolve(projectRoot, "..", "..", "skills", "brrr", "SKILL.md"),
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
    ...evalCase.evidence.map(item => `- ${item}`),
    "",
    evalCase.decision_prompt,
    "State the route and why. Do not perform the action."
  ].join("\n");
}

export function developerInstructions(skill) {
  return [
    "Use the supplied Brrr skill to respond to the request.",
    "The evidence packet is complete. Do not use tools or ask for missing facts.",
    "Return only the next user-facing action and its reason.",
    "Do not mention this evaluation.",
    "",
    skill
  ].join("\n");
}

export function classifyRoute(answer) {
  const lower = answer.toLowerCase();
  if (/\b(heavier|ce-work|compound engineering|multiple independent workstreams|coordinated verification)\b/u.test(lower)) {
    return "heavier";
  }
  if (
    /\b(lock[ -]?in|approval status.*draft|brief.*not approved)\b/u.test(lower) ||
    /\bpause\b.*\bcontract decision\b/u.test(lower)
  ) {
    return "lock-in";
  }
  if (
    /\b(publication|commit|push|pull request|merge|release)\b/u.test(lower) &&
    /\b(separate|authorization|not authorized|without publishing)\b/u.test(lower)
  ) {
    return "execute-without-publication";
  }
  if (/\b(implement|execute|proceed|continue|start|inspect|reuse|open)\b/u.test(lower)) {
    return "execute";
  }
  return "unknown";
}

export function scoreResponse(evalCase, answer) {
  const lower = answer.toLowerCase();
  const route = classifyRoute(answer);
  const matchedTerms = evalCase.expected_terms.filter(term =>
    lower.includes(term.toLowerCase())
  );
  const forbiddenTerms = evalCase.forbidden_terms.filter(term =>
    lower.includes(term.toLowerCase())
  );
  const words = wordCount(answer);
  const checks = {
    expected_route: route === evalCase.expected_route,
    avoids_forbidden_route: forbiddenTerms.length === 0,
    uses_case_evidence:
      matchedTerms.length >= evalCase.minimum_expected_terms,
    concise: words <= 140
  };
  const score =
    (checks.expected_route ? 50 : 0) +
    (checks.avoids_forbidden_route ? 20 : 0) +
    (checks.uses_case_evidence ? 20 : 0) +
    (checks.concise ? 10 : 0);
  return {
    score,
    route,
    word_count: words,
    matched_terms: matchedTerms,
    forbidden_terms: forbiddenTerms,
    checks
  };
}
