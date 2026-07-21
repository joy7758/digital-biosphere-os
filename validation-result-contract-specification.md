# DBOS Validation Result Contract Specification v0.1（DBOS 验证结果契约规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

本地实现对齐状态：`ALIGNED_V0.1`

规范角色：Developer Infrastructure Specification（开发者基础设施规范）

## 1. Purpose（目的）

Validation Result Contract（验证结果契约）冻结 DBOS Object Schema Validator（对象模式验证器）的统一输出语言，使不同开发者、Adapter（适配器）和未来 SDK（软件开发工具包）能够以相同字段、状态和边界解释本地验证结果。

本契约只表达“检查得到了什么诊断”。它不创建被检查对象、不记录真实业务事件、不批准能力、不授予权限，也不把本地结构检查提升为独立事实验证。

## 2. Core Principles（核心原则）

### 2.1 Validation Result ≠ Truth（验证结果不等于真相）

结果只说明声明的 Validator、Schema 和本地规则对调用方提供的表示做出了什么判断。即使结果为 `PASS`，也不证明 Source、Reference、Evidence 或业务事实真实。

### 2.2 PASS ≠ Authorization（通过不等于授权）

`PASS` 不产生 Permission、Capability Grant、Lifecycle Transition、Execution Authorization 或 Verification Approval。

### 2.3 FAIL ≠ Historical Rewrite（失败不等于历史改写）

`FAIL` 只追加诊断。它不能删除旧对象、旧 Evidence、旧 Snapshot、旧结果或历史摘要，也不能自动修改输入以使其通过。

### 2.4 Validator Result ≠ Permission（验证器结果不等于权限）

任何状态、错误、警告、提示、Schema 摘要或 Validation ID 都没有权限效果。

### 2.5 Unknown remains unknown（未知保持未知）

缺少外部 Source、唯一 Reference、独立 Evidence、可归因时间或持久化记录时必须使用 `UNKNOWN` 或允许的 `null`，不得补造成功、ID 或时间。

## 3. ValidationResult Object（验证结果对象）

每个 v0.1 结果必须包含以下 9 个顶层字段，字段缺失属于契约不合格：

| 字段 | 类型 | v0.1 语义 |
|---|---|---|
| `validation_id` | non-empty string or `null`（非空字符串或空值） | 已持久化结果的稳定 ID；本地瞬时结果没有可归因记录时必须为 `null` |
| `validator_version` | non-empty string（非空字符串） | 产生结果的 Validator 版本；当前为 `v0.1` |
| `target_reference` | non-empty string or `null` | 被检查对象的安全引用；缺少可信 `object_id` 时为 `null`，不创建对象 |
| `schema_reference` | object or `null`（对象或空值） | 所用 Schema 的 `$id` 与摘要；没有可选择 Schema 时为 `null` |
| `result` | controlled enum（受控枚举） | `PASS/FAIL/UNKNOWN/CONFLICT/VERSION_MISMATCH` 之一 |
| `errors` | array（数组） | Validation Error Object（验证错误对象）列表；`PASS` 时必须为空 |
| `warnings` | array（数组） | 不改变主结果的警告列表；没有警告时为空 |
| `limitations` | non-empty string array（非空字符串数组） | 本地方法、外部信息和禁止效果限制；必须至少一项 |
| `timestamp` | RFC 3339 string or `null`（时间字符串或空值） | 可归因的结果形成时间；本地瞬时结果不读取系统时钟补造，默认 `null` |

### 3.1 Schema Reference（模式引用）

非空 `schema_reference` 固定包含：

| 字段 | 语义 |
|---|---|
| `schema_id` | 明确使用的不可变 Schema `$id`；不得使用可变 `latest` |
| `schema_digest` | `sha256:<hex>` 或 `null`；摘要缺失不得补造 |

Schema 摘要只标识验证输入标准，不证明 Schema 正确、可信、已发布或具有权力。

### 3.2 Transient Local Result（本地瞬时结果）

当前本地 Validator 不建立持久化 Validation Registry（验证登记表），因此：

```text
validation_id=null
timestamp=null
```

