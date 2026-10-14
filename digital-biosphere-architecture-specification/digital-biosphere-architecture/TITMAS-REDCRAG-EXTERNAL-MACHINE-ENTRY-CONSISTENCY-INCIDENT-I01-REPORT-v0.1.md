---
report_id: TITMAS-REDCRAG-EXTERNAL-MACHINE-ENTRY-CONSISTENCY-INCIDENT-I01-v0.1
status: PASS_DEPLOYED_WITH_RECORDED_LIMITATIONS
observed_at: 2026-07-30T00:03:24+08:00
public_site: https://redcrag.cn/
---

# TITMAS redcrag.cn External Machine Entry Consistency Incident I01 Report v0.1

## Outcome

The website regression was corrected additively. Established public pages,
machine-readable resources, research and application material were restored
without replacing the current Stage 5.2 developer-trial truth.

The public identity now uses:

- `夏日之海` as the Chinese display brand;
- `TITMAS` as the English and technical identifier;
- the supplied boy-and-sea artwork as a real transparent PNG;
- the established blue, orange and teal visual language;
- a simplified five-entry primary navigation architecture.

```text
SOURCE_LINEAGE_REGRESSION_CONFIRMED=true
ADDITIVE_RESTORATION_COMPLETE=true
CURRENT_STAGE_TRUTH_PRESERVED=true

CHINESE_DISPLAY_BRAND=夏日之海
ENGLISH_TECHNICAL_BRAND=TITMAS
EXISTING_VISUAL_LANGUAGE_PRESERVED=true
PRIMARY_NAVIGATION_SIMPLIFIED=true
```

## Incident

A previous website update used an incomplete source lineage. The resulting
surface retained the newest developer-entry information but omitted established
routes and public assets. This was a presentation and source-integration
regression; it was not evidence that the omitted material had been deprecated
or withdrawn.

The correction used the previously complete website source as the restoration
baseline and overlaid the current Stage 5.2 truth. Existing historical reports
were not rewritten.

## Architecture correction

The correction changes information architecture, not the established color
system.

The primary navigation is limited to:

1. Participate / 参与入口;
2. Research / 研究;
3. Demos / Demo;
4. Applications / 应用;
5. Status / 状态.

Secondary material remains discoverable through page sections, the footer,
machine-readable indices and direct routes. Simplifying the first-level
navigation does not delete or de-authorize content.

## Source and review binding

| Field | Value |
|---|---|
| `source_repository` | `joy7758/digital-biosphere-architecture-specification` |
| `restoration_reference` | `3b002fe37ba4c456baab8f6bf52f1576d243a1cb` |
| `feature_branch` | `codex/redcrag-machine-entry-consistency-i01` |
| `pull_request` | `#57` |
| `reviewed_head` | `dcba2aaa7c6160de9e4d945d022eec4be0fa4253` |
| `merge_commit` | `422bec847ba3b21aefdd1d58af764ba651d1a4d0` |
| `ci` | `PASS` |

The exact merge source was built before deployment. No Release, Tag, Runtime,
Agent, Entity, Permission, certification authority or new hosting provider was
created.

## Content and brand preservation

The deployed surface preserves:

- the developer-community entry and current private-trial boundaries;
- the architecture, research, applications, demos, status and update routes;
- commercial-evaluation reference material and its recorded limitations;
- public-safe SDK, schema and synthetic-example resources;
- `llms.txt`, Agent Index and other machine-readable discovery surfaces;
- Chinese and English route parity;
- the existing color palette and graphic treatment.

The logo transformation removed the outer background only. It did not create a
new character, replace the sea scene or convert the asset into a text-only
brand.

## Validation

| Check | Result |
|---|---|
| Site test suite | `43/43 PASS` |
| Lint | `PASS` with four pre-existing image warnings |
| Formal static export | `PASS` |
| Bilingual routes in release index | `34` |
| Local links checked | `1468 PASS` |
| Release manifest files | `105` |
| On-host manifest verification | `105/105 PASS` |
| Publicly addressable manifest files | `103/103 HASH MATCH` |
| Online routes | `34/34 HTTP 200` |
| Transparent logo | `HTTP 200`, `image/png` |
| Chinese display-brand marker | `PASS` |
| English technical-brand marker | `PASS` |
| Agent-readable entry marker | `PASS` |

Two dot-prefixed build-control files are included in the on-host release
manifest but intentionally are not public URLs. They passed on-host verification
and are excluded from the `103/103` public-addressability check.

## Disclosure and security checks

```text
PRIVATE_REPOSITORY_URL_FINDINGS=0
SERVER_INFRASTRUCTURE_DISCLOSURE_FINDINGS=0
SECRET_FINDINGS=0
PRIVATE_PATH_FINDINGS=0
CORE_SOURCE_DISCLOSURE_FINDINGS=0
CUSTOMER_DATA_FINDINGS=0
```

The existing security configuration passed validation before the atomic site
switch. The preceding release remains available as the rollback target.

## Current-state boundary

The correction does not change:

```text
CURRENT_STAGE=TITMAS_STAGE_5_2_EXTERNAL_DEVELOPER_TRIAL
E01_STATUS=IN_PROGRESS_WAITING_FOR_PARTICIPANT_ACTION
FIRST_EXTERNAL_HUMAN_DEVELOPER_TRIAL_COMPLETE=false

PUBLIC_PROTOCOL_RELEASED=false
FORMAL_STANDARD_CHANGE_AUTHORIZED=false
NEXT_TRIAL_SLOT_AUTHORIZED=false
COMMERCIAL_ACCESS_GRANTED=false
PRODUCTION_READY=false
```

The public interest entry remains non-binding. Public presentation does not
grant private repository access, trial admission, certification, standard
adoption or commercial availability.

## Limitations

- Information-architecture simplification has passed technical and visual
  review, but reduced human management cost has not been independently measured.
- The public-safe resources remain bounded Developer Preview material.
- Core implementation remains private.
- E01 remains in progress; this incident correction is not trial completion or
  customer validation.

## TITMAS Drift Check

```text
TITMAS_DRIFT_CHECK

PRIMARY_INFRASTRUCTURE_OBJECTIVE_PRESERVED=true
CURRENT_STAGE_TRUTH_PRESERVED=true
ADDITIVE_UPDATE_DISCIPLINE_RESTORED=true

NEW_CONTROL_AUTHORITY_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
DUPLICATE_WEBSITE_CREATED=false
DUPLICATE_EVIDENCE_OR_VERIFICATION_CREATED=false
RUNTIME_OR_EXECUTOR_CREATED=false
CURRENT_CAPABILITY_OVERCLAIMED=false

ARCHITECTURE_SIMPLIFICATION_VALIDATED=true
HUMAN_MANAGEMENT_COST_REDUCTION=NOT_MEASURED

TITMAS_DRIFT_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```
