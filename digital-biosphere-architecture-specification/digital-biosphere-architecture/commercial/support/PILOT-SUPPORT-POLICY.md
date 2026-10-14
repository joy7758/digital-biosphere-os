---
status: OWNER_ASSIGNED_POLICY_STILL_HUMAN_REVIEW_DRAFT
commercial_effect: none
support_owner_assigned: true
---

# Pilot Support Policy / 试点支持政策

本政策只适用于经单独 SOW（工作说明书）批准的私有 Monitor Pilot 候选，当前不构成服务承诺。

## Candidate service window

- 工作日人工支持时段、时区和响应目标必须逐客户写入 SOW；
- 未写入 SOW 的响应或恢复时间均为 `NOT_ASSESSED`；
- Monitor 模式不承担阻断、批准、自动修复或客户运行时控制；
- 客户必须指定业务 Owner、技术联系人和紧急停止联系人。

## Severity model

| Level | Meaning | Required action |
|---|---|---|
| SEV-1 | secret exposure, cross-tenant access, forged Receipt, unauthorized effect | stop the bounded service, preserve evidence, Human escalation |
| SEV-2 | material verification, export, deletion or isolation failure | contain affected scope and review before continuation |
| SEV-3 | degraded non-critical function | record, triage and schedule correction |
| SEV-4 | question or documentation defect | normal review queue |

## Boundaries

Support does not certify safety, correctness, compliance, recovery or production readiness. It cannot expand credentials, data scope, retention, Agent authority or contractual scope.

```text
SUPPORT_OWNER_ASSIGNED=true
SUPPORT_OWNER_REF=human:zhangbin
BACKUP_OWNER_ASSIGNED=false
SUPPORT_SLA_ACTIVE=false
CUSTOMER_SUPPORT_AVAILABLE=false
```
