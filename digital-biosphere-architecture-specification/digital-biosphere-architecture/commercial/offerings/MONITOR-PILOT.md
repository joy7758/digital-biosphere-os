---
offering_id: TITMAS-MONITOR-PILOT
version: "0.1"
status: INTERNAL_DELIVERY_DRAFT_NOT_AVAILABLE
primary_paid_offering_candidate: true
commercial_effect: none
legal_effect: none
---

# TITMAS Monitor Pilot / TITMAS 监测试点

## Candidate scope

- one named critical software-delivery workflow;
- one to three Agent identities;
- up to 30 calendar days;
- bounded event and Receipt volumes fixed in the SOW;
- synthetic first value before any authorized customer metadata;
- weekly Human review and a final gap report.

## Delivery model

```text
MODE=MONITOR
ENFORCEMENT_EFFECT=NONE
```

The Pilot may compute `WOULD_ALLOW`, `WOULD_BLOCK`,
`WOULD_NEED_APPROVAL`, or `NOT_ASSESSED`. It must not block, approve, execute,
merge, release, write data, or send externally on the customer's behalf.

## Candidate deliverables

- Workspace and Agent metadata registration performed manually;
- scoped, expiring credential issued by an authorized Human operator;
- one bounded integration and baseline;
- Shadow Gate results, technical Receipts, and an Audit export;
- weekly finding review and final limitations/ROI-input report;
- credential revocation and exit/data-return record.

## Customer responsibilities

The customer owns business legality, action authority, supplied data rights,
integration safety, operator availability, and final decisions. It must not send
personal, production, confidential, or regulated data unless separately
authorized in writing.

## Acceptance

Acceptance is limited to agreed delivery artifacts, traceability, exportability,
and declared non-blocking behavior. It does not establish risk elimination,
model correctness, production readiness, adoption, certification, or legal
compliance.

## Stop conditions

Stop on secret exposure, cross-tenant access, unexpected raw payload
persistence, Receipt forgery, double counting, unauthorized action effect,
unrecoverable backup, or scope expansion.

## Commercial boundary

```text
PUBLIC_PRICE=false
FIXED_FEE_PRIVATE_PILOT_CANDIDATE=true
REQUEST_QUOTE=true
DELIVERY_AUTHORIZED=false
SIGNED_SOW_REQUIRED=true
HUMAN_LEGAL_REVIEW_REQUIRED=true
```
