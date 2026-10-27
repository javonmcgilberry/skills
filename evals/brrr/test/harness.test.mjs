import assert from "node:assert/strict";
import test from "node:test";
import {
  classifyRoute,
  loadProject,
  scoreResponse
} from "../scripts/lib.mjs";

test("the evaluation stays at six cases and twelve calls", async () => {
  const { fixtures, cases } = await loadProject();
  assert.deepEqual(fixtures.arms, ["initial", "current"]);
  assert.equal(cases.length, 6);
  assert.equal(fixtures.arms.length * cases.length, 12);
});

test("the classifier distinguishes the four workflow routes", () => {
  assert.equal(classifyRoute("Proceed with implementation and run the test."), "execute");
  assert.equal(classifyRoute("Inspect the named file before editing."), "execute");
  assert.equal(classifyRoute("Return to Lock In because approval is missing."), "lock-in");
  assert.equal(classifyRoute("Pause for a contract decision before continuing."), "lock-in");
  assert.equal(classifyRoute("Move this to a heavier workflow for coordinated verification."), "heavier");
  assert.equal(
    classifyRoute("Use the heavier workflow because Lock In is not needed."),
    "heavier"
  );
  assert.equal(
    classifyRoute("Implement now, but publication remains separate and requires authorization."),
    "execute-without-publication"
  );
});

test("an expected concise route receives full credit", async () => {
  const { cases } = await loadProject();
  const answer = "Inspect the named file, then proceed using the explicit acceptance criteria.";
  assert.equal(scoreResponse(cases[0], answer).score, 100);
});

test("a contradictory route loses route and forbidden-term points", async () => {
  const { cases } = await loadProject();
  const answer = "Proceed with implementation even though the brief is Draft.";
  const score = scoreResponse(cases[1], answer);
  assert.equal(score.checks.expected_route, false);
  assert.equal(score.checks.avoids_forbidden_route, false);
});
