# DBOS Developer Kit Specification v0.1（DBOS 开发者工具包规范 v0.1）

状态：`SPECIFICATION_WITH_LOCAL_SDK_PREVIEW`

实现状态：`MINIMAL_OBJECT_SDK_SKELETON_IMPLEMENTED_LOCAL_V0.1`

API 状态：`CONCEPTUAL_ONLY`

API 边界状态：`FROZEN_FOR_SPECIFICATION`

Object Schema（对象模式）状态：`DEFINED_V0.1`

Object Schema Validator（对象模式验证器）状态：`IMPLEMENTED_LOCAL_V0.1`

Validation Result Contract（验证结果契约）状态：`FROZEN_V0.1`

Minimal Object SDK Skeleton（最小对象软件开发工具包骨架）状态：`LOCAL_IMPORTABLE_NOT_PACKAGED`

规范角色：Developer Ecosystem Design（开发者生态设计）

## 1. 规范定位

DBOS Developer Kit（DBOS 开发者工具包）是外部开发者把既有 Agent（智能体）、服务或其他数字实体连接到 DBOS 存在治理层的契约集合。它面向 Identity（身份）、Lifecycle（生命周期）、Capability Boundary（能力边界）、Execution Context（执行上下文）、Evidence Reference（证据引用）和 Verification（验证）提供一致的开发者入口，并为未来只读 Autonomy Policy Reference（自主策略引用）预留边界。

Developer Kit（开发者工具包）不是 Agent Framework（智能体框架）。Agent 的模型、推理、规划、记忆、工具编排和业务行为由 Agent 应用及其选用的框架或 Runtime（运行时）负责；DBOS 只治理该数字实体如何被识别、约束、记录和验证。

```text
DBOS = Infrastructure
Agent = Application
SAEE = Evolution Layer
Architecture = Governance
```

中文：DBOS 是基础设施；Agent 是应用；SAEE 是演化层；Architecture（架构）是治理层。

## 2. 事实来源与权力边界

本规范受以下本地事实源约束：

1. `STRATEGIC_ALIGNMENT.md`：DBOS 的开放基础设施定位、DBA（数字生物圈架构）关系、SAEE 边界与商业边界；
2. `entity_support/README.md`：现有登记、能力、执行上下文、证据和验证支撑层的实际边界；
3. `reports/DBOS-DIGITAL-ENTITY-INFRASTRUCTURE-IMPLEMENTATION-ROADMAP-v0.1.md`：现有实现、测试与剩余风险；
4. `constitution/`、`registry/` 与 `policies/`：身份、能力、证据、验证和权限的规范事实源。

`STRATEGIC_ALIGNMENT.md` 中引用的 4 份 DBA 战略文件在 DBA 当前工作树和可见 Git 历史中均不可用。本规范不重建或修改这些 DBA 文件，只使用已经同步进 DBOS 的战略边界。DBA 来源恢复后，若存在冲突，必须另行审查本规范；不得静默改写。

## 3. 开发者获得什么

开发者获得的是一条可组合、可检查、失败关闭的可信运行链，而不是权限、认证或智能授予：

- 为外部创建的数字实体准备规范身份申请与登记引用；
- 使用统一 Reference Object（引用对象）和 Resolution Result（解析结果）定位跨模块、Adapter 与 Extension 引用；
- 记录生命周期状态和身份连续性；
- 声明能力边界，并保持声明、验证、授权与权限相互分离；
- 未来读取有来源、版本、范围和限制的 Autonomy Policy，判断策略声明的人工批准要求；
- 把调用方执行连接到明确的环境、输入、输出和依赖上下文；
- 引用现有证据，不复制或篡改规范证据；
- 请求限定范围的验证，并导出可供消费者独立判断的 Trust Package（信任包）。

任何 DBOS 返回值都必须说明它证明什么、没有证明什么以及仍需谁作出决定。

## 4. 开发者不获得什么

Developer Kit 不提供：

- Agent 创建、业务逻辑、推理循环、规划器或记忆系统；
- Foundation Model（基础模型）、模型托管、模型路由或模型控制；
- LangChain、CrewAI 或其他 Agent 框架的替代实现；
- Runtime 供应、任务调度、容器编排或生产部署；
- Capability（能力）、Permission（权限）、Authority（权力）或 Intelligence（智能）的自动授予；
- Autonomy Policy 的自动创建、激活、扩大、续期、撤销或 Runtime 强制；
- 认证、合规结论、生产适用性结论或商业承诺；
- Fitness（适应度）、演化算法、选择模型或 SAEE 评价结果。

