# DBOS Autonomy Policy Specification v0.1（DBOS 自主策略规范 v0.1）

状态：`PROPOSED_FOR_REVIEW`

实现状态：`NOT_STARTED`

策略实例：`0`

规范角色：Architecture Specification Proposal（架构规范提案）

## 1. Purpose（目的）

Autonomy Policy（自主策略）描述一个已识别数字实体在已验证 Capability（能力）、独立 Permission（权限）、明确 Scope（范围）和适用治理约束内，可以在多大程度上无需逐动作人工批准而运行。

它回答：

> 对于一个已经被允许的动作，Human Oversight（人工监督）必须在何时、以什么形式介入？

它不回答实体是谁、技术上能做什么、是否获准做某事、是否拥有治理权力，也不执行动作。

```text
IDENTITY
  -> VERIFIED_CAPABILITY
  -> SEPARATE_PERMISSION
  -> APPLICABLE_AUTONOMY_POLICY
  -> APPROVAL_REQUIREMENT
  -> EXTERNAL_EXECUTION
  -> EVIDENCE
```

该链条是未来治理顺序，不表示当前存在 Agent（智能体）、Runtime（运行时）、执行引擎、策略评估器或真实执行。

## 2. Core Separation（核心分离）

```text
AUTONOMY_NE_PERMISSION=true
CAPABILITY_NE_AUTHORITY=true
AUTHORIZATION_NE_UNLIMITED_AUTONOMY=true
POLICY_NE_EXECUTION=true
APPROVAL_NE_EXECUTION=true
```

| 层 | 回答的问题 | Autonomy Policy 不得替代 |
|---|---|---|
| Identity（身份） | 谁是被治理主体？ | 不能创建、合并或修改身份 |
| Capability | 主体在证据范围内技术上能做什么？ | 不能声明、验证或授予能力 |
| Permission | 该主体是否可以执行某个动作？ | 不能创建、扩大或撤销权限 |
| Authorization（授权） | 哪个可归因决定支持某个范围和时间内的动作？ | 不能把一次批准扩展为无限自主 |
| Autonomy Policy | 已获允许动作需要何种人工介入？ | 不能扩大其他层允许的动作集合 |
| Execution Context（执行上下文） | 动作将在什么环境、输入和限制下发生？ | 不能创建 Runtime 或执行结果 |
| Evidence（证据） | 决定和动作留下什么可追溯材料？ | 不能修改或删除历史证据 |
| Verification（验证） | 哪些声明在何种方法和范围内得到检查？ | 不能产生 Permission 或 Authority（权力） |

## 3. Autonomy Modes（自主模式）

v0.1 定义三种模式。模式名称是受控状态常量，不表示执行授权。

### 3.1 `APPROVAL_REQUIRED`（请求批准模式）

流程：

```text
Agent proposes action（智能体提出动作）
  -> scoped Human Approval（有范围的人工批准）
  -> external Execution（外部执行）
  -> Evidence record（证据记录）
```

规则：

- 每个动作在执行前都必须具有独立、可归因、未过期且范围匹配的批准记录；
- 批准必须绑定 Entity、Action、Capability、Permission、Context、时间窗口和限制；
- 批准不能复用于范围外动作，也不能由 Agent、SDK（软件开发工具包）或 Runtime 自行签发；
- 缺少批准、批准冲突、过期或撤销时保持阻断；
- 适用于高风险、不可逆、医疗、金融、法律、生产发布、论文最终发布等需要逐动作人工决定的场景；该示例不是合规认证。

### 3.2 `DELEGATED_AUTONOMY`（委托自主模式）

流程：

```text
Human defines bounded policy（人工定义有界策略）
  -> Agent evaluates an in-scope action（智能体判断范围内动作）
  -> external Execution（外部执行）
  -> per-action Evidence（逐动作证据）
  -> exception escalation（例外升级）
```

规则：

