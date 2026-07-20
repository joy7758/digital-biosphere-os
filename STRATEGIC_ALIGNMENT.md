# Digital Biosphere OS v0.1 战略对齐说明

中文定位：开放数字实体基础设施

规范定位：`Open Digital Entity Infrastructure`

状态：`STRATEGIC_ALIGNMENT_SYNCHRONIZED`

任务性质：`STRATEGY_ONLY`

实现效果：`NONE`

能力效果：`NONE`

权限效果：`NONE`

## 1. 战略来源与权力边界

本说明把 DBOS（Digital Biosphere Operating System，数字生物圈操作系统）与 Digital Biosphere Architecture（数字生物圈架构，以下简称 DBA）的最高开放基础设施战略对齐。

战略来源：

- [`open-infrastructure-strategy-constitution.md`](../digital-biosphere-architecture/architecture/open-infrastructure-strategy-constitution.md)：最高开放基础设施战略宪法；
- [`developer-ecosystem-strategy.md`](../digital-biosphere-architecture/architecture/developer-ecosystem-strategy.md)：开发者生态方向；
- [`commercialization-strategy.md`](../digital-biosphere-architecture/architecture/commercialization-strategy.md)：开放核心与商业边界；
- [`project-mapping.md`](../digital-biosphere-architecture/architecture/project-mapping.md)：项目战略角色映射。

DBA 是 public meaning and strategic constitution layer（公开含义与战略宪法层），拥有战略词汇、角色边界和架构决策语境。DBOS 是受该战略约束的操作治理基础设施，不修改、不复制、不覆盖 DBA 的战略权力。

本说明不修改 DBA，不改变任何 DBOS 技术事实、能力事实、证据事实、验证结果、发布状态、开发状态或商业可用性。发生战略解释冲突时，以 DBA 的 `Open Infrastructure Strategy Constitution v0.1`（开放基础设施战略宪法 v0.1）为上位来源；具体技术事实仍以 DBOS 自身登记表和证据为准。

## 2. DBOS 战略定位

> DBOS is Open Digital Entity Infrastructure.
>
> 中文：DBOS 是开放数字实体基础设施。

> DBOS governs existence.
>
> 中文：DBOS 治理存在。

DBOS 面向可信 Digital Entity（数字实体）提供开放、可检查、可替换、可追踪的存在治理基础。它处理数字实体“是谁、处于什么状态、在什么边界内行动、产生了什么事实、如何被引用和验证”等基础设施问题。

DBOS 的战略价值不以它内置多少 Agent（智能体）或应用功能衡量，而以身份、生命周期、边界、证据和验证机制能否被开发者理解、组合、替换与复用衡量。

## 3. DBOS 核心职责

### Identity（身份）

定义和维护数字实体的规范身份、所有权引用、谱系与身份连续性。Repository（仓库）、Protocol（协议）、Service（服务）、Artifact（工件）和 Runtime（运行时实例）不得被自动合并为同一主体。

### Lifecycle（生命周期）

维护从提出、活动、验证、弃用到退役的追加式生命周期记录。实体退役不等于删除历史。

### Capability Boundary（能力边界）

区分 capability claim（能力声明）、evidence（证据）、verification（验证）、permission（权限）和 authority（权力）。能力存在或被声明，不表示被批准、分配或允许使用。

### Execution Context（执行上下文）

记录受治理执行所依赖的环境、版本、配置、输入、输出和依赖关系，为限定范围内的可复核事实提供上下文。

### Evidence Integration（证据集成）

连接身份、声明、执行产物、事件、完整性与证明记录，保留来源、摘要、限制和撤销路径。DBOS 集成证据，不把文件存在自动升级为高等级证据或事实真理。

### Verification Support（验证支持）

提供验证结构、引用、等级边界、验证主体登记和 fail-closed（失败关闭）检查支持。Validator pass（验证器通过）不等于独立认证、能力批准或生产适用性结论。

### Federation（联邦）

为未来独立项目之间的身份引用、宪法继承、清单通信、证据关系和互操作治理提供连接基础。Federation（联邦）不合并仓库、不接管成员身份，也不自动注册成员。

## 4. 与 DBA 的关系

```text
Digital Biosphere Architecture
  -> 公开含义、最高战略宪法、角色边界与 ADR 语境

Digital Biosphere OS
  -> 开放数字实体基础设施、存在治理与事实链支持
```

该关系是战略继承，不是代码依赖、部署关系、执行授权或产品控制关系。

DBOS 必须引用 DBA 的战略方向，但不得：

- 单方面修改 DBA 战略宪法；
- 把战略说明转写成虚假的既有功能；
- 把 DBA 变成 DBOS 的 Runtime（运行时）或执行控制面；
- 以 DBOS 的局部技术事实覆盖 DBA 的战略角色映射。

## 5. 与 SAEE 的边界

保持以下不可混淆关系：

```text
DBOS governs existence.
SAEE governs evolution.
DBOS != SAEE.
```

中文：

```text
DBOS 治理存在。
SAEE 治理演化。
DBOS 不等于 SAEE。
```

DBOS 负责可归因事实及其存在治理边界，包括身份、生命周期、执行上下文、事件、证据引用和验证支持。

SAEE 负责 evaluation and evolution interpretation（评价与演化解释），包括适应度评价、适应分析和演化建议。SAEE 的评价不得获得 DBOS 身份、权限、执行或历史证据修改权。

DBOS 核心不得实现或占有：

- Fitness（适应度）计算或评分；
- Evolution Algorithm（演化算法）；
- Selection Model（选择模型）；
- Ecological Simulation（生态模拟）；
- 以演化建议自动改变身份、能力、权限或证据的机制。

