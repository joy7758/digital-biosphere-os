# DBOS Object Error Semantics v0.1（DBOS 对象错误语义 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

实现状态：`LOCAL_VALIDATOR_ALIGNED_V0.1`

## 1. Purpose（目的）

本文件定义 Object Contract validation（对象契约验证）的五类非成功语义。它们描述对象结构和引用问题，不是 HTTP 状态码、编程语言异常、Permission 决定或真实性结论。

## 2. Error Codes（错误代码）

### 2.1 `UNKNOWN`

对象结构基本可识别，但一个或多个受控值缺少可信 Source，无法确定。

要求：

- 保留未知字段位置和原始 Source；
- 不使用空字符串或默认成功替代；
- 不把未知解释为不存在、失败、撤销或低风险；
- 不自动补建对象。

### 2.2 `INVALID`

对象违反字段集合、类型、必填性、空值、ID 一致性或禁止字段规则。

要求：

- 返回字段路径和被违反的规则；
- 不进行部分成功投影；
- 不访问未经允许的外部 Source；
- 不把结构错误降级为 `UNKNOWN`。

### 2.3 `VERSION_MISMATCH`

对象公共 `version` 不是 `v0.1`，或对象、Reference、Source 和消费者之间缺少已批准的兼容关系。

要求：

- 返回 requested（请求）与 observed（观察）版本；
- 不自动升级、降级或选择“最新”；
- 保留旧版本对象和验证结果；
- 不通过改写历史对象消除差异。

### 2.4 `CONFLICT`

同一 `object_id`、专属 ID、Source、Version 或状态存在两个以上互不兼容的声明，无法按规范唯一选择。

要求：

- 返回冲突维度和允许披露的引用；
- 不选择路径最近、时间最新或最相似的对象；
- 不自动合并 Entity、Capability、Evidence 或 Verification；
- 要求更精确 Source、Version 或独立治理决定。

`object_id` 与专属 ID 不相等时，如果对象仍可识别为同一候选记录，使用 `CONFLICT`；如果结构本身无法识别，使用 `INVALID`。

### 2.5 `UNRESOLVED_REFERENCE`

对象结构有效，但一个必需 Reference Object 在声明的 Namespace、Version 和 Source 中没有得到唯一 `RESOLVED` 结果。

要求：

- 保留原始 Reference Object；
- 附带 Resolver 的 `AMBIGUOUS/UNKNOWN/INVALID` 状态；
- 不把未解析引用变成新对象；
- 不从目录、名称或相似字符串猜测目标；
- 不把未解析 Evidence 或 Verification 当作已满足条件。

## 3. Validation Result Envelope（验证结果封装）

规范对象验证结果使用 `validation-result-contract-specification.md` 冻结的 9 字段封装：

| 字段 | 语义 | 约束 |
|---|---|---|
| `validation_id` | 验证结果 ID | 本地瞬时结果无可归因记录时为 `null` |
| `validator_version` | Validator 版本 | 当前为 `v0.1` |
| `target_reference` | 被检查对象的安全引用 | 不创建对象；未知时为 `null` |
| `schema_reference` | 所用 Schema 的 ID 与摘要 | 摘要不是事实或权力 |
| `result` | 五种顶层状态之一 | `PASS/FAIL/UNKNOWN/CONFLICT/VERSION_MISMATCH` |
| `errors` | 结构化错误列表 | `PASS` 时为空，其他状态至少一项 |
| `warnings` | 结构化警告列表 | 不改变主结果 |
| `limitations` | 验证范围和剩余未知 | 必须至少一项 |
| `timestamp` | 可归因结果时间 | 本地瞬时结果不补造，默认为 `null` |

错误和警告必须使用 `validation-error-object-model.md`；无权力规则见 `validation-result-boundary-rules.md`。概念标签 `VALID` 现统一表达为顶层 `PASS`，诊断代码 `INVALID` 则确定性映射为顶层 `FAIL`。Validation Result 仍不是 Entity、Evidence、Verification Record、Permission 或 API response。

## 4. Deterministic Precedence（确定性优先级）

当一个对象同时存在多个问题时，主结果按以下顺序选择，并在诊断中保留其他问题：

1. `INVALID`：结构无法安全处理；
2. `VERSION_MISMATCH`：结构可识别但版本不兼容；
3. `CONFLICT`：存在互不兼容的多重声明；
4. `UNRESOLVED_REFERENCE`：必需引用未唯一解析；
5. `UNKNOWN`：结构和引用可处理，但领域值证据不足。

对应顶层结果优先级为：

```text
FAIL
  > VERSION_MISMATCH
  > CONFLICT
  > UNKNOWN
  > PASS
```

此顺序不允许绕过 Source access control（来源访问控制）。如果披露任何细节会违反 API 安全边界，API 层仍应返回 `UNAUTHORIZED_REFERENCE`。

## 5. Relationship to API Error Model（与接口错误模型的关系）

Object Error（对象错误）和 API Error（接口错误）属于不同层：

| Object Error | API 层常见映射 | 说明 |
|---|---|---|
| `UNKNOWN` | `UNKNOWN` | 保留未知 |
| `INVALID` | `INVALID` | 不访问 Source |
| `VERSION_MISMATCH` | `VERSION_MISMATCH` | 不自动替换版本 |
| `CONFLICT` | `CONFLICT` | 不自动选择候选 |
| `UNRESOLVED_REFERENCE` | `UNKNOWN` 或 `CONFLICT` | 取决于 Resolver 为零目标还是多目标 |

API 的 `UNAUTHORIZED_REFERENCE` 只表达访问或披露边界，不属于 Object Contract 的结构错误，也不创建 Permission。

## 6. Prohibited Error Behavior（禁止错误行为）

- 错误自动创建或修复对象；
- `UNKNOWN` 自动变成有效默认值；
- `CONFLICT` 自动合并身份或状态；
- `VERSION_MISMATCH` 静默使用最新版本；
- `UNRESOLVED_REFERENCE` 自动扫描工作区并登记命中目标；
- 错误结果授予 Permission、Capability 或 Authority；
- 错误结果触发 Execution 或 SAEE Evolution；
- 新验证覆盖旧错误记录。

```text
OBJECT_ERRORS_ARE_EXPLAINABLE=true
OBJECT_ERRORS_FAIL_CLOSED=true
OBJECT_ERROR_NE_PERMISSION_DECISION=true
OBJECT_ERROR_NE_TRUTH_DECISION=true
VALIDATION_RESULT_CONTRACT=FROZEN_V0.1
CURRENT_OBJECT_VALIDATOR=true
VALIDATION_RESULT_NE_PERMISSION=true
VALIDATION_RESULT_NE_AUTHORIZATION=true
VALIDATION_RESULT_NE_TRUTH=true
```
