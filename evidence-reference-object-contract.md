# DBOS Evidence Reference Object Contract v0.1（DBOS 证据引用对象契约 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

对象实例状态：`NOT_CREATED`

## 1. Definition（定义）

Evidence Reference Object（证据引用对象）把一个 Execution 引用连接到既有 Evidence Source（证据来源）中的记录。它不复制 Evidence 内容、不创建事实，也不把摘要或文件存在解释为 Truth（真相）。

```text
EVIDENCE_REFERENCE_OBJECT_NE_EVIDENCE_OBJECT=true
REFERENCE_NE_TRUTH=true
INTEGRITY_STATUS_NE_VERIFICATION=true
```

## 2. Complete Field Set（完整字段集合）

Evidence Reference Object 必须包含公共字段：

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

以及以下专属字段：

`evidence_id`、`execution_reference`、`source_reference`、`integrity_status`

用户要求的 `version` 使用统一公共字段，不重复定义。

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 约束 |
|---|---|---|
| `object_id` | 对象标识 | 必须等于 `evidence_id` |
| `object_type` | 核心对象类型 | 必须为 `EVIDENCE_REFERENCE` |
| `evidence_id` | Evidence Reference 的稳定 ID | 不是 canonical Evidence 内容 ID，除非 Source 明确声明相同 |
| `execution_reference` | 相关 Execution Object 引用 | 解析不表示执行发生 |
| `source_reference` | Evidence Source 内的具体记录引用 | 必须与公共 `source` 一致 |
| `integrity_status` | Source 声明的完整性状态 | v0.1 安全值为 `UNKNOWN/PENDING` |
| `version` | Object Contract 表示版本 | v0.1 固定为 `v0.1`；不替代 Evidence 自身版本 |
| `status` | 引用对象记录状态 | `UNKNOWN/DECLARED/SUPERSEDED/REVOKED` |

## 4. Reference Boundary（引用边界）

- `evidence_id` 标识 Evidence Reference Object，不自动标识 Evidence payload（证据载荷）；
- `source_reference` 必须能够被 Canonical Reference Resolver（规范引用解析器）按 `EVIDENCE` 类型处理；
- `RESOLVED` 只表示唯一记录可定位；
- Evidence Source 自身的版本、摘要、签名、等级和验证材料必须由 Source 记录表达；
- 本对象不增加或覆盖 E 等级；
- 当前支撑层只允许 `UNKNOWN/PENDING` integrity status（完整性状态）。

## 5. Validation Rules（验证规则）

必须返回错误的情况：

- `object_id != evidence_id`；
- `object_type != EVIDENCE_REFERENCE`；
- Execution 或 Source 引用缺失；
- `source` 与 `source_reference` 指向冲突的 Namespace 或 Owner；
- 未解析引用被静默视为 Evidence 存在；
- `integrity_status` 超过当前证据支持范围；
- 对象包含 `truth_confirmed`、`permission_granted`、自动 E 等级提升或历史删除字段；
- 引用对象创建时复制、修改或删除 Evidence 内容。

## 6. Explicit Non-effects（明确无效果）

Evidence Reference Object 不等于：

- Evidence Truth；
- Evidence 已验证；
- 摘要或签名有效；
- Evidence 与目标充分相关；
- Execution 已发生；
- Verification `PASS`；
- Capability、Authority 或 Permission。

```text
EVIDENCE_CREATION_EFFECT=NONE
EVIDENCE_MUTATION_EFFECT=NONE
EVIDENCE_LEVEL_EFFECT=NONE
TRUTH_EFFECT=NONE
PERMISSION_EFFECT=NONE
```
