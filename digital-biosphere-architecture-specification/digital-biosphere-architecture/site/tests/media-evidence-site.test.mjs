import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const siteRoot = new URL("../", import.meta.url);
const publicRoot = new URL("../public/", import.meta.url);

async function render(pathname) {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("media-evidence-test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("commercial carousel contains exactly three complete entries", async () => {
  const source = await readFile(new URL("app/components/hero-carousel.tsx", siteRoot), "utf8");
  assert.match(source, /slideCount: 3/);
  assert.match(source, /让 AI 智能体犯错时，也不能直接造成未经验证的后果/);
  assert.match(source, /先看哪些动作本应被阻断/);
  assert.match(source, /一个私有平台，四个对外产品/);
  assert.doesNotMatch(source, /slideCount: [4-9]/);
});

test("carousel controls preserve 44 by 44 CSS pixel touch targets", async () => {
  const styles = await readFile(new URL("app/globals.css", siteRoot), "utf8");
  assert.match(styles, /\.hero-carousel-controls > button \{[^}]*width: 44px;[^}]*min-width: 44px;[^}]*height: 44px;[^}]*min-height: 44px;/s);
  assert.match(styles, /\.hero-carousel-dots button \{[^}]*height: 44px;[^}]*min-height: 44px;/s);
  assert.match(styles, /@media \(max-width: 620px\) \{[\s\S]*?\.hero-carousel-controls \{[^}]*grid-template-columns: 44px 1fr 44px;/);
  assert.match(styles, /@media \(max-width: 620px\) \{[\s\S]*?\.hero-carousel-dots button \{ min-width: 44px; \}/);
  assert.doesNotMatch(styles, /\.hero-carousel-controls > button \{ width: 40px; height: 40px; \}/);
});

test("server-rendered homepage exposes the complete first slide without scripts", async () => {
  const response = await render("/");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /让 AI 智能体犯错时，也不能直接造成未经验证的后果/);
  assert.match(html, /闭源私有核心连接行动闸门/);
  assert.match(html, /申请私有评估/);
});

test("carousel disables automatic advance for reduced motion and pauses after interaction", async () => {
  const source = await readFile(new URL("app/components/hero-carousel.tsx", siteRoot), "utf8");
  assert.match(source, /AUTO_ADVANCE_MS = 8000/);
  assert.match(source, /matchMedia\("\(prefers-reduced-motion: reduce\)"\)/);
  assert.match(source, /if \(reducedMotion \|\| userPaused \|\| interactionPaused\) return/);
  assert.match(source, /setUserPaused\(true\)/);
  assert.match(source, /onMouseEnter/);
  assert.match(source, /onFocusCapture/);
});

test("media evidence application pages are bilingual and bounded", async () => {
  const [zh, en] = await Promise.all([render("/industry/media-evidence"), render("/en/industry/media-evidence")]);
  assert.equal(zh.status, 200);
  assert.equal(en.status, 200);
  const [zhHtml, enHtml] = await Promise.all([zh.text(), en.text()]);
  assert.match(zhHtml, /面向人工智能生成内容安全的智能审核证据链/);
  assert.match(zhHtml, /TRUTH_VERIFICATION=false/);
  assert.match(enHtml, /Review evidence chains for AI-generated-content safety/);
  assert.match(enHtml, /PRODUCTION_READY=false/);
});

test("media evidence demo pages expose all three synthetic scenarios", async () => {
  const [zh, en] = await Promise.all([render("/demo/media-evidence"), render("/en/demo/media-evidence")]);
  assert.equal(zh.status, 200);
  assert.equal(en.status, 200);
  const [zhHtml, enHtml] = await Promise.all([zh.text(), en.text()]);
  for (const marker of ["正常生命周期", "证据冲突", "篡改检测", "SYNTHETIC_DATA_ONLY"]) assert.match(zhHtml, new RegExp(marker));
  for (const marker of ["Normal lifecycle", "Evidence conflict", "Tamper detection", "SYNTHETIC_DATA_ONLY"]) assert.match(enHtml, new RegExp(marker));
});

test("machine-readable media profile preserves all prohibited claims as false", async () => {
  const profile = JSON.parse(await readFile(new URL("media-evidence-profile.json", publicRoot), "utf8"));
  assert.equal(profile.status, "LOCAL_SYNTHETIC_REFERENCE_IMPLEMENTATION");
  assert.equal(profile.data_policy, "SYNTHETIC_DATA_ONLY");
  for (const key of ["truth_verification", "identity_authentication", "legal_evidence", "production_ready", "external_standard_compatibility_claimed", "customer_adoption_claimed", "security_guaranteed"]) {
    assert.equal(profile[key], false, `${key} must fail closed`);
  }
});

test("application, demo, and machine links remain a closed historical discovery set", async () => {
  const profile = JSON.parse(await readFile(new URL("media-evidence-profile.json", publicRoot), "utf8"));
  const catalog = JSON.parse(await readFile(new URL("site-catalog.json", publicRoot), "utf8"));
  const agentIndex = JSON.parse(await readFile(new URL("agent-index.json", publicRoot), "utf8"));
  assert.equal(catalog.public_surfaces.media_evidence.application_zh, profile.application_url);
  assert.equal(catalog.public_surfaces.media_evidence.demo_zh, profile.demo_url);
  assert.equal(agentIndex.media_evidence.machine_profile, "/media-evidence-profile.json");
  const [application, demo] = await Promise.all([render("/industry/media-evidence"), render("/demo/media-evidence")]);
  assert.equal(application.status, 200);
  assert.equal(demo.status, 200);
});

test("static export contracts include every new bilingual route and public resource", async () => {
  const [exportSource, verifySource] = await Promise.all([
    readFile(new URL("scripts/export-static.mjs", siteRoot), "utf8"),
    readFile(new URL("scripts/verify-static.mjs", siteRoot), "utf8"),
  ]);
  for (const route of ["/industry/media-evidence", "/en/industry/media-evidence", "/demo/media-evidence", "/en/demo/media-evidence"]) {
    assert.match(exportSource, new RegExp(route.replaceAll("/", "\\/")));
  }
  for (const file of ["industry/media-evidence/index.html", "en/industry/media-evidence/index.html", "demo/media-evidence/index.html", "en/demo/media-evidence/index.html", "media-evidence-profile.json"]) {
    assert.match(verifySource, new RegExp(file.replaceAll("/", "\\/")));
  }
  await access(new URL("media-evidence-profile.json", publicRoot));
});
