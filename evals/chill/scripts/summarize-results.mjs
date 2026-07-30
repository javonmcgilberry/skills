import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  citationPresence,
  loadProject,
  parseArguments,
  projectRoot,
  retainedCitations,
  wordCount
} from "./lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const { fixtures, cases } = await loadProject();
const runRoot = path.join(projectRoot, "results", runId);
let manifest;
try {
  manifest = JSON.parse(
    await readFile(path.join(runRoot, "manifest.json"), "utf8")
  );
} catch (error) {
  if (error?.code === "ENOENT") {
    throw new Error(
      `Run ${runId} does not exist. Complete the pilot before summarizing it.`
    );
  }
  throw error;
}
if (manifest.status !== "complete" || manifest.completed_model_calls !== 9) {
  throw new Error("The run is incomplete. Expected 9 completed model calls.");
}

const summary = {
  schema_version: 1,
  run_id: runId,
  model_calls: manifest.completed_model_calls,
  generated_at: new Date().toISOString(),
  cases: {}
};

for (const evalCase of cases) {
  const answers = {};
  for (const arm of fixtures.arms) {
    answers[arm] = await readFile(
      path.join(runRoot, "raw", evalCase.id, arm, "response.md"),
      "utf8"
    );
  }
  summary.cases[evalCase.id] = {
    arms: Object.fromEntries(
      fixtures.arms.map(arm => [
        arm,
        {
          word_count: wordCount(answers[arm]),
          citations: citationPresence(evalCase, answers[arm])
        }
      ])
    ),
    afterward_citation_retention: retainedCitations(
      evalCase,
      answers.normal,
      answers.chill_afterward
    )
  };
}

await writeFile(
  path.join(runRoot, "summary.json"),
  `${JSON.stringify(summary, null, 2)}\n`
);
await writeFile(path.join(runRoot, "review.md"), buildReview(cases, fixtures.arms));
console.log(`Saved deterministic summary and human review sheet to ${runRoot}`);

function buildReview(evalCases, arms) {
  const sections = evalCases.map(evalCase => {
    const facts = evalCase.expected_facts
      .map(fact => `- [ ] ${fact.id}${fact.critical ? " critical" : ""}: ${fact.description}`)
      .join("\n");
    const candidates = arms
      .map(
        arm =>
          `### Candidate [blind label]\n\nSource file before blinding: raw/${evalCase.id}/${arm}/response.md\n\nResearch quality:\n\n- Factual coverage: /5\n- Evidence use: /5\n- Citation retention: /5\n- Uncertainty: /5\n- Recommendation: /5\n- Missing facts or unsupported additions:\n\nCommunication quality:\n\n- Clarity: /5\n- Natural language: /5\n- Concision without dilution: /5\n- Notes:\n`
      )
      .join("\n");
    return `## ${evalCase.id}\n\nExpected facts:\n\n${facts}\n\n${candidates}`;
  });

  return [
    `# Human review for ${runId}`,
    "",
    "Randomize candidate order and replace each arm with a blind label before scoring. Keep research and communication scores separate.",
    "",
    ...sections,
    "## Decision",
    "",
    "- Research-quality comparison:",
    "- Communication-quality comparison:",
    "- Any critical failures:",
    "- Preferred workflow and why:",
    ""
  ].join("\n");
}
