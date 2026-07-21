# DBOS MCP Reference Demo Report v0.1（DBOS MCP 参考演示报告 v0.1）

报告状态：`LOCAL_SYNTHETIC_DEMO_REPORT`

报告日期：`2026-07-21`

## 1. Objective（目标）

展示一个 Synthetic Agent Scenario（合成智能体场景）如何声明 MCP 风格 Tool Call（工具调用）输入，经最小 Adapter（适配器）转换为 DBOS Execution Object Candidate（执行对象候选），并由现有 Validator（验证器）返回 Validation Result（验证结果）。

“Synthetic Agent”只是开发者故事中的输入生产方名称，不是 Agent 身份、实例或 Runtime（运行时）。

## 2. Input（输入）

```text
tool_call_id=demo-synthetic-tool-call-001
tool_name=synthetic.demo.read_only_lookup
protocol_revision=DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1
mapping_profile_version=dbos.synthetic.mcp-tool-call/v0.1
source_namespace=extension:dbos-mcp-synthetic
```

输入中的 arguments、context、source 和 entity 都是 `fixture:` 或 `extension:` 合成引用，不对应真实系统或数据。

## 3. Mapping Result（映射结果）

```text
mapping_status=MAPPED
candidate_type=EXECUTION
candidate_status=UNKNOWN
output_reference=null
validator_invoked=true
```

候选 ID 处于 `extension:` 范围，不是 `dbio` Canonical ID（规范 ID）。候选没有触发 Tool 执行或对象登记。

## 4. Validation Result（验证结果）

```text
result=UNKNOWN
validator_version=v0.1
```

`UNKNOWN` 来自候选安全状态 `status=UNKNOWN`。这表示结构已进入 Validator，但没有外部信息支持执行事实或状态升级。

## 5. Negative Cases（负向案例）

| 案例 | 预期 | 本地观察 |
|---|---|---|
| Tool → Capability | 拒绝能力推断 | `REJECTED/FAIL` |
| Tool Permission → DBOS Permission | 拒绝权限升级 | `REJECTED/FAIL` |
| Unknown Version（未知版本） | 禁止自动兼容 | `VERSION_MISMATCH` |

所有负向案例的 `candidate_created=false`。

## 6. Limitations（限制）

- 只使用 DBOS 自有合成测试配置；
- 没有真实 MCP Server（MCP 服务器）、Client（客户端）或传输；
- 没有真实 Agent、Runtime、Tool 调用或数据访问；
- 没有 Permission、Capability Grant（能力授予）或 Execution Fact（执行事实）；
- 没有 Canonical Evidence（规范证据）或事实验证；
- 本地演示通过不等于真实互操作、客户验证或 Production Ready（生产就绪）。

## 7. Non-effects（无效果）

```text
AGENT_CREATED=false
RUNTIME_CREATED=false
MCP_SERVER_CREATED=false
REAL_MCP_CONNECTED=false
TOOL_INVOKED=false
PERMISSION_CREATED=false
CAPABILITY_GRANTED=false
EXECUTION_FACT_CREATED=false
CANONICAL_EVIDENCE_CREATED=false
PRODUCTION_READY=false
```

本报告是对可运行本地教学流程的静态说明，不是持久化 Demo Run Evidence（演示运行证据）或 Verification Record（验证记录）。
