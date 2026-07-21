# DBOS Canonical Reference Resolver Specification v0.1（DBOS 规范引用解析规范 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

API 状态：`NOT_DEFINED`

规范角色：Developer Infrastructure Specification（开发者基础设施规范）

## 1. Purpose（目的）

Canonical Reference Resolver（规范引用解析器）为跨 DBOS 模块、Adapter（适配器）、Developer Extension（开发者扩展）和外部开发者提供统一的引用语义。

它解决以下问题：

- 同一个字符串在不同模块中可能表示 Entity、Candidate、Authorization、Execution 或 Evidence；
- DBOS 规范 ID、外部系统 ID 和扩展 ID 可能发生词法碰撞；
- 引用可能缺少版本、来源或可用的规范记录；
- 外部 Adapter 可能把“找到记录”误写为“身份已验证”或“权限已授予”；
- 不同开发者可能对 `unknown`、冲突、撤销和不存在使用不同结果。

Resolver 的职责是验证引用结构、定位声明的 Namespace（命名空间）与 Source（来源）、执行无副作用查找、检测冲突并返回统一 Resolution Result（解析结果）。

```text
REFERENCE_LOOKUP=READ_ONLY
AUTHORITY_EFFECT=NONE
VERIFICATION_EFFECT=NONE
PERMISSION_EFFECT=NONE
LIFECYCLE_EFFECT=NONE
```

## 2. Core Position（核心定位）

Resolver 是统一引用语义解析层，不是：

- Database（数据库）或新的规范事实存储；
- Identity Provider（身份提供者）、认证服务或登录系统；
- Permission System（权限系统）或 Authorization Engine（授权引擎）；
- Verification Service（验证服务）；
- Entity Registry（实体登记表）的替代品；
- Agent、Runtime（运行时）或业务执行系统。

Resolver 读取调用方明确提供或由 Namespace 注册的 Source。它不拥有 Source 中的事实，不签发标识符，不保存业务对象，不执行验证，也不改变任何对象状态。

## 3. Normative Principles（规范原则）

### 3.1 Reference ≠ Authority（引用不等于权力）

引用只指向一个可能存在的记录。引用存在、格式正确或成功解析都不能产生治理权力、签发权或决策权。

### 3.2 Resolver ≠ Verification（解析不等于验证）

`RESOLVED` 只表示在声明的 Namespace、版本和 Source 中找到唯一匹配记录。它不证明记录内容真实、当前有效、独立验证或适用于某个目的。

### 3.3 Resolver ≠ Permission（解析不等于权限）

解析 Authorization Reference（授权引用）或 Permission 相关记录只能返回记录中声明的内容。Resolver 不计算某次动作是否允许，也不产生 Permission。

### 3.4 Unknown must remain Unknown（未知必须保持未知）

缺失 Namespace、版本、Source、唯一目标或必要上下文时，Resolver 必须返回 `UNKNOWN`、`AMBIGUOUS` 或 `INVALID`，不得从目录名、类名、Repository 名、框架类型或相似字符串推断。

### 3.5 Resolution is non-mutating（解析无修改效果）

Resolver 不创建 Entity、Candidate、Authorization、Registration、Execution、Evidence 或 Verification 记录；不改变 Lifecycle、C/E/V、Capability 或 Permission 状态。

### 3.6 Source ownership remains external（来源所有权保持独立）

每种引用仍由其规范 Source 管理。Resolver 只返回来源和定位结果，不建立第二套事实真源。

## 4. Current Identifier Reality（当前标识符事实）

DBOS 当前至少存在两类受控格式：

1. Canonical Entity ID（规范实体 ID）：

   ```text
   dbio://<entity_type>/<name>/<version>
   ```

   `registry/entities.yaml` 是当前规范实体身份事实真源；`registry/agents.yaml` 只是兼容视图。

2. Opaque DBOS Record ID（不透明 DBOS 记录 ID）：

   ```text
   dbio:<record_type>:<opaque-id>
   ```

   当前登记支撑层会确定性产生类似 `dbio:entity:registration:<digest>` 和 `dbio:registration:<digest>` 的记录 ID。

此外，Candidate、Owner、Decision、Task、Input、Output、Context 和外部系统对象仍可能使用调用方提供的裸字符串。v0.1 规范不废弃或重写这些既有 ID；它要求未来 Resolver 用显式 Reference Object 包装其类型、Namespace、版本和 Source。

## 5. Reference Types（引用类型）

v0.1 定义七种核心 Reference Type（引用类型）。类型必须显式声明，不能从字符串前缀之外的非规范线索推断。

### 5.1 Entity Reference（实体引用）

指向一个 Entity Registry 记录或经证据绑定的外部实体记录。

