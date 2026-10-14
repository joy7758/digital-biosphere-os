# TITMAS Data Governance v1.0

## Defaults

```text
NO_CUSTOMER_PAYLOAD_RETENTION=true
REQUEST_BODY_PERSISTENCE=false
RESPONSE_BODY_PERSISTENCE=false
NO_MODEL_TRAINING_USE=true
NO_ADVERTISING_USE=true
MINIMUM_METADATA_RETENTION=true
CUSTOMER_PRODUCTION_DATA_AUTHORIZED=false
```

## Data inventory

| class | examples | persistence | access |
|---|---|---|---|
| public | schemas, OpenAPI, public keys, machine status | versioned public artifacts | anyone |
| tenant metadata | tenant, Agent, plan, quota | PostgreSQL | bound tenant/control roles |
| security metadata | credential digest, scope, expiry, revocation | PostgreSQL | security service/offline admin |
| operational metadata | request ID, outcome, latency, reason code | PostgreSQL/log pipeline | tenant-safe operations |
| receipt metadata | digests, signature, chain link | PostgreSQL/public verifier response | bound tenant; verification material public-safe |
| billing preview | usage units, period, candidate currency | PostgreSQL/export | contracting principal/control role |
| prohibited by default | raw object, response body, provider key, plaintext token | none | none |

## Purpose limitation

Metadata is processed only for authentication, authorization, quota,
idempotency, receipt generation, audit, operation and billing preview. It is
not used to train models or target advertising.

## Retention baseline

Final periods remain draft inputs until legal and commercial review:

- credential and security audit: candidate 365 days after revocation;
- usage and billing preview: candidate 365 days;
- receipt metadata: plan-defined candidate period;
- application logs: candidate 30 days;
- backups: candidate rolling 7 daily and 4 weekly copies.

No retention value is a published contractual commitment at this phase.

## Tenant export

Machine-readable export may include:

- tenant and Agent metadata;
- credential metadata without secret verifier;
- quota and usage events;
- receipt metadata;
- billing previews;
- audit event references.

Exports require exact tenant authority and never include another tenant.

## Tenant deletion

Deletion is a controlled lifecycle:

1. suspend credentials;
2. close new writes;
3. create an export if authorized;
4. delete or cryptographically render inaccessible tenant data;
5. retain only legally or security-required tombstone metadata;
6. record deletion scope and result;
7. wait for backup expiry or execute separately approved secure purge.

The system must state what remains and why. `deletion_requested` is not
`deletion_proven`.

## Audit integrity

Usage, receipt and billing events are append-only. Corrections use compensating
records and retain the original event. Failures and `NOT_ASSESSED` outcomes are
not deleted.

## New-data gate

Any new persistent field must document:

```text
purpose
data_class
retention
authorized_readers
deletion_method
deletion_evidence
tenant_binding
```

Missing information blocks the migration.

## Legal status

This architecture baseline is not a privacy notice, data-processing agreement
or legal approval.

```text
DRAFT_NOT_LEGAL_APPROVAL=true
LEGAL_REVIEW_REQUIRED_BEFORE_PAID_PUBLIC_LAUNCH=true
```
