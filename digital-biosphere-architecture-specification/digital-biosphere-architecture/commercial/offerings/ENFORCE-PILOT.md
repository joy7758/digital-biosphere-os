---
offering_id: TITMAS-ENFORCE-PILOT
version: "0.1"
status: CUSTOMER_SPECIFIC_DRAFT_NOT_AVAILABLE
commercial_effect: none
legal_effect: none
---

# TITMAS Enforce Pilot / TITMAS 执行控制试点

## Permanent entry boundary

Enforce is not the default extension of Monitor. It is a separate,
customer-specific decision. No Enforce Pilot exists until all of the following
are recorded for one customer and one action scope:

- written customer authorization;
- approved policy and authorization revisions;
- approved rollback and emergency-stop procedures;
- named Human approval path;
- tested idempotency, nonce, replay protection, expiry, and callback behavior;
- reviewed false-block and `NOT_ASSESSED` handling;
- signed SOW and customer acceptance plan.

## Allowed decisions

`ALLOW`, `BLOCK`, `NEEDS_APPROVAL`, and `NOT_ASSESSED` are technical Gate
results. `NOT_ASSESSED` must enter `BLOCK_OR_HOLD`; it must never be silently
promoted to `ALLOW`.

## Candidate deliverables

- a customer-specific action and target allowlist;
- pre-action Gate integration in a synthetic or isolated environment first;
- Human approval queue and emergency stop;
- Receipt binding and Audit export;
- rollback drill and acceptance report.

## Non-effects

Gate `ALLOW` does not prove the action is correct, safe, lawful, or successful.
Receipt verification does not create authorization. TITMAS does not become the
customer's general authorization platform or execution Runtime.

## Status

```text
CUSTOMER_SPECIFIC_ACTION_SCOPE=false
CUSTOMER_WRITTEN_AUTHORIZATION=false
CUSTOMER_POLICY_APPROVED=false
CUSTOMER_ROLLBACK_APPROVED=false
CUSTOMER_ACCEPTANCE_TEST=NOT_ASSESSED
ENFORCE_PILOT_AVAILABLE=false
```
