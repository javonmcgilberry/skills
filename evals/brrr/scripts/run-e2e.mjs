import { spawn } from "node:child_process";
import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
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
const { skills } = await loadProject();
const runRoot = path.join(projectRoot, "results", runId);
const workspace = path.join(runRoot, "workspace");

await mkdir(path.dirname(runRoot), { recursive: true });
await mkdir(runRoot);
await cp(path.join(projectRoot, "fixtures", "e2e-repo"), workspace, {
  recursive: true
});
await writeFile(path.join(runRoot, "skill.md"), skills.current);

await requireSuccess("git", ["init", "-q"], workspace);
await requireSuccess("git", ["add", "."], workspace);
await requireSuccess(
  "git",
  [
    "-c",
    "user.name=Brrr Eval",
    "-c",
    "user.email=brrr-eval@example.invalid",
    "commit",
    "-qm",
    "fixture baseline"
  ],
  workspace
);

const baselineTest = await runCommand("npm", ["test"], {
  cwd: workspace,
  timeoutMs: 30000
});
await writeFile(
  path.join(runRoot, "baseline-test.log"),
  `${baselineTest.stdout}${baselineTest.stderr}`
);
if (baselineTest.code === 0) {
  throw new Error("The end-to-end fixture must begin with a failing test.");
}

const instructions = [
  "Use the supplied Brrr skill to execute the approved brief in brief.md.",
  "Run npm test as explicitly authorized verification.",
  "Update the brief's Execution checklist with compact evidence.",
  "Keep publication separate and leave the git changes uncommitted.",
  "",
  skills.current
].join("\n");
const responsePath = path.join(runRoot, "response.md");
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
    "workspace-write",
    "--cd",
    workspace,
    "--json",
    "--output-last-message",
    responsePath,
    "-c",
    `developer_instructions=${JSON.stringify(instructions)}`,
    "--skip-git-repo-check",
    "Implement the approved brief now."
  ],
  { cwd: workspace, timeoutMs }
);
await writeFile(path.join(runRoot, "trace.jsonl"), result.stdout);
await writeFile(path.join(runRoot, "stderr.log"), result.stderr);
if (result.code !== 0) {
  throw new Error("The Brrr end-to-end model call failed.");
}

const finalTest = await runCommand("npm", ["test"], {
  cwd: workspace,
  timeoutMs: 30000
});
await writeFile(
  path.join(runRoot, "final-test.log"),
  `${finalTest.stdout}${finalTest.stderr}`
);
const brief = await readFile(path.join(workspace, "brief.md"), "utf8");
const status = await requireSuccess("git", ["status", "--short"], workspace);
const workspaceDiff = await requireSuccess("git", ["diff"], workspace);
await writeFile(path.join(runRoot, "workspace.diff"), workspaceDiff.stdout);
const commitCount = await requireSuccess(
  "git",
  ["rev-list", "--count", "HEAD"],
  workspace
);
const checks = {
  baseline_reproduced: baselineTest.code !== 0,
  focused_test_passes: finalTest.code === 0,
  execution_record_updated: /- \[x\].*npm test/iu.test(brief),
  changes_left_uncommitted:
    commitCount.stdout.trim() === "1" &&
    status.stdout.includes("brief.md") &&
    status.stdout.includes("src/normalize-name.mjs")
};
const score = Object.values(checks).filter(Boolean).length * 25;
const summary = {
  schema_version: 1,
  run_id: runId,
  model,
  reasoning_effort: reasoningEffort,
  skill_sha256: sha256(skills.current),
  score,
  checks,
  git_status: status.stdout.trim().split("\n").filter(Boolean)
};
await writeFile(
  path.join(runRoot, "summary.json"),
  `${JSON.stringify(summary, null, 2)}\n`
);
await writeFile(
  path.join(runRoot, "result.md"),
  [
    "# Brrr end-to-end result",
    "",
    `Run: \`${runId}\``,
    "",
    `Score: ${score}/100`,
    "",
    ...Object.entries(checks).map(
      ([name, passed]) => `- ${passed ? "PASS" : "FAIL"}: ${name}`
    ),
    ""
  ].join("\n")
);
console.log(JSON.stringify(summary, null, 2));

async function requireSuccess(command, args, cwd) {
  const result = await runCommand(command, args, { cwd, timeoutMs: 30000 });
  if (result.code !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed: ${result.stderr}`);
  }
  return result;
}

function runCommand(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.cwd,
      stdio: ["ignore", "pipe", "pipe"]
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
  });
}
