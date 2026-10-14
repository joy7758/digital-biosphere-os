# TITMAS Operations Runbook v1.0

## Current state

```text
COMMERCIAL_SERVICE_DEPLOYED=true
SANDBOX_PREVIEW_SERVICE_ACTIVE=true
POSTGRESQL_INSTALLED=true
RUNBOOK_VALIDATED_BY_DRILL=false
RUNBOOK_PARTIALLY_VALIDATED=true
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY_FAILED_RETAINED
D04_FINAL_STATUS=CLOSED_FAILED_RETAINED
D04_FURTHER_CANARY_RETRIES_AUTHORIZED=false
PRODUCTION_READY=false
```

This runbook is the execution contract for the deployed bounded commercial
candidate. Deployment does not mean Production Candidate validation or
Production Ready. The CR-01 recovery gate remains blocked and its D04 internal
clean-ledger route is closed failed-retained.

## Baseline environment

Last reconciled on `2026-07-31T17:01:11+08:00`:

```text
host=existing-baidu-server
os=Ubuntu 24.04
cpu=2
memory=7.7 GiB
root_disk_free=83 GiB
sandbox_service=titmas-sandbox-preview.service active
sandbox_release=33a10e37d9582f240c518a0b65fb59f12dd3527c
commercial_service=titmas-commercial-candidate.service active
commercial_release=9bbfce6154d67f4ab50e911b5e49611f5a4a8b57
commercial_rollback_release=5b13693f80aae98a0b3d53d2f4f0187399904a4a
postgresql=16 installed candidate
api_v1_status=deployed_bounded_not_production_ready
```

The attempted CR-01 candidate
`33bea67bafcd5fe3aabc7e7f48b456dba42aaf76` failed package activation because
runtime Schemas were absent from its final immutable release path. Automatic
rollback restored the retained release in about 30 seconds. No second
activation is authorized under the exhausted CR-01 cap.

## Immutable release procedure

1. require an exact merged commit;
2. build in a clean checkout;
3. run tests, scans, SBOM and package verification;
4. produce a manifest with file hashes and dependency lock;
5. copy into `/srv/titmas-commercial/releases/<commit>/`;
6. create an isolated virtual environment;
7. perform migration dry-run and backup;
8. validate configuration without exposing secret values;
9. start a loopback canary on a non-public port;
10. run health, readiness, tenant-isolation and receipt tests;
11. update the Nginx `/api/v1` route only;
12. verify public machine endpoints from independent clients;
13. retain the previous release and rollback instructions.

```text
ZERO_DIRECT_SERVER_SOURCE_EDITING=true
ROLLBACK_TARGET_REQUIRED=true
SANDBOX_ROUTE_MUST_REMAIN_HEALTHY=true
```

## Configuration and secret locations

- service unit: `/etc/systemd/system/titmas-commercial-api.service`;
- environment: root-owned file outside the release;
- receipt private key: separate root-owned file, mode `0600`;
- PostgreSQL credentials: root/service-readable secret, not Git;
- public key and key ID: generated public-safe release artifact.

No command may print credential, database password or private key.

## Database migration

Before migration:

1. verify supported PostgreSQL major/minor;
2. create encrypted backup;
3. validate backup integrity;
4. run migration in a disposable database;
5. record migration hash and expected schema version.

Production-candidate migration runs under a dedicated role. Application
credentials must not own the schema.

## Health model

- liveness: process can serve a minimal response;
- readiness: database, credential registry, signer and migration version are
  usable;
- dependency health: structured internal diagnostic, not public secret detail.

The public status returns only bounded aggregate maturity and health.

## Monitoring

Collect tenant-safe metrics:

- request and outcome counts;
- latency;
- authentication, scope, quota and rate-limit failures;
- database and receipt failures;
- usage-ledger and billing-ledger lag;
- backup age and disk usage.

Never use raw tenant, Agent or credential identifiers as high-cardinality
public labels.

## Alert routing

| severity | example | immediate action |
|---|---|---|
| `SEV-1` | cross-tenant access, key exposure, receipt forgery | stop affected service, revoke, preserve evidence, Human notify |
| `SEV-2` | sustained unavailability, database loss risk | fail closed, rollback or restore |
| `SEV-3` | degraded latency, ledger lag | limit traffic and investigate |
| `SEV-4` | non-urgent warning | schedule correction |

## Rollback

Application rollback:

1. remove or disable only `/api/v1` Nginx route;
2. switch release symlink to the last verified commit;
3. restart commercial service;
4. verify Sandbox and public site unaffected.

Database rollback does not run destructive down migrations automatically.
Restore into a separate database, verify, then switch after a Human safety
check if data loss is possible.

## Backup and restore

Backup scope:

- PostgreSQL metadata and ledgers;
- configuration with secrets separately encrypted;
- public-key metadata;
- audit and release manifests.

Plaintext tokens are never backed up.

Restore evidence must record measured RPO and RTO. Design targets cannot be
reported as measured results.

The CR-01 isolated restore measured a 14-second RPO and completed structural
restore plus verification work in 1.095 seconds. Formal RTO is not established
because two of 1,661 historical synthetic Receipt signatures could not be
verified. Counts, schema, audit tip, 12 forced-RLS tables and all Receipt chain
links matched, but structural restoration is not full recovery.

The historical records must not be deleted, rewritten, re-signed, allowlisted,
upgraded or migrated. D04 retained all three Canary failures and permanently
closed the internal clean-ledger route. CR01-D02 and its Option C are historical
design evidence only and no longer form a current implementation route.

Future production use requires a separately authorized clean-genesis ledger
after `PAID_BETA_LAUNCH_AUTHORIZED`; it must not inherit the legacy chain,
sequence or signature exceptions. Until then, code, migration, deployment,
restore re-execution, soak and another Canary remain unauthorized.

## Synthetic drills required

1. application process failure;
2. database unavailable;
3. malformed credential registry;
4. receipt signer unavailable;
5. backup restore into an isolated database.

All drills use synthetic tenants only until customer-production-data
authorization exists.

## Stop conditions

Stop and rollback on secret exposure, cross-tenant access, receipt forgery,
billing double count, unexpected raw payload persistence, unrecoverable backup,
unbounded cost or any need for an unauthorized DNS/certificate change.
