# DBOS Entity Object Contract v0.1（DBOS 实体对象契约 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

对象实例状态：`NOT_CREATED`

## 1. Definition（定义）

Entity Object（实体对象）是对现有 DBOS Entity identity record（实体身份记录）的受范围投影。它表达“Source 声明了哪个实体及其当前记录状态”，不签发身份、不认证 Owner（所有者），也不创建 Active Entity（活动实体）。

```text
ENTITY_OBJECT_NE_ENTITY_INSTANCE=true
ENTITY_OBJECT_NE_ACTIVE_ENTITY=true
ENTITY_OBJECT_NE_AGENT=true
```

## 2. Complete Field Set（完整字段集合）

Entity Object 必须包含公共字段：

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

以及以下专属字段：

`entity_id`、`entity_type`、`owner_reference`、`lifecycle_state`、`source_reference`

`status` 使用公共字段，不重复出现。

## 3. Field Semantics（字段语义）

| 字段 | 语义 | 约束 |
|---|---|---|
| `object_id` | 对象标识 | 必须等于 `entity_id` |
| `object_type` | 核心对象类型 | 必须为 `ENTITY` |
| `entity_id` | Source 声明的 Entity ID | 必须非空；API/SDK 不得随机生成 |
| `entity_type` | 实体分类 | v0.1 使用现有 `agent/protocol/repository/service/artifact/governance_system` 词表或 `UNKNOWN` |
| `owner_reference` | Owner 声明引用 | 必须可归因；解析不表示 Owner 已认证 |
| `lifecycle_state` | Source 记录的生命周期状态 | 不由对象应用或升级 |
| `source_reference` | Source 内部的实体记录引用 | 必须与公共 `source` 一致 |
| `status` | Entity Object 记录状态 | `UNKNOWN/DECLARED/SUPERSEDED/REVOKED` |

## 4. Lifecycle Boundary（生命周期边界）

`lifecycle_state` 可以表达现有 DBOS 词表：

```text
UNKNOWN
PROPOSED
REGISTERED
VERIFIED
ACTIVE
EVALUATED
ADAPTED
RETIRED
```

字段值只反映 Source 声明。即使值为 `ACTIVE`，Entity Object 也不执行激活、不证明当前 Runtime 存在、不证明 Capability 或 Permission 已获得。

## 5. Validation Rules（验证规则）

必须返回错误的情况：

- `object_id != entity_id`；
- `object_type != ENTITY`；
- Entity ID、Owner 或 Source 缺失；
- `entity_type` 或 `lifecycle_state` 不在受控词表；
- 从 Repository、Service、path（路径）或名称自动推断 Agent；
- 对象包含 `permission_granted`、`capability_assigned` 或 `runtime_started`；
- `ACTIVE` 没有可解析的生命周期 Source，但对象仍声称已验证。

## 6. Explicit Non-effects（明确无效果）

Entity Object 不代表：

- Active Entity 已创建；
- Owner 已认证；
- Agent 或 Runtime 已存在；
- Capability 已验证或分配；
- Permission 已授予；
- Digital Organism 已形成。

```text
IDENTITY_DECLARATION_EFFECT=REFERENCE_ONLY
LIFECYCLE_EFFECT=NONE
AUTHORITY_EFFECT=NONE
PERMISSION_EFFECT=NONE
```
