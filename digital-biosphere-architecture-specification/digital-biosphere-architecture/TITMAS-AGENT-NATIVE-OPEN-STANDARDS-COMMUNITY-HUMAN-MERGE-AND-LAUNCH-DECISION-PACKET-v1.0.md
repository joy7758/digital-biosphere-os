---
document_id: TITMAS-AGENT-NATIVE-OPEN-STANDARDS-COMMUNITY-HUMAN-DECISION-PACKET-1.0
title: TITMAS Agent-Native Open Standards Community Human Merge and Launch Decision Packet v1.0
title_zh: TITMAS 智能体原生开放标准社区人工合并与启动决策包 v1.0
status: human-owner-core-merge-and-limited-opening-authorized
maturity: Development
normative: false
owner_ref: zhangbin
authority_ref: TITMAS-COMMUNITY-CORE-MERGE-AND-OPENING-D01
implementation_status: bounded-core-merge-and-public-contribution-activation-authorized
conformance_status: pass-at-remediation-head-human-owner-review-pass
security_review_status: activation-authorized-not-yet-executed
external_adoption_status: not-assessed
---

# TITMAS Human Merge and Launch Decision Packet v1.0

This packet records the bounded Human Owner decision
`TITMAS-COMMUNITY-CORE-MERGE-AND-OPENING-D01`.

```text
DECISION=ACCEPT
DECIDED_BY_REF=zhangbin
DECIDED_AT=2026-07-29T08:33:36+08:00
DECISION_SOURCE=EXPLICIT_HUMAN_OWNER_APPROVAL
```

The decision authorizes the PR #41 core merge, activation of GitHub Private
Vulnerability Reporting, one separate Activation PR, a limited repository
contribution preview and one bounded Welcome Issue. It does not authorize a
Foundation, Certification, Stable promotion, commercial product, Release tag,
deployment, Calibration v0.3, Formal Ecology Box or automatic acceptance of
external contributions.

The candidate branch is
`codex/titmas-agent-native-open-standards-community-canonical-integration-v1`,
based on `origin/main@ba6d51f60c12f1ac954dd67947451821fd5a3eb6`.
The canonical community name is **TITMAS Agent-Native Standards Community**
（TITMAS 智能体原生标准社区）.

## Decision table

| decision_id | question | status | current default |
|---|---|---|---|
| `COMMUNITY-HD-01` | Merge the Draft PR to `main`? | `ACCEPT` | Human Owner review lanes A–F pass |
| `COMMUNITY-HD-02` | Enable GitHub Private Vulnerability Reporting or another real private security intake? | `ACCEPT_AND_EXECUTE` | must verify `enabled=true` before template activation |
| `COMMUNITY-HD-03` | Activate the public Issue / PR contribution surface? | `ACCEPT_AND_EXECUTE` | one separate security-gated Activation PR |
| `COMMUNITY-HD-04` | Create the `titmas-cn` GitHub Organization? | `DEFER_GITHUB_ORGANIZATION_NOT_REQUIRED` | no organization |
| `COMMUNITY-HD-05` | Publish a Community Preview tag? | `DEFER_RELEASE_TAG_NOT_REQUIRED` | no tag or Release |
| `COMMUNITY-HD-06` | Publish a community announcement? | `ACCEPT_BOUNDED_REPOSITORY_WELCOME` | maximum one Welcome Issue |
| `COMMUNITY-HD-07` | Invite the first external Agent participant? | `ACCEPT_OPEN_PUBLIC_AGENT_AND_HUMAN_PARTICIPATION` | repository participation only; no Authority |
| `COMMUNITY-HD-08` | Assign an independent Human Reviewer? | `DEFER_INDEPENDENT_HUMAN_REVIEWER_NOT_ASSIGNED` | Human Owner review is not independent review |

## Evidence required before decisions

- `COMMUNITY-HD-01`: clean Draft PR, exact main base, complete integration
  manifest, local conformance, remote CI and no unresolved blocking finding.
- `COMMUNITY-HD-02`: a real receiving mechanism, access control, retention,
  escalation and response ownership; no invented mailbox.
- `COMMUNITY-HD-03`: merged canonical entries, active security transport,
  bounded permissions, abuse controls, an explicit activation record and a
  separate Activation PR.
- `COMMUNITY-HD-04`: ownership, account recovery, naming and repository
  migration decision.
- `COMMUNITY-HD-05` and `06`: merged candidate, exact release scope, remaining
  limitations and separate release/announcement authority.
- `COMMUNITY-HD-07`: participant contract, privacy boundary, scope lease,
  revocation, cost and Human exception path.
- `COMMUNITY-HD-08`: reviewer identity, independence, conflicts, scope and
  abstention terms.

## Current blockers and non-claims

GitHub Private Vulnerability Reporting was observed disabled on 2026-07-29.
Activation is now authorized but has not yet been executed. Public contribution
must remain inactive until a fresh API read confirms `enabled=true` and the
separate Activation PR is merged.

Prepared dormant assets:
[`TITMAS/community/github-activation-templates/README.md`](TITMAS/community/github-activation-templates/README.md).
Prepared Human review:
[`TITMAS-PR41-HUMAN-MERGE-REVIEW-CHECKLIST-v0.1.md`](TITMAS-PR41-HUMAN-MERGE-REVIEW-CHECKLIST-v0.1.md).

```text
COMMUNITY_HD_01=ACCEPT
COMMUNITY_HD_02=ACCEPT_AND_EXECUTE
COMMUNITY_HD_03=ACCEPT_AND_EXECUTE
COMMUNITY_HD_04=DEFER_GITHUB_ORGANIZATION_NOT_REQUIRED
COMMUNITY_HD_05=DEFER_RELEASE_TAG_NOT_REQUIRED
COMMUNITY_HD_06=ACCEPT_BOUNDED_REPOSITORY_WELCOME
COMMUNITY_HD_07=ACCEPT_OPEN_PUBLIC_AGENT_AND_HUMAN_PARTICIPATION
COMMUNITY_HD_08=DEFER_INDEPENDENT_HUMAN_REVIEWER_NOT_ASSIGNED
TITMAS_DRAFT_INTEGRATION_PR_AUTHORIZED_BY_D01=true
TITMAS_DRAFT_PR_CREATION_BLOCKED_BY_SECURITY_TRANSPORT=false
MERGE_TO_MAIN_AUTHORIZED=true
SECURITY_TRANSPORT_ACTIVATION_AUTHORIZED=true
PUBLIC_CONTRIBUTION_ACTIVATION_AUTHORIZED=true
LIMITED_PUBLIC_CONTRIBUTION_PREVIEW_AUTHORIZED=true
WELCOME_ISSUE_AUTHORIZED=true
MAX_PUBLIC_WELCOME_ISSUES=1
MAX_ACTIVATION_PULL_REQUESTS=1
PUBLIC_COMMUNITY_LAUNCH_AUTHORIZED=false
PUBLIC_ANNOUNCEMENT_AUTHORIZED=false
OPEN_REPOSITORY_PARTICIPATION_AUTHORIZED=true
TAG_AUTHORIZED=false
RELEASE_AUTHORIZED=false
FOUNDATION_CREATED=false
CERTIFICATION_AUTHORIZED=false
COMMERCIAL_OFFER_AUTHORIZED=false
CALIBRATION_V0_3_AUTHORIZED=false
FORMAL_ECOLOGY_BOX_EXECUTION_AUTHORIZED=false
```

Human Owner review is not independent third-party review. Core merge is not
public opening; public opening requires verified Security Transport and the
separate Activation PR. Conformance is not adoption; contribution is not
acceptance; external participation is not Authority.
