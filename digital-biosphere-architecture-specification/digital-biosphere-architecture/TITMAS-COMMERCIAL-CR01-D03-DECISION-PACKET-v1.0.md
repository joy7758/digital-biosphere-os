# TITMAS Commercial CR-01 D03 Human Decision Packet v1.0

Status: `READY_FOR_HUMAN_DECISION_NOT_AUTHORIZED`

Prepared at: `2026-07-31T19:20:00+08:00`

Primary repository: DBA. This packet proposes a bounded implementation scope;
it does not modify the private Gateway, PostgreSQL, a credential, a Receipt,
a deployment, CR-01 or soak.

## Decision question

Should the Human Owner authorize one bounded implementation of CR01-D02 Option
C, including one exceptional Gateway PR, one additive migration execution, one
application deployment attempt and a fail-closed restore revalidation?

Option C means:

```text
IMMUTABLE_LEGACY_RECEIPTS
  + SIGNED_PRIVATE_TRANSITION_MANIFEST
  + TENANT_SCOPED_ANCHORED_CLEAN_EPOCH
```

It does not make either missing signature valid.

## Current verified facts

| Source | Current identity or observation |
|---|---|
| DBA main | `8b01bb8988c9180392ac2b06a39e2541fc98b260` |
| Gateway main | `c319001cc1cf9e44d8b3d0b142a025c6c9af1678` |
| Integrations main | `6ed4dadd4693129d3daca0a9a29964a4f7f864e9` |
| Live commercial release | `9bbfce6154d67f4ab50e911b5e49611f5a4a8b57` |
| Failed release candidate | `33bea67bafcd5fe3aabc7e7f48b456dba42aaf76` |
| Historical Receipts | `1661` |
| Valid signatures | `1659` |
| Unverifiable signatures | `2` |
| Chain failures | `0` |
| Restore result | `FAIL_RECEIPT_VERIFICATION` |
| Formal RTO | `NOT_ESTABLISHED` |
| Active CR-01 credentials | `0` in the retained CR-01 report |
| Soak | `NOT_STARTED` |

The live commercial and Sandbox services are active. PostgreSQL 16.14 is
installed. These observations do not establish Production Ready.

## New machine-truth consistency finding

The live `/api/v1/readiness` response currently exposes
`technical_gates.backup_restore_ready=true`, while the canonical CR-01 evidence
records `backup_restore_drill=false` and `BLOCKED_LEDGER_INTEGRITY`. The same
response already keeps `commercial_technical_ready=false` and
`security_tests_pass=false`, but the restore field is stale and can mislead an
Agent consumer.

Any authorized implementation must replace the coarse mutable flag with at
least these distinct, evidence-bound fields:

```text
backup_integrity_pass=true
structural_restore_pass=true
receipt_ledger_integrity_pass=false
full_restore_pass=false
formal_rto_established=false
cr01_status=BLOCKED_LEDGER_INTEGRITY
```

No environment toggle may override an evidence-bound failed gate to `true`.
This correction is part of the proposed single Gateway PR and deployment, not
a separate status-only PR.

## Proposed implementation contract

### 1. Preserve the legacy Receipt rows

The implementation must not update or delete any existing value in:

- `receipt_document`;
- `receipt_hash`;
- `previous_receipt_hash`;
- `receipt_sequence`;
- signature metadata;
- request, response, Tenant, Agent or credential bindings.

The exact legacy outcome remains:

```text
LEGACY_RECEIPTS=1661
LEGACY_SIGNATURES_VALID=1659
LEGACY_SIGNATURES_UNVERIFIABLE_KEY_UNAVAILABLE=2
LEGACY_CHAIN_FAILURES=0
```

### 2. Use additive epoch metadata

The migration candidate is an additive `0005_receipt_ledger_epochs.sql`. It
creates Tenant-owned, forced-RLS epoch and transition metadata without adding
or backfilling a column on historical Receipt rows.

Each Tenant receives:

- one sealed legacy epoch whose inclusive sequence range describes existing
  Receipts;
- one transition record bound to the signed manifest digest and legacy tip;
- at most one `ACTIVE` epoch enforced by a partial unique index;
- a new epoch start sequence equal to the legacy last sequence plus one.