- `RESOLVED` 表示唯一实体记录可定位；
- 不表示身份已验证、Lifecycle 为 `ACTIVE`、Entity 是 Agent 或拥有 Capability；
- DBOS 规范实体查询必须以 `registry/entities.yaml` 或其未来明确 successor（后继）为 Source；
- 仅命中 `registry/agents.yaml` 兼容视图不能替代规范 Source。

### 5.2 Candidate Reference（候选引用）

指向 Candidate Proposal、Review 或 Registration Request 链中的候选记录。

- Candidate Reference 不是 Entity Reference；
- `RESOLVED` Candidate 不获得 `entity_id`；
- Candidate → Entity 只能通过独立 Registration 和 Identity Continuity（身份连续性）记录表达；
- Resolver 不跟随该关系自动返回 Entity。

### 5.3 Authorization Reference（授权引用）

指向一个 Authorization Record（授权记录）或治理决定引用。

- `RESOLVED` 只表示记录可定位；
- Resolver 可以原样返回记录状态和有效期字段，但不能判断该授权当前对某次动作有效；
- `AUTHORIZED` 字段不等于 Permission；
- Scope、Issuer、Expiry、Revocation 和 Decision 评估属于独立授权验证边界。

### 5.4 Registration Reference（登记引用）

指向一次 Registration Attempt、Registration Record 或 Registration Receipt（登记尝试、登记记录或登记回执）。

- 成功回执可以引用 `REGISTERED` Entity；
- 失败回执必须保持可解析且不能声明 `entity_id`；
- `SUCCESS` 不等于 `ACTIVE`、Agent、Runtime 或 Permission；
- Resolver 不重放登记，也不补建缺失实体。

### 5.5 Execution Reference（执行引用）

指向一个 DBOS Execution Record（执行记录）或外部 Runtime 的映射记录。

- 当前 `entity_support/execution_registry.py` 只支持 `CREATED` 记录；
- `RESOLVED` Execution 不表示任务已运行、成功或产生可信输出；
- Execution Result、Event、Context 和 Evidence 是独立引用，不得静默合并。

### 5.6 Evidence Reference（证据引用）

指向现有 Evidence 系统中的 Evidence Record、Artifact 或外部证据定位符。

- 当前支撑层只允许 `UNKNOWN/PENDING` integrity status（完整性状态）；
- `RESOLVED` 不表示 Evidence 真实、相关、充分或达到特定 E 等级；
- Digest（摘要）、Signature（签名）或文件存在不能替代来源和验证；
- Resolver 不复制 Evidence 正文，不提升 E 等级。

### 5.7 Verification Reference（验证引用）

指向 Verification Record、Verification Run 或外部验证结果记录。

- 当前支撑引用只允许 `PENDING/V0`；
- `RESOLVED` 不表示决定为 `pass`；
- 即使目标记录为 `pass`，Resolver 也只返回该记录，不扩大其方法、环境或范围；
- Verification 不产生 Capability Assignment、Authorization 或 Permission。

## 6. Reference Object（引用对象）

每个 Resolver 输入必须规范化为以下六字段 Reference Object。字段模型是规范概念，不是已发布 schema 或 API。

| 字段 | 类型 | 语义 | 约束 |
|---|---|---|---|
| `reference_id` | non-empty string（非空字符串） | Source 内部的目标标识符 | 不得由 Resolver 猜测或签发 |
| `reference_type` | controlled enum（受控枚举） | 七种核心引用类型之一 | 必须显式声明 |
| `namespace` | namespace identifier（命名空间标识符） | 决定语义所有者和解析规则 | 不得隐式默认为 DBOS |
| `version` | version string（版本字符串） | 引用语义或目标版本 | 未知时显式使用 `unresolved`，不得省略 |
| `source` | source descriptor（来源描述符） | 规范 Registry、Store、Adapter 或外部来源 | 必须可归因；路径存在不等于规范来源 |
| `status` | reference declaration status（引用声明状态） | 引用自身的声明生命周期 | 不得复用目标 Lifecycle 或 Verification 决定 |

### 6.1 `reference_type` 值

```text
ENTITY
CANDIDATE
AUTHORIZATION
REGISTRATION
EXECUTION
EVIDENCE
VERIFICATION
```

### 6.2 Reference Object `status` 值

```text
DECLARED
SUPERSEDED
REVOKED
UNKNOWN
```

- `DECLARED`：引用对象已声明，但不表示目标已解析；
- `SUPERSEDED`：存在明确 successor 引用；
- `REVOKED`：引用不应继续用于新决定，但历史解析仍可报告；
- `UNKNOWN`：引用自身状态未确认。

Reference Object `status` 与 Resolution Result 的 `resolution_status` 是不同字段。

### 6.3 概念示例

```yaml
reference_id: "<source-owned-id>"
reference_type: "EVIDENCE"
namespace: "external:<authority>"
version: "unresolved"
source: "<declared-source-descriptor>"
status: "UNKNOWN"
```

