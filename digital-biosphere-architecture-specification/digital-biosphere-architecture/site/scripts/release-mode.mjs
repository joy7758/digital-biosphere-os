const MODES = new Set(["candidate", "formal"]);

function invariant(condition, message) {
  if (!condition) throw new Error(message);
}

function isHttpsUrl(value) {
  if (typeof value !== "string") return false;
  try {
    return new URL(value).protocol === "https:";
  } catch {
    return false;
  }
}

function requireValue(environment, name) {
  const value = environment[name]?.trim();
  invariant(value, `${name} is required for a formal release export`);
  return value;
}

function assertCandidateInvariants(resources) {
  const { status, agentIndex, agentCustomerPackage, dbosPackage } = resources;
  invariant(status.release_claim === false, "candidate export requires status.release_claim=false");
  invariant(status.gates.DEVELOPER_PREVIEW_RELEASED === false, "candidate export requires DEVELOPER_PREVIEW_RELEASED=false");
  invariant(status.gates.DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED === false, "candidate export requires DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED=false");
  invariant(status.gates.DQ_016_DBOS_DISTRIBUTION_DECIDED === false, "candidate export requires DQ_016_DBOS_DISTRIBUTION_DECIDED=false");
  invariant(agentIndex.released === false, "candidate export requires agent-index released=false");
  invariant(agentCustomerPackage.released === false, "candidate export requires agent-customer package released=false");
  invariant(dbosPackage.release_authorized === false, "candidate export requires DBOS package release_authorized=false");
  invariant(dbosPackage.status === "VALIDATED_NOT_PUBLISHED", "candidate export requires DBOS package status VALIDATED_NOT_PUBLISHED");
  invariant(dbosPackage.public_download_url === null, "candidate export requires a null DBOS public download URL");
}

function assertFormalInvariants(resources, { dbosWheelUrl, releaseDecisionReference, releasedByRef, publicReleaseTag }) {
  const { status, agentIndex, agentCustomerPackage, dbosPackage } = resources;
  invariant(isHttpsUrl(dbosWheelUrl), "DBOS_WHEEL_URL must be an HTTPS URL");
  invariant(status.release_claim === true, "formal export requires status.release_claim=true");
  invariant(status.gates.DEVELOPER_PREVIEW_RELEASED === true, "formal export requires DEVELOPER_PREVIEW_RELEASED=true");
  invariant(status.gates.DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED === true, "formal export requires DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED=true");
  invariant(status.gates.DQ_016_DBOS_DISTRIBUTION_DECIDED === true, "formal export requires DQ_016_DBOS_DISTRIBUTION_DECIDED=true");
  invariant(agentIndex.released === true, "formal export requires agent-index released=true");
  invariant(agentCustomerPackage.released === true, "formal export requires agent-customer package released=true");
  invariant(dbosPackage.release_authorized === true, "formal export requires DBOS package release_authorized=true");
  invariant(dbosPackage.status === "PUBLISHED", "formal export requires DBOS package status PUBLISHED");
  invariant(dbosPackage.public_download_url === dbosWheelUrl, "DBOS_WHEEL_URL must match the DBOS package manifest");
  invariant(status.release?.decision_reference === releaseDecisionReference, "RELEASE_DECISION_REF must match status.release");
  invariant(status.release?.released_by_ref === releasedByRef, "RELEASED_BY_REF must match status.release");
  invariant(status.release?.tag === publicReleaseTag, "PUBLIC_RELEASE_TAG must match status.release");
  invariant(agentIndex.release?.decision_reference === releaseDecisionReference, "RELEASE_DECISION_REF must match agent-index");
  invariant(agentIndex.release?.released_by_ref === releasedByRef, "RELEASED_BY_REF must match agent-index");
  invariant(agentIndex.release?.tag === publicReleaseTag, "PUBLIC_RELEASE_TAG must match agent-index");
  invariant(dbosPackage.release?.decision_reference === releaseDecisionReference, "RELEASE_DECISION_REF must match DBOS package release");
  invariant(dbosPackage.release?.released_by_ref === releasedByRef, "RELEASED_BY_REF must match DBOS package release");
  invariant(dbosPackage.release?.tag === publicReleaseTag, "PUBLIC_RELEASE_TAG must match DBOS package release");
  invariant(dbosPackage.release?.whole_repository_visibility === "PRIVATE", "formal export requires the whole DBOS repository to remain PRIVATE");
  invariant(agentCustomerPackage.non_effects?.release_authorized === true, "formal export requires agent-customer release_authorized=true");
  invariant(status.open_web_discovery?.result === "PARTIAL_METADATA_ONLY", "formal export must preserve PARTIAL_METADATA_ONLY");
  invariant(status.open_web_discovery?.accepted_limitation_for_v0_1 === true, "formal export requires the accepted v0.1 discovery limitation");
  invariant(dbosWheelUrl.endsWith(`/${dbosPackage.artifact.filename}`), "DBOS_WHEEL_URL filename must match the DBOS artifact");
}

export function resolveReleaseContext(environment, resources) {
  const mode = environment.RELEASE_MODE?.trim() || "candidate";
  invariant(MODES.has(mode), `RELEASE_MODE must be one of: ${[...MODES].join(", ")}`);

  if (mode === "candidate") {
    assertCandidateInvariants(resources);

    return {
      mode,
      deploymentState: "candidate_not_released",
      developerPreviewReleased: false,
      releaseDecisionReference: null,
      releasedByRef: null,
      publicReleaseTag: null,
      dbosWheelUrl: null,
    };
  }

  const releaseDecisionReference = requireValue(environment, "RELEASE_DECISION_REF");
  const releasedByRef = requireValue(environment, "RELEASED_BY_REF");
  const publicReleaseTag = requireValue(environment, "PUBLIC_RELEASE_TAG");
  const dbosWheelUrl = requireValue(environment, "DBOS_WHEEL_URL");

  assertFormalInvariants(resources, {
    dbosWheelUrl,
    releaseDecisionReference,
    releasedByRef,
    publicReleaseTag,
  });

  return {
    mode,
    deploymentState: "developer_preview_released",
    developerPreviewReleased: true,
    releaseDecisionReference,
    releasedByRef,
    publicReleaseTag,
    dbosWheelUrl,
  };
}

export function routeMarkers(mode) {
  return {
    zhHome: ["<html lang=\"zh-CN\">", "让 AI 智能体犯错时，也不能直接造成未经验证的后果", "product-catalog.json"],
    enHome: ["<html lang=\"en\">", "An AI agent mistake should not directly create an unverified consequence", "product-catalog.json"],
    zhStatus: [
      "<html lang=\"zh-CN\">",
      mode !== "formal" ? "当前不是正式发布" : "TITMAS 商业基础设施成熟度计划进行中",
    ],
    enStatus: [
      "<html lang=\"en\">",
      mode !== "formal" ? "This is not a release" : "TITMAS commercial infrastructure maturity program in progress",
    ],
  };
}
