# DBOS Autonomy Policy Object Model v0.1（DBOS 自主策略对象模型 v0.1）

状态：`PROPOSED_FOR_REVIEW`

对象实例状态：`NOT_CREATED`

Schema（模式）状态：`NOT_DEFINED`

## 1. Definition（定义）

Autonomy Policy Object（自主策略对象）是未来用于表达某个 Entity（实体）在已验证 Capability（能力）、独立 Permission（权限）和明确范围内需要何种人工监督的不可执行政策表示。

它是 Proposed Extension Object（拟议扩展对象），不是 `object-contract-specification.md` 当前五类核心对象中的第六类，也不会因本模型存在而获得 `object_type`、Schema、SDK（软件开发工具包）类型、API（应用程序接口）或 Registry（登记表）。

```text
AUTONOMY_POLICY_OBJECT_NE_POLICY_INSTANCE=true
AUTONOMY_POLICY_OBJECT_NE_PERMISSION=true
AUTONOMY_POLICY_OBJECT_NE_AUTHORITY=true
AUTONOMY_POLICY_OBJECT_NE_EXECUTION=true
```

## 2. Field Set（字段集合）

用户要求的核心字段：

```text
policy_id
entity_reference
autonomy_mode
allowed_actions
restricted_actions
approval_required_actions
evidence_required
created_by
version
```

为保持范围、来源、生命周期和撤销可追溯，未来对象还必须定义：

```text
scope
constraints
policy_authority_reference
status
created_at
updated_at
effective_at
expires_at
revocation_reference
successor_reference
limitations
```

字段集合是概念合同，不是对象实例。

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 边界 |
|---|---|---|
| `policy_id` | Source 拥有的稳定策略标识 | 不创建 Entity、Permission 或 Authority |
| `entity_reference` | 被策略约束的唯一实体引用 | 必须已存在；策略不能创建或修改实体 |
| `autonomy_mode` | 三种受控自主模式之一 | 不是 Permission 或执行状态 |
| `scope` | 动作、能力、权限、环境、资源、风险、数据和时间交集 | 缺失维度保持 `UNKNOWN`，不代表无限 |
| `constraints` | 停止、阈值、例外、撤销和证据规则 | 只能收窄，不能扩大其他治理层 |
| `allowed_actions` | 可在其他层也允许时按当前模式评估的动作 | 列入不等于获准执行 |
| `restricted_actions` | 必须阻断、降级模式或升级人工复核的动作 | 不能由 Agent 自行解除 |
| `approval_required_actions` | 始终需要独立人工批准的动作 | 本字段优先于模式默认体验 |
| `evidence_required` | 策略判定和未来执行必须引用的证据类别 | 不产生 Evidence 或 E 等级 |
| `created_by` | 创建或提交该表示的可归因引用 | Creator（创建者）不自动拥有政策 Authority |
| `policy_authority_reference` | 支持策略生效的独立治理权力引用 | 解析不等于有效；必须独立验证 |
| `version` | 策略表示版本 | 与 Entity、Capability、Permission 和 Schema 版本分离 |
| `status` | 策略生命周期状态 | 不能由对象自行改变 |
| `created_at/updated_at` | Source 声明的形成和更新时间 | 未知为 `null`；禁止用读取时间补造 |
| `effective_at/expires_at` | 生效和过期边界 | `null` 不能解释为永不过期 |
| `revocation_reference` | 暂停或撤销材料引用 | 撤销历史不能删除 |
| `successor_reference` | 明确后继策略引用 | 后继不能覆盖前任历史 |
| `limitations` | 未知、适用边界和无效果声明 | 必填且至少一项 |

## 4. Controlled Values（受控值）

`autonomy_mode`：

```text
APPROVAL_REQUIRED
DELEGATED_AUTONOMY
FULL_AUTONOMY_WITHIN_SCOPE
```

`status`：

```text
DRAFT
PROPOSED
REVIEWED
ACTIVE
SUSPENDED
REVOKED
EXPIRED
SUPERSEDED
RETIRED
```

