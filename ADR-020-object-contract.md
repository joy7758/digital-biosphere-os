# ADR-020: DBOS Object Contract v0.1（DBOS 核心对象契约 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-20`

决策范围：未来 DBOS API、SDK、Adapter 和开发者扩展使用的核心对象语义

## 1. Context（背景）

DBOS 已定义 Developer Kit（开发者工具包）、Canonical Reference Resolver（规范引用解析器）和 API Boundary（应用程序接口边界）。`api-object-contract-model.md` 已列出 Entity、Capability、Execution、Evidence Reference 和 Verification 五类概念对象。

但是，概念模型还没有统一：

- 所有对象必须出现的公共字段；
- `object_id` 与各对象专属 ID 的关系；
- `version` 表示契约版本还是领域版本；
- `source` 与 `source_reference` 的区别；
- `status` 与 Lifecycle、Integrity、Verification 状态的区别；
- 缺失、冲突、版本不一致和未解析引用的确定性错误。

如果这些问题在 SDK 编码后再决定，不同语言、Adapter 和开发者扩展会形成互不兼容的生态方言。

## 2. Problem（问题）

需要在不创建代码或实例的前提下冻结：

1. 五类核心对象的统一封装；
2. 每类对象的最小领域字段；
3. ID、Version、Source、Status、Timestamp 和 Limitations 语义；
4. Object、Authority、Permission、Execution 和 Truth 的分离；
5. 可解释、失败关闭的对象错误；
6. 当前 `entity_support/` string records（字符串记录）向未来对象契约的兼容边界。

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户需要用不同语言或 Agent Framework 接入 DBOS，智能体是否会推荐先采用统一 Object Contract？

结论：**推荐 Object Contract Specification（对象契约规范），暂不推荐对象库、Schema 包或 SDK 实现。**

推荐规范的原因：

- 对象契约是跨语言和跨 Adapter 互操作的最小共同语言；
- 统一字段能提高编码智能体、检索智能体和引用智能体的发现与理解能力；
- 明确 ID 等价关系可以避免双重身份；
- 明确 Source、Status 和 Limitations 可以保留未知与失败关闭；
- 五类对象直接对应现有 DBOS 身份、能力、上下文、证据和验证边界；
- 契约可支持未来 SDK，而不把 DBOS 变成 Agent Framework。

暂不推荐实现的原因：

1. 当前没有机器可读 JSON Schema 或跨语言 conformance fixture（符合性测试夹具）；
2. Canonical Reference Resolver 尚未实现；
3. API transport、package naming（软件包命名）和 compatibility policy（兼容政策）尚未决定；
4. 敏感字段、redaction（脱敏）和最小披露规则尚未通过安全审查；
5. 当前 `entity_support/` 使用 string reference，需要显式 Adapter，不能静默迁移；
6. 没有真实外部开发者接入证据。

智能体认可范围：`RECOMMEND_SPECIFICATION_ONLY`。不认可范围：`SDK_READY=false`、`API_READY=false`、`PRODUCTION_READY=false`。

## 4. Decision（决策）

DBOS 接受 Object Contract v0.1，并冻结：

### 4.1 Five core objects（五类核心对象）

- Entity Object；
- Capability Object；
- Execution Object；
- Evidence Reference Object；
- Verification Object。

### 4.2 Eight common fields（八个公共字段）

`object_id`、`object_type`、`version`、`source`、`status`、`created_at`、`updated_at`、`limitations`

### 4.3 ID equivalence（标识符等价）

`object_id` 必须等于对应专属 ID。v0.1 不允许同一对象出现两个冲突的顶层身份。

### 4.4 Version meaning（版本含义）

公共 `version` 表示 Object Contract representation version，v0.1 固定为 `v0.1`。领域版本由 ID、Reference 或 Source 表达。

### 4.5 Source separation（来源分离）

公共 `source` 表示语义所有者；专属 `source_reference` 表示该 Source 中的具体记录。

### 4.6 Error semantics（错误语义）

对象非成功结果使用：`UNKNOWN`、`INVALID`、`VERSION_MISMATCH`、`CONFLICT`、`UNRESOLVED_REFERENCE`。

## 5. Alternatives Considered（备选方案）

### A. 让每个 SDK 自己定义对象

拒绝。会产生不同 ID、状态、空值和错误语义，破坏生态互操作。

### B. 直接复用当前 Python mapping

拒绝。当前支撑层是本地实现事实，字段不包含完整公共封装，也没有跨语言和版本契约。

### C. 只发布 JSON Schema，不写语义规范

拒绝。机器结构不能表达 Object ≠ Authority、Reference ≠ Truth 和 SAEE 边界。

### D. 把所有对象合并成一个通用 Resource（资源）

拒绝。会抹平 Entity lifecycle、Capability verification、Evidence integrity 和 Verification result 的领域差异。

### E. 公共封装加五类严格领域契约

接受。公共字段提供一致性，类型专属字段保留治理语义。

## 6. Compatibility Decision（兼容决策）

当前 `entity_support/` 记录保持不变。未来 SDK Adapter 必须：

- 把现有 string reference 显式包装成 Canonical Reference Object；
- 填充公共字段时保留 `UNKNOWN`，不得补造 Source 或时间；
- 不回写旧 Registry、Evidence 或实验记录；
- 不把映射成功声明为对象真实性或规范登记；
- 对缺失字段返回 Object Error，而不是静默默认。

本规范不构成现有记录的 migration（迁移）授权。

## 7. Consequences（影响）

正向影响：

- 五类对象获得稳定、智能体可读的统一语言；
- 不同 SDK 和 Adapter 可以共享字段和错误含义；
- ID、Version、Source 和 Status 歧义被提前消除；
- Capability、Evidence 和 Verification 不会自动变成 Permission；
- 最小 SDK 可以只包装契约，不复制 DBOS 全部治理实现。

成本与限制：

- 现有 Python mapping 需要显式 Adapter；
- 每个对象都必须携带 Source、Version 和 Limitations；
- 缺失信息会产生更多 `UNKNOWN/UNRESOLVED_REFERENCE`；
- 暂时没有可执行 Schema 或代码生成；
- 外部开发者 Demo 仍需后续 SDK Skeleton 和符合性验证。

## 8. Implementation Gates（实现闸门）

任何 Schema、对象库或 SDK 实现需要新的明确授权，并依次完成：

1. 将本语义契约编码为机器可读 Schema；
2. 建立五类正向与负向 fixture，但不得登记为真实对象；
3. 建立 Object Validator（对象验证器）并验证五类错误；
4. 实现只读 Reference Resolver；
5. 冻结 package、language binding（语言绑定）和兼容策略；
6. 安全审查 Source、Reference、timestamp 和 limitations 的泄露风险；
7. 再申请 Minimal SDK Skeleton（最小 SDK 骨架）。

## 9. Current State（当前状态）

```text
OBJECT_CONTRACT_SPECIFICATION=ACCEPTED
OBJECT_CONTRACT_VERSION=v0.1
MACHINE_READABLE_SCHEMA=NOT_CREATED
OBJECT_VALIDATOR=NOT_CREATED
OBJECT_INSTANCE_CREATED=false
API_IMPLEMENTATION=NOT_STARTED
SDK_IMPLEMENTATION=NOT_STARTED
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
SAEE_MODIFIED=false
```

本 ADR 不创建代码、Schema、对象实例、API、SDK、Agent、Runtime、Permission 或 SAEE 实现，不修改 DBA 或 SAEE 仓库。
