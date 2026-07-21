# DBOS Object Schema Version Policy v0.1（DBOS 对象模式版本政策 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

实现状态：`NOT_STARTED`

## 1. Purpose（目的）

本政策定义 DBOS Object Schema（对象模式）的版本、兼容、弃用和迁移规则。它不迁移现有记录、不生成对象实例，也不授权 API 或 SDK 实现。

## 2. Independent Version Axes（独立版本轴）

以下版本必须分开记录：

| 版本轴 | 位置 | 语义 |
|---|---|---|
| Schema dialect（模式方言） | `$schema` | JSON Schema 语义版本；v0.1 固定为 Draft 2020-12 |
| Schema release（模式发布版本） | `$id` 与 `x-dbios-schema-version` | 某个模式文件的治理版本 |
| Object Contract version（对象契约版本） | `x-dbios-object-contract-version` | 模式所实现的人类可读契约版本 |
| Object representation version（对象表示版本） | 对象字段 `version` | 对象声明遵循的契约表示版本 |
| Domain record version（领域记录版本） | ID、Reference Object 或 Source | Entity、Evidence、Verification 或协议自己的版本 |

这些值在首版都可能显示为 `v0.1`，但相同字符串不表示同一版本轴。Schema Version ≠ Object Version（模式版本不等于对象版本）。

## 3. Version Format（版本格式）

Schema release 使用：

```text
v<generation>.<revision>
```

- `generation`：发生 Breaking Change（破坏性变更）时递增；
- `revision`：保持当前 generation 兼容边界的变更时递增；
- 初始版本为 `v0.1`；
- 不允许可变 `latest` ID；
- 每个版本必须拥有唯一 `$id` 和独立保留的 Schema 文件；
- 旧 Schema 不得被新版本覆盖或删除。

## 4. Compatible Change（兼容变更）

Compatible Change 不改变既有实例的结构接受结果，也不改变字段的规范语义、治理效果或错误分类。

可兼容变更包括：

- 修正文案、拼写、标题或 `$comment`；
- 增加不改变验证结果的 `x-dbios-*` 诊断元数据；
- 改善安全说明和 non-effects（无效果）说明；
- 增加未被任何对象 Schema 引用的内部 `$defs`；
- 修正关联文档路径，但不改变 Source 或 Namespace 含义。

即使兼容，也必须创建新的 Schema release，保留旧 `$id` 和旧文件，并记录变化原因。不得原地修改已发布版本后仍沿用同一摘要。

## 5. Conditionally Compatible Addition（条件兼容新增）

由于类型 Schema 使用 `unevaluatedProperties=false`，新增可选顶层字段会被旧 Validator（验证器）拒绝，因此默认不属于完全兼容变更。

新增字段、枚举值或 Reference Type 只有同时满足以下条件时，才可作为同 generation 的条件兼容 revision：

- 新字段为可选；
- 旧对象在新 Schema 下仍有效；
- Producer（生产者）在消费者确认支持新版本前不发送新字段；
- Capability negotiation（能力协商）显式记录 Schema `$id`；
- Unknown preservation（未知保留）规则不变；
- 不新增 Authority、Permission、Execution 或 SAEE 效果。

缺少任一条件时，按 Breaking Change 处理。

## 6. Breaking Change（破坏性变更）

以下任一变化都属于 Breaking Change：

- 新增必填字段；
- 删除、重命名或改变字段类型；
- 改变 `object_id` 与专属 ID 等价规则；
- 改变 `object_type`、status 或受控枚举含义；
- 收窄或扩大 Reference、Namespace 或 Source 语义；
- 改变空值、timestamp、limitations 或 unknown 处理；
- 改变 `unevaluatedProperties` 策略；
- 让旧对象从 `VALID` 变成非成功，或让旧非成功对象变成 `VALID`；
- 改变错误优先级；
- 新增 Authority、Permission、Execution、Truth、Verification 或 SAEE 效果。

Breaking Change 必须递增 `generation`，创建新 `$id`、新文件和 Migration Requirement（迁移要求）。

## 7. Deprecated Field（弃用字段）

字段弃用必须：

- 保留字段在当前 generation 中的结构接受能力；
- 使用 `deprecated: true` 标注；
- 说明 replacement（替代字段）、弃用原因和最早移除版本；
- 保留旧对象、Evidence、Snapshot 和 Validation Result；
- 禁止把字段弃用解释为历史数据可以删除；
- 允许消费者继续读取，Producer 在迁移窗口后停止新写入。

弃用不是删除。删除只能发生在新的 generation 中。

## 8. Migration Requirement（迁移要求）

任何 Breaking Change 必须同时提供：

1. 旧 Schema `$id` 与新 Schema `$id`；
2. 字段级映射和不可映射字段清单；
3. Source、Reference 和 Object ID 连续性规则；
4. `UNKNOWN/null` 保留规则；
5. 历史 Evidence、Snapshot 和 Validation Result 的非改写证明；
6. 正向、负向和跨版本 fixture（测试夹具）；
7. rollback（回滚）和撤销路径；
8. 隐私、最小披露和敏感字段审查；
9. 人工批准与实施时间；
10. 追加式 evolution/change record（演化或变化记录）。

迁移必须生成新对象表示或新投影，不能原地改写旧 Evidence-bound object（证据约束对象）。

## 9. Validator Behavior（验证器行为）

未来 Validator 必须：

- 按调用方显式指定的 Schema `$id` 验证；
- 不默认选择最新版本；
- 找不到指定 Schema 时返回 `UNKNOWN` 或 `VERSION_MISMATCH`；
- 先执行标准 JSON Schema 结构验证，再执行 `x-dbios-invariants`；
- 把 `x-dbios-boundaries` 作为强制无效果检查；
- 保留全部错误和使用的 Schema 摘要；
- 不因 `VALID` 产生 Verification、Permission 或对象实例。

## 10. Current Policy State（当前政策状态）

```text
SCHEMA_VERSION_POLICY=v0.1
MUTABLE_LATEST_SCHEMA=false
IN_PLACE_SCHEMA_REWRITE=false
AUTOMATIC_MIGRATION=false
HISTORICAL_OBJECT_REWRITE=false
VALIDATION_NE_VERIFICATION=true
SCHEMA_AUTHORITY_EFFECT=NONE
SCHEMA_PERMISSION_EFFECT=NONE
```
