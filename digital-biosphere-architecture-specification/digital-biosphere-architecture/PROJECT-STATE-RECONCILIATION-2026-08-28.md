# Project State Reconciliation — 2026-08-28

```text
PROJECT_STATE_RECONCILIATION=PASS_WITH_RECORDED_DEPENDENCY_AUDIT_FAILURE
PRIMARY_ACTIVE_PROJECT=红岩公文
PRIMARY_ENGINEERING_DIRECTION=红岩公文
CURRENT_CANONICAL_DOMAIN=https://dcell.net
REDCRAG_CN_ROLE=LEGACY_HISTORICAL_DOMAIN
DIGITAL_CELL_DEMO_STATUS=RELEASED_FROZEN_REFERENCE_ASSET
DIGITAL_CELL_DEMO_MAINTENANCE_ONLY=true
TITMAS_ROLE=SUPPORTING_TRUST_AND_EVIDENCE_INFRASTRUCTURE
DCELL_ROLE=SUPPORTING_ARCHITECTURE_AND_LONG_TERM_RESEARCH_LAYER
DEB_STATUS=PAUSED
THEORY_EXPANSION_STATUS=PAUSED
INFRASTRUCTURE_SUPPORTS_PRODUCT=true
PRODUCT_EXISTS_TO_PROVE_THEORY=false
CONVERSATION_SCOPE=DBA_COCKPIT_ONLY
DBA_ROLE=PROGRAM_GOVERNANCE_COCKPIT
RED_YAN_PRODUCT_EXECUTION_OWNER=SEPARATE_RED_YAN_CONVERSATION
DBA_MAY_OBSERVE_RED_YAN=true
DBA_MAY_EXECUTE_RED_YAN=false
DBA_MAY_RECORD_HANDOFF=true
DBA_MAY_CHANGE_RED_YAN_RUNTIME=false
```

## Reconciled state

红岩公文是当前真实产品和工程主线。`dcell.net` 是当前公开权威域名。DCell 提供持续
主体架构，TITMAS 与 Evidence 提供边界、执行证据、审查和可验证历史；基础设施支持
产品，产品不是为了证明理论而存在。

Digital Cell Demo `v0.1.0` 已发布、已冻结，只允许不改变冻结语义的维护。DEB、Digital
Survival、Digital Immune、Multi-Cell 和新 TITMAS Runtime 工作默认暂停。

## Repository discovery and actual changes

| Scope | Observed source state | Changes in this reconciliation |
|---|---|---|
| Digital Cell Demo | `joy7758/titmas-demo`, public, `origin/main@2bc410b5ea88dea6a0d7deb8f15d8dde67280f26` | Current README/checklist contradiction correction; one current-state index; existing Release body and repository homepage metadata corrected; PR #5 merged |
| DBA cockpit | `joy7758/digital-biosphere-architecture-specification`, private; historical reconciliation baseline `origin/main@40a4b34370578e665767d9ba9a85dca205876b0f`; post-investigation baseline `origin/main@6eaab6d4e4d0608d31f2a49fc1709066043784c2` | PR #148 historical state preserved; PR #150 merged the bounded runtime-metadata investigation and machine-readable evidence snapshot; this sync changes only cockpit direction and reconciliation records |
| 红岩公文 | `joy7758/hongyan-official-document`, private; canonical reconciliation branch `875b706edbf687b53df6f39ed73e21e87922aef3` | Read-only; GitHub homepage metadata set to `https://dcell.net`; no source, runtime, deployment, feature, or status-record change |
| Current public site | `https://dcell.net` redirects to `/pilot`; source/runtime ownership remains with 红岩公文 | No visual, branding, architecture, deployment, or redirect change |

Unrelated dirty work was preserved. The primary DBA checkout was dirty, and the primary 红岩公文
workspace contained three unrelated untracked UI artifacts; both were isolated from these changes.

## Validation

