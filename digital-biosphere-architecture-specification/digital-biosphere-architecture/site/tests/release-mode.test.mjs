import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { resolveReleaseContext, routeMarkers } from "../scripts/release-mode.mjs";

async function currentResources() {
  const root = new URL("../public/", import.meta.url);
  const [status, agentIndex, agentCustomerPackage, dbosPackage] = await Promise.all([
    readFile(new URL("status.json", root), "utf8").then(JSON.parse),
    readFile(new URL("agent-index.json", root), "utf8").then(JSON.parse),
    readFile(new URL("agent-customer-package.json", root), "utf8").then(JSON.parse),
    readFile(new URL("dbos-public-package-manifest.json", root), "utf8").then(JSON.parse),
  ]);
  return { status, agentIndex, agentCustomerPackage, dbosPackage };
}

async function candidateResources() {
  const resources = structuredClone(await currentResources());
  resources.status.release_claim = false;
  resources.status.gates.DEVELOPER_PREVIEW_RELEASED = false;
  resources.status.gates.DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED = false;
  resources.status.gates.DQ_016_DBOS_DISTRIBUTION_DECIDED = false;
  resources.agentIndex.released = false;
  resources.agentCustomerPackage.released = false;
  resources.dbosPackage.release_authorized = false;
  resources.dbosPackage.status = "VALIDATED_NOT_PUBLISHED";
  resources.dbosPackage.public_download_url = null;
  return resources;
}

test("keeps the historical candidate mode fail closed", async () => {
  const context = resolveReleaseContext({}, await candidateResources());
  assert.deepEqual(context, {
    mode: "candidate",
    deploymentState: "candidate_not_released",
    developerPreviewReleased: false,
    releaseDecisionReference: null,
    releasedByRef: null,
    publicReleaseTag: null,
    dbosWheelUrl: null,
  });
  assert.match(routeMarkers(context.mode).zhStatus[1], /当前不是正式发布/);
});

test("rejects unknown release modes", async () => {
  const resources = await currentResources();
  assert.throws(
    () => resolveReleaseContext({ RELEASE_MODE: "production" }, resources),
    /RELEASE_MODE must be one of/,
  );
});

test("rejects formal release mode without explicit decision inputs", async () => {
  const resources = await currentResources();
  assert.throws(
    () => resolveReleaseContext({ RELEASE_MODE: "formal" }, resources),
    /RELEASE_DECISION_REF is required/,
  );
});

test("rejects formal release mode while public truth surfaces remain candidates", async () => {
  const resources = await candidateResources();
  assert.throws(
    () =>
      resolveReleaseContext(
        {
          RELEASE_MODE: "formal",
          RELEASE_DECISION_REF: "architecture/ADR-PLACEHOLDER.md",
          RELEASED_BY_REF: "release-owner",
          PUBLIC_RELEASE_TAG: "v0.1-developer-preview",
          DBOS_WHEEL_URL: "https://example.invalid/dbos.whl",
        },
        resources,
      ),
    /formal export requires status\.release_claim=true/,
  );
});

test("accepts formal mode only when every machine truth surface and input agree", async () => {
  const resources = await currentResources();
  const wheelUrl = "https://redcrag.cn/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl";

  const context = resolveReleaseContext(
    {
      RELEASE_MODE: "formal",
      RELEASE_DECISION_REF: "architecture/ADR-022-developer-preview-release.md",
      RELEASED_BY_REF: "zhangbin",
      PUBLIC_RELEASE_TAG: "v0.1-developer-preview",
      DBOS_WHEEL_URL: wheelUrl,
    },
    resources,
  );

  assert.equal(context.deploymentState, "developer_preview_released");
  assert.equal(context.developerPreviewReleased, true);
  assert.equal(context.dbosWheelUrl, wheelUrl);
  assert.equal(context.releasedByRef, "zhangbin");
  assert.match(routeMarkers(context.mode).enStatus[1], /commercial infrastructure maturity program in progress/);
});

test("routeMarkers yields formal release markers when mode is formal", () => {
  const markers = routeMarkers("formal");
  assert.deepEqual(markers, {
    zhHome: ["<html lang=\"zh-CN\">", "让 AI 智能体犯错时，也不能直接造成未经验证的后果", "product-catalog.json"],
    enHome: ["<html lang=\"en\">", "An AI agent mistake should not directly create an unverified consequence", "product-catalog.json"],
    zhStatus: [
      "<html lang=\"zh-CN\">",
      "TITMAS 商业基础设施成熟度计划进行中",
    ],
    enStatus: [
      "<html lang=\"en\">",
      "TITMAS commercial infrastructure maturity program in progress",
    ],
  });
});

test("routeMarkers yields candidate markers for other modes and edge cases", () => {
  const expectedCandidateMarkers = {
    zhHome: ["<html lang=\"zh-CN\">", "让 AI 智能体犯错时，也不能直接造成未经验证的后果", "product-catalog.json"],
    enHome: ["<html lang=\"en\">", "An AI agent mistake should not directly create an unverified consequence", "product-catalog.json"],
    zhStatus: [
      "<html lang=\"zh-CN\">",
      "当前不是正式发布",
    ],
    enStatus: [
      "<html lang=\"en\">",
      "This is not a release",
    ],
  };

  assert.deepEqual(routeMarkers("candidate"), expectedCandidateMarkers);
  assert.deepEqual(routeMarkers(undefined), expectedCandidateMarkers);
  assert.deepEqual(routeMarkers(null), expectedCandidateMarkers);
  assert.deepEqual(routeMarkers("unknown"), expectedCandidateMarkers);
});

test("rejects formal mode when the release identity drifts across truth surfaces", async () => {
  const resources = structuredClone(await currentResources());
  resources.agentIndex.release.released_by_ref = "different-owner";

  assert.throws(
    () => resolveReleaseContext(
      {
        RELEASE_MODE: "formal",
        RELEASE_DECISION_REF: "architecture/ADR-022-developer-preview-release.md",
        RELEASED_BY_REF: "zhangbin",
        PUBLIC_RELEASE_TAG: "v0.1-developer-preview",
        DBOS_WHEEL_URL: "https://redcrag.cn/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl",
      },
      resources,
    ),
    /RELEASED_BY_REF must match agent-index/,
  );
});

test("rejects formal mode when truth surfaces have mismatched release status", async () => {
  const resources = structuredClone(await currentResources());
  resources.status.gates.DEVELOPER_PREVIEW_RELEASED = false;

  assert.throws(
    () => resolveReleaseContext(
      {
        RELEASE_MODE: "formal",
        RELEASE_DECISION_REF: "architecture/ADR-022-developer-preview-release.md",
        RELEASED_BY_REF: "zhangbin",
        PUBLIC_RELEASE_TAG: "v0.1-developer-preview",
        DBOS_WHEEL_URL: "https://redcrag.cn/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl",
      },
      resources,
    ),
    /formal export requires DEVELOPER_PREVIEW_RELEASED=true/,
  );
});
