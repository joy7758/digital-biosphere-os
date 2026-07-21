# DBOS MCP Adapter Proposal v0.1（DBOS MCP 适配器提案 v0.1）

状态：`PROPOSAL_ONLY_NOT_IMPLEMENTED`

实现授权：`NOT_AUTHORIZED`

MCP Adapter（MCP 适配器）实现数量：`0`

下游规范状态：`FROZEN_V0.1`

## 1. Purpose（目的）

MCP Adapter 是 External Integration Boundary（外部集成边界）。它未来可以接收调用方显式提供的 MCP（Model Context Protocol，模型上下文协议）引用，把受支持字段转换为 DBOS 对象候选或上下文引用，并交给现有 Validator（验证器）。

```text
MCP source representation（MCP 来源表示）
  -> MCP Adapter Mapping（MCP 适配器映射）
  -> DBOS candidate representation（DBOS 候选表示）
  -> canonical Validator（规范验证器）
```

MCP 负责外部连接语义；Adapter 负责转换；DBOS 负责对象、引用和验证边界。任何一层都不能自动替代另一层。

## 2. Core Principles（核心原则）

```text
MCP_EVENT_NE_DBOS_FACT=true
TOOL_AVAILABILITY_NE_CAPABILITY_VERIFICATION=true
MCP_PERMISSION_NE_DBOS_PERMISSION=true
ADAPTER_NE_AUTHORITY=true
MCP_SERVER_NE_DBOS_ENTITY=true
RESOURCE_AVAILABILITY_NE_EVIDENCE_TRUTH=true
```

- MCP Event（MCP 事件）是外部来源声明，不是 DBOS Fact（DBOS 事实）；
- Tool（工具）可见、可描述或可调用不表示 Capability（能力）已验证；
- MCP 层的访问允许、凭据或会话决定不产生 DBOS Permission（权限）；
- Adapter 不能拥有 Architecture Authority（架构权力）或 Validator 决定权；
- MCP Server（MCP 服务器）存在不自动建立 Entity 或 Agent 身份；
- Resource（资源）存在或可读取不表示 Evidence（证据）真实、完整或相关。

## 3. Scope（范围）

v0.1 提案只允许未来评估三类输入：

### Tool Invocation Reference（工具调用引用）

调用方提供的稳定 Tool、invocation（调用）、input、output、context 和 source 引用。满足 `mcp-object-mapping-model.md` 的最低条件时，可以形成惰性 `ExecutionObject` 候选；它不证明调用发生、成功或产生预期效果。

### Resource Reference（资源引用）

调用方提供的稳定 Resource ID/URI（资源标识/统一资源标识符）、Source、Version 和内容引用。只有存在明确 Execution Reference、可归因 Source 与限制时，才可以形成 `EvidenceReferenceObject` 候选；否则只保留外部资源引用并返回 `UNKNOWN`。

### Context Reference（上下文引用）

调用方提供的会话、请求、环境或其他上下文引用。它可以被映射为 `ExecutionObject.context_reference` 所需的外部 Reference Object（引用对象），但不创建 DBOS Execution Context（执行上下文）记录或 Runtime（运行时）。

## 4. Allowed Transformations（允许转换）

未来 MCP Adapter 可以：

- 保留并包装 MCP Tool、invocation、Resource 和 Context 的外部引用；
- 把符合最低字段要求的 Tool Call（工具调用）映射为 Execution Object Candidate（执行对象候选表示）；
- 把符合来源与执行关联要求的 Resource 映射为 Evidence Reference Candidate（证据引用候选表示）；
- 把显式 Context 映射为 Execution Context Reference（执行上下文引用）；
- 记录 MCP 来源、协议版本、Server 来源、Adapter 版本和映射限制；
- 生成现有 DBOS Object Schema（对象模式）能够检查的输入；
- 在缺失、冲突或不兼容时返回结构化失败。

所有转换都必须是只读、显式、可复现且失败关闭的。

## 5. Forbidden Transformations（禁止转换）

MCP Adapter 禁止：

- 创建或登记 Entity（实体）、Agent（智能体）或 MCP Server 身份；
- 从 Tool 列表、Tool description（工具描述）或调用成功推导 Capability Grant（能力授予）；
- 把 MCP 访问决定、token（令牌）、credential（凭据）或会话权限转为 DBOS Permission；
- 启动 MCP Runtime、Server、Client、模型、Tool 或任务；
- 把 Tool result（工具结果）自动升级为 DBOS Fact、Evidence Truth 或 Verification `PASS`；
- 复制、覆盖、删除或改写 Canonical Evidence（规范证据）；
- 修改历史 hash、时间戳、签名、Source 或限制；
- 绕过、替换或弱化核心 Validator；
- 创建 Capability Object、Verification Object 或 Event Record（事件记录）作为自动副作用；
- 触发 SAEE Evolution（SAEE 演化）、Fitness（适应度）、选择或任何 C/E/V 等级变化。

