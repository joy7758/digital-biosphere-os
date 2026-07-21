# DBOS MCP Object Mapping Model v0.1（DBOS MCP 对象映射模型 v0.1）

状态：`PROPOSAL_ONLY`

映射实例：`0`

## 1. Mapping Pipeline（映射管线）

```text
MCP Object or Reference（MCP 对象或引用）
  -> MCP Mapping Profile（MCP 映射配置）
  -> explicit read-only transformation（显式只读转换）
  -> DBOS candidate or reference（DBOS 候选表示或引用）
  -> canonical Validator（规范验证器）
```

本模型不定义 MCP 协议对象 Schema，不声称覆盖任何具体 MCP 版本。未来 Mapping Profile 必须绑定准确协议版本并以真实样本验证。

## 2. Common Input Requirements（公共输入要求）

每次未来映射至少需要调用方提供：

```text
mcp_protocol_version
mcp_source_namespace
mcp_source_reference
mcp_server_reference
mcp_object_type
mcp_object_reference
observed_or_declared_status
mapping_scope
limitations
```

缺少 Source、Version、Object Reference 或 Scope 时不得生成 DBOS 候选；结果保持 `UNKNOWN/FAIL`。

## 3. Tool Call to Execution Candidate（工具调用到执行候选）

目标：`ExecutionObject`（执行对象）候选表示。

最低映射：

| MCP 来源字段方向 | DBOS 目标 | 规则 |
|---|---|---|
| 稳定 invocation reference（调用引用） | `execution_id/object_id` 的候选来源 | 不复制为规范 ID 后宣称已登记 |
| 调用方明确的实体引用 | `entity_reference` | 不从 Server/Client 名称推断 Agent |
| Tool reference（工具引用） | `task_reference` | Tool 可见不表示 Capability 已验证 |
| Context reference（上下文引用） | `context_reference` | 只引用，不创建 Context 或 Runtime |
| Input reference（输入引用） | `input_reference` | 不复制或验证输入正文 |
| Output reference（输出引用） | `output_reference` | 可为 `null`；存在不表示成功或真实 |

若只有 Tool availability（工具可见性）或调用请求，没有稳定 invocation/source/context/input 引用，则不能形成 Execution 候选。即使形成候选，`status` 上限仍为 `UNKNOWN/CREATED`，不证明调用实际发生。

```text
TOOL_CALL_CANDIDATE_NE_EXECUTION_FACT=true
TOOL_RESULT_NE_VERIFICATION_PASS=true
TOOL_AVAILABILITY_NE_CAPABILITY=true
```

## 4. Resource to Evidence Reference Candidate（资源到证据引用候选）

目标：`EvidenceReferenceObject`（证据引用对象）候选表示。

必要条件：

- 稳定 Resource reference（资源引用）；
- 可归因 MCP Source 与 Server reference；
- 明确外部版本与状态；
- 既有 Execution Reference（执行引用）；
- Resource 与该执行关系的调用方声明；
- 完整性状态与限制，缺失时保持 `UNKNOWN/PENDING`。

没有 Execution Reference 时，Resource 只能成为外部 `RESOURCE` 引用，不能形成当前 Evidence Reference Object，因为其对象契约要求关联执行。

MCP Resource 内容、URI、摘要或可访问性均不自动证明：

- Evidence Truth（证据事实）；
- Source authenticity（来源真实性）；
- 完整性、相关性或范围充分性；
- Execution 已发生；
- E 等级或 Verification 已提升。

```text
RESOURCE_NE_EVIDENCE_TRUTH=true
RESOURCE_URI_NE_SOURCE_AUTHENTICITY=true
RESOURCE_ACCESS_NE_INTEGRITY=true
```

## 5. Context to Execution Context Reference（上下文到执行上下文引用）

目标：一个供 `ExecutionObject.context_reference` 使用的外部 Reference Object（引用对象）。

允许保留：

- Context ID（上下文标识）；
- MCP Source、Server 与协议版本；
- 调用方声明的 session/request/environment scope（会话/请求/环境范围）；
- 配置或输入摘要引用，如果来源已提供；
- 已知限制与隐私标签。

Adapter 不读取上下文正文、不补造摘要、不捕获凭据，也不写入 `registry/execution-contexts.yaml`。Context reference 不表示上下文已冻结、可复现或已验证。

## 6. Explicit Non-mappings（明确禁止的映射）

| MCP 表示 | 禁止自动映射 | 原因 |
|---|---|---|
| Server | DBOS Entity/Agent | Server 存在不是规范身份来源 |
| Tool list/description | Capability Object/Grant | 可见性和描述不是能力证据或复核 |
| Access decision/token | DBOS Permission | 外部访问控制不拥有 DBOS 权限语义 |
| Tool result | DBOS Fact/Verification `PASS` | 输出需要来源、Evidence 与独立验证 |
| Resource contents | Canonical Evidence | Adapter 无证据写入或修改权 |
| Prompt/context text | Agent identity or instruction authority | 文本不能签发身份或治理权力 |
| MCP error | DBOS lifecycle change | 外部错误不改变规范实体状态 |

## 7. Source and ID Preservation（来源与标识保留）

- MCP 原始 ID 必须保留在 `external:<authority-id>` Namespace（命名空间）中；
- Adapter 自身使用未来分配的 `extension:<adapter-id>` Namespace；
- 禁止生成自称 `dbio` 所有的 ID；
- Tool、Resource、Context、Server 和 invocation ID 不得互换；
- 相同字符串但不同类型或 Source 仍是不同引用；
- 映射关系需要单独来源和撤销路径，不自动建立 Alias（别名）。

## 8. Validation and Output State（验证与输出状态）

未来输出必须先成为候选，再由核心 Validator 检查：

```text
MAPPING_STATUS=PROPOSED
CANONICAL_REGISTRATION_EFFECT=NONE
CAPABILITY_EFFECT=NONE
PERMISSION_EFFECT=NONE
EVIDENCE_LEVEL_EFFECT=NONE
VERIFICATION_EFFECT=NONE
```

Validator `PASS` 只证明候选结构符合当前规则，不证明 MCP Source、Server、Tool 调用或 Resource 内容真实。

## 9. Current State（当前状态）

```text
MCP_TOOL_CALL_MAPPING_COUNT=0
MCP_RESOURCE_MAPPING_COUNT=0
MCP_CONTEXT_MAPPING_COUNT=0
MCP_ENTITY_MAPPING_COUNT=0
MCP_CAPABILITY_MAPPING_COUNT=0
MCP_PERMISSION_MAPPING_COUNT=0
```
