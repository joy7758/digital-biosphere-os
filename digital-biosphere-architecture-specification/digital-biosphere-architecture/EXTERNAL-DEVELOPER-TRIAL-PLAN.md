---
document_id: DBA-EXTERNAL-DEVELOPER-TRIAL-PLAN-0.1
title: Trusted Multi-Agent Infrastructure External Developer Trial Plan v0.1
title_zh: 可信多智能体基础设施外部开发者试用计划 v0.1
status: superseded-as-primary-gate-retained-optional-human-study
program_artifact: External Developer Trial Preparation v0.1
target_participant_count: 3-5
trial_execution_authorized: false
external_contact_authorized: false
release_authorized: false
customer_validation_claimed: false
last_reviewed: 2026-07-21
---

# External Developer Trial Plan v0.1（外部开发者试用计划 v0.1）

> Supersession notice（取代说明）：`ADR-021` 已将 AI agent 定义为 TMAI 的首要客户，并以
> [`AGENT-CUSTOMER-VALIDATION-PROTOCOL.md`](AGENT-CUSTOMER-VALIDATION-PROTOCOL.md)
> 取代本文件作为 Developer Preview 的 primary validation gate（首要验证闸门）。本计划
> 作为可选的人类可用性研究和历史决策保留；它不再因缺少 3–5 名人类参与者阻塞本次发布审查。

## 1. Trial Objective（试用目标）

本计划验证一个没有参与内部架构设计的 Agent Developer（智能体开发者），能否独立理解并运行 `Trusted Multi-Agent Infrastructure Developer Preview v0.1`（可信多智能体基础设施开发者预览版 v0.1），再提交可归属、可修正的反馈。

它验证的是 onboarding（进入体验）、comprehension（理解）、usability（可用性）和 problem relevance signal（问题相关性信号），不是技术正确性、客户采用、企业验证、生产性能或商业需求证明。

```text
TRIAL_PLAN_NE_TRIAL_EXECUTION=true
TRIAL_PARTICIPANT_NE_CUSTOMER=true
FEEDBACK_NE_CUSTOMER_VALIDATION=true
TRIAL_PASS_NE_RELEASE=true
RELEASE_REQUIRES_HUMAN_DECISION=true
```

## 2. Responsibility Preflight（责任预检）

| 问题 | 结论 |
|---|---|
| Primary repository（主责任仓库） | DBA |
| 责任域 | Program Governance + Release Governance（项目群治理 + 发布治理） |
| 解决的问题 | 陌生开发者是否能进入、理解、运行并反馈，而不是继续扩展基础设施功能 |
| 是否修改 DBOS / SAEE | 否；本阶段冻结功能扩展，只引用候选版本和公开运行路径 |
| 是否重复建设 | 否；Plan 定义参与者、测量与 gate，现有 Guide 负责操作，Feedback Template 负责单次记录 |
| 是否需要人工决定 | 是；`DQ-010` 决定是否启动试用，`DQ-009` 决定是否发布 |

## 3. Agent Recommendation Gate（智能体推荐闸门）

