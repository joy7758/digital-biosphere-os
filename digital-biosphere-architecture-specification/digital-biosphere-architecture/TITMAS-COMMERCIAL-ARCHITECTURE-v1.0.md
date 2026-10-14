# TITMAS Commercial Architecture v1.0

## Document state

```text
MATURITY=TECHNICAL_ARCHITECTURE_BASELINE
IMPLEMENTATION_COMPLETE=false
DEPLOYMENT_COMPLETE=false
FIRST_MULTI_TENANT_VERTICAL_SLICE_IMPLEMENTED=true
BOUNDED_COMMERCIAL_CANDIDATE_DEPLOYED=true
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY
CR01_D02_STATUS=ACCEPTED_DESIGN_ONLY
LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED=false
COMMERCIAL_TECHNICAL_READY=false
PUBLIC_PAID_LAUNCH_AUTHORIZED=false
```

This document defines the implementation boundary for a machine-first
commercial technical candidate. The first bounded vertical slice now exists,
but the complete architecture and deployment gates are not complete. It does
not claim a production service.

ADR-037 adds an implementation-unapproved transition candidate: retain the
legacy ledger exactly, sign a private exception manifest, and begin new
Tenant-scoped Receipt epochs anchored to the legacy chain tips. This does not
validate the two missing signatures and does not authorize a Gateway or
database change.

## Product contract

TITMAS provides AI Agents with:

1. machine discovery;
2. bounded schema and capability discovery;
3. tenant- and Agent-bound credentials;
4. structural preflight with `PASS`, `FAIL` and `NOT_ASSESSED`;
5. a verifiable processing receipt;
6. quota and usage visibility.

It is not an Agent Runtime, orchestrator, model provider, truth database,
automatic authority, certification body or general cloud.

## System boundary

```text
Machine Entry
    |
    v
Nginx
    |
    +--> /sandbox/v0.1  Stateless Developer Preview
    |
    +--> /api/v1       Commercial Candidate API
                           |
                           +--> Authentication and Scope
                           +--> Tenant Isolation
                           +--> Preflight
                           +--> Receipt Signer
                           +--> Usage and Quota
                           +--> Billing Preview
                           |
                           v
                     PostgreSQL Metadata
```

No central reasoning Agent is added. The service applies deterministic policy
and data rules. It does not choose scientific truth or make human decisions.

## Repository and service layout

Primary implementation remains the private
`joy7758/titmas-sandbox-gateway` repository.

```text
src/titmas_sandbox/       existing stateless preview
src/titmas_commercial/    new commercial candidate modules
migrations/commercial/    append-only SQL migrations
schemas/commercial/       public-safe data contracts
deploy/commercial/        immutable release and service profile
```

Two systemd application services are allowed at most:

- current `titmas-sandbox-preview.service`;
- candidate `titmas-commercial-api.service`.

The commercial service may initially reuse pure schema-validation functions
through explicit internal interfaces. It must not duplicate or silently alter
the Sandbox endpoint contract.

## Canonical object model

```text
ContractingPrincipal
  -> Organization
    -> Tenant
      -> AgentIdentity
        -> ServiceCredential

Tenant
  -> Plan
  -> Quota
  -> UsageLedger
  -> Receipt
  -> BillingAccount
```

Every protected request is bound to:

```text
tenant_id
agent_id
credential_id
request_id
idempotency_key
api_version
timestamp
```

Client-supplied identifiers never establish ownership. The authenticated
credential determines the tenant and Agent binding; conflicting request values
fail closed.

## Data ownership and persistence

PostgreSQL stores metadata and append-only ledgers only:

- organizations, tenants and Agent identities;
- credential digests and metadata, never plaintext credentials;
- scopes, plans and quotas;
- usage, receipt metadata, billing preview and audit events.

Defaults:

```text
REQUEST_BODY_PERSISTENCE=false
RESPONSE_BODY_PERSISTENCE=false
NO_CUSTOMER_PAYLOAD_RETENTION=true
NO_MODEL_TRAINING_USE=true
```

Request and response digests may be stored. The raw object is processed in
memory and discarded after the response.

## Authentication and authorization

Initial credential type:

```text
API_KEY
```

The server stores a slow, salted credential verifier or one-way digest and an
explicit key identifier. It never stores or returns the plaintext after
creation. Short-lived Agent tokens remain a later candidate and must not be
invented as an OAuth provider.

Authorization order:

1. parse bounded transport;
2. authenticate credential;
3. validate active interval and revocation;
4. bind tenant and Agent;
5. check exact endpoint scope;
6. check quota and idempotency;
7. perform bounded operation;
8. append usage and receipt atomically.

## Tenant isolation

