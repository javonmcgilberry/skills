import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  buildPrompt,
  developerInstructions,
  loadProject,
  parseArguments,
  projectRoot,
  sha256
} from "./lib.mjs";

const values = parseArguments(process.argv.slice(2));
const runId = values.get("run-id");
if (!runId) {
  throw new Error("--run-id is required");
}

const model = values.get("model") ?? "gpt-5.6-sol";
const reasoningEffort = values.get("reasoning-effort") ?? "medium";
const timeoutMs = Number(values.get("timeout-ms") ?? 300000);
const { fixtures, cases, skills } = await loadProject();
const runRoot = path.join(projectRoot, "results", runId);
const expectedCalls = fixtures.arms.length * cases.length;

await assertCodexOauth();
await mkdir(path.dirname(runRoot), { recursive: true });
await mkdir(runRoot);
await mkdir(path.join(runRoot, "skills"));

for (const arm of fixtures.arms) {
  await writeFile(path.join(runRoot, "skills", `${arm}.md`), skills[arm]);
}

const manifest = {
  schema_version: 1,
  run_id: runId,
  status: "running",
  started_at: new Date().toISOString(),
  model,
  reasoning_effort: reasoningEffort,
  timeout_ms: timeoutMs,
  expected_model_calls: expectedCalls,
  completed_model_calls: 0,
  cases: cases.map(evalCase => evalCase.id),
  arms: fixtures.arms,
  skill_sha256: Object.fromEntries(
    fixtures.arms.map(arm => [arm, sha256(skills[arm])])
  )
};
await saveManifest(runRoot, manifest);

for (const evalCase of cases) {
  for (const arm of fixtures.arms) {
    console.log(`Running ${evalCase.id}/${arm}`);
    const candidateRoot = path.join(runRoot, "raw", evalCase.id, arm);
    await mkdir(candidateRoot, { recursive: true });
    const responsePath = path.join(candidateRoot, "response.md");
    const prompt = buildPrompt(evalCase);
    const instructions = developerInstructions(skills[arm]);
    await writeFile(
      path.join(candidateRoot, "request.json"),
      `${JSON.stringify({ prompt, developer_instructions: instructions }, null, 2)}\n`
    );
    const result = await runCommand(
      "codex",
      [
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--model",
        model,
        "-c",
        `model_reasoning_effort=\"${reasoningEffort}\"`,
        "-c",
        'approval_policy="never"',
        "--sandbox",
        "read-only",
        "--cd",
        projectRoot,
        "--json",
        "--output-last-message",
        responsePath,
        "-c",
        `developer_instructions=${JSON.stringify(instructions)}`,
        "--skip-git-repo-check",
        "-"
      ],
      { cwd: projectRoot, timeoutMs, input: prompt }
    );
    await writeFile(path.join(candidateRoot, "trace.jsonl"), result.stdout);
    await writeFile(path.join(candidateRoot, "stderr.log"), result.stderr);
    if (result.code !== 0) {
      throw new Error(`Call failed for ${evalCase.id}/${arm}.`);
    }
    manifest.completed_model_calls += 1;
    await saveManifest(runRoot, manifest);
  }
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
    throw new Error(`Codex login is required.\n${result.stderr.trim()}`);
  }
}

async function saveManifest(runRoot, manifest) {
  await writeFile(
    path.join(runRoot, "manifest.json"),
    `${JSON.stringify(manifest, null, 2)}\n`
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