```text
DIGITAL_CELL_TEST_COUNT=7
DIGITAL_CELL_TEST_RESULT=PASS
DIGITAL_CELL_DEMO_RUN=PASS
DIGITAL_CELL_DETERMINISTIC_REPLAY=PASS
DIGITAL_CELL_FROZEN_SOURCE_CONSISTENCY=PASS
DIGITAL_CELL_FROZEN_OUTPUT_CONSISTENCY=PASS
DBA_CONFORMANCE=PASS
DBA_UNIT_TESTS=147/147_PASS
DBA_CI_CONFORMANCE=PASS
DBA_CI_DEPENDENCY_AUDIT=FAIL_2_HIGH_NANOID_VIA_POSTCSS
DEPENDENCY_SECURITY_WORKSTREAM=SEPARATE_NOT_AUTHORIZED_IN_THIS_TASK
DBA_PR_148_MERGED=true
DBA_PR_148_MERGED_BY=joy7758
DBA_MERGE_COMMIT=9a00bde4928180fbb4de813b1970b243dffb2b07
DBA_PR_150_MERGED=true
DBA_PR_150_MERGE_COMMIT=6eaab6d4e4d0608d31f2a49fc1709066043784c2
RED_YAN_STATUS_ARTIFACTS_PARSE=PASS
RED_YAN_GIT_FSCK=PASS_NO_CORRUPTION
DCELL_NET_ROOT_GET=200_AT_HTTPS://DCELL.NET/PILOT
GITHUB_RELEASE_V0_1_0=INTACT_4_ASSETS
NEW_RELEASE_CREATED=false
NEW_TAG_CREATED=false
```

The first DBA unit-test run retained one `UNAPPROVED_CHANGE_PATH` failure because the old
path-scoped test did not recognize the two new state records or the legacy-site README. The
allowlist was narrowed to those documentation-only paths; no site implementation path was opened,
and the complete rerun passed 147/147.

## RedCrag classification

The count scope is the two changed repositories at their `origin/main` baselines plus current
GitHub repository homepage metadata. Baseline source contained 568 case-insensitive
`redcrag.cn` occurrences: 556 were already historical, while 12 appeared on current surfaces.
Two repository homepage references were also current, for 14 stale current references in total.

The merged Demo correction, two live GitHub metadata corrections, and merged DBA correction close
all 14 stale current references in the audited scope.

```text
CURRENT_REDCRAG_REFERENCES=0
HISTORICAL_REFERENCES_PRESERVED=556
STALE_CURRENT_REFERENCES_FIXED=14
UNRESOLVED_REFERENCES=0
```

The zero count applies only to audited current canonical surfaces. Historical publication,
deployment, source, and audit records remain unchanged and continue to contain RedCrag facts.

## Post-investigation authority boundary

The following authority hierarchy applies to this reconciliation:

1. Red Yan investigation report and machine evidence snapshot govern timestamp-bounded observed
   remote runtime facts.
2. DBA cockpit direction records govern project priority, cross-project risk, and handoff state.
3. Red Yan product decisions and execution remain with the separate Red Yan conversation and the
   product repository's own authorization chain.

DBA is not a Red Yan runtime source of truth and does not inherit product execution authority from
receiving an investigation report.

## Superseded pre-investigation findings

The following tokens are preserved as investigation history only. They are not current blockers.

| Pre-investigation token | Status | Current replacement |
|---|---|---|
| `STALE_SRV_CURRENT_POINTER` | `SUPERSEDED_BY_POST_INVESTIGATION_EVIDENCE` | Legacy pointer corrected to `CORRECTED_COMPATIBILITY_ALIAS_NO_CURRENT_DRIFT` |
| `MULTIPLE_SIMULTANEOUS_DRIFTS` | `SUPERSEDED_BY_POST_INVESTIGATION_EVIDENCE` | Current application runtime commit and canonical control pointer agree |
| `BRAND_DEPLOYMENT_RECEIPT_LINEAGE_NOT_REMOTE` | `SUPERSEDED_BY_POST_INVESTIGATION_EVIDENCE` | Receipt exists in pushed repository evidence; lineage is partial and remote release binding remains missing |
| `3_OPEN_OFFICECLI_P1` | `SUPERSEDED_BY_POST_INVESTIGATION_EVIDENCE` | Zero current-runtime blockers and three candidate-promotion blockers |

## Current Red Yan runtime and metadata state

```text
RED_YAN_REMOTE_RUNTIME_COMMIT=4c98ba8a09eb1ae2d1a5dbdc5c66f8b4131848dd
RED_YAN_CURRENT_RUNTIME_DRIFT=false
RED_YAN_CANONICAL_CONTROL_POINTER=/home/hongyan-v1/hongyan-v1/current
RED_YAN_CANONICAL_CONTROL_POINTER_STATUS=ACTIVE_CONTROL_POINTER
RED_YAN_LEGACY_POINTER=/srv/hongyan-v1/current
RED_YAN_LEGACY_POINTER_STATUS=CORRECTED_COMPATIBILITY_ALIAS_NO_CURRENT_DRIFT
BASE_CONTAINER_LABEL_COUNT=4
BASE_CONTAINER_LABEL_CLASSIFICATION=LABEL_NOT_AUTHORITATIVE
BASE_CONTAINER_LABEL_CORRECTION_REQUIRES_REBUILD=true
BRAND_RECEIPT_EXISTENCE=REPOSITORY_EVIDENCE_PRESENT
BRAND_RECEIPT_LINEAGE=PARTIAL_LINEAGE
BRAND_RECEIPT_MAINLINE_STATUS=NOT_ON_PRODUCT_MAIN
BRAND_RECEIPT_REMOTE_BINDING=MISSING_REMOTE_BINDING
OFFICECLI_CURRENT_RUNTIME_BLOCKER_COUNT=0
OFFICECLI_PROMOTION_BLOCKER_COUNT=3
OFFICECLI_CANDIDATE_STATE=QUARANTINED_SHADOW_ONLY
DEPENDENCY_SECURITY_WORKSTREAM_REQUIRED=true
DEPENDENCY_FINDING=postcss -> nanoid <3.3.18
DEPENDENCY_EXPLOITABILITY=NOT_ASSESSED
```

