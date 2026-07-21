# ADR-024: DBOS MCP Adapter Proposal v0.1（DBOS MCP 适配器提案 v0.1）

状态：`ACCEPTED_FOR_PROPOSAL`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-21`

## 1. Context（背景）

DBOS 已冻结通用 Adapter Boundary（适配器边界）。MCP（Model Context Protocol，模型上下文协议）是第一个进入独立提案审查的外部生态方向，因为其 Tool（工具）、Resource（资源）、Context（上下文）和调用引用可能影响 DBOS 的 Execution、Evidence、Reference 与 Permission 边界。

当前仓库没有 MCP Adapter 代码、协议样本、版本矩阵、运行连接、兼容性证据或实现授权。本 ADR 不宣称当前提案符合任何具体 MCP 协议版本。

## 2. Decision（决策）

采用 Proposal-first（提案先行）路径：

1. 先定义 MCP 专属允许输入、对象候选映射、安全边界和风险登记；
2. Tool Call 只可能成为惰性 Execution Object Candidate（执行对象候选表示）；
3. Resource 只有在来源、执行关联和限制充分时才可能成为 Evidence Reference Candidate（证据引用候选表示）；
4. Context 只形成外部 Execution Context Reference（执行上下文引用）；
5. MCP Server、Tool availability 和 access decision 不自动映射 Entity、Capability 或 Permission；
6. 所有候选必须进入核心 Validator（验证器）；
7. 具体协议版本、Schema、Adapter API、代码和本地探针必须等待新 Gate 与授权；
8. 当前不实现 MCP Server、Client、Runtime 或 Adapter。

## 3. Why Proposal First（为什么提案先行）

- Tool、Resource 与 Context 的外部语义不能由第一版代码隐式决定；
- MCP 访问控制与 DBOS Permission 属于不同治理域；
- Tool output 和 Resource 内容需要来源、证据和验证链，不能按连接成功推断；
- 安全风险包括注入、来源冒充、证据污染、权限升级和敏感数据泄露；
- 版本、供应链和撤销要求必须在依赖外部实现之前明确；
- 文档提案可被人工审查，而代码会过早制造事实和兼容性表面。

## 4. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户要求 DBOS 连接 MCP，现在是否应推荐直接实现？

结论：推荐提案审查，不推荐实现。

```text
RECOMMEND_MCP_PROPOSAL_REVIEW=true
RECOMMEND_MCP_ADAPTER_IMPLEMENTATION=false
RECOMMEND_MCP_RUNTIME_CONNECTION=false
RECOMMEND_PRODUCTION_USE=false
```

不推荐原因是缺少受控输入样本、版本矩阵、威胁模型测试、来源认证、供应链材料、隐私边界和外部试点授权。这些缺口不能由模拟数据或代码默认值填补。

## 5. Alternatives Considered（备选方案）

### A. 直接实现 MCP Adapter

拒绝。实现会在没有字段级映射和安全审查时固化错误语义。

### B. 把 DBOS 实现成 MCP Runtime 或 Server

拒绝。它会把连接、执行和服务职责带入 DBOS 核心。

### C. 把 Tool availability 直接登记为 Capability

拒绝。可见性、描述和调用成功都不足以构成能力验证或授予。

### D. 把 Resource 自动保存为 Canonical Evidence

拒绝。Resource 可访问性不证明来源、真实性、完整性、相关性或执行关联。

### E. 提案先行、Gate 控制、后续独立实现

接受。它保持开放接入方向，同时不放弃 DBOS 核心规则。

## 6. Consequences（影响）

正向影响：

- MCP 接入获得明确允许/禁止映射；
- Tool、Capability、Permission 和 Authority 保持分离；
- Resource 与 Evidence Truth 保持分离；
- 注入、污染、升级和泄露风险在代码前可审查；
- 后续 Specification 与 Reference Adapter 有明确 Gate。

限制：

- 当前仍不能连接或调用 MCP；
- 没有协议一致性、性能、安全或生产兼容证据；
- 没有 Mapping Profile、Schema、manifest 或负向测试实现；
- 没有任何外部 MCP Source 获得 DBOS 信任或规范身份。

## 7. Non-decisions（非决策）

本 ADR 没有：

- 创建 MCP、Adapter、Server、Client、Runtime 或网络代码；
- 创建 Agent、Entity、Capability、Permission、Evidence 或 Verification；
- 修改核心 Validator、Canonical Evidence 或历史记录；
- 触发 SAEE Evolution、Fitness 或 C/E/V 变化；
- 修改 SAEE、DBA 或外部项目；
- 授权 commit（提交）、release（发布）或部署。

## 8. Current State（当前状态）

```text
MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
MCP_ADAPTER_SPECIFICATION=NOT_CREATED
MCP_ADAPTER_IMPLEMENTATION=false
MCP_REFERENCE_ADAPTER=false
MCP_RUNTIME_CONNECTED=false
MCP_COMPATIBILITY_EVIDENCE=false
MCP_SECURITY_CONTROLS_TESTED=false
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
EVIDENCE_MODIFIED=false
VALIDATOR_OVERRIDDEN=false
EVOLUTION_TRIGGERED=false
```

## 9. Related Decisions（关联决策）

- `ADR-016-developer-ecosystem.md`
- `ADR-017-canonical-reference-resolver.md`
- `ADR-019-api-boundary-decision.md`
- `ADR-020-object-contract.md`
- `ADR-021-object-schema-governance.md`
- `ADR-022-validation-result-contract.md`
- `ADR-023-adapter-boundary.md`
- `mcp-adapter-proposal.md`
- `mcp-object-mapping-model.md`
- `mcp-security-boundary.md`
- `mcp-adapter-risk-assessment.md`
