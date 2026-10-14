---
document_id: TITMAS-FINAL-FORM-IMPLEMENTATION-DECISION-PACKET-1.0
title: TITMAS Final-Form Implementation Decision Packet v1.0
title_zh: TITMAS 最终形态实施决策包 v1.0
status: ready-for-human-decision
decision_authorized: false
implementation_authorized: false
---

# TITMAS Final-Form Implementation Decision Packet v1.0

## Decision requested

```text
NEXT_HUMAN_DECISION=
AUTHORIZE_FINAL_FORM_IMPLEMENTATION_FROM_ACCEPTED_ADOPTION_MATRIX
```

This packet proposes a bounded implementation sequence. It does not authorize
code changes, a new service, database migration, deployment, purchase, Paid
Beta, production, customer data or payment.

## D04 disposition prerequisite

```text
D04_FINAL_STATUS=CLOSED_FAILED_RETAINED
PR36_STATE=CLOSED
PR36_MERGED=false
D04_FURTHER_CANARY_RETRIES_AUTHORIZED=false
LEGACY_LEDGER_CLASSIFICATION=INTERNAL_EXPERIMENTAL_LEDGER
FUTURE_PRODUCTION_LEDGER_MODE=CLEAN_GENESIS
PRODUCTION_LEDGER_CREATED=false
PRODUCTION_SIGNER_CREATED=false
```

The accepted implementation must not reopen D04, reuse PR #36, run Migration
0005, create another internal clean ledger, or inherit legacy chain, sequence
or signature exceptions.

## Seven-layer final-form candidate

### Layer 1 — Agent Discovery

- TITMAS custom: machine discovery contract, versioned capability/profile
  links, stable status and reason semantics.
- Upstream: Nginx for ingress; OpenAPI as the API contract format.
- Thin adapter: public-safe discovery document to versioned API/profile links.
- Data boundary: public metadata only; no token, customer data or private repo
  path.
- Failure boundary: stale or inconsistent pointers fail `NOT_ASSESSED`/closed.
- Replacement boundary: proxy may change without changing discovery semantics.
- Current state: machine discovery exists; cross-surface consistency must be
  revalidated in P0.

### Layer 2 — Agent Identity and Scoped Access

- TITMAS custom: Agent identity, owner reference, scope, expiry and revocation
  semantics; Capability is not Permission.
- Upstream: PostgreSQL records and current application authentication.
- Thin adapter: scoped credential verifier to tenant-bound repository context.
- Data boundary: credential hashes/metadata only; no raw secret persistence.
- Failure boundary: unknown, expired or revoked scope denies access.
- Replacement boundary: future OpenFGA/OpenBao interfaces are optional and
  trigger-bound.
- Current state: candidate paths exist; restored tenant isolation and external
  Agent onboarding remain incomplete.

### Layer 3 — Schema and Preflight

- TITMAS custom: schemas/profiles, PASS/FAIL/NOT_ASSESSED, stable reason codes,
  fail-closed preflight.
- Upstream: JSON Schema/OpenAPI tooling and OpenAPI Generator.
- Thin adapter: generated transport clients plus handwritten semantic checks.
- Data boundary: schema-safe references, not unrestricted raw payloads.
- Failure boundary: incompatible/unknown schema does not execute.
- Replacement boundary: generator can change; contract and semantic fixtures
  remain canonical.
- Current state: several candidate schemas exist; API v1 and generation
  reproducibility require P0 freeze.

### Layer 4 — Receipt and Evidence

- TITMAS custom: Receipt semantics, provenance, Evidence mapping, Authority
  Boundaries and verifier reason codes.
- Upstream: PostgreSQL persistence; Cosign only for release/SBOM artifacts.
- Thin adapter: canonical Receipt verifier and Agent Evidence mapper.
- Data boundary: immutable references and signed fields; Evidence is not Truth.
- Failure boundary: invalid/unverifiable signatures remain failures and are
  never rewritten.
- Replacement boundary: signer/storage adapters can change without changing
  Receipt semantics.
- Current state: legacy ledger is experimental and failed-retained. Future
  production clean genesis is deferred to Paid Beta authorization.

### Layer 5 — Usage, Quota and Billing Preview

- TITMAS custom: tenant operation identity, quota result, Receipt linkage and
  billing-preview/non-payment boundary.
- Upstream: PostgreSQL transactions at current scale.
- Thin adapter: export interface for a future metering system.
- Data boundary: no real pricing/payment or customer production records yet.
- Failure boundary: duplicate operations fail idempotently; reconciliation
  unknown remains `NOT_ASSESSED`.
- Replacement boundary: OpenMeter only after its numeric trigger.
- Current state: candidate implementation exists; Paid Beta duties remain P1.

### Layer 6 — Observability and Operations

- TITMAS custom: readiness truth mapping, reason codes, recovery assessment and
  authority-safe operational status.
- Upstream: OpenTelemetry, GitHub Actions, Syft and Cosign; existing Nginx and
  systemd.
- Thin adapter: allowlisted telemetry and reproducible security/build jobs.
- Data boundary: no secrets/raw customer payloads in logs, traces or external
  services.
- Failure boundary: telemetry loss does not become Evidence or success.
- Replacement boundary: OTLP, SPDX/CycloneDX and signed artifacts are portable.
- Current state: partial observability exists; D04 showed restore/query/signer
  boundary gaps that P0 tests must preserve.

### Layer 7 — SDK and Agent Integrations

- TITMAS custom: Agent-readable semantics, structured handoff, Evidence and
  Authority mapping.
- Upstream: generated Python/TypeScript transport clients and official MCP SDK.
- Thin adapter: MCP and framework-specific mapping only.
- Data boundary: only explicitly scoped inputs/outputs; no provider key or
  customer payload capture.
- Failure boundary: framework/runtime claim does not become TITMAS fact without
  admitted evidence.
- Replacement boundary: adapters are replaceable and cannot own core schemas.
- Current state: public-safe source candidates exist; external Agent technical
  onboarding is not complete.

## Proposed acceptance scope

If accepted, the later implementation decision should authorize only the P0
items in
[`TITMAS-FINAL-FORM-IMPLEMENTATION-BACKLOG-v1.0.json`](TITMAS-FINAL-FORM-IMPLEMENTATION-BACKLOG-v1.0.json),
with path/repository ownership and per-change rollback defined before work.
P1 still requires Paid Beta decisions. P2 remains trigger-closed.

## Required Human checks before implementation

1. accept or amend every `RECOMMEND_ADOPT` decision and version pin;
2. approve exact repository/path owners for P0;
3. confirm license/NOTICE and hosted-service terms review owner;
4. confirm data-egress allowlist for telemetry and build services;
5. preserve D04 closure and production clean-genesis boundary;
6. define test, rollback and stop conditions per implementation PR.

## Explicitly not ready

```text
TITMAS_FINAL_FORM_TECHNICAL_CANDIDATE=false
TITMAS_COMMERCIAL_TECHNICAL_READY=false
TITMAS_PAID_BETA_READY=false
PRODUCTION_READY=false
TITMAS_MATURE_COMMERCIAL_INFRASTRUCTURE=false
```

## Decision options

- `ACCEPT_BOUNDED_P0`: authorize a later, path-scoped P0 implementation plan;
- `AMEND_MATRIX`: change component/mode/trigger and rerun affected audit;
- `DEFER`: retain this packet without implementation;
- `REJECT`: close the final-form implementation route.

No option is inferred from this packet's existence.
