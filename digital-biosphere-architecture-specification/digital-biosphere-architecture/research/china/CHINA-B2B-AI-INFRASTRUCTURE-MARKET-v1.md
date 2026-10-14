# China B2B AI Infrastructure Market Research v1

Status: `PRIVATE_RESEARCH_BASELINE`

Observed at: `2026-08-03`

## Evidence classification

| Finding | Classification | Basis |
|---|---|---|
| Alibaba AgentLoop exposes observation, audit, evaluation, experiment and continuous optimization | `VERIFIED_FROM_PRIMARY_VENDOR` | Alibaba Cloud official documentation |
| Tencent exposes Agent gateway and separate AI Agent security gateway products | `VERIFIED_FROM_PRIMARY_VENDOR` | Tencent Cloud official product pages |
| Baidu exposes Qianfan plus an AI/Agent guardrail product with purchase/trial paths | `VERIFIED_FROM_PRIMARY_VENDOR` | Baidu Intelligent Cloud official product pages |
| Chinese enterprise buyers are accustomed to cloud consoles, account activation, quota, billing, support and private-delivery consultation | `REASONED_HYPOTHESIS` supported by vendor funnels | must be tested with design partners, not reported as market validation |
| Coding-Agent teams are the best first paid segment for TITMAS | `REASONED_HYPOTHESIS` | risk is measurable and avoids initial medical/financial/industrial production data |
| Customers prefer China-local metadata and customer-local raw data | `REASONED_HYPOTHESIS` plus regulatory-risk reduction | requires direct buyer validation and legal review |
| There is proven willingness to pay for TITMAS | `NOT_ASSESSED` | no customer or authorized outreach evidence exists |

## Candidate buyer and user map

| Role | Candidate problem | TITMAS entry |
|---|---|---|
| engineering leader | coding Agent can merge/release/write without consistent precondition evidence | bounded Monitor Pilot |
| security leader | unclear authority, data boundary and response after an Agent action | architecture/data-boundary review plus Audit |
| platform team | different Agent runtimes expose incompatible action/evidence records | SDK/adapter plus portable Receipt |
| operations | difficult rollback, key revocation, incident correlation and replay | deployment/support runbook plus Audit |
| procurement/legal | unclear scope, acceptance, data location, liability and exit | SOW, DPA, security schedule and acceptance checklist |
| operational Agent | needs machine-readable discovery, schemas, reason codes and verifiable proof | public catalog, SDK, Sandbox and scoped key |

## China-specific commercial expectations to validate

- Chinese-language console and reason-code explanations;
- contracting entity, official seal, bank transfer and VAT invoice readiness;
- offline B2B qualification, NDA, security review, SOW and acceptance;
- workspace, scoped key, quota, audit log, export and support ticket;
- China-managed private pilot and customer-VPC reference deployment;
- compatibility with domestic cloud, model API, database, object storage, KMS
  and notification channels;
- data-location, retention, deletion and subprocessor disclosure;
- customer manager and Human support rather than self-service payment.

None of these hypotheses is customer validation. D29 must preserve
`CUSTOMERS_VERIFIED=0` unless a separately authorized real customer cycle
produces evidence.

## First market boundary

The first candidate use case is a controlled software-delivery workflow:

```text
Coding Agent proposes merge or release
  -> TITMAS Monitor records WOULD_BLOCK without interfering
  -> customer reviews evidence and false-block behavior
  -> separately authorized Enforce Pilot may block before side effect
```

Medical diagnosis, real financial transactions, manufacturing control,
critical infrastructure and autonomous aerospace remain research/private
discovery only.