Receipt sequence remains monotonically increasing across a Tenant. Epoch-local
sequence is carried only in the signed v1.1 Receipt document. This preserves
the existing database uniqueness rule while allowing the new epoch genesis to
have `previous_receipt_hash=null`.

For each Tenant, the private manifest must bind the immutable legacy set using
the existing algorithms exactly:

```text
canonicalization=RFC8785
digest=SHA-256
signature=Ed25519

legacy_receipt_set_digest = SHA-256(RFC8785([
  {
    receipt_sequence,
    receipt_hash,
    signature_verification_status,
    signature_verification_reason
  }, ... ordered by receipt_sequence
]))
```

The list order is strict ascending integer `receipt_sequence`; a missing,
duplicate or non-integer sequence rejects the seal. Each private exception
reference maps to the exact Tenant, sequence and `receipt_hash` inside the
private manifest. Public output exposes no such identifier.

`signature_verification_status` is either `VALID` or
`UNVERIFIABLE_KEY_UNAVAILABLE`. The latter is not renamed `INVALID`, does not
break a structurally valid hash link and is not made valid by the manifest.
The manifest also binds the inclusive legacy sequence range, the final legacy
tip and the exact `1659 / 2 / 0` aggregate. This proves what transition input
was sealed; it does not prove the two unavailable signatures.

### 3. Version the Receipt contract

- Receipt v1.0 remains the immutable verification profile for legacy records.
- Receipt v1.1 adds `ledger_epoch_id`, `epoch_sequence`,
  `previous_epoch_tip_hash`, `legacy_receipt_set_digest`,
  `transition_manifest_digest` and `transition_reason`;
- all of those fields are inside the unsigned Receipt document canonicalized
  with RFC 8785 and signed with Ed25519; the signed document hash remains
  SHA-256 over the complete canonical signed document;
- only an epoch genesis may set `previous_receipt_hash=null` after global
  sequence 1;
- a verifier must validate the manifest, Tenant legacy tip, epoch sequence and
  v1.1 signature before accepting the new epoch chain;
- v1.0 and v1.1 verification results remain independently reportable.

### 4. Sign a private transition manifest

The canonical private manifest is a root-owned regular file outside the
immutable application release. It includes ordered Tenant legacy seals, the
  two exact private exception references and their
  `UNVERIFIABLE_KEY_UNAVAILABLE` status, each Tenant's ordered
  `legacy_receipt_set_digest`, target epoch references, source and decision
  references, RFC 8785 canonicalization metadata, a SHA-256 digest and an
  Ed25519 signature.

Public output contains aggregate counts and the manifest digest only. It never
contains Tenant, Agent, credential, request or Receipt identifiers.

### 5. Use a two-phase cutover state machine

The transition has one persisted global state and per-Tenant state. Only the
transition command may move them, using compare-and-set semantics and an
append-only transition event record:

```text
PREPARED
  -> ISOLATED_VALIDATED
  -> WRITES_CLOSED
  -> MIGRATED_INACTIVE
  -> MANIFEST_SIGNED
  -> EPOCHS_ACTIVATING
  -> EPOCHS_ACTIVATED
  -> VERIFIED
  -> WRITES_OPEN
```

1. Build an epoch-aware release with the feature disabled by default.
2. Validate it against an isolated restored database and reach
   `ISOLATED_VALIDATED`.
3. Create and verify the encrypted data backup. Materialize the private
   manifest candidate and close protected writes.
4. Verify no active CR-01 credential and no in-flight protected transaction.
5. Apply the additive migration as `MIGRATED_INACTIVE`; legacy behavior remains
   selected and no epoch exists.
6. Sign and independently verify the private manifest.
7. For each Tenant, lock the legacy chain, verify its set digest and tip, then
   record the seal and create exactly one signed v1.1 genesis atomically.
8. Keep the global state at `EPOCHS_ACTIVATING` until every Tenant has exactly
   one activated epoch. Protected writes remain closed throughout.
9. Verify manifest, anchors, RLS, counts, idempotency, usage, billing and
   cross-Tenant negative cases before `VERIFIED`.
10. Open protected writes only from `VERIFIED`.

