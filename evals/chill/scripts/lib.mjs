import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  ".."
);

export function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function wordCount(value) {
  return value.trim() === "" ? 0 : value.trim().split(/\s+/u).length;
}

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

export async function loadProject() {
  const fixtures = JSON.parse(
    await readFile(path.join(projectRoot, "fixtures.json"), "utf8")
  );
  const manifest = JSON.parse(
    await readFile(path.join(projectRoot, "baselines", "manifest.json"), "utf8")
  );
  const skill = await readFile(
    path.join(projectRoot, manifest.snapshot_path),
    "utf8"
  );
  const cases = await Promise.all(
    fixtures.cases.map(async relativePath => {
      const contents = await readFile(path.join(projectRoot, relativePath), "utf8");
      return JSON.parse(contents);
    })
  );
  return { fixtures, manifest, skill, cases };
}

export function commonDeveloperInstructions() {
  return [
    "Complete the user's research or planning task using only the supplied source packet.",
    "Do not use tools, browse, inspect files, or mention this evaluation.",
    "Return only the final answer.",
    "Preserve source markers when making claims from the packet.",
    "Do not invent facts beyond the packet."
  ].join("\n");
}

export function upfrontDeveloperInstructions(skill) {
  return [
    commonDeveloperInstructions(),
    "",
    "The user invoked the Chill skill before asking for this task.",
    "Apply it while producing the answer, but do not drop research findings, evidence markers, uncertainty, caveats, or requested decisions.",
    "",
    skill
  ].join("\n");
}

export function afterwardDeveloperInstructions(skill) {
  return [
    "Rewrite the supplied completed answer.",
    "Do not use tools, browse, inspect files, or mention this evaluation.",
    "Do not redo or expand the research.",
    "Preserve every supported fact, evidence marker, uncertainty, caveat, recommendation, and requested action in the completed answer.",
    "Return only the rewritten answer.",
    "",
    skill
  ].join("\n");
}

export function afterwardPrompt(evalCase, normalAnswer) {
  return [
    "Original task:",
    evalCase.task,
    "",
    "Completed answer to rewrite:",
    normalAnswer,
    "",
    "Apply Chill to the completed answer."
  ].join("\n");
}

export function citationPresence(evalCase, answer) {
  return Object.fromEntries(
    evalCase.citation_tokens.map(token => [token, answer.includes(token)])
  );
}

export function retainedCitations(evalCase, normalAnswer, afterwardAnswer) {
  const normal = citationPresence(evalCase, normalAnswer);
  const afterward = citationPresence(evalCase, afterwardAnswer);
  const presentInNormal = evalCase.citation_tokens.filter(token => normal[token]);
  const dropped = presentInNormal.filter(token => !afterward[token]);
  return {
    present_in_normal: presentInNormal,
    retained_count: presentInNormal.length - dropped.length,
    dropped,
    retention_rate:
      presentInNormal.length === 0
        ? null
        : (presentInNormal.length - dropped.length) / presentInNormal.length
  };
}