当前结论：

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=CONTROLLED_EXTERNAL_DEVELOPER_TRIAL_PREPARATION
NOT_RECOMMENDED_AS=RELEASE_OR_CUSTOMER_VALIDATION
```

不无条件推荐的原因及修正：

| 不推荐原因 | 本计划的修正 | 剩余阻塞 |
|---|---|---|
| 现有指南没有参与者合格条件 | 定义 3–5 名独立 Agent Developer 画像 | 仍需招募与试用负责人 |
| 反馈字段不能判断理解是否正确 | 增加自由回答、评分 rubric（量表）和关键概念门 | 仍需真实回答 |
| 没有预先冻结成功阈值 | 在看到试用结果前冻结数量、时间、理解和价值信号标准 | 标准变更必须升版本 |
| 本地工作树不是可分发来源 | 冻结三个远端 commits，并由 `CLEAN-CLONE-VALIDATION-REPORT.md` 完成后继复验 | 已解决 |
| 计划可能被误写成外部验证开始 | `DQ-010` 采用条件授权；执行状态继续独立 | 真实 `participant_source` 仍缺失 |

只有准备条件全部通过后，智能体才推荐启动 3–5 人的受控试用；即便试用通过，也只推荐进入人工 Release Review（发布审查）。

## 4. Participant Profile（参与者画像）

目标样本：`3–5` 人。v0.1 追求观察入口问题，不追求统计代表性。

合格条件：

- 没有参与 DBA、DBOS、SAEE 本次 Developer Preview 的设计或实现；
- 能独立使用命令行和 Python 项目；
- 主要身份是 AI Agent developer、MCP developer（模型上下文协议开发者），或 LangChain / CrewAI 等多智能体工具使用者；
- 同意只使用 synthetic inputs（合成输入），不提交 secret（秘密）、客户数据或未公开材料；
- 同意记录匿名化的运行结果、时间、干预等级和反馈。

样本组合应尽量包含：

1. 至少 1 名 Agent application developer（智能体应用开发者）；
2. 至少 1 名 MCP / tool integration developer（MCP／工具集成开发者）；
3. 至少 1 名 multi-agent framework user（多智能体框架使用者）。

角色可以重叠。参与者不是企业、客户、认证者或项目授权主体；除非未来有独立协议，不得使用“客户试用”描述本批次。

## 5. Trial Package and Entry Conditions（试用包与进入条件）

试用只能基于一个冻结的 `trial_package_id`。当前技术包为
[`TMAI-DP-v0.1-TRIAL-20260721-001`](EXTERNAL-DEVELOPER-TRIAL-PACKAGE-v0.1.json)，包含：

- DBA [`PUBLIC-PROJECT-OVERVIEW.md`](PUBLIC-PROJECT-OVERVIEW.md)；
- 本计划；
- [`EXTERNAL-DEVELOPER-TRIAL-GUIDE.md`](EXTERNAL-DEVELOPER-TRIAL-GUIDE.md)；
- [`DEVELOPER-FEEDBACK-TEMPLATE.md`](DEVELOPER-FEEDBACK-TEMPLATE.md)；
- DBOS Developer Quick Start、Multi-Agent Trust Demo 和单一测试入口；
- SAEE read-only evaluation adapter（只读评价适配器）；
- exact repository URLs、branch/tag、commit hashes、依赖版本和 clean-clone validation result（干净检出验证结果）。

开始招募或发送仓库前必须满足：

```text
SOURCE_COMMITS_FROZEN=true
CLEAN_CLONE_VALIDATED=true
TRIAL_PACKAGE_ID_ASSIGNED=true
TRIAL_COORDINATOR_REF_ASSIGNED=true
PRIVACY_NOTICE_READY=true
DQ_010_TRIAL_EXECUTION_AUTHORIZED=true
EXTERNAL_CONTACT_AUTHORIZED=true
```

当前 source、Clean Clone、technical package、协调者、隐私和停止规则已经冻结；真实
`participant_source` 尚未提供，因此 `DQ-010` 条件授权仍未生效：

```text
TRIAL_PACKAGE_ID=TMAI-DP-v0.1-TRIAL-20260721-001
TRIAL_PACKAGE_TECHNICAL_FREEZE=true
TRIAL_PACKAGE_DISTRIBUTION_READY=false
SOURCE_COMMITS_FROZEN=true
CLEAN_CLONE_VALIDATED=true
TRIAL_COORDINATOR_REF=zhangbin
PRIVACY_NOTICE_READY=true
PARTICIPANT_SOURCE_CONFIRMED=false
TRIAL_EXECUTION_AUTHORIZED=false
EXTERNAL_CONTACT_AUTHORIZED=false
PARTICIPANTS_INVITED=0
```

## 6. Trial Workflow（试用流程）

```text
Receive frozen repositories（收到冻结仓库）
  -> Read Public Overview and Quick Start（阅读总览和快速入门）
  -> Install（安装）
  -> Run DBOS Quick Start（运行 DBOS 快速入门）
  -> Run Multi-Agent Trust Demo（运行多智能体可信演示）
  -> Read DBOS and SAEE results（理解 DBOS 与 SAEE 结果）
  -> Answer comprehension questions（回答理解问题）
  -> Submit feedback（提交反馈）
  -> Debrief after answers are frozen（答案冻结后复盘）
