import assert from "node:assert/strict";
import test from "node:test";
import {
  buildPrompt,
  loadProject,
  scoreResponse
} from "../scripts/lib.mjs";

test("the evaluation stays at four cases and eight calls", async () => {
  const { fixtures, cases } = await loadProject();
  assert.deepEqual(fixtures.arms, ["pre-checkpoint", "current"]);
  assert.equal(cases.length, 4);
  assert.equal(fixtures.arms.length * cases.length, 8);
});

test("the prompt includes the request and evidence packet", async () => {
  const { cases } = await loadProject();
  const prompt = buildPrompt(cases[0]);
  assert.match(prompt, /Request:/u);
  assert.match(prompt, /Evidence packet:/u);
  assert.match(prompt, /Manual installation/u);
});

test("a grounded single checkpoint receives full credit", async () => {
  const { cases } = await loadProject();
  const answer = [
    "I recommend changing only the heading to Manual installation, preserving the unrelated edits, and checking git diff --check.",
    "Does that match the contract you want?"
  ].join(" ");
  assert.equal(scoreResponse(cases[0], answer).score, 100);
});

test("a completed brief before confirmation loses the brief points", async () => {
  const { cases } = await loadProject();
  const answer = [
    "## Outcome",
    "Rename the heading to Manual installation while preserving unrelated edits.",
    "I recommend git diff --check. Do you approve?"
  ].join("\n");
  const score = scoreResponse(cases[0], answer);
  assert.equal(score.checks.avoids_premature_brief, false);
  assert.equal(score.score, 80);
});

test("asking for supplied facts receives a penalty", async () => {
  const { cases } = await loadProject();
  const answer = "I recommend following the repository convention. Which file should change?";
  const score = scoreResponse(cases[0], answer);
  assert.equal(score.checks.avoids_discoverable_fact_question, false);
  assert.equal(score.score, 65);
});
