# TITMAS Product Portfolio v0.1

Status: `FOUR_PRODUCT_PORTFOLIO_FROZEN`

TITMAS exposes exactly four horizontal products. They are public product
contracts over one private platform, not four independent cores.

## C-01 entry layer

`TITMAS Observer` is the shared entry layer before the four products. It helps a
customer discover Agents, actions, risks, evidence gaps and non-enforcing shadow
results. It is recorded under `entry_layers[]`, never `products[]`.

```text
ENTRY_LAYER_ID=TITMAS_OBSERVER
OBSERVER_IS_PRODUCT=false
PUBLIC_PRODUCT_COUNT_EFFECT=0
FIRST_VALUE_BEFORE_ENFORCEMENT=true
MONITOR_BEFORE_ENFORCE=true
```

Every product machine record now declares `entry_path`, `first_value`,
`required_permissions`, `required_data`, `monitor_available`,
`enforce_available`, `reversibility`, `deletion_path` and
`not_recommended_when`. These are architecture contracts; availability remains
separate.

## TITMAS Gate — TITMAS 行动闸门

Customer question: may this Agent perform the declared critical action now?

Outputs: `ALLOW`, `BLOCK`, `NEEDS_APPROVAL`, `NOT_ASSESSED`.

```text
GATE_RESULT_NE_TRUTH=true
GATE_RESULT_NE_CERTIFICATION=true
ALLOW_NE_RESULT_CORRECTNESS=true
BLOCK_NE_MALICIOUS_AGENT=true
```

## TITMAS Receipt — TITMAS 执行回执

Customer question: when and under which declared objects, rules and
authorization did a bounded execution occur?

```text
RECEIPT_PROVES_BOUNDED_RECORDED_EXECUTION=true
RECEIPT_NE_TRUTH=true
RECEIPT_NE_LEGALITY=true
RECEIPT_NE_CERTIFICATION=true
```

## TITMAS Audit — TITMAS 证据审计

Customer question: can the execution, approval, evidence and final recorded
state be replayed after a dispute?

```text
AUDIT_REPLAY_NE_REAL_WORLD_TRUTH=true
AUDIT_RESULT_NE_CERTIFICATION=true
```

## TITMAS Health — TITMAS 智能体健康

Customer question: is the Agent project becoming unstable, incomplete or
difficult to review over time?

```text
HEALTH_NE_MEDICAL_DIAGNOSIS=true
HEALTH_NE_CREDIT_SCORE=true
HEALTH_NE_CERTIFICATION=true
HEALTH_NE_AUTOMATIC_PERMISSION_CHANGE=true
```

## Portfolio guard

```text
PUBLIC_PRODUCT_COUNT=4
PUBLIC_PRODUCT_IDS=TITMAS_GATE,TITMAS_RECEIPT,TITMAS_AUDIT,TITMAS_HEALTH
FIFTH_PRODUCT_AUTHORIZED=false
PRIVATE_CORE_SOURCE_PUBLIC=false
```

Adding a fifth product, widening a product into a new core, or moving PACVP out
of Gate requires a new Human Decision.

Canonical machine catalog:
[`product-catalog.internal.json`](../portfolio/product-catalog.internal.json).
