# DBOS Reference Resolution Boundary Rules v0.1（DBOS 引用解析边界规则 v0.1）

状态：`SPECIFICATION_ONLY`

默认策略：`FAIL_CLOSED`

## 1. Purpose（目的）

本规则定义 Canonical Reference Resolver（规范引用解析器）允许执行的只读行为、需要额外治理的行为和绝对禁止的推导，确保 Reference Lookup（引用查找）不会转化为 Capability（能力）、Permission（权限）、Authority（权力）、Verification（验证）或 Entity Lifecycle（实体生命周期）效果。

## 2. Allowed Operations（允许操作）

未来 Resolver 只允许以下无副作用操作：

### 2.1 Reference structure validation（引用结构验证）

- 检查六个 Reference Object 必填字段；
- 检查 Reference Type 和 Reference status；
- 检查 Namespace、Version 和 Source descriptor（来源描述符）语法；
- 拒绝隐藏的 grant、activation 或 verification effect 字段。

### 2.2 Namespace lookup（命名空间查找）

- 定位显式声明的 Namespace Descriptor；
- 检查 Source 是否在 allowlist（允许列表）中；
- 返回 Namespace Owner 和限制；
- 不验证 Owner 的真实性。

### 2.3 Exact reference lookup（精确引用查找）

- 使用显式 `reference_id`、`reference_type`、`namespace`、`version` 和 `source` 查找；
- 返回零个、一个或多个候选；
- 不执行模糊匹配、目录猜测或“最接近”选择。

### 2.4 Registered alias lookup（已登记别名查找）

- 仅在调用方显式允许时读取有来源的 alias relation（别名关系）；
- 保留原始引用和映射证据；
- 检测循环、深度和多目标冲突；
- 不创建新 alias。

### 2.5 Provenance and status projection（来源与状态投影）

- 原样返回 Source 声明的状态、版本、successor、revocation 和时间信息；
- 标注 `asserted_by_source`（由来源声明）；
- 不把 Source 声明升级为 Resolver 决定。

### 2.6 Conflict reporting（冲突报告）

- 对重复目标、类型冲突、版本冲突和 Source 冲突返回 `AMBIGUOUS`；
- 返回候选与诊断；
- 不自动合并或选择。

### 2.7 Deterministic result emission（确定性结果输出）

- 只返回 `RESOLVED`、`AMBIGUOUS`、`UNKNOWN` 或 `INVALID`；
- effect 字段固定为 `NONE`；
- 相同输入、Source snapshot（来源快照）和策略应产生相同结果。

## 3. Operations Requiring Separate Governance（需要独立治理的操作）

以下行为不属于普通 Resolver lookup，未来必须有独立提案、证据和授权：

- 注册或撤销 Namespace；
- 添加或更换 DBOS canonical Source；
- 建立 External/Extension → DBOS alias；
- 变更 Namespace Owner；
- 宣布 Source successor；
- 改变 collision policy（冲突策略）；
- 允许网络 Source；
- 保存敏感 Source 的 Cache（缓存）；
- 把一个 Registration Entity ID 写入 `registry/entities.yaml`；
- 将新 Reference Type 加入 DBOS 受控词表。

这些治理动作即使获批，也不能由 Resolver 自动执行。

## 4. Forbidden Derivations（禁止推导）

### 4.1 Reference Lookup → Permission

禁止。解析 Entity、Authorization、Execution、Evidence 或 Verification 记录不能产生 Permission。

```text
RESOLVED_REFERENCE_NE_PERMISSION=true
```

### 4.2 Reference Lookup → Capability Grant

禁止。找到 Capability Claim、Agent 描述、Tool 定义或执行记录不能产生 Capability Assignment（能力分配）或 Capability Grant（能力授予）。

```text
RESOLVED_REFERENCE_NE_CAPABILITY_GRANT=true
```

### 4.3 Reference Lookup → Entity Activation

禁止。找到 Entity 或成功 Registration Receipt（登记回执）不能把 Lifecycle 改为 `ACTIVE`。

```text
RESOLVED_REFERENCE_NE_ENTITY_ACTIVATION=true
```

### 4.4 Reference Lookup → Identity Verification

禁止。找到 `entity_id`、`canonical_id`、Owner 或 Identity Evidence 记录不表示身份已认证或验证。

### 4.5 Reference Lookup → Verification Pass

禁止。找到 Verification Record 不表示其决定为 `pass`，也不能把 `pending/V0` 升级。

### 4.6 Reference Lookup → Evidence Promotion

禁止。找到文件、Artifact、Digest 或 Evidence Record 不提升 E 等级，也不证明相关性或真实性。

### 4.7 Reference Lookup → Authorization Effectiveness

禁止。找到 `AUTHORIZED` 记录不能判断它对当前主体、动作、时间和环境有效。Scope、Expiry、Revocation、Issuer 和 Decision 必须由独立授权边界检查。