- 人工必须预先批准策略本身、允许动作、限制动作、资源上限、风险上限、有效期和撤销条件；
- 只有同时被 Capability、Permission 和 `allowed_actions` 覆盖的动作才可在无逐动作批准时继续；
- 命中 `restricted_actions`、阈值、冲突、未知或环境变化时必须停止并请求人工批准；
- 每次策略判断和外部执行都必须留下可归因 Evidence；
- 适用于日常科研辅助、企业流程和有明确例外升级机制的中风险任务。

### 3.3 `FULL_AUTONOMY_WITHIN_SCOPE`（范围内完全自主模式）

定义：在人工事先批准的精确 Policy Scope（策略范围）内，若 Capability、Permission、风险政策、环境条件和其他治理规则均允许，动作可以不要求逐动作人工批准。

规则：

- “范围内完全自主”不等于全局自主、无限权限、不可撤销或脱离监督；
- 作用范围必须是动作允许列表、实体、能力、Permission、环境、资源、时间、数据敏感度、风险和副作用边界的交集；
- 任何范围外动作、未知状态、版本冲突、策略过期、撤销信号或 Evidence 缺失都必须停止；
- 现有 `constitution/capability-constitution.yaml` 对危险、高风险、外部、修改或自我演化能力规定的人工批准要求仍优先；本模式不能绕过；
- 必须具有逐动作 Evidence、资源使用记录、异常记录、撤销传播和定期人工复核；
- 当前 DBOS 没有可执行该模式的 Agent、Runtime 或策略引擎。

## 4. Scope Model（范围模型）

每项未来策略必须显式限定：

| 范围维度 | 最低要求 |
|---|---|
| Subject（主体） | 唯一 `entity_reference` |
| Capability | 已验证且受 Evidence 限定的能力引用集合 |
| Permission | 独立、有效、未撤销且范围匹配的权限引用 |
| Action（动作） | 精确允许、限制和需要批准的动作集合 |
| Environment（环境） | 允许的环境引用和版本 |
| Input/Output（输入/输出） | 数据类型、敏感度、来源和输出边界 |
| Side Effect（副作用） | 允许的最大副作用类别 |
| Resource（资源） | Token、Compute、Storage、Data Access 和 Human Attention（令牌、计算、存储、数据访问和人工注意力）上限 |
| Risk（风险） | 允许的最高风险等级和触发阈值 |
| Time（时间） | 生效、过期和复核窗口 |
| Geography/Organization（地域/组织） | 适用时明确组织、账户或地域边界 |

未声明的范围维度保持 `UNKNOWN`，不能解释为无限制。

## 5. Constraints（约束）

未来策略至少必须包含：

- `allowed_actions`：在其他治理层也允许时，可按当前模式评估的动作；
- `restricted_actions`：必须停止、降级模式或升级人工复核的动作；
- `approval_required_actions`：始终需要独立人工批准的动作；
- 资源、时间、环境、数据、风险和副作用阈值；
- 失败、异常、冲突和不确定性的停止规则；
- suspension/revocation（暂停/撤销）传播要求；
- Evidence、保留、复核和审计要求。

策略不能包含创建 Permission、扩大 Capability、修改 Identity、删除 Evidence、创建 Agent/Runtime 或修改自身 Authority 的效果。

## 6. Approval Requirement（批准要求）

### 策略级批准

所有三种模式都需要策略在成为未来 `ACTIVE` 状态前获得可归因治理 Authority Reference（权力引用）和人工批准。创建者、提交者或文件所有者不自动成为批准者。

### 动作级批准

- `APPROVAL_REQUIRED`：所有动作都需要；
- `DELEGATED_AUTONOMY`：范围外、受限、阈值触发、冲突或未知动作需要；
- `FULL_AUTONOMY_WITHIN_SCOPE`：范围内动作通常不需要逐动作批准，但任何其他宪法、Permission、风险政策或外部法律/组织规则要求的批准仍必须执行。

批准必须发生在执行之前。事后确认不能补造成事前批准，Human Approval（人工批准）也不证明动作已执行或成功。

## 7. Evidence Requirement（证据要求）

未来每次策略评估至少应引用：