该示例不创建真实引用或 API 输入。

## 7. Resolution Request（解析请求）

解析请求由一个 Reference Object 和可选的显式策略构成。策略只能缩小查找范围，不能授予 Resolver 新权力。

允许的未来策略概念：

- `exact_version_only=true`；
- `allow_registered_aliases=false`；
- `include_superseded=false`；
- `include_revoked=false`；
- `source_allowlist`；
- `network_access=false`。

安全默认值必须是精确版本、禁止未登记 alias（别名）、排除撤销目标、显式 Source allowlist（允许列表）和无网络访问。

## 8. Resolution Result（解析结果）

Resolution Result 必须包含可机器检查的状态和诊断。以下为概念字段，不是实现 API：

```text
request_reference
resolution_status
resolved_reference
resolved_type
resolved_source
resolved_version
target_status
candidates
diagnostics
limitations
authority_effect
verification_effect
permission_effect
```

三个 effect 字段必须固定为 `NONE`。

### 8.1 `RESOLVED`

含义：在声明 Namespace、Reference Type、Version 和 Source 内找到唯一、精确匹配的目标记录。

不表示：

- 目标内容真实；
- 身份已认证或验证；
- Authorization 当前有效；
- Evidence 达到某等级；
- Verification 通过；
- Permission 已授予；
- Entity 已激活或成为 Agent。

### 8.2 `AMBIGUOUS`

含义：存在两个或以上无法按规范规则唯一选择的候选目标，或多个 Source 对同一引用给出冲突结果。

要求：

- 返回候选引用和冲突 Source；
- 不选择“最像”、最新、路径最近或优先级未声明的目标；
- 不进行生命周期、版本或身份自动合并；
- 调用方必须提供更精确 Namespace、Version、Source 或人工决定。

### 8.3 `UNKNOWN`

含义：Reference Object 结构有效，但没有可用规范 Source、没有匹配记录、版本未解析，或查找范围不足。

要求：

- 保留原始 Reference Object；
- 返回缺失条件；
- 不把未知目标自动登记；
- 不搜索整个工作区并把目录命中当作规范记录。

### 8.4 `INVALID`

含义：Reference Object 缺少必填字段、Reference Type 不支持、Namespace 格式非法、Source 不允许、Version 与受控格式冲突，或请求试图触发禁止效果。

要求：

- 返回确定性错误；
- 不访问 Source；
- 不产生部分解析结果；
- 不降级为 `UNKNOWN` 以掩盖结构错误。

## 9. Deterministic Resolution Procedure（确定性解析流程）

未来实现必须按以下顺序执行：

1. 验证六字段 Reference Object 完整性；
2. 验证 `reference_type` 和 Reference Object `status`；
3. 解析显式 Namespace，禁止默认到 `dbio`；
4. 检查 Source 是否属于该 Namespace 的允许来源；
5. 使用精确 `reference_id` 和 `version` 查找；
6. 如允许 alias，只读取已登记、带来源的 alias relation（别名关系）；
7. 检测零个、一个或多个目标；
8. 检查目标类型与请求类型一致；
9. 原样附带目标 status、provenance（来源）、successor 和 revocation 信息；
10. 返回四种 Resolution Result 之一。

Resolver 不执行后续 Verification、Authorization、Permission、Lifecycle Transition 或 Evidence Promotion。

## 10. Canonical Source Model（规范来源模型）

| 引用类型 | 当前可确认 Source | 当前缺口 |
|---|---|---|
| Entity | `registry/entities.yaml` | 尚无通用 Resolver 接口；兼容视图不可替代规范 Source |
| Candidate | 调用方提供的 Candidate records/store | 没有全局 Candidate Registry 或默认 live path |
| Authorization | 调用方显式配置的 append-only Authorization Store | 没有默认 live path；解析不判断当前有效性 |
| Registration | 调用方显式配置的 Registration/Receipt Store | 需要区分 attempt、record 和 receipt |
| Execution | 当前主要为内存 Execution Record 或特定实验记录 | 没有统一持久化 Execution Registry |
| Evidence | 既有 DBOS Evidence registries 和明确外部 Source | Evidence 类型分散；解析不验证事实 |
| Verification | `registry/verification-records.yaml`、`registry/verification-runs.yaml` 或明确外部 Source | 记录可能为 `pending/V0`；解析不升级决定 |

如果某种类型没有已登记 Source，结果必须保持 `UNKNOWN`。Resolver 规范不通过创建中央数据库填补该缺口。

## 11. Identity Provider Boundary（身份提供者边界）

Resolver 不执行：

- 用户登录或账户管理；
- 密钥、Token（令牌）或 Credential（凭据）签发；
- 人或组织身份认证；
- DID（去中心化标识符）控制证明；
- Owner、Issuer 或 Producer 的真实性背书；
- Entity ID minting（铸造）或 Canonical ID 分配。