DBOS 中现有的 SAEE 映射、空适应度模型或选择压力词表只保留解释和边界作用，`authority_effect=none`；它们不是 DBOS 的演化引擎，也不产生适应度、选择或生态演化事实。

## 6. 开发者生态方向

DBOS 首要支持 Agent Developer Ecosystem（智能体开发者生态），让开发者能够构建可信 Digital Entity（数字实体）。未来基础设施方向包括：

- Open Protocol（开放协议）；
- SDK（软件开发工具包）；
- Validator（验证器）；
- Developer Tooling（开发者工具）；
- Reference Implementation（参考实现）。

这些项目必须满足开放、版本化、可引用、可替换、模型与供应商中立、Specification != Implementation（规范不等于实现）以及默认 fail-closed（失败关闭）等原则。

这些名称只表示战略方向，不表示相应 SDK、工具、市场、稳定版本、生产 Runtime、兼容实现或支持承诺已经存在。Reference Implementation（参考实现）只能证明限定范围内的最小可实现性，不能成为唯一官方运行时或全功能 Agent 平台。

未来 Codex（编码智能体）任务在提出 DBOS 开发前，必须先回答：

1. 如果潜在客户提出该需求，智能体是否会推荐 DBOS 现有程序？
2. 不推荐的原因是基础设施缺口，还是应用层、SAEE、商业服务或单一客户工作流需求？
3. 该提案是否能被多个数字实体复用，并可由开放 contract（契约）或 validator（验证器）表达？
4. 它是否保持 `DBOS is infrastructure, not application`（DBOS 是基础设施，不是应用）？

不能证明开放基础设施复用价值的功能，默认归入应用层、行业方案或独立项目，不进入 DBOS 核心。

## 7. 商业边界

DBOS 不直接定义：

- 企业产品价格；
- 商业合同或采购条款；
- SaaS（软件即服务）承诺；
- SLA（服务等级协议）；
- 客户采用、收入或市场验证；
- Enterprise Edition（企业版）、认证服务或行业方案的可用性。

这些事项属于 DBA 战略层、商业决策层、行业应用层或 Governance Service Ecosystem（治理服务生态）。DBOS 的开放协议和治理事实不得因付费、上架、客户关系或商业包装而被改写。

```text
STRATEGY != AVAILABLE_OFFERING
VALIDATOR_PASS != CERTIFICATION
OPEN_INFRASTRUCTURE != FREE_PRODUCT
```

中文：战略不等于可用产品；验证器通过不等于认证；开放基础设施不等于免费产品承诺。

## 8. 非目标范围

DBOS 不得被定位为：

- Foundation Model（基础模型）；
- Agent Application（智能体应用）；
- 普通 Agent Platform（智能体平台）；
- Chatbot Platform（聊天机器人平台）；
- Agent Builder（智能体构建器）；
- Evolution Engine（演化引擎）；
- SAEE substitute（SAEE 替代品）；
- Digital Organism factory（数字生命体制造平台）；
- 单一行业应用；
- 自动治理或自动授权系统；
- 封闭 SaaS（软件即服务）产品。

行业应用、企业部署、审计、合规、认证和高级治理服务可以建立在 DBOS 之上，但不自动成为 DBOS 核心，也不能获得 Evidence Truth（证据事实）或 Architecture Authority（架构权力）。

## 9. 战略提案闸门

所有未来 DBOS 提案必须先分类为以下之一：

- `INFRASTRUCTURE`：开放、跨应用复用的存在治理基础；
- `EVOLUTION`：应交由 SAEE 的评价或演化解释；
- `APPLICATION`：行业 Agent、工作流或最终用户应用；
- `GOVERNANCE_SERVICE`：审计、合规、适配或认证服务。

只有 `INFRASTRUCTURE` 类提案可以申请进入 DBOS 核心。仍须另行完成需求、证据、风险、架构和人工治理审查；战略归类本身不构成开发授权。

以下任一情况存在时，状态保持 `REVIEW_REQUIRED`：

- 把身份、能力、权限、权力、执行或证据事实混为一体；
- 复制 Foundation Model、Agent framework（智能体框架）、SAEE 或既有生态组件职责；
- 依赖单一模型、Runtime、行业、云厂商或客户工作流；
- 把战略、演示、验证器通过或本地实验升级为产品可用、采用、认证或合同事实；
- 不能说明开放协议、互操作性或开发者复用价值。

## 10. 不变量与非声明

```text
DBOS_ROLE=OPEN_DIGITAL_ENTITY_INFRASTRUCTURE
DBOS_GOVERNS_EXISTENCE=true
SAEE_GOVERNS_EVOLUTION=true
DBOS_NE_SAEE=true
DBOS_NE_AGENT_APPLICATION=true
DBOS_NE_AGENT_PLATFORM=true
DBOS_NE_FOUNDATION_MODEL=true
DBOS_NE_CHATBOT_PLATFORM=true
DBOS_NE_EVOLUTION_ENGINE=true
DEVELOPER_ECOSYSTEM_FIRST=true
SPECIFICATION_NE_IMPLEMENTATION=true
STRATEGY_NE_COMMERCIAL_COMMITMENT=true
CAPABILITY_EFFECT=NONE
PERMISSION_EFFECT=NONE
EXECUTION_EFFECT=NONE
DEVELOPMENT_STATUS_EFFECT=NONE
AUTOMATIC_AUTHORITY_EFFECT=NONE
```

本说明不创建 Agent、Runtime、Digital Organism、Capability 或 Permission；不恢复任何暂停开发；不授权功能开发；不执行实验；不修改 SAEE 或 DBA；不产生价格、合同、SaaS、认证、采用、发布或商业可用性承诺。

