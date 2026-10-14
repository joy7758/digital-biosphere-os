---
document_id: DBA-DEVELOPER-PREVIEW-PLAN-0.1
title: Trusted Multi-Agent Infrastructure Developer Preview Plan v0.1
title_zh: 可信多智能体基础设施开发者预览计划 v0.1
status: active-bounded-delivery-plan
target_version: v0.1
release_status: not-ready
automatic_authorization: false
last_reviewed: 2026-07-21
---

# Trusted Multi-Agent Infrastructure Developer Preview Plan v0.1（可信多智能体基础设施开发者预览计划 v0.1）

## 1. Outcome（成果）

本计划把 Digital Biosphere 从规范基线推进到第一个外部开发者能够理解、运行和复核的受限预览。目标不是最大功能，而是一条有来源、有失败记录、无自动提权的最小可信链路。

```text
Public Entry
  -> DBOS Local Developer Experience
  -> Three-Role Trust Demo
  -> SAEE Evaluation
  -> Human Review
  -> External Trial Preparation
```

Developer Preview 同时是 DBOS / SAEE Cross-project Test Engineering Program（跨项目测试工程计划）。Demo 不是终点，而是可重复的测试夹具；测试可以暴露真实功能缺口，并触发责任明确的最小功能补全。

```text
Governed Scenario（受控场景）
  -> DBOS Record and Validation Test（记录与校验测试）
  -> SAEE Evaluation Test（评价测试）
  -> Gap Classification（缺口分类）
  -> DBA Ownership / Duplication Decision（归属／重复建设判断）
  -> Minimal Feature in Owning Repository（责任仓库补最小功能）
  -> Regression and Cross-project Conformance（回归与跨项目符合性）
```

测试失败可以产生 Feature Proposal（功能提案），但不能自动授权实现。只有满足以下条件才进入开发：

1. 失败可稳定复现且不是 fixture（夹具）或文档误用；
2. 明确属于 DBOS、SAEE、Digital Entity 或 DBA 中的一个责任域；
3. 已检查现有能力和相邻项目，确认不是重复建设；
4. 定义正例、负例、不可产生的副作用和完成证据；
5. 高影响变化有 DBA decision reference（决策引用）。

## 2. Responsibility Preflight（责任预检）

| 问题 | 结论 |
|---|---|
| 属于哪个责任域？ | DBA 管阶段、发布与 gate；DBOS 管存在和记录；SAEE 管评价；演示角色只提供任务级合成输入 |
| 解决什么问题？ | 让长期运行、多角色协作和评价形成可检查的最小证据路径，并用跨项目测试暴露真实基础设施缺口 |
| 是否重复建设？ | DBA 不实现代码；DBOS 不实现 Agent 推理；SAEE 不复制 DBOS 事实；Demo 只编排三个受控角色 |
| 是否需要 DBA 决策？ | 是；`ADR-017` 接受本阶段及范围，具体发布仍需 Release Gate |

## 3. Workstreams and Exit Criteria（工作流与退出条件）

### DP-1 Public Entry（公开入口）— DBA

输出：

- `PUBLIC-PROJECT-OVERVIEW.md`；
- 本计划；
- `DEVELOPER-PREVIEW-RELEASE-PLAN.md`；
- README 导航和 `ADR-017`。

退出条件：统一定位、架构图、当前事实、Demo 入口占位和发布边界一致，链接验证通过。

### DP-2 DBOS Developer Preview（DBOS 开发者预览）— DBOS

输出：

- 可复制的隔离安装流程；
- 单一测试入口；
- Quick Start、正负示例和本地 SDK 入口；
- 冻结证据与当前文档的版本边界修复。
- 仓库级 test runner（测试入口）和“零测试即失败”保护；
- 面向 Demo 的确定性记录构建与 conformance fixture（符合性夹具），但不执行 Agent 行为。

