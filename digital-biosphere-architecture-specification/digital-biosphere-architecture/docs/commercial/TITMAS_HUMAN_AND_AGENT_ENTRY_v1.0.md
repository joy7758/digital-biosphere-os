---
document_id: TITMAS-HUMAN-AND-AGENT-ENTRY-1.0
title: TITMAS Human and Agent Entry v1.0
title_zh: TITMAS人类与智能体双入口v1.0
status: architecture-defined-not-implemented
---

# TITMAS Human and Agent Entry v1.0

## Human entry

The first Human surface must answer:

- What Agents do I have?
- What did they do or attempt?
- Which actions need attention?
- What would Gate do in Monitor mode?
- Which permissions and data are required?
- Where is data retained?
- How can I exit, revoke and request deletion?

The first screen is `Agent Overview`（智能体总览）. The first flow must not
require DBA, DBOS, EEOAP, ARO, SAEE, the Authority Model, Evidence Admission,
Digital Biosphere or Digital Immune Architecture. Those remain available in
advanced architecture, research and technical documentation.

## Agent entry

An Agent must be able to discover TITMAS, evaluate applicability, read products
and non-claims, inspect access modes/inputs/data boundaries, run a synthetic
example, prepare a Monitor request, interpret results, verify public proof and
abstain when not applicable.

The canonical machine entry links:

| purpose | path |
|---|---|
| product catalog | `portfolio/product-catalog.internal.json` |
| solution catalog | `portfolio/solution-catalog.internal.json` |
| recommendation policy | `commercial/discovery/recommendation-policy.json` |
| commercial offerings | `commercial/discovery/commercial-offerings.json` |
| deployment options | `commercial/discovery/deployment-options.json` |
| known limitations | `commercial/discovery/known-limitations.json` |
| current C-01 status | `commercial/discovery/status.json` |

Allowed recommendation outputs:

```text
RECOMMENDED
CONDITIONALLY_RECOMMENDED
NOT_RECOMMENDED
NOT_APPLICABLE
NOT_ASSESSED
UNIVERSAL_RECOMMENDATION=false
```

## Authority boundary

Human view is a projection over the same machine contracts; it cannot hide or
rewrite reason codes, identifiers, unknowns or limitations. Agent priority does
not create contract, payment, deployment or enforcement authority.

```text
HUMAN_ENTRY_DEFINED=true
AGENT_ENTRY_DEFINED=true
HUMAN_ENTRY_IMPLEMENTED=false
AGENT_ENTRY_IMPLEMENTED=false
```