Isolation is defense in depth:

- all repository methods require a `tenant_id`;
- ownership joins include the authenticated tenant;
- PostgreSQL Row-Level Security is required on every tenant-owned table;
- global administrator paths are offline and separately audited;
- cross-tenant negative tests are deployment blockers.

The program becomes `BLOCKED_SECURITY` after any cross-tenant access.

The application role must not own tenant tables or have `BYPASSRLS`. Each
transaction sets a local tenant context, and policies compare `tenant_id` with:

```text
NULLIF(current_setting('titmas.tenant_id', true), '')::uuid
```

Missing tenant context matches no row. Tests must query the database directly
under Tenant A, Tenant B and no-tenant contexts, independently of repository
methods.

## Receipt profile

Receipt v1 uses:

- JSON Schema Draft 2020-12;
- RFC 8785 JCS candidate canonicalization;
- SHA-256 digests;
- Ed25519 candidate signatures;
- a tenant chain sequence and `previous_receipt_hash`, omitted only for the
  genesis Receipt and required for every later Receipt.

The signature covers the receipt with signature value omitted and immutable
signature metadata included. A verifier checks syntax, canonical bytes,
digests, signature, version and chain linkage only.

Concurrent chain appends serialize through one tenant-chain row locked in the
same transaction. Receipt key lifecycle follows
[`TITMAS-RECEIPT-KEY-MANAGEMENT-v1.0.md`](TITMAS-RECEIPT-KEY-MANAGEMENT-v1.0.md).

```text
RECEIPT_NE_TRUTH=true
RECEIPT_NE_AUTHORIZATION=true
RECEIPT_NE_CERTIFICATION=true
```

## Transaction contract

One protected preflight transaction atomically:

1. reserves or resolves the idempotency key;
2. checks quota;
3. records one usage event;
4. records one receipt;
5. updates quota consumption;
6. commits the outcome.

A retry with the same tenant, operation and idempotency key returns the
original result without a second billable event. A mismatched payload digest
under the same key returns HTTP 409 with the stable Problem Details type:

```text
https://redcrag.cn/problems/idempotency-key-reused
```

## API separation

Public-safe discovery:

```text
/.well-known/titmas.json
/llms.txt
/agent-index.json
/status.json
/api/v1/openapi.json
/api/v1/status
/api/v1/capabilities
/api/v1/plans
```

Protected data plane:

```text
POST /api/v1/preflight
GET  /api/v1/receipts/{receipt_id}
POST /api/v1/receipts/verify
GET  /api/v1/usage
GET  /api/v1/quota
```

Control-plane operations are separately scoped and must not be granted to a
normal operational Agent.

## Control-plane boundary

The first vertical slice exposes no network control-plane endpoint. Tenant,
Agent, credential, plan and quota bootstrap use a root-controlled offline
administration command with an append-only audit record.

```text
NETWORK_CONTROL_PLANE_ACTIVE=false
OFFLINE_ADMINISTRATION_ONLY=true
NORMAL_AGENT_CAN_CREATE_CREDENTIAL=false
NORMAL_AGENT_CAN_CHANGE_PLAN=false
NORMAL_AGENT_CAN_CHANGE_QUOTA=false
```

Reserved control scopes do not create callable endpoints or permission. A
future network control plane requires an ADR defining its separate credential
realm, ingress restriction and deployment boundary. It must not share an
operational Agent credential. An Agent attempting a reserved operation fails
closed; an activated protected endpoint uses HTTP 403 and RFC 9457 Problem
Details, and records a sanitized audit event.

## Failure semantics

- `PASS`: the submitted object passed the declared structural checks.
- `FAIL`: the submitted object violated one or more declared structural rules.
- `NOT_ASSESSED`: the service could not safely reach a bounded conclusion.

Transport, authentication and authorization errors use RFC 9457 Problem
Details. Domain results remain domain objects and are not converted into
successful exceptions or truth claims.

## Deployment boundary

The existing Ubuntu 24.04 server has 2 CPUs, 7.7 GiB RAM and 83 GiB free disk
at baseline observation. PostgreSQL is not installed. The Ubuntu repository
candidate is PostgreSQL 16.

Deployment is allowed only after:

- migrations and rollback path pass locally;
- cross-tenant tests pass;
- receipt signer unavailability fails closed;
- a release manifest binds the exact commit and files;
- the existing Sandbox remains healthy;
- no DNS or certificate change is required.

## Readiness states

Architecture completion does not set readiness:

```text
COMMERCIAL_TECHNICAL_READY=false
PAID_BETA_READY=false
PRODUCTION_READY=false
MATURE_COMMERCIAL_INFRASTRUCTURE=false
```
