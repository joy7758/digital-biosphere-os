# ADR-021: DBOS Object Schema Governance v0.1（DBOS 对象模式治理 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`SCHEMA_DEFINITION_ONLY`

日期：`2026-07-20`

决策范围：五类 DBOS 核心对象的机器可读结构标准与版本治理

## 1. Context（背景）

`object-contract-specification.md` 已冻结五类核心对象及八个公共字段，但此前只有人类可读规则。不同语言、Adapter（适配器）和未来 SDK 如果各自解释必填字段、枚举、空值和 Reference，会产生不兼容对象。

仓库已经存在 `schemas/project-manifest.schema.yaml`，采用 JSON Schema Draft 2020-12（JSON 模式 2020-12 草案）并以 JSON-compatible YAML（与 JSON 兼容的 YAML）保存。因此本轮复用同一目录与方言，不覆盖既有 Federation Project Manifest Schema（联邦项目清单模式）。

## 2. Problem（问题）

需要把 Object Contract 转换为机器可读标准，同时保持：

- Schema ≠ Object Instance（模式不等于对象实例）；
- Schema ≠ Authority（模式不等于权力）；
- Validation ≠ Verification（结构验证不等于事实验证）；
- Schema Version ≠ Object Version（模式版本不等于对象版本）；
- Reference ≠ Truth（引用不等于事实）；
- DBOS ≠ SAEE。

标准 JSON Schema 还能表达字段、类型、枚举、必填性和未声明字段限制，但不能独立证明 Source 真实、Reference 已解析、两个字段值相等、时间有因果顺序或某个动作没有发生。

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户希望用陌生语言或工具接入 DBOS，智能体是否会推荐这套 Object Schema？

结论：**推荐 Schema Specification（模式规范），暂不推荐 Validator、SDK 或生产集成。**

推荐原因：

- JSON Schema Draft 2020-12 是跨语言、工具可消费的结构标准；
- 公共 Schema 避免五类对象重复定义基础字段；
- 严格 `unevaluatedProperties=false` 防止未经治理的字段进入核心对象；
- `$id`、Schema release 和 Object Contract version 分离，便于兼容治理；
- `x-dbios-invariants` 将标准 Schema 无法表达的治理规则显式交给未来 Validator；
- `x-dbios-boundaries` 让编码智能体能发现并保持无权限、无执行和无 SAEE 效果。

暂不推荐 Validator 或 SDK 的原因：

1. 当前没有 Object Validator 实现；
2. 没有正向、负向或跨版本对象 fixture；
3. `$id` Registry（登记表）和离线 Reference resolution（引用解析）尚未实现；
4. `format: date-time` 的强制程度依赖未来 Validator 配置；
5. 跨字段 ID 等价、时间顺序和 Source 对齐需要语义检查；
6. 尚无外部开发者、跨语言实现或生产证据。

智能体认可范围：`RECOMMEND_SCHEMA_SPECIFICATION_ONLY`。不认可范围：`VALIDATOR_READY=false`、`SDK_READY=false`、`PRODUCTION_READY=false`。

## 4. Decision（决策）

DBOS 采用 JSON Schema Draft 2020-12，并新增：

1. `schemas/common-object-schema.yaml`；
2. `schemas/entity-object-schema.yaml`；
3. `schemas/capability-object-schema.yaml`；
4. `schemas/execution-object-schema.yaml`；
5. `schemas/evidence-reference-object-schema.yaml`；
6. `schemas/verification-object-schema.yaml`。

所有 `.yaml` 文件使用 JSON-compatible YAML，能够由 JSON parser（解析器）读取，不依赖 YAML 特有语法。

## 5. Composition Decision（组合决策）

- Common Schema（公共模式）定义八个公共字段、Source Descriptor（来源描述）、Reference Object 和复用字符串规则；
- 五个类型 Schema 通过规范 `$id` 引用 Common Schema；
- 类型 Schema 使用 `unevaluatedProperties=false` 关闭未声明顶层字段；
- `object_type` 使用 `const` 固定类型；
- 受控状态和枚举由类型 Schema 冻结；
- 不提供 `default`，防止 Validator 或代码生成器补造事实；
- 不提供真实 `examples`，防止示例被误当成对象实例。

## 6. Extended Governance Keywords（扩展治理关键字）

