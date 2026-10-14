import assert from "node:assert/strict";
import test from "node:test";

const restoredRoutes = [
  "/research",
  "/en/research",
  "/platform",
  "/en/platform",
  "/products",
  "/en/products",
  "/solutions",
  "/en/solutions",
  "/proof",
  "/en/proof",
  "/research/index",
  "/en/research/index",
  "/applications",
  "/en/applications",
  "/demos",
  "/en/demos",
  "/community",
  "/en/community",
  "/updates",
  "/en/updates",
  "/updates/information-architecture-v0-1",
  "/en/updates/information-architecture-v0-1",
  "/updates/constitution",
  "/en/updates/constitution",
  "/industries",
  "/en/industries",
  "/industry/media-evidence",
  "/en/industry/media-evidence",
  "/industry/medical-evidence",
  "/en/industry/medical-evidence",
  "/industry/space-agent-evidence",
  "/en/industry/space-agent-evidence",
  "/demo/medical-evidence",
  "/en/demo/medical-evidence",
  "/demo/media-evidence",
  "/en/demo/media-evidence",
  "/medical-evidence",
  "/en/medical-evidence",
  "/digital-cell",
  "/en/digital-cell",
  "/commercial-evaluation",
  "/en/commercial-evaluation",
  "/products/gate",
  "/en/products/gate",
  "/products/receipt",
  "/en/products/receipt",
  "/products/audit",
  "/en/products/audit",
  "/products/health",
  "/en/products/health",
  "/design-partner",
  "/en/design-partner",
  "/private-evaluation",
  "/en/private-evaluation",
  "/monitor-pilot",
  "/en/monitor-pilot",
  "/enforce-pilot",
  "/en/enforce-pilot",
  "/request-access",
  "/en/request-access",
  "/security",
  "/en/security",
  "/trust-center",
  "/en/trust-center",
  "/privacy",
  "/en/privacy",
  "/terms",
  "/en/terms",
];

async function render(pathname) {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("additive-surface-test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("keeps all established bilingual surfaces reachable", async () => {
  for (const route of restoredRoutes) {
    const response = await render(route);
    assert.equal(response.status, 200, `expected ${route} to remain reachable`);
    assert.match(response.headers.get("content-type") ?? "", /text\/html/);
  }
});

test("keeps historical status surfaces while promoting the commercial mainline", async () => {
  const [homeResponse, statusResponse, communityResponse] = await Promise.all([render("/"), render("/status"), render("/community")]);
  const [home, status, community] = await Promise.all([homeResponse.text(), statusResponse.text(), communityResponse.text()]);

  assert.match(home, /人类与智能体双入口/);
  assert.match(home, /夏日之海/);
  assert.match(home, /\/titmas-logo\.png/);
  assert.doesNotMatch(home, /\/summersea-logo\.png/);
  assert.match(home, /让 AI 智能体犯错时，也不能直接造成未经验证的后果/);
  assert.match(home, /AVAILABLE OFFERINGS/);
  assert.match(status, /TITMAS 商业基础设施成熟度计划进行中/);
  assert.match(status, /Stage 5\.7 结果/);
  assert.match(status, /EXPIRED_ACCESS_REVOKED_NO_CONTRIBUTION_OBSERVED/);
  assert.match(community, /HISTORICAL_NON_CURRENT/);
  assert.match(community, /社区从未建立/);
});

test("does not restore private-core or deprecated product routes", async () => {
  for (const route of ["/products/agent-immune", "/en/products/agent-immune"]) {
    const response = await render(route);
    assert.equal(response.status, 404);
  }
});

test("adds bounded commercial collection routes without promoting availability", async () => {
  const expected = new Map([
    ["/platform", "TITMAS_PLATFORM_COLLECTION"],
    ["/products", "TITMAS_PRODUCTS_COLLECTION"],
    ["/solutions", "TITMAS_SOLUTIONS_COLLECTION"],
    ["/proof", "TITMAS_PROOF_COLLECTION"],
  ]);
  for (const [route, marker] of expected) {
    for (const path of [route, `/en${route}`]) {
      const response = await render(path);
      assert.equal(response.status, 200);
      const html = await response.text();
      assert.match(html, new RegExp(marker));
      assert.match(html, /AVAILABLE_OFFERINGS=0/);
      assert.match(html, /PRODUCTION_READY=false/);
      assert.match(html, /Verification ≠ Authorization/);
    }
  }
});
