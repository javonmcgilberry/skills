import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  afterwardDeveloperInstructions,
  afterwardPrompt,
  commonDeveloperInstructions,
  loadProject,
  parseArguments,
  projectRoot,
  sha256,
  upfrontDeveloperInstructions
} from "./lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const model = values.get("model") ?? "gpt-5.6-sol";
const reasoningEffort = values.get("reasoning-effort") ?? "medium";
const timeoutMs = Number(values.get("timeout-ms") ?? 300000);
const { fixtures, manifest: baselineManifest, skill, cases } = await loadProject();
const resultsRoot = path.join(projectRoot, "results");
const runRoot = path.join(resultsRoot, runId);
const expectedCalls = fixtures.arms.length * cases.length;

if (expectedCalls !== 9) {
  throw new Error(`Refusing to run ${expectedCalls} calls. This pilot must make exactly 9.`);
}

await assertCodexOauth();
await mkdir(resultsRoot, { recursive: true });
try {
  await mkdir(runRoot);
} catch (error) {
  if (error?.code === "EEXIST") {
    throw new Error(`Run ID already exists: ${runId}. Use a new run ID.`);
  }
  throw error;
}

const manifest = {
  schema_version: 1,
  run_id: runId,
  status: "running",
  started_at: new Date().toISOString(),
  model,
  reasoning_effort: reasoningEffort,
  timeout_ms: timeoutMs,
  cases: cases.map(evalCase => evalCase.id),
  arms: fixtures.arms,
  expected_model_calls: expectedCalls,
  completed_model_calls: 0,
  skill_sha256: sha256(skill),
  runtime_skill_path: baselineManifest.runtime_path
};
await saveManifest(runRoot, manifest);

for (const evalCase of cases) {
  console.log(`Running ${evalCase.id}`);

  const normal = await runArm({
    runRoot,
    evalCase,
    arm: "normal",
    prompt: evalCase.task,
    developerInstructions: commonDeveloperInstructions(),
    model,
    reasoningEffort,
    timeoutMs
  });
  manifest.completed_model_calls += 1;
  await saveManifest(runRoot, manifest);

  await runArm({
    runRoot,
    evalCase,
    arm: "chill_upfront",
    prompt: evalCase.task,
    developerInstructions: upfrontDeveloperInstructions(skill),
    model,
    reasoningEffort,
    timeoutMs
  });
  manifest.completed_model_calls += 1;
  await saveManifest(runRoot, manifest);

  await runArm({
    runRoot,
    evalCase,
    arm: "chill_afterward",
    prompt: afterwardPrompt(evalCase, normal),
    developerInstructions: afterwardDeveloperInstructions(skill),
    model,
    reasoningEffort,
    timeoutMs
  });
  manifest.completed_model_calls += 1;
  await saveManifest(runRoot, manifest);
}

manifest.status = "complete";
manifest.completed_at = new Date().toISOString();
await saveManifest(runRoot, manifest);
console.log(`Saved ${manifest.completed_model_calls} candidates to ${runRoot}`);

async function assertCodexOauth() {
  const result = await runCommand("codex", ["login", "status"], {
    cwd: projectRoot,
    timeoutMs: 30000
  });
  if (result.code !== 0) {
    throw new Error(
      `Codex login is required. Run \`codex login\` first.\n${result.stderr.trim()}`
    );
  }
}

async function runArm({
  runRoot,
  evalCase,
  arm,
  prompt,
  developerInstructions,
  model,
  reasoningEffort,
  timeoutMs
}) {
  const armRoot = path.join(runRoot, "raw", evalCase.id, arm);
  await mkdir(armRoot, { recursive: true });
  const finalPath = path.join(armRoot, "response.md");
  const requestPath = path.join(armRoot, "request.json");
  const tracePath = path.join(armRoot, "trace.jsonl");
  const stderrPath = path.join(armRoot, "stderr.log");

  await writeFile(
    requestPath,
    `${JSON.stringify(
      {
        case_id: evalCase.id,
        arm,
        model,
        reasoning_effort: reasoningEffort,
        developer_instructions: developerInstructions,
        prompt
      },
      null,
      2
    )}\n`
  );

  const args = [
    "exec",
    "--ephemeral",
    "--ignore-user-config",
    "--ignore-rules",
    "--model",
    model,
    "-c",
    `model_reasoning_effort="${reasoningEffort}"`,
    "-c",
    'approval_policy="never"',
    "--sandbox",
    "read-only",
    "--cd",
    projectRoot,
    "--json",
    "--output-last-message",
    finalPath,
    "-c",
    `developer_instructions=${JSON.stringify(developerInstructions)}`,
    "--skip-git-repo-check",
    "-"
  ];
  const result = await runCommand("codex", args, {
    cwd: projectRoot,
    timeoutMs,
    input: prompt
  });
  await writeFile(tracePath, result.stdout);
  await writeFile(stderrPath, result.stderr);
  if (result.code !== 0) {
    throw new Error(`Call failed for ${evalCase.id}/${arm}. See ${stderrPath}.`);
  }
  return readFile(finalPath, "utf8");
}

async function saveManifest(runRoot, value) {
  await writeFile(
    path.join(runRoot, "manifest.json"),
    `${JSON.stringify(value, null, 2)}\n`
  );
}

function runCommand(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      stdio: ["pipe", "pipe", "pipe"]
    });
    let stdout = "";
    let stderr = "";
    const timeout = setTimeout(() => {
      child.kill("SIGTERM");
    }, options.timeoutMs);

    child.stdout.on("data", chunk => {
      stdout += chunk;
    });
    child.stderr.on("data", chunk => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", code => {
      clearTimeout(timeout);
      resolve({ code, stdout, stderr });
    });
    child.stdin.end(options.input ?? "");
  });
}
