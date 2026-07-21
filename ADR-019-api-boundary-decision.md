# ADR-019: DBOS API Boundary Decision v0.1（DBOS 应用程序接口边界决策 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-20`

决策范围：未来 DBOS 开发者接口的职责、对象和错误边界

## 1. Context（背景）

DBOS 已建立 Developer Kit Specification（开发者工具包规范）、Canonical Reference Resolver Specification（规范引用解析规范）和 Documentation Evolution Evidence（文档演化证据）。`entity_support/` 也提供身份、生命周期、能力、执行上下文、证据与验证的本地记录支撑。

下一阶段需要让开发者调用这些基础设施概念，但如果直接把本地函数包装成公共 API，DBOS 容易被误解为 Agent Framework、Runtime、Permission Engine 或 SAEE 实现。

尤其是既有概念名称 `dbos.register(...)` 与 `dbos.execute(...)`：前者可能被误读为调用即签发规范身份，后者可能被误读为 DBOS 负责模型或 Agent 执行。当前事实并不支持这些语义。

## 2. Problem（问题）

需要在实现之前回答：

1. 哪些开发者操作属于 DBOS 基础设施接口？
2. 哪些治理决定不能由 API 调用产生？
3. 如何交换对象而不把引用变成权力？
4. 如何表达未知、非法、受限、冲突和版本错误？
5. 如何保持 Agent Framework、External Runtime、DBOS 与 SAEE 职责分离？
6. 哪些概念名称必须在 SDK 实现前重新冻结？

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户已有 Agent Framework 与 Runtime，希望增加可审计身份、生命周期、证据和验证引用，智能体是否会推荐 DBOS API？

结论：**推荐本次 API Boundary Specification（接口边界规范），暂不推荐任何可安装 API 或 SDK。**

推荐规范的原因：

- 它解决开放基础设施最容易发生的职责漂移；
- 它让开发者和编码智能体能确定性区分查询、引用、观察、连接与治理效果；
- 它复用既有 Canonical Reference、Evidence、Verification 和 fail-closed（失败关闭）边界；
- 它明确兼容外部 Agent Framework，而不是替代它；
- 它为未来最小 SDK 提供可审查的前置契约。

暂不推荐实现或客户使用的原因：

1. 当前没有冻结的 API Schema、transport、versioning（版本控制）或兼容政策；
2. `register` 和 `execute` 的早期概念名称存在 Authority 与 Execution Engine 歧义；
3. Authentication、API access control、privacy（隐私）和最小披露尚未设计；
4. Error Object、Object Contract 与幂等语义尚未通过实现验证；
5. Canonical Reference Resolver 尚未实现；
6. 没有外部 Agent、跨语言 SDK 或生产接入证据。

修正分解：

- 先冻结七类 API 职责；
- 把登记拆为申请、独立决定、持久化和回执，不允许“调用即注册”；
- 把执行收窄为 Execution Context 与 inert record（惰性记录），不允许模型推理；
- 使用 reference-first（引用优先）对象模型；
- 建立五类可解释、失败关闭的错误；
- 通过 conformance（符合性）和安全审查后才评估最小 SDK。

智能体对当前结果的认可范围：`RECOMMEND_SPECIFICATION_ONLY`。这不是对 API 实现、生产可用性或商业产品的认可。

## 4. Decision（决策）

DBOS 接受 API Boundary Model v0.1，冻结以下七类职责：

1. Identity API：身份引用和身份连续性观察；
2. Lifecycle API：生命周期状态查询；
3. Capability API：能力边界声明和查询；
4. Execution Context API：执行上下文与惰性执行记录引用；
5. Evidence API：证据引用和追加式关系连接；
6. Verification API：验证请求与结果引用；
7. Reference Resolver API：规范引用解析。

API 只允许 `READ/RESOLVE/OBSERVE/LINK` 四类效果。任何 `COMMAND/DECIDE/EXECUTE/GRANT/EVOLVE` 能力均不在本决策范围内。

## 5. Object Decision（对象决策）

未来 API 采用 reference-first object contract（引用优先对象契约）：

