# ADR-027: DBOS MCP Adapter Test Harness Specification v0.1（DBOS MCP 适配器测试环境规范 v0.1）

状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-21`

编号说明：用户任务建议 `ADR-026-mcp-test-harness.md`，但 `ADR-026-autonomy-policy.md` 已存在。为保持 ADR（Architecture Decision Record，架构决策记录）编号唯一并保留历史，本决策使用下一个唯一编号 `ADR-027`。

## 1. Context（背景）

DBOS 已冻结 MCP Adapter Proposal（MCP 适配器提案）、MCP Adapter Specification（MCP 适配器规范）、Object Contract（对象契约）、Schema（模式）、Validator（验证器）和最小 Object SDK（对象软件开发工具包）边界。

直接连接真实 MCP（Model Context Protocol，模型上下文协议）Server（服务器）会同时引入版本、来源、凭据、Tool（工具）、Resource（资源）、Permission（权限）和运行副作用。当前 `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]`、`MCP_MAPPING_PROFILE_COUNT=0`，也没有 Adapter 实现或隔离测试执行器。

在这种状态下直接实现或接入真实外部系统，会把未经验证的字段、版本和权力假设固化为代码。

## 2. Decision（决策）

接受 MCP Adapter Test Harness Specification v0.1（MCP 适配器测试环境规范 v0.1），先冻结未来隔离测试环境的：

1. Synthetic Fixture（合成夹具）公共封装；
2. Tool Call、Resource 和 Context（上下文）三类 fixture 模型；
3. Expected Mapping（预期映射）、Validation Expectation（验证预期）和 Failure Expectation（失败预期）；
4. 3 项正向、5 项负向和 5 项安全案例；
5. `PASS/FAIL/BLOCKED/INVALID_FIXTURE` 测试结果语义；
6. 不执行内容、不访问网络、不写入治理目录和不产生 Authority（权力）的隔离边界；
7. 精确协议修订、Mapping Profile（映射配置）、机器 Schema、隔离 Runner（执行器）和新授权等实现闸门。

本决策不创建实际 fixture、Harness 代码、Adapter 代码、MCP 连接或测试结果。

## 3. Why Harness Before Adapter（为什么先测试环境再实现适配器）

- 正向案例冻结允许的候选类型和必须保留的来源字段；
- 负向案例冻结 Tool 不得成为 Capability（能力）、Resource 不得成为 Evidence Truth（证据真相）、外部 Permission 不得成为 DBOS Permission 等拒绝条件；
- 安全案例在实现前明确工具注入、引用冲突、版本冲突、敏感数据暴露和重放风险；
- `BLOCKED` 允许当前版本诚实表达缺少协议修订和 Mapping Profile，而不是伪造 `PASS`；
- 合成输入让未来实现先在隔离边界内暴露字段和副作用问题；
- 测试结果与生产就绪、真实互操作和 Evidence（证据）严格分离。

## 4. Pre-development Agent Consultation（开发前智能体咨询）

潜在客户问题：“现在是否应采用 DBOS MCP Test Harness？”

```text
RECOMMEND_MCP_TEST_HARNESS_SPECIFICATION=true
RECOMMEND_MCP_TEST_HARNESS_IMPLEMENTATION=false
RECOMMEND_MCP_ADAPTER_IMPLEMENTATION=false
RECOMMEND_PRODUCTION_USE=false
```

可以向需要测试边界、fixture 合同、失败语义和实现闸门的基础设施开发者推荐本规范。

当前不能向需要可运行 Harness、真实 MCP 连接、协议兼容证明、生产安全或客户互操作的使用者推荐实现，原因是：

1. 没有受支持的精确 MCP 协议修订；
2. 没有获批 Mapping Profile 或版本矩阵；
3. 没有机器可读 fixture Schema 和真实合成 fixture；
4. 没有 Adapter-under-test（待测适配器）接口或代码；
5. 没有隔离 Runner、Validator 桥接和副作用检测；
6. 13 项案例都没有执行结果；
7. 没有真实外部开发者复核或实现授权。

## 5. Alternatives Considered（备选方案）

### A. 直接实现 MCP Adapter

拒绝。它会在无协议支持矩阵、无 Mapping Profile 和无负向证明的情况下固化假设。

### B. 先连接真实 MCP Server

拒绝。真实数据、权限、版本和网络副作用会混淆 Adapter 转换问题与外部系统问题。

### C. 只依赖现有 Object Validator 测试

拒绝。对象结构测试不覆盖 MCP 来源字段、版本配对、Adapter 错误、映射候选和安全边界。

### D. 把合成 fixture 当作 Evidence

拒绝。fixture 只表达测试输入和预期，不能证明真实事件、来源或生产行为。

### E. 先冻结 Test Harness 规范，再单独授权实现

接受。它使未来代码具有明确输入、拒绝条件、失败语义和停止规则，同时保留 DBOS 基础设施边界。

## 6. Consequences（影响）

正向影响：

- 开发者和编码智能体获得统一、可检索的测试词汇与案例 ID；
- 未知版本和缺少配置可以明确返回 `BLOCKED`；
- 治理越界和 Adapter 错误保持分层，不随意增加错误代码；
- 实现前即可审查敏感数据、重放、注入和副作用检测缺口；
- 未来测试记录可追加保留，不覆盖旧失败。

限制与成本：

- 当前没有任何可运行 Harness、fixture 文件或结果；
- 文档定义的 13 项案例不构成覆盖证据；
- 每个受支持协议修订都需要具体 Mapping Profile、fixture 和版本矩阵；
- 合成测试通过也不能替代真实外部兼容、安全审计或生产观察。

## 7. Non-decisions（非决策）

本 ADR 不决定：

- 使用哪个 MCP 协议修订、Server、Client、SDK 或传输；
- fixture 文件格式、编程语言、测试框架或包结构；
- Adapter 接口、代码、发布、Repository（仓库）或 License（许可证）；
- Agent（智能体）、Runtime（运行时）、Tool 执行或模型推理；
- Permission、Capability、Entity、Event（事件）、Evidence 或 Verification（事实验证）的创建；
- 生产部署、安全认证或外部互操作结论。

## 8. Current State（当前状态）

```text
MCP_TEST_HARNESS_SPECIFICATION=FROZEN_V0.1
MCP_TEST_HARNESS_IMPLEMENTATION=false
MCP_SYNTHETIC_FIXTURE_INSTANCE_COUNT=0
MCP_TEST_CASE_DEFINITION_COUNT=13
MCP_TEST_EXECUTION_COUNT=0
MCP_TEST_RESULT_COUNT=0
MCP_ADAPTER_IMPLEMENTATION=false
MCP_REAL_CONNECTION=false
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
MCP_MAPPING_PROFILE_COUNT=0
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EXECUTION_TRIGGERED=false
CANONICAL_EVIDENCE_MODIFIED=false
PRODUCTION_READY=false
```

## 9. Related Decisions（关联决策）

- `ADR-021-object-schema-governance.md`
- `ADR-022-validation-result-contract.md`
- `ADR-023-adapter-boundary.md`
- `ADR-024-mcp-adapter-proposal.md`
- `ADR-025-mcp-adapter-specification.md`
- `mcp-test-harness-specification.md`
- `mcp-test-fixture-model.md`
- `mcp-positive-test-cases.md`
- `mcp-negative-test-cases.md`
- `mcp-security-test-model.md`

## 10. Subsequent Bounded Implementation Addendum（后续有界实现附录）

`2026-07-21` 的后续明确任务授权了比本 ADR 原始实现闸门更窄的 synthetic-only Tool Call reference slice（仅合成工具调用参考切片）。该附录追加后续状态，不改写本 ADR 作出时“尚未授权实现”的历史事实。

```text
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_TEST_HARNESS_IMPLEMENTATION=PARTIAL_TOOL_CALL_ONLY
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
LATEST_LOCAL_MCP_ADAPTER_UNIT_TEST_RESULT=PASS
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
MCP_REAL_CONNECTION=false
PRODUCTION_READY=false
```

实现位置为 `adapters/mcp/`，测试位置为 `tests/mcp_adapter/`。该实现只接受 DBOS 自有合成测试标记，不支持真实 MCP 修订，不调用 Tool，不创建 Entity、Agent、Runtime、Permission、Capability Grant、Execution Result 或 Canonical Evidence。
