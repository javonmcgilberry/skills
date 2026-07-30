import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  applyStoppingRule,
  gradeCandidate,
  loadProcessProject,
  parseArguments,
  processResultsRoot,
  seededShuffle,
  summarizePairs
} from "./process-eval-lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const runRoot = path.join(processResultsRoot, runId);
const manifest = JSON.parse(
  await readFile(path.join(runRoot, "manifest.json"), "utf8")
);
if (
  manifest.status !== "complete"
  || manifest.completed_model_calls !== manifest.expected_model_calls
) {
  throw new Error(`Run ${runId} is incomplete.`);
}
const { cases } = await loadProcessProject(manifest.suite);
const candidates = [];

for (const evalCase of cases) {
  for (let trial = 1; trial <= manifest.trials_per_case; trial += 1) {
    for (const arm of manifest.arms) {
      const candidateRoot = path.join(
        runRoot,
        "raw",
        evalCase.id,
        `trial-${trial}`,
        arm
      );
      const [answer, record] = await Promise.all([
        readFile(path.join(candidateRoot, "response.md"), "utf8"),
        readFile(path.join(candidateRoot, "record.json"), "utf8").then(JSON.parse)
      ]);
      const grade = gradeCandidate(
        evalCase,
        answer,
        record.research_activity
      );
      const candidate = {
        case_id: evalCase.id,
        trial,
        arm,
        ...grade,
        duration_ms: record.duration_ms,
        usage: record.usage
      };
      candidates.push(candidate);
      await writeFile(
        path.join(candidateRoot, "grade.json"),
        `${JSON.stringify(candidate, null, 2)}\n`
      );
    }
  }
}

const pairs = summarizePairs(candidates);
const stoppingRule = applyStoppingRule(pairs);
const summary = {
  schema_version: 1,
  run_id: runId,
  suite: manifest.suite,
  model_calls: manifest.completed_model_calls,
  candidates,
  pairs,
  stopping_rule: stoppingRule
};
await writeFile(
  path.join(runRoot, "summary.json"),
  `${JSON.stringify(summary, null, 2)}\n`
);
await writeBlindReview(runRoot, runId, cases, manifest, candidates);
console.log(`Graded ${candidates.length} candidates for ${runId}`);
console.log(JSON.stringify(stoppingRule, null, 2));

async function writeBlindReview(runRoot, runId, cases, manifest, candidates) {
  const mapping = [];
  const sections = [];
  for (const evalCase of cases) {
    for (let trial = 1; trial <= manifest.trials_per_case; trial += 1) {
      const labels = seededShuffle(
        ["A", "B"],
        `${runId}/${evalCase.id}/${trial}/blind`
      );
      const arms = seededShuffle(
        manifest.arms,
        `${runId}/${evalCase.id}/${trial}/blind-arms`
      );
      sections.push(`## ${evalCase.id} trial ${trial}`);
      for (let index = 0; index < arms.length; index += 1) {
        const arm = arms[index];
        const label = labels[index];
        const answer = await readFile(
          path.join(
            runRoot,
            "raw",
            evalCase.id,
            `trial-${trial}`,
            arm,
            "response.md"
          ),
          "utf8"
        );
        const candidate = candidates.find(
          item =>
            item.case_id === evalCase.id
            && item.trial === trial
            && item.arm === arm
        );
        mapping.push({ case_id: evalCase.id, trial, label, arm });
        sections.push(
          [
            `### Candidate ${label}`,
            "",
            answer.trim(),
            "",
            "Review fields:",
            "",
            "- Clarity: /5",
            "- Natural language: /5",
            "- Concision without dilution: /5",
            `- Deterministic research score: ${candidate.research_quality.total_score}`,
            "- Qualitative omissions or unsupported additions:",
            ""
          ].join("\n")
        );
      }
    }
  }
  await writeFile(
    path.join(runRoot, "blind-review.md"),
    [
      "# Blind review packet",
      "",
      "Score the labeled candidates before opening blind-map.json.",
      "The deterministic score is included to keep prose preferences from overriding research quality.",
      "",
      ...sections
    ].join("\n")
  );
  await writeFile(
    path.join(runRoot, "blind-map.json"),
    `${JSON.stringify(mapping, null, 2)}\n`
  );
}
