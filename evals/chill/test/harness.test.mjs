import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";
import {
  afterwardPrompt,
  citationPresence,
  loadProject,
  projectRoot,
  retainedCitations,
  sha256,
  wordCount
} from "../scripts/lib.mjs";

test("the pilot stays at three fixtures and nine calls", async () => {
  const { fixtures, cases } = await loadProject();
  assert.deepEqual(fixtures.arms, ["normal", "chill_upfront", "chill_afterward"]);
  assert.equal(cases.length, 3);
  assert.equal(fixtures.arms.length * cases.length, 9);
});

test("the frozen skill matches the manifest and runtime skill", async () => {
  const { manifest, skill } = await loadProject();
  const runtimeSkill = await readFile(
    path.resolve(projectRoot, manifest.runtime_path),
    "utf8"
  );
  assert.equal(sha256(skill), manifest.sha256);
  assert.equal(sha256(runtimeSkill), manifest.sha256);
});

test("citation checks report presence and afterward losses", async () => {
  const { cases } = await loadProject();
  const evalCase = cases[0];
  const first = evalCase.citation_tokens[0];
  const second = evalCase.citation_tokens[1];
  const normal = `Finding ${first}. Another finding ${second}.`;
  const afterward = `Clear finding ${first}.`;

  assert.equal(citationPresence(evalCase, normal)[first], true);
  assert.deepEqual(retainedCitations(evalCase, normal, afterward).dropped, [second]);
  assert.equal(retainedCitations(evalCase, normal, afterward).retention_rate, 0.5);
});

test("afterward prompt includes the original task and completed answer", async () => {
  const { cases } = await loadProject();
  const prompt = afterwardPrompt(cases[0], "Completed research answer.");
  assert.match(prompt, /Original task:/u);
  assert.match(prompt, /Completed answer to rewrite:/u);
  assert.match(prompt, /Completed research answer\./u);
});

test("word count handles empty and ordinary answers", () => {
  assert.equal(wordCount(""), 0);
  assert.equal(wordCount("plain useful answer"), 3);
});