## 5. 目标开发者流程

以下是完整 Developer Kit 的未来目标体验。当前本地对象 SDK 骨架只能构造、序列化和验证对象表示，不表示 SDK 已经可以安装，也不表示下列登记、执行、证据或验证业务调用已经存在：

```text
Install DBOS SDK（安装未来的 DBOS SDK）
  ↓
Resolve Declared References（解析显式声明的引用）
  ↓
Register Agent Identity（登记 Agent 身份）
  ↓
Declare Capability Boundary（声明能力边界）
  ↓
Read Applicable Autonomy Policy（读取适用自主策略）
  ↓
Execute Through DBOS Context（通过 DBOS 上下文连接外部执行）
  ↓
Generate Evidence Reference（生成证据引用）
  ↓
Verify Execution（验证限定范围内的执行）
  ↓
Export Trust Package（导出信任包）
```

每一步都必须保留失败关闭边界：

| 步骤 | 最小输入 | 目标产物 | 不自动产生 |
|---|---|---|---|
| Resolve（解析） | Reference ID、Type、Namespace、Version、Source | 四态 Resolution Result | Authority、Verification、Permission |
| Register（登记） | Candidate、Owner、身份来源、独立授权引用 | Registration Receipt（登记回执）或失败记录 | `ACTIVE`、Agent 实例、Permission |
| Declare（声明） | 能力名称、范围、限制、风险 | Capability Claim（能力声明） | Verified Capability（已验证能力）、授权 |
| Policy（策略） | Entity、Capability、Permission、Action、Context 引用 | 人工批准要求或 `BLOCKED/UNKNOWN/CONFLICT` | Permission、Policy Authority、Execution |
| Context（上下文） | 已存在的实体、环境、输入、依赖 | Execution Context Reference（执行上下文引用） | Runtime、执行结果 |
| Evidence（证据） | 执行引用、来源、完整性材料 | Evidence Reference（证据引用） | Truth（事实真值）、高等级证据 |
| Verify（验证） | Claim、Evidence、方法、Verifier | 限定范围的 Verification Record（验证记录） | Permission、认证、生产就绪 |
| Export（导出） | 上述可解析引用与限制 | Trust Package（信任包） | 信任强制、客户采用或治理权力 |

## 6. SDK Layer（SDK 层）概念边界

以下名称仅用于讨论未来 API 形态，不是已实现、已冻结或可调用的接口：

```python
dbos.resolve(...)
dbos.register(...)
dbos.execute(...)
dbos.evidence(...)
dbos.verify(...)
```

### `dbos.resolve(...)`

- 接收：显式 `reference_id`、Reference Type（引用类型）、Namespace（命名空间）、Version、Source 和 status；
- 产生：`RESOLVED`、`AMBIGUOUS`、`UNKNOWN` 或 `INVALID` 四种 Resolution Result 之一；
- 边界：`RESOLVED` 只表示在声明范围内找到唯一记录，不表示身份已验证、Authorization 有效、Evidence 真实或 Permission 已授予；
- 约束：Resolver（解析器）只读、失败关闭、保留 Source ownership（来源所有权），不能创建或修改任何对象。

规范见 `canonical-reference-resolver-specification.md`、`reference-namespace-model.md` 与 `reference-resolution-boundary-rules.md`。当前没有 Resolver 代码、API 或 Namespace Registry（命名空间登记表）。

### `dbos.register(...)`

- 接收：外部 Candidate（候选体）记录、身份来源、Owner（所有者）引用和独立授权引用；
- 产生：成功或失败的登记结果与回执引用；
- 边界：登记上限为 `REGISTERED`，不能自动进入 `ACTIVE`，也不能把 Repository（仓库）或 Service（服务）自动变成 Agent。

### `dbos.execute(...)`

- 接收：已登记实体引用、调用方提供的兼容 Runtime、任务引用、环境和输入；
- 产生：受治理执行的上下文与结果引用；
- 边界：DBOS 包装并记录外部执行边界，不负责 Agent 推理，不供应 Runtime，也不允许没有授权和上下文的执行。

### `dbos.evidence(...)`