当前没有任何 `ACTIVE` 策略对象。

## 5. Scope Structure（范围结构）

未来 `scope` 至少表达：

```text
capability_references
permission_references
action_patterns
environment_references
input_constraints
output_constraints
side_effect_ceiling
resource_limits
risk_ceiling
data_classification
valid_from
valid_until
organization_boundary
```

- `action_patterns` 必须使用明确允许列表或确定性模式，不能使用“所有”“任意”“其他”等无限词；
- `permission_references` 缺失时对象不能成为 `ACTIVE`；
- `side_effect_ceiling` 不能超过 Capability、Permission 或风险政策允许范围；
- `valid_until` 未明确时对象保持 `PROPOSED/UNKNOWN`，不能成为永久授权；
- 范围内每个引用仍遵守 Reference ≠ Truth（引用不等于事实）。

## 6. Mode-specific Requirements（模式专属要求）

### `APPROVAL_REQUIRED`

- `approval_required_actions` 必须覆盖全部 `allowed_actions`；
- 每次动作必须引用事前批准；
- 不允许把策略级批准替代动作级批准。

### `DELEGATED_AUTONOMY`

- 必须具有明确 `allowed_actions/restricted_actions/approval_required_actions`；
- 必须具有阈值、异常、未知和冲突升级规则；
- 必须记录每次策略评估和动作证据。

### `FULL_AUTONOMY_WITHIN_SCOPE`

- 必须是精确白名单、固定版本、资源受限、可暂停和可撤销；
- 必须声明定期人工复核与持续 Evidence 要求；
- 不能包含被其他宪法或风险政策强制要求逐动作批准的动作；
- 不能包含 Policy、Identity、Permission、Evidence 或 Authority 自我修改动作。

## 7. Validation Rules（验证规则）

未来验证器必须拒绝：

- `policy_id`、`entity_reference`、`autonomy_mode`、`scope`、`constraints`、`created_by` 或 `version` 缺失；
- 未知模式或生命周期状态；
- `allowed_actions` 超出 Capability 或 Permission 范围；
- 同一动作同时允许且禁止但没有更严格优先级；
- `FULL_AUTONOMY_WITHIN_SCOPE` 使用无限 action、无过期、无撤销或无资源上限；
- `created_by` 被自动当作 `policy_authority_reference`；
- Policy 自我激活、自我续期、自我修改 Authority；
- 产生 Agent、Runtime、Entity、Capability Grant（能力授予）、Permission、Execution 或 Evidence 修改的字段；
- 试图覆盖 SAEE、身份宪法、能力宪法或历史证据。

结构 `PASS` 只表示未来对象符合所用 Schema 和治理规则，不表示策略已经批准、生效、执行或适用于现实客户。

## 8. Future SDK Impact（未来软件开发工具包影响）

未来 SDK 可以：

- 读取并序列化 Autonomy Policy Object；
- 验证字段、版本、引用和冲突；
- 在调用方提供完整 Capability、Permission、Context 和风险输入时，确定策略声明的是“需要人工批准”“范围内无需逐动作批准”还是“阻断/未知”；
- 返回解释、缺失条件和 Evidence 要求。

未来 SDK 不能：

- 创建、激活、扩大、续期或撤销 Policy Authority（策略权力）；
- 把评估结果变成 Permission、Authorization、Execution 或 Verification；
- 选择 Agent 目标、执行 Tool（工具）或修改 Runtime；
- 自动修改策略对象或历史 Evidence。

当前没有 Autonomy Policy SDK、Schema 或 Validator 实现。

## 9. Explicit Non-effects（明确无效果）

```text
AUTONOMY_POLICY_OBJECT_MODEL=PROPOSED_V0.1
AUTONOMY_POLICY_OBJECT_INSTANCE_COUNT=0
AUTONOMY_POLICY_SCHEMA=false
AUTONOMY_POLICY_VALIDATOR=false
AUTONOMY_POLICY_SDK=false
AUTONOMY_POLICY_API=false
POLICY_AUTHORITY_CREATED=false
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
