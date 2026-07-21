# DBOS MCP Positive Test Cases v0.1（DBOS MCP 正向测试案例 v0.1）

状态：`DEFINED_NOT_RUN`

案例数量：`3`

执行数量：`0`

## 1. Interpretation Boundary（解释边界）

本文件定义未来 MCP Adapter Test Harness（MCP 适配器测试环境）的规范正向预期，不提供实际 fixture（测试夹具）或通过结果。

由于当前 `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]` 且 `MCP_MAPPING_PROFILE_COUNT=0`，以下案例都必须保持 `NOT_RUN`。只有未来选择精确 MCP（Model Context Protocol，模型上下文协议）修订、批准 Mapping Profile（映射配置）并实现隔离 Harness 后，才可执行。

```text
POSITIVE_CASE_NE_PRODUCTION_EVIDENCE=true
EXPECTED_MAPPING_NE_OBSERVED_RESULT=true
CURRENT_PASS_COUNT=0
```

## 2. `MCP-POS-001` — Tool Call to Execution Candidate（工具调用到执行候选）

### Preconditions（前置条件）

- 精确协议修订和 Mapping Profile 已进入支持矩阵；
- Tool Call Fixture（工具调用夹具）包含全部公共字段；
- `tool_call_id/tool_name/arguments_reference/source_reference` 明确；
- `entity_reference/task_reference/context_reference/tool_version` 明确且唯一；
- 参数正文未被 Harness 或 Adapter 读取；
- 核心 Validator（验证器）桥接可用且不可绕过。

### Expected Mapping（预期映射）

```text
mapping_status=MAPPED
candidate_type=EXECUTION
authority_effect=NONE
permission_effect=NONE
execution_effect=NONE
```

候选必须保留 Tool Call ID、Tool 名、参数惰性引用、Context（上下文）、Source（来源）、Namespace（命名空间）、协议修订和映射配置版本。

### Validation Expectation（验证预期）

候选应交给 Execution Object Schema（执行对象模式）和治理约束验证器。预期 `PASS` 只表示结构符合冻结规则，不表示 Tool 被调用、Execution（执行）发生、任务成功或对象已登记。

### Current Status（当前状态）

```text
CASE_STATUS=NOT_RUN
BLOCKED_BY=NO_SUPPORTED_PROTOCOL_REVISION,NO_MAPPING_PROFILE,NO_ADAPTER_IMPLEMENTATION,NO_HARNESS_IMPLEMENTATION
```

## 3. `MCP-POS-002` — Resource to Evidence Reference Candidate（资源到证据引用候选）

### Preconditions（前置条件）

- 精确协议修订和 Mapping Profile 已进入支持矩阵；
- Resource Fixture（资源夹具）包含 `resource_id/source/version/origin`；
- 既有 `execution_reference` 明确且唯一；
- Resource（资源）正文没有被读取、复制、哈希或保存；
- Source、Origin（来源原点）、Version（版本）和限制完整保留。

### Expected Mapping（预期映射）

```text
mapping_status=MAPPED
candidate_type=EVIDENCE_REFERENCE
authority_effect=NONE
permission_effect=NONE
evidence_truth_effect=NONE
```

候选只能引用 Resource，不能把外部 `integrity_status`、成功响应或可访问性升级为 Evidence Truth（证据真相）。

### Validation Expectation（验证预期）

候选应交给 Evidence Reference Object Schema（证据引用对象模式）和治理约束验证器。预期 `PASS` 不验证正文真实性、相关性、充分性、完整性或来源身份。

### Current Status（当前状态）

```text
CASE_STATUS=NOT_RUN
BLOCKED_BY=NO_SUPPORTED_PROTOCOL_REVISION,NO_MAPPING_PROFILE,NO_ADAPTER_IMPLEMENTATION,NO_HARNESS_IMPLEMENTATION
```

## 4. `MCP-POS-003` — Context to Context Reference（上下文到上下文引用）

### Preconditions（前置条件）

- 精确协议修订和 Mapping Profile 已进入支持矩阵；
- Context Fixture（上下文夹具）包含 `context_id/namespace/version/source`；
- `context_kind/scope_reference/owner_reference/content_reference` 明确；
- Namespace 隔离有效；
- 引用解析结果唯一且不需要推断。

### Expected Mapping（预期映射）

```text
mapping_status=MAPPED
candidate_type=CONTEXT_REFERENCE
authority_effect=NONE
permission_effect=NONE
context_instance_effect=NONE
```

输出只形成 DBOS Context Reference（DBOS 上下文引用），不能创建 Execution Context（执行上下文）实例，也不宣称所有 MCP 修订具有统一顶层 Context 对象。

### Validation Expectation（验证预期）

结构验证检查 Namespace、Source、Version 和引用一致性。预期 `PASS` 不证明 Context 已冻结、可复现、完整或获授权。

### Current Status（当前状态）

```text
CASE_STATUS=NOT_RUN
BLOCKED_BY=NO_SUPPORTED_PROTOCOL_REVISION,NO_MAPPING_PROFILE,NO_ADAPTER_IMPLEMENTATION,NO_HARNESS_IMPLEMENTATION
```

## 5. Aggregate State（汇总状态）

```text
POSITIVE_TEST_CASE_DEFINITION_COUNT=3
POSITIVE_TEST_EXECUTION_COUNT=0
POSITIVE_TEST_PASS_COUNT=0
POSITIVE_TEST_FAIL_COUNT=0
PRODUCTION_COMPATIBILITY_CLAIM=false
```
