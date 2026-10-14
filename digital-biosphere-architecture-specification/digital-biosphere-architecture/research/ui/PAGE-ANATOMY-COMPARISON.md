# Page Anatomy Comparison

Status: `PRIVATE_RESEARCH_ONLY`

This comparison records reusable information-architecture patterns, not
third-party visual assets or source code.

| Surface | Repeated market pattern | TITMAS original response | Explicit non-copy boundary |
|---|---|---|---|
| Global shell | product switcher, workspace context, documentation and support | stable `TITMAS Console` shell with workspace and mode always visible | no vendor-specific menu names, icons or header geometry |
| Overview | 4–8 summary cards plus activity and limits | evidence-first cards for mode, observed actions, shadow blocks, Receipts, verification and quota | no cloned KPI order, card silhouette or gradients |
| Resource list | dense table, saved filters, bulk export, row detail | Agent-readable column contract with machine reason codes and bilingual human labels | no copied table styling or filter wording |
| Event investigation | summary, timeline, related policy/identity/evidence | immutable Gate timeline ending in Receipt and Audit references | no borrowed trace graph or investigation narrative |
| Policy | editor, version, deployment state and test | reference/version display plus customer configuration only; no new general policy language | no Cerbos/Permit/Cisco policy syntax or editor clone |
| Approval | queue, requester, scope, expiry, reviewer and outcome | separate Human authorization record; approval cannot rewrite old decision | no competitor workflow naming or visual composition |
| Receipt | status, signature, decision, action result and download | technical execution receipt with `PASS/FAIL/NOT_ASSESSED/UNVERIFIABLE_KEY_UNAVAILABLE` | no certification badge, seal or legal-certificate presentation |
| Audit | actor/authority chain, replay, retention and export | offline-verifiable bundle, missing-evidence state and limitations always visible | no copied SIEM dashboard or vendor export experience |
| Usage | plan, quota, history and export | workspace-scoped technical usage separated from billing units | no copied price cards or metering labels |
| Settings | keys, retention, data region, support and security | one-time secret display, revocation, region and explicit private-deployment boundaries | no generic cloud IAM clone |
| Empty/error | guided next step and bounded support path | fail-closed state, stable reason code, recovery link and no false success | no copied illustrations or playful error language |

## Original hierarchy

```text
TITMAS Console
  Workspace context + Mode boundary
    Overview
    Agents and Integrations
    Gate and Approvals
    Receipts and Audit
    Health and Usage
    Deployments, Settings and Support
```

TITMAS preserves a short navigation depth. A high-impact action always exposes
its authorization, policy revision, evidence reference, decision, receipt and
limitations without requiring a user to infer them from separate dashboards.
