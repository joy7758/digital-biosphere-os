# DBOS Autonomy Boundary Rules v0.1（DBOS 自主边界规则 v0.1）

状态：`PROPOSED_FOR_REVIEW`

执行效果：`NONE`

## 1. Purpose（目的）

本文件冻结 Autonomy Policy（自主策略）与 Identity（身份）、Capability（能力）、Permission（权限）、Authorization（授权）、Execution（执行）、Evidence（证据）、Verification（验证）和 SAEE 之间的禁止效果与优先级。

## 2. Fundamental Boundaries（基本边界）

```text
AUTONOMY_NE_PERMISSION=true
AUTONOMY_NE_CAPABILITY=true
AUTONOMY_NE_AUTHORITY=true
AUTONOMY_NE_EXECUTION=true
AUTONOMY_NE_VERIFICATION=true
```

- Autonomy Mode（自主模式）只描述人工介入方式；
- `allowed_actions` 只是在其他层已经允许时可进入策略判断的集合；
- Policy 创建、读取、解析、验证或选择都不创建 Permission；
- Policy Authority Reference（策略权力引用）只指向独立治理记录，不由 Policy 自己签发；
- Human Approval（人工批准）是有范围、有时效的决定引用，不是无限 Permission 或事实证明。

## 3. Effective Scope Intersection（有效范围交集）

任何未来可继续动作必须位于所有适用约束的交集：

```text
effective_action_scope
  = verified_capability_scope
  ∩ valid_permission_scope
  ∩ applicable_autonomy_policy_scope
  ∩ execution_context_scope
  ∩ risk_policy_scope
  ∩ organization_and_legal_scope
```

Autonomy Policy 只能收窄该交集，不能扩大它。任一集合为空、未知、冲突、过期、暂停或撤销时，结果必须是 `BLOCKED/UNKNOWN`，不能选择更宽模式。

## 4. Full Autonomy Boundary（范围内完全自主边界）

禁止以下推导：

```text
FULL_AUTONOMY_WITHIN_SCOPE
  -> UNLIMITED_PERMISSION

FULL_AUTONOMY_WITHIN_SCOPE
  -> GLOBAL_SCOPE

FULL_AUTONOMY_WITHIN_SCOPE
  -> NO_HUMAN_ACCOUNTABILITY
```

`FULL_AUTONOMY_WITHIN_SCOPE`：

- 不能覆盖现有危险能力、高风险、外部动作、修改或自我演化的强制人工批准规则；
- 不能使用无限动作、无期限、无资源上限、无撤销、无 Evidence 或无责任主体的范围；
- 不能允许 Agent（智能体）修改自身 Policy、Permission、Identity、Capability、Evidence 或 Authority；
- 不能把没有逐动作批准解释为没有人工责任；策略本身仍需事前人工批准和定期复核；
- 不能因执行成功次数增加而自动扩大范围或升级模式。

## 5. Approval Boundary（批准边界）

禁止：

```text
USER_APPROVAL
  -> HISTORICAL_EVIDENCE_MODIFICATION

USER_APPROVAL
  -> IDENTITY_CHANGE

USER_APPROVAL
  -> UNBOUNDED_FUTURE_ACTIONS
```

批准规则：

- 必须绑定批准者引用、策略版本、Entity、Action、Capability、Permission、Context、时间和限制；
- 必须在动作前产生；事后确认不能补造成事前批准；
- 批准记录可被撤销或过期，但不能从历史中删除；
- Policy 创建者、SDK（软件开发工具包）、API（应用程序接口）、Agent、Runtime（运行时）或 Validator（验证器）不能自动成为 Human Approver（人工批准者）；
- 一次批准不自动覆盖后继策略、新版本、新环境或相似动作；
- 批准不证明执行发生、成功或产生可信 Evidence。

## 6. Identity and Capability Boundary（身份与能力边界）

Autonomy Policy 不能：

- 创建、激活、合并、重命名、继承或退休 Entity；
- 把 Repository（仓库）、Service（服务）、Tool（工具）或 Agent 名称推断为身份；
- 创建 Capability Object（能力对象）、能力声明、能力验证或 Capability Grant（能力授予）；
- 扩大 Capability 的输入、输出、环境、版本、副作用或 Evidence 范围；
- 把某种自主模式解释为主体更“智能”、更可信或具备更高能力。

