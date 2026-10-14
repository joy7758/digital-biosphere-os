# TITMAS Enterprise Metering Model v0.1

Metering records technical usage by Workspace and time. It supports capacity,
Audit, export, and future billing review without exposing customer content.

## Dimensions

- active Agent identities;
- Gate and Monitor evaluations;
- Receipts created and verified;
- Audit storage and retention days;
- API requests and exports;
- support hours and deployment work.

## Required record fields

`tenant_ref`, `workspace_ref`, `meter`, `period_start`, `period_end`, `quantity`,
`unit`, `source_reference`, `verification_status`, and `limitations`.

## Boundaries

- usage record is not an invoice;
- failed and `NOT_ASSESSED` treatment requires Human pricing decision;
- metering must not include raw customer content;
- quota is a technical control, not commercial authority;
- disputed usage remains visible and cannot be overwritten silently.

No Enterprise metering price, allowance, or SLA is currently approved.
