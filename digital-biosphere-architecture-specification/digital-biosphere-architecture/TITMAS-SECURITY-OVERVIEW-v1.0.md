# TITMAS Security Overview v1.0

## Status and audience

This is a public-safe architecture description, not a penetration-test report,
security certification or production guarantee.

```text
THREAT_MODEL_BASELINE_DEFINED=true
SECURITY_IMPLEMENTATION_COMPLETE=false
INDEPENDENT_SECURITY_TEST_COMPLETE=false
BOUNDED_SECURITY_IMPLEMENTATION_PRESENT=true
CRITICAL_SECURITY_FINDINGS_OPEN=1
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY_FAILED_RETAINED
CR01_D02_STATUS=ACCEPTED_DESIGN_ONLY_SUPERSEDED_BY_D04_CLOSURE
D04_FINAL_STATUS=CLOSED_FAILED_RETAINED
D04_FURTHER_CANARY_RETRIES_AUTHORIZED=false
LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED=false
FUTURE_PRODUCTION_LEDGER_MODE=CLEAN_GENESIS
PRODUCTION_READY=false
```

## Protected assets

- tenant, organization and Agent identity metadata;
- credential verifiers and revocation state;
- quotas, usage and billing-preview records;
- receipt metadata and chain state;
- receipt signing private key;
- audit and deployment records.

Raw customer objects are not intended to be persisted.

## Trust boundaries

1. public network to Nginx;
2. Nginx to loopback application;
3. application to PostgreSQL;
4. application to receipt signer;
5. offline administrator to credential and migration tools;
6. public verifier to published public key.

No model provider receives a service credential, receipt private key or
customer payload from the commercial control plane.

## Primary threats and required controls

| threat | required control | fail-closed evidence |
|---|---|---|
| cross-tenant object access | authenticated tenant binding on every object query; negative matrix | zero cross-tenant reads/writes |
| credential theft | one-time display, stored verifier only, scope, expiry, revocation and audit | revoked/expired key rejected |
| replay | request ID, tenant-bound idempotency key and stored payload digest | duplicate returns same result without new charge |
| scope escalation | exact endpoint scope and management/operational separation | missing scope denied |
| quota bypass | transactional reservation and append-only usage | concurrent limit tests |
| receipt forgery | canonical bytes, Ed25519 signature and versioned public key | tamper tests fail verification |
| chain tampering | per-tenant previous hash and unique sequence | deletion/reorder detected where chain applies |
| billing double count | unique tenant-operation-idempotency constraint | one billable event |
| JSON complexity attack | 64 KiB commercial target, depth/width/duplicate-key/NaN limits | parser rejects before domain work |
| log injection or secret logging | structured allowlisted fields and redaction | repository/log scan |
| database or signer failure | no fallback to unverified success | `NOT_ASSESSED` or service unavailable |

OWASP identifies object-level authorization failures as a common API risk and
requires an authorization check whenever client input selects a record. TITMAS
therefore does not treat a UUID, tenant field or Agent field as proof of
ownership.

## Cryptographic profile candidate

- canonicalization: RFC 8785 JCS;
- digest: SHA-256;
- signature: Ed25519 (RFC 8032);
- private key source: root-owned file or OS secret facility outside the release;
- public key: versioned, public-safe machine document;
- rotation: overlapping verification window, one active signer, retained key ID.

The reference library must implement the protocol; TITMAS will not implement
curve arithmetic.

Generation, file controls, backup, rotation, public-key discovery and
compromise response are normative for the candidate in
[`TITMAS-RECEIPT-KEY-MANAGEMENT-v1.0.md`](TITMAS-RECEIPT-KEY-MANAGEMENT-v1.0.md).

## Database-enforced tenant isolation

PostgreSQL Row-Level Security is mandatory for tenant-owned tables. The
application role has neither table ownership nor `BYPASSRLS`; each transaction
sets a local tenant context. Missing context returns no tenant row. Application
queries must still include explicit tenant predicates. Direct SQL tests prove
the RLS layer independently.

The first control plane is an offline, root-controlled administration tool.
No public or Agent-callable tenant, credential, plan or quota administration
endpoint is active in the first slice.

## Data minimization

Never log or persist:

```text
Authorization header
plaintext API key or token
raw request body
full response body
customer production object
receipt signing private key
provider API key
```

Allowed structured metadata is limited to pseudonymous IDs, operation,
outcome, latency, size, quota delta and error reason code.

## Security gates

Before a commercial candidate deployment:

- SAST, dependency and secret scans;
- SBOM;
- migration and release manifest verification;
- property-based receipt/idempotency tests;
- complete cross-tenant negative matrix;
- DAST against the candidate endpoints;
- signer/database degradation tests.

Any secret exposure, cross-tenant access, receipt forgery, billing double
count, unexpected payload persistence or unrecoverable backup blocks the
program and triggers rollback.

## Non-claims

```text
VERIFICATION_NE_AUTHORIZATION=true
RECEIPT_NE_TRUTH=true
CONFORMANCE_NE_CERTIFICATION=true
SECURITY_OVERVIEW_NE_SECURITY_CERTIFICATION=true
```

## References

- <https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/>
- <https://www.rfc-editor.org/info/rfc8785>
- <https://www.rfc-editor.org/info/rfc8032>
- <https://www.rfc-editor.org/info/rfc9457>
