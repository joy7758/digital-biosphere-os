# DBOS API Error Model v0.1（DBOS 应用程序接口错误模型 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

## 1. Purpose（目的）

本模型定义未来 DBOS API 的最小错误语义，使开发者和智能体能够区分未知、结构非法、引用访问受限、冲突和版本不匹配，而不依赖自然语言猜测。

错误必须 explainable（可解释）、deterministic（确定性）、fail-closed（失败关闭）且不泄露敏感信息。

## 2. Error Codes（错误代码）

### 2.1 `UNKNOWN`

含义：请求结构有效，但目标、Source、Version 或必要上下文无法在允许范围内确定。

要求：

- 返回缺失条件；
- 保留原始 Reference；
- 不把“未找到”声明为“绝对不存在”；
- 不自动登记、猜测或跨工作区搜索。

### 2.2 `INVALID`

含义：请求缺少必填字段、类型或格式非法、包含禁止效果，或违反对象契约。

要求：

- 指明字段路径和违反的规则；
- 在访问外部 Source 前失败；
- 不返回部分成功对象；
- 不降级为 `UNKNOWN` 掩盖结构错误。

### 2.3 `UNAUTHORIZED_REFERENCE`

含义：该请求无权在声明的 Source、Scope 或安全边界中解析或披露某引用。

该错误名称表示 reference access denial（引用访问被拒绝），不是 DBOS Permission 状态，也不表示目标对象本身“未经授权”。

要求：

- 不泄露目标是否存在；
- 返回受限范围或所需独立 authority reference（权力引用）的类别，而非伪造授权；
- 不创建、授予、撤销或推导 Permission；
- 不把 API authentication（接口认证）和 DBOS Entity Permission 混为一体。

### 2.4 `CONFLICT`

含义：两个或以上记录、Source、版本、状态或幂等请求互相冲突，无法按已声明规则唯一选择。

要求：

- 返回不敏感的 conflicting references（冲突引用）和冲突维度；
- 不选择最新、最相似或路径最近的候选；
- 不自动合并身份、证据或状态；
- 要求调用方缩小范围或提交独立治理决定。

### 2.5 `VERSION_MISMATCH`

含义：请求版本、对象版本、Source 版本或契约版本不一致，且不存在已批准的兼容关系。

要求：

- 返回 requested version（请求版本）和 observed version（观察版本）；
- 不自动升级、降级或改写对象；
- 不把“最新版本”作为隐式替代；
- 保留旧版本 Evidence 和 Validation 结果。

## 3. Error Object（错误对象）

未来 Error Object 至少应表达以下概念字段：

| 字段 | 语义 | 约束 |
|---|---|---|
| `error_code` | 五种错误代码之一 | 稳定且可机器检查 |
| `message` | 面向开发者的简洁解释 | 不得成为唯一语义载体 |
| `operation` | 失败的 API 类别和操作 | 不使用未冻结 endpoint 名称 |
| `reference` | 相关引用或安全脱敏引用 | 不泄露敏感目标 |
| `source` | 允许披露的 Source 描述 | 未知时保持 `null` |
| `details` | 字段路径、冲突维度或缺失条件 | 不包含 Secret、Token 或 Evidence 正文 |
| `required_action` | 调用方下一步 | 不能表示系统已代为授权 |
| `retryable` | 是否可在输入或外部状态改变后重试 | 不保证重试成功 |
| `correlation_id` | 一次请求的诊断关联 ID | 不是 Evidence ID 或 Authority |
| `authority_effect` | 权力效果 | 固定为 `NONE` |
| `permission_effect` | 权限效果 | 固定为 `NONE` |

这是概念对象，不是已发布 Schema、HTTP response（响应）或 SDK class（类）。

## 4. Relationship to Resolution Result（与解析结果的关系）

Canonical Resolver 的 `RESOLVED/AMBIGUOUS/UNKNOWN/INVALID` 是 Resolution Result（解析结果）；本文件中的错误代码是 API operation error（接口操作错误）。二者不能静默互换。

| Resolver 状态 | API 层可能结果 | 说明 |
|---|---|---|
| `RESOLVED` | 成功或后续独立错误 | 解析成功不保证操作可继续 |
| `AMBIGUOUS` | `CONFLICT` | 必须保留候选与歧义 |
| `UNKNOWN` | `UNKNOWN` | 不得推断不存在 |
| `INVALID` | `INVALID` | 不访问 Source |
| 未允许的 Source/Scope | `UNAUTHORIZED_REFERENCE` | 不透露目标存在性 |
| 明确版本不一致 | `VERSION_MISMATCH` | 不自动替换版本 |

## 5. Evaluation Order（判定顺序）

未来实现必须按安全顺序判定：

1. 检查请求与对象结构；失败为 `INVALID`；
2. 检查 Source、Scope 和披露边界；失败为 `UNAUTHORIZED_REFERENCE`；
3. 检查显式版本兼容性；失败为 `VERSION_MISMATCH`；
4. 检查唯一性和并发冲突；失败为 `CONFLICT`；
5. 在允许范围内找不到充分记录；返回 `UNKNOWN`。

如果披露版本或候选会泄露受限目标，`UNAUTHORIZED_REFERENCE` 优先，并省略敏感细节。

## 6. Explainability Requirements（可解释性要求）

每个错误必须让开发者确定：

- 哪类操作失败；
- 哪条规范规则被触发；
- 哪些输入已知、未知或冲突；
- 是否允许重试；
- 需要补充什么引用、版本、Source 或人工决定；
- 该错误明确没有产生哪些治理效果。

错误不得只返回“failed（失败）”“not found（未找到）”或无法区分的数字代码。

## 7. Prohibited Error Behavior（禁止错误行为）

- 将 `UNKNOWN` 自动转换为成功；
- 在 `CONFLICT` 时任意选择候选；
- 在 `VERSION_MISMATCH` 时静默使用最新版本；
- 用 `UNAUTHORIZED_REFERENCE` 创建或修改 Permission；
- 在诊断中泄露 Secret、Token、Credential、个人数据或 Evidence 正文；
- 用重试覆盖原始失败记录；
- 把 API 错误解释为 SAEE Fitness 或 Evolution 结果。

```text
ERRORS_ARE_EXPLAINABLE=true
ERRORS_FAIL_CLOSED=true
ERROR_NE_PERMISSION_DECISION=true
ERROR_NE_TRUTH_DECISION=true
CURRENT_ERROR_SCHEMA=false
CURRENT_ERROR_IMPLEMENTATION=false
```
