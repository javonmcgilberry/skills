import assert from "node:assert/strict";
import test from "node:test";
import {
  applyStoppingRule,
  commonResearchInstructions,
  gradeCandidate,
  loadProcessProject,
  parseTrace,
  upfrontResearchInstructions
} from "../scripts/process-eval-lib.mjs";

test("process evaluation has 18 initial calls and isolates Chill", async () => {
  const { config, skill, cases } = await loadProcessProject("initial");
  assert.equal(cases.length, 3);
  assert.equal(config.trials_per_case, 3);
  assert.deepEqual(config.arms, [
    "normal_research",
    "chill_upfront_research"
  ]);
  assert.equal(cases.length * config.trials_per_case * config.arms.length, 18);
  assert.equal(commonResearchInstructions().includes(skill), false);
  assert.equal(upfrontResearchInstructions(skill).includes(skill), true);
});

test("trace parser records research actions, usage, and direct-tool violations", () => {
  const trace = [
    JSON.stringify({
      type: "item.completed",
      item: {
        type: "command_execution",
        command: "/bin/zsh -lc 'node research.mjs search \"oauth callback\"'",
        exit_code: 0
      }
    }),
    JSON.stringify({
      type: "item.completed",
      item: {
        type: "command_execution",
        command: "/bin/zsh -lc 'node research.mjs read OAUTH-BOUNDARY-2026'",
        exit_code: 0
      }
    }),
    JSON.stringify({
      type: "item.completed",
      item: {
        type: "command_execution",
        command: "/bin/zsh -lc 'cat .research/corpus.json'",
        exit_code: 0
      }
    }),
    JSON.stringify({
      type: "turn.completed",
      usage: {
        input_tokens: 100,
        output_tokens: 20
      }
    })
  ].join("\n");

  const parsed = parseTrace(trace);
  assert.deepEqual(parsed.actions, [
    { action: "search", value: "oauth callback" },
    { action: "read", value: "OAUTH-BOUNDARY-2026" }
  ]);
  assert.equal(parsed.violations.length, 1);
  assert.equal(parsed.usage.output_tokens, 20);
});

test("deterministic candidate grader separates process and outcome", async () => {
  const { cases } = await loadProcessProject("initial");
  const evalCase = cases.find(
    candidate => candidate.id === "hubspot-local-dev-architecture"
  );
  const answer = [
    "For ordinary frontend-only work, the recommended day-to-day setup is a local Vite client connected to the hosted API [DEV-ARCH-2026].",
    "Keep the hosted database and OAuth exchange on the server, so no local backend, local database, or tunnel is required [OAUTH-BOUNDARY-2026] [TEAM-LOOP-2026].",
    "Provider secrets and token exchange remain on the hosted server [SECURITY-REVIEW-2026].",
    "Use a broader local or separate server environment when server behavior, a database migration, or the OAuth callback changes."
  ].join(" ");
  const activity = {
    commands: ["one", "two", "three", "four"],
    actions: [
      { action: "search", value: "architecture" },
      { action: "read", value: "DEV-ARCH-2026" },
      { action: "read", value: "OAUTH-BOUNDARY-2026" },
      { action: "read", value: "TEAM-LOOP-2026" }
    ],
    violations: []
  };

  const grade = gradeCandidate(evalCase, answer, activity);
  assert.equal(grade.research_quality.missing_critical_facts.length, 0);
  assert.equal(grade.research_quality.forbidden_claims.length, 0);
  assert.equal(grade.research_process.search_count, 1);
  assert.equal(grade.research_process.unique_sources_opened, 3);
  assert.equal(grade.research_process.interface_violations.length, 0);
});

test("stopping rule distinguishes material and mixed results", () => {
  const materialPairs = Array.from({ length: 9 }, (_, index) => ({
    case_id: `case-${index % 3}`,
    quality_delta: 6,
    critical_failure_delta: 0,
    tool_call_delta_percent: 25,
    sources_opened_delta_percent: 25,
    relevant_recall_delta: 0,
    distractor_rate_delta: 0
  }));
  const mixedPairs = Array.from({ length: 9 }, (_, index) => ({
    case_id: `case-${index % 3}`,
    quality_delta: index % 2 === 0 ? 2 : -2,
    critical_failure_delta: 0,
    tool_call_delta_percent: index % 2 === 0 ? 10 : -10,
    sources_opened_delta_percent: 0,
    relevant_recall_delta: 0,
    distractor_rate_delta: 0
  }));

  assert.equal(applyStoppingRule(materialPairs).stop_after_initial, true);
  assert.equal(applyStoppingRule(mixedPairs).needs_holdout, true);
});