Failure before the first epoch genesis may return to the retained application
and legacy writes only after proving `active_epoch_count=0`. Failure after any
epoch genesis enters `PARTIAL_EPOCH_ACTIVATION` or `BLOCKED_LEDGER_INTEGRITY`;
protected writes remain closed and only a separately reviewed epoch-aware
forward repair may continue. No dual-write period is allowed.

### 6. Fail closed after activation

Before epoch activation, the application may return to the retained release
because the migration is additive and inactive. After any Tenant activates a
new epoch, an automatic rollback to an epoch-unaware release is forbidden.
Failure after activation leaves protected writes closed and requires either an
epoch-aware rollback release or a separately reviewed forward repair. It must
not append new Receipts back to the sealed legacy epoch.

## Proposed source allowlist

One implementation PR may modify only these private Gateway paths or narrower
children:

```text
migrations/commercial/0005_receipt_ledger_epochs.sql
schemas/commercial/receipt-v1.1.schema.json
schemas/commercial/ledger-transition-manifest-v1.0.schema.json
src/titmas_commercial/app.py
src/titmas_commercial/config.py
src/titmas_commercial/models.py
src/titmas_commercial/postgres_store.py
src/titmas_commercial/receipts.py
src/titmas_commercial/service.py
src/titmas_commercial/ledger_transition.py
scripts/titmas_commercial_backup.py
scripts/titmas_cr01_reconcile.py
scripts/titmas_cr01_transition.py
scripts/titmas_commercial_release_preflight.py
tests/commercial/
deploy/systemd/titmas-commercial-environment.example
TITMAS-COMMERCIAL-RELIABILITY-CR01-REPORT-v1.0.md
TITMAS-RESTORE-DRILL-v1.0.json
cr01-state.json
machine-status.json
```

The implementation PR must record exact post-change hashes. Any additional
path requires a new Human scope decision. No Sandbox source, Agent evaluation,
provider configuration or public integration repository is in scope.

## Key custody and signing ceremony

- use a dedicated, non-exportable transition-manifest Ed25519 key with a
  domain-separated key ID; do not reuse the lost test key identity or the
  online Receipt key;
- provision it only after authorization in a hardware-backed or managed KMS
  boundary that can produce Ed25519 signatures and an auditable key version;
- a root-owned `0600` filesystem private key is not an allowed fallback;
- the signing request contains only the reviewed manifest digest; customer
  payloads and private identifiers do not leave the bounded ceremony;
- append only the public key, KMS key/version reference, fingerprint and
  lifecycle metadata to the private registry; bind the exact provider
  attestation or independently verified public-key export to the registry;
  public output exposes only the public key/fingerprint and aggregate manifest
  digest;
- the Human Owner confirms the public fingerprint and exact manifest digest,
  never private bytes;
- the encrypted backup contains the signed manifest, signature, public key and
  verification metadata, not exportable private key material;
- restore verification must succeed using only restored public verification
  material. The one-time signing key may be disabled after transition sealing
  without preventing future verification;
- the signing call has a bounded timeout and no blind retry. Before
  `MANIFEST_SIGNED`, an unavailable or indeterminate signer returns to a
  fail-closed state and may reopen legacy writes only after proving
  `active_epoch_count=0`. After a verified manifest signature exists, the
  transition never requires that private key again; all remaining checks use
  the registered public key and exact key-version binding;
- if an approved non-exportable signing boundary is unavailable, or its
  fingerprint/version does not match, stop with `BLOCKED_LEDGER_INTEGRITY`.

The current program explicitly keeps
`NEW_PAID_CLOUD_RESOURCE_AUTHORIZED=false` and
`NEW_PROVIDER_PURCHASE_AUTHORIZED=false`. Option A does not override those
constraints. Before implementation begins, a read-only preflight must confirm
an already approved non-exportable signing boundary. If none exists, no key or
provider resource may be created; the work stops for a separate Human Decision.

The read-only provider-capability assessment is
[`architecture/cr01-signing-boundary-assessment-v1.0.json`](architecture/cr01-signing-boundary-assessment-v1.0.json).
Current official documentation lists RSA and SM2, but not Ed25519, for Baidu
KMS. Alibaba Cloud documents non-exportable, software-protected Ed25519/EdDSA,
but no existing TITMAS KMS instance or key has been confirmed and this packet
does not authorize its purchase or creation. Provider documentation is not
account-inventory evidence.

