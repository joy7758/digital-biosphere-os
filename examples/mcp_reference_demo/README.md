# DBOS MCP Reference Demo v0.1（DBOS MCP 参考演示 v0.1）

这个教学样板展示一个外部开发者如何把 Synthetic MCP Tool Call（合成 MCP 工具调用）转换为 DBOS Execution Object Candidate（DBOS 执行对象候选），再交给现有 Validator（验证器）。

## What This Demonstrates（演示内容）

```text
synthetic_agent.py
  -> synthetic_mcp_event.py
  -> adapters/mcp/tool_call_adapter.py
  -> Execution Object Candidate
  -> DBOS Validator
  -> Validation Result
  -> deterministic JSON demo output
```

`synthetic_agent.py` 只是教学场景声明函数。它没有 Agent（智能体）类、身份、生命周期、推理、自治或 Runtime（运行时）。

## Run Locally（本地运行）

在仓库根目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 examples/mcp_reference_demo/run_demo.py
```

脚本只向标准输出打印 JSON（JavaScript Object Notation，JavaScript 对象表示法），不生成或修改文件。

## Expected Story（预期故事）

- 正向链路：`mapping_status=MAPPED`；
- 候选类型：`object_type=EXECUTION`；
- 候选状态：`status=UNKNOWN`；
- Validator 已被调用：`validator_invoked=true`；
- 验证结果：`result=UNKNOWN`；
- Tool → Capability：`REJECTED/FAIL`；
- Tool Permission → DBOS Permission：`REJECTED/FAIL`；
- 未知协议版本：`VERSION_MISMATCH`。

`UNKNOWN` 是预期安全状态：演示没有执行 Tool（工具），也没有外部执行事实。

## Files（文件）

- `synthetic_agent.py`：声明无 Agent 身份的合成 Tool Call 场景；
- `synthetic_mcp_event.py`：补齐严格合成版本配置；
- `run_demo.py`：运行正向与负向链路并打印结果；
- `demo_report.md`：人类可读的静态演示报告；
- `tests/mcp_reference_demo/`：15 项成功、拒绝和零副作用测试。

## Boundaries（边界）

```text
DEMO_NE_PRODUCTION=true
SYNTHETIC_NE_REAL=true
VALIDATION_NE_TRUTH=true
REAL_AGENT_CREATED=false
RUNTIME_CREATED=false
MCP_SERVER_CREATED=false
REAL_MCP_CONNECTED=false
TOOL_INVOKED=false
PERMISSION_CREATED=false
EXECUTION_FACT_CREATED=false
CANONICAL_EVIDENCE_CREATED=false
```

该演示不证明真实 MCP 兼容、外部互操作、客户验证、安全认证或生产就绪。
