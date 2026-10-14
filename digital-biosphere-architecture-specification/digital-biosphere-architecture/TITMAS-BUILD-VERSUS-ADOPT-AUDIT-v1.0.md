---
document_id: TITMAS-BUILD-VERSUS-ADOPT-AUDIT-1.0
title: TITMAS Build-versus-Adopt Audit v1.0
title_zh: TITMAS 自研与采用审计 v1.0
status: complete-decision-support-only
observed_at: 2026-08-01T04:20:00+08:00
implementation_authorized: false
production_ready: false
---

# TITMAS Build-versus-Adopt Audit v1.0

## 1. Outcome

TITMAS should adopt mature commodity infrastructure and build only the trust
semantics that make TITMAS distinct. At the current scale—one Baidu server,
supported concurrency 10, approximately 19 RPS, zero paying customers and no
real customer data—additional control planes and distributed data systems are
not justified.

```text
ADOPT_BEFORE_BUILD=true
AUDIT_STATUS=PASS_WITH_RECORDED_LIMITATIONS
COMPONENTS_AUDITED=15
RECOMMEND_ADOPT_COUNT=8
CONDITIONAL_ADOPT_COUNT=6
DEFER_COUNT=1
REJECT_COUNT=0
KEEP_CUSTOM_COUNT=10
IMPLEMENTATION_AUTHORIZED=false
```

The detailed, machine-readable evidence is
[`titmas-component-adoption-matrix-v1.0.json`](titmas-component-adoption-matrix-v1.0.json).
Scores measure fit for the present TITMAS baseline, not global project quality.

Read-only closure verification:

```text
PR36_STATE=CLOSED
PR36_MERGED=false
PR36_HEAD=3b8356d90b5eea3a0056e4672fdd7be077ec8177
LIVE_SERVICE_STATUS=active
LIVE_DATABASE_MIGRATION_EXECUTIONS=0
APPLICATION_DEPLOYMENT_ATTEMPTS=0
LIVE_RELEASE_CHANGED=false
LIVE_RELEASE=9bbfce6154d67f4ab50e911b5e49611f5a4a8b57
LEGACY_RECEIPTS=1661
CLEAN_SCHEMA_COUNT=0
TEMP_CANARY_DATABASE_COUNT=0
LEGACY_VALID_SIGNATURES=1659
LEGACY_UNVERIFIABLE_SIGNATURES=2
LEGACY_CHAIN_FAILURES=0
LEGACY_ROWS_MODIFIED=0
```

The current row count, absent clean schema, live release pointer and closed PR
were rechecked. Signature/chain counts and zero historical-row mutation are
retained from the immutable final-canary evidence; they were not recomputed by
writing to the live system.

## 2. Keep custom: unique TITMAS semantics

The following remain `KEEP_CUSTOM_UNIQUE_SEMANTICS`:

1. Agent Absolute Priority, without Agent self-authorization;
2. TITMAS machine discovery contract;
3. `PASS`, `FAIL`, `NOT_ASSESSED` result semantics;
4. stable Reason Codes;
5. Observation / Evidence / Verification / Evaluation / Authorization
   boundaries;
6. Receipt semantics and Authority Boundaries;
7. core and domain Schema/Profile definitions;
8. Agent Evidence mappings;
9. DBA / DBOS / SAEE responsibility and interface model;
10. cross-Agent structured handoff rules.

These semantics may use third-party libraries but cannot be delegated to a
database, proxy, telemetry collector, policy engine or workflow service.

### Full functional-scope disposition

