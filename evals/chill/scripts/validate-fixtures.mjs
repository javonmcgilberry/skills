import { readFile } from "node:fs/promises";
import path from "node:path";
import { loadProject, projectRoot, sha256 } from "./lib.mjs";

const { fixtures, manifest, skill, cases } = await loadProject();
const errors = [];

if (fixtures.arms.join(",") !== "normal,chill_upfront,chill_afterward") {
  errors.push("The arm list must contain only normal, chill_upfront, and chill_afterward.");
}
if (cases.length !== 3) {
  errors.push(`Expected 3 cases, found ${cases.length}.`);
}
if (cases.filter(evalCase => evalCase.kind === "research").length !== 2) {
  errors.push("Expected exactly 2 research cases.");
}
if (cases.filter(evalCase => evalCase.kind === "planning").length !== 1) {
  errors.push("Expected exactly 1 planning case.");
}

const caseIds = new Set();
for (const evalCase of cases) {
  if (caseIds.has(evalCase.id)) {
    errors.push(`Duplicate case ID: ${evalCase.id}`);
  }
  caseIds.add(evalCase.id);

  if (!evalCase.task || evalCase.task.length < 300) {
    errors.push(`${evalCase.id} needs a self-contained task and source packet.`);
  }
  if (!Array.isArray(evalCase.expected_facts) || evalCase.expected_facts.length < 4) {
    errors.push(`${evalCase.id} needs at least 4 expected facts.`);
  }
  if (!Array.isArray(evalCase.citation_tokens) || evalCase.citation_tokens.length < 3) {
    errors.push(`${evalCase.id} needs at least 3 citation tokens.`);
  }

  const factIds = new Set();
  for (const fact of evalCase.expected_facts ?? []) {
    if (factIds.has(fact.id)) {
      errors.push(`${evalCase.id} has duplicate fact ID ${fact.id}.`);
    }
    factIds.add(fact.id);
  }
  for (const token of evalCase.citation_tokens ?? []) {
    if (!evalCase.task.includes(token)) {
      errors.push(`${evalCase.id} does not define citation token ${token}.`);
    }
  }
}

const runtimeSkill = await readFile(
  path.resolve(projectRoot, manifest.runtime_path),
  "utf8"
);
const snapshotHash = sha256(skill);
const runtimeHash = sha256(runtimeSkill);
if (snapshotHash !== manifest.sha256) {
  errors.push(`Snapshot hash ${snapshotHash} does not match the manifest.`);
}
if (runtimeHash !== manifest.sha256) {
  errors.push(`Runtime Chill hash ${runtimeHash} does not match the frozen baseline.`);
}

const callCount = fixtures.arms.length * cases.length;
if (callCount !== 9) {
  errors.push(`Expected exactly 9 calls, calculated ${callCount}.`);
}

const requiredFiles = ["protocol.md", "rubric.md", "fixtures.json"];
for (const relativePath of requiredFiles) {
  try {
    await readFile(path.join(projectRoot, relativePath), "utf8");
  } catch {
    errors.push(`Missing required file: ${relativePath}`);
  }
}

if (errors.length > 0) {
  for (const error of errors) {
    console.error(`FAIL ${error}`);
  }
  process.exitCode = 1;
} else {
  console.log(`PASS 3 fixtures, 3 arms, ${callCount} planned calls`);
  console.log(`PASS frozen Chill skill ${manifest.sha256}`);
  console.log("PASS runtime skill matches the frozen baseline");
}
