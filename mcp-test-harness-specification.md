# DBOS MCP Adapter Test Harness Specification v0.1（DBOS MCP 适配器测试环境规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION_V0.1`

实现状态：`PARTIAL_TOOL_CALL_REFERENCE_IMPLEMENTATION`

执行状态：`LOCAL_UNIT_TESTED`

规范日期：`2026-07-21`

## 1. Purpose（目的）

本规范定义未来 MCP Adapter Test Harness（MCP 适配器测试环境）如何在不连接真实 MCP（Model Context Protocol，模型上下文协议）Server（服务器）、Client（客户端）、Agent（智能体）或 Runtime（运行时）的情况下，使用 Synthetic Input（合成输入）检查 Adapter（适配器）的转换边界。

```text
Synthetic MCP Fixture（合成 MCP 夹具）
  -> fixture preflight（夹具前置检查）
  -> future Adapter under test（未来待测适配器）
  -> DBOS object candidate or reference（DBOS 对象候选或引用）
  -> DBOS Validator（DBOS 验证器）
  -> expectation assertion（预期断言）
  -> harness result（测试环境结果）
```

本规范现有一个只处理合成 Tool Call（工具调用）的最小参考实现。Resource（资源）、Context（上下文）、真实 MCP 协议、网络连接和生产 Harness 仍未实现。

## 2. Normative Principles（规范原则）

```text
SYNTHETIC_INPUT_NE_REAL_MCP_EVENT=true
TEST_FIXTURE_NE_EVIDENCE_TRUTH=true
TEST_PASS_NE_PRODUCTION_READY=true
TEST_HARNESS_AUTHORITY_EFFECT=NONE
FIXTURE_CANONICAL_EFFECT=NONE
```

- Synthetic Input 不证明真实 MCP Event（MCP 事件）发生；
- Test Fixture（测试夹具）只表达可复现输入，不是 Evidence Truth（证据真相）；
- Test Pass（测试通过）只表示观察结果符合已冻结预期，不表示生产兼容、安全认证或外部互操作；
- Test Harness 不能创建 Authority（权力）、Permission（权限）、Capability（能力）、Entity（实体）或执行效果；
- 未知协议修订、映射配置、引用或预期必须失败关闭，不能默认成功。

## 3. Scope（范围）

v0.1 定义三类合成输入：

1. `TOOL_CALL_FIXTURE`：Tool Call Fixture（工具调用夹具）；
2. `RESOURCE_FIXTURE`：Resource Fixture（资源夹具）；
3. `CONTEXT_FIXTURE`：Context Fixture（上下文夹具）。

测试范围包括：

- Input Fixture Model（输入夹具模型）；
- Expected Mapping（预期映射）；
- Validation Expectation（验证预期）；
- Failure Expectation（失败预期）；
- 正向、负向和安全案例定义；
- 未来测试结果的确定性语义。

不在范围内：网络连接、MCP 传输、Tool（工具）调用、Resource（资源）读取、模型推理、Agent 执行、对象登记、事件生成、Canonical Evidence（规范证据）写入、身份认证、Permission 决定和生产兼容声明。

## 4. Isolation Boundary（隔离边界）

未来实现必须默认离线、只读和无副作用：

- 不访问网络、真实 MCP Server 或外部 API（应用程序接口）；
- 不读取凭据、Secret（秘密）、Token（令牌）、个人信息或真实 Resource 正文；
- 不写入 `registry/`、`evidence/`、`evolution/` 或历史报告；
- 不调用 Tool，不启动 Agent 或 Runtime，不执行 fixture 中的指令；
- 不使用当前时间、随机数、可变 `latest` 或隐式环境作为预期来源；
- 所有 Namespace（命名空间）、版本、Source（来源）和限制都必须由 fixture 显式声明；
- 未明确列入未来隔离目录的文件系统路径一律不可访问。

fixture payload（夹具载荷）中的文本全部按不可信数据处理。任何类似指令、Prompt（提示）或可执行片段都只能被验证为数据，不得执行。

## 5. Input Fixture Model（输入夹具模型）

每个未来 fixture 必须包含：

