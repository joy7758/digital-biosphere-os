---
offering_id: TITMAS-ENTERPRISE-PRIVATE-DEPLOYMENT
version: "0.1"
status: ARCHITECTURE_CANDIDATE_NOT_AVAILABLE
commercial_effect: none
legal_effect: none
---

# TITMAS Enterprise Private Deployment / TITMAS 企业私有部署

## Candidate deployment modes

- customer VPC in China;
- customer private cloud;
- customer on-premises environment;
- air-gapped profile reserved for future architecture work only.

## Entry criteria

Private deployment requires a completed Monitor Pilot, and an Enforce Pilot if
blocking is requested. It also requires a separately approved architecture,
security review, data map, retention/deletion plan, support schedule, release
and rollback plan, commercial agreement, and customer acceptance test.

## Data boundary

Raw customer content stays in the customer environment by default. The
management plane receives only agreed minimum metadata. Customer-controlled
KMS/HSM, local Receipt storage, data region, backups, and retention are defined
per deployment.

## Delivery exclusions

No public self-service SaaS, automatic production deployment, automatic key
issuance, online payment, default cross-border processing, or universal
enterprise SLA is included.

## Status

```text
CUSTOMER_VPC_REFERENCE=DESIGN_ONLY
ON_PREMISES_REFERENCE=DOCUMENTATION_REQUIRED
AIR_GAPPED_PROFILE=FUTURE
ENTERPRISE_PRIVATE_DEPLOYMENT_AVAILABLE=false
PRODUCTION_READY=false
```
