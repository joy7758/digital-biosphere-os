# ADR-017: Canonical Reference Resolver v0.1（规范引用解析器 v0.1）

ADR（Architecture Decision Record，架构决策记录）状态：`ACCEPTED_FOR_SPECIFICATION`

实现授权：`NOT_AUTHORIZED`

日期：`2026-07-20`

决策范围：跨模块、Adapter（适配器）与 Developer Extension（开发者扩展）的引用语义

## 1. Context（背景）

DBOS 已形成多类真实引用：

- `registry/entities.yaml` 中的 `entity_id` 与 `dbio://...` canonical ID（规范 ID）；
- Candidate Proposal、Review 和 Registration Request 中的 `candidate_id`、`request_id` 与 mapping reference（映射引用）；
- Authorization Record 中的 `authorization_id`、decision、issuer 和 revocation references（撤销引用）；
- Registration Execution 中的 `dbio:entity:registration:<digest>`、`dbio:registration:<digest>` 与 receipt（回执）；
- Execution、Context、Evidence 和 Verification 支撑层中的多个 opaque reference（不透明引用）。

这些模块均有局部安全边界，但没有统一声明 Reference Type、Namespace（命名空间）、Version、Source 和解析结果的契约。Developer Kit（开发者工具包）和第三方 Adapter 开放后，裸字符串可能被不同开发者解释成不同对象，甚至把“查到记录”误写为“身份已验证”“授权有效”或“权限已授予”。

## 2. Problem（问题）

需要一个统一语义层回答：

1. 这个引用属于哪种对象？
2. 由哪个 Namespace 和 Source 拥有其含义？
3. 请求的是哪个版本？
4. 是否唯一定位到一个记录？
5. 如果缺失、冲突或非法，如何确定性表达？
6. 解析结果明确不产生哪些治理效果？

该问题不能通过添加中央 Database（数据库）、默认目录搜索或模型推断解决，因为这些方式会制造第二套事实真源或把未知静默升级为事实。

## 3. Pre-development Agent Consultation（开发前智能体咨询）

问题：如果潜在客户需要把既有 Agent、Adapter 或 Evidence system（证据系统）接入 DBOS，智能体是否会推荐先建立 Canonical Reference Resolver？

结论：**推荐规范，暂不推荐实现或生产使用。**

推荐原因：

- 它解决 Developer Kit 已确认的跨模块基础设施缺口；
- 可被不同 Agent Framework、Runtime 和 Extension 复用；
- 可通过开放 Reference Object、Namespace 和 Resolution Result 契约表达；
- 能保留 `unknown/pending`，并防止 Permission、Capability 和 Lifecycle 越权推导；
- 不要求 DBOS 创建 Agent、模型或业务应用。

暂不推荐实现的原因：

- Reference Object 和 Namespace schema 尚未冻结；
- Candidate、Authorization、Registration 和 Execution 没有统一默认 live Source；
- 错误模型、Cache、安全、隐私和远程 Source 策略尚未实现或验证；
- 还没有 Adapter conformance（适配器符合性）和真实外部接入证据。

## 4. Decision（决策）

DBOS 采用一个 read-only semantic resolution layer（只读语义解析层）规范，包含：

1. 七种核心 Reference Type：Entity、Candidate、Authorization、Registration、Execution、Evidence、Verification；
2. 六字段 Reference Object：`reference_id`、`reference_type`、`namespace`、`version`、`source`、`status`；
3. 三类 Namespace：DBOS、External、Extension；
4. 四种 Resolution Result：`RESOLVED`、`AMBIGUOUS`、`UNKNOWN`、`INVALID`；
5. 精确、显式、失败关闭的查找顺序；
6. Source ownership（来源所有权）保留；
7. Reference、Authority、Verification 和 Permission 严格分离；
8. Unknown preservation（未知保留）；
9. External/Extension Namespace 不能覆盖 `dbio` 规范含义；
10. Resolver 不持久化业务对象、不签发 ID、不修改状态。

## 5. Resolution Meaning（解析含义）

`RESOLVED` 的规范含义限定为：

> 在声明的 Namespace、Reference Type、Version 和 Source 中找到唯一、精确匹配的记录。

它不表示：

- 记录真实；
- 身份已认证或验证；
- Authorization 对当前动作有效；
- Permission 已授予；
- Evidence 等级充分；
- Verification 为 `pass`；
- Entity 为 `ACTIVE`、Agent 或 Runtime；
- 客户、商业或生产环境已采用。

## 6. Namespace Decision（命名空间决策）

保留 `dbio` 作为 DBOS Namespace，并承认当前两类合法但不同的格式：

```text
dbio://<entity_type>/<name>/<version>
dbio:<record_type>:<opaque-id>
```

外部系统必须使用：

```text
external:<authority>
```

第三方扩展必须使用：

```text
extension:<extension-id>
```

不提供隐式默认 Namespace。裸 ID 必须由上层显式 contract（契约）包装；不能因运行位置在 DBOS 仓库内而归入 `dbio`。

## 7. Source Decision（来源决策）

Resolver 不建立中央数据存储。每种 Reference Type 继续使用其规范 Source：

- Entity：`registry/entities.yaml` 或明确 successor；
- Candidate：调用方提供的 Candidate records/store；
- Authorization：调用方显式配置的 append-only store（只追加存储）；
- Registration：Registration/Receipt store；
- Execution：明确的 Execution record source；
- Evidence：既有 DBOS Evidence system 或已登记外部 Source；
- Verification：Verification records/runs 或已登记外部 Source。

Source 缺失时返回 `UNKNOWN`。Resolver 规范不通过自动创建存储或全局扫描补齐缺口。

## 8. Alternatives Considered（备选方案）

