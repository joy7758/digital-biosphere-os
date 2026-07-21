# DBOS Object Contract Specification v0.1（DBOS 核心对象契约规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

实现状态：`NOT_STARTED`

Machine-readable Schema（机器可读模式）状态：`DEFINED_V0.1`

对象实例状态：`NOT_CREATED`

规范角色：Developer Infrastructure Specification（开发者基础设施规范）

## 1. Purpose（目的）

DBOS Object Contract（DBOS 对象契约）定义开发者、Adapter（适配器）、未来 API（应用程序接口）和未来 SDK（软件开发工具包）交换核心治理对象时必须使用的统一语义。

本规范冻结 object vocabulary（对象词表）、字段含义、空值规则、版本边界和禁止效果。配套 Object Schema Layer（对象模式层）已把这些语义编码为 6 个 JSON Schema（JSON 模式）文件；Schema 存在不创建对象实例、代码类、数据库表、API endpoint（端点）或 SDK。

## 2. Core Principles（核心原则）

### 2.1 Object Contract ≠ Object Instance（对象契约不等于对象实例）

字段和规则只描述未来对象应如何表达。规范文件存在不表示任何 Entity、Capability、Execution、Evidence 或 Verification 对象已经形成。

### 2.2 Object ≠ Authority（对象不等于权力）

对象可以携带 Authority Reference（权力引用）或来源声明，但对象的创建、解析、传输、存储和验证都不产生治理权力。

### 2.3 Reference ≠ Truth（引用不等于事实本身）

可解析引用只证明在声明的 Namespace、Version 和 Source 中能定位记录，不证明记录真实、完整、当前有效或适用于某个决定。

### 2.4 Schema Definition ≠ Implementation（模式定义不等于实现）

即使未来形成 JSON Schema、Protocol Buffer（协议缓冲）或语言类型，也只表示结构契约；不表示 API、SDK、Runtime 或业务执行已经存在。

### 2.5 Unknown remains unknown（未知保持未知）

缺少来源、版本、状态、时间、唯一目标或证据时必须显式使用 `UNKNOWN` 或允许的 `null`，不得从目录、类名、框架类型、调用次数或相似字符串推断。

### 2.6 Objects are projections, not canonical owners（对象是投影，不是规范所有者）

API 或 SDK Object 是对规范 Source 的受范围投影。它不能取代 `registry/`、Evidence Store（证据存储）、Verification Record（验证记录）或其他明确的事实来源。

## 3. Core Object Types（核心对象类型）

v0.1 冻结五种 `object_type`：

```text
ENTITY
CAPABILITY
EXECUTION
EVIDENCE_REFERENCE
VERIFICATION
```

其他对象类型必须通过新的契约版本或 Extension Namespace（扩展命名空间）提出，不能占用上述含义。

## 3A. Proposed Autonomy Policy Extension Object（拟议自主策略扩展对象）

`autonomy-policy-object-model.md` 提出未来 Autonomy Policy Object（自主策略对象），用于表达 Entity（实体）在已验证 Capability（能力）、独立 Permission（权限）和明确 Scope（范围）内的人工监督方式。

该对象当前：

- 不是 v0.1 五类核心 `object_type` 的第六类；
- 没有 Object Schema（对象模式）、Validator（验证器）、SDK（软件开发工具包）类型、API（应用程序接口）或实例；
- 只能通过未来 Extension Namespace 或新的 Object Contract 版本申请进入机器契约；
- 不能创建 Policy Authority（策略权力）、Permission、Capability Grant（能力授予）或 Execution（执行）；
- 不能把 `FULL_AUTONOMY_WITHIN_SCOPE` 解释为无限权限；
- 不能修改 Identity、Evidence（证据）或 SAEE。

当前五类核心对象和 6 个 Schema 文件保持不变。

## 4. Common Field Contract（统一字段契约）

所有五类对象必须支持以下 8 个顶层字段：

| 字段 | 规范类型 | 语义 | v0.1 约束 |
|---|---|---|---|
| `object_id` | non-empty identifier（非空标识符） | 对象的稳定领域标识 | 必须等于该对象的专属 ID；不能由序列化过程随机生成 |
| `object_type` | controlled enum（受控枚举） | 五类核心对象之一 | 必须与专属契约一致 |
| `version` | contract version string（契约版本字符串） | 对象表示遵循的契约版本 | v0.1 必须为 `v0.1`；不是 Entity 生命周期版本 |
| `source` | Source descriptor or Reference Object（来源描述或引用对象） | 拥有或提供该记录的规范 Source | Cache、路径或 API host（主机）不能单独成为 Source |
| `status` | object-type status（对象类型状态） | 由具体对象契约定义的记录状态 | 不产生状态效果；不能与 resolution status 混用 |
| `created_at` | RFC 3339 timestamp or null（时间戳或空值） | Source 声明的对象首次形成时间 | 未知时为 `null`；不得用读取时间补造 |
| `updated_at` | RFC 3339 timestamp or null（时间戳或空值） | Source 声明的当前表示更新时间 | 未知时为 `null`；非空时不得早于 `created_at` |
| `limitations` | non-empty string array（非空字符串数组） | 未知项、范围、方法和使用限制 | 必须存在；无充分限制材料时使用 `UNKNOWN`，不得省略 |

