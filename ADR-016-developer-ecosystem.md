# ADR-016: DBOS Developer Ecosystem v0.1（DBOS 开发者生态 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-20`

决策范围：Developer Kit（开发者工具包）的定位、体验、扩展和信任边界

## 1. Context（背景）

DBOS 已建立 Digital Entity Infrastructure（数字实体基础设施）、Candidate Registration（候选登记）、Registration Execution（登记执行）、Evidence Reference（证据引用）和 Verification Boundary（验证边界）。现有支撑层通过 Python 标准库模块和 Validator（验证器）证明了一组安全默认记录契约，但仍没有可安装 SDK、稳定公共 API、官方 Adapter（适配器）或生产 Runtime（运行时）。

DBOS 的最高战略定位是 Open Digital Entity Infrastructure（开放数字实体基础设施）。如果不先冻结开发者边界，后续 SDK 很容易吸收模型、Agent 编排、Runtime 和应用职责，退化为通用 Agent Framework（智能体框架）。

本 ADR 只决定规范方向，不批准实现、不恢复任何暂停开发，也不改变 C/E/V、Capability（能力）、Permission（权限）、Agent、Runtime 或 Digital Organism（数字生命体）事实。

## 2. Source Boundary（来源边界）

决策依据：

- `STRATEGIC_ALIGNMENT.md`
- `entity_support/README.md`
- `reports/DBOS-DIGITAL-ENTITY-INFRASTRUCTURE-IMPLEMENTATION-ROADMAP-v0.1.md`
- `constitution/`、`registry/`、`policies/`
- 本轮用户授权的 Developer Ecosystem Design（开发者生态设计）目标

`STRATEGIC_ALIGNMENT.md` 引用的 DBA（数字生物圈架构）四份战略文件在 DBA 当前工作树和可见 Git 历史中不可用。本 ADR 不重建 DBA 内容，也不把 DBOS 的解释提升为 DBA Architecture Authority（架构权力）。来源恢复后需要执行冲突审查。

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户询问“我能否用当前 DBOS 把既有 Agent 接入可信身份、证据和验证链”，智能体是否会推荐？

结论：**限定推荐。**

可推荐场景：

- 研究或本地集成设计；
- 安全默认的身份与登记契约；
- Capability/Permission 隔离；
- 执行上下文、证据和验证引用建模；
- 失败关闭的基础设施原型与审计边界。

不可推荐场景：

- 期望直接安装稳定 SDK；
- 期望 DBOS 提供生产 Agent Runtime；
- 期望官方 LangChain、CrewAI 或 MCP Adapter；
- 期望 Permission Engine（权限引擎）、独立认证或 SaaS（软件即服务）；
- 期望 SAEE 适应度、选择或演化功能。

不推荐原因：

1. SDK package（软件包）和公共 API 尚不存在；
2. 跨语言 schema（模式）、错误模型和兼容策略尚未冻结；
3. canonical reference resolver（规范引用解析器）尚未建立；
4. Trust Package（信任包）契约和导出验证器尚不存在；
5. 没有真实外部 Agent 端到端接入证据；
6. Adapter 和生产支持尚未建立。

这些原因应分解为开放基础设施缺口，不应通过增加 Agent 应用功能来解决。

## 4. Decision（决策）

DBOS Developer Kit v0.1 采用“governed integration contracts（受治理集成契约）”定位：

1. 外部开发者在 DBOS 之外创建和运行 Agent/Application（智能体/应用）；
2. DBOS 提供 Identity、Lifecycle、Capability Boundary、Execution Context、Evidence Reference 和 Verification 的开发者契约；
3. SDK 概念入口为 `register`、`execute`、`evidence`、`verify`，但 v0.1 规范不冻结函数签名或实现 API；
4. `execute` 只治理调用方提供的外部 Runtime 上下文，不让 DBOS 成为 Runtime 或模型控制面；
5. Developer Trust 通过可解析 Trust Package 表达，不授予 Permission、认证或全局信任；
6. LangChain、CrewAI 和 MCP 通过独立、可替换 Adapter 接入，不进入核心依赖；
7. 第三方可开发 Adapter、Validator、Tooling（工具）和 Industry Extension（行业扩展），但不获得 Architecture Authority；
8. 商业服务位于开放核心契约之上，不能修改身份、证据、验证或历史事实；
9. 下一阶段先冻结契约和引用解析，再申请最小 SDK 实现。

## 5. Developer Journey（开发者旅程）

采用以下目标流程：

```text
Create Agent externally（在外部创建 Agent）
  ↓
Register identity（登记身份）
  ↓
Declare capability boundary（声明能力边界）
  ↓
Test locally（本地测试）
  ↓
Execute through governed context（通过受治理上下文连接执行）
  ↓
Reference evidence（引用证据）
  ↓
Verify within scope（在范围内验证）
  ↓
Export trust package（导出信任包）
```

流程中每个箭头都是证据或授权闸门，不是自动状态转换。

## 6. SDK Boundary（SDK 边界）

SDK 核心候选范围：

- 版本化数据契约；
- 候选登记和回执；
- 生命周期引用；
- Capability Boundary 声明；
- Execution Context 连接；
- Evidence/Verification 引用；
- manifest 和 Trust Package 验证；
- 结构化错误与失败关闭。

