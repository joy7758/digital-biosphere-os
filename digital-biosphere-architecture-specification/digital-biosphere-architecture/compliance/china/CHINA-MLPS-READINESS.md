# China MLPS Readiness

Status: `HUMAN_SECURITY_AND_LEGAL_REVIEW_REQUIRED`

Current standard record: GB/T 22239-2019, status `现行`, published by the
State Administration for Market Regulation and Standardization Administration:
https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=BAFB47E8874764186BDB7865E8344DAF

```text
MLPS_LEVEL=NOT_ASSESSED
MLPS_FILING_COMPLETE=false
MLPS_ASSESSMENT_COMPLETE=false
```

## Prepared technical inputs

- candidate system boundary: public website, managed private pilot, customer
  VPC and customer on-prem are distinct systems;
- assets: tenant/workspace metadata, scoped-key verifier, policy and
  authorization references, Gate decisions, Receipts, Audit bundles and usage;
- trust boundaries: public ingress, application, PostgreSQL, signer, offline
  administration and customer adapter;
- initial controls: tenant isolation, scope, expiry/revocation, replay,
  idempotency, tamper detection, backup/restore, audit and incident response;
- data-minimization default: no raw customer payload persistence.

## Missing before specialist consultation

- authoritative deployment topology and operating entity;
- system grading rationale and business-impact analysis;
- asset inventory, account/role matrix and network zones;
- measured vulnerability, penetration, backup/restore and incident-drill evidence;
- supplier/cloud responsibilities and maintenance model;
- selected cryptography profile and key-management boundary.

No MLPS level or compliance claim may appear on the website or sales material
until the required specialist and authority process is complete.