The active user-level pointer is the canonical control pointer. The legacy `/srv` pointer is now a
corrected compatibility alias, not a current drift blocker. Four base-container labels remain
non-authoritative maintenance debt; correcting them requires a separately authorized rebuild and
was not executed by DBA.

The brand receipt is not absent. It exists as pushed repository evidence, but it is not on product
`main` and is not bound into the remote release artifact. OfficeCLI remains quarantined and
shadow-only: three P1 records block candidate promotion, while none is classified as a current
controlled-pilot runtime blocker.

## Current bounded factual issues

1. `https://dcell.net/digital-cell/`, `/digital-cell.json`, `/.well-known/titmas.json`,
   `/agent-index.json`, and `/llms.txt` all returned 404 on 2026-08-28. No dedicated Digital Cell
   page, TITMAS discovery surface, or public GitHub link was found on the current product page.
2. 红岩公文 remains in `REFINE_CORRECT_SIMPLIFY_STABILIZE_ONLY` freeze mode. Current remote
   runtime identity is consistent, while four non-authoritative base-container labels remain for a
   separately authorized maintenance window.
3. OfficeCLI has three candidate-promotion blockers but zero current-runtime blockers. Brand
   receipt evidence has partial lineage: repository evidence is present, product-main integration
   and remote-release binding are absent.
4. Production readiness, real customer validation, `main` merge, and `v1.0.0` tag remain false.
5. DBA PR #148 was manually merged by `joy7758` at 2026-08-28T13:19:27Z while its checks were
   still running. Conformance later passed; the site build later failed `npm audit --omit=dev` on
   two high-severity findings in the existing `postcss` to `nanoid <3.3.18` dependency chain.
   This reconciliation changed no package or lock file. Dependency repair remains a separate
   security task; the failed audit must not be described as passing merely because the PR merged.

## Red Yan Product Handoff

## 红岩产品交接

```text
RED_YAN_HANDOFF_STATUS=READY
RED_YAN_HANDOFF_TARGET=SEPARATE_RED_YAN_PRODUCT_CONVERSATION
RED_YAN_HANDOFF_ITEM=CANONICALIZE_VERIFIED_CONTROL_METADATA_AND_DEPLOYMENT_LINEAGE_WITHOUT_RUNTIME_CHANGE
DBA_EXECUTION_STATUS=NOT_EXECUTED_IN_DBA_COCKPIT
RUNTIME_CHANGE_AUTHORIZED_BY_DBA=false
PRODUCT_REPOSITORY_CHANGE_AUTHORIZED_BY_DBA=false
```

The separate Red Yan product conversation may, under its own explicit authorization, decide
whether to integrate verified receipts into product `main`, establish future remote-release
binding, schedule container-label maintenance, remediate OfficeCLI, or address the security
dependency. DBA records those workflows and their cross-project effects but does not execute them.

## DBA next action

```text
DBA_NEXT_ACTION=WAIT_FOR_PROJECT_STATUS_HANDOFFS_AND_MONITOR_CROSS_PROJECT_DRIFT
DBA_ACTIVE_PRODUCT_IMPLEMENTATION_TASK=NONE
DBA_RED_YAN_EXECUTION_TASK=NONE
DBA_CI_DEPENDENCY_AUDIT=FAIL_2_HIGH_NANOID_VIA_POSTCSS
DEPENDENCY_SECURITY_WORKSTREAM=SEPARATE_NOT_AUTHORIZED_IN_THIS_TASK
```

After receiving completion summaries from the separate Red Yan conversation, DBA may update
program state and check architecture drift, new truth-source creation, duplicate construction, and
project-priority effects. This cockpit record authorizes no product patch, product PR, runtime
change, deployment, OfficeCLI remediation, dependency remediation, merge, tag, release, or
production claim.
