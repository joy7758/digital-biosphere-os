# TITMAS Commercial CR-01 Ledger Transition Design v1.0

Status: `DESIGN_REVIEWED_IMPLEMENTATION_NOT_AUTHORIZED`

Primary repository: DBA, for architecture and decision boundaries only.

Implementation candidate repository: private Gateway, subject to CR01-D03.

## Problem

The CR-01 isolated restore preserved schema, counts, tenant Row-Level Security,
audit tip and all Receipt chain links. Two historical synthetic Receipts cannot
be signature-verified because their random integration-test public key was
never retained. Recovering that key is impossible. Treating these records as
valid would convert absence of evidence into a false verification claim.

## Options

| Option | Description | Result |
|---|---|---|
| A | Add a quarantine marker while continuing one active ledger | Rejected as sufficient remedy: it either mutates legacy semantics or requires verification skip logic; full restore remains ambiguous. |
| B | Start an unrelated clean ledger | Rejected: it breaks cryptographic continuity and risks creating a second unbound truth source. |
| C | Preserve the legacy ledger, record exceptions in a signed immutable manifest, and start tenant-scoped clean epochs cryptographically anchored to legacy tips | `RECOMMENDED_NOT_AUTHORIZED` |

Option C is the only recommended candidate. It combines immutable exception
recording with a clean epoch; it does not quarantine by modifying a Receipt or
by bypassing verification.

## Canonical model

```text
Immutable legacy tenant ledger
  -> exact chain verification
  -> exact signature results, including KEY_UNAVAILABLE
  -> LegacyLedgerSeal

Signed LedgerTransitionManifest
  -> legacy seal digests
  -> exact private exception references
  -> decision and source references
  -> no validity override

New tenant epoch genesis Receipt
  -> manifest digest
  -> prior tenant legacy tip hash
  -> new epoch identifier
  -> active retained signing key

New clean tenant epoch
  -> normal signed Receipt chain
  -> restore and runtime verification
```

This is one canonical ledger service with explicit epochs, not two competing
truth sources. Exactly one epoch per Tenant may accept new writes.

## Object contracts

### LegacyLedgerSeal

- `tenant_reference`: private opaque Tenant reference;
- `legacy_epoch_id`;
- `first_sequence` and `last_sequence`;
- `receipt_count`;
- `legacy_tip_hash`;
- `signatures_valid`;
- `signatures_unverifiable`;
- `chain_failures`;
- `sealed_at`;
- `source_backup_digest`;
- `decision_reference`.

The seal describes observed history. It does not certify the legacy epoch.

### LedgerTransitionException

- private `receipt_reference`;
- `tenant_reference` and `receipt_sequence`;
- `receipt_hash`;
- `key_id`;
- `verification_result=UNVERIFIABLE_KEY_UNAVAILABLE`;
- `classification=HISTORICAL_SYNTHETIC_INTEGRATION_TEST`;
- `disposition=RETAIN_IMMUTABLE_NO_VALIDITY_OVERRIDE`.

Public projections expose only aggregate counts and classification, never
Tenant, Agent, request, credential or Receipt identifiers.

### LedgerTransitionManifest

- `transition_id` and `manifest_version`;
- source Gateway, release and backup references;
- ordered `legacy_ledger_seals`;
- ordered private `exceptions`;
- target epoch references;
- canonicalization and digest algorithms;
- manifest digest and signature metadata;
- Human Decision reference;
- authority-boundary booleans fixed to false for Truth, Authorization,
  Certification and formal conformance.

### NewEpochGenesisReceipt

For each Tenant, the genesis Receipt must cryptographically cover:

- `new_epoch_id`;
- `tenant_reference`;
- `ledger_transition_manifest_digest`;
- `legacy_epoch_id`;
- `legacy_tip_hash`;
- `previous_receipt_hash=null` within the new epoch;
- `transition_reason=CR01_LEDGER_INTEGRITY_BOUNDARY`;
- retained active signing-key identity;
- timestamp and decision reference.

