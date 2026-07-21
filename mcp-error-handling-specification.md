# DBOS MCP Adapter Error Handling Specification v0.1（DBOS MCP 适配器错误处理规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

实现状态：`MINIMAL_SYNTHETIC_TOOL_CALL_REFERENCE_ONLY`

## 1. Purpose（目的）

本规范冻结未来 MCP Adapter（MCP 适配器）在 Tool Call（工具调用）、Resource（资源）和 Context Reference（上下文引用）无法安全转换时的错误语言。

错误是 Adapter Mapping Error（适配器映射错误），不是 MCP 传输错误、JSON-RPC（JSON 远程过程调用）错误、DBOS Permission（权限）决定、Verification（验证）结果或历史修复命令。

## 2. Error Object（错误对象）

未来每个错误必须包含以下概念字段：

| 字段 | 语义 | 约束 |
|---|---|---|
| `error_code` | 本规范定义的五种错误之一 | 不能使用自由文本替代 |
| `message` | 面向开发者的简洁说明 | 不得成为唯一机器语义 |
| `field_reference` | 失败字段或引用路径 | 不能泄露 Resource 正文或凭据 |
| `source_reference` | 允许披露的来源引用 | 不能因此认证 Source |
| `mcp_protocol_revision` | 输入声明的精确 MCP 修订 | 缺失时为 `null`，禁止补造 |
| `mapping_profile_version` | 实际尝试或需要的映射配置版本 | 未选择时为 `null` |
| `result` | 对应 DBOS Validation Result（验证结果）状态 | 只允许下表映射 |
| `retryable` | 外部输入或支持矩阵变化后是否可重试 | 不保证重试成功 |
| `resolution_hint` | 人工修复提示 | 不是自动修复指令 |
| `limitations` | 未检查范围和敏感边界 | 至少一项 |
| `authority_effect` | 权力效果 | 固定为 `NONE` |
| `permission_effect` | 权限效果 | 固定为 `NONE` |

该对象是规范概念，不是已发布 Schema（模式）、SDK class（软件开发工具包类）或 API response（应用程序接口响应）。

## 3. Error Codes（错误代码）

### 3.1 `INVALID_TOOL_REFERENCE`

Tool Call ID、Tool reference（工具引用）、arguments reference（参数引用）或必需类型不符合声明 Mapping Profile（映射配置）。

- 顶层 `result=FAIL`；
- `retryable=false`，除非调用方提交新的合法输入；
- 不调用 Tool、不修复参数、不猜测 Tool 名；
- 不把错误转成默认 Execution Object Candidate（执行对象候选）。

### 3.2 `UNKNOWN_RESOURCE`

Resource 引用、Source（来源）、Origin（来源原点）、Version（版本）或既有 Execution Reference（执行引用）缺失，无法形成 Evidence Reference Candidate（证据引用候选）。

- 顶层 `result=UNKNOWN`；
- 只保留允许披露的外部 Resource 引用；
- 不扫描网络、文件系统或 Registry（登记表）寻找替代资源；
- 不生成 Evidence、摘要或 Execution。

### 3.3 `VERSION_MISMATCH`

MCP 协议修订、Server/Client 实现、Adapter、Mapping Profile、DBOS Object Contract（对象契约）、Schema 或 Validator（验证器）之间没有已声明的兼容关系。

- 顶层 `result=VERSION_MISMATCH`；
- 返回 requested/observed（请求/观察）版本轴，前提是不泄露受限信息；
- 不自动升级、降级、选择 `latest` 或采用草案；
- 旧输入、错误和限制必须保留。

### 3.4 `UNRESOLVED_CONTEXT`

Context、Entity（实体）、Input（输入）或其他形成 Execution 候选所需的类型化引用没有得到唯一解析。

- 顶层 `result=UNKNOWN`；
- 附带 Resolver（解析器）的 `UNKNOWN/AMBIGUOUS/INVALID` 状态；
- 不创建 Context、Entity、Agent（智能体）或 Runtime（运行时）；
- 不使用目录名、Server 名、会话 ID 或 Tool 名进行推断。

### 3.5 `CONFLICTING_REFERENCE`

同一外部 ID 在多个 Source、Namespace（命名空间）、类型、版本或 Scope（范围）中对应互不兼容的声明。

- 顶层 `result=CONFLICT`；
- 返回允许披露的冲突维度和引用；
- 不选择最新、最近、最相似或最先出现的候选；
- 不合并身份、Execution、Evidence、Context 或版本。

