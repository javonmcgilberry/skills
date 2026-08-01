import assert from "node:assert/strict";
import { loadProject } from "./lib.mjs";

const { fixtures, cases, skills } = await loadProject();

assert.deepEqual(fixtures.arms, ["initial", "current"]);
assert.equal(cases.length, 6);
assert.equal(new Set(cases.map(evalCase => evalCase.id)).size, cases.length);

for (const evalCase of cases) {
  assert.ok(evalCase.request.length > 0);
  assert.ok(evalCase.evidence.length > 0);
  assert.ok(evalCase.expected_terms.length > 0);
  assert.ok(evalCase.expected_terms.length >= evalCase.minimum_expected_terms);
  assert.ok(evalCase.expected_route.length > 0);
  assert.ok(evalCase.decision_prompt.length > 0);
  assert.ok(Array.isArray(evalCase.forbidden_terms));
}

for (const arm of fixtures.arms) {
  assert.match(skills[arm], /^---\nname: brrr\n/u);
}

console.log(`Validated ${cases.length} cases and ${fixtures.arms.length} arms.`);