The legacy tip reference proves linkage, not validity of every legacy
signature.

## Verification vocabulary

Machine interfaces must preserve these distinct states:

```text
VALID
INVALID_SIGNATURE
UNVERIFIABLE_KEY_UNAVAILABLE
CHAIN_INVALID
ANCHOR_MISMATCH
MANIFEST_INVALID
NOT_ASSESSED
```

`UNVERIFIABLE_KEY_UNAVAILABLE` must never be translated to `VALID`, `PASS`,
`ACCEPTED` or `AUTHORIZED`.

## Migration candidate sequence

This sequence is a future implementation contract, not authorization:

1. take a new encrypted allowlisted backup and verify its digest;
2. restore into an isolated empty database;
3. recompute every Tenant chain and exact signature distribution;
4. generate tenant-scoped legacy seals and the private exception list;
5. canonicalize, hash and sign the transition manifest with a retained key;
6. create one signed new-epoch genesis Receipt per Tenant;
7. freeze writes for a bounded cutover window;
8. atomically select the new active epoch for each Tenant;
9. verify the legacy anchor, manifest, new epoch, forced RLS and tenant access;
10. retain the old ledger read-only and run the complete restore drill;
11. only after all gates pass may a separate decision allow CR-01 to resume.

No dual-write period is assumed. A partial Tenant cutover fails closed and may
not be reported as a global success.

## Restore gates

A future restore passes only when all of the following are independently true:

- the legacy 1,661 records, hashes and chain tips are preserved exactly;
- the legacy signature distribution remains `1659 valid / 2 unverifiable`;
- the signed transition manifest verifies and matches its private exceptions;
- every new epoch genesis matches its Tenant legacy tip and manifest digest;
- every new-epoch Receipt signature and chain link verifies;
- the active epoch pointer is unique per Tenant;
- all Tenant-owned tables preserve enabled and forced RLS;
- cross-Tenant negative runtime tests pass in the restored environment;
- usage, billing, quota and idempotency reconciliation passes;
- rollback and failure-injection evidence is retained;
- formal RTO is measured only after the complete drill passes.

Passing the new epoch does not rewrite the legacy result. Reports must say:

```text
LEGACY_LEDGER_VERIFICATION=INCOMPLETE_KEY_UNAVAILABLE
ACTIVE_EPOCH_VERIFICATION=PASS|FAIL|NOT_ASSESSED
TRANSITION_ANCHOR_VERIFICATION=PASS|FAIL|NOT_ASSESSED
FULL_RESTORE_PASS=true|false
```

## Rollback and failure closure

- Before activation, failure leaves the current release and ledger untouched.
- The active epoch switch must be atomic per Tenant and auditable.
- After activation, rollback must not append new Receipts to both epochs.
- An anchor, manifest, signature, RLS or reconciliation failure blocks
  activation and retains all evidence.
- Loss of the transition signing key, partial manifest materialization or a
  mismatched legacy tip is `BLOCKED_LEDGER_INTEGRITY`, not a warning.
- No destructive down migration is automatic.

## Required evidence before CR01-D03 can authorize implementation

- private schema and migration design with no raw payload or secret fields;
- threat model for epoch equivocation, manifest substitution, cross-Tenant
  leakage and rollback divergence;
- exact test matrix including negative and fault-injection cases;
- source allowlist and migration artifact hashes;
- key custody and signing ceremony plan;
- bounded PR and deployment-cap proposal;
- rollback plan that preserves both epochs and every failure record;
- independent Agent review with zero unresolved blockers.

## Current state

```text
CR01_D02_ACCEPTED=true
LEDGER_TRANSITION_DESIGN_COMPLETE=true
RECOMMENDED_OPTION=OPTION_C
IMPLEMENTATION_AUTHORIZED=false
DATABASE_MIGRATION_AUTHORIZED=false
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=false
SOAK_EXECUTION_AUTHORIZED=false
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY
PRODUCTION_READY=false
```
