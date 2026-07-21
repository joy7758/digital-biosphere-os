# DBOS MCP Security Boundary v0.1（DBOS MCP 安全边界 v0.1）

状态：`PROPOSAL_ONLY_NO_ENFORCEMENT`

安全认证：`NONE`

## 1. Namespace Isolation（命名空间隔离）

- MCP Tool、Resource、Context、Server 与 invocation 必须保留外部 Namespace（命名空间）；
- MCP Adapter 未来只能使用独立 `extension:<adapter-id>` Namespace；
- MCP Source 或 Adapter 不能签发、覆盖或冒充 `dbio` Canonical ID（规范标识）；
- 相同名称、URI host（统一资源标识符主机）、Server 名称或 Tool 名称不能自动建立身份等价；
- Namespace 缺失或冲突时返回 `INVALID/CONFLICT`，不选择默认 Source。

## 2. Reference Preservation（引用保留）

- 保留 Tool、Resource、Context、Server、invocation 的类型区别与原始 ID；
- 每个引用携带 Source、Version、Status 和限制；
- 默认不跟随 Alias（别名）、重定向或镜像；
- 不可解析引用保持 `UNKNOWN`，不能改写成本地路径后声称 `RESOLVED`；
- 输入与输出之间必须保留可检查 Mapping relation（映射关系）；
- Adapter 不修改、回收或复用外部 ID。

## 3. Source Attribution（来源归属）

未来每条输入必须区分：

```text
declared_mcp_source
transport_or_collection_source
mcp_server_reference
caller_reference
adapter_reference
mapping_profile_reference
```

连接端点、Server 自报名称、网络凭据或调用方账户不能单独证明 Source authenticity（来源真实性）。Source 不明确时不得形成 Evidence 候选或 DBOS Fact。

## 4. Untrusted Content Boundary（不可信内容边界）

Tool description、Tool input/output、Resource contents、Prompt（提示）和 Context 文本全部视为不可信数据：

- Adapter 不解释或执行其中的指令；
- 不把文本交给模型决定身份、权限或验证状态；
- 不允许内容覆盖 Mapping Profile、Namespace、Validator 或安全策略；
- 不允许 Tool/Resource 内容请求读取凭据、环境变量或未声明文件；
- 可疑或越界内容产生错误与限制，不触发工具调用。

这构成 Tool Injection（工具注入）与 Prompt Injection（提示注入）的第一道隔离，但提案文本本身不是运行时防护实现。

## 5. Failure Handling（失败处理）

| 条件 | 处理 |
|---|---|
| 输入或引用形状非法 | `FAIL/INVALID` |
| Source、Server、Context 或执行关联缺失 | `UNKNOWN` 并停止候选生成 |
| 同一 ID 指向不同类型或来源 | `CONFLICT` |
| 任一版本轴不兼容 | `VERSION_MISMATCH` |
| Tool/Resource 内容尝试修改规则 | `FAIL`，保留失败范围 |
| Validator 非 `PASS` | 原样返回，不修复或重试 |
| 部分映射成功 | 不产生部分规范登记或证据写入 |

失败不得转化为默认 Tool、默认 Server、默认 Entity 或默认 Permission。

## 6. Version Compatibility（版本兼容）

未来实现必须固定：

```text
mcp_protocol_version
mcp_server_implementation_version
mcp_client_or_collector_version
mcp_adapter_version
mcp_mapping_profile_version
dbos_object_contract_version
dbos_validator_version
```

- 缺失版本保持 `UNKNOWN`；
- 禁止用 `latest/main/current` 替代精确版本；
- 兼容性只在声明的版本、环境、输入类型和范围内成立；
- 协议或对象 Breaking Change（破坏性变更）需要新的 Mapping Profile；
- 旧映射、失败、限制和撤销记录必须保留。

## 7. Permission and Credential Isolation（权限与凭据隔离）

- MCP access decision（访问决定）与 DBOS Permission 是不同系统的决定；
- Adapter 不申请、缓存、刷新、转发或扩大凭据；
- Adapter 不因能看到 Tool 或 Resource 就获得调用权；
- 未来连接器如需网络或凭据，必须位于单独授权边界，并向 Adapter 提供最小、脱敏引用；
- 凭据内容不得进入 Object Candidate、Evidence Reference、错误或 Mapping Report；
- MCP Permission 被撤销不自动修改 DBOS 历史，DBOS Permission 也不能由 Adapter恢复。

## 8. Canonical Evidence Protection（规范证据保护）

- Adapter 只能产生 Evidence Reference Candidate（证据引用候选表示）；
- 不写入、覆盖、删除或重新签名 Canonical Evidence；
- 不生成缺失 hash、timestamp、signature（摘要、时间戳、签名）或 Source；
- Resource 更新形成新的外部版本引用，不能覆盖旧证据；
- Tool result、Resource 内容和 Server 日志不自动获得 E 等级；
- Evidence 与候选之间的关系需要独立复核，Adapter `PASS` 不足以证明。

## 9. Validator and Evolution Isolation（验证器与演化隔离）

```text
MCP_CAN_OVERRIDE_VALIDATOR=false
MCP_CAN_MINT_DBOS_PASS=false
MCP_CAN_TRIGGER_EVOLUTION=false
MCP_CAN_CHANGE_CEV_LEVEL=false
MCP_CAN_GRANT_PERMISSION=false
```

MCP Source、Server、Client、Adapter 和 Vendor（供应商）均不能修改核心 Validator、SAEE、C/E/V 等级、Fitness、Entity lifecycle（实体生命周期）或治理决定。

## 10. Privacy and Data Minimization（隐私与数据最小化）

未来实现必须默认：

- 只接收映射所需引用和元数据；
- 不收集 Tool input/output 或 Resource 正文；
- 对可能包含个人信息、密钥、业务数据的字段先阻断或脱敏；
- 不进行网络传输、遥测或持久化，除非另有明确授权；
- 声明保留期限、删除请求与历史证据保留之间的边界；
- 安全日志不能泄露原始敏感内容。

当前没有实现，因此这些要求尚未经过运行验证。
