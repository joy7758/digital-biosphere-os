# TITMAS Discount Authority v0.1

## Current authority

```text
AUTOMATIC_DISCOUNT_AUTHORITY=false
AGENT_DISCOUNT_AUTHORITY=false
SALES_DISCOUNT_AUTHORITY=false
HUMAN_OWNER_APPROVAL_REQUIRED=true
```

Any discount proposal must reference an approved base price, term, scope,
cost model, margin impact, expiry, and approving Human. A proposal creates no
quote, contract, credit, refund, or entitlement.

Until a Human-approved pricing baseline exists, no discount can be calculated
or offered. Pilot feedback, contribution, publicity, or case-study consent must
not be exchanged for an undisclosed price change.
