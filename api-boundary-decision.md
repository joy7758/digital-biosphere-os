# DBOS API Boundary Model v0.1（DBOS 应用程序接口边界模型 v0.1）

状态：`SPECIFICATION_ONLY`

实现状态：`NOT_STARTED`

API 状态：`NOT_CREATED`

规范角色：Developer Infrastructure Architecture Specification（开发者基础设施架构规范）

## 1. Purpose（目的）

DBOS API Boundary（DBOS 应用程序接口边界）定义未来开发者接口可以读取、声明、连接和观察什么，以及它不得决定、执行或授予什么。

DBOS API 是 infrastructure interface（基础设施接口），不是：

- Agent Framework API（智能体框架接口）；
- Model API（模型接口）；
- Tool Calling API（工具调用接口）；
- Chat API（聊天接口）；
- Execution Engine（执行引擎）；
- Permission Engine（权限引擎）；
- SAEE evaluation interface（SAEE 评价接口）。

本规范冻结职责边界，不冻结 endpoint（端点）、transport（传输协议）、语言绑定、URL、函数名称或 SDK（软件开发工具包）实现。

## 2. Current Evidence Boundary（当前证据边界）

当前 `entity_support/` 已证明的上限是：

- Entity registration support（实体登记支撑）只构造 `PROPOSED` mapping（映射），不写规范 Registry（登记表）；
- Lifecycle support（生命周期支撑）只验证并构造 transition record（转换记录），不应用状态；
- Capability boundary（能力边界）可以表达 `DECLARED/VERIFIED/AUTHORIZED` 记录，但 `permission_effect=NONE`；
- Execution record（执行记录）只能处于 `CREATED`，不会运行任务、工具、模型或 Runtime（运行时）；
- Execution Context integration（执行上下文集成）只连接调用方提供的既有上下文；
- Evidence 与 Verification 支撑只创建引用，安全默认值保持 `UNKNOWN/PENDING/V0`；
- Registration persistence（登记持久化）需要调用方显式配置 Store（存储）和独立 Authorization（授权）来源；
- Canonical Reference Resolver（规范引用解析器）和公开 API 当前均未实现。

未来 API 不得把这些事实扩大为已存在的远程服务、公共端点、生产 Registry 或自动治理系统。

## 3. Core Principles（核心原则）

### 3.1 API ≠ Authority（接口不等于权力）

API 调用、成功响应、对象创建请求或引用解析都不产生治理权力。Authority 必须来自可归因、可验证、范围明确的独立治理记录。

### 3.2 API ≠ Permission（接口不等于权限）

API 可以读取或原样返回 Permission 相关引用，但不能创建、推导、扩大或撤销 Permission。访问 API 的技术访问控制也不等于数字实体的 DBOS Permission。

### 3.3 API ≠ Execution Engine（接口不等于执行引擎）

DBOS 可以记录 Execution Object（执行对象）和连接 Execution Context（执行上下文），但 Agent reasoning（智能体推理）、Model inference（模型推理）、planning（规划）、tool invocation（工具调用）和任务执行属于外部 Agent Framework 与 Runtime。

### 3.4 API Boundary preserves DBOS/SAEE separation（接口边界保持 DBOS 与 SAEE 分离）

DBOS API 提供身份、状态、证据和验证引用。它不计算 Fitness（适应度）、执行 Selection（选择）、生成 Evolution Recommendation（演化建议）或代表 SAEE 作出解释。

### 3.5 Unknown remains unknown（未知保持未知）

缺少规范 Source（来源）、版本、证据、授权或唯一目标时，API 必须返回显式错误或未知状态，不能从路径、名称、框架类型或相似字段推断。

### 3.6 Requests do not equal decisions（请求不等于决定）

未来 API 可以接受 declaration（声明）、link（连接）或 review request（复核请求），但接收请求只形成待处理记录或引用。它不能把请求状态自动升级为治理决定。

## 4. API Categories（接口分类）

下列七类是 v0.1 的职责分类，不是已经发布的 endpoint 或函数名。

### 4.1 Identity API（身份接口）

负责：

- 接收和返回 Entity Reference（实体引用）；
- 读取规范 Entity Object（实体对象）及其 Source、Version 和状态；
- 连接 Candidate、Registration 与 Entity 的既有身份连续性引用；
- 对缺失或冲突身份保持 `UNKNOWN` 或显式错误。

不负责：

- 创建 Agent、Runtime 或 Digital Organism（数字生命体）；
- 认证人、组织、密钥或账户；
- 仅凭 API 调用签发 canonical identity（规范身份）；
- 激活实体或合并不同实体身份。

当前边界：公开 Registration Command API（登记命令接口）尚未批准。`entity_support/` 中的登记函数不能直接视为公共 Identity API。

### 4.2 Lifecycle API（生命周期接口）