## 4. Deterministic Evaluation Order（确定性判定顺序）

当一次输入同时触发多个问题时，主错误按以下顺序选择，并在 `limitations` 中保留其他问题：

```text
INVALID_TOOL_REFERENCE
  > VERSION_MISMATCH
  > CONFLICTING_REFERENCE
  > UNRESOLVED_CONTEXT
  > UNKNOWN_RESOURCE
```

安全披露边界优先于诊断细节。如果返回 Source 或冲突目标会泄露受限信息，错误只保留不敏感的字段路径和缺失条件；它仍不能创建 DBOS Permission。

## 5. Relationship to MCP and DBOS Errors（与 MCP 和 DBOS 错误的关系）

- 外部 MCP 或 JSON-RPC 错误必须作为 Source-owned error reference（来源拥有的错误引用）保留；
- Adapter 不把外部 `isError=false`、成功响应或无错误响应转换为 DBOS `PASS`；
- Adapter 错误映射到 Validation Result Contract（验证结果契约）的顶层状态，但不是 Verification Object（验证对象）；
- API Error Model（应用程序接口错误模型）的 `UNAUTHORIZED_REFERENCE` 属于未来接口披露边界，不属于本规范五个映射错误；
- 同一失败可同时引用外部协议错误和 Adapter 错误，但二者不能互相覆盖。

## 6. Failure Handling Rules（失败处理规则）

- 所有错误失败关闭；
- 不进行自动修复、自动重试、Tool fallback（工具回退）或版本 fallback（版本回退）；
- 不产生部分 Canonical Object（规范对象）或部分 Registry 写入；
- 不删除、覆盖或“修正”旧错误和旧映射；
- 新输入或新版本必须产生新的映射尝试引用；
- `resolution_hint` 只能告诉调用方补充字段、缩小范围或选择已支持版本；
- 错误日志不得包含参数正文、Resource 内容、Secret、Token 或 Credential（秘密、令牌或凭据）。

## 7. Prohibited Error Effects（禁止的错误效果）

```text
ERROR_CAN_CREATE_ENTITY=false
ERROR_CAN_CREATE_AGENT=false
ERROR_CAN_CREATE_RUNTIME=false
ERROR_CAN_GRANT_CAPABILITY=false
ERROR_CAN_GRANT_PERMISSION=false
ERROR_CAN_MODIFY_EVIDENCE=false
ERROR_CAN_OVERRIDE_VALIDATOR=false
ERROR_CAN_TRIGGER_EVOLUTION=false
AUTOMATIC_REPAIR=false
AUTOMATIC_RETRY=false
```

## 8. Test Harness Error Assertions（测试环境错误断言）

未来 MCP Adapter Test Harness（MCP 适配器测试环境）必须把“Adapter 实际错误”和“测试预期不匹配”分开记录：

- 正向或负向 fixture（测试夹具）的 `expected_failure` 只能引用本规范五个 Adapter 错误，或显式为 `null`；
- `HARNESS_ASSERTION_MISMATCH` 只表示实际结果与预期不一致，不是第六个 Adapter 错误；
- `INVALID_FIXTURE` 表示 fixture 自身无效，不表示 Adapter 已运行；
- `BLOCKED` 表示协议修订、Mapping Profile（映射配置）、实现或 Validator（验证器）桥接缺失，不得降级为 `PASS`；
- Governance Assertion Label（治理断言标签）可以描述 Capability、Permission、Evidence 或 Validator 越界，但不能覆盖 Adapter 错误；
- Harness 不得通过修改输入、错误或预期来自动修复失败。

测试入口：

- `mcp-test-harness-specification.md`
- `mcp-negative-test-cases.md`
- `mcp-security-test-model.md`

## 9. Current Test State（当前测试状态）

```text
MCP_ADAPTER_ERROR_CODE_COUNT=5
MCP_TEST_HARNESS_IMPLEMENTATION=PARTIAL_TOOL_CALL_ONLY
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
PERSISTED_MCP_HARNESS_RUN_RECORD_COUNT=0
PERSISTED_MCP_HARNESS_RESULT_RECORD_COUNT=0
HARNESS_ASSERTION_MISMATCH_IS_ADAPTER_ERROR=false
AUTOMATIC_FIXTURE_REPAIR=false
```

五种错误已在 `adapters/mcp/errors.py` 中作为最小合成 Tool Call 参考实现的稳定枚举。该实现不构成真实 MCP 协议错误兼容、传输错误处理或生产运行证据。
