# DBOS MCP Adapter Specification v0.1（DBOS MCP 适配器规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

实现状态：`MINIMAL_SYNTHETIC_TOOL_CALL_REFERENCE_ONLY`

兼容性声明：`NONE`

规范日期：`2026-07-21`

## 1. Purpose（目的）

本规范冻结未来 MCP Adapter（MCP 适配器）把调用方提供的 MCP（Model Context Protocol，模型上下文协议）表示转换为 DBOS 候选表示或引用时必须遵守的输入、输出、生命周期、错误、版本和安全规则。

```text
MCP source representation（MCP 来源表示）
  -> explicit adapter eligibility check（显式适配器资格检查）
  -> version-bound mapping profile（版本绑定映射配置）
  -> DBOS candidate or context reference（DBOS 候选或上下文引用）
  -> canonical Validator（规范验证器）
  -> Validation Result（验证结果）
```

该管线只形成结构化候选。它不运行 Tool（工具）、不读取 Resource（资源）正文、不建立 Agent（智能体）身份，也不把外部声明变成 DBOS Fact（DBOS 事实）。

## 2. Normative Position（规范定位）

```text
MCP_EVENT_NE_DBOS_OBJECT=true
MAPPING_NE_VERIFICATION=true
CANDIDATE_NE_CANONICAL_OBJECT=true
ADAPTER_AUTHORITY_INCREASE=false
TOOL_NE_CAPABILITY=true
RESOURCE_NE_EVIDENCE_TRUTH=true
```

- MCP Event（MCP 事件）必须先经过字段级转换，不能直接写入 DBOS 对象层；
- Mapping（映射）只表达受控字段关系，不验证来源真实性、执行发生或业务结果；
- Candidate（候选）即使通过结构验证，也不会自动登记为 Canonical Object（规范对象）；
- Adapter 不能增加调用方、Server（服务器）、Client（客户端）或 Tool 的 Authority（权力）；
- MCP 访问控制、凭据或授权决定不能转换为 DBOS Permission（权限）；
- 本规范不定义 MCP Runtime（MCP 运行时）、MCP Server、MCP Client 或 Agent Framework（智能体框架）。

## 3. Scope（范围）

v0.1 只定义以下三类只读转换：

1. `TOOL_CALL`：Tool Call（工具调用）引用到 Execution Object Candidate（执行对象候选）；
2. `RESOURCE`：Resource 引用到 Evidence Reference Candidate（证据引用候选）；
3. `CONTEXT_REFERENCE`：调用方声明的上下文引用到 DBOS Context Reference（DBOS 上下文引用）。

`CONTEXT_REFERENCE` 是 DBOS Adapter Input Abstraction（DBOS 适配器输入抽象），不是对所有 MCP 协议修订中存在统一 `Context` 顶层对象的声明。

不在范围内：Prompt（提示）映射、Sampling（采样）、模型推理、任务调度、网络连接、凭据处理、Resource 正文采集、Tool 执行、Event 写入、对象登记、Evidence 保存和 Verification（验证）决定。

## 4. Common Input Model（公共输入模型）

未来每次映射输入必须包含以下概念字段。字段集合是规范，不是已实现 Schema（模式）或 API（应用程序接口）。

| 字段 | 必填 | 语义 | 约束 |
|---|---|---|---|
| `input_type` | 是 | `TOOL_CALL/RESOURCE/CONTEXT_REFERENCE` | 不允许调用方自定义类型 |
| `mcp_protocol_revision` | 是 | 来源表示所依据的精确 MCP 修订 | 禁止 `latest/main/current` |
| `mcp_source_namespace` | 是 | 来源语义所有者 | 不能默认为 `dbio` |
| `source_reference` | 是 | 可归属 MCP 来源引用 | 网络位置不自动证明来源真实性 |
| `server_reference` | 是 | 来源 Server 的外部引用 | 不创建 Entity 或 Agent |
| `object_reference` | 是 | Tool Call、Resource 或 Context 的原始引用 | 必须保留类型，不能互换 |
| `object_version` | 是 | 外部对象或声明版本 | 与协议、DBOS 对象版本分离 |
| `mapping_profile_version` | 是 | 精确字段映射配置版本 | 必须与协议修订显式配对 |
| `payload_reference` | 否 | 输入正文或内容的外部引用 | Adapter 不读取或复制正文 |
| `observed_at` | 否 | 来源明确提供的观察时间 | 缺失保持 `null`，禁止补造 |
| `limitations` | 是 | 已知缺口、敏感边界和适用范围 | 至少一项，不能为空 |

缺少任一必填字段、字段类型冲突或来源无法归属时，不得产生候选对象。未知值必须保留为 `UNKNOWN`，不能通过目录名、Tool 名、Server 名或相似字符串推断。

## 5. Common Output Model（公共输出模型）

未来 Adapter 输出必须使用以下概念封装：