## 7. Permission and Authority Boundary（权限与权力边界）

Autonomy Policy 不能：

- 创建、推导、扩大、委托、续期、撤销或替代 Permission；
- 把 Authorization Record（授权记录）、用户偏好或模式选择转成无限 Permission；
- 把 `created_by`、文件 Owner（所有者）、Repository maintainer（仓库维护者）或调用方账户当作 Policy Authority；
- 把 Validator `PASS`、Reference `RESOLVED` 或 Evidence 存在当作 Authority；
- 修改 `policies/permissions.yaml` 或绕过其中需要确认/禁止的动作；
- 在 Permission 未知或冲突时用自主模式继续执行。

## 8. Execution and Runtime Boundary（执行与运行时边界）

Autonomy Policy 只提供未来策略输入或决定引用。它不能：

- 创建或启动 Agent、Runtime、模型、进程、Tool 或工作流；
- 创建 Execution Result（执行结果）、Event（事件）或行为事实；
- 调度、重试、取消、恢复或自我修改任务；
- 因模式为 `DELEGATED_AUTONOMY` 或 `FULL_AUTONOMY_WITHIN_SCOPE` 而自动调用外部系统；
- 把策略评估 `ALLOW_WITHIN_SCOPE` 解释为动作已经发生。

未来 Runtime 必须位于 DBOS 外部，并独立执行 Permission、Approval、Context 和 Evidence 约束。

## 9. Evidence and History Boundary（证据与历史边界）

Autonomy Policy、User Approval 或模式变更不能：

- 修改、删除、覆盖、重新签名或重算历史 Evidence；
- 把缺失的批准、时间戳、执行结果或资源记录补造成已发生；
- 因策略后来放宽而把旧阻断改写为允许；
- 因策略后来收紧而把旧合规执行改写为未发生；
- 自动提升 E/V/C 等级或 Verification 状态；
- 把连续日志存在解释为 Evidence Truth（证据真相）。

策略变化必须产生新的版本和追加式 change reference（变化引用），旧 Policy、Approval、Decision 和 Evidence 保持可定位。

## 10. SAEE Boundary（SAEE 边界）

Autonomy Policy 是 DBOS 的执行监督边界，不是 SAEE 的 Fitness（适应度）、Selection（选择）或 Evolution（演化）模型。

- 模式选择不计算 Fitness；
- 自主程度不表示进化阶段或 Digital Organism（数字生命体）资格；
- 策略效果、成功率或使用量不能自动触发 SAEE Evolution；
- SAEE 解释不能直接修改 Autonomy Policy、Permission 或执行范围。

```text
AUTONOMY_POLICY_REPLACES_SAEE=false
AUTONOMY_MODE_HAS_FITNESS_EFFECT=false
AUTONOMY_MODE_HAS_EVOLUTION_EFFECT=false
```

## 11. Conflict and Revocation Rules（冲突与撤销规则）

- 多项 Policy 同时适用时，选择更严格要求；无法唯一比较时返回 `CONFLICT` 并阻断；
- Policy 与 Capability、Permission、风险或组织政策冲突时，Autonomy Policy 不能获胜；
- Permission 或 Authority 撤销后，未来动作立即失去策略继续基础；
- Policy 撤销不能删除撤销前的决定、执行或 Evidence；
- 撤销传播失败时必须停止新动作；
- Agent 或 Runtime 不能忽略、延迟或覆盖撤销信号。

## 12. Future SDK Boundary（未来软件开发工具包边界）

未来 SDK 可以读取 Policy 并确定 Policy 声明的人工批准要求，但输出最多为：

```text
APPROVAL_REQUIRED
ALLOW_WITHIN_SCOPE
BLOCKED
UNKNOWN
CONFLICT
```

`ALLOW_WITHIN_SCOPE` 不是 Permission、Authorization 或 Execution command（执行命令）。SDK 不能修改 Policy Authority、选择更宽模式、自动批准、调用 Agent/Runtime 或修复历史 Evidence。

## 13. Explicit Non-effects（明确无效果）

```text
AUTONOMY_POLICY_ENFORCEMENT=false
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
