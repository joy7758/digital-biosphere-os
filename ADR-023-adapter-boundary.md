# ADR-023: DBOS Adapter Boundary v0.1（DBOS 适配器边界 v0.1）

状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-21`

## 1. Context（背景）

DBOS 已有 Object Contract（对象契约）、机器 Schema（模式）、本地 Validator（验证器）、Minimal Object SDK Skeleton（最小对象软件开发工具包骨架）和 Developer Quick Start（开发者快速入门）。下一生态问题是外部 Agent Framework（智能体框架）如何把已有表示连接到 DBOS。

如果直接为 MCP、LangChain 和 CrewAI 分别编写集成，三个实现可能各自定义身份、引用、错误、版本和验证语义，并把框架 Runtime（运行时）职责带入 DBOS 核心。

## 2. Decision（决策）

采用独立、框架中立的 Adapter Boundary（适配器边界）：

1. Adapter 被定义为 Translation Boundary（转换边界），不是框架、Runtime 或治理主体；
2. 输入是调用方显式提交的外部表示、Source、Version、Scope 和 Limitation；
3. 转换必须显式、版本化、保留来源并保持未知；
4. 输出只形成现有 DBOS 对象契约的候选表示和 Validator 输入；
5. 所有候选必须经过规范 Validator；
6. Adapter 不登记实体、不授予 Permission（权限）、不修改 Evidence（证据）或产生 Verification（事实验证）；
7. Adapter 独立版本化、可替换、可撤销，不进入 DBOS 核心依赖；
8. MCP、LangChain 和 CrewAI 必须分别提案、分别审查，当前均不实现。

## 3. Why Outside the Core（为什么必须独立于核心）

- 外部框架版本和对象模型变化频率高于 DBOS 核心契约；
- 独立组件可以按框架版本升级而不改变规范身份与历史证据；
- 多个实现者可以竞争和替换，不形成供应商锁定；
- Adapter 故障、撤销或供应链事件不会破坏 DBOS 核心；
- 权力与责任更清晰：外部框架运行，Adapter 转换，DBOS 验证结构。

## 4. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户希望把某个 Agent 框架连接到 DBOS，是否应推荐现在实现官方 Adapter？

结论：先推荐边界规范，不推荐具体实现。

```text
RECOMMEND_COMMON_ADAPTER_BOUNDARY=true
RECOMMEND_MCP_ADAPTER_IMPLEMENTATION=false
RECOMMEND_LANGCHAIN_ADAPTER_IMPLEMENTATION=false
RECOMMEND_CREWAI_ADAPTER_IMPLEMENTATION=false
```

不推荐实现的原因：没有受控真实输入样本、框架版本矩阵、Mapping Profile（映射配置）、供应链审查、兼容性证据或外部试点授权。增加代码不能替代这些材料。

## 5. Alternatives Considered（备选方案）

### A. 把框架集成直接加入 DBOS 核心

拒绝。框架依赖会污染核心对象语义并使 DBOS 生命周期受第三方发布节奏控制。

### B. 让每个 Adapter 自行定义对象和验证结果

拒绝。它会产生不兼容身份、错误和结果语言，并允许弱化 Validator。

### C. 把 Adapter 设计成 Runtime proxy（运行时代理）

拒绝。转发执行会让 Adapter 获得任务、网络、凭据和权限职责，违反基础设施边界。

### D. 独立、框架中立的转换边界

接受。它允许生态扩展，同时保持 DBOS 对象、验证、证据和权力语义稳定。

## 6. Consequences（影响）

正向影响：

- 三类未来框架共享统一输入—转换—输出语言；
- 外部 ID、Namespace（命名空间）与 DBOS 规范身份保持分离；
- Adapter 输出必须复用现有 Validator；
- 框架依赖、许可证和供应链风险可以独立管理；
- 未来兼容性主张可以绑定精确版本、环境和范围。

代价与限制：

- 当前仍没有可用 Adapter；
- 真实实现前必须建立 Mapping Profile、manifest（清单）、样本和负向测试；
- 外部框架没有稳定 ID 或来源时，映射必须保持 `UNKNOWN`；
- 转换后仍需独立登记、证据、验证和授权流程。

## 7. Non-decisions（非决策）

本 ADR 没有：

- 创建 Adapter 代码、Schema、SDK API 或 registry；
- 实现或宣称兼容 MCP、LangChain、CrewAI；
- 创建 Agent、Runtime、Permission、Capability 或真实 DBOS Object；
- 修改 Canonical Evidence（规范证据）或 Validator；
- 授予 Architecture Authority（架构权力）；
- 修改 SAEE、DBA、C/E/V 等级或历史记录；
- 执行 commit（提交）或 release（发布）。

## 8. Current State（当前状态）

```text
ADAPTER_BOUNDARY_SPECIFICATION=FROZEN_V0.1
ADAPTER_OBJECT_MAPPING_MODEL=DEFINED_V0.1
ADAPTER_SECURITY_BOUNDARY=DEFINED_V0.1
ADAPTER_IMPLEMENTATION_COUNT=0
OFFICIAL_ADAPTER_COUNT=0
MAPPING_INSTANCE_COUNT=0
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_CREATED=false
EVIDENCE_MODIFIED=false
VALIDATOR_OVERRIDDEN=false
```

## 9. Related Decisions（关联决策）

- `ADR-016-developer-ecosystem.md`
- `ADR-017-canonical-reference-resolver.md`
- `ADR-019-api-boundary-decision.md`
- `ADR-020-object-contract.md`
- `ADR-021-object-schema-governance.md`
- `ADR-022-validation-result-contract.md`
- `adapter-boundary-specification.md`
- `adapter-object-mapping-model.md`
- `adapter-security-boundary-rules.md`
