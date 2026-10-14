import { createHash } from "node:crypto";
import { cp, mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { resolveReleaseContext, routeMarkers } from "./release-mode.mjs";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const outputRoot = join(siteRoot, "out");
const clientRoot = join(siteRoot, "dist", "client");
const serverEntry = join(siteRoot, "dist", "server", "index.js");
const sourceRevision = process.env.SOURCE_REVISION || "working-tree";
const generatedAt = new Date().toISOString();

const [status, agentIndex, agentCustomerPackage, dbosPackage] = await Promise.all([
  readFile(join(siteRoot, "public", "status.json"), "utf8").then(JSON.parse),
  readFile(join(siteRoot, "public", "agent-index.json"), "utf8").then(JSON.parse),
  readFile(join(siteRoot, "public", "agent-customer-package.json"), "utf8").then(JSON.parse),
  readFile(join(siteRoot, "public", "dbos-public-package-manifest.json"), "utf8").then(JSON.parse),
]);
const releaseContext = resolveReleaseContext(process.env, {
  status,
  agentIndex,
  agentCustomerPackage,
  dbosPackage,
});
const markers = routeMarkers(releaseContext.mode);

const routes = [
  { request: "/", output: "index.html", markers: markers.zhHome, lang: "zh-CN" },
  { request: "/en", output: "en/index.html", markers: markers.enHome, lang: "en" },
  { request: "/platform", output: "platform/index.html", markers: ["TITMAS_PLATFORM_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "zh-CN" },
  { request: "/en/platform", output: "en/platform/index.html", markers: ["TITMAS_PLATFORM_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "en" },
  { request: "/products", output: "products/index.html", markers: ["TITMAS_PRODUCTS_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "zh-CN" },
  { request: "/en/products", output: "en/products/index.html", markers: ["TITMAS_PRODUCTS_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "en" },
  { request: "/solutions", output: "solutions/index.html", markers: ["TITMAS_SOLUTIONS_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "zh-CN" },
  { request: "/en/solutions", output: "en/solutions/index.html", markers: ["TITMAS_SOLUTIONS_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "en" },
  { request: "/proof", output: "proof/index.html", markers: ["TITMAS_PROOF_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "zh-CN" },
  { request: "/en/proof", output: "en/proof/index.html", markers: ["TITMAS_PROOF_COLLECTION", "AVAILABLE_OFFERINGS=0"], lang: "en" },
  { request: "/products/gate", output: "products/gate/index.html", markers: ["TITMAS GATE", "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_DEPLOYED"], lang: "zh-CN" },
  { request: "/en/products/gate", output: "en/products/gate/index.html", markers: ["Verify context and authority before a critical action occurs", "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_DEPLOYED"], lang: "en" },
  { request: "/products/receipt", output: "products/receipt/index.html", markers: ["TITMAS RECEIPT", "PRIVATE_REFERENCE_IMPLEMENTED_NOT_AVAILABLE_OFFERING"], lang: "zh-CN" },
  { request: "/en/products/receipt", output: "en/products/receipt/index.html", markers: ["Bind action, provenance, decision, and limits into a portable technical receipt", "PRIVATE_REFERENCE_IMPLEMENTED_NOT_AVAILABLE_OFFERING"], lang: "en" },
  { request: "/products/audit", output: "products/audit/index.html", markers: ["TITMAS AUDIT", "PRIVATE_REFERENCE_IMPLEMENTED_NOT_DEPLOYED"], lang: "zh-CN" },
  { request: "/en/products/audit", output: "en/products/audit/index.html", markers: ["Review principals, authority, decisions, receipts, and outcomes on one timeline", "PRIVATE_REFERENCE_IMPLEMENTED_NOT_DEPLOYED"], lang: "en" },
  { request: "/products/health", output: "products/health/index.html", markers: ["TITMAS HEALTH", "EVALUATION_PROFILE_NOT_AVAILABLE_OFFERING"], lang: "zh-CN" },
  { request: "/en/products/health", output: "en/products/health/index.html", markers: ["Identify identity, boundary, evidence, gate, and audit gaps first", "EVALUATION_PROFILE_NOT_AVAILABLE_OFFERING"], lang: "en" },
  { request: "/design-partner", output: "design-partner/index.html", markers: ["DESIGN PARTNER", "PROGRAM_DEFINED_OUTREACH_NOT_AUTHORIZED"], lang: "zh-CN" },
  { request: "/en/design-partner", output: "en/design-partner/index.html", markers: ["Validate a Monitor-first product path with one real workflow", "PROGRAM_DEFINED_OUTREACH_NOT_AUTHORIZED"], lang: "en" },
  { request: "/private-evaluation", output: "private-evaluation/index.html", markers: ["PRIVATE EVALUATION", "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_PUBLICLY_AVAILABLE"], lang: "zh-CN" },
  { request: "/en/private-evaluation", output: "en/private-evaluation/index.html", markers: ["Validate first value with zero customer data and synthetic scenarios", "SYNTHETIC_REFERENCE_IMPLEMENTED_NOT_PUBLICLY_AVAILABLE"], lang: "en" },
  { request: "/monitor-pilot", output: "monitor-pilot/index.html", markers: ["MONITOR PILOT", "SYNTHETIC_REFERENCE_PROOF_ONLY_NOT_AVAILABLE_OFFERING"], lang: "zh-CN" },
  { request: "/en/monitor-pilot", output: "en/monitor-pilot/index.html", markers: ["Observe actions that would be blocked or require approval without affecting the real system", "SYNTHETIC_REFERENCE_PROOF_ONLY_NOT_AVAILABLE_OFFERING"], lang: "en" },
  { request: "/enforce-pilot", output: "enforce-pilot/index.html", markers: ["ENFORCE PILOT", "SYNTHETIC_REFERENCE_ONLY_CUSTOMER_AUTHORIZATION_COUNT_0"], lang: "zh-CN" },
  { request: "/en/enforce-pilot", output: "en/enforce-pilot/index.html", markers: ["Evaluate real blocking only after customer-specific authorization", "SYNTHETIC_REFERENCE_ONLY_CUSTOMER_AUTHORIZATION_COUNT_0"], lang: "en" },
  { request: "/request-access", output: "request-access/index.html", markers: ["REQUEST ACCESS", "INFORMATION_ONLY_INTAKE_NOT_ACTIVE"], lang: "zh-CN" },
  { request: "/en/request-access", output: "en/request-access/index.html", markers: ["Every commercial access path is reviewed by a human and bounded by scope", "INFORMATION_ONLY_INTAKE_NOT_ACTIVE"], lang: "en" },
  { request: "/security", output: "security/index.html", markers: ["SECURITY", "SECURITY_REVIEW_REQUIRED_BEFORE_COMMERCIAL_AVAILABILITY"], lang: "zh-CN" },
  { request: "/en/security", output: "en/security/index.html", markers: ["Closed core, minimum metadata, and fail-closed behavior are the defaults", "SECURITY_REVIEW_REQUIRED_BEFORE_COMMERCIAL_AVAILABILITY"], lang: "en" },
  { request: "/trust-center", output: "trust-center/index.html", markers: ["TRUST CENTER", "PUBLIC_TRUST_INFORMATION_NOT_CERTIFICATION"], lang: "zh-CN" },
  { request: "/en/trust-center", output: "en/trust-center/index.html", markers: ["Keep evidence, verification, authorization, and execution as separate facts", "PUBLIC_TRUST_INFORMATION_NOT_CERTIFICATION"], lang: "en" },
  { request: "/privacy", output: "privacy/index.html", markers: ["PRIVACY", "HUMAN_LEGAL_REVIEW_REQUIRED"], lang: "zh-CN" },
  { request: "/en/privacy", output: "en/privacy/index.html", markers: ["No raw customer content by default and no customer data sent to foreign models", "HUMAN_LEGAL_REVIEW_REQUIRED"], lang: "en" },
  { request: "/terms", output: "terms/index.html", markers: ["TERMS", "DRAFT_INFORMATION_NOT_CONTRACT"], lang: "zh-CN" },
  { request: "/en/terms", output: "en/terms/index.html", markers: ["This public surface is not a quote, contract, SLA, or service commitment", "DRAFT_INFORMATION_NOT_CONTRACT"], lang: "en" },
  { request: "/research", output: "research/index.html", markers: ["从研究框架到可验证基础设施", "Evidence Governance", "Evidence ≠ Truth"], lang: "zh-CN" },
  { request: "/en/research", output: "en/research/index.html", markers: ["From research frames to verifiable infrastructure", "Evidence Governance", "Evidence ≠ Truth"], lang: "en" },
  { request: "/research/index", output: "research/index/index.html", markers: ["研究索引", "PUBLISHED_ARCHITECTURE_BASELINE", "DEVELOPER_PREVIEW_RELEASED"], lang: "zh-CN" },
  { request: "/en/research/index", output: "en/research/index/index.html", markers: ["Research index", "PUBLISHED_ARCHITECTURE_BASELINE", "DEVELOPER_PREVIEW_RELEASED"], lang: "en" },
  { request: "/applications", output: "applications/index.html", markers: ["可信基础设施如何进入行业", "自主航天智能体可信执行", "PUBLISHED_RESEARCH_PROFILE"], lang: "zh-CN" },
  { request: "/en/applications", output: "en/applications/index.html", markers: ["How trust infrastructure enters industries", "Space Agent Evidence Profile", "PUBLISHED_RESEARCH_PROFILE"], lang: "en" },
  { request: "/demos", output: "demos/index.html", markers: ["用可检查的演示理解基础设施", "REFERENCE_COMPLETE", "CLINICAL_VALIDATION=false"], lang: "zh-CN" },
  { request: "/en/demos", output: "en/demos/index.html", markers: ["Understand the infrastructure through inspectable demos", "REFERENCE_COMPLETE", "CLINICAL_VALIDATION=false"], lang: "en" },
  { request: "/updates", output: "updates/index.html", markers: ["每次变化，都要说明发生了什么", "RELEASE_NOTE", "网站更新宪法"], lang: "zh-CN" },
  { request: "/en/updates", output: "en/updates/index.html", markers: ["Every change should explain what changed", "RELEASE_NOTE", "Website Update Constitution"], lang: "en" },
  { request: "/updates/information-architecture-v0-1", output: "updates/information-architecture-v0-1/index.html", markers: ["网站结构已更新", "AVAILABLE_PRODUCTS=0", "6a30da9c3e4ea52885ba911da50320a06191fd6f"], lang: "zh-CN" },
  { request: "/en/updates/information-architecture-v0-1", output: "en/updates/information-architecture-v0-1/index.html", markers: ["Site structure updated", "AVAILABLE_PRODUCTS=0", "6a30da9c3e4ea52885ba911da50320a06191fd6f"], lang: "en" },
  { request: "/updates/constitution", output: "updates/constitution/index.html", markers: ["TITMAS 网站更新宪法", "REFERENCE_NE_ADOPTION", "OpenTelemetry"], lang: "zh-CN" },
  { request: "/en/updates/constitution", output: "en/updates/constitution/index.html", markers: ["TITMAS Website Update Constitution", "REFERENCE_NE_ENDORSEMENT", "OpenTelemetry"], lang: "en" },
  { request: "/community", output: "community/index.html", markers: ["历史开发者社区设计资料", "HISTORICAL_NON_CURRENT"], lang: "zh-CN" },
  { request: "/en/community", output: "en/community/index.html", markers: ["Historical developer-community design material", "HISTORICAL_NON_CURRENT"], lang: "en" },
  { request: "/industries", output: "industries/index.html", markers: ["智能制造智能体生态", "TITMAS 不提供", "自主航天 SAEP"], lang: "zh-CN" },
  { request: "/en/industries", output: "en/industries/index.html", markers: ["Manufacturing AI Agent Ecosystem", "TITMAS does not provide", "Space Agent Evidence Profile"], lang: "en" },
  { request: "/industry/media-evidence", output: "industry/media-evidence/index.html", markers: ["面向人工智能生成内容安全的智能审核证据链", "LOCAL_SYNTHETIC_REFERENCE_IMPLEMENTATION", "TRUTH_VERIFICATION=false"], lang: "zh-CN" },
  { request: "/en/industry/media-evidence", output: "en/industry/media-evidence/index.html", markers: ["Review evidence chains for AI-generated-content safety", "LOCAL_SYNTHETIC_REFERENCE_IMPLEMENTATION", "PRODUCTION_READY=false"], lang: "en" },
  { request: "/industry/medical-evidence", output: "industry/medical-evidence/index.html", markers: ["医疗证据基础设施", "INDEPENDENT_MEDICAL_PLATFORM=false", "Medical Agent Evidence"], lang: "zh-CN" },
  { request: "/en/industry/medical-evidence", output: "en/industry/medical-evidence/index.html", markers: ["Medical Evidence Infrastructure", "INDEPENDENT_MEDICAL_PLATFORM=false", "Medical Agent Evidence"], lang: "en" },
  { request: "/industry/space-agent-evidence", output: "industry/space-agent-evidence/index.html", markers: ["自主航天智能体可信执行", "SAEP_STATUS=RESEARCH_PROTOTYPE", "FLIGHT_CERTIFICATION_CLAIM=false"], lang: "zh-CN" },
  { request: "/en/industry/space-agent-evidence", output: "en/industry/space-agent-evidence/index.html", markers: ["Space Agent Evidence Profile", "SAEP_STATUS=RESEARCH_PROTOTYPE", "FLIGHT_CERTIFICATION_CLAIM=false"], lang: "en" },
  { request: "/demo/medical-evidence", output: "demo/medical-evidence/index.html", markers: ["UDI-DICOM Evidence Validator Demo", "SYNTHETIC_DATA_ONLY", "REAL_REGISTRY_LOOKUP=false"], lang: "zh-CN" },
  { request: "/en/demo/medical-evidence", output: "en/demo/medical-evidence/index.html", markers: ["UDI-DICOM Evidence Validator Demo", "SYNTHETIC_DATA_ONLY", "REAL_REGISTRY_LOOKUP=false"], lang: "en" },
  { request: "/demo/media-evidence", output: "demo/media-evidence/index.html", markers: ["媒体证据治理生命周期演示", "SYNTHETIC_DATA_ONLY", "本地校验通过（PASS）"], lang: "zh-CN" },
  { request: "/en/demo/media-evidence", output: "en/demo/media-evidence/index.html", markers: ["Media evidence governance lifecycle demo", "SYNTHETIC_DATA_ONLY", "Local check passed (PASS)"], lang: "en" },
  { request: "/medical-evidence", output: "medical-evidence/index.html", markers: ["UDI-DICOM Evidence Validator Demo", "SYNTHETIC_DATA_ONLY", "REAL_REGISTRY_LOOKUP=false"], lang: "zh-CN" },
  { request: "/en/medical-evidence", output: "en/medical-evidence/index.html", markers: ["UDI-DICOM Evidence Validator Demo", "SYNTHETIC_DATA_ONLY", "REAL_REGISTRY_LOOKUP=false"], lang: "en" },
  { request: "/digital-cell", output: "digital-cell/index.html", markers: ["TITMAS Digital Cell Demo", "REFERENCE_COMPLETE", "NO DIGITAL LIFE CLAIM"], lang: "zh-CN" },
  { request: "/en/digital-cell", output: "en/digital-cell/index.html", markers: ["Make agent execution", "REFERENCE_COMPLETE", "NO DIGITAL LIFE CLAIM"], lang: "en" },
  { request: "/commercial-evaluation", output: "commercial-evaluation/index.html", markers: ["商业评估包 v0.2", "AGENT_FIRST_RUN_VALIDATED"], lang: "zh-CN" },
  { request: "/en/commercial-evaluation", output: "en/commercial-evaluation/index.html", markers: ["Commercial Evaluation Pack v0.2", "AGENT_FIRST_RUN_VALIDATED"], lang: "en" },
  { request: "/status", output: "status/index.html", markers: markers.zhStatus, lang: "zh-CN" },
  { request: "/en/status", output: "en/status/index.html", markers: markers.enStatus, lang: "en" },
];

await rm(outputRoot, { recursive: true, force: true });
await mkdir(outputRoot, { recursive: true });
await cp(clientRoot, outputRoot, { recursive: true });

const workerUrl = pathToFileURL(serverEntry);
workerUrl.searchParams.set("export", `${process.pid}-${Date.now()}`);
const { default: worker } = await import(workerUrl.href);

for (const route of routes) {
  const response = await worker.fetch(
    new Request(`https://redcrag.cn${route.request}`, {
      headers: { accept: "text/html" },
    }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );

  if (response.status !== 200) {
    throw new Error(`Cannot export ${route.request}: HTTP ${response.status}`);
  }

  const renderedHtml = await response.text();
  const html = renderedHtml.replace(
    /<html lang="[^"]+">/,
    `<html lang="${route.lang}">`,
  );
  if (!html.includes(`<html lang="${route.lang}">`)) {
    throw new Error(`Cannot export ${route.request}: document language was not set to ${route.lang}`);
  }
  for (const marker of route.markers) {
    if (!html.includes(marker)) {
      throw new Error(`Cannot export ${route.request}: expected marker is absent: ${marker}`);
    }
  }

  const target = join(outputRoot, route.output);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, html, "utf8");
}

await writeFile(
  join(outputRoot, "release.json"),
  `${JSON.stringify(
    {
      schema_version: "0.1",
      artifact: "trusted-multi-agent-infrastructure-website",
      source_revision: sourceRevision,
      generated_at: generatedAt,
      release_mode: releaseContext.mode,
      deployment_state: releaseContext.deploymentState,
      developer_preview_released: releaseContext.developerPreviewReleased,
      release_decision_reference: releaseContext.releaseDecisionReference,
      released_by_ref: releaseContext.releasedByRef,
      public_release_tag: releaseContext.publicReleaseTag,
      dbos_public_package_url: releaseContext.dbosWheelUrl,
      routes: routes.map((route) => route.request),
    },
    null,
    2,
  )}\n`,
  "utf8",
);

async function listFiles(root, current = root) {
  const entries = await readdir(current, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const absolute = join(current, entry.name);
    if (entry.isDirectory()) files.push(...(await listFiles(root, absolute)));
    else if (entry.isFile() && entry.name !== "release-manifest.json") files.push(absolute);
  }
  return files;
}

const manifestFiles = [];
for (const absolute of (await listFiles(outputRoot)).sort()) {
  const bytes = await readFile(absolute);
  const metadata = await stat(absolute);
  manifestFiles.push({
    path: relative(outputRoot, absolute),
    bytes: metadata.size,
    sha256: createHash("sha256").update(bytes).digest("hex"),
  });
}

await writeFile(
  join(outputRoot, "release-manifest.json"),
  `${JSON.stringify(
    {
      schema_version: "0.1",
      source_revision: sourceRevision,
      generated_at: generatedAt,
      files: manifestFiles,
    },
    null,
    2,
  )}\n`,
  "utf8",
);

console.log(`Static export created: ${outputRoot}`);
console.log(`Source revision: ${sourceRevision}`);
console.log(`Files: ${manifestFiles.length + 1}`);
