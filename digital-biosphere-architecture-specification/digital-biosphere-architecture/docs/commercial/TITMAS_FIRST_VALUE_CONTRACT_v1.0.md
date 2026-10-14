---
document_id: TITMAS-FIRST-VALUE-CONTRACT-1.0
title: TITMAS FirstValueContract v1.0
title_zh: TITMAS首次价值合同v1.0
status: machine-contract-defined-not-implemented
---

# TITMAS FirstValueContract v1.0

`FirstValueContract` declares the smallest inputs, permissions, data classes,
steps, target time, explained result, verification, limitations, reversibility,
deletion and optional next stage for a first-value path.

Required fields are defined by
[`first-value-contract.schema.json`](../../commercial/entry/first-value-contract.schema.json):

```text
contract_id
entry_surface
customer_type
input_type
required_architecture_concepts
required_permissions
required_data_classes
production_write_access_required
core_source_access_required
automatic_enforcement_required
enforce_activation_required
raw_trace_required
estimated_steps
design_target_time_to_first_value
design_target_not_achievement
result_type
result_explanation
machine_reason_codes
verification_available
verification_contract_defined
verification_runtime_available
limitations
reversible
deletion_supported
deletion_request_path_defined
deletion_runtime_available
next_stage
non_claims
```

## Path A — Synthetic demonstration

Input: zero customer data. Permission: zero production permission. Intended
output: a complete synthetic `Observer -> Shadow Gate -> Receipt -> Audit`
demonstration.

## Path B — Public or redacted Trace import

Input: public, synthetic or explicitly authorized redacted metadata. Permission:
read-only import. Intended output: Agent discovery, action classification,
evidence gaps and shadow Gate result.

## Path C — Read-only Monitor connection

Input: customer-authorized minimum metadata. Permission: read-only or event
copy. Intended output: `WOULD_ALLOW`, `WOULD_BLOCK`, `WOULD_NEED_APPROVAL` or
`NOT_ASSESSED` with enforcement effect `NONE`.

Canonical example instances are in
[`first-value-examples.json`](../../commercial/entry/first-value-examples.json).

## Design targets

```text
DESIGN_TARGETS_NOT_PRODUCT_CLAIMS=true
SYNTHETIC_DEMO_TIME_TO_FIRST_VALUE_TARGET=10_MINUTES_OR_LESS
MONITOR_SANDBOX_TIME_TO_FIRST_VALUE_TARGET=30_MINUTES_OR_LESS
PRODUCTION_WRITE_PERMISSION_FOR_FIRST_VALUE=false
AUTOMATIC_ENFORCEMENT_FOR_FIRST_VALUE=false
CORE_SOURCE_ACCESS_FOR_FIRST_VALUE=false
RAW_TRACE_UPLOAD_DEFAULT=false
METADATA_ONLY_ENTRY_AVAILABLE=true
CURRENTLY_ACHIEVED=false
```

These are unmeasured design targets. No current product availability, time-to-
value achievement or customer result is claimed.

`verification_available` and `deletion_supported` describe current runtime
availability and remain `false` in every example. Their companion contract
fields remain `true` because verification and a deletion-request path are
requirements for a future conforming implementation. A contract requirement is
not evidence that the runtime exists.
