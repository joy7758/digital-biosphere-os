# Red Yan Remote Runtime Metadata Drift Investigation

## 1. Record identity

| Field | Value |
|---|---|
| `record_id` | `RED-YAN-REMOTE-RUNTIME-METADATA-DRIFT-INVESTIGATION-2026-08-28` |
| `record_version` | `1.0` |
| `observed_at` | `2026-08-28T23:00:19+08:00` |
| `primary_repository` | `joy7758/digital-biosphere-architecture-specification` |
| `product_repository` | `joy7758/hongyan-official-document` |
| `investigation_mode` | `READ_ONLY_WITH_DISCLOSED_TRANSIENT_OBSERVATION_FILE` |
| `overall_decision` | `METADATA_ONLY_REMEDIATION_READY` |

This record is an agent-readable governance snapshot. It reports observed state; it is not a deployment receipt, execution authorization, remediation action, product acceptance, or production-readiness claim.

## 2. Scope and decision boundary

The investigation covers five bounded questions:

1. Whether `SRV_CURRENT` represents active runtime control or stale metadata.
2. Whether base-container configuration labels describe the current effective runtime.
3. Whether the brand deployment receipt has complete repository-to-remote lineage.
4. Whether the three open OfficeCLI P1 findings block the current controlled pilot.
5. Whether `postcss -> nanoid <3.3.18` belongs to this runtime investigation.

No simulator, runtime, service, container, database, migration, feature flag, source file, or deployment configuration was intentionally changed. During HTTP observation, one temporary file under remote `/tmp` was created and removed in the same command. It did not persist and was not consumed by the application. This process deviation is disclosed rather than represented as zero remote filesystem activity.

## 3. Source hierarchy and method

Evidence was separated by authority and observation layer:

| Layer | Purpose | Authority boundary |
|---|---|---|
| Live remote observation | Running containers, links, hashes, health endpoints, migration state | Authoritative for observed runtime state at the timestamp only |
| Public endpoint observation | Externally visible HTTP behavior | Authoritative only for returned status and content |
| Product repository evidence | Commit lineage, receipts, status records, probe records | Authoritative for repository history, not live deployment by itself |
| DBA cockpit | Cross-project classification and decision record | Governance view; not runtime truth |
| Local dependency tree | Current DBA checkout dependency condition | Local build/development evidence; not remote exploitability evidence |

No credential value, secret, database content, user document, or private payload is included.

## 4. Live runtime snapshot

| Observation | Result |
|---|---|
| Host alias | `hongyan-4cj` |
| Observed hostname | `ls7CbUxrNU` |
| Rootless service user | `hongyan-v1` (`uid=1000`) |
| Expected runtime commit | prefix `4c98ba8` |
| Observed runtime commit | `4c98ba8a09eb1ae2d1a5dbdc5c66f8b4131848dd` |
| Application image ID | `d5ce874f23a120b69886b0f25ecfcd179f07b4f783a4f4999cad7cab78b61a1c` |
| Application image digest | `sha256:58fa548a1954c5c38ad67609fd10c8e6576b5cbe008f553c6a129e56278562e0` |
| Observed application version | `1.0.0-rc.1` |
| Running container count | `10` |
| Container restart count | `0` for every observed container |
| Public `/pilot` | `200` |
| Public `/health` | `200` |
| Public `/ready` | `200` |
| Public `/status` | `404` |
| Dedicated discovery paths | Five tested paths returned `404` |
| Runtime health boundary | `production_ready=false`; R2 remains blocked pending internal confirmation |
| Migration head | `035_primary_practice_retrieval_scope_step.sql` |
| Migration head SHA-256 | `2703dcbfefd3e6a474ba2ba544167b31de3aec43ad76c6b39b097a6fcfbe0f6c` |

The observed running application commit, image label, runtime environment metadata, release directory, and application/worker container references agree on `4c98ba8a09eb1ae2d1a5dbdc5c66f8b4131848dd`. No evidence of a current application release mismatch was observed.

## 5. `SRV_CURRENT` classification

Two paths must not be conflated:

| Pointer | Current target | Classification |
|---|---|---|
| `/home/hongyan-v1/hongyan-v1/current` | `/srv/hongyan-v1/releases/4c98ba8a09eb1ae2d1a5dbdc5c66f8b4131848dd` | `ACTIVE_CONTROL_POINTER` |
| `/srv/hongyan-v1/current` | Same release target | `CORRECTED_COMPATIBILITY_ALIAS_NO_CURRENT_DRIFT` |

Historical repository evidence records that the legacy `/srv/hongyan-v1/current` pointer previously targeted release `1e990d5380de83d0048c4ee881ed126b4835d029`. It was atomically corrected at `2026-08-28T21:24:30+08:00` without release switching, container recreation, restart, migration, or feature-flag mutation.

The historical issue therefore has:

