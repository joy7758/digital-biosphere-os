# DBOS Capability Object Contract v0.1（DBOS 能力对象契约 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

对象实例状态：`NOT_CREATED`

## 1. Definition（定义）

Capability Object（能力对象）表达某个 Entity 的能力边界声明、范围、限制和验证状态。它是 declaration projection（声明投影），不是能力实例、执行能力或 Permission。

```text
CAPABILITY_OBJECT_NE_CAPABILITY_INSTANCE=true
CAPABILITY_OBJECT_NE_CAPABILITY_GRANT=true
CAPABILITY_OBJECT_NE_PERMISSION=true
```

## 2. Complete Field Set（完整字段集合）

Capability Object 必须包含公共字段：

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

以及以下专属字段：

`capability_id`、`entity_reference`、`capability_name`、`scope`、`constraints`、`verification_status`

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 约束 |
|---|---|---|
| `object_id` | 对象标识 | 必须等于 `capability_id` |
| `object_type` | 核心对象类型 | 必须为 `CAPABILITY` |
| `capability_id` | 能力边界声明 ID | 不表示能力实例已存在 |
| `entity_reference` | 被声明 Entity 的引用 | 必须显式；解析不表示 Entity 可执行该能力 |
| `capability_name` | Source 声明的能力名称 | 名称存在不证明能力存在 |
| `scope` | 声明适用范围 | 必须是非空、明确结构；不得默认为全局 |
| `constraints` | 禁止条件、资源和环境限制 | 必须是非空、明确结构 |
| `verification_status` | 声明的验证状态 | v0.1 安全值见下节 |
| `status` | Capability Object 记录状态 | `UNKNOWN/DECLARED/SUPERSEDED/REVOKED` |

## 4. Verification Boundary（验证边界）

v0.1 可独立表达的 `verification_status`：

```text
UNKNOWN
UNVERIFIED
PENDING
```

`VERIFIED` 只有在 Source 中存在可解析、证据约束的 Verification Record 时才可投影。由于本契约没有把 Verification 内容嵌入 Capability Object，开发者必须通过独立 Verification Object 解析该状态；缺失时不得使用 `VERIFIED`。

## 5. Validation Rules（验证规则）

必须返回错误的情况：

- `object_id != capability_id`；
- `object_type != CAPABILITY`；
- Entity 引用未解析但未报告 `UNRESOLVED_REFERENCE`；
- `scope` 或 `constraints` 为空、隐式或被扩大；
- 从函数、工具清单、代码路径或模型描述自动推导 `VERIFIED`；
- Capability Object 包含 Permission、Grant、execution authority（执行权力）或自动授权字段；
- `verification_status=VERIFIED` 但没有可解析的独立 Verification Object。

## 6. Explicit Non-effects（明确无效果）

Capability Object 不等于：

- Capability Grant；
- Capability Assignment；
- 当前任务可以执行；
- Authorization；
- Permission；
- Agent autonomy（智能体自治）。

```text
CAPABILITY_DECLARATION_EFFECT=REFERENCE_ONLY
CAPABILITY_GRANT_EFFECT=NONE
EXECUTION_EFFECT=NONE
PERMISSION_EFFECT=NONE
```
