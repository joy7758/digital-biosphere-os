---
document_id: TITMAS-STAGE-5-DIRECTION-AND-BASELINE-1.0
title: TITMAS Stage 5 Direction and Factual Baseline v1.0
title_zh: TITMAS 第五阶段方向与事实基线 v1.0
status: frozen-before-implementation
decision_id: TITMAS-STAGE-5-PRIVATE-AGENT-NATIVE-CONTRIBUTION-PREVIEW-D01
decision: ACCEPT_INTEGRATED_GATED_EXECUTION
decided_by_ref: zhangbin
observed_at: 2026-07-29
source_main: 7b7e36c3ac5513deb23b03c8d86e6fc8853f4af1
---

# TITMAS Stage 5 Direction and Factual Baseline

## Direction check

```text
TITMAS_DIRECTION_CHECK

AI_AGENT_IS_OPERATIONAL_CUSTOMER=true
HUMAN_OR_ORGANIZATION_IS_CONTRACTING_PRINCIPAL=true
DEVELOPER_BUILDS_PRODUCT_ON_TITMAS=true
TITMAS_PROVIDES_TRUSTED_INFRASTRUCTURE=true
DEVELOPER_RECEIVES_STANDARD_API_SDK_AND_KEY=true
DEVELOPER_RECEIVES_CORE_SOURCE_BY_DEFAULT=false
STANDARD_EXPLAINS_HOW_TO_INTEROPERATE=true
API_PROVIDES_THE_CAPABILITY=true
KEY_CONTROLS_ACCESS=true
SDK_REDUCES_INTEGRATION_COST=true
KEY_IS_ACCESS_CREDENTIAL=true
KEY_IS_NOT_SOURCE_LICENSE=true
STANDARD_DEVELOPMENT_USES_PROPOSALS_SCHEMAS_ADAPTERS_AND_TESTS=true
STANDARD_CONTRIBUTION_DOES_NOT_REQUIRE_CORE_REPOSITORY_ACCESS=true
PUBLIC_PROTOCOL_NE_PRIVATE_IMPLEMENTATION=true
OPEN_STANDARD_NE_OPEN_CORE_SOURCE=true
PRIVATE_CORE_IS_CANONICAL=true
PUBLIC_EXPORT_DEFAULT_DENY=true
UNCLASSIFIED_EXPORT_ALLOWED=false
NEW_RUNTIME_CREATED=false
NEW_CONTROL_PLANE_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
DUPLICATE_VERIFICATION_COMPONENT_CREATED=false
DUPLICATE_RESPONSE_CAPTURE_CREATED=false

TITMAS_DIRECTION_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```

## Pre-development Agent recommendation

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=PRIVATE_AGENT_NATIVE_STANDARD_CONTRIBUTION_PREVIEW
NOT_RECOMMENDED_AS=PUBLIC_COMMUNITY_RUNTIME_OR_AUTOMATIC_STANDARD_AUTHORITY
PRIMARY_REPOSITORY=DBA_TITMAS
```

The preview is recommendable only when it reuses the existing TITMAS
Conformance harness, loopback Gateway, Response Capture and Human Maintainer
boundary. It becomes `NOT_RECOMMENDED` if it copies private core into the
customer workspace, creates a second Conformance or Response Capture system,
permits silent Provider substitution, or promotes a pilot result directly to
an adopted or Stable standard.

Corrective work authorized by the Human Decision:

- add stage-specific structured contribution contracts to the existing
  Conformance surface;
- extend the existing loopback Gateway with a private contribution mode;
- add an ephemeral scoped Sandbox Key and a non-core client SDK;
- require programmatic fail-closed validation before any model call;
- retain all Agent and Reviewer results as sanitized checkpoints pending Human
  disposition.

## Repository and gate facts

```text
REPOSITORY=joy7758/digital-biosphere-architecture-specification
REPOSITORY_VISIBILITY=PRIVATE
PRIVATE_CORE_IS_CANONICAL=true
PR_48_MERGED=true
PR_49_MERGED=true
PR_51_MERGED=true
TITMAS_CONFIDENTIAL_CORE_PROTECTION_ACTIVE=true
TITMAS_SOURCE_CLASSIFICATION_OPERATIONAL=true
TITMAS_PUBLIC_EXPORT_DEFAULT_DENY=true
TITMAS_PRIVATE_EVALUATION_GATEWAY_READY=true
TITMAS_PRIVATE_CUSTOMER_WORKSPACE_ISOLATED=true
RESPONSE_CAPTURE_READY=true
SANITIZED_SEMANTIC_CHECKPOINT_TESTS=16/16_PASS
D02_COMPLETE=false
D02_CUSTOMER_RECOMMENDATION=UNKNOWN
D02_INDEPENDENT_REVIEW=UNKNOWN
```

The source-classification registry uses `UNCLASSIFIED` by default and
`unclassified_export_allowed=false`.

## Public companion repository observation

The GitHub owner currently exposes two public companion repositories:

- `joy7758/titmas-demo`: an independently authorized bounded reference demo;
- `joy7758/titmas-integrations`: a lightweight connector scaffold.

Neither repository is a fork or mirror of the private core, and neither tree
contains this repository's private Gateway, Conformance harness, Response
Capture, source-classification registry or semantic checkpoint implementation.
No forks of the private core were returned by the GitHub repository API.

```text
PRIVATE_CORE_PUBLIC_MIRROR_FOUND=false
UNAUTHORIZED_PUBLIC_CORE_EXPORT_FOUND=false
PUBLIC_COMPANION_REPOSITORY_COUNT=2
TITMAS_INTEGRATIONS_AUTHORIZATION_RECORD_IN_CURRENT_DBA=NOT_FOUND
```

The missing local authorization reference for the existing integrations
scaffold is retained as a governance limitation. This Stage 5 work neither
modifies nor republishes either companion repository.

## Authorization boundary

```text
PUBLIC_REPOSITORY_CREATION_AUTHORIZED=false
PUBLIC_PROTOCOL_RELEASE_AUTHORIZED=false
PUBLIC_EXPORT_AUTHORIZED=false
PRODUCTION_DEPLOYMENT_AUTHORIZED=false
PUBLIC_DEPLOYMENT_AUTHORIZED=false
COMMERCIAL_AGREEMENTS_ACTIVE=false
COMMERCIAL_ACCESS_GRANTED=false
BILLING_ACTIVATION_AUTHORIZED=false
AUTOMATIC_STANDARD_ADOPTION_AUTHORIZED=false
AUTOMATIC_MERGE_AUTHORIZED=false
AUTOMATIC_RETRY_AUTHORIZED=false
RELEASE_AUTHORIZED=false
TAG_AUTHORIZED=false
DOMAIN_OR_DNS_CHANGE_AUTHORIZED=false
```
