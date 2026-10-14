---
document_id: TITMAS-PRIVATE-AGENT-CUSTOMER-EVALUATION-GATEWAY-REPORT-v0.1
title: TITMAS Private Agent Customer Evaluation Gateway Completion Report v0.1
title_zh: TITMAS 私有智能体客户评估网关完成报告 v0.1
status: validated-private-merge-candidate
decision_id: TITMAS-PRIVATE-AGENT-CUSTOMER-EVALUATION-GATEWAY-D01
decision: ACCEPT_LOCAL_BLACK_BOX_GATEWAY_PREPARATION
decided_by_ref: zhangbin
---

# TITMAS Private Agent Customer Evaluation Gateway Completion Report v0.1

## Outcome

A local, loopback-only and one-session black-box evaluation facade now exposes
the bounded synthetic contract without exposing the private implementation.
It reuses the existing Response Capture component and reconstructs a separate
customer workspace from an explicit nine-file allowlist.

```text
PRIVATE_EVALUATION_FACADE=true
LOCAL_EPHEMERAL_SERVICE=true
BLACK_BOX_CUSTOMER_SURFACE=true
NETWORK_SCOPE=LOOPBACK_ONLY
SERVICE_LIFETIME=ONE_EVALUATION_SESSION
PUBLIC_NETWORK_EXPOSURE=false

NEW_AGENT_RUNTIME=false
NEW_CONTROL_PLANE=false
NEW_TRUTH_SOURCE=false
PUBLIC_API_SERVICE=false
PRODUCTION_SERVICE=false
```

## Pre-development Agent recommendation

The required Agent-readable product-fit review concluded:

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=LOCAL_LOOPBACK_BLACK_BOX_EVALUATION_FACADE
NOT_RECOMMENDED_AS=PUBLIC_API_RUNTIME_OR_CUSTOMER_ACCESS
```

The existing bundle and harness were understandable but not callable through
a black-box interface. The implementation closes that specific gap. It does
not resolve the separate reasons to withhold recommendation for public or real
customer use: no D02 Human Decision, no Provider/privacy freeze, no real
customer evidence, no public deployment authorization and no commercial
agreement.

## Verified baseline

```text
REPOSITORY_VISIBILITY=PRIVATE
PR_48_MERGED=true
PR_48_HEAD=ecacfe489c9fc4d80c288340a86c00cf598ca864
PR_48_MERGE_COMMIT=f893d5ef986e52e70957d6bef5c66dfbd1329fba
TITMAS_PUBLIC_EXPORT_DEFAULT_DENY=true
```

The stale PR #48 completion record was corrected to
`completed-merged-private-main` without changing its recorded test or risk
facts.

## Architecture

```text
Private core checkout
  -> loopback facade on 127.0.0.1:ephemeral-port
  -> one in-memory evaluation-scoped session credential
  -> bounded public JSON contract
  -> canonical Response Capture envelope
  -> deterministic synthetic result
  -> shutdown, token revocation and temporary workspace cleanup
