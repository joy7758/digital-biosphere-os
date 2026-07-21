# DBOS Validation Error Object Model v0.1（DBOS 验证错误对象模型 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

## 1. Purpose（目的）

Validation Error Object（验证错误对象）为 `errors` 与 `warnings` 提供统一、可解释、可机器读取的诊断格式。它不是异常堆栈、自动修复命令、Permission 决定或 Evidence 正文。

## 2. Required Fields（必填字段）

每个诊断对象必须包含以下 5 个字段：

| 字段 | 类型 | 语义 |
|---|---|---|
| `error_code` | non-empty string（非空字符串） | 稳定机器代码，如 `INVALID`、`UNKNOWN`、`CONFLICT` 或 `VERSION_MISMATCH` |
| `message` | non-empty string（非空字符串） | 不包含敏感观察值的简洁解释；不能成为唯一机器语义 |
| `field_reference` | non-empty string（非空字符串） | JSON Path（JSON 路径）或 `$schema` 等安全位置引用 |
| `severity` | `ERROR` or `WARNING` | `ERROR` 进入 `errors`，`WARNING` 进入 `warnings` |
| `resolution_hint` | non-empty string or `null`（非空字符串或空值） | 面向调用方的人工下一步；不是自动修复命令 |

字段必须全部存在。未知提示使用 `null`，不得使用空字符串。

## 3. Error Codes（错误代码）

v0.1 允许以下核心诊断语义：

| `error_code` | 含义 | 常见主结果 |
|---|---|---|
| `INVALID` | 字段、类型、结构或治理边界明确违反 | `FAIL` |
| `UNKNOWN` | 缺少外部信息或受控值保持未知 | `UNKNOWN` |
| `UNRESOLVED_REFERENCE` | 引用没有唯一解析 | `UNKNOWN` |
| `CONFLICT` | ID、Source、Schema 或状态互相冲突 | `CONFLICT` |
| `VERSION_MISMATCH` | 版本不兼容 | `VERSION_MISMATCH` |

具体规则名称可以用于内部生成 `resolution_hint`，但不能创建第二套结果状态。

## 4. Resolution Hint Boundary（修复提示边界）

允许：

- 指向需要人工阅读的字段或规范规则；
- 说明缺少何种 Source、Evidence、版本或人工决定；
- 建议调用方提交新输入或显式选择兼容版本。

禁止：

- 自动修改输入；
- 生成补丁并应用；
- 自动选择冲突候选；
- 自动授予 Permission 或 Authorization；
- 自动执行任务、迁移或 SAEE Evolution；
- 宣称“修复后必然通过”。

## 5. Privacy and Disclosure（隐私与披露）

`message`、`field_reference` 和 `resolution_hint` 不得包含：

- Secret、Token 或 Credential；
- Evidence 正文；
- 未获披露许可的目标存在性；
- 原始个人数据；
- 完整输入对象。

当前本地 Validator 只输出规则类别和字段位置，不回显观察值。

## 6. Current State（当前状态）

```text
VALIDATION_ERROR_FIELD_COUNT=5
ERROR_SEVERITY=ERROR
WARNING_SEVERITY=WARNING
RESOLUTION_HINT_AUTO_EXECUTES=false
ERROR_CREATES_PERMISSION=false
ERROR_CREATES_AUTHORIZATION=false
ERROR_MODIFIES_TARGET=false
ERROR_REWRITES_HISTORY=false
```