```

观察规则：

1. 参与者提交理解答案前，不提供架构口头教学；
2. `time_to_demo_minutes` 从首次打开 Quick Start 开始，到出现 `demo_contract_satisfied=true` 结束；
3. 每次帮助记录 `intervention_level`：`0=none`、`1=clarification`、`2=command_hint`、`3=hands_on_fix`；
4. 只有等级 `0` 或 `1` 的完成记录计入 unassisted completion（无实质协助完成）；
5. 失败、退出、超时、未知和误解全部保留，不用成功记录覆盖；
6. 参与者完成原始回答后才允许解释正确边界。

## 7. Measurement Model（测量模型）

### 7.1 Understanding（理解）

参与者必须用自己的语言回答：

1. DBOS 是什么？
2. 为什么 DBOS 不是 Agent Framework（智能体框架）？
3. DBOS 和 MCP 的关系是什么？
4. Validation Result `PASS` 能证明什么、不能证明什么？
5. SAEE 的 `HOLD` / `STOP` 是什么，谁仍然负责 Decision（决策）？

Reviewer（复核者）按预先冻结的 rubric 记录每题 `CORRECT`、`PARTIAL` 或 `INCORRECT`。不得用关键词命中替代语义判断，也不得在评分前改写参与者原始回答。

关键正确边界：

- DBOS 是可信存在与记录基础设施，不是 Agent 创建／推理／编排框架；
- MCP 是可选 interface/transport（接口／传输）边界，不是 DBOS 本体、Evidence Truth 或 Permission Authority；
- Validation `PASS` 只说明声明结构和受检规则通过，不证明事实、身份、授权或科学正确；
- SAEE Recommendation（建议）不是 Decision、Authorization 或 Execution。

### 7.2 Use（使用）

记录：

- install result（安装结果）；
- Quick Start result；
- Demo result；
- SAEE evaluation result；
- time to first successful demo；
- intervention level / count；
- first failure command 和 failure output reference（失败输出引用）。

### 7.3 Value Signal（价值信号）

参与者回答：

- 你当前在哪类 Agent 工作流中遇到身份、执行记录、证据引用或评价边界问题？
- 本预览与该问题的相关性是 `HIGH`、`MEDIUM`、`LOW` 还是 `NONE`？为什么？
- 哪个具体 use case（使用场景）值得继续试？
- 你会选择 `TRY_AGAIN`、`TRY_IF_IMPROVED` 或 `NOT_RELEVANT`？

这是 problem relevance signal，不是购买意向、采用、客户验证或市场规模证据。

## 8. Success Criteria（成功标准）

设合格并完成记录的参与者数为 `N`，要求 `3 <= N <= 5`。Trial Gate（试用闸门）只有同时满足下列条件才为 `PASS`：

| 维度 | 通过条件 |
|---|---|
| Participant coverage | 至少 3 名合格参与者完成记录，画像覆盖三类目标角色 |
| Demo completion | 至少 `ceil(0.8 × N)` 人在 `intervention_level <= 1` 下完成 Demo |
| Time to demo | 成功记录的 `median(time_to_demo_minutes) <= 30` |
| Concept comprehension | 全部五题中 `CORRECT` 比例至少 80% |
| Critical boundaries | DBOS≠Agent Framework、MCP≠Authority、Validation≠Truth 三题分别至少 80% 正确 |
| Result interpretation | 至少 80% 参与者正确解释 SAEE Recommendation≠Decision |
| Value signal | 至少 `ceil(0.6 × N)` 人给出 `HIGH`/`MEDIUM` 相关性和一个具体 use case |
| Actionable feedback | 可归属反馈记录数至少为 `N`，且包含 owner/category/severity |
| Safety | 未发生 secret/customer data 输入、Permission、Agent/Runtime 创建或未声明外部副作用 |
| Critical defects | 没有未解决的 release-blocking documentation、installation 或 boundary defect |

若样本不足、数据缺失或评分冲突，结果必须为 `INCOMPLETE`，不能按已完成参与者比例推断通过。

## 9. Feedback Model（反馈模型）

| category | Primary owner | 例子 | 当前阶段处理 |
|---|---|---|---|
| `DOCUMENTATION` | DBA 或对应文档 Owner | 入口不清、术语误解、步骤缺失 | 登记并评估是否阻塞下一批次 |
| `INSTALLATION` | DBOS | 依赖、命令、环境失败 | 本阶段只登记；DBA 不直接修 DBOS |
| `CONCEPT_MISUNDERSTANDING` | DBA | 把 DBOS 当框架、把 PASS 当 Truth | 视为 public entry / wording 缺口 |
| `EVALUATION_INTERPRETATION` | SAEE | 把 HOLD 当命令或权限 | 登记为 SAEE 输出解释缺口 |
| `FEATURE_REQUEST` | 待归属 | 新 capability、adapter 或 workflow | 进入 duplicate review；不在试用期间直接开发 |
| `SECURITY_PRIVACY` | DBA 协调，领域 Owner 处理 | secret、数据、非预期副作用 | 立即停止受影响 session（会话）并保留失败记录 |

任何功能请求都必须回到 DBA Test-to-Feature Governance（测试到功能治理），回答 Owner、重复建设、最小范围和禁止副作用。Trial feedback（试用反馈）不产生 Implementation Authorization。

## 10. Trial Result States（试用结果状态）

```text
PREPARED
  -> AUTHORIZED
  -> IN_PROGRESS
  -> COMPLETE_PENDING_REVIEW
  -> PASS | CONDITIONAL | FAIL | INCOMPLETE
