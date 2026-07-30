import { spawn } from "node:child_process";
import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  commonResearchInstructions,
  loadProcessProject,
  parseArguments,
  parseTrace,
  processResultsRoot,
  projectRoot,
  seededShuffle,
  sha256,
  upfrontResearchInstructions
} from "./process-eval-lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
const suite = values.get("suite") ?? "initial";
if (!runId) {
  throw new Error("--run-id is required");
}
if (!["initial", "holdout"].includes(suite)) {
  throw new Error("--suite must be initial or holdout");
}

const model = values.get("model") ?? "gpt-5.6-sol";
const reasoningEffort = values.get("reasoning-effort") ?? "medium";
const timeoutMs = Number(values.get("timeout-ms") ?? 300000);
const { config, baselineManifest, skill, cases } =
  await loadProcessProject(suite);
const expectedCalls =
  cases.length * config.trials_per_case * config.arms.length;
if (suite === "initial" && expectedCalls !== 18) {
  throw new Error(`Initial suite must contain exactly 18 calls, found ${expectedCalls}.`);
}
if (suite === "holdout" && expectedCalls !== 12) {
  throw new Error(`Holdout suite must contain exactly 12 calls, found ${expectedCalls}.`);
}

await assertCodexLogin();
await mkdir(processResultsRoot, { recursive: true });
const runRoot = path.join(processResultsRoot, runId);
try {
  await mkdir(runRoot);
} catch (error) {
  if (error?.code === "EEXIST") {
    throw new Error(`Run ID already exists: ${runId}`);
  }
  throw error;
}

const pairPlan = [];
for (const evalCase of cases) {
  for (let trial = 1; trial <= config.trials_per_case; trial += 1) {
    pairPlan.push({
      case_id: evalCase.id,
      trial,
      arm_order: seededShuffle(
        config.arms,
        `${runId}/${evalCase.id}/${trial}/arms`
      ),
      corpus_order: seededShuffle(
        evalCase.corpus.map(source => source.id),
        `${runId}/${evalCase.id}/${trial}/corpus`
      )
    });
  }
}

const manifest = {
  schema_version: 1,
  run_id: runId,
  suite,
  status: "running",
  started_at: new Date().toISOString(),
  model,
  reasoning_effort: reasoningEffort,
  timeout_ms: timeoutMs,
  cases: cases.map(evalCase => evalCase.id),
  trials_per_case: config.trials_per_case,
  arms: config.arms,
  pair_plan: pairPlan,
  expected_model_calls: expectedCalls,
  attempted_model_calls: 0,
  completed_model_calls: 0,
  skill_sha256: sha256(skill),
  runtime_skill_path: baselineManifest.runtime_path
};
await saveManifest(runRoot, manifest);

for (const pair of pairPlan) {
  const evalCase = cases.find(candidate => candidate.id === pair.case_id);
  const corpusById = new Map(evalCase.corpus.map(source => [source.id, source]));
  const randomizedCorpus = pair.corpus_order.map(id => corpusById.get(id));

  for (const arm of pair.arm_order) {
    console.log(
      `Running ${evalCase.id} trial ${pair.trial} ${arm} `
      + `(${manifest.completed_model_calls + 1}/${expectedCalls})`
    );
    manifest.attempted_model_calls += 1;
    await saveManifest(runRoot, manifest);
    await runCandidate({
      runRoot,
      evalCase,
      randomizedCorpus,
      trial: pair.trial,
      arm,
      model,
      reasoningEffort,
      timeoutMs,
      developerInstructions:
        arm === "chill_upfront_research"
          ? upfrontResearchInstructions(skill)
          : commonResearchInstructions()
    });
    manifest.completed_model_calls += 1;
    await saveManifest(runRoot, manifest);
  }
}

manifest.status = "complete";
manifest.completed_at = new Date().toISOString();
await saveManifest(runRoot, manifest);
console.log(`Saved ${manifest.completed_model_calls} research candidates to ${runRoot}`);

async function runCandidate({
  runRoot,
  evalCase,
  randomizedCorpus,
  trial,
  arm,
  model,
  reasoningEffort,
  timeoutMs,
  developerInstructions
}) {
  const candidateRoot = path.join(
    runRoot,
    "raw",
    evalCase.id,
    `trial-${trial}`,
    arm
  );
  const workspace = path.join(
    runRoot,
    "workspaces",
    evalCase.id,
    `trial-${trial}`,
    arm
  );
  await mkdir(candidateRoot, { recursive: true });
  await mkdir(path.join(workspace, ".research"), { recursive: true });
  await cp(path.join(projectRoot, "scripts", "research.mjs"), path.join(workspace, "research.mjs"));
  await writeFile(
    path.join(workspace, ".research", "corpus.json"),
    `${JSON.stringify(randomizedCorpus, null, 2)}\n`
  );

  const prompt = [
    evalCase.task.trim(),
    "",
    "Use the local research interface to investigate before answering."
  ].join("\n");
  const finalPath = path.join(candidateRoot, "response.md");
  const tracePath = path.join(candidateRoot, "trace.jsonl");
  const stderrPath = path.join(candidateRoot, "stderr.log");
  await writeFile(
    path.join(candidateRoot, "request.json"),
    `${JSON.stringify(
      {
        case_id: evalCase.id,
        trial,
        arm,
        model,
        reasoning_effort: reasoningEffort,
        developer_instructions: developerInstructions,
        prompt,
        corpus_sha256: sha256(JSON.stringify(randomizedCorpus))
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
    workspace,
    "--json",
    "--output-last-message",
    finalPath,
    "-c",
    `developer_instructions=${JSON.stringify(developerInstructions)}`,
    "--skip-git-repo-check",
    "-"
  ];
  const startedAt = Date.now();
  const result = await runCommand("codex", args, {
    cwd: workspace,
    timeoutMs,
    input: prompt
  });
  const durationMs = Date.now() - startedAt;
  await writeFile(tracePath, result.stdout);
  await writeFile(stderrPath, result.stderr);
  if (result.code !== 0) {
    throw new Error(
      `Candidate failed for ${evalCase.id}/trial-${trial}/${arm}. `
      + `See ${stderrPath}.`
    );
  }
  const trace = parseTrace(result.stdout);
  await writeFile(
    path.join(candidateRoot, "record.json"),
    `${JSON.stringify(
      {
        status: "complete",
        duration_ms: durationMs,
        usage: trace.usage,
        research_activity: {
          commands: trace.commands,
          actions: trace.actions,
          violations: trace.violations
        }
      },
      null,
      2
    )}\n`
  );
  await readFile(finalPath, "utf8");
}

async function assertCodexLogin() {
  const result = await runCommand("codex", ["login", "status"], {
    cwd: projectRoot,
    timeoutMs: 30000
  });
  if (result.code !== 0) {
    throw new Error(`Codex login is required.\n${result.stderr.trim()}`);
  }
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
    const timeout = setTimeout(() => child.kill("SIGTERM"), options.timeoutMs);
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
