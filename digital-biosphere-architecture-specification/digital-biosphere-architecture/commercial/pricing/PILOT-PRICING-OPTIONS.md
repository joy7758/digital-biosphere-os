# TITMAS Pilot Pricing Options v0.1

## Decision state

All amounts remain unset until measured costs and Human finance review exist.
These are option structures, not quotations.

| option | construction | included obligations | amount |
|---|---|---|---|
| `CONSERVATIVE` | measured delivery cost + approved risk reserve | one workflow, up to three Agents, standard weekly review | `NOT_ASSESSED` |
| `REFERENCE` | Conservative + approved target margin | adds final findings and ROI-input report | `NOT_ASSESSED` |
| `PREMIUM` | Reference + separately costed deployment/security/support | customer-specific only | `NOT_ASSESSED` |

## Fixed-fee Pilot boundary

The SOW must state the workflow, duration, Agent limit, event/Receipt cap,
retention, support window, exclusions, overage disposition, exit, and acceptance
criteria. Overage does not automatically create a charge or expanded quota.

```text
PRICING_HUMAN_APPROVED=false
PUBLIC_PRICE=false
REQUEST_QUOTE=true
ONLINE_PAYMENT=false
AUTOMATIC_INVOICE=false
```
