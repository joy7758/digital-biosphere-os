# ADR-025: DBOS MCP Adapter Specification v0.1（DBOS MCP 适配器规范 v0.1）

状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-21`

## 1. Context（背景）

`ADR-024-mcp-adapter-proposal.md` 已决定采用 Proposal-first（提案先行）：先说明 MCP Adapter（MCP 适配器）为什么需要、风险在哪里、哪些效果必须拒绝，再考虑实现。

Proposal（提案）不足以让不同开发者一致实现。没有字段、生命周期、错误和版本规则时，Tool Call（工具调用）可能被误写成执行事实，Resource（资源）可能被误写成 Evidence Truth（证据真相），外部权限可能被误写成 DBOS Permission（权限），不同协议修订也可能被静默混用。

## 2. Decision（决策）

接受 MCP Adapter Specification v0.1（MCP 适配器规范 v0.1）作为 specification-only translation contract（仅规范的转换合同）：

1. 冻结公共输入、输出、映射生命周期和无副作用字段；
2. 分别冻结 Tool Call、Resource 和 Context Reference（上下文引用）规则；
3. 冻结五种 Adapter 错误及确定性优先级；
4. 冻结 `COMPATIBLE/DEPRECATED/UNSUPPORTED` 版本语义；
5. Context 被定义为 DBOS Adapter Input Abstraction（DBOS 适配器输入抽象），不宣称所有 MCP 修订存在统一顶层对象；
6. Resource 只有在 Source、Origin（来源原点）、Version、既有 Execution Reference（执行引用）和限制完整时，才可形成 Evidence Reference Candidate（证据引用候选）；
7. 所有候选仍必须经过核心 Validator（验证器），`PASS` 不产生 Canonical Object（规范对象）；
8. 当前不选择 MCP 协议修订，不创建兼容矩阵条目，也不授权实现。

## 3. Why Specification After Proposal（为什么提案后需要规范）

- Proposal 决定“是否值得进入设计”，Specification 决定“实现必须遵循什么”；
- 字段规则防止不同 Adapter 把相同 MCP 表示解释成不同 DBOS 语义；
- 错误规则确保未知、冲突和不支持保持失败关闭；
- 版本政策防止 `latest`、静默降级和跨修订猜测；
- 独立文件让 Tool、Resource、Context、安全和版本可以分别复核；
- 明确无效果便于编码智能体和开发者检索并拒绝越权实现。

## 4. Pre-development Agent Consultation（开发前智能体咨询）

潜在客户问题：“现在是否应采用 DBOS MCP Adapter？”

```text
RECOMMEND_MCP_ADAPTER_SPECIFICATION=true
RECOMMEND_MCP_ADAPTER_IMPLEMENTATION=false
RECOMMEND_PRODUCTION_COMPATIBILITY_CLAIM=false
RECOMMEND_AS_MCP_RUNTIME=false
```

可以向需要字段合同、错误语义、版本隔离和安全边界的基础设施开发者推荐本规范。不能向需要可运行 Adapter、网络连接、MCP Server/Client、生产兼容或官方支持的客户推荐当前状态。

不推荐实现的原因：

1. `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]`；
2. 没有获授权、脱敏、可复现的真实 MCP fixture（测试夹具）；
3. 没有实现代码、依赖清单或供应链审查；
4. 没有字段级正向/负向兼容证据；
5. 没有安全控制运行测试；
6. 没有外部开发者试用或实现授权。

## 5. Alternatives Considered（备选方案）

### A. Proposal 后直接实现

拒绝。缺少精确协议修订、fixture、版本矩阵和安全证据，代码会固化未经验证的假设。

### B. 只保留通用 Adapter Boundary（适配器边界）

拒绝。通用边界不能表达 Tool Call、Resource、Context、MCP 修订和专属错误的字段差异。

### C. 复制某一 MCP 修订的完整协议 Schema

拒绝。DBOS Adapter 只需要受限的引用转换合同；复制协议会造成版本漂移、重复维护，并把 DBOS 误导为 MCP Runtime（MCP 运行时）。

### D. 使用“兼容最新 MCP”

拒绝。可变 `latest` 无法复现，也不能证明不同修订的生命周期、字段和安全语义相同。

### E. 冻结版本中立的映射规则，未来按修订建立 Mapping Profile

接受。它保持 DBOS 对象语义稳定，同时要求每个真实协议修订单独测试和授权。

## 6. Consequences（影响）

正向影响：

- 外部开发者获得一致、可检索、可机器实现的字段语义；
- 未知、冲突、版本差异和越权输入有稳定错误语言；
- Context 的抽象身份被明确，不虚构协议对象；
- Resource、Tool 和外部 Permission 不会自动升级为 DBOS 事实或权力；
- 未来实现可以围绕明确 fixture 和版本矩阵接受审查。

限制与成本：

- 当前仍没有代码、Schema、Adapter API 或兼容性测试；
- 每个 MCP 修订都需要独立 Mapping Profile 和测试材料；
- 本规范可能在真实 fixture 暴露缺口后通过新版本演化；
- Specification `FROZEN` 只表示 v0.1 文档语义已冻结，不表示实现 readiness（就绪）或生产支持。

## 7. Non-decisions（非决策）

本 ADR（Architecture Decision Record，架构决策记录）不决定：

- 使用哪个 MCP 协议修订、SDK 或传输；
- Adapter 编程语言、包名、API、Repository 或许可证；
- MCP Server、Client、Runtime 或 Agent Framework；
- 认证、凭据、Permission 或 Tool 授权；
- Event、Evidence、Attestation（证明）或 Verification 写入；
- Minimal MCP Adapter Implementation（最小 MCP 适配器实现）的授权。

## 8. Current State（当前状态）

```text
MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
MCP_ADAPTER_IMPLEMENTATION=false
MCP_REFERENCE_ADAPTER=false
MCP_RUNTIME_CONNECTED=false
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
MCP_MAPPING_PROFILE_COUNT=0
MCP_FIXTURE_COUNT=0
MCP_COMPATIBILITY_EVIDENCE=false
MCP_SECURITY_CONTROLS_TESTED=false
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
CANONICAL_EVIDENCE_MODIFIED=false
VALIDATOR_OVERRIDDEN=false
SAEE_EVOLUTION_TRIGGERED=false
```

## 9. Related Decisions（关联决策）

- `ADR-017-canonical-reference-resolver.md`
- `ADR-019-api-boundary-decision.md`
- `ADR-020-object-contract.md`
- `ADR-021-object-schema-governance.md`
- `ADR-022-validation-result-contract.md`
- `ADR-023-adapter-boundary.md`
- `ADR-024-mcp-adapter-proposal.md`
- `mcp-adapter-specification.md`
- `mcp-version-compatibility-policy.md`