| Audited function | Disposition | Boundary or gap |
|---|---|---|
| Machine discovery entry | `KEEP_CUSTOM_UNIQUE_SEMANTICS` | Nginx only serves the versioned contract |
| OpenAPI | custom canonical contract + `GENERATE_FROM_CONTRACT` | generator cannot define TITMAS semantics |
| Schema Catalog | `KEEP_CUSTOM_UNIQUE_SEMANTICS` | registry/storage implementation remains a P0 choice |
| Preflight | `KEEP_CUSTOM_UNIQUE_SEMANTICS` | fail closed on unknown schema/scope |
| Reason Codes | `KEEP_CUSTOM_UNIQUE_SEMANTICS` | stable machine-readable meanings |
| Receipt semantics | `KEEP_CUSTOM_UNIQUE_SEMANTICS` | Evidence and Authority boundaries remain canonical |
| Receipt signing | custom signer interface | production signer is P1 and does not yet exist |
| Receipt verification | custom verifier + standard crypto libraries | invalid/unverifiable is never rewritten |
| Receipt ledger | PostgreSQL + custom immutable chain semantics | legacy is experimental; production is clean genesis only |
| Agent Identity | custom object + PostgreSQL | identity does not create permission |
| Scoped Credentials | custom scope contract + current authentication | plaintext credentials are not persisted |
| Key expiry and revocation | custom contract/current storage | OpenBao deferred to rotation/dynamic-secret trigger |
| Tenant isolation | PostgreSQL RLS + application binding | restored runtime confirmation remains P0 |
| Quota | custom result semantics + PostgreSQL transaction | quota result is not payment authority |
| Usage metering | custom event/Receipt linkage + PostgreSQL | OpenMeter deferred to numeric trigger |
| Billing Preview | custom non-payment semantics + PostgreSQL | no price, invoice or payment authority |
| API entry | Nginx + existing FastAPI | APISIX deferred |
| Reverse proxy | Nginx | commodity ingress only |
| Rate limiting | existing Nginx/application controls | revalidation remains P0; no new gateway now |
| Policy engine | fixed custom scopes | OPA deferred to independent policy lifecycle |
| Secret management | existing OS/service boundaries | OpenBao deferred; no new secret service authorized |
| Python SDK | OpenAPI Generator | generated transport + thin semantic adapter |
| TypeScript SDK | OpenAPI Generator | generated transport + thin semantic adapter |
| MCP Adapter | official MCP SDK | MCP transport does not grant authority |
| Agent framework adapters | thin TITMAS mappings | framework behavior is not Evidence without admission |
| Logs | OpenTelemetry | allowlisted telemetry only |
| Metrics | OpenTelemetry | metrics are observations, not truth |
| Traces | OpenTelemetry | trace correlation is not authorization |
| Alerts | OTel signals + existing operations | long-term alert backend is not selected; P0 gap |
| SBOM | Syft | inventory is not vulnerability or license clearance |
| Release/SBOM signing | Cosign | artifact signature does not replace Receipt semantics |
| Dependency scanning | GitHub Actions orchestration and existing ecosystem scanners | exact scanner/version pin is P0 |
| Vulnerability scanning | adopt a maintained scanner through CI | specific scanner not selected in this 15-project audit; P0 decision gap |
| Message system | NATS/JetStream deferred | asynchronous delivery trigger required |
| Long workflow | Temporal deferred | durable multi-hour workflow trigger required |
| Complex authorization | OpenFGA deferred | relational-rule trigger required |
| Professional metering/billing | OpenMeter deferred | paying-tenant/event-volume trigger required |
| Large API gateway | APISIX deferred | Nginx capability-gap trigger required |

## 3. Adopt now as architecture baseline

| Component | Mode | TITMAS use | Boundary |
|---|---|---|---|
| PostgreSQL | `KEEP_EXISTING_COMMODITY_COMPONENT` | transactions, RLS, persistence | SQL repository boundary; no trust semantics delegated |
| Nginx | `KEEP_EXISTING_COMMODITY_COMPONENT` | TLS ingress, proxy, basic limits | HTTP ingress only |
| OpenTelemetry | `ADOPT_AS_RUNTIME_SERVICE` | logs, metrics, traces | sanitized OTLP; telemetry is not Evidence Truth |
| OpenAPI Generator | `GENERATE_FROM_CONTRACT` | Python/TypeScript transport clients | generated transport only; semantic adapter remains custom |
| official MCP SDK | `ADOPT_AS_DEPENDENCY` | MCP transport/protocol | transport does not grant capability or permission |
| Syft | `ADOPT_AS_BUILD_TOOL` | SPDX/CycloneDX SBOM | inventory is not vulnerability or license clearance |
| Cosign | `ADOPT_AS_BUILD_TOOL` | release/SBOM signature | artifact signature is not a TITMAS Receipt or Authorization |
| GitHub Actions | `KEEP_EXISTING_COMMODITY_COMPONENT` | CI, scans, reproducible builds | hosted terms, action pins and least privilege remain required |

Adoption is a recommendation for a later implementation decision. No package,
service or workflow change occurs in this audit.

## 4. Defer deployment by explicit trigger

| Component | Trigger | Why deferred now |
|---|---|---|
| OpenBao | `internal_secret_rotation_or_dynamic_credentials_exceed_current_boundary` | new secret service and MPL-2.0 operational obligations |
| OPA | `policy_rules_require_independent_policy_lifecycle` | fixed scopes do not justify a separate policy lifecycle |
| OpenFGA | `relational_authorization_rules_exceed_fixed_scope_model` | extra service/datastore and model governance |
| OpenMeter | `real_paying_tenants>=3 OR monthly_usage_events>=100000` | official architecture uses Kafka, ClickHouse, PostgreSQL and multiple workers |
| NATS / JetStream | `asynchronous_agent_event_delivery_required` | no current durable event-delivery requirement; production JetStream adds resource/HA duties |
| Temporal | `durable_multi_hour_workflow_required` | current flow does not justify a workflow control plane and persistence history |
| Apache APISIX | `Nginx_capabilities_no_longer_meet_route_or_plugin_requirements` | Nginx meets present needs; APISIX adds OpenResty/plugins and often etcd |