退出条件：公开命令在干净环境中通过；全部适用 validator 通过；历史 `DBOS-EXP-0001` Evidence 不被修改；无 Agent、Runtime 或 Permission 创建。

本地结果：`DP-GAP-001` 与 `DP-GAP-002` 已实现并回归。版本感知校验使用保留的历史 binding（绑定）验证 `DBOS-EXP-0001`，不改写旧 digest；统一 test runner 共发现并通过 331 个测试；34/34 validator 通过。变更尚未发布。

### DP-3 Multi-Agent Trust Demo（多智能体可信演示）— Demo / DBOS

输出：

- `Research Agent`、`Analysis Agent`、`Review Agent` 三个受控角色模拟；
- 每个角色的显式 identity declaration（身份声明）、输入、输出、执行记录和 failure path（失败路径）；
- DBOS Evidence Reference（证据引用）与 Validation Result（验证结果）；
- 确定性本地运行命令和测试。
- 可被 DBOS 和 SAEE 分别消费的同一 fixture envelope（夹具信封），避免双份事实。

退出条件：链路可重复运行；角色不能自我授权；Review 不等于事实；无网络、生产 Runtime、真实 Entity 注册或 Evidence 重写。

### DP-4 SAEE Evaluation Layer v0.1（SAEE 最小评价层）— SAEE

输入：DBOS `Execution History`、`Validation Result`、`Evidence Reference`、`Resource Information`。

输出：`Reliability`、`Stability`、`Risk Assessment`、`Evolution Recommendation`。

退出条件：先审计 SAEE 现有 canonical capability（规范能力），避免重复实现；评价结果有来源、有局限、可确定性复核，不写回 DBOS，不产生 Decision、Permission 或状态变化。

允许由测试证明后补全的最小功能包括：只读 DBOS input adapter（输入适配器）、透明且可重复的四维评价、`UNSUPPORTED/UNKNOWN`（不支持／未知）失败关闭结果和机器可读 Recommendation envelope（建议信封）。不得借机恢复完整自动演化或控制系统。

### DP-5A External Developer Trial Preparation（外部开发者试用准备）— DBA / Developer Experience

输出：

- 试用范围与安装前置条件；
- 3–5 名参与者画像、独立性和隐私要求；
- 理解、使用、价值信号和干预程度的测量方法；
- 在看到结果前冻结的成功标准；
- issue/feedback（问题／反馈）模板；
- privacy/security（隐私／安全）边界；
- 本地清理和失败报告说明。

退出条件：[`EXTERNAL-DEVELOPER-TRIAL-PLAN.md`](EXTERNAL-DEVELOPER-TRIAL-PLAN.md)、Guide、Feedback Template 和 ADR-018 一致；不表示试用已经开始或成功。

### DP-5B External Developer Trial Execution（外部开发者试用执行）— DBA / Trial Coordinator

输入：冻结 source commits、clean-clone validation、`trial_package_id`、隐私说明、试用协调者和 `DQ-010` 明确授权。

输出：3–5 份匿名 session records、失败与干预记录、理解评分、价值信号、aggregate Trial Result Report（汇总试用结果报告）。

退出条件：按预先冻结标准形成 `PASS`、`CONDITIONAL`、`FAIL` 或 `INCOMPLETE`；反馈不被误记为 adoption、customer validation 或 release。

## 4. Test-to-Feature Governance（测试到功能治理）

每个由测试触发的新增功能必须登记：

```text
gap_id=
failing_test_reference=
owner_domain=DBOS|SAEE|DIGITAL_ENTITY|DBA
existing_capability_checked=
duplication_result=
proposed_minimal_feature=
positive_test=
negative_test=
forbidden_side_effects=
dba_decision_reference=
implementation_repository=
regression_result=
```

初始测试驱动功能候选：

