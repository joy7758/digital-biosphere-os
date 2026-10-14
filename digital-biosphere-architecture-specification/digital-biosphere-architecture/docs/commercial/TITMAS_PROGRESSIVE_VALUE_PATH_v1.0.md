---
document_id: TITMAS-PROGRESSIVE-VALUE-PATH-1.0
title: TITMAS Progressive Value Path v1.0
title_zh: TITMAS渐进式价值路径v1.0
status: architecture-frozen-not-implemented
---

# TITMAS Progressive Value Path v1.0

```text
DISCOVER -> CONNECT -> OBSERVE -> UNDERSTAND -> MONITOR
  -> ENFORCE -> PROVE -> AUDIT -> EXPAND
```

| stage | customer value | maximum initial control | optional next step | stop option |
|---|---|---|---|---|
| Discover | applicability and non-fit result | none | Connect | abstain |
| Connect | minimum safe input boundary | none/read-only | Observe | delete import and stop |
| Observe | Agent/action inventory and gaps | read-only/event copy | Understand | export and stop |
| Understand | reason codes and limitations | read-only | Monitor | retain explanation |
| Monitor | `WOULD_*` / `NOT_ASSESSED` | enforcement effect `NONE` | Enforce | remain Monitor or exit |
| Enforce | bounded action decision | separate Human authorization | Prove | return to Monitor |
| Prove | portable technical Receipt | issuance scope | Audit | offline verify and stop |
| Audit | integrity/replay with unknowns | read-only audit | Expand | export and stop |
| Expand | deployment decision packet | separate contract/deployment authority | none | do not expand |

Every stage defines `customer_question`, `minimum_input`,
`permission_required`, `data_required`, `value_output`, `explanation`,
`reversibility`, `next_step`, `stop_option` and `known_limitations` in
[`customer-path.json`](../../commercial/entry/customer-path.json).

No customer must complete a later stage to obtain or export the prior stage's
result. A Monitor result cannot be reused as Enforce authorization.