OpenBao, OPA, OpenFGA, NATS, Temporal and APISIX score
`CONDITIONAL_ADOPT`; OpenMeter scores `DEFER`. All seven use
`DEFER_UNTIL_SCALE_TRIGGER`, because classification of upstream suitability is
not permission to deploy it now. `DEFER` is not a negative judgment on upstream
quality. It is the required response when current demand does not justify
runtime weight or governance.

## 5. License and supply-chain review

Official license sources were checked for all candidates. The recommended
baseline uses PostgreSQL License, BSD-2-Clause, Apache-2.0 and MIT components,
plus the GitHub-hosted Actions service under GitHub terms. OpenBao uses
MPL-2.0 and remains deferred; a file-level copyleft and distribution-obligation
review is required before any future use. No candidate with SSPL, missing or
unclear commercial terms was recommended.

This audit is not legal advice. Before distribution, a Human Owner must verify:

- exact version license text and `NOTICE` obligations;
- generated-code notices and runtime/package transitive licenses;
- GitHub Actions service terms and every third-party Action pin;
- MPL-2.0 file boundaries if OpenBao is reconsidered;
- security advisories at the implementation date.

Default forbidden modes:

```text
COPY_SOURCE_INTO_TITMAS=false
RENAME_UPSTREAM_AS_TITMAS=false
VENDOR_WHOLE_REPOSITORY=false
UNTRACKED_PATCH_TO_UPSTREAM=false
```

Any fork requires an ADR, upstream synchronization plan, security update plan
and exit plan.

## 6. Data and failure boundaries

- PostgreSQL may hold canonical application records; it does not determine
  Evidence Truth or Authorization.
- Nginx and APISIX see request metadata; secrets and customer payload retention
  remain prohibited unless separately authorized.
- OpenTelemetry receives allowlisted telemetry. External exporters require a
  separate data-egress review.
- GitHub Actions receives repository/workflow data and scoped secrets; hosted
  CI is not a customer data plane.
- Syft may scan local artifacts without data egress. Remote registry access is
  explicit and separately scoped.
- Cosign keyless modes can use network transparency services; signing mode and
  identity policy must be separately selected.
- Deferred services cannot become an implicit Truth Source, Authority or
  irreversible control dependency.

## 7. Official-source register

The bounded review used only official project pages, repositories and release
records, including:

