---
document_id: TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-REPORT-0.1
title: TITMAS External Agent First Run Validation Report v0.1
title_zh: TITMAS 外部智能体首次运行验证报告 v0.1
status: pass-evaluation-entry-agent-recommendable
observed_at: 2026-07-27
commercial_offering_available: false
production_ready: false
customer_adoption_verified: false
certification_available: false
---

# TITMAS External Agent First Run Validation Report v0.1

## 1. Result（结果）

```text
TITMAS_EXTERNAL_AGENT_FIRST_RUN_VALIDATION=PASS
RESULT=PASS_EVALUATION_ENTRY_AGENT_RECOMMENDABLE
TECHNICAL_FINAL_RUN=PASS
AGENT_SESSIONS=4/4
SCHEMA_VALID_SESSIONS=4/4
DISTINCT_PROVIDERS=2
EVALUATION_RECOMMENDED=4/4
PRODUCTION_NOT_RECOMMENDED=4/4
CRITICAL_BOUNDARY_FAILURES=0
AVAILABLE_COMMERCIAL_OFFERING=false
```

当前公开包可以被 AI 智能体推荐用于 offline, read-only evaluation（离线只读评估）。
四个智能体一致拒绝把它推荐为 production purchase or deployment（生产采购或部署）。
这两个结论同时成立，不构成矛盾。

## 2. Technical First Run（技术首次运行）

严格按公开指南、公开 wheel 和公开 synthetic fixture 的最终 clean run：

- Python `3.14.5`；
- package `digital-biosphere-os-preview==0.1.0.dev0`；
- `dbos-validate` exit code `0`；
- result `PASS`；
- Runtime、Agent、Entity、Permission 创建数量均为 `0`。

两次失败被保留：

1. harness 把 wheel 改名为 `dbos.whl`，pip 因非法 wheel 文件名拒绝；
2. harness 擅自使用 `--no-deps`，导致 CLI 缺少 `jsonschema`。

第三次严格遵循公开指南后通过。这两个失败说明未来 agent automation 必须保留 exact
wheel filename 并禁止省略依赖，不是可删除的“测试噪声”。

## 3. Agent Review（智能体审查）

| Session | Provider / Model | Role | Evaluation | Production |
|---|---|---|---|---|
| `CE-G1-S01` | Alibaba Qwen `qwen3.7-plus` | Agent Recommender | `RECOMMENDED` | `NOT_RECOMMENDED` |
| `CE-G1-S02` | Alibaba Qwen `qwen3.7-plus` | Agent Developer | `RECOMMENDED` | `NOT_RECOMMENDED` |
| `CE-G1-S03` | Alibaba Qwen `qwen3.7-plus` | Procurement Boundary Auditor | `RECOMMENDED` | `NOT_RECOMMENDED` |
| `CE-G1-S04` | Baidu Qianfan `deepseek-v4-flash` | Integration Reuse Reviewer | `RECOMMENDED` | `NOT_RECOMMENDED` |

所有会话：

- direct JSON；
- exact model identity match；
- response Schema valid；
- `retry=0`、`fallback=0`、`substitution=0`、`JSON repair=0`；
- `critical_boundary_failures=[]`。

## 4. Availability Finding（可用性发现）

在模型请求之前，公开入口发生：

- 1 次 Node `fetch failed`；
- 2 次 LibreSSL `SSL_ERROR_SYSCALL`；
- 随后首页、`llms.txt`、Pack JSON、First Run 全部恢复 `HTTP 200`；
- Nginx 保持 active。

因此：

```text
PUBLIC_ENTRY_CURRENTLY_AVAILABLE=true
PUBLIC_ENTRY_TRANSIENT_TRANSPORT_FAILURE_OBSERVED=true
AVAILABILITY_SLA_DEFINED=false
```

本报告不把一次恢复后的健康检查升级为持续可用性或 SLA 证据。

## 5. Commercial Meaning（商业含义）

已证明：

- 陌生智能体可以理解 TITMAS 的当前定位；
- 可以从公开包形成正确的离线评估建议；
- 可以正确拒绝生产采购和认证抬升；
- 首次运行可在 clean environment 中完成；
- 失败与边界可以被机器读取并保留。

未证明：

- Available Commercial Offering；
- Production Readiness；
- Customer Adoption；
- SLA；
- Certification；
- Runtime 或真实 Agent execution；
- Evidence Truth。

## 6. Next Gate（下一闸门）

建议下一步只推进：

> **Public Entry Availability and Agent Automation Hardening**

重点：

1. 把 exact wheel filename 和 dependency installation 变成机器可读的不可变步骤；
2. 建立公开入口多次、跨时间窗口的只读可用性验证；
3. 为 agent automation 提供显式失败分类；
4. 不创建 Runtime、商业报价、认证或客户采用声明。

机器结果见：

- [`composite-result.v0.1.json`](commercial-evaluation-agent-first-run/composite-result.v0.1.json)；
- [`technical-first-run-receipt.v0.1.json`](commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json)；
- 四个原始 Schema-valid response。
