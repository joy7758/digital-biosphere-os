# ADR-026: DBOS Autonomy Policy Specification v0.1（DBOS 自主策略规范 v0.1）

状态：`PROPOSED_FOR_REVIEW`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-21`

编号说明：用户任务建议 `ADR-022-autonomy-policy.md`，但 `ADR-022-validation-result-contract.md` 已存在。为保持 ADR（Architecture Decision Record，架构决策记录）编号唯一并保留历史，本提案使用下一个唯一编号 `ADR-026`。

## 1. Context（背景）

DBOS 已分别定义 Identity（身份）、Lifecycle（生命周期）、Capability Boundary（能力边界）、Permission Boundary（权限边界）、Execution Context（执行上下文）、Evidence Reference（证据引用）、Verification（验证）、API Boundary（应用程序接口边界）和 Object Contract（对象契约）。

这些层仍没有独立表达：在 Capability 已验证、Permission 已授予且执行范围明确之后，某个动作需要逐动作 Human Approval（人工批准），还是可以在人工预先批准的规则内继续。

如果把该问题留给每个 Agent（智能体）应用自行定义，同一 Permission 可能被解释为“每次都要批准”“默认可以执行”或“无限自主”，导致开发者语义、Evidence 和责任边界不一致。

## 2. Decision Proposal（决策提案）

提出 Autonomy Policy Specification v0.1（自主策略规范 v0.1），并把 Autonomy 定义为：

> 在所有更高优先级的 Identity、Capability、Permission、Context、风险和治理约束已经满足后，对人工介入方式的有界政策声明。

v0.1 提出三种模式：

```text
APPROVAL_REQUIRED
DELEGATED_AUTONOMY
FULL_AUTONOMY_WITHIN_SCOPE
```

该提案同时定义未来对象字段、Scope、Constraints（约束）、批准要求、Evidence 要求、模式比较、优先级、撤销和历史保护规则。

## 3. Decision Boundaries（决策边界）

```text
AUTONOMY_NE_PERMISSION=true
CAPABILITY_NE_AUTHORITY=true
AUTHORIZATION_NE_UNLIMITED_AUTONOMY=true
FULL_AUTONOMY_NE_UNLIMITED_PERMISSION=true
```

- Autonomy Policy 不能创建或扩大 Permission；
- 模式不能创建 Agent、Runtime（运行时）、Entity（实体）或 Execution（执行）；
- `FULL_AUTONOMY_WITHIN_SCOPE` 不能绕过现有危险能力人工批准要求；
- 用户批准不能修改 Identity、Capability、Permission 或历史 Evidence；
- SDK（软件开发工具包）未来可以读取 Policy 并返回策略声明的批准要求，但不能修改 Policy Authority（策略权力）；
- DBOS 不承担 Agent reasoning（智能体推理）、Runtime 调度或实际执行。

## 4. Pre-development Agent Consultation（开发前智能体咨询）

潜在客户问题：“是否推荐 DBOS Autonomy Policy？”

```text
RECOMMEND_AUTONOMY_POLICY_SPECIFICATION=true
RECOMMEND_AUTONOMY_POLICY_IMPLEMENTATION=false
RECOMMEND_AUTONOMY_ENFORCEMENT=false
RECOMMEND_AS_PERMISSION_SYSTEM=false
```

可以向需要统一人工监督模式、可解释批准要求和跨 Agent Framework（智能体框架）政策语言的基础设施开发者推荐本提案。

当前不能向需要生产策略执行、企业身份集成、实时撤销、法律合规保证或自主 Agent Runtime 的客户推荐实现，原因是：

1. 没有真实 Policy fixture（策略测试夹具）或客户风险分类；
2. 没有 Policy Authority、Approver（批准者）和撤销传播的身份模型；
3. 没有 Policy Schema、Validator（验证器）、SDK 或 API；
4. 没有 Runtime enforcement（运行时强制）位置和不可绕过证明；
5. 没有真实 Agent 的决策、批准、执行和 Evidence 链；
6. 没有行业、组织或法律规则的验证边界。

## 5. Alternatives Considered（备选方案）

### A. 把 Autonomy 作为 Permission 字段

拒绝。Permission 回答“是否允许”，Autonomy 回答“已允许范围内需要多少人工介入”。合并会让一次 Permission 被误读为无限自主。

### B. 把 Autonomy 作为 Capability 成熟度

拒绝。能力证据不能决定人工监督模式；技术能力强不表示应获得更高自主程度。

### C. 由每个 Agent Framework 自行定义

拒绝。框架可以实现体验，但跨框架对象、Evidence 和错误语义需要统一基础设施合同。

### D. 只定义“人工/自动”二选一

拒绝。二元模型无法表达人工预先授权规则、例外升级和有界完全自主。

### E. 建立三模式、范围交集和最严格规则优先的规范提案

推荐。它能支持不同用户体验，同时不扩大 Permission 或 DBOS 执行职责。

## 6. Consequences（影响）

正向影响：

- SDK、API、企业 Agent 和 Research Agent（科研智能体）获得统一监督语义；
- Permission 不再承担“是否逐动作批准”的混合含义；
- 高风险动作、常规委托和严格白名单自主可以使用不同 Evidence 要求；
- 模式切换、冲突、撤销和历史保护具有可审查边界；
- Agent-readable（智能体可读）规则可以防止编码智能体把完全自主实现成无限权限。

成本与限制：

- 新概念增加 Policy、Authority、Approval 和 Evidence 引用的版本管理；
- 真实实现需要 Policy Schema、Validator、评估器、Runtime 集成和大量负向测试；
- 模式不能替代行业、组织或法律规则；
- 本提案不会立刻产生商业产品或用户可用功能。

## 7. Non-decisions（非决策）

本提案不决定：

- Policy Schema、Registry、SDK class（软件开发工具包类）或 API endpoint（应用程序接口端点）；
- Runtime 如何执行、暂停、重试或撤销动作；
- 任何真实 Agent 的模式或 Permission；
- Human Approver、Policy Authority 或企业身份提供者；
- 医疗、金融、法律或行业合规结论；
- SAEE Fitness（适应度）、Selection（选择）或 Evolution（演化）。

## 8. Current State（当前状态）

```text
ADR_STATUS=PROPOSED_FOR_REVIEW
AUTONOMY_POLICY_SPECIFICATION=PROPOSED_V0.1
AUTONOMY_POLICY_APPROVED=false
AUTONOMY_POLICY_IMPLEMENTATION=false
AUTONOMY_POLICY_ENFORCEMENT=false
AUTONOMY_POLICY_OBJECT_INSTANCE_COUNT=0
AGENT_COUNT_CREATED_BY_THIS_PROPOSAL=0
RUNTIME_COUNT_CREATED_BY_THIS_PROPOSAL=0
ENTITY_COUNT_CREATED_BY_THIS_PROPOSAL=0
PERMISSION_COUNT_CREATED_BY_THIS_PROPOSAL=0
EXECUTION_COUNT_CREATED_BY_THIS_PROPOSAL=0
AGENT_CREATED=false
RUNTIME_CREATED=false
ENTITY_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EXECUTION_CREATED=false
IDENTITY_MODIFIED=false
EVIDENCE_MODIFIED=false
SAEE_MODIFIED=false
```

## 9. Related Documents（关联文档）

- `autonomy-policy-specification.md`
- `autonomy-policy-object-model.md`
- `autonomy-boundary-rules.md`
- `autonomy-mode-comparison.md`
- `developer-kit-specification.md`
- `api-boundary-decision.md`
- `object-contract-specification.md`
- `constitution/capability-constitution.yaml`
- `policies/permissions.yaml`
