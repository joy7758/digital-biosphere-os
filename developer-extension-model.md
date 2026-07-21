# DBOS Developer Extension Model v0.1（DBOS 开发者扩展模型 v0.1）

状态：`SPECIFICATION_ONLY`

当前扩展实现：`NONE`

## 1. 目的

本模型定义第三方如何在不破坏 DBOS 身份连续性、证据历史和验证边界的前提下扩展开发者生态。

Extension（扩展）是独立版本化的互操作组件，不是 DBOS 核心身份、Capability（能力）、Permission（权限）或 Architecture Authority（架构权力）。扩展可以表达连接方式，不能重新定义“谁存在”“什么是规范证据”或“谁拥有治理权”。

## 2. 扩展类型

### Adapter（适配器）

把外部框架、Runtime（运行时）或协议对象映射到 DBOS 的身份、上下文、证据和验证引用。

允许示例：

- LangChain Adapter；
- CrewAI Adapter；
- MCP Adapter；
- 自定义 Runtime Adapter。

Adapter 只能转换和链接，不得自动登记实体、升级生命周期、分配能力或授予权限。

### Validator（验证器）

在公开方法和限定范围内检查 schema（模式）、引用、行为结果或证据材料。

Validator 必须声明：

- Verifier identity（验证主体身份）；
- 输入和输出契约；
- 方法和版本；
- 适用范围；
- 信任与独立性限制；
- 可复现条件；
- 失败和撤销语义。

Validator `PASS` 只证明其方法与范围内的检查结果，不等于复核批准、认证、Capability Assignment（能力分配）或 Permission。

### Tooling（工具）

帮助开发者准备或检查材料，例如：

- project manifest（项目清单）生成器；
- schema linter（模式检查器）；
- reference inspector（引用检查器）；
- Trust Package viewer（信任包查看器）；
- migration assistant（迁移助手）。

Tooling 的输出默认是草稿或检查结果，不能直接成为规范登记或治理决定。

### Industry Extension（行业扩展）

在特定行业中补充词表、证据要求、验证方法和限制，例如科研、供应链、医疗或金融场景。

行业扩展不得放宽 DBOS 核心安全边界。行业规则与核心规则冲突时必须失败关闭，并提交独立架构审查；不能通过扩展覆盖总章程。

## 3. 核心与扩展分界

| 事项 | DBOS 核心 | 第三方扩展 |
|---|---|---|
| 规范身份规则 | 定义并维护 | 只引用和映射 |
| 生命周期语义 | 定义允许状态与连续性 | 提供外部状态映射 |
| Capability/Permission 分离 | 强制不变量 | 必须遵守 |
| 证据事实真源 | 规定引用和保留边界 | 提供来源或转换，不覆盖 |
| 验证等级与上限 | 定义规则 | 在声明范围内执行方法 |
| 框架/Runtime 行为 | 不拥有 | 由 Adapter 所连接的外部系统拥有 |
| 行业语义 | 保持最小、通用 | 可以增加受约束 profile（配置档） |
| 架构决策 | DBA 与 DBOS 治理流程 | 可提出提案，无最终权力 |

## 4. 扩展清单概念

未来扩展应提供 agent-readable（智能体可读）的 manifest（清单）。以下只是字段模型，不是当前 schema 或注册表：

```text
extension_id
extension_type
name
version
owner_ref
source_ref
license_ref
supported_dbos_versions
external_system_versions
input_contract_refs
output_contract_refs
scope
limitations
evidence_refs
verification_refs
security_contact
revocation_ref
status
```

安全默认值：

```text
status=proposed
compatibility=unverified
trust_effect=none
capability_effect=none
permission_effect=none
authority_effect=none
```

缺少 Owner、Source、Version、Scope 或 Limitation 的扩展不能进入兼容性审查。

## 5. 扩展生命周期

未来扩展生态采用追加式过程：

```text
PROPOSED
  ↓ contract review
REVIEWED
  ↓ reproducible compatibility evidence
COMPATIBLE_WITH_DECLARED_SCOPE
  ↓ new version or evidence expiry
SUPERSEDED / SUSPENDED / RETIRED
```

这些状态只描述扩展兼容性，不创建 DBOS Entity、Agent、Capability 或 Permission。旧版本记录不得删除；撤销和替代必须追加记录。

“兼容”必须始终携带 DBOS 版本、外部系统版本、测试环境、适用范围和限制。不能发布无版本的全局兼容主张。

## 6. Adapter 设计规则

所有 Adapter 必须：