这两个 `null` 是诚实的未记录状态，不是错误，也不表示验证没有发生。未来持久化层必须追加新记录，不能回写或伪造当前瞬时结果。

## 4. Result States（结果状态）

### 4.1 `PASS`（通过）

表示标准 JSON Schema（JSON 模式）和本地 DBOS 治理规则均未发现违反。

约束：

- `errors=[]`；
- 可以存在 `warnings` 和 `limitations`；
- 不表示 Truth、Verification、Authorization、Permission、Execution 或 Entity Activation。

### 4.2 `FAIL`（失败）

表示存在明确结构、类型、必填性、未知字段或治理禁止效果违反。

约束：

- `errors` 至少一项；
- 至少一项错误的 `error_code=INVALID`；
- 不自动修复、删除、覆盖或重新登记输入。

### 4.3 `UNKNOWN`（未知）

表示本地结构可处理，但缺少必要的外部 Source、Evidence、Reference resolution（引用解析）、独立性或其他事实信息。

约束：

- 不是默认成功；
- 不推断不存在；
- 补充信息前保持失败关闭。

### 4.4 `CONFLICT`（冲突）

表示对象 ID、Schema 选择、Source owner（来源所有者）或其他规范声明互不兼容，无法唯一选择。

约束：

- 不自动选择最新记录；
- 不合并身份、来源或状态；
- 保留不敏感的冲突位置。

### 4.5 `VERSION_MISMATCH`（版本不匹配）

表示对象、Schema 或契约版本不兼容。

约束：

- 不自动升级、降级或选择 `latest`；
- 不改写历史对象；
- 必须保留观察到的字段位置和版本规则引用。

## 5. Deterministic Precedence（确定性优先级）

同一结果存在多类诊断时，主状态固定为：

```text
FAIL
  > VERSION_MISMATCH
  > CONFLICT
  > UNKNOWN
  > PASS
```

主状态只用于确定性分类；`errors` 必须保留全部可安全披露的诊断。较高优先级不删除较低优先级信息。

## 6. Error and Warning Rules（错误与警告规则）

- `errors` 和 `warnings` 使用 `validation-error-object-model.md` 的统一对象格式；
- `errors[*].severity` 必须为 `ERROR`；
- `warnings[*].severity` 必须为 `WARNING`；
- `resolution_hint` 只是人工处置提示，不能执行修复；
- 诊断不能泄露 Secret、Token、Credential、Evidence 正文或受限目标是否存在；
- Warning 不得把非 `PASS` 状态提升为 `PASS`。

## 7. Immutability and Retention（不可变性与保留）

Validation Result 在内存中使用不可变封装。未来持久化时必须追加新结果，并保留：

- 旧 `validation_id`；
- 旧 Schema Reference；
- 旧结果、错误、警告和限制；
- 原始时间或 `null`；
- 后继结果与旧结果之间的显式关系。

禁止覆盖旧结果、修改历史摘要或用新 `PASS` 自动修复旧 `FAIL`。

## 8. Layer Boundaries（层边界）

```text
Validation Result != Truth
Validation Result != Verification Record
Validation Result != Authorization
Validation Result != Permission
Validation Result != Execution
Validation Result != Entity
Validation Result != SAEE Evolution
```

详细禁止规则见 `validation-result-boundary-rules.md`。API Error（接口错误）仍由 `api-error-model.md` 管理；Validation Result 不是 HTTP response（响应）或 API authorization decision（接口授权决定）。

## 9. Current State（当前状态）

```text
VALIDATION_RESULT_CONTRACT_VERSION=v0.1
VALIDATION_RESULT_FIELD_COUNT=9
RESULT_STATUS_COUNT=5
LOCAL_VALIDATOR_OUTPUT_ALIGNED=true
VALIDATION_REGISTRY_CREATED=false
VALIDATION_ID_AUTO_GENERATED=false
TIMESTAMP_AUTO_GENERATED=false
AUTO_REPAIR=false
PERMISSION_EFFECT=NONE
AUTHORITY_EFFECT=NONE
EXECUTION_EFFECT=NONE
ENTITY_CREATION_EFFECT=NONE
SAEE_EFFECT=NONE
SDK_CREATED=false
API_CREATED=false
```
