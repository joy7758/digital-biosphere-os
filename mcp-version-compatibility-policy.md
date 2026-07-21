# DBOS MCP Version Compatibility Policy v0.1（DBOS MCP 版本兼容政策 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

受支持协议修订：`NONE`

兼容性测试证据：`NONE`

## 1. Purpose（目的）

本政策定义未来 MCP Adapter（MCP 适配器）如何声明、判定、弃用和停止支持 MCP（Model Context Protocol，模型上下文协议）版本。它不选择默认协议、不实现兼容层，也不证明任何 Server（服务器）或 Client（客户端）可以互操作。

## 2. Independent Version Axes（独立版本轴）

以下版本必须分别记录：

| 版本轴 | 语义 | 缺失时处理 |
|---|---|---|
| `mcp_protocol_revision` | MCP 规范修订 | `VERSION_MISMATCH`，停止映射 |
| `mcp_server_implementation_version` | Source Server 实现版本 | `UNKNOWN`，除非配置明确允许 |
| `mcp_client_or_collector_version` | 提供输入的 Client/Collector（客户端/采集器）版本 | `UNKNOWN`，不得推断 |
| `mcp_adapter_specification_version` | 本转换规范版本 | 必须精确匹配受支持矩阵 |
| `mcp_adapter_implementation_version` | 未来 Adapter 代码版本 | 当前为 `null` |
| `mcp_mapping_profile_version` | 类型和修订专属字段映射版本 | 缺失时停止映射 |
| `dbos_object_contract_version` | DBOS 对象契约版本 | 不得由 Adapter 改写 |
| `dbos_schema_version` | 机器可读 Schema（模式）版本 | 必须由 Validator 明确选择 |
| `dbos_validator_version` | 核心 Validator（验证器）版本 | 结果必须记录 |

相同字符串出现在多个版本轴上不表示语义相同或自动兼容。

## 3. Compatibility States（兼容状态）

### 3.1 `COMPATIBLE`

只有以下条件全部满足才能声明：

- 精确协议修订与 Mapping Profile 已列入批准矩阵；
- Tool Call、Resource 和 Context Reference 的受支持字段形状明确；
- 正向、负向、未知、冲突、版本差异和安全 fixture（测试夹具）全部通过；
- Validator 桥接未被绕过；
- 兼容范围、限制、环境和撤销路径已记录；
- 获得针对该版本组合的人工批准。

`COMPATIBLE` 只说明该组合在声明映射范围内通过测试，不证明生产适用性、Source 真实性或 Tool 安全。

### 3.2 `DEPRECATED`

某个已支持组合不再推荐用于新接入，但仍处于明确迁移窗口：

- 必须保留旧 Mapping Profile、测试、错误和结果；
- 必须声明替代版本、迁移限制和停止支持日期；
- 新字段或新协议功能不能反向注入旧配置；
- Deprecated（已弃用）不等于失效、删除或历史错误。

### 3.3 `UNSUPPORTED`

没有批准矩阵、已越过停止支持日期、使用草案/候选修订但未单独批准，或发生未映射的 Breaking Change（破坏性变更）时，状态为 `UNSUPPORTED`。

- 返回 `VERSION_MISMATCH`；
- 不选择最近版本；
- 不自动降级、升级或裁剪字段后继续；
- 不产生 DBOS 候选对象。

## 4. Version Selection Rules（版本选择规则）

- 必须由输入明确声明 `mcp_protocol_revision`；
- 禁止 `latest`、`main`、`current`、空字符串和仅依赖 Server 自报“兼容”；
- 精确协议修订必须唯一选择一个批准的 Mapping Profile；
- 一个 Mapping Profile 不能在没有独立 fixture 的情况下覆盖多个协议修订；
- Draft（草案）、Release Candidate（发布候选）和正式发布属于不同支持目标；
- 协议修订更改生命周期、请求方法、字段、Capability negotiation（能力协商）或安全语义时，必须重新评估；
- 较新修订的存在不使较旧输入失效，也不允许覆盖历史结果。

## 5. Mapping Profile Lifecycle（映射配置生命周期）

```text
PROPOSED
  -> TESTED
  -> SUPPORTED
  -> DEPRECATED
  -> UNSUPPORTED
  -> RETIRED
```

- `PROPOSED` 和 `TESTED` 均不能用于生产兼容性声明；
- `SUPPORTED` 需要版本矩阵、测试证据和人工批准；
- `DEPRECATED/UNSUPPORTED/RETIRED` 采用追加记录，不能删除旧配置或结果；
- 安全撤销可以直接把未来使用阻断为 `UNSUPPORTED`，但历史状态仍保留；
- 状态变化不授予 Permission、Capability（能力）或 Authority（权力）。

## 6. Change Classification（变化分类）

以下变化至少需要新的 Mapping Profile revision（映射配置修订）：

- 仅文档澄清且字段和安全语义不变；
- 新增 Adapter 诊断元数据但不改变候选；
- 错误提示改进但错误代码和优先级不变。

以下变化需要新的 Mapping Profile generation（映射配置代际）并重新验证：

- Tool Call、Resource 或上下文引用字段增加、删除、重命名或类型变化；
- 协议生命周期、会话、传输或能力协商语义变化；
- Source、Origin、Namespace、ID 或版本所有权变化；
- 错误分类或判定顺序变化；
- 安全、授权、Resource 内容或 Tool 执行边界变化；
- DBOS Object Contract、Schema 或 Validator 的破坏性变化。

## 7. Current Compatibility Matrix（当前兼容矩阵）

```text
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
DEPRECATED_MCP_PROTOCOL_REVISIONS=[]
UNSUPPORTED_MCP_PROTOCOL_REVISIONS=[]
DEFAULT_MCP_PROTOCOL_REVISION=null
SUPPORTED_MAPPING_PROFILES=[]
MCP_COMPATIBILITY_FIXTURE_COUNT=0
MCP_COMPATIBILITY_EVIDENCE=false
MCP_PRODUCTION_COMPATIBILITY_CLAIM=false
```

空矩阵表示尚未选择或验证协议修订，不表示所有修订都不符合 MCP，也不表示 DBOS Adapter 已实现。

## 8. Prohibited Version Effects（禁止的版本效果）

```text
AUTOMATIC_VERSION_SELECTION=false
AUTOMATIC_UPGRADE=false
AUTOMATIC_DOWNGRADE=false
SILENT_FIELD_DROPPING=false
HISTORICAL_MAPPING_REWRITE=false
VERSION_STATUS_CAN_GRANT_PERMISSION=false
VERSION_STATUS_CAN_TRIGGER_EXECUTION=false
VERSION_STATUS_CAN_TRIGGER_EVOLUTION=false
```