### 4.1 ID normalization（标识符归一化）

v0.1 禁止同一对象拥有两个不一致的顶层身份：

| `object_type` | 专属 ID | 必须满足 |
|---|---|---|
| `ENTITY` | `entity_id` | `object_id == entity_id` |
| `CAPABILITY` | `capability_id` | `object_id == capability_id` |
| `EXECUTION` | `execution_id` | `object_id == execution_id` |
| `EVIDENCE_REFERENCE` | `evidence_id` | `object_id == evidence_id` |
| `VERIFICATION` | `verification_id` | `object_id == verification_id` |

不满足该关系必须返回 `CONFLICT` 或 `INVALID`，不能自动选择其中一个 ID。

### 4.2 Version semantics（版本语义）

`version` 表示 Object Contract representation version（对象契约表示版本），v0.1 固定为 `v0.1`。它不替代：

- Canonical Entity ID 中的身份版本；
- Source record version（来源记录版本）；
- API version（接口版本）；
- SDK package version（软件包版本）；
- Evidence、Verification 或协议自己的版本。

这些领域版本必须由相应 ID、Reference Object 或 Source metadata（来源元数据）表达。缺少兼容关系时返回 `VERSION_MISMATCH`，不得使用“最新版本”替代。

### 4.3 Source semantics（来源语义）

`source` 表示拥有对象含义的系统或 Namespace。对象专属 `source_reference` 表示该 Source 内部的具体记录。两者不可混用：

- `source` 回答“谁拥有这条记录的含义”；
- `source_reference` 回答“该来源中的哪一条记录支持本对象”。

只有专属契约要求 `source_reference` 时才出现该字段。Source 可解析不表示 Source 内容真实或独立验证。

### 4.4 Status separation（状态分离）

公共字段名 `status` 在每类对象中使用受控的类型专属词表。它必须与以下状态分开：

- Resolution Result（解析结果）：`RESOLVED/AMBIGUOUS/UNKNOWN/INVALID`；
- Entity `lifecycle_state`；
- Capability `verification_status`；
- Evidence `integrity_status`；
- Verification `verification_status`。

对象状态只陈述 Source 中记录的状态，不应用 Lifecycle 转换，不提升 C/E/V 等级。

### 4.5 Timestamp semantics（时间语义）

- 非空时间必须包含时区；
- `created_at` 和 `updated_at` 均来自可归因 Source；
- 文件系统修改时间、API 接收时间或当前时钟不能自动替代来源时间；
- `updated_at=null` 表示没有可信更新时间，不表示从未更新；
- 时间匹配不证明对象真实或有权力。

### 4.6 Limitations semantics（限制语义）

`limitations` 是必填的失败关闭字段。它至少应表达以下适用项：

- 未解析引用；
- 未验证身份或来源；
- 未确认的范围或环境；
- 不支持的版本；
- 缺失 Evidence 或 Verification；
- 对象明确不产生的治理效果。

空数组只有在 Source 明确声明“当前没有已知限制”且该声明可归因时才允许；空数组仍不表示无限适用。

## 5. Field Presence and Null Rules（字段存在与空值规则）

1. 公共字段和具体对象契约列出的字段必须全部存在；
2. 缺少必填字段返回 `INVALID`；
3. 只有具体契约明确允许的字段可以为 `null`；
4. `UNKNOWN` 是受控语义，不得用空字符串、空对象或缺失字段代替；
5. 未识别顶层字段在 v0.1 中返回 `INVALID`；
6. Extension（扩展）不得把自定义字段塞入核心对象；必须使用独立、带 Namespace 的扩展对象或未来契约版本；
7. 字段顺序不产生语义，也不能作为身份或摘要证据。

## 6. Reference Rules（引用规则）

所有以 `_reference` 结尾的字段必须：

- 使用 `canonical-reference-resolver-specification.md` 定义的 Reference Object，或由 Adapter 明确包装为该对象；
- 声明 Reference Type、Namespace、Version、Source 和 status；
- 在未解析时保留原始引用和 `UNRESOLVED_REFERENCE`；
- 不从 `RESOLVED` 推导 Authority、Truth、Permission、Activation 或 Verification；
- 不允许循环引用静默通过；
- 不允许外部 Namespace 覆盖 `dbio` 规范含义。