| gap | Owner | 建议最小功能 | 本地结果 |
|---|---|---|---|
| `DP-GAP-001` | DBOS | Version-aware frozen evidence validation（版本感知冻结证据校验） | `PASS`：历史 digest 保留；34/34 validators 通过 |
| `DP-GAP-002` | DBOS | 单一 test runner，且测试数为 0 时失败 | `PASS`：15 个测试目录、331/331 tests |
| `DP-GAP-003` | DBOS | Multi-role execution/evidence fixture builder（多角色执行／证据夹具构建器） | `PASS`：三角色、3 个执行记录、3 个证据引用、9 个结构校验结果；11/11 tests |
| `DP-GAP-004` | SAEE | 只读 Evaluation Adapter + 四维透明输出 | `PASS`：复用现有 evaluator；8/8 adapter tests；不写 DBOS |
| `DP-GAP-005` | Cross-project | DBOS output / SAEE input conformance tests（输出／输入符合性测试） | `PASS`：同一 envelope 端到端本地执行；输出 fail closed |
| `DP-GAP-006` | SAEE governance | Constitution 要求字段的 Agent-readable index 投影 | `PASS`：补齐 3 个既有字段；Constitution smoke 通过；无 capability truth 变化 |

Feature Proposal 不得由 Demo 仓库吸收为新的 canonical DBOS 或 SAEE 能力。

## 5. Required Gates（必要闸门）

| gate | Developer Preview 解释 | 当前状态 |
|---|---|---|
| `G1 Source Truth` | 所有声明指向 repo、commit/version 和运行记录 | `PARTIAL_UNCOMMITTED_WORKTREES` |
| `G2 Architecture Contract` | DBA / DBOS / SAEE / Demo 边界明确 | `PASS_FOR_SCOPED_START` |
| `G3 Implementation Mapping` | 复用现有 DBOS/SAEE 能力，不建立第二套权威 | `PASS_SCOPED_LOCAL` |
| `G4 Conformance` | 正负测试、validator 和确定性重放通过 | `PASS_SCOPED_LOCAL` |
| `G6 Execution Evidence` | Demo 运行形成合成、可追踪、不可静默删除的输出 | `PASS_SYNTHETIC_RECORD_CHAIN_ONLY` |
| `G7 Evaluation and Adoption` | SAEE Recommendation 与人工判断分离 | `PASS_RECOMMENDATION_BOUNDARY_NO_ADOPTION` |
| `G8 Trial Preparation` | 参与者、测量、成功标准和发布交接明确 | `PASS_PLAN_ONLY_TRIAL_NOT_AUTHORIZED` |
| `G8 Release and Adoption` | trial、release、deployment、adoption 分开记录 | `NOT_READY` |

## 6. Stop Rules（停止规则）

任一情况发生时停止当前工作流：

- 需要修改历史 Evidence 或把当前文档伪装成旧快照；
- DBOS 被要求推理、规划、调度 Agent 或授予 Permission；
- SAEE 被要求直接改变 DBOS 或主体状态；
- Demo 需要真实凭证、生产数据或未治理外部动作；
- 外部试用缺少 source freeze、clean clone、`DQ-010` 或 external contact authorization；
- validator、负向测试或 identity continuity（身份连续性）失败；
- 现有能力 Owner 不明确，可能形成第二套 canonical truth（规范事实）。

## 7. Agent Recommendation Gate（智能体推荐闸门）

当前结论：

```text
RECOMMEND_BOUNDED_DBOS_LOCAL_PREVIEW=true
RECOMMEND_DEVELOPER_PREVIEW_RELEASE=false
```

只有 DP-2 至 DP-5D 的退出条件都有可复核证据或已记录的显式限制接受，并经 `DQ-009` 人工发布决定后，才可改为：

```text
RECOMMEND_DEVELOPER_PREVIEW_RELEASE=true
```

推荐对象仍是可信记录与评价基础设施预览，不是 Agent 平台、生产 Runtime、自动演化系统或事实认证服务。