SDK 核心排除范围：

- 模型、推理、规划、记忆和 Tool 编排；
- Agent builder（智能体构建器）；
- Runtime 调度、托管或生产执行；
- Permission 自动决策；
- 独立认证和法律/合规结论；
- SAEE Fitness、Evolution Algorithm 或 Selection Model；
- 单一框架、云厂商、行业或客户工作流。

## 7. Alternatives Considered（备选方案）

### A. 直接构建通用 Agent Framework

拒绝。它会复制 LangChain、CrewAI 等生态职责，并破坏 `DBOS = Infrastructure` 边界。

### B. 先实现三个官方 Adapter，再补核心契约

拒绝。没有统一身份、上下文、证据和错误契约时，Adapter 会产生三套不兼容事实模型，并把外部框架耦合进核心。

### C. 只发布文档，不规划 SDK

拒绝作为长期路线。DBOS 的战略目标是让外部开发者可用；纯文档不能证明互操作契约可实现。但在本阶段，规范先于实现是必要闸门。

### D. 采用受治理集成契约并分阶段实现

接受。它保留 DBOS 的基础设施职责，同时允许 SDK、Adapter、Validator 和商业服务独立演化。

## 8. Consequences（影响）

正向影响：

- 外部开发者能理解 DBOS 提供什么和不提供什么；
- Agent 框架和 Runtime 保持独立；
- Capability、Evidence、Verification、Permission 和 Trust 继续分离；
- Adapter 可以独立版本化、替换和商业维护；
- 下一阶段开发拥有可检查的 stop rule（停止规则）。

代价：

- SDK 实现前必须先解决 schema、引用和兼容性问题；
- 初期接入流程会比“自动发现并注册”更严格；
- 第三方扩展需要维护 manifest、证据和版本矩阵；
- 不能用单一 `trusted=true` 或 `verified=true` 简化复杂治理事实；
- DBA 战略源文件缺失需要后续来源修复和冲突审查。

## 9. Implementation Gates（实现闸门）

`DBOS Developer Kit Implementation v0.1` 只有在新的明确授权后才能启动，并按以下顺序推进：

1. `GATE-1 CONTRACT_FREEZE`：实体类型/角色、Capability 字段、风险词表、版本和错误模型一致；
2. `GATE-2 REFERENCE_RESOLUTION`：规范引用解析、撤销、过期和失败语义明确；
3. `GATE-3 API_DECISION`：包名、API 表面、幂等和同步/异步边界经审查；
4. `GATE-4 MINIMAL_SDK`：只实现基础设施接口，Agent/Runtime/Permission 仍为外部；
5. `GATE-5 TRUST_PACKAGE`：schema、验证器、限制和隐私边界可测试；
6. `GATE-6 LOCAL_REFERENCE`：合成 fixture 通过正向和负向检查；
7. `GATE-7 EXTERNAL_PILOT`：真实既有 Agent 自愿申请，人工授权，证据和失败保留；
8. `GATE-8 ADAPTER_REVIEW`：LangChain、CrewAI、MCP 分别提案、分别版本化。

每个 Gate 需要再次回答智能体推荐问题。Gate 通过不自动授权下一个 Gate。

## 10. Commercial Interface Decision（商业接口决策）

允许未来商业参与者基于开放契约提供集成、托管 Validator、证据保留、行业映射、审计支持、私有部署和培训。

不在本 ADR 中决定：

- 价格；
- 合同；
- SLA；
- SaaS 产品；
- Enterprise Edition（企业版）；
- 认证计划；
- 市场上架；
- 收入或客户采用。

商业关系不得改变 DBOS 技术事实、Evidence 等级、Verification 决定或 Permission。

## 11. Non-decisions（非决策）

本 ADR 没有：

- 创建 SDK 文件、包或 API；
- 创建 Agent、Runtime 或 Digital Organism；
- 修改 DBA 或 SAEE；
- 建立官方 Adapter；
- 产生 Capability、Permission、认证或商业产品；
- 改变现有 C/E/V 状态；
- 修改历史 Evidence；
- 授权 commit（提交）或 release（发布）。

## 12. Decision Invariants（决策不变量）

```text
DECISION_SCOPE=DEVELOPER_ECOSYSTEM_SPECIFICATION
IMPLEMENTATION_AUTHORIZED=false
DBOS_ROLE=INFRASTRUCTURE
AGENT_ROLE=APPLICATION
SAEE_ROLE=EVOLUTION
ARCHITECTURE_ROLE=GOVERNANCE
SDK_NE_AGENT_FRAMEWORK=true
ADAPTERS_ARE_OPTIONAL=true
RUNTIME_IS_EXTERNAL=true
TRUST_NE_PERMISSION=true
COMMERCIAL_INTERFACE_NE_COMMERCIAL_OFFER=true
```

## 13. 关联规范

- `developer-kit-specification.md`
- `developer-quickstart-model.md`
- `developer-extension-model.md`
- `developer-trust-model.md`
- `STRATEGIC_ALIGNMENT.md`
- `entity_support/README.md`