- 接收：Execution、Event、Artifact（工件）或外部 Evidence 的可解析引用；
- 产生：来源、摘要、范围、限制和状态明确的 Evidence Reference；
- 边界：引用不复制事实真源，不自动提升 E 等级，也不把文件存在视为真实性。

### `dbos.verify(...)`

- 接收：Claim、Evidence、Verifier、方法和目标范围；
- 产生：Verification Record 与限制；
- 边界：验证结果不等于 Review Approval（复核批准）、Capability Assignment（能力分配）、Permission 或 Certification（认证）。

未来 API 必须保持显式输入、显式状态、结构化错误、幂等或重放边界、版本字段和追加式审计记录。任何省略关键证据或授权的调用都必须失败关闭。

## 6A. API Boundary Decision（应用程序接口边界决策）

未来 Developer Kit 必须遵守 `api-boundary-decision.md`，并把公共接口限定为七类职责：Identity、Lifecycle、Capability、Execution Context、Evidence、Verification 和 Reference Resolver。

允许的 API effect（接口效果）只有：

```text
READ
RESOLVE
OBSERVE
LINK
```

以下效果不在 v0.1 API 边界内：

```text
COMMAND
DECIDE
EXECUTE
GRANT
EVOLVE
```

因此，本节已有的 `dbos.register(...)` 与 `dbos.execute(...)` 仍只是讨论早期流程的概念名称，不能直接实现为公共接口：

- `register` 必须拆分为 Candidate request（候选请求）、独立治理决定、显式持久化和 Receipt（回执）；API 调用本身不签发规范身份；
- `execute` 必须收窄为 Execution Context 与 inert Execution Record（惰性执行记录）边界；模型、工具、任务和 Agent 执行仍由外部 Runtime 负责。

API 的职责、非职责、对象和错误分别见：

- `api-boundary-decision.md`；
- `api-responsibility-model.md`；
- `api-object-contract-model.md`；
- `api-error-model.md`；
- `ADR-019-api-boundary-decision.md`。

这些文件冻结架构语义，不冻结 endpoint、transport、Schema、SDK 或实现。

## 6B. Object Contract Specification（对象契约规范）

未来 Developer Kit 必须使用 `object-contract-specification.md` 冻结的五类核心对象：

- Entity Object（实体对象）；
- Capability Object（能力对象）；
- Execution Object（执行对象）；
- Evidence Reference Object（证据引用对象）；
- Verification Object（验证对象）。

所有对象共享：

```text
object_id
object_type
version
source
status
created_at
updated_at
limitations
```

SDK 不得自行重命名字段、改变 `UNKNOWN` 语义、建立第二套 ID，或从对象生成 Authority、Permission、Capability Grant、Execution 和 SAEE Evolution。`object_id` 必须等于对应类型的专属 ID。

规范入口：

- `object-contract-specification.md`；
- `entity-object-contract.md`；
- `capability-object-contract.md`；
- `execution-object-contract.md`；
- `evidence-reference-object-contract.md`；
- `verification-object-contract.md`；
- `object-error-semantics.md`；
- `ADR-020-object-contract.md`。

这些文件冻结 semantic contract（语义契约）。配套机器可读 Schema 现已定义：

- `schemas/common-object-schema.yaml`；
- `schemas/entity-object-schema.yaml`；
- `schemas/capability-object-schema.yaml`；
- `schemas/execution-object-schema.yaml`；
- `schemas/evidence-reference-object-schema.yaml`；
- `schemas/verification-object-schema.yaml`；
- `schema-version-policy.md`；
- `ADR-021-object-schema-governance.md`。

Schema 只提供结构标准。本地 `sdk/` 现可创建五类不可变内存对象表示并将其交给 DBOS Object Schema Validator（对象模式验证器），但对象表示不创建其描述的现实主体；可安装 SDK、远程 API 与 API Server（应用程序接口服务器）仍不存在。`validator/` 显式执行通用 JSON Schema Validator 忽略的 `x-dbios-*` 规则，只检查调用方提供的表示，不访问外部 Source、不创建治理对象，也不产生 Permission、Execution 或 Verification。

Validator Output Contract（验证器输出契约）已冻结为：

- `validation-result-contract-specification.md`；
- `validation-error-object-model.md`；
- `validation-result-boundary-rules.md`；
- `ADR-022-validation-result-contract.md`。

