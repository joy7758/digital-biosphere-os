# DBOS Developer Quickstart Model v0.1（DBOS 开发者快速入门模型 v0.1）

状态：`BACKGROUND_TARGET_WORKFLOW_WITH_RUNNABLE_LOCAL_ENTRY`

适用对象：希望把既有 Agent（智能体）或数字实体接入 DBOS 治理链的开发者

当前限制：已经存在仓库内可导入的 Minimal Object SDK Skeleton（最小对象软件开发工具包骨架）和可运行快速入门，但不存在可安装的 DBOS SDK、稳定公共 API（应用程序接口）或官方 Adapter（适配器）。本文件保留完整未来接入流程；第一次本地使用应进入 `docs/developer-quickstart.md`。

## 1. 开始之前

开发者必须已经在 DBOS 之外拥有或负责一个明确的数字实体。DBOS 不负责创建该实体。

最低准备材料：

- Candidate（候选体）或既有实体的稳定外部引用；
- Owner（所有者）或责任主体引用；
- 可检查的 Repository（仓库）、Service（服务）或 Artifact（工件）来源；
- 拟申请的 DBOS entity type（实体类型）；
- 能力范围、限制、环境和副作用声明；
- 本地测试方法和预期证据来源；
- 如涉及执行，由开发者提供兼容的外部 Runtime（运行时）；
- 需要人工或独立治理决定时，提供相应授权与审查引用。

缺少任何关键来源时，字段应保持 `unknown`、`pending` 或 `null`，不得由 SDK 猜测。

## 2. 两条状态线

开发者必须区分 current path（当前可用路径）和 target path（未来目标路径）。

### 当前可用路径

当前 DBOS 提供 `sdk/` 中的五类不可变对象表示、序列化和 Validator（验证器）桥接；可运行入口位于 `docs/developer-quickstart.md` 与 `examples/basic_object/`。更深层登记支撑仍位于 `entity_support/`。这些本地能力不构成已发布 SDK、生产 Runtime 或线上服务。

### 未来目标路径

未来 SDK 计划把这些支撑契约封装成版本化、稳定、可安装的开发者接口。只有完成单独实现、测试、发布和兼容性审查后，才能给出安装命令或生产支持声明。

```text
CURRENT_SUPPORT_LAYER_AVAILABLE=true
LOCAL_OBJECT_SDK_SKELETON_AVAILABLE=true
RUNNABLE_DEVELOPER_QUICKSTART_AVAILABLE=true
INSTALLABLE_SDK_AVAILABLE=false
PUBLIC_API_STABLE=false
OFFICIAL_ADAPTER_AVAILABLE=false
PRODUCTION_RUNTIME_AVAILABLE=false
```

## 3. 目标接入流程

### Step 1 — Create Agent externally（在外部创建 Agent）

开发者使用自己的框架、模型和 Runtime 创建或维护 Agent。DBOS 不介入模型选择、推理、规划、记忆或工具调度。

预期输入：

- 外部主体引用；
- 所有者引用；
- 代码或服务来源；
- 版本信息。

DBOS 效果：`NONE`。

### Step 2 — Prepare registration package（准备登记包）

登记包应表达：

- Candidate ID 或外部稳定引用；
- 请求的 entity type；
- 身份证据引用；
- Owner 引用；
- 提案、审查和授权引用；
- 请求的生命周期上限。

当前支撑层对应：

- `entity_support/candidate/`
- `entity_support/registration/`
- `entity_support/authorization/`
- `entity_support/registration_store/`

Candidate Proposal（候选提案）、Review（复核）、Registration Request（登记请求）、Authorization（授权）和 Registration（登记）是不同记录。`APPROVED` Review 不等于已登记；`REGISTERED` 不等于 `ACTIVE`，也不自动等于 Agent 身份。

### Step 3 — Register（登记）

未来概念入口：

```python
# Concept only（仅为概念，不可直接调用）
receipt = dbos.register(candidate=..., authorization_ref=...)
```

安全结果只有两类：

- 成功：返回 `REGISTERED` 上限的实体记录引用和不可覆盖回执；
- 失败：返回结构化错误和失败回执，不创建部分身份。

登记不会授予 Capability（能力）、Permission（权限）、Runtime 或生产可用性。

### Step 4 — Declare Capability Boundary（声明能力边界）

开发者声明该实体可能做什么，以及明确不能做什么：

- capability name（能力名称）；
- scope（范围）；
- environment（环境）；
- inputs/outputs（输入/输出）；
- side effects（副作用）；
- constraints（限制）；
- risk level（风险等级）；
- evidence requirement（证据要求）。

初始状态必须是声明或未知，不能因代码、README、测试或框架名称自动升级为已验证或已授权。

```text
DECLARATION_NE_VERIFICATION=true
VERIFICATION_NE_AUTHORIZATION=true
AUTHORIZATION_NE_PERMISSION=true
```

### Step 5 — Test Locally（本地测试）

开发者在自己的环境中运行测试。DBOS 只接收可归因结果和上下文引用。

最低要求：

- 锁定软件版本；
- 记录依赖与配置摘要；
- 明确输入和预期输出；
- 保留失败结果；
- 不把本地测试通过描述为独立验证、认证或生产就绪。

### Step 6 — Execute Through DBOS Context（通过 DBOS 上下文连接外部执行）

未来概念入口：

```python
# Concept only（仅为概念，不可直接调用）
result_ref = dbos.execute(
    entity_ref=...,
    runtime=external_runtime,
    context=...,
)
```