负责：

- 查询实体已记录的 lifecycle state（生命周期状态）；
- 返回状态来源、版本、观察时间和 transition references（转换引用）；
- 对冲突状态返回 `CONFLICT`；
- 对版本不一致返回 `VERSION_MISMATCH`。

不负责：

- 自动应用状态转换；
- 把 `REGISTERED` 自动升级为 `VERIFIED` 或 `ACTIVE`；
- 通过查询、缓存或调用次数推导生命周期。

### 4.3 Capability API（能力接口）

负责：

- 接收 Capability Boundary Declaration（能力边界声明）；
- 查询能力名称、范围、限制、风险、声明状态及相关证据；
- 保持 Claim、Verification、Authorization 和 Permission 分离；
- 对未经验证的能力保持 `DECLARED/UNKNOWN/PENDING`。

不负责：

- 分配或执行能力；
- 从声明、代码存在或工具清单推导能力已验证；
- 创建 Permission；
- 让 `AUTHORIZED` Capability Record 代表某次任务已获准执行。

### 4.4 Execution Context API（执行上下文接口）

负责：

- 记录或查询调用方提供的 Execution Context Reference；
- 连接既有 Entity、Task、Input、Output、Environment 和 Dependency 引用；
- 返回 inert Execution Object（惰性执行对象）和明确状态；
- 保留外部 Runtime ownership（运行时所有权）。

不负责：

- 创建或启动 Runtime；
- 调用模型、工具或进程；
- 规划、调度、重试或终止 Agent 任务；
- 把 `CREATED` 记录声明为已执行或成功。

### 4.5 Evidence API（证据接口）

负责：

- 创建或查询指向既有 Evidence Source（证据来源）的引用；
- 把 Evidence Reference 与 Entity、Execution、Event 或 Claim 连接；
- 返回 Source、Digest（摘要）、Scope（范围）、Integrity Status（完整性状态）和限制；
- 保留 append-only provenance（只追加来源链）。

不负责：

- 修改或复制规范 Evidence 的事实真源；
- 仅凭文件存在、摘要匹配或 API 成功提升 E 等级；
- 把 Evidence 声明为 Truth（真相）；
- 删除或覆盖历史证据。

### 4.6 Verification API（验证接口）

负责：

- 创建受范围约束的 Verification Request Reference（验证请求引用）；
- 查询 Verification Record、Run、Method、Verifier、Decision 和 Limitation 引用；
- 返回当前可证明的验证等级与状态；
- 保持当前支撑层安全默认值 `PENDING/V0`。

不负责：

- 因请求已接收而生成 `pass`；
- 把 Verification 变成 Review Approval、Certification（认证）、Capability Assignment 或 Permission；
- 伪造独立验证者或验证材料。

### 4.7 Reference Resolver API（规范引用解析接口）

负责：

- 验证 Reference Object（引用对象）结构；
- 在显式 Namespace、Version、Source 和 Type 中执行只读 lookup（查找）；
- 返回 `RESOLVED/AMBIGUOUS/UNKNOWN/INVALID`；
- 保留 Source ownership（来源所有权）、provenance 和限制。

不负责：

- 创建 Identity、Authorization、Permission、Evidence 或 Verification；
- 从 `RESOLVED` 推导 verified、authorized、active 或 trusted；
- 建立第二套中央事实数据库；
- 对未知目标进行工作区猜测或自动登记。

## 4A. Proposed Autonomy Policy Read Boundary（拟议自主策略读取边界）

`autonomy-policy-specification.md` 提出未来接口可以只读返回适用 Autonomy Policy（自主策略）及其 Entity、Capability、Permission、Scope（范围）、Constraint（约束）、Approval（批准）、Evidence、版本、过期和撤销引用。

该边界当前不是第八类已冻结 API，也不批准 endpoint（端点）或实现。未来若进入新的 API 版本，只允许现有操作类别：

- `READ`：读取显式 Source 中的 Policy 表示；
- `RESOLVE`：解析 Policy、Entity、Capability、Permission 和 Authority Reference（权力引用）；
- `OBSERVE`：返回 Policy 当前来源声明的状态、版本和限制；
- `LINK`：追加待处理 Policy/Approval/Evidence 引用，不应用决定。

未来 API 可以返回 Policy 声明的 `APPROVAL_REQUIRED/ALLOW_WITHIN_SCOPE/BLOCKED/UNKNOWN/CONFLICT`，但不能：

- 创建、激活、扩大、续期或撤销 Policy Authority；
- 从 Mode（模式）生成 Permission、Capability Grant（能力授予）或 Authorization；
- 把 `FULL_AUTONOMY_WITHIN_SCOPE` 解释为无限权限；
- 创建 Agent、Runtime（运行时）、Execution（执行）或 Evidence；
- 修改 Identity（身份）、历史 Evidence 或 SAEE；
- 替代外部 Runtime 的执行前 Permission、Approval 和撤销检查。