| 字段 | 语义 | 约束 |
|---|---|---|
| `fixture_id` | 测试夹具唯一标识 | 只属于测试命名空间，不是 DBOS Entity ID |
| `fixture_type` | 三种夹具类型之一 | 不允许自定义类型自动进入测试 |
| `synthetic` | 合成标记 | 必须固定为 `true` |
| `fixture_version` | 夹具版本 | 与 MCP、Mapping Profile（映射配置）和对象版本分离 |
| `mcp_protocol_revision` | 精确协议修订 | 禁止 `latest/main/current` |
| `mapping_profile_version` | 精确映射配置版本 | 必须存在于未来获批支持矩阵 |
| `source_namespace` | 合成来源命名空间 | 不得使用 `dbio` 或冒充真实来源 |
| `source_reference` | 合成来源引用 | 不认证 Source |
| `input_payload` | 类型化测试输入 | 不能包含真实秘密或真实业务数据 |
| `expected_mapping` | 预期候选或拒绝结果 | 不是事实声明 |
| `expected_validation` | 预期 Validator 结果 | 不产生 Verification（事实验证） |
| `expected_failure` | 预期错误或治理拒绝 | 无失败时显式为 `null` |
| `limitations` | 未覆盖范围 | 至少一项，不能为空 |

具体字段见 `mcp-test-fixture-model.md`。本规范不创建任何实际 fixture 记录。

## 6. Expected Mapping（预期映射）

每项正向案例必须声明：

- 输入类型和精确版本；
- 预期 `candidate_type`；
- 允许进入 `candidate_payload` 的字段；
- 必须保留的 Source、Namespace、版本和 Origin（来源原点）；
- 必须保持为 `NONE/false/null` 的 Authority、Permission、执行和事实效果；
- 预期映射状态；
- 未验证事实与限制。

每项负向案例必须声明：

- 被违反的规则；
- 预期 `REJECTED/UNKNOWN/CONFLICT/VERSION_MISMATCH`；
- 适用时使用既有五种 Adapter 错误之一；
- 必须保持为零的副作用；
- 不得出现的部分候选、登记或证据写入。

Expected Mapping 是测试 Oracle（预期判定基准），不是 Canonical Object（规范对象）或验证结论。

## 7. Validation Expectation（验证预期）

未来 Harness（测试环境）必须把 Adapter 输出交给既有 DBOS Validator，并分别记录：

1. Adapter 映射状态；
2. Validator 的 `PASS/FAIL/UNKNOWN/CONFLICT/VERSION_MISMATCH`；
3. 预期与实际是否一致；
4. Validator 是否被调用且未被绕过；
5. 结构检查的限制。

`PASS` 只说明候选结构与治理约束符合当前 Schema（模式）和规则。它不证明 Tool Call 发生、Resource 真实、Context 完整、来源可信、协议生产兼容或对象已经登记。

## 8. Failure Expectation（失败预期）

未来测试结果允许：

```text
PASS
FAIL
BLOCKED
INVALID_FIXTURE
```

- `PASS`：实际映射、验证和副作用边界与冻结预期完全一致；
- `FAIL`：待测实现产生了不同结果或违反治理边界；
- `BLOCKED`：缺少精确协议修订、映射配置、Validator 桥接或其他前置条件；
- `INVALID_FIXTURE`：fixture 自身缺字段、冲突、泄露敏感信息或违反合成边界。

`HARNESS_ASSERTION_MISMATCH` 可作为未来 Harness 的断言诊断标签，但不是第六种 MCP Adapter 错误，也不能覆盖实际 Adapter 错误。

## 9. Test Lifecycle（测试生命周期）

未来单次测试只能按顺序进入：

```text
FIXTURE_LOADED
  -> PREFLIGHT_CHECKED
  -> MAPPING_ATTEMPTED
  -> VALIDATION_ATTEMPTED
  -> ASSERTION_RECORDED
  -> COMPLETE
```

- fixture 不合法时从 `PREFLIGHT_CHECKED` 进入 `INVALID_FIXTURE`；
- 前置版本或实现缺失时进入 `BLOCKED`；
- 映射或验证不符合预期时进入 `FAIL`；
- 禁止跳过 `PREFLIGHT_CHECKED`、映射尝试或 Validator；
- `COMPLETE` 不等于 `PASS`，最终结果必须单独记录；
- 新运行必须追加新记录，不能覆盖旧输入、输出或失败。

当前没有持久化生命周期实例或 Harness 测试运行记录。`tests/mcp_adapter/` 已执行本地单元测试，但测试进程输出没有登记为 Canonical Evidence（规范证据）或 Verification（事实验证）。

## 10. Test Inventory（测试清单）

v0.1 定义但未执行：

| 分类 | 定义数量 | 执行数量 | 当前结果 |
|---|---:|---:|---|
| Positive Test Case（正向测试案例） | 3 | 0 | `NOT_RUN` |
| Negative Test Case（负向测试案例） | 5 | 0 | `NOT_RUN` |
| Security Test Case（安全测试案例） | 5 | 0 | `NOT_RUN` |
| 合计 | 13 | 0 | `NOT_RUN` |

