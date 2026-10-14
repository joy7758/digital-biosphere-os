# TITMAS Solution Catalog v0.1

Status: `PORTFOLIO_MAPPING_ONLY`

Solutions reuse the same TITMAS private core. A solution may differ only by an
industry Adapter, policy configuration, workflow, UI or report template.

| Solution | Product bundle | Current portfolio status |
|---|---|---|
| Software Delivery | Gate + Receipt + Audit | primary controlled synthetic proof |
| Media Evidence | Receipt + Audit + Health | secondary public configuration; private reference candidate retained |
| Medical Imaging | Receipt + Audit | direction only; no medical decision capability claim |
| Smart Manufacturing | Gate + Receipt + Audit | direction only; no production equipment action |
| Financial Action Control | Gate + Receipt + Audit | direction only; no real transaction authority |
| Autonomous Space Research | Gate + Receipt + Audit + Health | direction only; no autonomous mission authority |

Forbidden solution-local capabilities include an identity core, evidence core,
receipt engine, audit chain, tenant system or issuance system.

```text
SHARED_CORE_REUSE_TARGET=70_PERCENT
REUSE_TARGET_IS_INTERNAL_MANAGEMENT_THRESHOLD=true
REUSE_TARGET_IS_STANDARD=false
REUSE_TARGET_IS_SCIENTIFIC_LAW=false
```

If the reuse gate cannot be satisfied, the candidate is classified
`NOT_A_TITMAS_PORTFOLIO_EXTENSION` and is deferred from the current roadmap.