- Entity Object；
- Capability Object；
- Execution Object；
- Evidence Reference Object；
- Verification Object。

对象必须携带 Source、Version、Status 与 Limitations，并固定 Authority、Permission、Runtime 和 Truth effect 为 `NONE`。

## 6. Error Decision（错误决策）

未来 API 使用以下五类错误：

- `UNKNOWN`；
- `INVALID`；
- `UNAUTHORIZED_REFERENCE`；
- `CONFLICT`；
- `VERSION_MISMATCH`。

错误必须可机器检查、可解释、失败关闭且不泄露敏感信息。HTTP status code（HTTP 状态码）和语言异常类型本轮不冻结。

## 7. Separation Decision（职责分离决策）

```text
Agent Framework = reasoning + planning + tool orchestration
External Runtime = model + tool + task execution
DBOS API = identity + lifecycle + context + evidence + verification references
SAEE = evolution interpretation
```

中文：Agent Framework 负责推理、规划与工具编排；External Runtime 负责模型、工具和任务执行；DBOS API 负责身份、生命周期、上下文、证据与验证引用；SAEE 负责演化解释。

DBOS 不通过 API 接管任何外部 Agent 或 Runtime，也不通过 API 实现 Fitness、Selection 或 Evolution Algorithm。

## 8. Alternatives Considered（备选方案）

### A. 直接公开 `entity_support/` 的 Python 函数

拒绝。现有函数是本地支撑和测试边界，没有公共版本、传输、安全或兼容契约。

### B. 建立完整 CRUD API（增删改查接口）

拒绝。通用 Update/Delete（更新/删除）会破坏追加式证据和生命周期治理，并可能让 API 成为 Authority。

### C. 建立 Agent Framework API

拒绝。模型、推理、规划、记忆和工具调用不属于 DBOS。

### D. 建立中央 Database API（数据库接口）

拒绝。它会复制 Entity、Evidence、Verification 和 Authorization 的规范 Source。

### E. 建立 reference-first、observation-first（引用优先、观察优先）的受限 API

接受。它能开放基础设施语义，同时保留既有 Source 和治理所有权。

## 9. Consequences（影响）

正向影响：

- 开发者获得稳定的职责分类；
- 外部 Agent Framework 可以保持独立；
- 引用、状态、证据与验证不会静默变成权力；
- 错误具有可解释、可机器检查的语义；
- 最小 SDK 可以围绕边界生成，而不是复制整个 DBOS。

成本与限制：

- 不能把当前 Python 函数直接宣传为 API；
- 登记、状态转换和验证决定需要独立治理流程；
- 调用方需要显式处理 Source、Version、`UNKNOWN` 和冲突；
- 初始 SDK 会比通用 Agent SDK 更窄；
- 当前仍没有可安装包、端点或外部兼容承诺。

## 10. Implementation Gates（实现闸门）

任何 API 或 SDK 实现需要新的明确授权，并依次完成：

1. 冻结五类 Object Contract 与 Error Object schema；
2. 冻结 Namespace、Version、idempotency（幂等）和 compatibility policy（兼容政策）；
3. 决定本地库与远程接口边界，不默认创建 Server（服务器）；
4. 实现只读 Canonical Reference Resolver 的最小原型；
5. 为七类 API 建立正向、负向和跨版本符合性测试；
6. 验证 Agent/Runtime/Permission/SAEE effect 全部为 `NONE`；
7. 完成安全、隐私、错误泄露和重放审查；
8. 再决定是否创建 Minimal SDK Skeleton（最小 SDK 骨架）。

## 11. Current State（当前状态）

```text
API_BOUNDARY_SPECIFICATION=ACCEPTED
API_OBJECT_SCHEMA=NOT_DEFINED
API_ERROR_SCHEMA=NOT_DEFINED
API_IMPLEMENTATION=NOT_STARTED
SDK_IMPLEMENTATION=NOT_STARTED
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
SAEE_MODIFIED=false
```

本 ADR 不创建代码、API、SDK、Agent、Runtime、Permission 或 SAEE 实现，不修改 DBA 或 SAEE 仓库。
