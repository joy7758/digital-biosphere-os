---
document_id: TITMAS-CUSTOMER-ENTRY-ACCEPTANCE-1.0
title: TITMAS Customer Entry Acceptance v1.0
title_zh: TITMAS客户入口验收v1.0
status: document-and-machine-contract-gate
---

# TITMAS Customer Entry Acceptance v1.0

## Check contract

`TITMAS_CUSTOMER_ENTRY_CHECK` evaluates low cognitive, integration, data and
control risk entry; first value before enforcement; Monitor before Enforce;
explanation and proof before configuration/purchase expansion; Observer
classification; Human/Agent entry; data minimization; no production permission;
reversibility and deletion.

Results are `PASS`, `FAIL` or `NOT_ASSESSED`. The current `PASS` applies only to
the document and machine-contract scope. Implementation and measured customer
experience remain `NOT_ASSESSED`.

## Acceptance scenarios

| ID | expected | requirement |
|---|---|---|
| T01 | PASS | synthetic Demo does not require DBA/DBOS/EEOAP understanding |
| T02 | PASS | first value requires no production write permission |
| T03 | PASS | first value requires no Enforce |
| T04 | PASS | raw private Trace upload is not the default |
| T05 | PASS | Observer is absent from `products[]` |
| T06 | PASS | public product count remains four |
| T07 | PASS | Human entry is defined |
| T08 | PASS | Agent machine entry is defined |
| T09 | PASS | Monitor has no blocking effect |
| T10 | PASS | Enforce requires separate Human authorization |
| T11 | PASS | exit, key revocation and deletion request are defined |
| T12 | PASS | first result includes explanation and limitations |
| T13 | PASS | simplicity preserves machine reason codes |
| T14 | PASS | simplicity does not change Receipt, Gate or Evidence semantics |
| T15 | PASS | no Trace platform or fifth product is created |

Machine tests live in
`TITMAS/conformance/tests/test_commercial_c01_entry.py` and validate the
canonical JSON plus cross-document invariants.

## Required gate outputs

```text
TITMAS_DIRECTION_CHECK_RESULT=PASS
TITMAS_CUSTOMER_ENTRY_CHECK_RESULT=PASS
COMMERCIAL_CONSTITUTION_VALID=PASS
C01_MACHINE_CONTRACT_VALID=PASS
FIRST_VALUE_SCHEMA_VALID=PASS
ENTRY_REASON_CODES_VALID=PASS
PRODUCT_COUNT=4
OBSERVER_IS_PRODUCT=false
CROSS_DOCUMENT_CONSISTENCY=PASS
```

## Scope non-effects

```text
CORE_CODE_CHANGED=false
RUNTIME_CHANGED=false
DATABASE_CHANGED=false
WEBSITE_CHANGED=false
OWNER_MAP_CHANGED=false
OWNER_RESOLVER_CHANGED=false
PR_113_CHANGED=false
```
