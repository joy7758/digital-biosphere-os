# DBOS API Object Contract Model v0.1（DBOS 应用程序接口对象契约模型 v0.1）

状态：`SPECIFICATION_ONLY`

Schema 状态：`NOT_DEFINED`

API 实现状态：`NOT_STARTED`

规范 Object Contract（对象契约）：`FROZEN_FOR_SPECIFICATION`

规范入口：`object-contract-specification.md`

## 1. Purpose（目的）

本模型定义未来 DBOS API 可以交换的五类概念对象边界。它不是 JSON Schema（JSON 模式）、OpenAPI 文档、代码类或已发布 API。

本文件保留 API 视角的解释模型；五类对象的统一字段、ID 等价、Version、Source、Status、空值和错误规则，以 `object-contract-specification.md` 及其五份类型契约为规范语义来源。两者冲突时，Object Contract Specification v0.1（对象契约规范 v0.1）优先；这不产生实现授权。

所有对象遵守：

```text
OBJECT_NE_ENTITY_INSTANCE=true
OBJECT_NE_AUTHORITY=true
OBJECT_NE_PERMISSION=true
REFERENCE_NE_TRUTH=true
STATUS_NE_STATE_EFFECT=true
```

## 2. Common Contract Rules（通用契约规则）

每个未来 API 对象必须：

- 使用显式 Reference（引用），不以文件路径或显示名称替代身份；
- 声明 object version（对象版本）和 Source（来源）；
- 区分 object status（对象状态）、resolution status（解析状态）和 domain state（领域状态）；
- 保留 `limitations`；
- 对未知值使用 `UNKNOWN` 或 `null`，不能推断；
- 不包含隐式 Permission、Agent activation（智能体激活）或 Runtime effect（运行时效果）；
- 只通过追加式关系引用 Evidence 和 Verification；
- 不把 API transport metadata（传输元数据）当作治理证据。

## 3. Entity Object（实体对象）

API 投影必须包含 `object-contract-specification.md` 的八个公共字段，并使用以下规范专属字段：

| 字段 | 语义 | 边界 |
|---|---|---|
| `entity_id` | Source 声明的规范 Entity ID | `object_id` 必须等于 `entity_id`；API 不签发或猜测 |
| `entity_type` | 受控实体分类 | Repository 不自动等于 Agent |
| `owner_reference` | Owner 声明引用 | 不表示 Owner 已认证 |
| `lifecycle_state` | Source 记录的生命周期状态 | 不应用转换；对象不等于 `ACTIVE` Entity |
| `source_reference` | Source 内部的实体记录引用 | 必须与公共 `source` 一致 |

Entity Object 只能表示或引用已存在的治理记录，不能因 API 序列化而创建 Agent、Runtime 或 Digital Organism。

## 4. Capability Object（能力对象）

API 投影必须包含八个公共字段，并使用以下规范专属字段：

| 字段 | 语义 | 边界 |
|---|---|---|
| `capability_id` | Capability Boundary 声明 ID | `object_id` 必须等于 `capability_id`；不等于能力实例 |
| `entity_reference` | 声明所关联的实体 | 关联不等于拥有或可执行 |
| `capability_name` | 受控或来源声明的能力名称 | 名称存在不证明能力存在 |
| `scope` | 声明覆盖范围 | 不得省略或扩大 |
| `constraints` | 限制与禁止条件 | 必须随对象返回 |
| `verification_status` | `UNKNOWN/UNVERIFIED/PENDING` 或有独立记录支持的状态 | 不等于 Permission 或 Capability Grant |

Capability Object 允许开发者声明和查询边界，不允许分配 Capability 或授予 Permission。

## 5. Execution Object（执行对象）

API 投影必须包含八个公共字段，并使用以下规范专属字段：

| 字段 | 语义 | 边界 |
|---|---|---|
| `execution_id` | 惰性 Execution Record ID | `object_id` 必须等于 `execution_id`；不证明执行发生 |
| `entity_reference` | 被记录主体的引用 | 不创建主体 |
| `task_reference` | 外部任务引用 | DBOS 不规划任务 |
| `context_reference` | 既有 Execution Context 引用 | API 不创建 Runtime |
| `input_reference` | 输入快照或引用 | 不复制敏感输入 |
| `output_reference` | 可选输出引用 | 缺失保持 `null` |

