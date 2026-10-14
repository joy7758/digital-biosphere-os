import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const publicRoot = new URL("../public/", import.meta.url);
const [status, agentIndex, customerPackage, llms, dbosPackage, wellKnown, ledgerTransition] = await Promise.all([
  readFile(new URL("status.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("agent-index.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("agent-customer-package.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("llms.txt", publicRoot), "utf8"),
  readFile(new URL("dbos-public-package-manifest.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL(".well-known/titmas.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("architecture/cr01-ledger-transition-design-v1.0.json", publicRoot), "utf8").then(JSON.parse),
]);

async function render(pathname) {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("machine-truth-test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);
  const response = await worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
  assert.equal(response.status, 200);
  return response.text();
}

const [zhHome, enHome, zhStatus, enStatus] = await Promise.all([
  render("/"),
  render("/en"),
  render("/status"),
  render("/en/status"),
]);

function assertJsonTruth(key, expected) {
  assert.equal(status[key], expected);
  assert.equal(agentIndex[key], expected);
  assert.equal(customerPackage.current_truth[key], expected);
}

test("MT-01 current stage agrees", () => {
  const expected = "TITMAS_AGENT_NATIVE_COMMERCIAL_MATURITY_PROGRAM";
  assertJsonTruth("current_stage", expected);
  assert.match(llms, new RegExp(`CURRENT_STAGE=${expected}`));
  assert.match(zhHome, /当前商业事实/);
  assert.match(enHome, /CURRENT COMMERCIAL TRUTH/);
});

test("MT-00 public brand stays distinct from the TITMAS technical identifier", () => {
  assert.equal(agentIndex.display_name_zh, "夏日之海");
  assert.equal(agentIndex.display_name_en, "titmas");
  assert.equal(agentIndex.public_brand_logo, "/titmas-logo.png");
  assert.equal(agentIndex.technical_project_identifier, "TITMAS");
  assert.equal(status.community.canonical_name_zh, "夏日之海");
  assert.equal(status.community.canonical_name_en, "titmas");
  assert.equal(status.community.public_brand_logo, "/titmas-logo.png");
  assert.equal(wellKnown.display_brand_zh, "夏日之海");
  assert.equal(wellKnown.display_brand_en, "titmas");
  assert.equal(wellKnown.public_brand_logo, "/titmas-logo.png");
  assert.equal(wellKnown.technical_brand, "TITMAS");
  assert.match(zhHome, /\/titmas-logo\.png/);
  assert.match(enHome, /aria-label="titmas · Trusted Multi-Agent Infrastructure"/);
  assert.doesNotMatch(zhHome, /\/summersea-logo\.png/);
  assert.doesNotMatch(enHome, /\/summersea-logo\.png/);
});

test("MT-00A commercial collection entries are Agent-readable and bilingual", () => {
  const expected = {
    platform_collection_zh: "/platform/",
    platform_collection_en: "/en/platform/",
    products_collection_zh: "/products/",
    products_collection_en: "/en/products/",
    solutions_collection_zh: "/solutions/",
    solutions_collection_en: "/en/solutions/",
    proof_collection_zh: "/proof/",
    proof_collection_en: "/en/proof/",
  };
  for (const [key, value] of Object.entries(expected)) {
    assert.equal(agentIndex.entrypoints[key], value);
    assert.match(llms, new RegExp(`${key.toUpperCase()}=${value.replaceAll("/", "\\/")}`));
  }
});

test("MT-02 E01 status agrees", () => {
  const expected = "EXPIRED_ACCESS_REVOKED_NO_CONTRIBUTION_OBSERVED";
  assertJsonTruth("e01_status", expected);
  assert.match(llms, new RegExp(`E01_STATUS=${expected}`));
  assert.match(zhStatus, new RegExp(expected));
  assert.match(enStatus, new RegExp(expected));
  assertJsonTruth("e01_participant_access_authorized", false);
  assertJsonTruth("e01_participant_access_active", false);
  assert.equal(status.e01_access_mode, "NONE");
  assert.equal(agentIndex.e01_access_mode, "NONE");
  assert.equal(customerPackage.current_truth.e01_access_mode, "NONE");
  assert.match(llms, /E01_PARTICIPANT_ACCESS_ACTIVE=false/);
  assert.match(llms, /E01_HUMAN_DISPOSITION=NOT_RECORDED/);
});

test("MT-03 private core status agrees", () => {
  assertJsonTruth("current_core_repository_visibility", "PRIVATE");
  assertJsonTruth("public_core_clone_available", false);
  assert.match(llms, /CURRENT_CORE_REPOSITORY_VISIBILITY=PRIVATE/);
  assert.match(zhHome, /闭源私有核心/);
  assert.match(enHome, /closed private core/i);
});

test("MT-04 public intake status agrees", () => {
  assertJsonTruth("titmas_public_trial_interest_entry_active", true);
  assert.match(llms, /TITMAS_PUBLIC_TRIAL_INTEREST_ENTRY_ACTIVE=true/);
});

test("MT-05 compensated recruitment history is retired", () => {
  assertJsonTruth("compensated_trial_recruitment_demand_submitted", true);
  assertJsonTruth("compensated_trial_recruitment_publication_confirmed", true);
  assertJsonTruth("compensated_human_trial_strategy_status", "RETIRED");
  assert.match(llms, /COMPENSATED_HUMAN_TRIAL_STRATEGY_STATUS=RETIRED/);
  assert.match(zhStatus, /COMPENSATED_HUMAN_TRIAL_STRATEGY/);
  assert.match(enStatus, /COMPENSATED_HUMAN_TRIAL_STRATEGY/);
  assert.doesNotMatch(zhHome, /程序员客栈|需求ID/);
  assert.doesNotMatch(enHome, /Proginn|demand ID/i);
});

test("MT-11 Stage 5.7 evidence agrees", () => {
  assertJsonTruth("agent_absolute_priority_principle_adopted", true);
  assertJsonTruth("primary_operational_customer", "AI_AGENT");
  assert.equal(status.stage5_7_agent_native_selection_roi.valid_sessions, 24);
  assert.equal(agentIndex.stage5_7_agent_native_selection_roi.valid_sessions, 24);
  assert.equal(status.stage5_7_agent_native_selection_roi.agent_selection_auditor_status, "PASS");
  assert.match(llms, /OPTION_D_RANKED_FIRST=24\/24/);
});

test("MT-06 protocol release status agrees", () => {
  assertJsonTruth("public_protocol_released", false);
  assert.match(llms, /PUBLIC_PROTOCOL_RELEASED=false/);
  assert.match(zhStatus, /PUBLIC_PROTOCOL_RELEASED/);
  assert.match(enStatus, /PUBLIC_PROTOCOL_RELEASED/);
});

test("MT-07 commercial status agrees", () => {
  assertJsonTruth("commercial_access_granted", false);
  assert.match(llms, /COMMERCIAL_ACCESS_GRANTED=false/);
  assert.match(zhStatus, /COMMERCIAL_ACCESS_GRANTED/);
  assert.match(enStatus, /COMMERCIAL_ACCESS_GRANTED/);
});

test("MT-12 CR-01 restore failure remains fail-closed across public surfaces", () => {
  const expectedSource = "c319001cc1cf9e44d8b3d0b142a025c6c9af1678";
  const expectedRelease = "9bbfce6154d67f4ab50e911b5e49611f5a4a8b57";
  const expectedIntegration = "6ed4dadd4693129d3daca0a9a29964a4f7f864e9";
  for (const candidate of [status.commercial_candidate, agentIndex.commercial_candidate]) {
    assert.equal(candidate.status, "WAITING_FOR_HUMAN_DECISION");
    assert.equal(candidate.cr01_status, "BLOCKED_LEDGER_INTEGRITY");
    assert.equal(candidate.data_plane_repository_revision, expectedSource);
    assert.equal(candidate.live_commercial_release_revision, expectedRelease);
    assert.equal(candidate.integration_source_revision, expectedIntegration);
    assert.equal(candidate.cr01_d02_status, "ACCEPTED_DESIGN_ONLY");
    assert.equal(
      candidate.ledger_transition_recommendation,
      "IMMUTABLE_EXCEPTION_MANIFEST_PLUS_TENANT_SCOPED_CLEAN_EPOCH",
    );
    assert.equal(candidate.ledger_transition_implementation_authorized, false);
    assert.equal(candidate.second_deployment_retry_authorized, false);
    assert.equal(candidate.soak_execution_authorized, false);
    assert.equal(candidate.backup_integrity_pass, true);
    assert.equal(candidate.structural_restore_pass, true);
    assert.equal(candidate.restored_receipt_verification_pass, false);
    assert.equal(candidate.restored_receipt_signatures_invalid, 2);
    assert.equal(candidate.backup_restore_drill_pass, false);
    assert.equal(candidate.restore_rto_status, "NOT_ESTABLISHED");
  }
  assert.match(llms, /CR01_STATUS=BLOCKED_LEDGER_INTEGRITY/);
  assert.match(llms, /CR01_D02_STATUS=ACCEPTED_DESIGN_ONLY/);
  assert.match(llms, /LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED=false/);
  assert.match(llms, /BACKUP_RESTORE_DRILL_PASS=false/);
  assert.match(llms, /RESTORE_RTO_STATUS=NOT_ESTABLISHED/);
  assert.equal(wellKnown.deployment_evidence.cr01_status, "BLOCKED_LEDGER_INTEGRITY");
  assert.equal(wellKnown.sdk_locations.source_revision, expectedIntegration);
  assert.equal(wellKnown.deployment_evidence.cr01_d02_status, "ACCEPTED_DESIGN_ONLY");
  assert.equal(wellKnown.deployment_evidence.ledger_transition_implementation_authorized, false);
  assert.equal(ledgerTransition.projection_role, "PUBLIC_DERIVED_VIEW");
  assert.equal(ledgerTransition.decision_status, "ACCEPTED_DESIGN_ONLY");
  assert.equal(ledgerTransition.retained_facts.signatures_unverifiable, 2);
  assert.deepEqual(ledgerTransition.recommended_option.anchor, [
    "LEGACY_TENANT_CHAIN_TIP_HASH",
    "TRANSITION_MANIFEST_DIGEST",
  ]);
  assert.equal("anchors" in ledgerTransition.recommended_option, false);
  assert.equal(ledgerTransition.recommended_option.legacy_validity_override, false);
  assert.equal(ledgerTransition.authorization.implementation, false);
  assert.equal(wellKnown.deployment_evidence.restored_receipt_verification_pass, false);
  assert.equal(wellKnown.deployment_evidence.backup_restore_drill_pass, false);
  assert.equal(wellKnown.deployment_evidence.restore_rto_status, "NOT_ESTABLISHED");
  assert.match(zhStatus, /BLOCKED_LEDGER_INTEGRITY/);
  assert.match(enStatus, /BLOCKED_LEDGER_INTEGRITY/);
});

test("MT-08 community status agrees", () => {
  assertJsonTruth("titmas_community_established", false);
  assert.match(llms, /TITMAS_COMMUNITY_ESTABLISHED=false/);
  assert.equal(status.community.current_state, "HISTORICAL_NON_CURRENT");
  assert.equal(agentIndex.community.current_state, "HISTORICAL_NON_CURRENT");
  assert.match(llms, /COMMUNITY_MATERIAL_STATUS=HISTORICAL_NON_CURRENT/);
});

test("MT-09 production status agrees", () => {
  assertJsonTruth("production_ready", false);
  assert.match(llms, /PRODUCTION_READY=false/);
  assert.match(zhStatus, /PRODUCTION_READY/);
  assert.match(enStatus, /PRODUCTION_READY/);
});

test("MT-10 private repository URLs are absent", () => {
  const publicText = [
    JSON.stringify(status),
    JSON.stringify(agentIndex),
    JSON.stringify(customerPackage),
    JSON.stringify(dbosPackage),
    llms,
    zhHome,
    enHome,
    zhStatus,
    enStatus,
  ].join("\n");
  const privateRepositoryUrls = [
    /github\.com\/joy7758\/digital-biosphere-architecture-specification/i,
    /github\.com\/joy7758\/digital-biosphere-os/i,
    /github\.com\/joy7758\/SAEE/i,
    /github\.com\/joy7758\/titmas-private-developer-trial/i,
  ];
  for (const pattern of privateRepositoryUrls) assert.doesNotMatch(publicText, pattern);
});