本地 SDK 骨架已经原样复用 9 字段 ValidationResult Object（验证结果对象）和五种结果状态，未重命名、未自动修复，也不从 `PASS` 推导 Authorization。未来可分发 SDK 仍必须保持这一契约。

## 6C. Proposed Autonomy Policy Read Boundary（拟议自主策略读取边界）

`autonomy-policy-specification.md` 提出未来 SDK 只读使用 Autonomy Policy（自主策略）的边界。它不是当前五类核心对象的第六类，也没有 Schema、Validator、SDK 或 API 实现。

未来 SDK 可以：

- 读取 `autonomy-policy-object-model.md` 描述的 Policy 表示；
- 检查 `entity_reference`、`autonomy_mode`、Scope（范围）、Constraint（约束）、Capability、Permission、Approval（批准）、版本和撤销引用；
- 根据调用方提供的完整治理输入，确定 Policy 声明的是 `APPROVAL_REQUIRED/ALLOW_WITHIN_SCOPE/BLOCKED/UNKNOWN/CONFLICT`；
- 返回缺失条件、适用限制和 Evidence 要求。

未来 SDK 不能：

- 创建、激活、扩大、续期或撤销 Policy Authority（策略权力）；
- 把 `ALLOW_WITHIN_SCOPE` 变成 Permission、Authorization（授权）、Execution command（执行命令）或 Verification；
- 选择更宽自主模式、自动批准或绕过现有危险能力人工批准规则；
- 创建 Agent、Runtime、Entity、Evidence 或实际执行。

规范入口：

- `autonomy-policy-specification.md`；
- `autonomy-policy-object-model.md`；
- `autonomy-boundary-rules.md`；
- `autonomy-mode-comparison.md`；
- `ADR-026-autonomy-policy.md`。

## 7. Developer Workflow（开发者工作流）

```text
Create Agent outside DBOS（在 DBOS 外部创建 Agent）
  ↓
Prepare registration package（准备登记材料）
  ↓
Register（登记）
  ↓
Declare capability boundary（声明能力边界）
  ↓
Test locally（本地测试）
  ↓
Verify within an explicit scope（在明确范围内验证）
  ↓
Deploy through a compatible external runtime（通过兼容的外部 Runtime 部署）
```

开发者必须保留 Agent 原有框架和 Runtime 的所有权。DBOS 只接受其产生的身份、上下文、证据和验证引用，不接管模型或应用。

当前可运行的最短流程见 `docs/developer-quickstart.md`；完整登记、执行上下文、证据和验证目标流程仍见 `developer-quickstart-model.md`，后者不表示相关 API 已实现。

## 8. Reference Integration（参考集成）方向

以下均为未来生态方向，当前没有官方 Adapter（适配器）、兼容性保证或支持承诺：

| 生态 | 未来 DBOS Adapter 的职责 | 明确不负责 |
|---|---|---|
| LangChain | 把外部 Agent/Run 标识、工具调用摘要和回调证据映射到 DBOS 契约 | 替代 LangChain、改变链或模型行为 |
| CrewAI | 把 Crew、Agent、Task 和运行输出投影为受范围约束的实体与证据引用 | 接管 Crew 调度、角色设计或任务执行 |
| MCP | 把 MCP（Model Context Protocol，模型上下文协议）的 Server、Tool、Resource 与调用证据连接到 DBOS manifest 和上下文 | 把 MCP 暴露自动视为身份、能力、权限或验证 |

Adapter 必须位于 DBOS 核心边界之外，可独立版本化和替换。第三方 Adapter 不能修改 DBOS 身份、证据或验证事实真源。

通用 Adapter Input（适配器输入）、Transformation（转换）、Output（输出）、对象候选映射和第三方安全边界已经冻结为：

- `adapter-boundary-specification.md`；
- `adapter-object-mapping-model.md`；
- `adapter-security-boundary-rules.md`；
- `ADR-023-adapter-boundary.md`。

这些规范只建立 Translation Boundary（转换边界），不实现或批准 MCP、LangChain、CrewAI Adapter。所有候选表示仍必须经过现有 Validator，且不能自动登记、授权或修改 Evidence。

在通用边界之下，MCP 专属转换合同已经冻结为：

