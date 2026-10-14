---
document_id: DBA-EXTERNAL-DEVELOPER-TRIAL-GUIDE-0.1
title: Trusted Multi-Agent Infrastructure External Developer Trial Guide v0.1
title_zh: 可信多智能体基础设施外部开发者试用指南 v0.1
status: superseded-primary-route-retained-optional-human-runbook
external_trial_started: false
trial_execution_authorized: false
customer_validation_claimed: false
last_reviewed: 2026-07-21
---

# External Developer Trial Guide v0.1（外部开发者试用指南 v0.1）

> Supersession notice（取代说明）：依据 `ADR-021`，本指南不再是 Developer Preview 的
> primary customer validation（首要客户验证）入口。它作为未来可选 human usability study
> （人类可用性研究）手册保留；当前首要入口是
> [`AGENT-CUSTOMER-VALIDATION-PROTOCOL.md`](AGENT-CUSTOMER-VALIDATION-PROTOCOL.md)。

本指南是参与者操作手册。参与者画像、测量、成功条件、结果状态和发布闸门由 [`EXTERNAL-DEVELOPER-TRIAL-PLAN.md`](EXTERNAL-DEVELOPER-TRIAL-PLAN.md) 定义。

本指南准备一个完全本地、合成、只读的 Developer Preview（开发者预览）试用。技术
来源和 Clean Clone（干净检出）已经冻结，但真实 `participant_source` 仍缺失，`DQ-010`
条件授权尚未生效。因此本文件是 source-frozen candidate guide（来源冻结候选指南），
不是外部验证、招募授权或正式 release（发布）证明。

## Trial question（试用问题）

> 一个外部开发者能否看懂并运行三角色可信链路，并确认 DBOS 只记录事实、SAEE 只给出受限评价建议？

## Prerequisites（前置条件）

- Python 3.11+，支持 `venv`；
- 能通过组织或个人批准的软件源安装仓库声明的 Python 依赖；
- 本地可访问的 `digital-biosphere-os` 与 `SAEE` source checkout（源码检出）；
- 不需要 API key、模型、网络服务、客户数据或生产 Runtime。

每次 session 必须使用
[`EXTERNAL-DEVELOPER-TRIAL-PACKAGE-v0.1.json`](EXTERNAL-DEVELOPER-TRIAL-PACKAGE-v0.1.json)
中的 exact commits（精确提交），不能用任意分支、开发工作树或缓存替代来源冻结。

正式 session（会话）开始前，协调者还必须提供：

```text
trial_package_id=TMAI-DP-v0.1-TRIAL-20260721-001
dba_source_version=91928e3b1096566aad5568124707e3a6cb3a40ca
dbos_source_version=0caa2c45e511a82d0dcab778b0ffc3163aac0029
saee_source_version=2173c258f91aed03fc02c0097d4250a87be703aa
clean_clone_validation_reference=CLEAN-CLONE-VALIDATION-REPORT.md
trial_coordinator_ref=zhangbin
participant_source=PENDING_REAL_INPUT
```

`participant_source` 仍为 `PENDING_REAL_INPUT` 时，不开始正式计时、不添加 DBOS
collaborator（协作者），也不把任何内部运行记录计入外部开发者试用结果。

## Local trial（本地试用）

```bash
cd <DBOS_REPO>
git checkout 0caa2c45e511a82d0dcab778b0ffc3163aac0029
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python tools/run_tests.py
.venv/bin/python -m examples.multi_agent_trust_demo.run_demo \
  > /tmp/dbos-multi-agent-trust-demo-v0.1.json

cd <SAEE_REPO>
git checkout 2173c258f91aed03fc02c0097d4250a87be703aa
python3 -m venv .venv
.venv/bin/python -m pip install 'jsonschema>=4.18,<5.0' referencing
.venv/bin/python -m unittest tests/test_dbos_developer_preview_adapter.py
.venv/bin/python scripts/saee_evaluate_dbos_preview.py \
  --input /tmp/dbos-multi-agent-trust-demo-v0.1.json \
  > /tmp/saee-dbos-developer-preview-evaluation-v0.1.json
```

预期最小结果：

```text
DBOS_TEST_RESULT=PASS
demo_contract_satisfied=true
agent_instance_created=false
runtime_created=false
permission_granted=false
Reliability=NOT_ASSESSED
Stability=NOT_ASSESSED
Risk=RISKS_IDENTIFIED
EvolutionRecommendation=HOLD
```

`NOT_ASSESSED` 是预期的 truthful result（真实结果）：DBOS Demo 只生成 `CREATED` execution records（执行记录）和 `PENDING` evidence references（证据引用），不伪装成真实完成的执行与已验证证据。

## Feedback scope（反馈范围）

使用 [`DEVELOPER-FEEDBACK-TEMPLATE.md`](DEVELOPER-FEEDBACK-TEMPLATE.md) 记录：

- 安装与运行是否可理解；
- DBA / DBOS / SAEE 边界是否清楚；
- 输出是否能区分 Record、Evidence、Validation、Evaluation、Recommendation；
- 错误是否 fail closed（失败关闭）；
- 哪个最小功能缺口阻碍试用。

在查看任何讲解答案前，用自己的语言回答：

1. DBOS 是什么？
2. 为什么 DBOS 不是 Agent Framework（智能体框架）？
3. DBOS 和 MCP 是什么关系？
4. Validation `PASS` 能证明什么、不能证明什么？
5. SAEE 的 `HOLD` / `STOP` 是建议、决策还是执行？

不要为了匹配术语而复制 README；目标是判断你是否能形成自己的正确解释。

反馈不是 adoption（采用）、customer validation（客户验证）、certification（认证）或 production evidence（生产证据）。

## Privacy and security（隐私与安全）

- 只使用仓库自带 synthetic inputs（合成输入）；
- 不输入个人、客户、密钥、未公开科研或生产数据；
- 不启用模型、网络或外部工具调用；
- 不把结构 Validation `PASS` 写成 Evidence truth（证据真相）；
- 不把 SAEE `HOLD`/`STOP` 写成授权或命令。

## Cleanup（清理）

本流程只允许删除两个明确的临时输出：

```text
/tmp/dbos-multi-agent-trust-demo-v0.1.json
/tmp/saee-dbos-developer-preview-evaluation-v0.1.json
```

不得清理仓库、Evidence 历史、测试失败或用户工作树。

```text
TRIAL_GUIDE_PREPARED=true
TRIAL_PLAN_DEFINED=true
TRIAL_PACKAGE_ID=TMAI-DP-v0.1-TRIAL-20260721-001
SOURCE_COMMITS_FROZEN=true
CROSS_PROJECT_CLEAN_CLONE_PASS=true
PARTICIPANT_SOURCE_CONFIRMED=false
TRIAL_EXECUTION_AUTHORIZED=false
EXTERNAL_CONTACT_AUTHORIZED=false
PARTICIPANTS_INVITED=0
EXTERNAL_TRIAL_EXECUTED=false
RELEASED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```