当前 `entity_support/` 的 string reference（字符串引用）是已有本地记录格式。未来 Adapter 必须显式包装，不能回写或重解释历史记录。

## 7. Immutability and History（不可变性与历史）

Object projection（对象投影）可以反映 Source 的新观察，但不得改写规范 Source 或历史 Evidence。对象变化必须保留：

- Source record version；
- previous object reference（前一对象引用）；
- 观察时间和限制；
- 冲突或撤销材料；
- 旧快照和旧验证结果。

API 返回新投影不等于历史对象被替换，也不自动形成 Documentation Evolution Evidence（文档演化证据）。

## 8. Cross-object Relationship（跨对象关系）

```text
Entity Object
  ├─ referenced by → Capability Object
  ├─ referenced by → Execution Object
  │                    └─ referenced by → Evidence Reference Object
  └─ target of → Verification Object
```

关系只表示引用。它不产生 containment authority（包含权力）、所有权、执行、事实、验证通过或状态传播。

## 9. Prohibited Effects（禁止效果）

任何核心对象都不得自动：

- 创建 Entity、Agent、Runtime 或 Digital Organism（数字生命体）；
- 产生 Capability Grant（能力授予）；
- 产生或修改 Permission；
- 触发模型、工具、任务或 Execution；
- 生成 Evidence Truth（证据真相结论）；
- 生成 Verification `PASS`；
- 应用 Lifecycle Transition（生命周期转换）；
- 计算 Fitness 或触发 SAEE Evolution（SAEE 演化）。

## 10. Object Validation Result（对象验证结果）

对象结构验证的规范顶层结果使用：

```text
PASS
FAIL
UNKNOWN
VERSION_MISMATCH
CONFLICT
```

`INVALID` 和 `UNRESOLVED_REFERENCE` 保留为诊断 `error_code`，分别确定性映射到顶层 `FAIL` 与 `UNKNOWN`。详细语义见 `object-error-semantics.md`、`validation-result-contract-specification.md`、`validation-error-object-model.md` 和 `validation-result-boundary-rules.md`。`PASS` 只表示对象符合本地结构与治理约束，不表示对象内容真实、获授权、已执行或被独立验证。

## 11. Contract Documents（契约文档）

- `entity-object-contract.md`
- `capability-object-contract.md`
- `execution-object-contract.md`
- `evidence-reference-object-contract.md`
- `verification-object-contract.md`
- `object-error-semantics.md`
- `ADR-020-object-contract.md`
- `validation-result-contract-specification.md`
- `validation-error-object-model.md`
- `validation-result-boundary-rules.md`
- `ADR-022-validation-result-contract.md`
- `autonomy-policy-specification.md`
- `autonomy-policy-object-model.md`
- `autonomy-boundary-rules.md`
- `autonomy-mode-comparison.md`
- `ADR-026-autonomy-policy.md`

机器可读 Schema 与治理入口：

- `schemas/common-object-schema.yaml`
- `schemas/entity-object-schema.yaml`
- `schemas/capability-object-schema.yaml`
- `schemas/execution-object-schema.yaml`
- `schemas/evidence-reference-object-schema.yaml`
- `schemas/verification-object-schema.yaml`
- `schema-version-policy.md`
- `ADR-021-object-schema-governance.md`

标准 JSON Schema Validation（模式验证）只检查结构。本地 Object Schema Validator（对象模式验证器）现已执行跨字段 ID 等价、Source 对齐、时间顺序和 `x-dbios-*` 无效果规则，但仍不解析外部事实或形成独立 Verification；Validation ≠ Verification。

## 12. Current State（当前状态）

```text
OBJECT_CONTRACT_VERSION=v0.1
OBJECT_CONTRACT_SEMANTICS=FROZEN_FOR_SPECIFICATION
MACHINE_READABLE_SCHEMA=DEFINED_V0.1
OBJECT_SCHEMA_FILE_COUNT=6
OBJECT_VALIDATOR_CREATED=true
OBJECT_VALIDATOR_IMPLEMENTATION=LOCAL_READ_ONLY_V0.1
VALIDATION_RESULT_CONTRACT=FROZEN_V0.1
OBJECT_INSTANCE_COUNT_CREATED_BY_THIS_SPEC=0
AUTONOMY_POLICY_OBJECT_MODEL=PROPOSED_V0.1
AUTONOMY_POLICY_OBJECT_INSTANCE_COUNT=0
AUTONOMY_POLICY_SCHEMA=false
API_IMPLEMENTATION=NOT_STARTED
SDK_IMPLEMENTATION=NOT_STARTED
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
SAEE_MODIFIED=false
```
