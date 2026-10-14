---
document_id: TITMAS-OBSERVER-ENTRY-LAYER-1.0
title: TITMAS Observer Entry Layer v1.0
title_zh: TITMAS智能体观察入口层v1.0
status: architecture-defined-runtime-not-implemented
---

# TITMAS Observer Entry Layer v1.0

```text
ENTRY_LAYER_ID=TITMAS_OBSERVER
NAME=TITMAS Observer
NAME_ZH=TITMAS智能体观察入口
TYPE=CUSTOMER_ENTRY_LAYER
IS_PRODUCT=false
PUBLIC_PRODUCT_COUNT_EFFECT=0
OBSERVATION_ONLY=true
EVIDENCE_TRUTH=false
AUTHORITY_EFFECT=NONE
ENFORCEMENT_EFFECT=NONE
```

Observer helps a customer discover which Agents exist, what actions are being
attempted, which actions have external side effects, where identity/evidence/
authorization/approval is missing, and what Gate might have decided in shadow
mode.

Observer is a shared entry layer over Gate, Receipt, Audit and Health. It is not
a fifth product, Trace semantic owner, Evidence semantic owner, observability
platform, permission mutator or truth authority. It does not replace LangSmith,
AgentLoop or OpenTelemetry and may consume their authorized exports only through
bounded adapters.

```text
OBSERVER_RUNTIME_IMPLEMENTED=false
NEW_TRACE_PLATFORM_CREATED=false
NEW_EVIDENCE_CORE_CREATED=false
AUTOMATIC_ACTION_BLOCKING=false
```

Canonical machine classification:
[`entry-layer.json`](../../commercial/entry/entry-layer.json).
