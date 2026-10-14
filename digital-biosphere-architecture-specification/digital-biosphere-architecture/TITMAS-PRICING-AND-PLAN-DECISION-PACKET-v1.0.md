# TITMAS Pricing and Plan Decision Packet v1.0

## Decision status

```text
PACKET_STATUS=DRAFT_INPUT_MODEL
PRICING_ACTIVATION_AUTHORIZED=false
PUBLIC_PRICE_AUTHORIZED=false
REAL_PAYMENT_ACCEPTANCE_AUTHORIZED=false
CURRENCY_DECIDED=false
```

No amount in this packet is a price, offer, quote or invoice.

## Plan capability candidates

| plan | intended Agent scale | capabilities |
|---|---|---|
| `AGENT_TRIAL` | one bounded internal/external evaluation | limited calls, short receipt retention, no SLA |
| `AGENT_DEVELOPER` | small development Agent set | higher quota, SDK/adapters, usage export |
| `AGENT_FLEET` | multiple operational Agents | higher identity and rate limits, longer retention |
| `ENTERPRISE_SOVEREIGN` | separately governed tenant | contractual controls and deployment options subject to Human review |

Each plan defines:

```text
monthly_request_quota
requests_per_minute
agent_identity_limit
tenant_limit
receipt_retention
support_class
sla_eligibility
```

Plan assignment is not permission to core repositories, standard adoption or
certification.

## Cost model inputs

The decision owner needs measured:

- existing server monthly allocated cost;
- PostgreSQL CPU, memory and disk consumption;
- backup storage and transfer;
- bandwidth;
- monitoring and operational labor;
- incident/support allowance;
- optional provider-model cost, if any;
- transaction and tax cost after a payment provider is separately selected.

Current values:

```text
MEASURED_COST_PER_1000_CALLS=UNKNOWN
MEASURED_STORAGE_COST=UNKNOWN
MEASURED_BANDWIDTH_COST=UNKNOWN
MEASURED_OPERATIONS_COST=UNKNOWN
TARGET_GROSS_MARGIN=UNDECIDED
RECOMMENDED_PRICE_RANGE=NOT_ASSESSED
```

## Calculation contract

```text
fully_loaded_monthly_cost =
  infrastructure
  + storage
  + bandwidth
  + model_calls
  + operations
  + support
  + payment_and_tax_allowance

unit_cost_per_1000_successful_calls =
  fully_loaded_monthly_cost
  / successful_protected_calls
  * 1000
```

Failed or `NOT_ASSESSED` calls must remain visible. Whether they are billable
is a future Human commercial decision and cannot be silently inferred.

## Human decisions required

1. currency and tax treatment;
2. included and overage units;
3. treatment of failed and `NOT_ASSESSED` calls;
4. receipt retention by plan;
5. support and SLA eligibility;
6. target gross margin;
7. final price and publication;
8. refund/credit policy.

## Activation gate

Prices remain inactive until technical readiness, external Agent Beta,
measured cost, legal drafts and explicit Human authorization are all present.