```

The customer-visible side receives only:

1. a reconstructed nine-file contract bundle;
2. an ephemeral loopback endpoint;
3. an in-memory session token;
4. a result directory.

It does not receive `gateway/`, `.git`, private governance, core source,
internal tests, Provider credentials, commercialization drafts, the exposure
inventory, hidden expected answers or repository paths.

```text
CUSTOMER_WORKSPACE_CORE_SOURCE_COUNT=0
CUSTOMER_WORKSPACE_INTERNAL_TEST_COUNT=0
CUSTOMER_WORKSPACE_GIT_METADATA_COUNT=0
CUSTOMER_WORKSPACE_PRIVATE_PATH_COUNT=0
```

## Session and Response Capture

- The token uses 32 random bytes (256 bits) and remains in process memory.
- Authorization is evaluation-scoped, single-session, expiring and revocable.
- Logs contain only a token hash prefix.
- Shutdown clears the token, closes the socket, removes both temporary
  workspaces and leaves no response spool.
- Each request is adapted into the existing provider-neutral Response Capture;
  no second capture component is introduced.
- Gateway audit fields are optional schema extensions so historical v0.1
  envelopes remain loadable.

Each gateway envelope establishes:

```text
attempt_id
customer_session_id
requested_operation
request_contract_sha256
request_body_sha256
dispatch_started_at
response_status
response_body_sha256
final_state
```

```text
RESPONSE_ENVELOPE_IS_NOT_EVIDENCE_TRUTH=true
```

## Interface

The authenticated local surface contains:

- `GET /health`
- `GET /v1/capabilities`
- `POST /v1/evaluate`
- `POST /v1/verify`

All nine declared `TITMAS-EVAL-*` error classes return bounded JSON. Error
responses expose no stack, path, internal symbol, token, environment variable,
policy rule or algorithm detail.

## Deterministic customer rehearsal

The fake customer reads only the reconstructed bundle, discovers the local
surface, sends one valid synthetic request, sends a prohibited request and
writes structured feedback.

```text
FAKE_CUSTOMER_DISCOVERY=PASS
FAKE_CUSTOMER_VALID_CALL=PASS
FAKE_CUSTOMER_INVALID_CALL_HANDLED=PASS
FAKE_CUSTOMER_CORE_ACCESS=false
REAL_MODEL_CALL_COUNT=0
REAL_PROVIDER_CALL_COUNT=0
```

## Validation

| Validation | Result |
|---|---|
| Private Evaluation Gateway EG-01 through EG-16 | `16/16 PASS` |
| Response Capture compatibility | `16/16 PASS` |
| Private boundary and source classification | `18/18 PASS` |
| TITMAS conformance unit tests | `40/40 PASS` |
| TITMAS conformance harness | `PASS` |
| Agent-native tests | `25/25 PASS` |
| Reference tests | `5/5 PASS` |
| Site tests | `22/22 PASS` |
| Site lint | `PASS` |
| Production dependency audit | `0 vulnerabilities` |
| JSON parse | `85/85 PASS` |
| YAML parse | `9/9 PASS` |
| Python compile | `PASS` |
| Markdown links through conformance harness | `61 PASS` |
| Git diff check | `PASS` |
| Strong-pattern current-tree secret scan | `0 findings` |
| Customer bundle private-path scan | `0 findings` |
| Customer bundle internal-symbol scan | `0 findings` |
| Boundary symlink scan | `0 findings` |
| Conflict-marker scan | `0 findings` |

The complete site development dependency tree still reports nine high-severity
advisories. Production dependencies report zero vulnerabilities. This work
does not alter site dependencies or apply a breaking forced upgrade.

## D02 readiness

The gateway, isolated workspace, bundle and Response Capture are now
technically ready for a separately authorized one-time D02 cycle.

```text
TITMAS_PRIVATE_AGENT_CUSTOMER_D02_EXECUTION_READY=true
D02_PRIVATE_AGENT_CUSTOMER_CYCLE_AUTHORIZED=false
REAL_MODEL_CALL_COUNT=0
REAL_PROVIDER_CALL_COUNT=0
```

Provider/model names and a two-call budget in the D02 packet remain proposals.
They create no Provider selection, customer access, data processing,
commercial agreement or call authorization.

## Final state

```text
TITMAS_PRIVATE_EVALUATION_GATEWAY_READY=true
TITMAS_PRIVATE_EVALUATION_GATEWAY_TESTED=true
TITMAS_PRIVATE_CUSTOMER_WORKSPACE_ISOLATED=true
TITMAS_PRIVATE_AGENT_CUSTOMER_D02_EXECUTION_READY=true

D02_PRIVATE_AGENT_CUSTOMER_CYCLE_AUTHORIZED=false
REAL_MODEL_CALL_COUNT=0
REAL_PROVIDER_CALL_COUNT=0
COMMERCIAL_ACCESS_GRANTED=false
COMMERCIAL_AGREEMENTS_ACTIVE=false
CORE_REPOSITORIES_PRIVATE=true
PUBLIC_EXPORT_AUTHORIZED=false
PUBLIC_EXPORT_EXECUTED=false
PUBLIC_DEPLOYMENT_EXECUTED=false
TITMAS_COMMUNITY_ESTABLISHED=false
```

## TITMAS drift check

```text
CORE_INTEROPERABILITY_OBJECTIVE_PRESERVED=true
NEW_CONTROL_AUTHORITY_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
DUPLICATE_EVIDENCE_OR_VERIFICATION_CREATED=false
RUNTIME_OR_EXECUTOR_CREATED=false
CURRENT_CAPABILITY_OVERCLAIMED=false
PUBLIC_LAUNCH_AUTHORIZED=false
COMMUNITY_ESTABLISHED=false
TITMAS_DRIFT_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```