- `mcp-adapter-proposal.md`；
- `mcp-adapter-specification.md`；
- `mcp-tool-call-mapping-specification.md`；
- `mcp-resource-mapping-specification.md`；
- `mcp-context-mapping-specification.md`；
- `mcp-error-handling-specification.md`；
- `mcp-version-compatibility-policy.md`；
- `ADR-024-mcp-adapter-proposal.md`；
- `ADR-025-mcp-adapter-specification.md`。

这些文件定义字段、生命周期、错误、版本和安全规则。当前 `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]`、`MCP_ADAPTER_IMPLEMENTATION=false`、`MCP_MAPPING_INSTANCE_COUNT=0`；Specification（规范）存在不表示 MCP 兼容、连接或实现已经产生。

## 9. Extension Model（扩展模型）

第三方可以提出和实现：

- Adapter（适配器）：框架、Runtime 或协议映射；
- Validator（验证器）：在声明范围内执行可复现检查；
- Tooling（工具）：生成 manifest、检查引用、呈现证据包；
- Industry Extension（行业扩展）：增加行业词表和限制，不改变核心含义。

扩展必须声明 Owner、版本、范围、依赖、证据要求、失败模式、兼容矩阵和撤销路径。扩展不获得 Architecture Authority（架构权力），不得覆盖总章程、规范身份、证据历史、验证边界或 Permission 决策。

详细规则见 `developer-extension-model.md`。

## 10. Developer Trust Model（开发者信任模型）

DBOS 中的 trust（信任）是消费者基于可归因材料作出的限定判断，不是一个由 SDK 写入的全局布尔值。

未来 Trust Package 应至少包含：

- `package_version`
- `entity_identity_ref`
- `lifecycle_state_ref`
- `capability_boundary_refs`
- `execution_context_refs`
- `evidence_refs`
- `verification_refs`
- `limitations`
- `revocation_refs`
- `generated_at`

该字段集合只是 v0.1 概念模型，不是已发布 schema（模式）。Trust Package 的存在不等于认证、Permission、Authority、生产适用性或客户采用。

详细规则见 `developer-trust-model.md`。

## 11. 商业生态接口

DBOS 核心只提供开放、可检查、可替换的契约边界。未来商业参与者可以在核心之上提供：

- 企业集成和 Adapter 维护；
- 托管 Validator 或证据保存服务；
- 行业映射、合规准备和审计支持；
- 私有部署、运营支持和培训；
- 独立认证服务，但必须与 DBOS Validator 结果明确分离。

商业接口不得：

- 通过付费改变身份、能力、证据或验证历史；
- 把 Validator `PASS` 表述为独立认证；
- 把商业合同变成 DBOS Permission；
- 把私有扩展设为不可替代的 DBOS 架构权威；
- 在没有真实产品和合同证据时声明 SaaS、SLA、价格或市场可用性。

## 12. 开发前智能体推荐审查

当前 Codex（编码智能体）判断：

```text
recommend_for_bounded_identity_and_evidence_governance=true
recommend_for_research_or_local_integration_design=true
recommend_as_local_object_sdk_preview=true
recommend_common_adapter_boundary_specification=true
recommend_mcp_adapter_specification=true
recommend_autonomy_policy_specification=true
recommend_concrete_adapter_implementation=false
recommend_autonomy_policy_implementation=false
recommend_autonomy_enforcement=false
recommend_as_installable_sdk=false
recommend_as_production_agent_platform=false
recommend_as_managed_runtime=false
```

可向需要安全默认值、登记契约、证据引用、验证边界和本仓库内对象构造/序列化/验证的研究型或基础设施开发者推荐当前 DBOS。不能向需要可安装 SDK、生产 Runtime、官方 LangChain/CrewAI/MCP Adapter、权限引擎或认证服务的客户推荐当前版本。

不推荐的主要原因是开发者产品化缺口，而不是需要把 DBOS 改造成 Agent 应用：

1. 没有发布的 SDK 包和稳定公共 API；
2. 已有本地 Python（Python 编程语言）对象类型，但尚无发布的跨语言类型与兼容性测试矩阵；
3. 已有 canonical reference resolver specification（规范引用解析规范），但尚无 Resolver 实现；
4. 没有 Trust Package schema 和导出验证器；
5. 没有真实外部 Agent 的端到端接入证据；
6. 没有官方 Adapter 或生产支持承诺。
7. Autonomy Policy 当前只有提案，没有 Policy Schema、Authority/Approver 身份模型、撤销传播、策略评估器或 Runtime 不可绕过证据。