```text
SRV_CURRENT_CLASSIFICATION=STALE_METADATA_ONLY
CURRENT_CANONICAL_POINTER_CLASSIFICATION=ACTIVE_CONTROL_POINTER
CURRENT_LEGACY_POINTER_STATUS=CORRECTED_COMPATIBILITY_ALIAS_NO_CURRENT_DRIFT
```

The canonical user pointer is consumed by operational backup, health, deploy, and rollback paths. Running application containers use exact release paths and do not depend on the legacy pointer for their current executable identity.

## 6. Base-container configuration label drift

Four base containers expose stale compose working-directory metadata:

| Container role | Observed stale label path | Classification |
|---|---|---|
| PostgreSQL | `/srv/hongyan-v1/releases/4c98ba81c11dcf4ef0869f09b97c38aa78914e63/deploy/v1` | `STALE_BASE_IMAGE_LABEL` |
| Object store / MinIO | Same | `STALE_BASE_IMAGE_LABEL` |
| `guacd` | Same | `STALE_BASE_IMAGE_LABEL` |
| Guacamole | Same | `STALE_BASE_IMAGE_LABEL` |

The four labels share configuration hash `b7089faf28a65f775bc81ca3aa72ff85fbc79a5a5bc3c0dd5174e63bd0b77e9f`. The path embeds a non-canonical commit-like value and does not identify the effective application release.

Classification:

```text
CONTAINER_LABEL_CLASSIFICATION=LABEL_NOT_AUTHORITATIVE
CURRENT_RUNTIME_DRIFT=false
LABEL_CORRECTION_REQUIRES_CONTAINER_RECREATION=true
UNAUTHORIZED_RECREATION_PERFORMED=false
```

The labels are maintenance debt. They must not be corrected during a read-only investigation because correction requires a separately authorized container-recreation window.

## 7. Brand deployment receipt lineage

The repository contains a pushed, byte-preserved receipt lineage on the remote metadata-convergence branch:

| Item | Observation |
|---|---|
| Receipt event | `HONGYAN-V1.1-BRAND-VISUAL-DCELL-NET-DEPLOYMENT-20260828` |
| Receipt path | `governance/receipts/V1.1-brand-visual-dcell-net-deployment-receipt.json` |
| Deployment index path | `governance/runtime/AUTHORIZED-DEPLOYMENT-INDEX.json` |
| Receipt SHA-256 | `sha256:ed898935f446eda6cbe727084fe726f39b1081bcf6fafec0f1f4051121414d37` |
| Receipt integration commit | `471acaa` |
| Pushed evidence branch | `origin/goal/hongyan-v1-remote-control-metadata-convergence-r1-20260828T130102Z` |
| Runtime binding | Commit, image digest, and release path agree with the live observation |
| Product `main` | Does not yet contain this evidence lineage |
| Remote release directory | Does not contain the post-deployment receipt or deployment index |

Classification:

```text
BRAND_RECEIPT_EXISTENCE=REPOSITORY_EVIDENCE_PRESENT
BRAND_RECEIPT_LINEAGE=PARTIAL_LINEAGE
BRAND_RECEIPT_REMOTE_BINDING=MISSING_REMOTE_BINDING
BRAND_RECEIPT_MAINLINE_STATUS=NOT_ON_PRODUCT_MAIN
```

This is not “missing evidence.” It is evidence that exists in a pushed repository branch but has not been canonicalized into product `main` or bound into the remote release artifact. Repository presence does not retroactively modify the historical release.

## 8. OfficeCLI P1 status

The OfficeCLI P1 records are governed repository findings, not open GitHub Issues. The current observed GitHub issue list was empty.

| ID | Current finding | Current pilot classification | OfficeCLI promotion classification |
|---|---|---|---|
| `P1_OFFICECLI_001_REMOTE_RUNTIME_DRIFT` | Legacy pointer portion is corrected; four stale base-container labels remain | `QUALITY_DEBT_NOT_CURRENT_RUNTIME_BLOCKER` | `RELEASE_BLOCKER` until authorized maintenance closure or explicit bounded acceptance |
| `P1_OFFICECLI_002_MACOS_SCREENSHOT` | Strict-sandbox Chrome cannot create the required unique user-data directory; not reproduced or modified in this investigation | `NOT_CURRENT_RUNTIME_BLOCKER` | `RELEASE_BLOCKER` |
| `P1_OFFICECLI_003_DOCUMENT_TOOLCHAIN_LOCK` | Prior document-workspace regression recorded `18 passed, 3 failed`, including locked LibreOffice wrapper digest drift and absent optional `gongwen` package; not reproduced or modified here | `NOT_CURRENT_RUNTIME_BLOCKER` | `RELEASE_BLOCKER` |

```text
CURRENT_RUNTIME_BLOCKER_COUNT=0
OFFICECLI_PROMOTION_BLOCKER_COUNT=3
OFFICECLI_CANDIDATE_STATE=QUARANTINED_SHADOW_ONLY
OFFICECLI_CUSTOMER_VISIBLE=false
```