```text
policy_reference
policy_version
entity_reference
capability_references
permission_references
action_reference
execution_context_reference
autonomy_mode
policy_evaluation_result
approval_reference_or_not_required_reason
constraint_evaluation
resource_boundary
decision_timestamp
limitations
```

如果外部 Runtime 随后执行，还应追加 Execution、Event、Output、Resource usage（资源使用）、Failure（失败）和 Evidence 引用。策略文档本身不产生这些记录。

Evidence 要求不表示 Evidence 已存在、真实或达到某个 E 等级。历史 Evidence 只追加；策略变更、批准或用户选择不能覆盖、删除或重新解释旧记录。

## 8. Evaluation Order and Precedence（判定顺序与优先级）

未来评估器必须依次检查：

1. Entity Reference 是否唯一解析且未被策略修改；
2. Capability 是否在声明环境和 Evidence 范围内得到验证；
3. 独立 Permission 是否允许该动作、范围和时间；
4. Autonomy Policy 是否适用、有效、未撤销且版本明确；
5. 其他宪法、风险、组织和批准要求是否更严格；
6. 当前模式是否允许不经逐动作批准继续；
7. Evidence 要求是否能够满足；
8. 仅向外部 Runtime 返回受限的“需要批准/范围内可继续/阻断”策略结果。

有效动作集合必须满足：

```text
effective_actions
  <= verified_capability_scope
  ∩ permission_scope
  ∩ autonomy_policy_scope
  ∩ execution_context_constraints
  ∩ risk_and_governance_constraints
```

任一层拒绝、未知、冲突、过期或撤销时，Autonomy Policy 不能使动作继续。最严格规则优先。

## 9. Policy Lifecycle（策略生命周期）

未来状态：

```text
DRAFT
  -> PROPOSED
  -> REVIEWED
  -> ACTIVE
  -> SUSPENDED / REVOKED / EXPIRED / SUPERSEDED
  -> RETIRED
```

- `DRAFT/PROPOSED/REVIEWED` 均不能支持执行；
- `ACTIVE` 需要独立 Authority、人工批准、版本、范围、有效期和 Evidence 要求；
- `SUSPENDED/REVOKED/EXPIRED` 必须阻断新动作并保留历史决定；
- `SUPERSEDED` 必须引用后继策略，不能原地覆盖；
- 策略不能自我激活、自我续期、自我扩大或撤销治理记录。

本规范不创建策略登记表、生命周期记录或策略实例。

## 10. Research Agent Application（科研智能体应用方式）

未来 Research Agent（科研智能体）可以按任务风险选择：

- 文献检索、格式检查等低副作用动作：在独立 Permission 和策略范围内评估 `DELEGATED_AUTONOMY`；
- 数据删除、外部邮件、费用、敏感数据、作者身份和论文最终发布：保持 `APPROVAL_REQUIRED`；
- `FULL_AUTONOMY_WITHIN_SCOPE` 只能用于严格白名单、可撤销、资源受限、证据连续且不被其他规则要求人工批准的任务。

这只是未来应用映射，不创建 Research Agent Pilot（科研智能体试点）、Agent、Runtime、Capability、Permission 或执行。

## 11. Current State（当前状态）

```text
AUTONOMY_POLICY_SPECIFICATION=PROPOSED_V0.1
AUTONOMY_POLICY_APPROVED=false
AUTONOMY_POLICY_SCHEMA=false
AUTONOMY_POLICY_VALIDATOR=false
AUTONOMY_POLICY_API=false
AUTONOMY_POLICY_SDK=false
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
PERMISSION_GRANTED=false
EXECUTION_CREATED=false
IDENTITY_MODIFIED=false
EVIDENCE_MODIFIED=false
SAEE_MODIFIED=false
```

## 12. Related Documents（关联文档）

- `autonomy-policy-object-model.md`
- `autonomy-boundary-rules.md`
- `autonomy-mode-comparison.md`
- `ADR-026-autonomy-policy.md`
- `constitution/capability-constitution.yaml`
- `policies/capability-policy.yaml`
- `policies/permissions.yaml`
- `api-boundary-decision.md`
- `object-contract-specification.md`
- `developer-kit-specification.md`
