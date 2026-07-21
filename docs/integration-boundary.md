# DBOS Integration Boundary v0.1（DBOS 集成边界 v0.1）

状态：`COMMON_BOUNDARY_DEFINED_IMPLEMENTATIONS_ABSENT`（公共边界已定义、实现不存在）

当前官方 Adapter（适配器）数量：`0`

DBOS 不替代外部 Agent Framework（智能体框架）或 Runtime（运行时）。未来 Adapter 只把外部系统已经产生的身份、上下文、输出和证据投影为 DBOS 对象与引用。

## Responsibility Split（责任分工）

| 层 | 负责 | 不负责 |
|---|---|---|
| 外部框架/应用 | 推理、规划、工具调用、任务调度、实际执行 | DBOS 规范身份或验证语义 |
| 未来 Adapter | 显式字段映射、版本转换、限制声明、失败关闭 | 修改外部行为、授予权限、制造证据 |
| DBOS | 对象契约、模式验证、引用与结果边界 | 模型推理、Runtime、Permission、自动决策 |

## Common Adapter Model（公共适配器模型）

所有未来框架 Adapter 必须共同遵守：

- [`../adapter-boundary-specification.md`](../adapter-boundary-specification.md)：输入—转换—输出、允许行为、禁止行为与失败语义；
- [`../adapter-object-mapping-model.md`](../adapter-object-mapping-model.md)：Entity、Execution、Evidence、Verification 候选映射和 Capability 默认排除；
- [`../adapter-security-boundary-rules.md`](../adapter-security-boundary-rules.md)：Namespace 隔离、Reference、Version、Validator、Evidence 与供应链边界；
- [`../ADR-023-adapter-boundary.md`](../ADR-023-adapter-boundary.md)：Adapter 独立于 DBOS 核心的架构决策。

公共规范存在不表示某个具体 Adapter 已实现、兼容或获准进入 DBOS 核心。

## LangChain Boundary（LangChain 边界）

未来 LangChain Adapter 可以把外部 run ID（运行标识）、配置、输入/输出引用和 Callback Evidence（回调证据）映射为 Execution Object（执行对象）与 Evidence Reference Object（证据引用对象）。

它不得替代 LangChain、改变 Chain/Agent 行为、执行工具或把 callback 存在解释为验证通过。

## CrewAI Boundary（CrewAI 边界）

未来 CrewAI Adapter 可以把 Crew、Task（任务）、外部执行标识与结果引用投影为受限制的 DBOS 对象。

它不得接管 Crew 调度、角色设计、任务执行，也不得把 Role（角色）自动登记为 DBOS Agent 身份。

## MCP Boundary（模型上下文协议边界）

未来 MCP Adapter 可以映射 Server（服务器）、Tool（工具）、Resource（资源）和调用引用。

MCP Tool 可调用不表示 Capability（能力）已验证或 Permission（权限）已授予；MCP Server 存在也不表示 Agent 身份已经建立。

专属提案入口：

- [`mcp-adapter-proposal.md`](../mcp-adapter-proposal.md)：定位、允许范围、禁止效果和实现闸门；
- [`mcp-object-mapping-model.md`](../mcp-object-mapping-model.md)：Tool Call、Resource 与 Context 的候选映射；
- [`mcp-security-boundary.md`](../mcp-security-boundary.md)：命名空间、引用、来源、失败和版本边界；
- [`mcp-adapter-risk-assessment.md`](../mcp-adapter-risk-assessment.md)：接入风险及停止条件；
- [`ADR-024-mcp-adapter-proposal.md`](../ADR-024-mcp-adapter-proposal.md)：Proposal-first（提案先行）决策。

Resource 不自动成为 Evidence Reference（证据引用）。只有稳定引用、可归属来源和既有 Execution Reference（执行引用）同时存在时，Adapter 才可生成 Evidence Reference Candidate（证据引用候选）；条件不足必须保留外部引用并返回 `UNKNOWN`。

## Adapter Admission Requirements（适配器准入要求）

未来每个 Adapter 必须单独声明：

- 外部版本与兼容范围；
- 输入、输出和字段映射；
- 无法映射时的 `UNKNOWN/FAIL/CONFLICT/VERSION_MISMATCH` 行为；
- Source ownership（来源所有权）与限制；
- 不创建 Agent、Runtime、Permission 或事实结论的负向测试；
- 独立版本、撤销与迁移路径。

```text
CURRENT_LANGCHAIN_ADAPTER=false
CURRENT_CREWAI_ADAPTER=false
CURRENT_MCP_ADAPTER=false
CURRENT_MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
CURRENT_MCP_ADAPTER_SPECIFICATION=false
CURRENT_MCP_REFERENCE_ADAPTER=false
ADAPTER_NE_FRAMEWORK_REPLACEMENT=true
ADAPTER_NE_PERMISSION=true
ADAPTER_NE_VERIFICATION=true
ADAPTER_BOUNDARY_SPECIFICATION=FROZEN_V0.1
ADAPTER_IMPLEMENTATION_COUNT=0
```

本文件不实现、批准或宣称兼容任何 Adapter。第一个 Reference Implementation（参考实现）需要新的范围、真实外部项目证据和明确授权。
