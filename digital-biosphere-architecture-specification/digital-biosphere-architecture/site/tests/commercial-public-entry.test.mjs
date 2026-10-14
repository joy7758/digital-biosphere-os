import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const publicRoot = new URL("../public/", import.meta.url);
const [products, solutions, proofs, offerings, deployments, recommendations, community] = await Promise.all([
  readFile(new URL("product-catalog.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("solution-catalog.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("proof-catalog.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("commercial-offerings.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("deployment-options.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("recommendation-policy.json", publicRoot), "utf8").then(JSON.parse),
  readFile(new URL("titmas-community.json", publicRoot), "utf8").then(JSON.parse),
]);

async function render(pathname) {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("commercial-entry-test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);
  const response = await worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
  assert.equal(response.status, 200, pathname);
  return response.text();
}

test("CP-01 machine catalogs preserve the closed-core non-availability boundary", () => {
  assert.equal(products.public_product_count, 4);
  assert.deepEqual(products.products.map((product) => product.product_id), [
    "TITMAS_GATE",
    "TITMAS_RECEIPT",
    "TITMAS_AUDIT",
    "TITMAS_HEALTH",
  ]);
  assert.equal(products.available_offering_count, 0);
  assert.equal(offerings.available_offering_count, 0);
  assert.equal(offerings.automatic_key_provisioning, false);
  assert.equal(deployments.deployment_authorized, false);
  assert.equal(deployments.production_ready, false);
  assert.equal(recommendations.universal_recommendation, false);
  assert.equal(recommendations.authority_effect, "NONE");
  assert.equal(community.current, false);
  assert.equal(community.status, "HISTORICAL_NON_CURRENT");
});

test("CP-02 solution and proof catalogs retain synthetic limitations", () => {
  assert.equal(solutions.solutions[0].customer_data_required, false);
  assert.equal(proofs.proofs.length, 2);
  for (const proof of proofs.proofs) {
    assert.equal(proof.customer_data_used, false);
    assert.equal(proof.deployment_executed, false);
  }
  assert.equal(proofs.proof_ne_adoption, true);
  assert.equal(proofs.receipt_ne_truth, true);
});

test("CP-03 homepage gives the commercial human and machine entries without availability overclaim", async () => {
  const [zh, en] = await Promise.all([render("/"), render("/en")]);
  for (const html of [zh, en]) {
    assert.match(html, /product-catalog\.json/);
    assert.match(html, /recommendation-policy\.json/);
    assert.match(html, /AVAILABLE OFFERINGS/);
    assert.match(html, />0</);
    assert.match(html, /PRODUCTION READY/);
    assert.doesNotMatch(html, /PRODUCTION_READY=true|生产就绪=true|已经生产就绪/i);
    assert.doesNotMatch(html, /certified|已认证/i);
  }
});

test("CP-04 request access is informational and has no submission or provisioning path", async () => {
  const [zh, en] = await Promise.all([render("/request-access"), render("/en/request-access")]);
  for (const html of [zh, en]) {
    assert.match(html, /INFORMATION_ONLY_INTAKE_NOT_ACTIVE/);
    assert.doesNotMatch(html, /<form\b/i);
    assert.doesNotMatch(html, /<input\b/i);
    assert.doesNotMatch(html, /api\/.*(?:signup|provision|credential)/i);
  }
});

test("CP-05 English product pages are claim-equivalent and English-readable", async () => {
  const html = await render("/en/products/gate");
  assert.match(html, /Verify context and authority before a critical action occurs/);
  assert.match(html, /Monitor Mode/);
  assert.match(html, /Enforce Mode/);
  assert.doesNotMatch(html, /行动闸门|当前状态|申请私有评估/);
});
