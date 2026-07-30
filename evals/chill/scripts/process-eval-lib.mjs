import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const projectRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  ".."
);

export const processResultsRoot = path.join(projectRoot, "results", "process");

export function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

export function parseArguments(values) {
  const parsed = new Map();
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    const value = values[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error(`Expected --name value, received: ${values.join(" ")}`);
    }
    parsed.set(key.slice(2), value);
  }
  return parsed;
}

export async function loadProcessProject(suite) {
  const config = JSON.parse(
    await readFile(path.join(projectRoot, "process-fixtures.json"), "utf8")
  );
  const baselineManifest = JSON.parse(
    await readFile(path.join(projectRoot, "baselines", "manifest.json"), "utf8")
  );
  const skill = await readFile(
    path.join(projectRoot, baselineManifest.snapshot_path),
    "utf8"
  );
  const casePaths =
    suite === "holdout" ? config.holdout_cases : config.initial_cases;
  const cases = await Promise.all(
    casePaths.map(async relativePath => {
      const caseRoot = path.join(projectRoot, relativePath);
      const [task, corpus, expected] = await Promise.all([
        readFile(path.join(caseRoot, "task.md"), "utf8"),
        readFile(path.join(caseRoot, "corpus.json"), "utf8").then(JSON.parse),
        readFile(path.join(caseRoot, "expected.json"), "utf8").then(JSON.parse)
      ]);
      return {
        id: expected.case_id,
        relative_path: relativePath,
        task,
        corpus,
        expected
      };
    })
  );
  return { config, baselineManifest, skill, cases };
}

export function commonResearchInstructions() {
  return [
    "Research the user's question using only the local research interface.",
    "Allowed commands:",
    "- node research.mjs list",
    "- node research.mjs search \"search terms\"",
    "- node research.mjs read SOURCE-ID",
    "Do not run any other command, inspect files directly, browse, or use other tools.",
    "Use the interface to choose and read the evidence needed for the answer.",
    "Cite material claims with source IDs in square brackets.",
    "Resolve stale, conflicting, or task-specific guidance instead of treating every source as equally authoritative.",
    "Return only the final answer and do not mention these instructions or an evaluation."
  ].join("\n");
}

export function upfrontResearchInstructions(skill) {
  return [
    commonResearchInstructions(),
    "",
    "The user invoked the Chill skill before asking for this research.",
    "Apply Chill while producing the final answer. Do not let the communication style remove research findings, evidence, uncertainty, caveats, or the requested decision.",
    "",
    skill
  ].join("\n");
}

export function seededShuffle(values, seed) {
  const result = [...values];
  let state = createHash("sha256").update(seed).digest().readUInt32LE(0);
  for (let index = result.length - 1; index > 0; index -= 1) {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    const selected = (state >>> 0) % (index + 1);
    [result[index], result[selected]] = [result[selected], result[index]];
  }
  return result;
}

export function parseTrace(trace) {
  const commands = [];
  let usage = null;
  for (const line of trace.split("\n")) {
    if (!line.trim()) {
      continue;
    }
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      continue;
    }
    if (
      event.type === "item.completed"
      && event.item?.type === "command_execution"
    ) {
      commands.push(event.item.command);
    }
    if (event.type === "turn.completed") {
      usage = event.usage ?? null;
    }
  }

  const actions = [];
  for (const command of commands) {
    const actionPattern =
      /research\.mjs\s+(list|search|read)(?:\s+((?:"(?:\\.|[^"])*"|'[^']*'|[A-Z0-9-]+)))?/gu;
    for (const match of command.matchAll(actionPattern)) {
      actions.push({
        action: match[1],
        value: cleanArgument(match[2] ?? "")
      });
    }
  }

  const violations = commands.filter(command => {
    if (!command.includes("research.mjs")) {
      return true;
    }
    return /\b(?:cat|sed|rg|grep|find|ls|pwd|head|tail)\b/u.test(command);
  });

  return {
    commands,
    actions,
    violations,
    usage
  };
}