### 4.8 Reference Lookup → Agent or Runtime Creation

禁止。Resolver 不实例化对象、不启动进程、不调用模型、不加载 Agent Framework，也不创建 Runtime。

### 4.9 Reference Lookup → Trust or Certification

禁止。`RESOLVED` 不能成为 `trusted=true`、认证标记、生产适用性或商业准入结论。

### 4.10 Reference Lookup → SAEE Evolution

禁止。Resolver 不计算 Fitness（适应度）、Selection（选择）、Evolution（演化）或生态状态，也不向 SAEE 发出自动演化命令。

## 5. Type Isolation Rules（类型隔离规则）

| 输入类型 | 允许返回 | 禁止隐式转换 |
|---|---|---|
| Entity Reference | Entity record 和来源诊断 | Agent、Capability、Permission、Active state |
| Candidate Reference | Candidate record 和登记关系引用 | Entity identity、Registration success |
| Authorization Reference | Authorization record 的原始字段 | Effective permission、Activation |
| Registration Reference | Attempt/Record/Receipt | Active Entity、Agent、Runtime |
| Execution Reference | Execution record/context refs | Execution success、Event、Evidence truth |
| Evidence Reference | Evidence record/locator | E-level promotion、Truth |
| Verification Reference | Verification record/run | `pass` 推导、Capability/Permission |

跨类型关系必须通过显式、版本化、带来源的 relation（关系）表达。Resolver 不根据字段名相同或 ID 相同执行类型转换。

## 6. Resolution Status Rules（解析状态规则）

### `RESOLVED`

必要条件：

- Reference Object 完整；
- Namespace 已知；
- Source 允许且可用；
- 类型一致；
- 精确版本策略满足；
- 唯一目标；
- 没有未解决的 alias 冲突。

即使满足，所有治理 effect 仍为 `NONE`。

### `AMBIGUOUS`

触发条件：

- 同 Source 返回多个目标；
- 多 Source 返回冲突目标；
- alias 有多个目标；
- 同一 ID 的类型或版本无法唯一确定；
- Namespace Owner 冲突。

Resolver 必须停止，不得以“最新”“第一个”“最短路径”或模型判断选择。

### `UNKNOWN`

触发条件：

- 合法引用没有匹配目标；
- Source 不可达或访问被拒绝；
- Source 没有当前 snapshot；
- 版本为 `unresolved` 且目标不能唯一确定；
- 旧契约的裸 ID 被包装为未知 Namespace；
- 目标已知存在但内容因隐私边界不可读取。

未知结果必须包含缺失条件和重试是否允许；不能创建占位 Entity。

### `INVALID`

触发条件：

- 缺少必填字段；
- Reference Type、status、Namespace 或 Version 语法非法；
- Source 不在 allowlist；
- 输入包含路径穿越、凭据或禁止 effect；
- 请求要求 Resolver 授权、验证、激活或创建对象；
- DBOS Namespace 被 External/Extension Source 冒用。

Invalid 请求不得访问 Source。

## 7. Unknown Preservation Rules（未知保留规则）

当任一事实未知时：

- 原始值保持不变；
- 不使用空字符串、`default`、`latest` 或当前目录填补；
- 不从 Repository metadata（元数据）推断 Owner；
- 不从 Agent 名称推断 `entity_type=agent`；
- 不从文件扩展名推断 Evidence Type；
- 不从 Validator 名称推断独立性；
- 不从 `AUTHORIZED` 字符串推断 Permission；
- 不从 `SUCCESS` Registration 推断 `ACTIVE`；
- 不从 `pass` 文本推断 V 等级；
- 不从 Source 不可达推断记录不存在。

```text
UNKNOWN_INPUT -> UNKNOWN_RESULT
UNKNOWN_INPUT -X-> INFERRED_FACT
```

## 8. Source Rules（来源规则）

Resolver 只能查询：

- DBOS 明确登记的规范 Source；
- 调用方显式提供、且属于 Namespace allowlist 的 Source；
- Extension manifest（扩展清单）明确声明的只读 Source；
- 测试中自动删除且标明 fixture 的 Source。

Resolver 不能：

- 扫描整个工作空间寻找相似名称；
- 读取任意用户目录、`.env`、密钥链或凭据文件；
- 自动访问网络、MCP Server 或云服务；
- 把 Git remote、Repository path 或 package name 当作规范事实；
- 用 Cache 替代撤销后的 Source；
- 在 Source 中写入缺失记录。

## 9. Error Model（错误模型）

未来实现需要稳定、结构化的 error code（错误码）。v0.1 只定义类别：