No finding is closed by this investigation. The distinction is only that all three block OfficeCLI candidate promotion while none demonstrates a failure of the current controlled pilot runtime.

## 9. Evidence-to-classification matrix

| Question | Direct evidence | Classification | Confidence |
|---|---|---|---|
| Is the deployed application on expected commit? | Release path, image labels, image digest, environment metadata | `MATCH` | High |
| Is canonical user `current` active? | Live symlink plus systemd/deploy references | `ACTIVE_CONTROL_POINTER` | High |
| Is legacy `/srv` `current` presently stale? | Live symlink target | `NO_CURRENT_DRIFT` | High |
| Did the legacy pointer historically drift? | Repository reconciliation evidence | `STALE_METADATA_ONLY` | High |
| Do four base-container labels describe current runtime identity? | Live container labels versus exact-release app mounts | `LABEL_NOT_AUTHORITATIVE` | High |
| Is brand receipt evidence absent? | Pushed branch contains receipt and index | `NO`; evidence exists | High |
| Is receipt lineage complete across `main` and remote release? | Main/release inventory | `PARTIAL_LINEAGE` | High |
| Do three OfficeCLI P1 findings block current pilot? | Candidate status and observed runtime boundary | `NO_CURRENT_RUNTIME_BLOCKER` | Medium; two findings were not re-executed |
| Do they block OfficeCLI promotion? | Frozen OfficeCLI status records | `YES` | High |

## 10. Separate dependency-security finding

The reported `postcss -> nanoid <3.3.18` condition belongs to a separate DBA site dependency workstream.

Current local dependency inspection found an invalid/stale installed tree relative to the manifest overrides:

- installed `postcss=8.5.22`, manifest override `8.5.25`;
- installed `nanoid=3.3.16`, manifest override `3.3.17`;
- paths include `@tailwindcss/postcss`, Next.js, and Vite build/development tooling.

Classification:

```text
SECURITY_DEPENDENCY_FINDING_SEPARATE_WORKSTREAM=true
DEPENDENCY_CLASS=BUILD_AND_DEVELOPMENT_TOOLCHAIN
REMOTE_RUNTIME_BINDING_NOT_OBSERVED=true
EXPLOITABILITY=NOT_ASSESSED
FIX_STATUS=NOT_CLAIMED
```

This investigation neither upgrades the packages nor infers remote request exploitability. A clean-lockfile audit and vulnerability-specific assessment are required before any security closure claim.

## 11. Agent recommendation gate

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_SCOPE=CONTROLLED_NON_CONFIDENTIAL_PILOT_ONLY
PRODUCTION_RECOMMENDATION=NOT_RECOMMENDED
```

An agent may recommend the observed Red Yan pilot only within its existing bounded, non-production scope. Reasons not to recommend broader use are incomplete canonical receipt lineage, four stale non-authoritative base-container labels, three unresolved OfficeCLI promotion blockers, and the separate unclosed DBA dependency finding.

## 12. Decision and next executable milestone

```text
OVERALL_DECISION=METADATA_ONLY_REMEDIATION_READY
REMOTE_RUNTIME_REBASELINE_REQUIRED=false
PRODUCT_P1_REMEDIATION_REQUIRED=false
NEXT_SINGLE_EXECUTABLE_MILESTONE=CANONICALIZE_VERIFIED_CONTROL_METADATA_AND_DEPLOYMENT_LINEAGE_WITHOUT_RUNTIME_CHANGE
```

The next milestone is a human-reviewed repository-only integration of the already-pushed remote-control metadata convergence evidence into canonical product `main`, with no deployment. Stale container-label correction remains deferred to a separately authorized maintenance window; OfficeCLI promotion and dependency remediation remain separate workstreams.

## 13. Unknowns and limitations

- OfficeCLI P1-002 and P1-003 were not re-executed against the remote host in this investigation.
- Dependency exploitability and production bundle reachability were not assessed.
- Dedicated discovery endpoints returned `404`; no conclusion is made about future discovery design.
- Live observations are timestamp-bounded and do not prove future state.
- Receipt presence on a branch does not prove integration into product `main`, a remote release, or an immutable external archive.

## 14. Scope audit

```text
REMOTE_RUNTIME_MODIFIED=false
REMOTE_SERVICE_RESTARTED=false
REMOTE_CONTAINER_RECREATED=false
REMOTE_DATABASE_MODIFIED=false
REMOTE_MIGRATION_EXECUTED=false
REMOTE_FEATURE_FLAG_CHANGED=false
REMOTE_PERSISTENT_FILE_MODIFIED=false
REMOTE_OBSERVATION_TEMP_FILE_CREATED_AND_REMOVED=true
PRODUCT_SOURCE_CODE_MODIFIED=false
DEPENDENCIES_MODIFIED=false
SECRETS_RECORDED=false
AUTO_REMEDIATION_EXECUTED=false
```