```

- `PASS`：全部成功条件满足，可以提交 `DQ-009` 人工发布审查；
- `CONDITIONAL`：只有低／中风险文档或体验问题，修正后必须对受影响路径重试；不得直接发布；
- `FAIL`：关键理解、运行、安全或边界条件失败；保持 `NOT_RELEASED`；
- `INCOMPLETE`：样本、记录、来源或评分不足；不得按 PASS 处理。

任何结果都必须生成未来的 `External Developer Trial Result Report`（外部开发者试用结果报告），引用匿名 session records（会话记录）、source versions、失败、评分冲突和已知限制。

## 11. Release Gate（发布闸门）

```text
Trial PASS or remediated CONDITIONAL
  -> Result Report Review
  -> DQ-009 Human Release Decision
  -> Release Record
  -> Developer Preview Release
```

`PASS` 只使发布进入 `READY_FOR_REVIEW`，不自动产生 release、tag、push、deployment 或 adoption。发布仍必须有 `decided_by_ref`、`released_by_ref`、exact source versions、release notes 和 rollback/preservation plan（回退／保留计划）。

## 12. Stop Rules（停止规则）

任一情况发生时停止试用或保持未开始：

- source commit、trial package 或 clean-clone validation 缺失；
- `DQ-010`、trial coordinator 或 external contact authorization 缺失；
- 参与者需要真实凭证、客户数据、生产 Runtime 或未治理外部动作；
- 发生 Agent/Runtime/Permission 创建或历史 Evidence 修改；
- 指标、rubric 或成功阈值在看到结果后被静默修改；
- 失败记录被删除、合并或改写为成功；
- 试用被宣传为 customer validation、certification、production readiness 或 adoption。

## 13. Naming Rule（命名规则）

统一层级：

```text
Underlying program: Digital Biosphere
Public entry: Trusted Multi-Agent Infrastructure
Preview name: Trusted Multi-Agent Infrastructure Developer Preview v0.1
中文名称: 可信多智能体基础设施开发者预览版 v0.1
```

对外材料不得把底层项目名 `Digital Biosphere` 直接作为本 Developer Preview（开发者预览版）的首要名称。该命名规则不重命名 DBA、DBOS、SAEE 仓库或各自规范身份。

## 14. Current State（当前状态）

```text
TRIAL_PLAN_DEFINED=true
TRIAL_GUIDE_PREPARED=true
FEEDBACK_TEMPLATE_PREPARED=true
TRIAL_PACKAGE_ID=TMAI-DP-v0.1-TRIAL-20260721-001
TRIAL_PACKAGE_TECHNICAL_FREEZE=true
TRIAL_PACKAGE_DISTRIBUTION_READY=false
SOURCE_COMMITS_FROZEN=true
CLEAN_CLONE_VALIDATED=true
PARTICIPANT_SOURCE_CONFIRMED=false
TRIAL_EXECUTION_AUTHORIZED=false
EXTERNAL_CONTACT_AUTHORIZED=false
PARTICIPANTS_RECRUITED=0
TRIAL_SESSIONS_EXECUTED=0
EXTERNAL_DEVELOPER_VALIDATION_COMPLETE=false
CUSTOMER_VALIDATED=false
DEVELOPER_PREVIEW_RELEASED=false
```