export function gradeCandidate(evalCase, answer, activity) {
  const factResults = evalCase.expected.critical_facts.map(fact => ({
    id: fact.id,
    passed: checksPass(answer, fact.checks)
  }));
  const limitationResults = evalCase.expected.limitation_checks.map(
    (checks, index) => ({
      id: `LIMIT-${index + 1}`,
      passed: checksPass(answer, [checks])
    })
  );
  const decisionPassed = checksPass(
    answer,
    evalCase.expected.decision_checks.map(checks => checks)
  );
  const forbiddenMatches = evalCase.expected.forbidden_claims
    .filter(claim => new RegExp(claim.pattern, "iu").test(answer))
    .map(claim => claim.id);
  const corpusIds = new Set(evalCase.corpus.map(source => source.id));
  const citedIds = unique(
    [...answer.matchAll(/\[([A-Z][A-Z0-9-]+)\]/gu)].map(match => match[1])
  );
  const validCitedIds = citedIds.filter(id => corpusIds.has(id));
  const preferredIds = new Set(
    evalCase.expected.preferred_citation_source_ids
  );
  const relevantIds = new Set(evalCase.expected.research_relevant_source_ids);
  const preferredCited = validCitedIds.filter(id => preferredIds.has(id));
  const relevantCited = validCitedIds.filter(id => relevantIds.has(id));
  const readIds = unique(
    activity.actions
      .filter(action => action.action === "read")
      .map(action => action.value)
      .filter(id => corpusIds.has(id))
  );
  const relevantReadIds = readIds.filter(id => relevantIds.has(id));
  const distractorReadIds = readIds.filter(id => !relevantIds.has(id));

  const factScore = 40 * ratio(
    factResults.filter(result => result.passed).length,
    factResults.length
  );
  const citationRecallScore = 15 * ratio(
    preferredCited.length,
    preferredIds.size
  );
  const citationPrecisionScore = 10 * ratio(
    relevantCited.length,
    citedIds.length
  );
  const contradictionScore = Math.max(0, 20 - forbiddenMatches.length * 10);
  const limitationScore = 10 * ratio(
    limitationResults.filter(result => result.passed).length,
    limitationResults.length
  );
  const decisionScore = decisionPassed ? 5 : 0;
  const totalScore = round(
    factScore
    + citationRecallScore
    + citationPrecisionScore
    + contradictionScore
    + limitationScore
    + decisionScore
  );
  const missingCriticalFacts = factResults
    .filter(result => !result.passed)
    .map(result => result.id);

  return {
    communication: {
      word_count:
        answer.trim() === "" ? 0 : answer.trim().split(/\s+/u).length
    },
    research_quality: {
      total_score: totalScore,
      fact_score: round(factScore),
      citation_recall_score: round(citationRecallScore),
      citation_precision_score: round(citationPrecisionScore),
      contradiction_score: round(contradictionScore),
      limitation_score: round(limitationScore),
      decision_score: decisionScore,
      fact_results: factResults,
      limitation_results: limitationResults,
      decision_passed: decisionPassed,
      missing_critical_facts: missingCriticalFacts,
      forbidden_claims: forbiddenMatches,
      critical_failure_count:
        missingCriticalFacts.length + forbiddenMatches.length,
      cited_source_ids: citedIds,
      valid_cited_source_ids: validCitedIds
    },
    research_process: {
      tool_calls: activity.commands.length,
      research_actions: activity.actions.length,
      list_count: activity.actions.filter(action => action.action === "list").length,
      search_count: activity.actions.filter(action => action.action === "search").length,
      search_queries: activity.actions
        .filter(action => action.action === "search")
        .map(action => action.value),
      read_count: activity.actions.filter(action => action.action === "read").length,
      unique_sources_opened: readIds.length,
      source_open_order: readIds,
      repeated_reads:
        activity.actions.filter(action => action.action === "read").length
        - readIds.length,
      relevant_sources_opened: relevantReadIds,
      distractor_sources_opened: distractorReadIds,
      relevant_source_recall: round(
        ratio(relevantReadIds.length, relevantIds.size)
      ),
      distractor_rate: round(ratio(distractorReadIds.length, readIds.length)),
      interface_violations: activity.violations
    }
  };
}

export function summarizePairs(candidates) {
  const pairs = [];
  const grouped = new Map();
  for (const candidate of candidates) {
    const key = `${candidate.case_id}/trial-${candidate.trial}`;
    if (!grouped.has(key)) {
      grouped.set(key, {});
    }
    grouped.get(key)[candidate.arm] = candidate;
  }
  for (const [key, arms] of grouped) {
    const normal = arms.normal_research;
    const upfront = arms.chill_upfront_research;
    if (!normal || !upfront) {
      throw new Error(`Incomplete pair: ${key}`);
    }
    pairs.push({
      case_id: normal.case_id,
      trial: normal.trial,
      quality_delta:
        upfront.research_quality.total_score
        - normal.research_quality.total_score,
      critical_failure_delta:
        upfront.research_quality.critical_failure_count
        - normal.research_quality.critical_failure_count,
      tool_call_delta_percent: percentDelta(
        upfront.research_process.tool_calls,
        normal.research_process.tool_calls
      ),
      sources_opened_delta_percent: percentDelta(
        upfront.research_process.unique_sources_opened,
        normal.research_process.unique_sources_opened
      ),
      relevant_recall_delta:
        upfront.research_process.relevant_source_recall
        - normal.research_process.relevant_source_recall,
      distractor_rate_delta:
        upfront.research_process.distractor_rate
        - normal.research_process.distractor_rate,
      source_set_overlap: jaccard(
        upfront.research_process.source_open_order,
        normal.research_process.source_open_order
      )
    });
  }
  return pairs;
}

