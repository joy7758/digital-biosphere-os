---
document_id: TITMAS-COMMERCIAL-CONSTITUTION-1.0
title: TITMAS Commercial Constitution v1.0
title_zh: TITMAS商业宪法v1.0
status: frozen-commercial-constitution
decision_reference: TITMAS-COMMERCIAL-CONSTITUTION-C01-LOW-FRICTION-ENTRY-D29-INTEGRATION
implementation_authorized: false
public_launch_authorized: false
---

# TITMAS Commercial Constitution v1.0（TITMAS商业宪法v1.0）

## Constitutional effect

This Constitution governs TITMAS commercial architecture, product priority,
customer entry and D29 interpretation. It does not implement or launch a
commercial service.

```text
COMMERCIAL_CONSTITUTION_STATUS=C01_FROZEN
COMMERCIAL_PRINCIPLE_C01=LOW_FRICTION_ENTRY_AND_PROGRESSIVE_VALUE
C01_IS_FIRST_COMMERCIAL_PRINCIPLE=true
ONE_PRIVATE_PLATFORM=true
ONE_SHARED_CORE=true
PUBLIC_PRODUCT_COUNT=4
PUBLIC_PRODUCTS=GATE_RECEIPT_AUDIT_HEALTH
OBSERVER_IS_ENTRY_LAYER=true
OBSERVER_IS_FIFTH_PRODUCT=false
```

## C-01 — Low-Friction Entry and Progressive Value Realization

中文：低门槛进入与渐进式价值原则。

TITMAS must provide verifiable initial value before requiring customers to
understand the full architecture, surrender production control, disclose
unnecessary sensitive data, deploy complex infrastructure, or commit to a
high-cost commercial arrangement.

TITMAS必须在要求客户理解完整架构、交出生产控制权、披露不必要的敏感数据、部署复杂基础设施
或承担高成本商业承诺之前，先提供一个真实、可解释、可验证的初始价值结果。

> 先让客户看见价值，再要求客户承担集成和控制成本。

```text
FIRST_VALUE_BEFORE_ENFORCEMENT=true
MONITOR_BEFORE_ENFORCE=true
MINIMUM_NECESSARY_DATA=true
REVERSIBLE_ENTRY=true
CLEAR_UPGRADE_PATH=true
EXPLANATION_BEFORE_CONFIGURATION=true
PROOF_BEFORE_PURCHASE_EXPANSION=true
FIRST_VALUE_WITHOUT_CORE_SOURCE_ACCESS=true
FIRST_VALUE_WITHOUT_PRODUCTION_WRITE_PERMISSION=true
FIRST_VALUE_WITHOUT_AUTOMATIC_ENFORCEMENT=true
```

Lower friction never weakens safety, authorization or evidence:

```text
LOWER_ENTRY_NE_LOWER_SAFETY=true
LOWER_ENTRY_NE_DEFAULT_ALLOW=true
LOWER_ENTRY_NE_WEAK_AUTHORIZATION=true
LOWER_ENTRY_NE_UNVERIFIED_EVIDENCE=true
LOWER_ENTRY_NE_PUBLIC_CORE_SOURCE=true
LOWER_ENTRY_NE_UNNECESSARY_RAW_DATA_COLLECTION=true
LOWER_ENTRY_NE_AUTOMATIC_PRODUCTION_ACCESS=true
SIMPLICITY_DOES_NOT_WEAKEN_AUTHORITY=true
SIMPLICITY_DOES_NOT_WEAKEN_EVIDENCE=true
SIMPLICITY_DOES_NOT_HIDE_LIMITATIONS=true
SIMPLICITY_DOES_NOT_REMOVE_HUMAN_AUTHORIZATION=true
```

The bounded drift contract also freezes no new Trace platform, Runtime,
control plane, truth source or duplicate verification; no public core,
customer-data or secret disclosure; no automatic contact, enforcement or
production deployment; and no P0-10 or D04 reopening.

## Supporting principles

Only C-01 is frozen by this decision. C-02 through C-10 are ordered supporting
candidates whose source and stable-ID status require separate verification;
their inclusion here does not silently freeze or renumber them.

| order | ID | principle | binding interpretation |
|---:|---|---|---|
| 2 | `TITMAS-COMMERCIAL-C02` | Closed core, open discovery and proof | commercial access is not a source licence |
| 3 | `TITMAS-COMMERCIAL-C03` | One core, multiple product surfaces | Gate, Receipt, Audit and Health do not own separate cores |
| 4 | `TITMAS-COMMERCIAL-C04` | Monitor before Enforce | shadow results have no enforcement or permission effect |
| 5 | `TITMAS-COMMERCIAL-C05` | Agent is the operational customer | the Human or organization remains contracting principal |
| 6 | `TITMAS-COMMERCIAL-C06` | Evidence first and no overclaim | Evidence is not Truth; Verification is not Authorization |
| 7 | `TITMAS-COMMERCIAL-C07` | Customer data minimization | raw Trace and customer payload retention are not defaults |
| 8 | `TITMAS-COMMERCIAL-C08` | Exit, revocation and deletion | exit does not rewrite immutable retained history |
| 9 | `TITMAS-COMMERCIAL-C09` | Design-partner first | a pilot is not adoption or production |
| 10 | `TITMAS-COMMERCIAL-C10` | Real external signals drive evolution | synthetic results are not customer evidence |

The canonical machine ordering and stable IDs are in
[`commercial-constitution-index.json`](../../commercial/constitution/commercial-constitution-index.json).

## Progressive commercial path

```text
DISCOVER -> CONNECT -> OBSERVE -> UNDERSTAND -> MONITOR
  -> ENFORCE -> PROVE -> AUDIT -> EXPAND
```

No later stage is required to receive the prior stage's result. Enforce,
contract, payment and private deployment retain separate Human gates.

## Pre-development Agent recommendation

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=BOUNDED_SYNTHETIC_OR_READ_ONLY_CUSTOMER_ENTRY_EVALUATION
NOT_RECOMMENDED_AS=PRODUCTION_ENFORCEMENT_OR_AVAILABLE_COMMERCIAL_OFFERING
```

The original non-recommendation reasons were high cognitive/integration cost,
unclear first value, unnecessary data/permission risk, and the possibility of
mistaking Monitor for Enforce. C-01 corrects those architecture defects with
Observer, three FirstValue paths, explicit reason codes, reversibility and an
entry check. Implementation, measured time-to-value, external customer use,
production recovery and commercial readiness remain unresolved.

## Non-effects

```text
IMPLEMENTATION_AUTHORIZED=false
CONSOLE_IMPLEMENTATION_AUTHORIZED=false
WEBSITE_IMPLEMENTATION_AUTHORIZED=false
OBSERVER_RUNTIME_IMPLEMENTED=false
PUBLIC_LAUNCH_AUTHORIZED=false
CUSTOMER_CREATED=false
CONTACT_CUSTOMER=false
CONTRACT_SIGNED=false
PAYMENT_COLLECTED=false
PUBLIC_CORE_SOURCE=false
```
