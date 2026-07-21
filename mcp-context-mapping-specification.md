# DBOS MCP Context Mapping Specification v0.1（DBOS MCP 上下文映射规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

映射实例：`0`

## 1. Purpose and Protocol Boundary（目的与协议边界）

本规范定义调用方提供的 MCP-related Context Reference（MCP 相关上下文引用）如何转换为供 DBOS Execution Object（执行对象）使用的 Context Reference（上下文引用）。

```text
MCP_CONTEXT_IS_ADAPTER_INPUT_ABSTRACTION=true
MCP_CONTEXT_IS_UNIVERSAL_PROTOCOL_OBJECT=false
CONTEXT_REFERENCE_NE_EXECUTION_CONTEXT_RECORD=true
```

“MCP Context”在本规范中是 Adapter 输入抽象，不声明每个 MCP 修订都定义统一的顶层 `Context` 对象。任何 session（会话）、request（请求）、environment（环境）、conversation（对话）或 extension（扩展）语义都必须由精确协议修订、Source 和 Mapping Profile 明确给出。

## 2. Required Input Fields（必需输入字段）

| 字段 | 语义 | 约束 |
|---|---|---|
| `context_reference` | Source 拥有的上下文引用 | 不由 Adapter 猜测或签发 |
| `namespace` | 上下文语义命名空间 | 不能默认为 `dbio` |
| `source` | 上下文来源 | 必须可归属 |
| `version` | 上下文表示版本 | 与 MCP 修订和 DBOS 对象版本分离 |
| `context_kind` | 调用方声明的上下文类别 | 只允许 Mapping Profile 明确支持的值 |
| `server_reference` | 相关 Server 外部引用 | 不创建 Entity 或 Agent |
| `scope` | 上下文适用范围 | 必须显式，不允许全局默认 |
| `mcp_protocol_revision` | 精确 MCP 修订 | 缺失时不能选择 Mapping Profile |
| `mapping_profile_version` | 精确 Context 映射配置版本 | 必须声明对 `context_kind` 的处理 |
| `limitations` | 可复现性、隐私和来源限制 | 至少一项 |

允许的 `context_kind` 不是全局固定枚举。每个 Mapping Profile 必须列出受支持值；未列出的值返回 `UNRESOLVED_CONTEXT`，不得按名称相似性映射。

## 3. Output Reference Model（输出引用模型）

成功形成的候选必须保持 Canonical Reference Resolver（规范引用解析器）的六字段语义：

| 输出字段 | 来源 | 约束 |
|---|---|---|
| `reference_id` | `context_reference` | 保留 Source 所有权；不得变成 `dbio` ID |
| `reference_type` | 固定 `EXECUTION_CONTEXT` Adapter 子类型 | 只供 Execution Object 使用，不扩展核心七类引用登记 |
| `namespace` | 输入 `namespace` | 外部或 Adapter Namespace，不能覆盖规范 Namespace |
| `version` | 输入 `version` | 不隐式选择最新 |
| `source` | 输入 `source` | 保留 Server、协议修订与 Origin 绑定 |
| `status` | `DECLARED/UNKNOWN` | Adapter 不产生 `RESOLVED`；解析结果由 Resolver 决定 |

`EXECUTION_CONTEXT` 在此是 Adapter 使用的类型化引用标签，不创建 `registry/execution-contexts.yaml` 记录，也不改变现有 Canonical Reference Type（规范引用类型）集合。

## 4. Preservation Rules（保留规则）

必须保留：

- `namespace`、`source`、`version`、`context_kind` 和 `scope`；
- MCP 协议修订、Server 引用和 Mapping Profile 版本；
- 调用方提供的 configuration/input snapshot reference（配置/输入快照引用），但不读取正文；
- 隐私分类、保留期限和已知可复现性限制；
- 原始引用与映射后引用之间的可检查关系。

禁止：

- 把会话 ID、请求 ID、目录、环境名称或进程 ID 推断为 Entity、Agent 或 Runtime；
- 捕获 Context 正文、Prompt、Secret、Token 或 Credential；
- 生成缺失配置摘要、环境摘要或时间戳；
- 把 Context reference 声明为 frozen（已冻结）、reproducible（可复现）或 verified（已验证）；
- 因某协议修订存在会话语义而假设其他修订也存在。

## 5. Resolution and Error Rules（解析与错误规则）

- Reference Resolver 返回 `RESOLVED` 才能把该引用用于结构完整的 Execution Object Candidate；
- `RESOLVED` 仍不表示 Context 真实、完整、授权、冻结或可复现；
- 零个目标、缺失 Source/Namespace/Version 或不支持的 `context_kind` 返回 `UNRESOLVED_CONTEXT`；
- 多个目标、同一 ID 对应不同 Source/Scope 或版本返回 `CONFLICTING_REFERENCE`；
- 协议修订和 Mapping Profile 不兼容返回 `VERSION_MISMATCH`；
- 错误不触发工作区扫描、网络解析、默认 Context 或 Runtime 创建。

## 6. Explicit Non-effects（明确无效果）

```text
CONTEXT_MAPPING_INSTANCE_COUNT=0
EXECUTION_CONTEXT_RECORD_CREATED=false
RUNTIME_CREATED=false
AGENT_CREATED=false
ENTITY_CREATED=false
CONTEXT_CONTENT_CAPTURED=false
CONFIGURATION_DIGEST_GENERATED=false
PERMISSION_GRANTED=false
```
