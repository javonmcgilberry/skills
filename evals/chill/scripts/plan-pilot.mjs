import { parseArguments, loadProject, projectRoot } from "./lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const model = values.get("model") ?? "gpt-5.6-sol";
const reasoningEffort = values.get("reasoning-effort") ?? "medium";
const { fixtures, cases } = await loadProject();
const callCount = fixtures.arms.length * cases.length;

console.log("CHILL RESEARCH TIMING PILOT");
console.log(`Run ID: ${runId}`);
console.log(`Model: ${model}`);
console.log(`Reasoning effort: ${reasoningEffort}`);
console.log(`Model calls: ${callCount}`);
console.log("");

for (const evalCase of cases) {
  console.log(`FIXTURE ${evalCase.id} (${evalCase.kind})`);
  console.log(evalCase.task);
  console.log("");
}

console.log("ARMS");
console.log("1. normal: task and source packet, no Chill instructions");
console.log("2. chill_upfront: task and source packet, frozen Chill loaded before generation");
console.log("3. chill_afterward: fresh rewrite call using the normal answer and frozen Chill");
console.log("");
console.log("COMMAND");
console.log(
  `cd ${projectRoot} && npm run pilot -- --run-id ${runId} --model ${model} --reasoning-effort ${reasoningEffort}`
);
console.log("");
console.log("EXPECTED OUTPUTS");
console.log(`results/${runId}/manifest.json`);
console.log(`results/${runId}/raw/<case>/<arm>/request.json`);
console.log(`results/${runId}/raw/<case>/<arm>/response.md`);
console.log(`results/${runId}/raw/<case>/<arm>/trace.jsonl`);
console.log(`results/${runId}/raw/<case>/<arm>/stderr.log`);
console.log(`results/${runId}/summary.json after npm run summarize`);
console.log(`results/${runId}/review.md after npm run summarize`);
