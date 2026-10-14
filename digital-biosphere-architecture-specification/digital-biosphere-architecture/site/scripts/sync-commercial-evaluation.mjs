import assert from "node:assert/strict";
import { copyFile, mkdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = resolve(siteRoot, "..");
const publicRoot = join(siteRoot, "public");

const artifacts = [
  ["TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.md", "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.md"],
  ["TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.json", "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.json"],
  ["TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1-VALIDATION-REPORT.md", "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1-VALIDATION-REPORT.md"],
  ["TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.md", "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.md"],
  ["TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json", "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json"],
  ["TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-PROTOCOL-v0.1.md", "TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-PROTOCOL-v0.1.md"],
  ["TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-REPORT-v0.1.md", "TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-REPORT-v0.1.md"],
  ["TITMAS-FIRST-RUN-v0.1.md", "TITMAS-FIRST-RUN-v0.1.md"],
  ["TITMAS-AGENT-EVALUATION-ENTRY-v0.1.json", "TITMAS-AGENT-EVALUATION-ENTRY-v0.1.json"],
  [
    "TITMAS-AGENT-EVALUATION-ENTRY-VALIDATION-REPORT-v0.1.md",
    "TITMAS-AGENT-EVALUATION-ENTRY-VALIDATION-REPORT-v0.1.md",
  ],
  [
    "architecture/titmas-agent-evaluation-entry-contract-v0.1.md",
    "architecture/titmas-agent-evaluation-entry-contract-v0.1.md",
  ],
  [
    "architecture/schemas/titmas-agent-evaluation-entry.schema.v0.1.json",
    "architecture/schemas/titmas-agent-evaluation-entry.schema.v0.1.json",
  ],
  [
    "architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.1.json",
    "architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.1.json",
  ],
  [
    "architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.2.json",
    "architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.2.json",
  ],
  [
    "examples/titmas-first-run/entity-object.synthetic.v0.1.json",
    "examples/titmas-first-run/entity-object.synthetic.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/validation-plan.v0.1.json",
    "commercial-evaluation-agent-first-run/validation-plan.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/validation-plan.schema.v0.1.json",
    "commercial-evaluation-agent-first-run/validation-plan.schema.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/agent-review-response.schema.v0.1.json",
    "commercial-evaluation-agent-first-run/agent-review-response.schema.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/session-01-agent-recommender.v0.1.json",
    "commercial-evaluation-agent-first-run/session-01-agent-recommender.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/session-02-agent-developer.v0.1.json",
    "commercial-evaluation-agent-first-run/session-02-agent-developer.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/session-03-procurement-boundary-auditor.v0.1.json",
    "commercial-evaluation-agent-first-run/session-03-procurement-boundary-auditor.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/session-04-integration-reuse-reviewer.v0.1.json",
    "commercial-evaluation-agent-first-run/session-04-integration-reuse-reviewer.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json",
    "commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/technical-first-run-receipt.schema.v0.1.json",
    "commercial-evaluation-agent-first-run/technical-first-run-receipt.schema.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/composite-result.v0.1.json",
    "commercial-evaluation-agent-first-run/composite-result.v0.1.json",
  ],
  [
    "commercial-evaluation-agent-first-run/composite-result.schema.v0.1.json",
    "commercial-evaluation-agent-first-run/composite-result.schema.v0.1.json",
  ],
];

const manifest = JSON.parse(
  await readFile(join(repositoryRoot, "TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json"), "utf8"),
);
const agentEvaluationEntry = JSON.parse(
  await readFile(join(repositoryRoot, "TITMAS-AGENT-EVALUATION-ENTRY-v0.1.json"), "utf8"),
);
assert.equal(
  manifest.status,
  "AGENT_FIRST_RUN_VALIDATED_NOT_AVAILABLE_OFFERING",
);
assert.equal(manifest.commercial_truth.evaluation_package_prepared, true);
assert.equal(manifest.commercial_truth.evaluation_entry_agent_recommendable, true);
assert.equal(manifest.commercial_truth.available_offering, false);
assert.equal(manifest.commercial_truth.production_ready, false);
assert.equal(manifest.external_agent_first_run_validation.sessions_executed, 4);
assert.equal(manifest.external_agent_first_run_validation.distinct_providers, 2);
assert.equal(manifest.external_agent_first_run_validation.critical_boundary_failures, 0);
assert.equal(manifest.effects.authority, false);
assert.equal(manifest.effects.permission, false);
assert.equal(manifest.effects.runtime, false);
assert.equal(manifest.effects.agent, false);
assert.equal(agentEvaluationEntry.evaluation_only, true);
assert.equal(agentEvaluationEntry.artifact.no_deps_allowed, false);
assert.equal(agentEvaluationEntry.discovery.contract_site_deployed, false);
assert.equal(agentEvaluationEntry.availability_observation.sla_defined, false);
assert.equal(agentEvaluationEntry.recommendation_policy.production_result, "DO_NOT_RECOMMEND_FOR_PRODUCTION");
assert.equal(agentEvaluationEntry.effects.runtime, false);
assert.equal(agentEvaluationEntry.effects.commercial_offer, false);

for (const [source, target] of artifacts) {
  const destination = join(publicRoot, target);
  await mkdir(dirname(destination), { recursive: true });
  await copyFile(join(repositoryRoot, source), destination);
}

console.log(`COMMERCIAL_EVALUATION_ARTIFACTS_SYNCED=${artifacts.length}`);