## 13. SDK 实现路线

本轮用户授权只覆盖第 4 项的本地 Minimal Object SDK Scaffold（最小对象 SDK 骨架）。它不授权可分发软件包、Reference Resolver（引用解析器）、远程 API、登记命令、执行功能或后续阶段；其余路线仍需分别审查和授权：

1. **Contract Freeze（契约冻结）**：以 `object-contract-specification.md`、五份类型契约、`object-error-semantics.md`、Validation Result Contract、`ADR-020-object-contract.md` 和 `ADR-022-validation-result-contract.md` 作为 v0.1 语义来源，并以 `schemas/*-object-schema.yaml`、`schema-version-policy.md` 和 `ADR-021-object-schema-governance.md` 作为机器可读结构来源；本地对象 Validator 已实现并通过合成测试，但跨语言兼容和发布仍需新的授权；
2. **Reference Resolution（引用解析）**：以 `canonical-reference-resolver-specification.md` 为基础，另行冻结 schema、Namespace、错误模型和只读 Source adapter；规范存在不表示 Resolver 已实现；
3. **Package and API Decision（包与 API 决策）**：以 `api-boundary-decision.md`、四份配套模型和 `ADR-019-api-boundary-decision.md` 为上限，另行确定命名、语言支持、同步/异步边界和幂等策略；当前边界规范不等于包或 API 已批准；
4. **Minimal Object SDK Scaffold（最小对象 SDK 骨架）**：`IMPLEMENTED_LOCAL_V0.1`；当前只实现五类数据表示、`dict/JSON` 序列化、既有 Validator 桥接和无自动修复错误包装。Registration Command（登记命令）、Reference Resolver（引用解析器）、执行引擎、Agent 与 Runtime 均不在骨架内；
5. **Trust Package Contract（信任包契约）**：建立 schema、验证器、限制和撤销表达；
6. **Local Reference Integration（本地参考集成）**：使用合成 fixture（测试夹具）证明边界，不声称生产兼容；
7. **External Pilot（外部试点）**：由一个既有 Agent 项目显式申请接入，保留人工授权和独立证据；
8. **Adapter Proposals and MCP Specification（适配器提案与 MCP 规范）**：公共边界已在 `adapter-boundary-specification.md` 与 `ADR-023-adapter-boundary.md` 冻结；MCP 的 Proposal、字段映射、错误和版本规则已由 `mcp-adapter-specification.md` 与 `ADR-025-mcp-adapter-specification.md` 冻结，但支持版本、fixture、代码、兼容证据和实现授权仍为空。LangChain、CrewAI 和 MCP Adapter 必须分别评估、分别授权，禁止绑定进核心 SDK。
9. **Autonomy Policy Proposal（自主策略提案）**：`autonomy-policy-specification.md`、对象模型、边界、模式比较和 `ADR-026-autonomy-policy.md` 只提出人工监督语义。进入 Schema、Validator、SDK、API 或 Runtime enforcement（运行时强制）前，必须重新审查 Authority、Permission、撤销、Evidence 和不可绕过边界。

每个阶段必须重新执行智能体推荐审查。只有缺口属于跨应用、开放、可替换的基础设施问题时，才允许申请进入 DBOS 核心。

## 14. 规范不变量