### A. 继续使用裸字符串和模块内局部验证

拒绝。局部字段验证无法防止跨模块类型碰撞、Namespace 覆盖和 Adapter 语义分叉。

### B. 建立一个中央 Reference Database

拒绝。它会复制 Entity、Evidence、Verification 和 Authorization 事实真源，产生同步、权力和历史一致性问题。

### C. 把所有对象强制迁移为单一 URI/DID

拒绝。当前 `dbio://` Entity ID、不透明登记 ID 和外部系统 ID 具有不同 Owner 和生命周期。强制迁移会重写身份或伪造等价关系。

### D. 让每个 Adapter 自己定义 Resolver

拒绝。它会产生不同的 unknown、collision、version 和 permission 语义，破坏 Developer Kit 互操作性。

### E. 采用统一 contract + type-specific source adapter（统一契约加类型专用来源适配器）

接受。统一 Reference Object、Namespace、Result 和边界，同时保留各规范 Source 所有权。

## 9. Consequences（影响）

正向影响：

- Developer、Adapter 和 Extension 使用同一引用语义；
- `unknown`、冲突和非法输入有确定性结果；
- DBOS 规范 ID 与外部 ID 不再因字符串相似被合并；
- Reference lookup（引用查找）与 Verification、Authorization、Permission 分离；
- Trust Package（信任包）可以携带可解释 Resolution Result；
- 未来 SDK 可以提供稳定的引用入口而不成为 Database 或 Identity Provider（身份提供者）。

成本与限制：

- 每个引用需要显式 Type、Namespace、Version 和 Source；
- 既有裸引用需要 Adapter 包装，不能静默默认；
- Source unavailable（来源不可用）会产生更多 `UNKNOWN`，这是安全设计而非功能失败；
- Namespace、alias、Cache 和远程 Source 需要额外治理；
- 规范完成后仍需独立实现和安全验证。

## 10. Developer Kit Impact（开发者工具包影响）

Developer Kit 增加 Canonical Reference Resolution（规范引用解析）作为基础能力。未来概念入口可表达为：

```python
# Concept only（仅为概念，不是当前 API）
result = dbos.resolve(reference=...)
```

该概念调用只返回四种 Resolution Result，不自动继续执行 `register`、`execute`、`evidence` 或 `verify`。调用方必须显式处理非 `RESOLVED` 状态，即使 `RESOLVED` 也必须继续执行独立验证与权限检查。

## 11. Implementation Gates（实现闸门）

未来 `Canonical Reference Resolver Implementation v0.1` 需要新的明确授权，并依次通过：

1. `GATE-R1 REFERENCE_SCHEMA_FREEZE`：冻结 Reference Object 和 Result 字段；
2. `GATE-R2 NAMESPACE_POLICY_FREEZE`：冻结 Namespace、Version、alias 和 collision 规则；
3. `GATE-R3 ERROR_MODEL_FREEZE`：冻结结构化错误码；
4. `GATE-R4 LOCAL_READ_ONLY_RESOLVER`：只支持明确本地 Source、无网络、无写入；
5. `GATE-R5 TYPE_ADAPTERS`：分别实现七种类型的 Source adapter；
6. `GATE-R6 NEGATIVE_CONFORMANCE`：拒绝 Permission、Capability、Activation、Verification 和 Evidence promotion；
7. `GATE-R7 SDK_INTEGRATION`：接入 Developer Kit，但保持概念边界；
8. `GATE-R8 EXTERNAL_NAMESPACE_PILOT`：选择一个外部 Agent 项目测试 Namespace 与冲突语义；
9. `GATE-R9 SECURITY_REVIEW`：审查路径、网络、隐私、Cache、alias 和拒绝服务风险。

每个 Gate 独立决定，不能自动授权下一步。

## 12. README Version Boundary（README 版本边界）

本任务按用户明确要求更新根 `README.md`，增加 Canonical Reference Layer（规范引用层）入口。该修改是 `DBOS-EXP-0001` 冻结快照之后的文档工作树版本，不改写、删除或重新声称历史 snapshot digest（快照摘要）。

```text
README_DOCUMENTATION_UPDATED=true
DBOS_EXP_0001_HISTORICAL_SNAPSHOT_CHANGED=false
HISTORICAL_EVIDENCE_REWRITTEN=false
```

## 13. Non-decisions（非决策）

本 ADR 没有：

- 创建 Resolver 代码；
- 创建 Database、Namespace Registry、Identity Provider 或 Permission Engine；
- 创建 SDK package 或 API；
- 创建 Entity、Agent、Runtime 或 Digital Organism（数字生命体）；
- 修改 Capability、Permission、Evidence 或 Verification 状态；
- 修改 DBA 或 SAEE；
- 执行实验；
- 授权 commit（提交）、release（发布）或外部部署。

## 14. Decision Invariants（决策不变量）

```text
DECISION_SCOPE=REFERENCE_RESOLUTION_SPECIFICATION
IMPLEMENTATION_AUTHORIZED=false
DBOS_ROLE=INFRASTRUCTURE
REFERENCE_NE_AUTHORITY=true
REFERENCE_NE_TRUTH=true
RESOLVER_NE_VERIFICATION=true
VERIFICATION_NE_PERMISSION=true
UNKNOWN_MUST_REMAIN_UNKNOWN=true
SOURCE_OWNERSHIP_PRESERVED=true
CURRENT_API=false
CURRENT_CODE=false
```

## 15. Related Documents（关联文档）

- `canonical-reference-resolver-specification.md`
- `reference-namespace-model.md`
- `reference-resolution-boundary-rules.md`
- `developer-kit-specification.md`
- `ADR-016-developer-ecosystem.md`
- `entity_support/README.md`
- `validation/identity_validator.py`