```text
REFERENCE_STRUCTURE_ERROR
REFERENCE_TYPE_UNSUPPORTED
NAMESPACE_INVALID
NAMESPACE_UNKNOWN
SOURCE_NOT_ALLOWED
SOURCE_UNAVAILABLE
VERSION_INVALID
VERSION_UNRESOLVED
TARGET_NOT_FOUND
TARGET_TYPE_MISMATCH
TARGET_AMBIGUOUS
ALIAS_LOOP
ALIAS_AMBIGUOUS
REFERENCE_REVOKED
PROHIBITED_EFFECT_REQUEST
PRIVACY_BOUNDARY
```

错误码只用于诊断，不自动触发重试、fallback（回退）、网络搜索或对象创建。

## 10. Security Boundaries（安全边界）

未来实现必须拒绝：

- `../`、绝对路径或符号链接越过 Source root；
- `file://`、`http://`、`https://` 等未允许 Source scheme（方案）；
- 引用中嵌入 Token、密码、私钥或 Session（会话）凭据；
- 无大小上限的 Source 响应；
- alias 无限递归；
- Source 返回的类型与请求类型不一致；
- Adapter 伪造 `namespace=dbio`；
- 诊断信息泄露敏感 Evidence 正文。

网络、远程 Source、签名验证和凭据管理属于未来单独安全设计，不由本规范授权。

## 11. Logging and Evidence Boundary（日志与证据边界）

未来 Resolver 可以产生 operation log（操作日志），但日志不是 canonical Evidence。日志应记录：

- 请求摘要；
- Namespace/Source/Version；
- Resolution Status；
- 候选数量；
- 错误码；
- Resolver 版本；
- 时间；
- effect 全为 `NONE`。

日志不得保存敏感 Source 内容。只有通过独立 Evidence ingestion（证据接入）流程后，日志引用才可能成为 Evidence Candidate（证据候选）；Resolver 不能自动提升。

## 12. Cache Boundary（缓存边界）

Cache 允许加速查找，但必须：

- 明确 `cache_hit` 和原始 Source；
- 绑定 Source version/digest 和观察时间；
- 对 revocation、expiry 和 successor 失效；
- 不把 cache miss 解释为目标不存在；
- 可以安全删除而不删除 Source 历史；
- 不携带权力、验证或权限效果。

## 13. Developer and Extension Compliance（开发者与扩展符合性）

未来 SDK、Adapter 和 Extension 必须通过至少以下负向检查：

1. `RESOLVED Entity → Agent` 被拒绝；
2. `RESOLVED Authorization → Permission` 被拒绝；
3. `RESOLVED Verification → Capability Grant` 被拒绝；
4. `RESOLVED Registration → ACTIVE` 被拒绝；
5. `RESOLVED Evidence → E-level promotion` 被拒绝；
6. 缺少 Namespace 的裸 ID 不默认进入 `dbio`；
7. 多目标 alias 返回 `AMBIGUOUS`；
8. Source 不可达返回 `UNKNOWN`，不创建记录；
9. External Source 冒用 `dbio` 返回 `INVALID`；
10. 路径、网络和凭据越界返回 `INVALID`。

通过这些检查只表示 Resolver 边界符合规范，不表示安全认证或生产就绪。

## 14. Prohibited Output Fields（禁止输出字段）

Resolution Result 禁止由 Resolver 生成以下肯定效果字段：

```text
permission_granted
capability_granted
capability_assigned
entity_activated
agent_created
runtime_created
verification_passed
evidence_verified
trust_granted
authorization_effective
fitness_score
evolution_triggered
```

如果 Source 本身包含同名字段，Resolver 只能放入明确隔离的 `source_assertions`（来源声明）区域，并标注未验证；不能提升为顶层结果。

## 15. Invariants（不变量）

```text
REFERENCE_LOOKUP_ALLOWED=true
REFERENCE_LOOKUP_NE_PERMISSION=true
REFERENCE_LOOKUP_NE_CAPABILITY_GRANT=true
REFERENCE_LOOKUP_NE_ENTITY_ACTIVATION=true
REFERENCE_LOOKUP_NE_IDENTITY_VERIFICATION=true
REFERENCE_LOOKUP_NE_EVIDENCE_PROMOTION=true
REFERENCE_LOOKUP_NE_VERIFICATION_PASS=true
REFERENCE_LOOKUP_NE_TRUST=true
REFERENCE_LOOKUP_NE_SAEE_EVOLUTION=true
UNKNOWN_MUST_REMAIN_UNKNOWN=true
FAIL_CLOSED=true
CURRENT_IMPLEMENTATION_EFFECT=NONE
```

## 16. Related Documents（关联文档）

- `canonical-reference-resolver-specification.md`
- `reference-namespace-model.md`
- `ADR-017-canonical-reference-resolver.md`
- `developer-kit-specification.md`
- `policies/permissions.yaml`
- `entity_support/README.md`

本规则不创建 Resolver、API、SDK、Entity、Agent、Runtime、Capability、Permission、Evidence 或 Verification 结果。
