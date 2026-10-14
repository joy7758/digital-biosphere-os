---
document_id: TITMAS-COMMERCIAL-C01
title: Low-Friction Entry and Progressive Value Realization
title_zh: 低门槛进入与渐进式价值原则
status: frozen-commercial-constitution
display_order: 1
---

# C-01 — Low-Friction Entry and Progressive Value Realization

## Normative rule

The customer must be able to obtain a real, explainable and verifiable initial
result without full TITMAS theory, private-core source, production write access,
automatic enforcement, unnecessary raw data, complex deployment or a long-term
commercial commitment.

The initial result must declare inputs, permissions, data classes, reason codes,
verification, limitations, reversibility, deletion path and the optional next
stage. It may be `NOT_ASSESSED`; it must never manufacture `ALLOW`, Truth,
Authorization, product availability or production evidence.

## Required entry qualities

1. Low cognitive entry: the Human homepage and first console flow start from
   Agents, actions, risk, evidence gaps and shadow outcomes.
2. Low integration entry: synthetic, public/redacted import and read-only event
   copy are valid first paths.
3. Low data-risk entry: raw private Trace upload defaults to false.
4. Low control-risk entry: first value has no production write or enforcement
   effect.
5. Progressive value: every stage returns its own explained result before an
   upgrade is requested.

## Redesign rule

Any entry requiring full architecture understanding, a long-term contract,
complete private Trace, production write access, production blocking authority,
complex Kubernetes, an annual purchase, core source access or all-Agent
integration before first value fails closed:

```text
TITMAS_CUSTOMER_ENTRY_CHECK_RESULT=FAIL
CUSTOMER_ENTRY_TOO_HIGH=true
REDESIGN_REQUIRED=true
```

The canonical machine rule is
[`c01-low-friction-entry.json`](../../commercial/constitution/c01-low-friction-entry.json).

## Non-effects

This principle changes commercial architecture and priority only. It does not
implement Observer, Monitor, Enforce, Console, Trace storage, Health, Gate,
Receipt, Audit, production services, customers, contracts or payment.