- PostgreSQL [current documentation](https://www.postgresql.org/docs/current/),
  [license](https://www.postgresql.org/about/licence/) and
  [version policy](https://www.postgresql.org/support/versioning/);
- Nginx [downloads](https://nginx.org/en/download.html) and
  [security advisories](https://nginx.org/en/security_advisories.html);
- OpenTelemetry [Collector documentation](https://opentelemetry.io/docs/collector/)
  and [official releases](https://github.com/open-telemetry/opentelemetry-collector-releases/releases);
- OpenAPI Generator [documentation](https://openapi-generator.tech/docs/) and
  [releases](https://github.com/OpenAPITools/openapi-generator/releases);
- MCP TypeScript SDK [documentation](https://ts.sdk.modelcontextprotocol.io/)
  and [repository](https://github.com/modelcontextprotocol/typescript-sdk);
- Syft [documentation](https://oss.anchore.com/docs/guides/sbom/getting-started/),
  Cosign [documentation](https://docs.sigstore.dev/cosign/), and
  GitHub Actions [security guidance](https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions);
- OpenBao [security model](https://openbao.org/docs/internals/security/), OPA
  [deployment guidance](https://www.openpolicyagent.org/docs/deploy), OpenFGA
  [production guidance](https://openfga.dev/docs/best-practices/running-in-production),
  and OpenMeter [architecture](https://openmeter.io/docs/open-source/architecture);
- NATS [installation/resource guidance](https://docs.nats.io/running-a-nats-service/introduction/installation),
  Temporal [repository](https://github.com/temporalio/temporal), and APISIX
  [deployment modes](https://apisix.apache.org/docs/apisix/3.13/deployment-modes/).

Release observations are point-in-time facts dated 2026-08-01. They are not a
permanent security clearance.

## 8. Two-lineage advisory review

```text
AGENT_AUDIT_SESSION_COUNT=2
ARCHITECTURE_ADOPTION_AUDITOR_MODEL=qwen3.7-max
LICENSE_AND_SUPPLY_CHAIN_AUDITOR_MODEL=deepseek-v4-pro
MODEL_LINEAGES_DISTINCT=true
RAW_PROVIDER_RESPONSE_COMMITTED=false
SECRET_OR_CUSTOMER_DATA_SENT=false
AGENT_APPROVAL_AUTHORITY=false
```

### `qwen3.7-max` — `ARCHITECTURE_ADOPTION_AUDITOR`

The model did not recommend TITMAS to a customer at current maturity. It agreed
with the lightweight baseline and deferred list, and identified the need for
machine-verifiable reason codes, trust boundaries and handoff fixtures. Its
proposal to continue D04 remediation or migrate the legacy ledger was rejected
because it conflicts with the Human Decision that permanently closes D04 and
requires future clean genesis.

### `deepseek-v4-pro` — `LICENSE_AND_SUPPLY_CHAIN_AUDITOR`

The model found the permissive-license baseline generally adoptable and asked
for notices, third-party Action review and an MPL boundary check. Its suggestion
that no Human legal gate was needed was rejected. License obligations and
commercial distribution remain a Human responsibility.

```text
AGENT_REVIEW_NE_ARCHITECTURE_DECISION=true
MODEL_RECOMMENDATION_NE_CUSTOMER_ADOPTION=true
MODEL_REVIEW_NE_LEGAL_APPROVAL=true
```

## 9. Recommendation gate

Current customer recommendation result:

```text
RECOMMEND_TITMAS_TO_CUSTOMER_NOW=false
```

Reasons: D04 is a retained failure; no external Agent beta exists; technical
candidate, paid beta and production gates remain false; unique semantics still
need an implementation decision and complete machine-verifiable fixtures.

The remediation is not “add more infrastructure.” It is to execute only an
accepted P0 backlog, preserve fail-closed semantics, complete external Agent
technical onboarding, and obtain new Human authorization for each later gate.

## 10. Completion state

```text
D04_FINAL_CLOSURE_RECORDED=true
PR36_CLOSED_UNMERGED_CONFIRMED=true
D04_FURTHER_RETRY_PATH_REMOVED=true
D04_PROGRAM_GATE=false

LEGACY_EXPERIMENTAL_LEDGER_BOUNDARY_FROZEN=true
FUTURE_PRODUCTION_CLEAN_GENESIS_PRINCIPLE_FROZEN=true
NO_MORE_INTERNAL_CLEAN_LEDGER_PROJECTS=true
NO_MORE_LEGACY_LEDGER_TRANSITION_PROJECTS=true
NO_MORE_D04_CANARIES=true

BUILD_VERSUS_ADOPT_AUDIT_COMPLETE=true
COMPONENT_ADOPTION_MATRIX_COMPLETE=true
LICENSE_REVIEW_COMPLETE=true
FINAL_FORM_ARCHITECTURE_PACKET_READY=true
FINAL_FORM_IMPLEMENTATION_BACKLOG_READY=true
P0_IMPLEMENTATION_ITEMS=10
P1_IMPLEMENTATION_ITEMS=6
P2_TRIGGERED_ITEMS=7

GATEWAY_CHANGED=false
DATABASE_CHANGED=false
LIVE_RELEASE_CHANGED=false
PAYMENT_EXECUTED=false

TITMAS_BUILD_VERSUS_ADOPT_AUDIT_COMPLETE=true
TITMAS_FINAL_FORM_IMPLEMENTATION_PLAN_READY=true
TITMAS_FINAL_FORM_TECHNICAL_CANDIDATE=false
TITMAS_COMMERCIAL_TECHNICAL_READY=false
TITMAS_PAID_BETA_READY=false
PRODUCTION_READY=false
TITMAS_MATURE_COMMERCIAL_INFRASTRUCTURE=false

NEXT_HUMAN_DECISION=AUTHORIZE_FINAL_FORM_IMPLEMENTATION_FROM_ACCEPTED_ADOPTION_MATRIX
```

## 11. Drift check

```text
D04_FAILURE_RETAINED=true
FOURTH_CANARY_AUTHORIZED=false
LEGACY_HISTORY_REWRITTEN=false
INTERNAL_EXPERIMENTAL_LEDGER_NE_PRODUCTION_LEDGER=true
FUTURE_PRODUCTION_LEDGER_NE_LEGACY_MIGRATION=true
ADOPT_BEFORE_BUILD=true
UPSTREAM_NE_TITMAS_CORE_SEMANTICS=true
OPEN_SOURCE_ADOPTION_NE_SOURCE_COPY=true
ARCHITECTURE_PLAN_NE_IMPLEMENTATION_COMPLETE=true
TECHNICAL_CANDIDATE_NE_PRODUCTION_READY=true
CUSTOMER_ADOPTION_FABRICATED=false
PAYMENT_FABRICATED=false
PRODUCTION_CLAIM_FABRICATED=false

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