| 字段 | 语义 | 约束 |
|---|---|---|
| `mapping_reference` | 本次转换的惰性引用 | 不是 Evidence、Event 或 Canonical ID |
| `mapping_profile_version` | 实际使用的映射版本 | 不得隐式替换 |
| `source_bindings` | 原始类型、Namespace、版本和来源绑定 | 必须可检查且不可改写 |
| `candidate_type` | `EXECUTION/EVIDENCE_REFERENCE/CONTEXT_REFERENCE/null` | `null` 表示未形成候选 |
| `candidate_payload` | 结构化候选表示 | 不能包含 Permission、Authority 或执行命令 |
| `mapping_status` | 映射状态 | 只允许下述五值 |
| `errors` | 结构化 Adapter 错误 | 不自动修复或重试 |
| `limitations` | 未验证事实和适用范围 | 必须保留输入限制并增加映射限制 |
| `validation_input_reference` | 可交给核心 Validator 的惰性引用 | 不表示 Validator 已运行或通过 |
| `authority_effect` | 权力效果 | 固定为 `NONE` |
| `permission_effect` | 权限效果 | 固定为 `NONE` |

`mapping_status` 只允许：

```text
MAPPED
REJECTED
UNKNOWN
CONFLICT
VERSION_MISMATCH
```

`MAPPED` 只表示所需字段可以形成候选，不等于 `PASS`、`RESOLVED`、执行成功、Evidence 真实或对象已登记。

## 6. Mapping Lifecycle（映射生命周期）

未来单次映射只能按顺序进入：

```text
RECEIVED
  -> ELIGIBILITY_CHECKED
  -> CANDIDATE_PRODUCED
  -> VALIDATION_PENDING
  -> VALIDATION_RECORDED
  -> RETIRED
```

任一步都可以进入 `REJECTED`，但不得跳过 `ELIGIBILITY_CHECKED`、版本选择或核心 Validator。生命周期规则：

- `RECEIVED` 不表示来源可信；
- `CANDIDATE_PRODUCED` 不表示创建 DBOS 对象；
- `VALIDATION_RECORDED` 只引用 Validation Result，不产生 Verification 或 Permission；
- 被撤销或替代的映射配置必须追加记录，不能覆盖旧输入、输出、错误和限制；
- 本规范不创建 mapping registry（映射登记表）或任何真实生命周期记录。

## 7. Type-specific Specifications（类型专属规范）

- `mcp-tool-call-mapping-specification.md`：Tool Call 到 Execution Object Candidate；
- `mcp-resource-mapping-specification.md`：Resource 到 Evidence Reference Candidate；
- `mcp-context-mapping-specification.md`：调用方上下文引用到 DBOS Context Reference；
- `mcp-error-handling-specification.md`：Adapter 错误代码、优先级和无副作用边界；
- `mcp-version-compatibility-policy.md`：独立版本轴、兼容、弃用和不支持策略。

## 8. Error Handling（错误处理）

v0.1 Adapter 错误代码：

```text
INVALID_TOOL_REFERENCE
UNKNOWN_RESOURCE
VERSION_MISMATCH
UNRESOLVED_CONTEXT
CONFLICTING_REFERENCE
```

所有错误必须 explainable（可解释）、deterministic（确定性）且 fail-closed（失败关闭）。错误不得触发外部查找、默认 Tool、默认 Resource、默认 Context、自动降级、自动重试或部分规范登记。

## 9. Version Policy（版本策略）

协议修订、Server 实现、Client/Collector（客户端/采集器）、Adapter 规范、Adapter 实现、Mapping Profile（映射配置）、DBOS Object Contract（对象契约）、Schema 和 Validator 版本必须分别记录。

当前状态：

```text
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
DEFAULT_MCP_PROTOCOL_REVISION=null
MCP_VERSION_COMPATIBILITY_CLAIM=NONE
MUTABLE_LATEST_ALLOWED=false
AUTOMATIC_DOWNGRADE=false
```

本规范冻结转换语义，但不选择或认证任何 MCP 协议修订。未来实现必须用精确修订和受控 fixture（测试夹具）建立版本矩阵；草案、候选版本或较新发布不得自动继承兼容性。

## 10. Security Rules（安全规则）

- 所有 Tool description（工具描述）、arguments（参数）、result（结果）、Resource 内容、Prompt 和 Context 文本均视为不可信数据；
- Adapter 不解释或执行内容中的指令；
- `external:<authority-id>` 与 `extension:<adapter-id>` Namespace（命名空间）必须和 `dbio` 隔离；
- 原始 ID、Source、Origin（来源原点）、协议版本和限制必须保留；
- Credential、Secret、Token（凭据、秘密、令牌）不得进入候选、错误或日志；
- Resource 不得被读取、复制、哈希、签名或保存，除非未来另有独立授权；
- Adapter 不得写入 Canonical Evidence（规范证据）、Event、Registry（登记表）或 Evolution Ledger（演化台账）。