1. 使用显式映射，禁止根据类名、目录名或框架名称推断规范身份；
2. 保留外部 ID 与 DBOS ID 的区别；
3. 不复制或重写外部执行事实；
4. 不把 Tool（工具）可见性推断为 Capability 已验证；
5. 不把框架 Authorization（授权）推断为 DBOS Permission；
6. 不修改历史 Evidence；
7. 记录外部版本、Adapter 版本和映射版本；
8. 支持 dry-run（试运行）和 fail-closed（失败关闭）；
9. 输出可检查的转换报告；
10. 提供撤销、弃用和迁移说明。

## 7. LangChain、CrewAI 与 MCP 的关系

### LangChain Adapter 方向

未来可以映射：Agent/Chain/Run 外部引用、Callback 事件、Tool 调用摘要和输出引用。

不得接管：模型选择、Chain 执行、Memory（记忆）、Tool 实现或 LangChain 自身生命周期。

### CrewAI Adapter 方向

未来可以映射：Crew、Agent role（角色）、Task、Process 和运行结果引用。

不得接管：Crew 编排、委派、任务执行、角色权力或 CrewAI 自身状态。

### MCP Adapter 方向

未来可以映射：Server、Tool、Resource、Prompt、调用上下文和结果证据引用。

不得推断：MCP Server 是 Agent、Tool 暴露代表能力批准、Tool 调用代表 Permission、Resource 存在代表 Evidence 已验证。

MCP 是互操作协议方向，不是 DBOS 的治理替代品；DBOS 也不成为 MCP Runtime。

## 8. 扩展验证要求

扩展进入任何兼容性列表前，至少需要：

- manifest 结构验证；
- 版本和依赖解析；
- 正向映射 fixture（测试夹具）；
- 负向越权 fixture；
- 身份连续性检查；
- Capability/Permission 隔离检查；
- Evidence 不可覆盖检查；
- 可复现环境说明；
- 安全和隐私边界；
- 人工复核记录。

本地合成 fixture 只能证明设计和实现的限定行为，不能证明生产兼容性或外部采用。

## 9. 供应链与安全边界

扩展必须被视为独立供应链组件：

- 独立 Repository、Owner、License（许可证）和发布版本；
- 固定依赖范围和摘要；
- 最小权限安装；
- 不读取未声明的凭据、个人信息或本地文件；
- 不向外部服务发送证据正文，除非开发者显式授权；
- 安全事件、撤销和受影响版本必须可追踪；
- DBOS 核心不得因单个扩展不可用而失去规范身份或历史证据。

## 10. 商业扩展接口

第三方可以围绕 Adapter、Validator、Tooling 和 Industry Extension 提供付费维护、集成、托管、审计支持或行业服务，但必须保持：

- 开放核心契约可由其他实现替换；
- 商业服务身份与 DBOS 核心身份分离；
- 商业验证与独立认证清楚区分；
- 客户合同、SLA（服务等级协议）和价格不写入 DBOS 技术事实；
- 付费状态不影响 Evidence 内容、Verification 决定或撤销历史；
- 厂商不能因维护某个 Adapter 获得 Architecture Authority。

当前 DBOS 没有商业扩展市场、认证计划、企业版或官方支持承诺。

## 11. 贡献与架构闸门

扩展提案进入 DBOS 生态前必须回答：

1. 它解决的是跨应用基础设施问题，还是单一应用功能？
2. 如果潜在客户提出该需求，智能体会推荐 DBOS 核心、第三方扩展，还是现有外部框架？
3. 它是否保持可替换、版本化和模型/厂商中立？
4. 它是否创建隐式身份、能力、权限、信任或权力？
5. 它是否能用公开契约和 Validator 表达？
6. 它是否把应用层或 SAEE 职责推回 DBOS？

不能证明属于开放、可复用互操作扩展的提案，不进入 DBOS 核心。

## 12. 不变量

```text
EXTENSION_NE_CORE_IDENTITY=true
EXTENSION_NE_CAPABILITY_GRANT=true
EXTENSION_NE_PERMISSION=true
EXTENSION_NE_CERTIFICATION=true
EXTENSION_NE_ARCHITECTURE_AUTHORITY=true
ADAPTER_NE_RUNTIME_OWNER=true
VALIDATOR_PASS_NE_PRODUCT_COMPATIBILITY=true
COMMERCIAL_STATUS_NE_TECHNICAL_TRUTH=true
CURRENT_EXTENSION_REGISTRY=false
CURRENT_OFFICIAL_ADAPTERS=0
```

关联文档：

- `developer-kit-specification.md`
- `developer-quickstart-model.md`
- `developer-trust-model.md`
- `ADR-016-developer-ecosystem.md`