## 5. Operation Classes（操作类别）

未来 API 操作必须属于以下四类之一：

| 操作类别 | 允许效果 | 固定边界 |
|---|---|---|
| `READ` | 读取显式 Source 中的受范围记录 | 不改变状态 |
| `RESOLVE` | 返回规范引用解析结果 | 不验证真实性、不授予权力 |
| `OBSERVE` | 返回带来源和时间的状态观察 | 不应用 Lifecycle 转换 |
| `LINK` | 追加引用关系或待处理声明 | 不创建被引用事实、不提升等级 |

任何未来 `COMMAND`、`DECIDE`、`EXECUTE`、`GRANT` 或 `EVOLVE` 类接口都不在 v0.1 边界内，必须经过新的独立架构决策。

## 6. Request and Response Effects（请求与响应效果）

每个未来响应都必须显式表达：

```text
authority_effect=NONE
permission_effect=NONE
agent_creation_effect=NONE
runtime_effect=NONE
model_execution_effect=NONE
saee_evaluation_effect=NONE
```

响应可以返回 Source 原有声明，但必须标为 source-asserted（来源声明），不能改写为 DBOS API 决定。

## 7. Existing Conceptual Names（既有概念名称）

`developer-kit-specification.md` 中的 `dbos.resolve(...)`、`dbos.register(...)`、`dbos.execute(...)`、`dbos.evidence(...)` 和 `dbos.verify(...)` 只是早期概念名称，不是已冻结 API。

本决策明确：

- `resolve` 可继续作为未来只读解析方向；
- `register` 不能表示调用即获得规范身份，必须拆为申请、独立决定、持久化和回执；
- `execute` 不能表示 DBOS 执行 Agent，只能表示 Execution Context 与记录边界；
- `evidence` 只能创建或查询引用，不创建 Truth；
- `verify` 只能请求或读取限定验证，不自动产生 `pass`。

未来命名必须先通过 contract freeze（契约冻结），不得直接把这些概念名称实现为公共接口。

## 8. Security and Privacy Boundary（安全与隐私边界）

未来实现至少必须：

- 使用显式 Source allowlist（来源允许列表）；
- 默认拒绝路径越界和任意网络读取；
- 不在错误信息中泄露 Secret、Token、Credential 或 Evidence 正文；
- 区分 API access control（接口访问控制）与 DBOS Permission；
- 保留版本、请求标识、来源和可审计限制；
- 对重放、重复请求和冲突失败关闭；
- 不因 Cache（缓存）命中改变规范 Source 状态。

## 9. Non-goals（非目标）

本层不定义：

- HTTP、RPC、GraphQL 或其他传输协议；
- endpoint path（端点路径）、port（端口）或 deployment（部署）；
- Authentication Provider（认证提供者）；
- Database、Queue（队列）或 Event Bus（事件总线）；
- Agent loop（智能体循环）、模型调用、工具执行或聊天会话；
- API 定价、SLA（服务等级协议）或商业合同；
- SAEE 的 Fitness、Selection 或 Evolution Algorithm（演化算法）。
- Autonomy Policy evaluator（自主策略评估器）、Policy Authority provider（策略权力提供者）或 Runtime enforcement（运行时强制）。

## 10. Invariants（不变量）

```text
DBOS_ROLE=INFRASTRUCTURE
API_NE_AUTHORITY=true
API_NE_PERMISSION=true
API_NE_AGENT_FRAMEWORK=true
API_NE_EXECUTION_ENGINE=true
API_NE_MODEL_API=true
REFERENCE_NE_TRUTH=true
VERIFICATION_NE_PERMISSION=true
AUTONOMY_NE_PERMISSION=true
AUTONOMY_NE_AUTHORITY=true
AUTONOMY_POLICY_NE_EXECUTION=true
DBOS_NE_SAEE=true
CURRENT_API_IMPLEMENTATION=false
CURRENT_SDK_IMPLEMENTATION=false
CURRENT_AUTONOMY_POLICY_API=false
```

## 11. Related Documents（关联文档）

- `api-responsibility-model.md`
- `api-object-contract-model.md`
- `api-error-model.md`
- `ADR-019-api-boundary-decision.md`
- `developer-kit-specification.md`
- `canonical-reference-resolver-specification.md`
- `documentation-evolution-evidence-specification.md`
- `entity_support/README.md`
- `autonomy-policy-specification.md`
- `autonomy-policy-object-model.md`
- `autonomy-boundary-rules.md`
- `autonomy-mode-comparison.md`
- `ADR-026-autonomy-policy.md`

本规范不创建 API、SDK、Agent、Runtime、Capability、Permission、Digital Organism 或 SAEE 评价结果。