```text
DEVELOPER_KIT_NE_AGENT_FRAMEWORK=true
SPECIFICATION_NE_IMPLEMENTATION=true
IDENTITY_NE_AUTHENTICATION=true
CAPABILITY_NE_PERMISSION=true
EVIDENCE_NE_TRUTH=true
REFERENCE_NE_AUTHORITY=true
RESOLVER_NE_VERIFICATION=true
RESOLVER_NE_PERMISSION_SYSTEM=true
UNKNOWN_REMAINS_UNKNOWN=true
VERIFICATION_NE_CERTIFICATION=true
TRUST_PACKAGE_NE_TRUST_GRANT=true
ADAPTER_NE_ARCHITECTURE_AUTHORITY=true
API_NE_AUTHORITY=true
API_NE_PERMISSION=true
API_NE_AGENT_FRAMEWORK=true
API_NE_EXECUTION_ENGINE=true
AUTONOMY_NE_PERMISSION=true
AUTONOMY_NE_AUTHORITY=true
AUTONOMY_POLICY_NE_EXECUTION=true
RUNTIME_OWNERSHIP=EXTERNAL
SAEE_OWNERSHIP=EVOLUTION
CURRENT_API_IMPLEMENTATION=false
CURRENT_MINIMAL_OBJECT_SDK_SKELETON=true
CURRENT_INSTALLABLE_SDK_PACKAGE=false
CURRENT_DEVELOPER_QUICKSTART=RUNNABLE_LOCAL_PREVIEW_V0.1
CURRENT_EXTERNAL_USABILITY_EVIDENCE=false
CURRENT_ADAPTER_BOUNDARY_SPECIFICATION=FROZEN_V0.1
CURRENT_MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
CURRENT_MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
CURRENT_ADAPTER_IMPLEMENTATION=false
CURRENT_MCP_ADAPTER_IMPLEMENTATION=false
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
CURRENT_AUTONOMY_POLICY_SPECIFICATION=PROPOSED_V0.1
CURRENT_AUTONOMY_POLICY_IMPLEMENTATION=false
CURRENT_AUTONOMY_POLICY_OBJECT_INSTANCE_COUNT=0
CURRENT_COMMERCIAL_OFFER=false
```

## 15. Agent-readable（智能体可读）入口

按以下顺序读取：

1. `STRATEGIC_ALIGNMENT.md`
2. `developer-kit-specification.md`
3. `canonical-reference-resolver-specification.md`
4. `reference-namespace-model.md`
5. `reference-resolution-boundary-rules.md`
6. `ADR-017-canonical-reference-resolver.md`
7. `api-boundary-decision.md`
8. `api-responsibility-model.md`
9. `api-object-contract-model.md`
10. `api-error-model.md`
11. `ADR-019-api-boundary-decision.md`
12. `object-contract-specification.md`
13. `entity-object-contract.md`
14. `capability-object-contract.md`
15. `execution-object-contract.md`
16. `evidence-reference-object-contract.md`
17. `verification-object-contract.md`
18. `object-error-semantics.md`
19. `ADR-020-object-contract.md`
20. `schemas/common-object-schema.yaml`
21. `schemas/entity-object-schema.yaml`
22. `schemas/capability-object-schema.yaml`
23. `schemas/execution-object-schema.yaml`
24. `schemas/evidence-reference-object-schema.yaml`
25. `schemas/verification-object-schema.yaml`
26. `schema-version-policy.md`
27. `ADR-021-object-schema-governance.md`
28. `validator/validation_result_model.py`
29. `validator/object_schema_validator.py`
30. `validation-result-contract-specification.md`
31. `validation-error-object-model.md`
32. `validation-result-boundary-rules.md`
33. `ADR-022-validation-result-contract.md`
34. `sdk/README.md`
35. `sdk/objects/`
36. `sdk/serialization/`
37. `sdk/validation/`
38. `sdk/errors/`
39. `tests/sdk/`
40. `docs/developer-quickstart.md`
41. `examples/basic_object/`
42. `docs/developer-concepts.md`
43. `docs/integration-boundary.md`
44. `tests/developer_quickstart/`
45. `adapter-boundary-specification.md`
46. `adapter-object-mapping-model.md`
47. `adapter-security-boundary-rules.md`
48. `ADR-023-adapter-boundary.md`
49. `developer-quickstart-model.md`
50. `developer-trust-model.md`
51. `developer-extension-model.md`
52. `ADR-016-developer-ecosystem.md`
53. `entity_support/README.md`
54. `mcp-adapter-proposal.md`
55. `mcp-adapter-specification.md`
56. `mcp-tool-call-mapping-specification.md`
57. `mcp-resource-mapping-specification.md`
58. `mcp-context-mapping-specification.md`
59. `mcp-error-handling-specification.md`
60. `mcp-version-compatibility-policy.md`
61. `ADR-024-mcp-adapter-proposal.md`
62. `ADR-025-mcp-adapter-specification.md`
63. `autonomy-policy-specification.md`
64. `autonomy-policy-object-model.md`
65. `autonomy-boundary-rules.md`
66. `autonomy-mode-comparison.md`
67. `ADR-026-autonomy-policy.md`

本规范与本地工具层只创建对象表示、序列化和结构验证入口，不创建可安装或已发布 SDK、Agent、Runtime、Capability、Permission、Digital Organism（数字生命体）或商业产品，也不修改 DBA 或 SAEE。
