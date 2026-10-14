---
document_id: DBA-AGENT-CUSTOMER-VALIDATION-REPORT-0.1
title: TMAI Agent Customer Validation Report v0.1
title_zh: 可信多智能体基础设施智能体客户验证报告 v0.1
status: baseline-complete-conditional-remediation-required
validation_id: TMAI-ACV-20260721-001
result: CONDITIONAL
release_authorized: false
customer_adoption_claimed: false
last_reviewed: 2026-07-22
---

# Agent Customer Validation Report v0.1（智能体客户验证报告 v0.1）

> Follow-up（后继结果）：本文件保留首轮 `001=CONDITIONAL` 及其失败。修复后
> `TMAI-ACV-20260722-002=PASS`，见
> [`AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md`](AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md)。

## 1. Outcome First（结果优先）

```text
VALIDATION_ID=TMAI-ACV-20260721-001
RESULT=CONDITIONAL
API_SESSIONS_COMPLETED=12/12
PROVIDERS_WITH_SUCCESS=2/2
MODEL_IDENTITIES_WITH_SUCCESS=4/4
PARSE_FAILURES=0
AUTHORITY_SAFETY_FAILURES=0
OPEN_WEB_DISCOVERY=NOT_ASSESSED
CUSTOMER_ADOPTION_CLAIMED=false
RELEASE_AUTHORIZED=false
```

六个独立 agent-customer profiles（智能体客户画像）全部能从公开机器入口识别 TMAI，全部保持未发布／非生产状态，且没有把 Recommendation（建议）升级为 Decision、Execution 或 Permission。

但冻结人类开发者试用包没有通过“可直接被智能体准确调用、组合和推荐”的预设阈值。结果不是技术失败，也不是市场通过；它是一个可归属的 agent-readable packaging（智能体可读包装）缺口。

## 2. Execution Record（执行记录）

| 项目 | 结果 |
|---|---|
| Provider（提供方） | Baidu Qianfan（百度千帆）、Volcengine Ark（火山方舟） |
| Models（模型） | `ernie-4.5-turbo-128k`、`deepseek-v4-flash-260425`、`glm-5-2-260617`、`doubao-seed-2-0-lite-260215` |
| Profiles（画像） | retrieval、coding、recommendation、integration、governance review、multi-agent solution |
| Contexts（上下文） | 每画像 `PUBLIC_ONLY` + `BOUNDED_PACKAGE` |
| API sessions | 12 个完成，12 个 JSON 可解析 |
| First preflight | API 前一次 `redcrag.cn` TLS `SSL_UNEXPECTED_EOF`；一次传输重试后成功，失败被保留 |
| Provider retries | 0 |
| Model fallback | 0 |
| Secret scan | 12/12 PASS；没有密钥进入输出工件 |

API key 只从 `/Users/zhangbin/GitHub/SAEE/.env.local` 读入进程。该路径和密钥值没有写入请求、原始回答或提交工件。

## 3. Frozen Score（冻结评分）

| metric | observed | threshold | result |
|---|---:|---:|---|
| Provider coverage | 2 | ≥2 | `PASS` |
| Model identity coverage | 4 | ≥3 | `PASS` |
| Parseable sessions | 12/12 | ≥8 | `PASS` |
| Public project identification | 6/6 | ≥5/6 | `PASS` |
| Architecture boundary assertions | 130/132 = 98.5% | ≥80% | `PASS` |
| Release truth | 12/12 = 100% | ≥80% | `PASS` |
| Exact canonical command extraction | 2/6 | ≥5/6 | `FAIL_THRESHOLD` |
| Complete DBOS → SAEE → Decision composition | 0/6 | ≥5/6 | `FAIL_THRESHOLD` |
| Positive-fit recommendation | 7/12 = 58.3% | ≥80% | `FAIL_THRESHOLD` |
| Simple-lookup negative control | 9/12 = 75% | ≥80% | `FAIL_THRESHOLD` |
| Real-time authorization negative control | 12/12 | ≥80% | `PASS` |
| Agent-framework negative control | 12/12 | ≥80% | `PASS` |
| Authority safety failures | 0 | 0 | `PASS` |

全部回答的 overall verdict（总建议）为：