外部 Runtime 负责真正执行。DBOS 负责检查：

- 实体引用是否可解析；
- 上下文是否绑定环境、输入、依赖与配置；
- 执行请求是否在声明和授权范围内；
- 结果是否可以形成追加式引用；
- 缺失条件时是否失败关闭。

当前 `entity_support/execution_context_integration.py` 只支持只读上下文链接，不会启动 Runtime 或任务。

### Step 7 — Generate Evidence Reference（生成证据引用）

未来概念入口：

```python
# Concept only（仅为概念，不可直接调用）
evidence_ref = dbos.evidence(
    execution_ref=...,
    source=...,
    digest=...,
)
```

Evidence Reference（证据引用）必须记录来源、范围、摘要算法、完整性状态和限制。它只连接规范 Evidence 系统，不复制事实真源。

当前 `entity_support/evidence_reference.py` 只允许 `UNKNOWN/PENDING` 完整性状态；文件存在不能自动提升等级。

### Step 8 — Verify（验证）

未来概念入口：

```python
# Concept only（仅为概念，不可直接调用）
verification_ref = dbos.verify(
    claim_ref=...,
    evidence_ref=...,
    verifier_ref=...,
    scope=...,
)
```

验证必须声明 Verifier（验证主体）、方法、环境、输入摘要、决定、时间和限制。当前支撑引用只允许 `PENDING/V0`；真正升级必须遵守 C/E/V 等级、独立性和证据上限。

验证不生成 Permission、Capability Assignment（能力分配）或 Certification（认证）。

### Step 9 — Export Trust Package（导出信任包）

未来 Trust Package（信任包）把可解析的身份、生命周期、能力边界、执行上下文、证据和验证引用组合成一个消费包。

消费者仍需独立判断：

- 引用是否可访问；
- 证据是否适用于自己的环境和目的；
- Verifier 是否满足独立性要求；
- 是否存在撤销、过期或范围冲突；
- 是否需要额外的人类、法律、商业或安全决定。

当前没有 Trust Package schema、导出器或发布格式。

## 4. 目标状态机

以下流程表示累积闸门，不是自动状态机：

```text
External Agent/Application（外部 Agent/应用）
  ↓ candidate proposal
PROPOSED
  ↓ review + registration authorization
REGISTERED
  ↓ identity/capability/evidence verification
VERIFIED
  ↓ separate activation authorization
ACTIVE
```

任何上游记录被撤销、过期、范围不匹配或无法解析时，下游动作必须停止。历史记录继续保留。

## 5. 框架接入模型

### LangChain

开发者继续使用 LangChain 定义模型、链、Agent、Tool 和 Callback（回调）。未来 Adapter 只映射：

- 外部 run/agent 标识；
- 工具调用与结果摘要；
- 环境、输入和输出引用；
- Evidence 与 Verification 引用。

### CrewAI

开发者继续使用 CrewAI 定义 Crew、角色、Task（任务）和 Process（流程）。未来 Adapter 只映射受治理实体、任务上下文和执行证据，不改变 Crew 调度。

### MCP

开发者继续使用 MCP（Model Context Protocol，模型上下文协议）暴露 Tool、Resource（资源）或 Prompt（提示）。未来 Adapter 只建立 manifest、身份、上下文和调用证据引用。MCP Server 存在不证明 Agent 身份；Tool 可调用不证明 Capability 已验证或 Permission 已授予。

三类 Adapter 均为独立、可替换扩展，不是 DBOS 核心依赖。

## 6. 失败关闭清单

出现以下任一情况时，SDK 必须返回结构化失败，不得猜测：

- 身份来源不存在或不一致；
- Owner 或责任主体不明确；
- Candidate、Authorization、Registration 引用链断裂；
- 请求生命周期超过授权上限；
- Capability、Permission 和 Authority 被混为同一状态；
- Execution Context 缺少环境、输入或依赖；
- Evidence 来源、摘要或范围缺失；
- Verifier、方法或独立性材料不足；
- Adapter 请求修改 DBOS 规范身份或历史证据；
- SAEE 评价被用作 DBOS Permission 或自动身份变更。

## 7. 开发者完成标准

未来一个外部接入只有在以下材料都真实存在时，才可以称为“完成接入”：

- 有可解析的规范实体引用；
- 生命周期状态与授权链一致；
- Capability Boundary 已声明，且没有隐式 Permission；
- 本地测试材料与环境范围明确；
- 外部 Runtime 与 DBOS Context 的责任边界明确；
- Evidence Reference 可解析且限制清晰；
- Verification Record 真实存在且等级未越过证据上限；
- Trust Package 可验证、可撤销、可解释；
- 没有把 SDK、Adapter 或 Validator 误报为 Agent、认证机构或 Architecture Authority（架构权力）。

## 8. 当前下一步

当前开发者可以运行 `docs/developer-quickstart.md` 中的三个本地命令，但不应执行虚构的软件包安装或 API 命令。下一阶段是另行审查 Reference Implementation（参考实现）；它必须使用真实、受控且明确授权的外部项目，不能从合成示例推导生产兼容或外部采用。

关联文档：

- `developer-kit-specification.md`
- `docs/developer-quickstart.md`
- `docs/developer-concepts.md`
- `docs/integration-boundary.md`
- `examples/basic_object/README.md`
- `developer-trust-model.md`
- `developer-extension-model.md`
- `ADR-016-developer-ecosystem.md`
