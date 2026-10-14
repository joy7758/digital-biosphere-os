# TITMAS Pricing Research v0.1 / TITMAS 定价研究 v0.1

## Status

```text
PRICING_RESEARCH_COMPLETE=PARTIAL_INTERNAL_MODEL
PUBLIC_PRICE=false
REQUEST_QUOTE=true
PRICING_HUMAN_APPROVED=false
CURRENCY_CANDIDATE=CNY
REAL_PAYMENT_ACCEPTANCE_AUTHORIZED=false
```

The preferred first paid unit is a fixed-fee, bounded Monitor Pilot, not an
unbounded usage plan. Usage remains visible for capacity, acceptance, and future
renewal analysis, but it is not silently converted into a bill.

## Required cost evidence

- engineering and integration labor;
- China-region cloud allocation;
- storage, backup, transfer, and Audit retention;
- optional model API usage;
- support and incident allowance;
- deployment and security review;
- travel, tax, invoicing, and risk reserve;
- target gross margin selected by the Human Owner.

No reliable measured values are currently recorded. Therefore this package
defines formulas and decision fields, not a price or quote.

## Candidate structures

1. `CONSERVATIVE`: recovers measured delivery cost plus approved risk reserve;
2. `REFERENCE`: adds an approved target margin and standard support allowance;
3. `PREMIUM`: adds customer-specific deployment, extended support, and security
   review only when those obligations are explicitly scoped.

## Non-equivalence

Plan assignment is not permission, a source licence, standard adoption,
certification, SLA, or production authority. Pricing approval is not payment
acceptance or delivery authorization.