## 11. Validation Boundary（验证边界）

核心 Validator 可以检查候选结构和治理禁止字段。它不验证：

- MCP Server、Client 或 Source 身份；
- Tool Call 是否发生、成功或产生业务效果；
- Resource 内容真实、完整、相关或充分；
- Context 已冻结、可复现或获得授权；
- Adapter 与某协议修订的生产兼容性。

```text
VALIDATION_NE_VERIFICATION=true
VALIDATOR_PASS_NE_CANONICAL_REGISTRATION=true
VALIDATOR_PASS_NE_PERMISSION=true
VALIDATOR_PASS_NE_EXECUTION_RESULT=true
```

## 12. Implementation Prerequisites（实现前置条件）

实现或 Reference Adapter（参考适配器）开始前必须具备：

1. 获授权、脱敏、可复现的 Tool Call、Resource 和 Context 引用 fixture；
2. 精确 MCP 修订及 Server、Client、Adapter、Mapping Profile 和 DBOS 版本矩阵；
3. 字段级正向、缺失、冲突、注入、权限升级和版本差异测试；
4. 核心 Validator 桥接及“不能绕过”的负向证明；
5. Owner（所有者）、Repository（仓库）、License（许可证）、依赖、撤销和安全联系人；
6. 隐私、数据最小化、凭据隔离和日志披露审查；
7. 本地隔离 Probe（探针），保留全部失败和限制；
8. 真实外部开发者复核；
9. 新的明确实现授权。

当前这些条件未被本规范宣称完成。

受 `2026-07-21` 明确任务授权，`adapters/mcp/` 实现了一个更窄的 synthetic-only Tool Call reference slice（仅合成工具调用参考切片）。它只接受 DBOS 自有测试标记，不选择真实 MCP 修订，因此不满足也不取代真实接入的上述条件。

## 13. Test Harness Specification（测试环境规范）

`mcp-test-harness-specification.md` 冻结未来隔离 MCP Adapter Test Harness（MCP 适配器测试环境）的输入夹具、预期映射、验证预期、失败语义和安全边界。

它当前只提供设计输入：

- `mcp-test-fixture-model.md`：Tool Call（工具调用）、Resource（资源）和 Context（上下文）合成夹具字段；
- `mcp-positive-test-cases.md`：3 项未来支持版本下的规范正向案例；
- `mcp-negative-test-cases.md`：5 项必须拒绝的治理越界；
- `mcp-security-test-model.md`：5 项安全威胁案例；
- `ADR-027-mcp-test-harness.md`：为什么先冻结测试环境，再考虑 Adapter 实现。

该层现已拥有 Tool Call 的内存 fixture 模板、最小映射代码和 21 项本地单元测试。它没有 Resource/Context Adapter、真实协议 fixture、网络 Harness、持久化测试记录或生产结果，也不证明本规范第 12 节的真实接入条件已经满足。当前受支持的真实协议修订和真实 Mapping Profile（映射配置）仍为空。

```text
MCP_TEST_HARNESS_SPECIFICATION=FROZEN_V0.1
MCP_TEST_HARNESS_IMPLEMENTATION=PARTIAL_TOOL_CALL_ONLY
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
MCP_TEST_CASE_DEFINITION_COUNT=13
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
PERSISTED_MCP_HARNESS_RUN_RECORD_COUNT=0
PERSISTED_MCP_HARNESS_RESULT_RECORD_COUNT=0
```

## 14. Specification Non-effects（规范无效果）

```text
MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
MCP_REFERENCE_ADAPTER_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_RUNTIME_CONNECTED=false
MCP_SERVER_CREATED=false
MCP_CLIENT_CREATED=false
PERSISTED_MCP_MAPPING_INSTANCE_COUNT=0
SYNTHETIC_EXECUTION_CANDIDATE_IN_MEMORY=true
CANONICAL_DBOS_OBJECT_CREATED=false
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
CANONICAL_EVIDENCE_MODIFIED=false
VALIDATOR_OVERRIDDEN=false
SAEE_EVOLUTION_TRIGGERED=false
```

## 15. Related Documents（关联文档）

- `mcp-adapter-proposal.md`
- `mcp-object-mapping-model.md`
- `mcp-security-boundary.md`
- `mcp-adapter-risk-assessment.md`
- `mcp-test-harness-specification.md`
- `mcp-test-fixture-model.md`
- `mcp-positive-test-cases.md`
- `mcp-negative-test-cases.md`
- `mcp-security-test-model.md`
- `adapters/mcp/`
- `tests/mcp_adapter/`
- `adapter-boundary-specification.md`
- `object-contract-specification.md`
- `canonical-reference-resolver-specification.md`
- `ADR-024-mcp-adapter-proposal.md`
- `ADR-025-mcp-adapter-specification.md`
- `ADR-027-mcp-test-harness.md`