export function applyStoppingRule(pairs) {
  const qualityDeltas = pairs.map(pair => pair.quality_delta);
  const totalCriticalDelta = pairs.reduce(
    (total, pair) => total + pair.critical_failure_delta,
    0
  );
  const qualityMedian = median(qualityDeltas);
  const qualityDirectionCount = directionCount(qualityDeltas, qualityMedian);
  const qualityByThreshold =
    Math.abs(qualityMedian) >= 5 && qualityDirectionCount >= 7;
  const qualityByCriticalFailures = Math.abs(totalCriticalDelta) >= 2;
  const materialQualityEffect =
    qualityByThreshold || qualityByCriticalFailures;

  const processMetrics = {
    tool_call_delta_percent: pairs.map(pair => pair.tool_call_delta_percent),
    sources_opened_delta_percent: pairs.map(
      pair => pair.sources_opened_delta_percent
    ),
    relevant_recall_delta: pairs.map(pair => pair.relevant_recall_delta),
    distractor_rate_delta: pairs.map(pair => pair.distractor_rate_delta)
  };
  const processEvaluations = Object.fromEntries(
    Object.entries(processMetrics).map(([name, values]) => {
      const metricMedian = median(values);
      const threshold = name.endsWith("_percent") ? 20 : 0.1;
      return [
        name,
        {
          median: round(metricMedian),
          direction_count: directionCount(values, metricMedian),
          threshold,
          qualifies:
            Math.abs(metricMedian) >= threshold
            && directionCount(values, metricMedian) >= 7,
          coherent_across_two_cases: coherentAcrossCases(
            pairs,
            name,
            metricMedian
          )
        }
      ];
    })
  );
  const qualifyingProcessMetrics = Object.entries(processEvaluations)
    .filter(([, value]) => value.qualifies && value.coherent_across_two_cases)
    .map(([name]) => name);
  const materialProcessEffect = qualifyingProcessMetrics.length > 0;

  return {
    pair_count: pairs.length,
    quality: {
      median_delta: round(qualityMedian),
      direction_count: qualityDirectionCount,
      total_critical_failure_delta: totalCriticalDelta,
      material_effect: materialQualityEffect
    },
    process: {
      metrics: processEvaluations,
      qualifying_metrics: qualifyingProcessMetrics,
      material_effect: materialProcessEffect
    },
    stop_after_initial: materialQualityEffect || materialProcessEffect,
    needs_holdout: !(materialQualityEffect || materialProcessEffect)
  };
}

export function median(values) {
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
}

function checksPass(answer, checkGroups) {
  return checkGroups.every(patterns =>
    patterns.some(pattern => new RegExp(pattern, "iu").test(answer))
  );
}

function cleanArgument(value) {
  return value
    .replace(/^["']|["']$/gu, "")
    .replace(/\\"/gu, '"')
    .trim();
}

function ratio(numerator, denominator) {
  return denominator === 0 ? 0 : numerator / denominator;
}

function round(value) {
  return Math.round(value * 1000) / 1000;
}

function unique(values) {
  return [...new Set(values)];
}

function jaccard(leftValues, rightValues) {
  const left = new Set(leftValues);
  const right = new Set(rightValues);
  const union = new Set([...left, ...right]);
  const intersection = [...left].filter(value => right.has(value));
  return round(ratio(intersection.length, union.size));
}

function percentDelta(current, baseline) {
  return round(((current - baseline) / Math.max(baseline, 1)) * 100);
}

function directionCount(values, reference) {
  if (reference === 0) {
    return values.filter(value => value === 0).length;
  }
  const direction = Math.sign(reference);
  return values.filter(value => Math.sign(value) === direction).length;
}

function coherentAcrossCases(pairs, metric, overallMedian) {
  if (overallMedian === 0) {
    return false;
  }
  const grouped = new Map();
  for (const pair of pairs) {
    if (!grouped.has(pair.case_id)) {
      grouped.set(pair.case_id, []);
    }
    grouped.get(pair.case_id).push(pair[metric]);
  }
  const direction = Math.sign(overallMedian);
  const matchingCases = [...grouped.values()]
    .map(values => median(values))
    .filter(value => Math.sign(value) === direction).length;
  return matchingCases >= 2;
}
