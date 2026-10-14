---
document_id: TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-DECISION-1.0
title: TITMAS Stage 5.1 Private External Developer Trial Channel Decision v1.0
title_zh: TITMAS Stage 5.1 私有外部开发者试用通道决策 v1.0
status: accepted-preparation-and-internal-validation
maturity: Development
normative: false
owner_ref: zhangbin
decision_id: TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-D01
---

# TITMAS Stage 5.1 Private Trial Channel Decision

## Human Decision

```text
DECISION_ID=TITMAS-STAGE-5-1-PRIVATE-EXTERNAL-DEVELOPER-TRIAL-CHANNEL-D01
DECISION=ACCEPT_PREPARATION_AND_INTERNAL_VALIDATION
DECIDED_BY_REF=zhangbin
```

The Decision authorizes preparation and internal validation of a separate
private developer trial channel. It authorizes exact-file allowlist
reconstruction, private repository creation, repository protection
configuration, deterministic programmatic trial, security scans, private
infrastructure commits, a private Pull Request and merge after all gates pass.

It does not authorize a participant invitation, access to the private core,
public export, public protocol release, commercial access, formal Specification
Registry change, production Deployment, Release, Tag, real model call or real
Provider call.

## Direction Check

```text
AI_AGENT_IS_OPERATIONAL_CUSTOMER=true
HUMAN_OR_ORGANIZATION_IS_CONTRACTING_PRINCIPAL=true
DEVELOPER_RECEIVES_STANDARD_API_SDK_AND_KEY=true
DEVELOPER_RECEIVES_CORE_SOURCE_BY_DEFAULT=false
PRIVATE_CORE_IS_CANONICAL=true
CORE_REPOSITORY_ACCESS_FOR_EXTERNAL_DEVELOPER=false
TRIAL_REPOSITORY_NE_CORE_REPOSITORY=true
TRIAL_REPOSITORY_IS_RECONSTRUCTED_FROM_ALLOWLIST=true
KEY_IS_ACCESS_CREDENTIAL=true
KEY_IS_NOT_SOURCE_LICENSE=true
STANDARD_CONTRIBUTION_USES_PROPOSALS_SCHEMAS_ADAPTERS_AND_TESTS=true
STANDARD_CONTRIBUTION_DOES_NOT_REQUIRE_CORE_ACCESS=true
PUBLIC_EXPORT_DEFAULT_DENY=true
UNCLASSIFIED_EXPORT_ALLOWED=false
NEW_RUNTIME_CREATED=false
NEW_CONTROL_AUTHORITY_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
DUPLICATE_CONFORMANCE_CREATED=false
DUPLICATE_RESPONSE_CAPTURE_CREATED=false
TITMAS_DIRECTION_CHECK_RESULT=PASS
TASK_STOPPED_FOR_STRATEGIC_DRIFT=false
```

The trial client can call the existing bounded Stage 5 Sandbox. The
reconstruction does not copy its implementation and does not create another
Runtime, Conformance authority, response-capture system or Truth source.

## Explicitly closed gates

```text
EXTERNAL_PARTICIPANT_INVITATION_AUTHORIZED=false
CORE_REPOSITORY_COLLABORATOR_INVITATION_AUTHORIZED=false
PUBLIC_REPOSITORY_AUTHORIZED=false
PUBLIC_EXPORT_AUTHORIZED=false
COMMERCIAL_ACCESS_GRANTED=false
COMMERCIAL_AGREEMENTS_ACTIVE=false
FORMAL_STANDARD_CHANGE_AUTHORIZED=false
PRODUCTION_DEPLOYMENT_AUTHORIZED=false
RELEASE_AUTHORIZED=false
TAG_AUTHORIZED=false
REAL_MODEL_CALL_AUTHORIZED=false
REAL_PROVIDER_CALL_AUTHORIZED=false
```

## Recommendation gate

The Agent recommendation is `CONDITIONALLY_RECOMMENDED`: a developer-facing
trial channel is recommendable only when it exposes bounded protocol, Schema,
SDK, synthetic examples and tasks without core source; preserves fail-closed
Conformance and Human Maintainer disposition; uses a separate private
repository with required protection; and passes a clean-clone trial.

If protection cannot block direct push, force push and branch deletion while
requiring a Pull Request, owner review and status checks, the repository may be
prepared but is not invitation-ready.

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDATION_DOES_NOT_GRANT_AUTHORITY=true
```