v0.1 使用以下非标准、机器可读注解：

- `x-dbios-schema-version`；
- `x-dbios-object-contract-version`；
- `x-dbios-invariants`；
- `x-dbios-prohibited-fields`；
- `x-dbios-boundaries`。

标准 JSON Schema Validator 可以忽略未知关键字，因此只运行通用 Validator 不能证明完整 DBOS conformance（符合性）。下一阶段 DBOS Object Validator 必须执行这些注解。

## 7. Validation Boundary（验证边界）

Schema Validation `VALID` 只表示：

- 必填字段存在；
- JSON 类型、枚举、常量和局部结构满足模式；
- 未声明字段被拒绝；
- `$ref` 在已提供 Schema Registry 中可解析。

它不表示：

- 对象实例已创建或规范登记；
- ID、Owner、Source 或 Reference 真实；
- `object_id` 与专属 ID 的值等价已由通用 Validator 证明；
- Entity 为 `ACTIVE`；
- Capability 已授予；
- Execution 已发生或成功；
- Evidence 为 Truth；
- Verification 为事实验证或 Permission；
- SAEE 已调用或发生演化。

## 8. Version Decision（版本决策）

每个 Schema 同时声明：

- `$schema`：JSON Schema 方言；
- `$id`：Schema release identity（模式发布身份）；
- `x-dbios-schema-version`：Schema 治理版本；
- `x-dbios-object-contract-version`：所实现的对象契约版本。

对象字段 `version` 仍表示对象契约表示版本。版本规则见 `schema-version-policy.md`。

## 9. Alternatives Considered（备选方案）

### A. 继续只维护 Markdown（文档）

拒绝。无法让陌生工具确定性检查字段、枚举和未声明属性。

### B. 为每类对象复制公共字段

拒绝。会导致五份 Schema 漂移，并让未来修订难以保持一致。

### C. 使用开放的 `additionalProperties=true`

拒绝。扩展字段会未经治理进入核心对象，形成第二套语义。

### D. 直接编写 Python class（Python 类）

拒绝。会把语言实现误当成规范，并提前进入 SDK。

### E. Common Schema + strict type schemas + governance annotations（公共模式、严格类型模式与治理注解）

接受。标准结构约束与 DBOS 治理边界保持分层。

## 10. Consequences（影响）

正向影响：

- 陌生开发者和工具获得机器可读入口；
- 五类对象字段和枚举可以跨语言复用；
- 未声明字段、危险状态和错误类型可以失败关闭；
- 下一阶段 Validator 有明确标准输入；
- SDK 可以生成类型，但不能改变规范语义。

成本与限制：

- `$id` 引用需要未来 Validator 提供离线 Registry；
- 通用 JSON Schema 不能执行全部 `x-dbios-*` 规则；
- Strict schema（严格模式）提高兼容治理成本；
- 当前没有对象 fixture，不能声称完整实例验证；
- Schema 文件本身不是 API 或产品。

## 11. Next Gate（下一闸门）

下一阶段应建立 DBOS Object Schema Validator v0.1（DBOS 对象模式验证器 v0.1），但必须获得新的明确授权，并至少：

1. 离线加载 6 个 Schema `$id`；
2. 执行 Draft 2020-12 标准验证；
3. 执行 `x-dbios-invariants` 与 `x-dbios-boundaries`；
4. 验证日期格式和跨字段 ID 等价；
5. 使用纯合成 fixture，且不得登记为真实对象；
6. 输出 `VALID/UNKNOWN/INVALID/VERSION_MISMATCH/CONFLICT/UNRESOLVED_REFERENCE`；
7. 保持 Permission、Execution、Verification 和 SAEE effect 为 `NONE`。

## 12. Current State（当前状态）

```text
OBJECT_SCHEMA_SPECIFICATION=ACCEPTED
SCHEMA_DIALECT=JSON_SCHEMA_DRAFT_2020_12
SCHEMA_FILE_COUNT=6
OBJECT_INSTANCE_CREATED=false
OBJECT_VALIDATOR_CREATED=false
SDK_CREATED=false
API_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
SAEE_CALLED=false
```

本 ADR 不创建对象实例、Validator、SDK、API、Agent、Runtime、Permission 或 SAEE 实现，不修改 DBA 或 SAEE 仓库。