```text
RECOMMEND=0
CONDITIONAL=6
DO_NOT_RECOMMEND=6
```

## 4. Why Agents Would Not Recommend（智能体为什么不推荐）

### A. Package truth is still human-trial shaped（包仍以人类试用为中心）

冻结包反复出现 `participant_source=PENDING_REAL_INPUT`、`trial_execution_authorized=false`、参与者 0 和 3–5 人流程。模型正确判断它尚不可作为 agent-native（智能体原生）使用入口。

### B. Public runtime availability is missing（缺少公开运行可用性）

DBOS 仍是 private collaborator trial（私有协作者试用），没有 public API、公开 package 或面向智能体的受控调用表面。模型不会把规范和候选站点误当成可部署产品。

### C. Exact commands are not a single machine contract（精确命令不是单一机器契约）

虽然材料含有命令，模型常返回带 `.venv/bin`、重定向或片段化的变体。只有 2/6 个冻结包会话至少原样提取一个 package canonical command（包规范命令）。

### D. Composition stops before Governance Decision（组合链停在治理决策前）

6/6 冻结包回答都能连接 DBOS 与 SAEE，但 `composition_flow` 没有完整表达：

```text
DBOS records
  -> SAEE evaluation/recommendation
  -> Governance Decision review/adoption
  -> DBOS authorized execution
```

### E. Non-fit guidance is not strong enough（不适用指引不够强）

3 个千帆冻结包会话对一次性查询给出 `CONDITIONAL`，而不是 `DO_NOT_RECOMMEND`。基础设施入口需要主动告诉推荐智能体何时不要推荐 TMAI。

## 5. Remediation Ownership（修复归属）

| gap | Owner | 允许的最小修复 | 禁止扩展 |
|---|---|---|---|
| Agent customer framing | DBA | 新建 agent-native protocol、package、machine status 和 ADR | 不创建 Agent 或 Runtime |
| Exact public validation commands | DBA website candidate | 提供 `curl`／GitHub 精确只读入口 | 不虚构 public DBOS API |
| Canonical composition flow | DBA | 在机器包中明确四段有权力边界的数据流 | 不实现 Decision Service |
| Non-fit rules | DBA | 明确 simple lookup、Agent framework、production authorization 三类不适用场景 | 不改变 DBOS/SAEE capability truth |
| Operational use/reuse | DBOS Domain + Human Owner decision | 单独决定 public distribution、受控 agent access 或保持 private | 本报告不自动公开 DBOS |

本轮不建议增加 DBOS 功能。当前首先修复 DBA 的公开 agent-readable contract（智能体可读契约），再用相同阈值复测。

## 6. Artifact Integrity（工件完整性）

| artifact | SHA-256 |
|---|---|
| [`raw-sanitized-observations.v0.1.json`](agent-customer-validation/raw-sanitized-observations.v0.1.json) | `25e6f94443217b9dd82eb84be1e8dba6ab99cb62fbc8a5f1dc935d3474a7f7a4` |
| [`scored-result.v0.1.json`](agent-customer-validation/scored-result.v0.1.json) | `77a14daddc4f3071f5f5efd238032e1e14d518e874260032ad47bc639d0a6931` |
| [`validation-plan.v0.1.json`](agent-customer-validation/validation-plan.v0.1.json) | 由 Git commit 固定；计划先于调用形成 |

原始回答只做 secret scan（密钥扫描）和 JSON 解析，没有人工改写。评分细节逐 session 保存在 scored result 中。

## 7. Governance Conclusion（治理结论）

首轮结果支持两点：

1. TMAI 已经能被给定 URL 的陌生智能体识别和正确理解；
2. 当前材料尚不能让多数智能体从冻结包准确组合和推荐它。

因此下一状态是 `REMEDIATION_AND_CONTROLLED_RERUN`，不是正式发布。完成 agent-readable 修复后，使用新 validation ID、相同阈值和相同 Provider／model allowlist（提供方／模型白名单）复测。

```text
BASELINE_RESULT=CONDITIONAL
REMEDIATION_REQUIRED=true
DBOS_FEATURE_EXPANSION_REQUIRED=false
DBOS_VISIBILITY_DECISION_REQUIRED=true
FORMAL_RELEASE_READY=false
```
