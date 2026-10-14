# TITMAS Commercial CR-01 D02 Human Decision Record v1.0

## Decision

```text
decision_id=CR01-D02
decision=HOLD_AND_DESIGN_IMMUTABLE_TEST_RECEIPT_QUARANTINE_OR_NEW_CLEAN_LEDGER_MIGRATION
decided_by_ref=zhangbin
decided_at=2026-07-31T18:44:30+08:00
decision_status=ACCEPTED
```

The Human Owner accepts a bounded design phase for the two historical
synthetic Receipts whose `postgres-integration-key` public key was never
retained. This decision does not change their verification result and does not
authorize implementation.

## Accepted scope

- retain the complete 1,661-Receipt historical ledger without deletion,
  rewriting, re-signing or allowlisting;
- compare immutable exception-manifest, quarantine and clean-ledger designs;
- define tenant-scoped epoch, manifest, restore, rollback and verification
  contracts;
- use independent Agent review as advisory design evidence;
- prepare a later Human Decision on implementation and exhausted deployment
  caps.

## Closed scope

```text
IMPLEMENTATION_AUTHORIZED=false
GATEWAY_CODE_CHANGE_AUTHORIZED=false
DATABASE_MIGRATION_AUTHORIZED=false
SECOND_DEPLOYMENT_RETRY_AUTHORIZED=false
SOAK_EXECUTION_AUTHORIZED=false
CR01_RESTART_AUTHORIZED=false
PRODUCTION_READY=false
```

No Runtime, credential, Tenant, Receipt, database row, signing key, Release or
deployment is created or changed by this decision.

## Retained facts

| Fact | Retained value |
|---|---|
| Historical Receipts checked | `1661` |
| Signatures valid | `1659` |
| Signatures unverifiable | `2` |
| Chain failures | `0` |
| Missing key reference | `postgres-integration-key` |
| Backup integrity | `PASS` |
| Structural restore | `PASS` |
| Full restore | `FAIL_RECEIPT_VERIFICATION` |
| RTO | `NOT_ESTABLISHED` |
| CR-01 | `BLOCKED_LEDGER_INTEGRITY` |

## Advisory review

Three separate `qwen3.7-max` review sessions examined the design as a
reliability architect, adversarial security reviewer and Agent customer. All
selected the combined option:

```text
OPTION_C=IMMUTABLE_EXCEPTION_MANIFEST_PLUS_NEW_CLEAN_LEDGER_EPOCH
AGENT_REVIEW_CONSENSUS=3_OF_3
OPTION_C_IMPLEMENTATION_AUTHORIZED=false
```

The reviews are recommendations, not Authority. Their common requirement is
to leave the legacy ledger untouched, sign a transition manifest, bind each
new tenant epoch to the corresponding legacy chain tip, and continue to expose
the two legacy signatures as unverifiable.

## Next decision

```text
NEXT_HUMAN_DECISION=CR01-D03_AUTHORIZE_OR_REJECT_OPTION_C_IMPLEMENTATION_AND_CAP_EXCEPTION
```

CR01-D03 must separately decide the implementation scope, private Gateway PR
cap, application redeployment cap, migration execution, rollback drill and
whether CR-01 may resume. Until then all remain closed.

## Authority boundary

```text
DECISION_NE_EXECUTION=true
DESIGN_NE_IMPLEMENTATION=true
QUARANTINE_NE_ALLOWLIST=true
LEGACY_ANCHOR_NE_LEGACY_SIGNATURE_VERIFICATION=true
EVIDENCE_NE_TRUTH=true
VERIFICATION_NE_AUTHORIZATION=true
```
