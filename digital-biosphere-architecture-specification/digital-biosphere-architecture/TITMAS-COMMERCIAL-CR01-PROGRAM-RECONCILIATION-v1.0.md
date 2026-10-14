# TITMAS Commercial CR-01 Program Reconciliation v1.0

## Scope

This is a reference-only DBA cockpit reconciliation observed at
`2026-07-31T17:01:11+08:00`. It does not modify the Gateway, activate a
release, repair historical records, authorize another deployment, restart
CR-01 or change any commercial authority.

```text
PRIMARY_REPOSITORY=DBA
CHILD_IMPLEMENTATION_REPOSITORY_MODIFIED=false
PROGRAM_STATUS=WAITING_FOR_HUMAN_DECISION
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY
```

## Authoritative sources

| source | exact identity | bounded fact |
|---|---|---|
| DBA governance | `joy7758/digital-biosphere-architecture-specification@4edee669e67a3b5ba0c1cb0d0c17bc699f57cf3e` | pre-reconciliation governance baseline |
| Gateway canonical evidence | `joy7758/titmas-sandbox-gateway@c319001cc1cf9e44d8b3d0b142a025c6c9af1678` | implementation and merged CR-01 failure evidence |
| Public integrations | `joy7758/titmas-integrations@e8eeccbf19e5e1d1f01ab9ad8796a53591a38dc8` | observed integration repository baseline; commercial SDK readiness remains unassessed |
| Active commercial release at stop | `9bbfce6154d67f4ab50e911b5e49611f5a4a8b57` | retained bounded candidate release, not Production Ready |
| Failed CR-01 candidate | `33bea67bafcd5fe3aabc7e7f48b456dba42aaf76` | first candidate activation failed and rolled back |

The Gateway repository is the canonical source for implementation and
operational evidence. DBA records only bounded references and does not replace
those facts.

## Material progress since the governance baseline

The old DBA state said that no multi-Tenant API, PostgreSQL store, signed
Receipt, Usage Ledger, Billing Ledger or backup/restore evidence existed. That
statement is now stale.

Gateway PRs `#18` through `#35` established and tested:

- a separately namespaced PostgreSQL-backed `/api/v1` candidate;
- forced Row-Level Security on Tenant-owned tables;
- Tenant- and Agent-bound machine credentials, scopes, expiry and revocation;
- idempotent preflight without raw request or response persistence;
- Ed25519-signed, hash-linked Receipts and public verification material;
- Usage, Quota and Billing Preview ledgers;
- database-backed per-credential rate limits;
- machine-readable status, capabilities, plans and OpenAPI;
- bounded load, failure-injection, encrypted backup and isolated restore tools.

These are implementation facts, not evidence of production readiness,
external adoption, payment, formal Conformance or Certification.

## CR-01 retained outcome

```text
RESTORED_RECEIPTS_CHECKED=1661
RESTORED_RECEIPT_SIGNATURES_VALID=1659
RESTORED_RECEIPT_SIGNATURES_INVALID=2
RESTORED_RECEIPT_CHAIN_FAILURES=0

BACKUP_INTEGRITY=PASS
STRUCTURAL_RESTORE=PASS
FULL_RESTORE_DRILL=FAIL_RECEIPT_VERIFICATION

SUSTAINED_CAPACITY_60_MIN=NOT_STARTED
RESOURCE_HEADROOM=NOT_ASSESSED
RATE_LIMIT_AND_QUOTA=NOT_ASSESSED
SOAK_72H=NOT_STARTED

PRODUCTION_CANDIDATE_CAPACITY_PROFILE_VALIDATED=false
PRODUCTION_READY=false
```

The two invalid signatures are historical synthetic integration-test Receipts
whose random public key was never retained. The records and failure remain
immutable: they were not deleted, rewritten, re-signed or allowlisted.

## Capacity boundary

The only declared bounded profile remains:

```text
SUPPORTED_CONCURRENCY=10
SUPPORTED_RPS_RANGE=17_TO_19
SUPPORTED_P95_TARGET_MS=750
```

Concurrency 15 and 20 remain unsupported p95 failures. They are not mandatory
remediation targets for the current declaration and are not rerun to improve a
marketing number. The concurrency-10 observation is also not a sustained or
Production Candidate capacity claim.

## Pre-development Agent recommendation gate

`qwen3.7-max` reviewed the sanitized current facts before this reconciliation:

```text
AGENT_RECOMMENDATION=NOT_RECOMMENDED
RECOMMENDED_AS=INTERNAL_OR_PRE_PRODUCTION_TECHNICAL_CANDIDATE
NOT_RECOMMENDED_AS=PRODUCTION_COMMERCIAL_SERVICE
HUMAN_DECISION_STILL_REQUIRED=true
```

Valid reasons retained:

- CR-01 is blocked on restored Receipt integrity;
- sustained capacity, headroom and 72-hour evidence do not exist;
- external Agent Beta, real payment and customer adoption do not exist;
- Production Candidate and Production Ready remain false.

One advisory statement is not adopted: the model treated concurrency 15 and 20
as capacity defects that must be fixed. The authorized profile is concurrency
10 at 17–19 RPS, so higher profiles remain retained unsupported observations,
not current remediation requirements.

The recommendation is advisory and creates no implementation, deployment,
commercial or release authority.

## Current gate interpretation

| area | program status | interpretation |
|---|---|---|
| Multi-Tenant model | `PASS_IMPLEMENTED` | scoped implementation exists |
| Tenant-bound credentials | `PASS_IMPLEMENTED` | no public self-registration |
| Usage and Billing Preview | `PASS_IMPLEMENTED` | no active price or payment |
| Signed Receipts | `FAILED_RETAINED` | current design exists; historical restored ledger is not fully verifiable |
| Candidate deployment | `PASS_WITH_LIMITATIONS` | retained candidate is active; attempted CR-01 candidate rolled back |
| Backup | `PASS` | encrypted backup integrity only |
| Restore | `FAIL_RECEIPT_VERIFICATION` | structural restoration is not full recovery |
| Incident/rollback | `PARTIAL` | startup fail-close and rollback observed; formal drill incomplete |
| Load | `PASS_WITH_LIMITATIONS` | frozen bounded matrix only; no one-hour sustained result |
| 72-hour soak | `NOT_STARTED` | elapsed time is not fabricated |
| External Agent Beta | `NOT_STARTED` | internal synthetic activity is not adoption |

## Required Human Decision

The next step must separately decide:

1. how to preserve and govern the two immutable historical synthetic Receipts
   without deleting, rewriting, re-signing or allowlisting them;
2. whether to authorize an exception to the exhausted
   `MAX_APPLICATION_REDEPLOYMENTS=1` and
   `MAX_REMEDIATION_IMPLEMENTATION_PRS=2` limits.

Until then:

```text
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=false
SOAK_EXECUTION_AUTHORIZED=false
PUBLIC_PAID_LAUNCH_AUTHORIZED=false
REAL_PAYMENT_ACCEPTANCE_AUTHORIZED=false
CUSTOMER_PRODUCTION_DATA_AUTHORIZED=false
```

## Drift Check

```text
TITMAS_DRIFT_CHECK
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
