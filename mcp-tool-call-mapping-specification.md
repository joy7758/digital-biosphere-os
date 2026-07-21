# DBOS MCP Tool Call Mapping Specification v0.1（DBOS MCP 工具调用映射规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

实现状态：`MINIMAL_SYNTHETIC_REFERENCE_AVAILABLE`

持久化映射实例：`0`

## 1. Purpose（目的）

本规范定义未来 Adapter 如何把调用方提供的 MCP Tool Call（MCP 工具调用）表示转换为 Execution Object Candidate（执行对象候选）。它不调用 Tool、不创建 Execution Result（执行结果），也不证明调用发生。

```text
MCP_TOOL_CALL_NE_EXECUTION_FACT=true
MCP_TOOL_CALL_NE_EXECUTION_RESULT=true
TOOL_AVAILABILITY_NE_CAPABILITY=true
```

## 2. Required Input Fields（必需输入字段）

| 字段 | 语义 | 约束 |
|---|---|---|
| `tool_call_id` | Source 拥有的稳定调用引用 | 不直接成为规范 `execution_id` |
| `tool_name` | 来源声明的 Tool 名称 | 视为不可信字符串，不推导 Capability |
| `arguments_reference` | 参数或输入快照的外部引用 | 不复制、解析或执行参数正文 |
| `context_reference` | 调用方明确提供的上下文引用 | 必须符合 Context 映射规范 |
| `source_reference` | 可归属的 MCP 来源引用 | 网络端点或 Server 自报名称不足以认证 |
| `entity_reference` | 调用方明确提供的既有 Entity Reference（实体引用） | 禁止从 Server、Client、Tool 名称推断 |
| `server_reference` | Server 外部引用 | 不建立 Entity 或 Agent 身份 |
| `mcp_protocol_revision` | 精确 MCP 协议修订 | 禁止默认 `latest` |
| `mapping_profile_version` | 精确 Tool Call 映射配置版本 | 必须支持声明的协议修订 |
| `limitations` | 未验证事实与适用范围 | 至少一项 |

未来 Mapping Profile 可以要求协议方法引用，例如某个明确修订中的 `tools/call`。方法名称必须由版本配置声明，不能跨修订硬编码成通用事实。

## 3. Eligibility Rules（候选资格规则）

形成候选前必须同时满足：

- `tool_call_id` 在声明 Source 和 Namespace 中非空且类型明确；
- `entity_reference`、`arguments_reference` 和 `context_reference` 均为完整 Reference Object（引用对象）；
- Tool、Server、Source 与协议修订之间不存在冲突；
- 精确 Mapping Profile 支持该协议修订和 Tool Call 形状；
- 输入不包含要求 Adapter 执行 Tool、授予 Permission 或绕过 Validator 的字段；
- 原始字段和限制可保留，不需要猜测或内容解释。

条件不足不得产生部分 Execution 候选。

## 4. Field Mapping Rules（字段映射规则）

| MCP 输入 | Execution Object Candidate 字段 | 规则 |
|---|---|---|
| `tool_call_id` + Source + Mapping Profile | `object_id/execution_id` 的候选来源 | 未来只能在 Adapter 的 `extension:` Namespace 中确定性派生；不得签发 `dbio` ID |
| 固定目标类型 | `object_type=EXECUTION` | 只是候选类型 |
| DBOS 对象契约版本 | `version` | 与 MCP 协议修订分离 |
| `source_reference` | `source` | 必须保持 Owner、Namespace 和版本 |
| 固定安全值 | `status=UNKNOWN` | 不允许自动使用 `CREATED/RUNNING/SUCCESS/COMPLETED` |
| Source 明确提供的时间引用 | `created_at/updated_at` | 无可归属时间时保持 `null`；禁止使用 Adapter 当前时间补造 |
| 输入及映射限制 | `limitations` | 合并但不删除调用方限制 |
| `entity_reference` | `entity_reference` | 必须已经是外部或 DBOS 实体引用；不创建 Entity |
| Tool 的外部类型化引用 | `task_reference` | `tool_name` 不能单独成为 Task 或 Capability |
| `context_reference` | `context_reference` | 必须唯一解析；解析不创建 Context 或 Runtime |
| `arguments_reference` | `input_reference` | 只保留引用，不读取参数 |
| 无独立输出引用 | `output_reference=null` | Tool result 不作为自动副作用生成 |

`tool_name` 必须保留在 Tool 的外部 Reference metadata（引用元数据）或 Source binding（来源绑定）中，不能直接替代 `task_reference.reference_id`，除非对应 Mapping Profile 证明该名称在声明 Namespace 内稳定且唯一。

## 5. Tool Result Boundary（工具结果边界）

即使调用方另行提供 Tool result reference（工具结果引用）：

- 它最多成为 `output_reference` 的候选；
- 它不能产生 `result`、`success`、`runtime_started` 或 `permission_granted` 字段；
- MCP 的 `isError=false` 等外部状态不等于 DBOS 执行成功；
- 结果内容不自动成为 Event、Evidence、Attestation（证明）或 Verification `PASS`；
- Adapter 不执行、解释、总结或修改结果正文。

## 6. Error Mapping（错误映射）

| 条件 | Adapter 错误 |
|---|---|
| Tool Call ID、Tool 引用或 arguments 引用形状非法 | `INVALID_TOOL_REFERENCE` |
| Context 或 Entity 引用不能唯一解析 | `UNRESOLVED_CONTEXT` |
| Tool、Server、Source 或调用 ID 互相冲突 | `CONFLICTING_REFERENCE` |
| 协议修订或 Mapping Profile 不兼容 | `VERSION_MISMATCH` |

错误停止候选生成，不触发 Tool 重试、Source 扫描或默认对象创建。

## 7. Minimal Synthetic Reference Implementation（最小合成参考实现）

`adapters/mcp/` 实现本规范的一个严格子集：

- 只接受内存中的 Tool Call fixture（工具调用夹具）；
- 输入字段使用任务要求的 `protocol_revision`，其语义对应本规范的 `mcp_protocol_revision`；
- 额外要求 `entity_reference` 和 `mapping_profile_version`，禁止身份或版本推断；
- 唯一接受的修订是 `DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1`；
- 唯一接受的配置是 `dbos.synthetic.mcp-tool-call/v0.1`；
- 两者均为 DBOS 测试标记，不是实际 MCP 兼容声明；
- 候选只存在内存中，使用 `extension:` ID、`status=UNKNOWN` 和 `output_reference=null`；
- 映射后强制调用既有 DBOS Validator（DBOS 验证器）；
- 当前本地验证结果保持 `UNKNOWN`，不会把候选状态升级为执行事实。

测试入口为 `tests/mcp_adapter/`，当前包含 21 项本地单元测试。

## 8. Explicit Non-effects（明确无效果）

```text
PERSISTED_TOOL_CALL_MAPPING_INSTANCE_COUNT=0
SYNTHETIC_EXECUTION_CANDIDATE_IN_MEMORY=true
CANONICAL_EXECUTION_OBJECT_CREATED=false
EXECUTION_RESULT_CREATED=false
TOOL_INVOKED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EVENT_CREATED=false
EVIDENCE_CREATED=false
REAL_MCP_PROTOCOL_SUPPORTED=false
PRODUCTION_ADAPTER_READY=false
```
