import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  loadProject,
  parseArguments,
  projectRoot,
  scoreResponse
} from "./lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const { fixtures, cases } = await loadProject();
const runRoot = path.join(projectRoot, "results", runId);
const manifest = JSON.parse(
  await readFile(path.join(runRoot, "manifest.json"), "utf8")
);
if (manifest.status !== "complete") {
  throw new Error(`Run ${runId} is not complete.`);
}

const rows = [];
for (const evalCase of cases) {
  for (const arm of fixtures.arms) {
    const candidateRoot = path.join(runRoot, "raw", evalCase.id, arm);
    const answer = await readFile(path.join(candidateRoot, "response.md"), "utf8");
    const score = scoreResponse(evalCase, answer);
    await writeFile(
      path.join(candidateRoot, "score.json"),
      `${JSON.stringify(score, null, 2)}\n`
    );
    rows.push({ case_id: evalCase.id, arm, ...score });
  }
}

const arms = Object.fromEntries(
  fixtures.arms.map(arm => {
    const armRows = rows.filter(row => row.arm === arm);
    return [
      arm,
      {
        mean_score:
          armRows.reduce((total, row) => total + row.score, 0) / armRows.length,
        scores: Object.fromEntries(armRows.map(row => [row.case_id, row.score]))
      }
    ];
  })
);
const summary = { schema_version: 1, run_id: runId, arms, rows };
await writeFile(
  path.join(runRoot, "summary.json"),
  `${JSON.stringify(summary, null, 2)}\n`
);

const tableRows = rows.map(
  row =>
    `| ${row.case_id} | ${row.arm} | ${row.score} | ${row.question_count} |`
);
const result = [
  "# Lock In evaluation result",
  "",
  `Run: \`${runId}\``,
  "",
  "| Arm | Mean score |",
  "| --- | ---: |",
  ...fixtures.arms.map(arm => `| ${arm} | ${arms[arm].mean_score.toFixed(1)} |`),
  "",
  "| Case | Arm | Score | Questions |",
  "| --- | --- | ---: | ---: |",
  ...tableRows,
  ""
].join("\n");
await writeFile(path.join(runRoot, "result.md"), result);
console.log(result);
