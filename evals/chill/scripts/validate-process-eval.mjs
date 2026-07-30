import { readFile } from "node:fs/promises";
import path from "node:path";
import {
  commonResearchInstructions,
  loadProcessProject,
  projectRoot,
  seededShuffle,
  sha256,
  upfrontResearchInstructions
} from "./process-eval-lib.mjs";

const { config, baselineManifest, skill, cases } =
  await loadProcessProject("initial");
const errors = [];
const runtimeSkill = await readFile(
  path.resolve(projectRoot, baselineManifest.runtime_path),
  "utf8"
);

if (sha256(skill) !== baselineManifest.sha256) {
  errors.push("Frozen Chill skill does not match its manifest.");
}
if (sha256(runtimeSkill) !== baselineManifest.sha256) {
  errors.push("Runtime Chill skill changed.");
}
if (cases.length !== 3 || config.trials_per_case !== 3) {
  errors.push("Initial suite must contain 3 cases with 3 trials each.");
}
if (
  config.arms.join(",")
  !== "normal_research,chill_upfront_research"
) {
  errors.push("Process arms are incorrect.");
}
if (cases.length * config.trials_per_case * config.arms.length !== 18) {
  errors.push("Initial suite must make exactly 18 calls.");
}
if (commonResearchInstructions().includes(skill)) {
  errors.push("Control instructions contain the Chill skill.");
}
if (!upfrontResearchInstructions(skill).includes(skill)) {
  errors.push("Upfront instructions do not contain the exact Chill skill.");
}

for (const evalCase of cases) {
  const sourceIds = new Set(evalCase.corpus.map(source => source.id));
  if (sourceIds.size !== evalCase.corpus.length || evalCase.corpus.length < 7) {
    errors.push(`${evalCase.id} needs unique IDs and at least 7 sources.`);
  }
  for (const id of [
    ...evalCase.expected.research_relevant_source_ids,
    ...evalCase.expected.preferred_citation_source_ids
  ]) {
    if (!sourceIds.has(id)) {
      errors.push(`${evalCase.id} references missing source ${id}.`);
    }
  }
  if (evalCase.expected.critical_facts.length < 4) {
    errors.push(`${evalCase.id} needs at least 4 critical facts.`);
  }
  const firstOrder = seededShuffle(
    evalCase.corpus.map(source => source.id),
    `validation/${evalCase.id}/1/corpus`
  );
  const repeatedOrder = seededShuffle(
    evalCase.corpus.map(source => source.id),
    `validation/${evalCase.id}/1/corpus`
  );
  if (JSON.stringify(firstOrder) !== JSON.stringify(repeatedOrder)) {
    errors.push(`${evalCase.id} corpus randomization is not reproducible.`);
  }
}

for (const relativePath of [
  "scripts/research.mjs",
  "scripts/run-process-eval.mjs",
  "scripts/grade-process-eval.mjs"
]) {
  try {
    await readFile(path.join(projectRoot, relativePath), "utf8");
  } catch {
    errors.push(`Missing ${relativePath}.`);
  }
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(`FAIL ${error}`);
  }
  process.exitCode = 1;
} else {
  console.log("PASS 3 process cases, 3 trials, 2 arms, 18 planned calls");
  console.log(`PASS runtime Chill skill ${baselineManifest.sha256}`);
  console.log("PASS control excludes Chill and upfront includes the exact frozen skill");
  console.log("PASS paired corpus randomization is reproducible");
}