公共 `status` 当前只允许 `UNKNOWN/CREATED`；公共 `limitations` 必须说明对象不等于 Execution Result。

Execution Object 是执行事实的容器或引用，不是执行命令、模型调用或 Agent loop。

## 6. Evidence Reference Object（证据引用对象）

Evidence Reference Object 必须复用 Canonical Reference Object（规范引用对象）语义，而不是建立第二套 ID。

API 投影必须包含八个公共字段，并使用以下规范专属字段：

| 字段 | 语义 | 边界 |
|---|---|---|
| `evidence_id` | Evidence Reference Object ID | `object_id` 必须等于 `evidence_id`；不等于 Evidence payload |
| `execution_reference` | 相关 Execution Object 引用 | 解析不表示执行发生 |
| `source_reference` | Evidence Source 内的具体记录引用 | `RESOLVED` 不等于真实；必须与公共 `source` 一致 |
| `integrity_status` | `UNKNOWN/PENDING` 或证据支持的状态 | 不自动升级 |

公共 `version` 固定表示 Object Contract `v0.1`，不替代 Evidence 自身版本；公共 `limitations` 必须保留 Truth 和完整性边界。

## 7. Verification Object（验证对象）

API 投影必须包含八个公共字段，并使用以下规范专属字段：

| 字段 | 语义 | 边界 |
|---|---|---|
| `verification_id` | Verification Record 或 Run ID | `object_id` 必须等于 `verification_id`；引用不执行验证 |
| `target_reference` | 被验证对象、Claim 或 Evidence 引用 | 不创建或批准目标 |
| `verification_type` | 受控验证方法类别 | 不自动证明独立性 |
| `verification_status` | `UNKNOWN/PENDING` 或有完整 Source 支持的限定结果 | API 请求不能生成 `PASS` |

公共 `limitations` 必须保留方法、环境、证据和独立性限制；公共时间字段不能为 `PENDING` 伪造完成时间。

Verification Object 不等于 Review Approval、Certification、Capability Assignment 或 Permission。

## 8. Object Relationship Model（对象关系模型）

```text
Entity Object
  ├─ references → Capability Object
  ├─ references → Execution Object
  │                 └─ links → Evidence Reference Object
  └─ references → Evidence Reference Object
                         └─ supports → Verification Object
```

关系箭头只表示可解析引用，不表示所有权、真实性、授权、Permission 或自动状态传播。

## 9. Prohibited Object Fields（禁止对象字段）

未来通用对象不得包含或推导：

- `agent_created=true`；
- `runtime_started=true`；
- `permission_granted=true`；
- `capability_assigned=true`；
- `entity_activated=true`；
- `truth_confirmed=true`；
- `fitness_score`；
- `evolution_decision`；
- 未附 Evidence 和方法的 `verification_passed=true`。

## 10. Contract Freeze Gates（契约冻结闸门）

`object-contract-specification.md`、五份类型契约、`object-error-semantics.md` 和 `ADR-020-object-contract.md` 已完成语义层冻结。Machine-readable Schema（机器可读模式）、Validator（验证器）和 SDK 仍未创建。

进入 Schema 或 SDK 实现前，仍必须另行授权并完成：

1. 字段名称、必填性和空值语义；
2. Version 与 Namespace 规则；
3. 状态词表和状态转换所有权；
4. Digest、timestamp 和 provenance 格式；
5. 敏感字段、最小披露和 redaction（脱敏）规则；
6. 正向、负向和跨版本 conformance fixture（符合性测试夹具）；
7. 确认所有 authority/permission/runtime effects 保持 `NONE`。

## 11. Normative Object Contract Documents（规范对象契约文档）

- `object-contract-specification.md`；
- `entity-object-contract.md`；
- `capability-object-contract.md`；
- `execution-object-contract.md`；
- `evidence-reference-object-contract.md`；
- `verification-object-contract.md`；
- `object-error-semantics.md`；
- `ADR-020-object-contract.md`。

```text
OBJECT_CONTRACT_SEMANTICS=FROZEN_FOR_SPECIFICATION
MACHINE_READABLE_SCHEMA=NOT_CREATED
OBJECT_VALIDATOR=NOT_CREATED
OBJECT_INSTANCE_CREATED=false
```
