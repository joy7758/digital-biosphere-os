# DBOS MCP Negative Test Cases v0.1（DBOS MCP 负向测试案例 v0.1）

状态：`DEFINED_NOT_RUN`

案例数量：`5`

执行数量：`0`

## 1. Purpose and Error Boundary（目的与错误边界）

本文件定义未来 MCP Adapter Test Harness（MCP 适配器测试环境）必须拒绝的治理越界。案例中的 Governance Assertion Label（治理断言标签）只供 Harness 判断，不新增 MCP Adapter（MCP 适配器）错误代码。

既有 Adapter 错误仍只有：

```text
INVALID_TOOL_REFERENCE
UNKNOWN_RESOURCE
VERSION_MISMATCH
UNRESOLVED_CONTEXT
CONFLICTING_REFERENCE
```

治理断言标签可以说明“为什么必须拒绝”，但不能覆盖 Adapter 实际错误或伪造 Validation Result（验证结果）。

## 2. `MCP-NEG-001` — Tool Directly Becomes Capability（工具直接成为能力）

- 违规输入：fixture（测试夹具）要求把 Tool Availability（工具可用性）或 Tool Call（工具调用）直接映射为 Capability（能力）；
- 预期映射：`mapping_status=REJECTED`、`candidate_type=null`；
- 治理断言：`PROHIBITED_CAPABILITY_DERIVATION`；
- 适用 Adapter 错误：若 Tool 引用本身非法则使用 `INVALID_TOOL_REFERENCE`，否则不虚构第六种 Adapter 错误；
- 必须保持：`CAPABILITY_GRANTED=false`、`PERMISSION_GRANTED=false`、`ENTITY_CREATED=false`。

## 3. `MCP-NEG-002` — Resource Directly Becomes Evidence Truth（资源直接成为证据真相）

- 违规输入：fixture 要求把 Resource（资源）、可访问 URI（统一资源标识符）或成功响应直接登记为 Evidence Truth（证据真相）；
- 预期映射：`mapping_status=REJECTED`，不得产生 Evidence Reference Candidate（证据引用候选）的部分规范写入；
- 治理断言：`CANONICAL_EVIDENCE_MUTATION_ATTEMPT`；
- 适用 Adapter 错误：来源字段缺失时使用 `UNKNOWN_RESOURCE`；
- 必须保持：`CANONICAL_EVIDENCE_MODIFIED=false`、`VERIFICATION_CREATED=false`、`TRUTH_CLAIM_CREATED=false`。

## 4. `MCP-NEG-003` — External Permission Becomes DBOS Permission（外部权限成为 DBOS 权限）

- 违规输入：外部 Server（服务器）、Client（客户端）、Tool 或 MCP 访问决定被要求转换为 DBOS Permission（权限）；
- 预期映射：`mapping_status=REJECTED`、`permission_effect=NONE`；
- 治理断言：`PROHIBITED_PERMISSION_DERIVATION`；
- 适用 Adapter 错误：若引用冲突则使用 `CONFLICTING_REFERENCE`；否则由治理验证器拒绝，不添加 Adapter 错误；
- 必须保持：`PERMISSION_GRANTED=false`、`AUTHORITY_EFFECT=NONE`、`EXECUTION_TRIGGERED=false`。

## 5. `MCP-NEG-004` — Unknown Version Automatically Accepted（未知版本自动兼容）

- 违规输入：`mcp_protocol_revision` 或 `mapping_profile_version` 未知、缺失、使用 `latest` 或不在支持矩阵，却要求继续映射；
- 预期映射：`mapping_status=VERSION_MISMATCH`、`candidate_type=null`；
- Adapter 错误：`VERSION_MISMATCH`；
- 治理断言：`MUTABLE_OR_UNSUPPORTED_VERSION_REJECTED`；
- 必须保持：`AUTOMATIC_DOWNGRADE=false`、`AUTOMATIC_COMPATIBILITY=false`、`PARTIAL_CANDIDATE=false`。

## 6. `MCP-NEG-005` — Validator Bypass（绕过验证器）

- 违规输入：待测 Adapter 直接返回 Canonical Object（规范对象）、登记状态或成功结果，不调用 DBOS Validator（DBOS 验证器）；
- 预期 Harness 结果：`FAIL`；
- 治理断言：`VALIDATOR_BYPASS_ATTEMPT`；
- Adapter 错误：不添加新代码；Harness 必须保留实际输出并报告断言不匹配；
- 必须保持：`CANONICAL_REGISTRATION=false`、`ENTITY_CREATED=false`、`EXECUTION_TRIGGERED=false`、`PERMISSION_GRANTED=false`。

## 7. Required Rejection Invariants（必须拒绝的不变量）

每项负向测试必须同时证明：

```text
NO_PARTIAL_REGISTRY_WRITE=true
NO_CANONICAL_EVIDENCE_WRITE=true
NO_PERMISSION_EFFECT=true
NO_EXECUTION_EFFECT=true
NO_AUTOMATIC_REPAIR=true
NO_DEFAULT_SUCCESS=true
```

未来 Harness 若只能观察返回值而不能检测副作用，不得把这些案例标记 `PASS`，必须返回 `BLOCKED`。

## 8. Aggregate State（汇总状态）

```text
NEGATIVE_TEST_CASE_DEFINITION_COUNT=5
NEGATIVE_TEST_EXECUTION_COUNT=0
NEGATIVE_TEST_PASS_COUNT=0
NEGATIVE_TEST_FAIL_COUNT=0
```
