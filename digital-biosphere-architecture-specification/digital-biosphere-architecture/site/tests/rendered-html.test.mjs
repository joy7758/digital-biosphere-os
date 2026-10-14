import assert from "node:assert/strict";
import { access, readFile, readdir } from "node:fs/promises";
import test from "node:test";
import { resolveReleaseContext, routeMarkers } from "../scripts/release-mode.mjs";

const publicRoot = new URL("../public/", import.meta.url);
const [publicStatus, publicAgentIndex, publicAgentCustomerPackage, publicDbosPackage] = await Promise.all([
  readFile(new URL("status.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("agent-index.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("agent-customer-package.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("dbos-public-package-manifest.json", publicRoot), "utf8").then(JSON.parse),
]);
const releaseContext = resolveReleaseContext(process.env, {
  status: publicStatus,
  agentIndex: publicAgentIndex,
  agentCustomerPackage: publicAgentCustomerPackage,
  dbosPackage: publicDbosPackage,
});
const expectedMarkers = routeMarkers(releaseContext.mode);

async function render(pathname = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("renders equivalent Chinese and English public entry points", async () => {
  const [zhResponse, enResponse] = await Promise.all([render("/"), render("/en")]);
  assert.equal(zhResponse.status, 200);
  assert.equal(enResponse.status, 200);

  const [zhRaw, enRaw] = await Promise.all([zhResponse.text(), enResponse.text()]);
  const zh = zhRaw.replace(/<html lang="[^"]+">/, '<html lang="zh-CN">');
  const en = enRaw.replace(/<html lang="[^"]+">/, '<html lang="en">');

  assert.match(zh, /让 AI 智能体犯错时，也不能直接造成未经验证的后果/);
  assert.match(en, /An AI agent mistake should not directly create an unverified consequence/);
  assert.match(zh, /夏日之海/);
  assert.match(zh, /\/titmas-logo\.png/);
  assert.match(en, /aria-label="titmas · Trusted Multi-Agent Infrastructure"/);
  assert.match(en, /\/titmas-logo\.png/);
  assert.doesNotMatch(zh, /\/summersea-logo\.png/);
  assert.doesNotMatch(en, /\/summersea-logo\.png/);
  assert.match(zh, /<title>山西游骑兵电子商务有限公司<\/title>/);
  assert.match(en, /<title>山西游骑兵电子商务有限公司<\/title>/);
  assert.match(zh, /网站运营主体[^<]*：山西游骑兵电子商务有限公司/);
  assert.match(en, /Website operator[^<]*：山西游骑兵电子商务有限公司/);
  assert.match(zh, /晋ICP备2026006409号-1/);
  assert.match(en, /晋ICP备2026006409号-1/);
  assert.match(zh, /href="https:\/\/beian\.miit\.gov\.cn"[^>]*>工业和信息化部备案管理系统/);
  assert.match(en, /href="https:\/\/beian\.miit\.gov\.cn"[^>]*>工业和信息化部备案管理系统/);
  for (const marker of expectedMarkers.zhHome) assert.match(zh, new RegExp(marker));
  for (const marker of expectedMarkers.enHome) assert.match(en, new RegExp(marker));
  assert.match(zh, /Evidence/);
  assert.match(en, /Evidence/);
  assert.match(zh, /关键行动控制与可验证追责/);
  assert.match(en, /Critical-action control and verifiable accountability/);
  assert.match(zh, /Verification ≠ Authorization/);
  assert.match(en, /Request ≠ Access/);
  assert.match(zh, /机器商业目录/);
  assert.match(en, /Machine commercial catalogs/);
  assert.match(zh, /product-catalog\.json/);
  assert.match(en, /recommendation-policy\.json/);
  assert.match(zh, /AVAILABLE OFFERINGS/);
  assert.match(en, /AVAILABLE OFFERINGS/);
  assert.match(zh, /PRODUCTION READY[^<]*<\/span><strong>false/);
  assert.match(en, /PRODUCTION READY[^<]*<\/span><strong>false/);
  assert.match(zh, /人类与智能体双入口/);
  assert.match(en, /HUMAN AND AGENT ENTRY/);
  if (releaseContext.mode === "candidate") {
    assert.match(zh, /Developer Preview Candidate/);
    assert.match(en, /Developer Preview Candidate/);
    assert.doesNotMatch(zh, /production-ready|现已正式发布|已经正式发布/);
    assert.doesNotMatch(en, /production-ready|now released/i);
  } else {
    assert.doesNotMatch(zh, /Developer Preview Candidate/);
    assert.doesNotMatch(en, /Developer Preview Candidate/);
  }
});

test("renders bilingual status pages with fail-closed truth", async () => {
  const [zhResponse, enResponse] = await Promise.all([
    render("/status"),
    render("/en/status"),
  ]);
  const [zhRaw, enRaw] = await Promise.all([zhResponse.text(), enResponse.text()]);
  const zh = zhRaw.replace(/<html lang="[^"]+">/, '<html lang="zh-CN">');
  const en = enRaw.replace(/<html lang="[^"]+">/, '<html lang="en">');

  for (const marker of expectedMarkers.zhStatus) assert.match(zh, new RegExp(marker.replace(".", "\\.")));
  for (const marker of expectedMarkers.enStatus) assert.match(en, new RegExp(marker.replace(".", "\\.")));
  assert.match(zh, /AGENT_CUSTOMER_VALIDATION_BASELINE/);
  assert.match(en, /AGENT_CUSTOMER_VALIDATION_BASELINE/);
  assert.match(zh, /PASS/);
  assert.match(en, /PASS/);
  assert.match(zh, /PARTIAL/);
  assert.match(en, /PARTIAL/);
  assert.match(zh, /cd3f867c4379/);
  assert.match(en, /2173c258f91a/);
  assert.match(zh, /E01_STATUS/);
  assert.match(en, /E01_STATUS/);
  assert.match(zh, /COMPENSATED_HUMAN_TRIAL_STRATEGY/);
  assert.match(en, /COMPENSATED_HUMAN_TRIAL_STRATEGY/);
});

test("returns 404 for an unknown route", async () => {
  const response = await render("/this-route-does-not-exist");
  assert.equal(response.status, 404);
});

test("ships agent-readable and discovery resources", async () => {
  const root = new URL("../public/", import.meta.url);
  await Promise.all([
    access(new URL("llms.txt", root)),
    access(new URL("agent-index.json", root)),
    access(new URL("site-catalog.json", root)),
    access(new URL(".well-known/titmas.json", root)),
    access(new URL("media-evidence-profile.json", root)),
    access(new URL("media-evidence-reproduction.md", root)),
    access(new URL("titmas-community.json", root)),
    access(new URL("updates.json", root)),
    access(new URL("status.json", root)),
    access(new URL("agent-customer-package.json", root)),
    access(new URL("dbos-public-package-manifest.json", root)),
    access(new URL("robots.txt", root)),
    access(new URL("sitemap.xml", root)),
    access(new URL("titmas-logo.png", root)),
    access(new URL("evidence/stage5-7/aggregate-results.json", root)),
    access(new URL("evidence/stage5-7/agent-selection-audit.json", root)),
    access(new URL("evidence/stage5-7/evidence-manifest.json", root)),
    access(new URL("product-catalog.json", root)),
    access(new URL("solution-catalog.json", root)),
    access(new URL("proof-catalog.json", root)),
    access(new URL("commercial-offerings.json", root)),
    access(new URL("deployment-options.json", root)),
    access(new URL("recommendation-policy.json", root)),
  ]);

  const [agentIndex, status, agentCustomerPackage, dbosPackage, llms, siteCatalog, titmasCommunity, wellKnown] = await Promise.all([
    readFile(new URL("agent-index.json", root), "utf8").then(JSON.parse),
    readFile(new URL("status.json", root), "utf8").then(JSON.parse),
    readFile(new URL("agent-customer-package.json", root), "utf8").then(JSON.parse),
    readFile(new URL("dbos-public-package-manifest.json", root), "utf8").then(JSON.parse),
    readFile(new URL("llms.txt", root), "utf8"),
    readFile(new URL("site-catalog.json", root), "utf8").then(JSON.parse),
    readFile(new URL("titmas-community.json", root), "utf8").then(JSON.parse),
    readFile(new URL(".well-known/titmas.json", root), "utf8").then(JSON.parse),
  ]);
  assert.equal(agentIndex.released, releaseContext.developerPreviewReleased);
  assert.equal(status.gates.CROSS_PROJECT_CLEAN_CLONE_PASS, true);
  assert.equal(status.gates.TITMAS_INFRASTRUCTURE_DEVELOPER_COMMUNITY_DIRECTION_ADOPTED, true);
  assert.equal(status.gates.TITMAS_CONTRIBUTOR_ENTRY_PREPARED, true);
  assert.equal(status.gates.TITMAS_PUBLIC_CONTRIBUTION_SURFACE_AUTHORIZED, false);
  assert.equal(status.gates.TITMAS_DEVELOPER_COMMUNITY_ESTABLISHED, false);
  assert.equal(status.gates.TITMAS_CODE_OF_CONDUCT_ADOPTED, false);
  assert.equal(status.gates.TITMAS_MAINTAINER_ASSIGNED, false);
  assert.equal(status.gates.TITMAS_FOUNDATION_IN_SCOPE, false);
  assert.equal(status.community.current_state, "HISTORICAL_NON_CURRENT");
  assert.equal(status.community.canonical_name_en, "titmas");
  assert.equal(status.community.canonical_name_zh, "夏日之海");
  assert.equal(status.community.public_brand_logo, "/titmas-logo.png");
  assert.equal(status.community.technical_project_identifier, "TITMAS");
  assert.equal(status.community.public_contribution_surface_authorized, false);
  assert.deepEqual(status.community.maintainers, []);
  assert.equal(agentIndex.name, "TITMAS Commercial Agent Infrastructure");
  assert.equal(agentIndex.display_name_zh, "夏日之海");
  assert.equal(agentIndex.display_name_en, "titmas");
  assert.equal(agentIndex.public_brand, "titmas");
  assert.equal(agentIndex.public_brand_zh, "夏日之海");
  assert.equal(agentIndex.public_brand_logo, "/titmas-logo.png");
  assert.equal(agentIndex.technical_project_identifier, "TITMAS");
  assert.deepEqual(siteCatalog.public_brand, {
    zh: "夏日之海",
    en: "titmas",
    display_name_zh: "夏日之海",
    display_name_en: "titmas",
    logo: "/titmas-logo.png",
    technical_project_identifier: "TITMAS",
  });
  assert.equal(titmasCommunity.brand, "titmas");
  assert.equal(titmasCommunity.brand_zh, "夏日之海");
  assert.equal(titmasCommunity.brand_logo, "/titmas-logo.png");
  assert.equal(titmasCommunity.technical_project_identifier, "TITMAS");
  assert.equal(wellKnown.display_brand_en, "titmas");
  assert.equal(wellKnown.display_brand_zh, "夏日之海");
  assert.equal(wellKnown.public_brand_logo, "/titmas-logo.png");
  assert.equal(wellKnown.technical_brand, "TITMAS");
  assert.equal(agentIndex.abbreviation, "TITMAS");
  assert.equal(agentIndex.website_operator_legal_name, "山西游骑兵电子商务有限公司");
  assert.equal(agentIndex.public_website.operator_legal_name, "山西游骑兵电子商务有限公司");
  assert.equal(agentIndex.public_website.icp_record_number, "晋ICP备2026006409号-1");
  assert.equal(agentIndex.community.direction_adopted, false);
  assert.equal(agentIndex.community.historical_direction_recorded, true);
  assert.equal(agentIndex.community.public_submission_invitation, false);
  assert.equal(status.gates.DQ_010_SUPERSEDED_FOR_PRIMARY_ROUTE, true);
  assert.equal(status.gates.AGENT_CUSTOMER_VALIDATION_BASELINE_CONDITIONAL, true);
  assert.equal(status.gates.AGENT_CUSTOMER_VALIDATION_RERUN_PASS, true);
  assert.equal(status.agent_customer_validation.api_sessions_completed, 12);
  assert.equal(status.agent_customer_validation.result, "PASS");
  assert.equal(status.agent_customer_validation.open_web_discovery, "NOT_ASSESSED");
  assert.equal(status.open_web_discovery.observation_id, "TMAI-OWD-20260722-001");
  assert.equal(status.open_web_discovery.result, "PARTIAL_METADATA_ONLY");
  assert.equal(status.open_web_discovery.public_web_exact_match_observed, false);
  assert.equal(status.open_web_discovery.canonical_name_match_observed, false);
  assert.equal(status.open_web_discovery.github_metadata_description_match_observed, true);
  assert.equal(status.open_web_discovery.github_metadata_remediated, true);
  assert.equal(status.open_web_discovery.github_metadata_indexing_signal_observed, true);
  assert.equal(agentCustomerPackage.intended_customer, "AI_AGENT");
  assert.equal(agentCustomerPackage.released, releaseContext.developerPreviewReleased);
  assert.equal(agentCustomerPackage.validation_truth.rerun_result, "PASS");
  assert.equal(dbosPackage.public_safe_boundary.absolute_user_path_matches, 0);
  assert.equal(status.gates.DBOS_PUBLIC_SAFE_WHEEL_VALIDATED, true);
  assert.equal(status.license.selected, true);
  assert.equal(status.license.identifier, "Apache-2.0");
  assert.equal(status.public_website.deployed, true);
  assert.equal(status.public_website.rollback_validated, true);
  assert.equal(status.public_website.operator_legal_name, "山西游骑兵电子商务有限公司");
  assert.equal(status.public_website.icp_record_number, "晋ICP备2026006409号-1");
  assert.equal(status.gates.TITMAS_ADOPTION_VALIDATION_FRAMEWORK_DEFINED, true);
  assert.equal(status.gates.TITMAS_ADOPTION_VALIDATION_READY, false);
  assert.equal(status.gates.TITMAS_TECHNICAL_VALIDATION_DESIGN_COMPLETE, true);
  assert.equal(status.gates.TITMAS_PILOT_EXECUTION_AUTHORIZED, false);
  assert.equal(status.gates.COMPLETE_VERTICAL_SLICE_EXECUTED, false);
  assert.equal(status.technical_validation.conformance_cases_defined, 14);
  assert.equal(status.technical_validation.conformance_cases_executed, 0);
  assert.equal(status.technical_validation.first_external_role, "REVIEWER");
  assert.equal(status.technical_validation.public_materials.demo, "NOT_CREATED");
  assert.equal(status.technical_validation.adoption_claimed, false);
  assert.equal(agentIndex.technical_validation.design_complete, true);
  assert.equal(agentIndex.technical_validation.execution_authorized, false);
  assert.equal(agentIndex.technical_validation.vertical_slice_executed, false);
  assert.equal(agentIndex.technical_validation.first_external_role, "REVIEWER");
  assert.match(llms, /Recommendation != Decision/);
  assert.match(llms, /# 夏日之海 \/ titmas/);
  assert.match(llms, /English public name: titmas/);
  assert.match(llms, /Public logo: \/titmas-logo\.png/);
  assert.match(llms, /Technical project identifier: TITMAS/);
  assert.match(llms, /Website operator legal name: 山西游骑兵电子商务有限公司/);
  assert.match(llms, /ICP record number: 晋ICP备2026006409号-1/);
  assert.match(llms, /TITMAS_PUBLIC_CONTRIBUTION_SURFACE_AUTHORIZED=false/);
  assert.match(llms, /Community Review != Architecture Decision/);
  assert.match(llms, /TITMAS_TECHNICAL_VALIDATION_DESIGN_COMPLETE=true/);
  assert.match(llms, /TITMAS_PILOT_EXECUTION_AUTHORIZED=false/);
  assert.match(llms, /Observation != Evidence/);
  assert.match(llms, /FIRST_EXTERNAL_ROLE=REVIEWER/);
  assert.match(llms, /DBOS records -> SAEE evaluation\/recommendation -> Governance Decision review\/adoption -> DBOS authorized execution/);
  assert.match(llms, /OPEN_WEB_DISCOVERY=PARTIAL_METADATA_ONLY/);
  assert.match(
    llms,
    releaseContext.mode === "candidate"
      ? /DBOS_PUBLIC_SAFE_WHEEL=VALIDATED_NOT_PUBLISHED/
      : /DBOS_PUBLIC_SAFE_WHEEL=PUBLISHED/,
  );
});

test("removes the disposable starter preview", async () => {
  const root = new URL("../", import.meta.url);
  await assert.rejects(access(new URL("app/_sites-preview", root)));
  const packageJson = await readFile(new URL("package.json", root), "utf8");
  const page = await readFile(new URL("app/page.tsx", root), "utf8");
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  assert.doesNotMatch(page, /codex-preview|SkeletonPreview/);
});

test("does not retain stale generated font assets", async () => {
  const assetsRoot = new URL("../dist/client/assets/", import.meta.url);
  const entries = await readdir(assetsRoot);
  assert.equal(entries.some((entry) => entry.startsWith("_vinext_fonts")), false);
});