## 6. Responsibility Model（责任模型）

| 层 | 负责 | 不负责 |
|---|---|---|
| MCP 外部生态 | 连接、Tool/Resource 暴露、调用方定义的传输和访问控制 | DBOS 对象、证据和权限语义 |
| MCP Adapter | 显式字段映射、来源保留、限制与失败报告 | 连接运行、Agent 行为、权限、事实验证 |
| DBOS SDK/Validator | 对象表示、机器模式、结构与治理边界检查 | MCP Runtime、远程调用、事实来源认证 |
| 独立治理流程 | 登记、Evidence 复核、Verification 与授权决定 | 由 Adapter 自动替代 |

## 7. Proposal Non-effects（提案无效果）

```text
MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
MCP_ADAPTER_IMPLEMENTED=false
MCP_RUNTIME_CONNECTED=false
MCP_SERVER_CREATED=false
MCP_CLIENT_CREATED=false
MCP_EVENT_INGESTED=false
DBOS_OBJECT_CANDIDATE_CREATED=false
ENTITY_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EVIDENCE_MODIFIED=false
VALIDATOR_OVERRIDDEN=false
EVOLUTION_TRIGGERED=false
```

本提案不创建 Schema、代码、SDK API（软件开发工具包接口）、网络连接、映射实例或兼容性声明。

## 8. Future Implementation Gates（未来实现条件）

本轮明确文档授权允许建立 MCP Adapter Specification（MCP 适配器规范），但不表示以下实现证据已经存在。进入 Adapter 实现或 Reference Adapter（参考适配器）前，必须分别满足：

1. `MCP-G1 SOURCE_FIXTURE`：具有授权、脱敏、可复现的 MCP 输入样本和来源说明；
2. `MCP-G2 VERSION_MATRIX`：固定 MCP 协议、Server、Client、Adapter、Mapping Profile 和 DBOS 契约版本；
3. `MCP-G3 MAPPING_CONTRACT`：Tool Call、Resource、Context 的字段级 Schema 与未知值语义冻结；
4. `MCP-G4 THREAT_MODEL`：Tool injection（工具注入）、证据污染、权限升级和数据泄露负向案例可测试；
5. `MCP-G5 VALIDATOR_CONFORMANCE`：证明输出不能绕过或弱化核心 Validator；
6. `MCP-G6 SUPPLY_CHAIN`：Repository、Owner、License、依赖、撤销和安全联系人明确；
7. `MCP-G7 HUMAN_AUTHORIZATION`：具体实现范围获得新的明确授权；
8. `MCP-G8 LOCAL_PROBE`：只在隔离环境运行本地探针，保留失败，不声称生产兼容；
9. `MCP-G9 EXTERNAL_REVIEW`：真实外部开发者复核映射、限制和失败语义。

任何 Gate（闸门）通过都不自动授权下一个 Gate。

`mcp-adapter-specification.md` 已冻结字段、生命周期、错误和版本语义，但没有真实 fixture（测试夹具）、版本矩阵或运行证据，因此不自动把 `MCP-G1` 至 `MCP-G9` 标记为通过。

## 9. Pre-development Agent Consultation（开发前智能体咨询）

```text
RECOMMEND_MCP_ADAPTER_PROPOSAL=true
RECOMMEND_MCP_ADAPTER_CODE=false
RECOMMEND_MCP_RUNTIME_INTEGRATION=false
RECOMMEND_PRODUCTION_COMPATIBILITY_CLAIM=false
```

提案值得推荐，因为 MCP 引用、Tool 调用和 Resource 来源需要统一的 DBOS 映射边界。不推荐实现，因为当前没有受控样本、版本矩阵、威胁模型验证、供应链材料或外部试点授权。

## 10. Related Documents（关联文档）

- `adapter-boundary-specification.md`
- `adapter-object-mapping-model.md`
- `adapter-security-boundary-rules.md`
- `mcp-object-mapping-model.md`
- `mcp-security-boundary.md`
- `mcp-adapter-risk-assessment.md`
- `ADR-024-mcp-adapter-proposal.md`
- `mcp-adapter-specification.md`
- `mcp-tool-call-mapping-specification.md`
- `mcp-resource-mapping-specification.md`
- `mcp-context-mapping-specification.md`
- `mcp-error-handling-specification.md`
- `mcp-version-compatibility-policy.md`
- `ADR-025-mcp-adapter-specification.md`