## Required negative and fault-injection matrix

The machine-readable matrix is
[`architecture/cr01-d03-implementation-readiness-v1.0.json`](architecture/cr01-d03-implementation-readiness-v1.0.json).
It includes manifest substitution, wrong Tenant tip, duplicate active epoch,
partial activation, genesis replay, missing transition key, Receipt downgrade,
RLS isolation, migration replay, billing/idempotency reconciliation,
post-activation rollback and public readiness drift.

All critical cases must fail closed. A test PASS does not authorize the
migration or deployment.

## Proposed cap exception

If Option A is accepted, the maximum exceptional scope is:

```text
MAX_ADDITIONAL_GATEWAY_IMPLEMENTATION_PRS=1
MAX_ADDITIONAL_DATABASE_MIGRATION_EXECUTIONS=1
MAX_ADDITIONAL_APPLICATION_DEPLOYMENT_ATTEMPTS=1
MAX_ADDITIONAL_ISOLATED_RESTORE_REVALIDATIONS=1
SOAK_EXECUTION_AUTHORIZED=false
```

The cap is consumed by an attempted action, not only by success. A failure
stops the gate and requires another Human Decision. CI reruns that do not alter
source do not consume a PR, but new commits after review remain part of the
same one-PR cap.

## Options for Human Decision

### Option A — authorize the bounded implementation

```text
decided_by_ref=zhangbin
CR01-D03=AUTHORIZE_OPTION_C_BOUNDED_IMPLEMENTATION_AND_ONE_CAP_EXCEPTION
LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED=true
MAX_ADDITIONAL_GATEWAY_IMPLEMENTATION_PRS=1
MAX_ADDITIONAL_DATABASE_MIGRATION_EXECUTIONS=1
MAX_ADDITIONAL_APPLICATION_DEPLOYMENT_ATTEMPTS=1
MAX_ADDITIONAL_ISOLATED_RESTORE_REVALIDATIONS=1
DATABASE_MIGRATION_AUTHORIZED=true
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=true
ISOLATED_RESTORE_REVALIDATION_AUTHORIZED=true
CR01_RESTART_AUTHORIZED=true
SOAK_EXECUTION_AUTHORIZED=false
NEW_PAID_CLOUD_RESOURCE_AUTHORIZED=false
NEW_PROVIDER_PURCHASE_AUTHORIZED=false
```

This permits implementation, isolated validation, one migration and one
deployment attempt. It does not declare CR-01 passed. Soak remains closed until
the complete restored runtime, security, reconciliation, latency and headroom
gates pass and are recorded.

### Option B — keep the current hold

```text
decided_by_ref=zhangbin
CR01-D03=REJECT_OR_DEFER_OPTION_C_IMPLEMENTATION
IMPLEMENTATION_AUTHORIZED=false
DATABASE_MIGRATION_AUTHORIZED=false
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=false
CR01_RESTART_AUTHORIZED=false
SOAK_EXECUTION_AUTHORIZED=false
```

### Option C — request revision

The Human Owner may identify exact sections requiring revision. Current gates
remain closed until a later decision.

## Required evidence before Option A becomes executable

- this packet and its machine matrix are merged into DBA main;
- at least one isolated `qwen3.7-max` security review reports zero unresolved
  blockers;
- one additional model lineage performs a scoped adversarial review, or the
  Human Owner explicitly accepts the single-lineage limitation;
- an already approved non-exportable Ed25519 signing boundary is confirmed
  without purchasing or provisioning a new provider resource, otherwise a
  separate Human Decision is required;
- Gateway main, live release and current database migration version are
  reverified at execution time;
- the implementation worktree is a clean checkout of the exact authorized
  base commit;
- no secret, customer payload or private identifier is placed in the PR or
  model context.

## Current authority state

```text
CR01_D03_DECISION_PACKET_READY=true
CR01_D03_DECIDED=false
IMPLEMENTATION_AUTHORIZED=false
DATABASE_MIGRATION_AUTHORIZED=false
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=false
CR01_RESTART_AUTHORIZED=false
SOAK_EXECUTION_AUTHORIZED=false
COMMERCIAL_TECHNICAL_READY=false
PRODUCTION_READY=false
```