解析 `identity_ref` 只定位声明的身份记录；身份验证属于独立 Evidence 和 Verification 流程。

## 12. Authority and Permission Boundary（权力与权限边界）

Resolver 输出中禁止出现由查找推导的：

- `permission_granted=true`；
- `capability_assigned=true`；
- `entity_activated=true`；
- `authorization_effective=true`；
- `verification_passed=true`；
- `trust_granted=true`。

Resolver 可以原样返回目标记录声明的字段，但必须标注 `asserted_by_source`（由来源声明），不能改写为 Resolver 决定。

## 13. Cache and Index Boundary（缓存与索引边界）

未来实现可以建立只读 Cache（缓存）或 Index（索引）以提高查找效率，但：

- Cache 不是规范 Source；
- 每个结果必须保留 Source、Version、摘要和观察时间；
- Cache miss（缓存未命中）不能证明目标不存在；
- 过期 Cache 不能覆盖 Source 的撤销或 successor；
- Cache 不得持久化未授权的 Evidence 正文或敏感数据；
- 删除 Cache 不得删除历史 Evidence 或 Source 记录。

## 14. Security and Privacy Boundary（安全与隐私边界）

未来 Resolver 必须：

- 默认禁止网络访问；
- 使用 Source allowlist，禁止任意 URL 抓取；
- 拒绝路径穿越、符号链接越界和本地敏感文件读取；
- 对外部 Namespace 使用独立 Adapter；
- 不在诊断中泄露 Token、密钥、个人数据或 Evidence 正文；
- 对超时、不可达和拒绝访问返回 `UNKNOWN`，并保留原因；
- 对恶意或格式非法输入返回 `INVALID`；
- 限制 alias 链深度并检测循环。

## 15. Developer Impact（开发者影响）

开发者和 Extension 需要：

1. 为每个引用声明 Type、Namespace、Version 和 Source；
2. 不再依赖裸字符串或目录搜索表达规范含义；
3. 显式处理 `RESOLVED/AMBIGUOUS/UNKNOWN/INVALID`；
4. 把解析结果和 Verification、Authorization、Permission 分开；
5. 在日志和 Trust Package（信任包）中保留 Resolution Result 与限制；
6. 为外部系统提供 Namespace Adapter，而不是占用 `dbio`；
7. 在 Source 或 Version 缺失时保持未知。

这会增加初始集成工作，但可避免 Adapter 和 Developer Extension 生成互不兼容或越权的引用语义。

## 16. SDK Integration Path（SDK 集成路径）

本规范不授权实现。未来 SDK 路径为：

1. 冻结 Reference Object 和 Resolution Result schema；
2. 冻结 Namespace registration（命名空间登记）与 collision policy（冲突策略）；
3. 定义结构化 error taxonomy（错误分类）；
4. 实现只读、无网络、本地 Source Resolver 的最小原型；
5. 为七种 Reference Type 建立正向和负向 fixture（测试夹具）；
6. 验证 `AMBIGUOUS/UNKNOWN/INVALID` 全部失败关闭；
7. 将概念 `dbos.resolve(...)` 接入未来 Developer Kit；
8. 分别建立 LangChain、CrewAI 和 MCP Namespace Adapter conformance（适配器符合性）测试；
9. 在真实外部 Agent 试点前进行安全、隐私和独立审查。

每一步需要单独授权；规范完成不等于 SDK 实现开始。

## 17. Invariants（不变量）

```text
DBOS_ROLE=INFRASTRUCTURE
RESOLVER_NE_DATABASE=true
RESOLVER_NE_IDENTITY_PROVIDER=true
RESOLVER_NE_VERIFICATION=true
RESOLVER_NE_PERMISSION_SYSTEM=true
REFERENCE_NE_AUTHORITY=true
REFERENCE_NE_TRUTH=true
RESOLVED_NE_VERIFIED=true
RESOLVED_NE_AUTHORIZED=true
RESOLVED_NE_PERMISSION=true
UNKNOWN_REMAINS_UNKNOWN=true
CANONICAL_SOURCE_OWNERSHIP_PRESERVED=true
CURRENT_RESOLVER_IMPLEMENTATION=false
CURRENT_RESOLVER_API=false
```

## 18. Related Documents（关联文档）

- `reference-namespace-model.md`
- `reference-resolution-boundary-rules.md`
- `ADR-017-canonical-reference-resolver.md`
- `developer-kit-specification.md`
- `developer-quickstart-model.md`
- `developer-trust-model.md`
- `entity_support/README.md`
- `registry/entities.yaml`

本规范不创建 Resolver、Database、Identity Provider、API、SDK、Entity、Agent、Runtime、Capability、Permission 或 Verification 决定，不修改 DBA 或 SAEE。