由于 `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]` 且真实 `MCP_MAPPING_PROFILE_COUNT=0`，面向真实协议的三项正向案例当前不能产生 `PASS`；它们是未来获批精确版本配置下的规范预期。

当前最小参考实现另有以下本地状态：

```text
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
LATEST_LOCAL_MCP_ADAPTER_UNIT_TEST_RESULT=PASS
PERSISTED_MCP_HARNESS_RUN_RECORD_COUNT=0
PERSISTED_MCP_HARNESS_RESULT_RECORD_COUNT=0
```

这里的 `PASS` 只表示 21 项本地单元测试符合代码断言。正向 Tool Call 映射本身返回 `mapping_status=MAPPED`，而 DBOS Validator 结果保持 `UNKNOWN`，因为候选 `status=UNKNOWN` 且没有外部执行事实。

## 11. Reproducibility Requirements（可复现要求）

未来实现必须冻结：

- fixture 内容和 digest（摘要）；
- 精确 MCP 修订、Mapping Profile、DBOS Schema 和 Validator 版本；
- 确定性 ID、时钟和执行顺序；
- 输入、输出、错误、日志脱敏策略和限制；
- 不可变的预期结果；
- Harness 版本和执行环境。

版本或预期改变必须创建新 fixture 版本和追加式变化记录，不能静默修改旧测试。

## 12. Implementation Prerequisites（实现前置条件）

开始 Harness 或 Adapter 实现前必须满足：

1. 选择并批准精确 MCP 协议修订；
2. 创建经复核的 Mapping Profile 和版本矩阵；
3. 将本规范转换为机器可读 fixture Schema；
4. 定义 Adapter-under-test（待测适配器）的纯转换接口；
5. 建立不可写 Registry、Evidence 和历史目录的隔离 Runner（执行器）；
6. 冻结确定性 ID、时钟、摘要和日志脱敏规则；
7. 建立不可绕过的 Validator 桥接与副作用检测；
8. 审查 13 项 fixture 定义并创建真实合成 fixture；
9. 获得新的明确实现授权。

当前这些条件没有被本规范宣称完成。

### 12.1 Controlled Synthetic Implementation Authorization（受控合成实现授权）

`2026-07-21` 的明确任务授权仅允许实现 Tool Call 的 synthetic-only reference slice（仅合成参考切片）。为避免越过上述真实接入闸门：

- 代码只接受 `DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1`；
- 该值是 DBOS 测试标记，不是任何真实 MCP 协议修订；
- 固定测试配置为 `dbos.synthetic.mcp-tool-call/v0.1`；
- 不访问网络、文件系统 Registry、Evidence 或 Runtime；
- 不实现 Resource/Context Adapter、MCP Server/Client 或传输；
- 真实 MCP 支持矩阵继续为空。

真实 MCP Adapter 实现仍必须满足本节九项条件并获得新的明确授权。

## 13. Specification Non-effects（规范无效果）

```text
MCP_TEST_HARNESS_SPECIFICATION=FROZEN_V0.1
MCP_TEST_HARNESS_IMPLEMENTATION=PARTIAL_TOOL_CALL_ONLY
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
MCP_RESOURCE_ADAPTER_IMPLEMENTED=false
MCP_CONTEXT_ADAPTER_IMPLEMENTED=false
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
MCP_TEST_CASE_DEFINITION_COUNT=13
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
LATEST_LOCAL_MCP_ADAPTER_UNIT_TEST_RESULT=PASS
PERSISTED_MCP_HARNESS_RUN_RECORD_COUNT=0
PERSISTED_MCP_HARNESS_RESULT_RECORD_COUNT=0
MCP_REAL_CONNECTION=false
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
MCP_RUNTIME_CONNECTED=false
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EXECUTION_TRIGGERED=false
EVENT_CREATED=false
CANONICAL_EVIDENCE_MODIFIED=false
VERIFICATION_RESULT_CREATED=false
PRODUCTION_READY=false
```

## 14. Related Documents（关联文档）

- `mcp-test-fixture-model.md`
- `mcp-positive-test-cases.md`
- `mcp-negative-test-cases.md`
- `mcp-security-test-model.md`
- `mcp-adapter-specification.md`
- `mcp-error-handling-specification.md`
- `mcp-version-compatibility-policy.md`
- `adapters/mcp/`
- `tests/mcp_adapter/`
- `ADR-027-mcp-test-harness.md`
