# DBOS Developer Trust Model v0.1（DBOS 开发者信任模型 v0.1）

状态：`SPECIFICATION_ONLY`

当前 Trust Package 实现：`NONE`

## 1. 信任定义

DBOS 中的 Trust（信任）不是由平台授予的永久属性。它是消费者在明确主体、目的、环境、时间和证据范围内，对一组可归因事实作出的判断。

```text
Trust = scoped consumer judgment over inspectable evidence
```

中文：信任是消费者基于可检查证据作出的范围化判断。

Developer Trust Model（开发者信任模型）的目标，是帮助开发者形成可追踪、可复核、可撤销的可信运行材料，而不是获得 Permission（权限）、Authority（权力）、Certification（认证）或全局可信标记。

## 2. 信任链参与者

| 参与者 | 责任 | 不自动拥有 |
|---|---|---|
| Entity Owner（实体所有者） | 声明身份来源、版本和责任边界 | 验证独立性、Permission |
| Developer（开发者） | 定义能力边界、环境、集成和测试材料 | 架构权力、认证权力 |
| Runtime Provider（运行时提供者） | 执行外部 Agent/Application 并提供上下文 | DBOS 身份事实真源 |
| Evidence Producer（证据生产者） | 产生有来源的 Artifact、Event 或记录 | 事实自证、独立验证 |
| Verifier（验证主体） | 用声明方法检查限定 Claim 和 Evidence | Capability Assignment、Permission |
| Trust Package Producer（信任包生产者） | 组合引用、限制与撤销材料 | 修改原始 Evidence |
| Consumer（消费者） | 结合自己的风险、目的和政策作最终判断 | 改写上游历史 |

同一主体可以承担多个角色，但必须声明角色重合和 conflict of interest（利益冲突）。角色重合不能被表述为独立验证。

## 3. 可信运行能力

开发者通过 DBOS 获得的“可信运行能力”仅指能够：

- 为执行主体提供稳定、连续的身份引用；
- 声明并检查 Capability Boundary（能力边界）；
- 把执行绑定到环境、输入、输出、依赖和版本；
- 形成不可静默覆盖的 Evidence Reference（证据引用）；
- 请求限定范围的 Verification（验证）；
- 向消费者导出可解析的 Trust Package（信任包）；
- 在撤销、过期或证据缺失时失败关闭。

它不表示开发者或实体获得了执行权限、业务准入、法律合规、模型安全、生产适用性或生态地位。

## 4. 信任材料层次

DBOS 现有 C/E/V 体系保持权威：

- C（Capability Maturity，能力成熟度）：`C0–C5`；
- E（Evidence Maturity，证据成熟度）：`E0–E5`；
- V（Verification Level，验证等级）：`V0–V5`。

Trust Package 不创建新的等级轴，也不能取三者的最高值作为“信任分数”。

解释原则：

1. Capability Claim 说明主体声称能做什么；
2. Evidence 说明该声明有什么材料支持；
3. Verification 说明谁用什么方法检查了哪些材料；
4. Permission 说明某次动作是否被允许；
5. Trust 由消费者在自己的场景中综合判断。

```text
Capability != Evidence
Evidence != Verification
Verification != Permission
Permission != Trust
Trust != Certification
```

中文：能力、证据、验证、权限、信任和认证彼此不同，不能自动推导。

## 5. Trust Package 概念模型

未来 Trust Package 是只读引用包，不是新的事实数据库。概念字段如下：

```text
package_id
package_version
subject_entity_ref
subject_version_ref
lifecycle_state_ref
capability_boundary_refs
execution_context_refs
event_refs
evidence_refs
verification_refs
authorization_refs
permission_statement
limitations
validity_window
revocation_refs
producer_ref
generated_at
package_digest
```

安全要求：

- 每个引用必须可以独立解析或明确标记不可用；
- `permission_statement` 只能引用外部真实决定，默认 `not_granted`；
- `generated_at` 只表示打包时间，不表示上游材料仍然有效；
- `package_digest` 保护包内容完整性，不证明内容真实性；
- `limitations` 不得为空；
- 撤销、过期和冲突材料必须随包暴露；
- 不复制可由规范来源解析的 Evidence 正文；
- 包生产者不能修改或提升 C/E/V 等级。

该字段集合尚未形成 schema（模式）、API（应用程序接口）或导出器。

## 6. 信任包验证流程

消费者收到 Trust Package 后应按顺序检查：

```text
Package structure（包结构）
  ↓
Package digest（包摘要）
  ↓
Subject identity and lineage（主体身份与谱系）
  ↓
Lifecycle status and validity（生命周期状态与有效期）
  ↓
Capability scope and limitations（能力范围与限制）
  ↓
Execution context reproducibility（执行上下文可复现性）
  ↓
Evidence provenance and integrity（证据来源与完整性）
  ↓
Verifier identity, method and independence（验证主体、方法与独立性）
  ↓
Revocation and conflict checks（撤销与冲突检查）
  ↓
Consumer policy decision（消费者政策决定）
```

任一步骤失败时，应返回失败原因和未确认范围。不得在引用不可用时退化为“默认可信”。

## 7. Evidence 与信任边界

以下材料单独存在时，均不足以形成广义信任结论：

- README 或设计说明；
- 本地测试通过；
- CI（持续集成）状态；
- 文件摘要或签名；
- 自我证明；
- 单个 Validator `PASS`；
- Demo（演示）或合成 fixture（测试夹具）；
- 软件包发布；
- 市场上架、合同或付费关系；
- Agent 框架或模型品牌。

Digest（摘要）证明内容未发生可检测变化；Signature（签名）证明某个密钥对某段内容作出声明；Attestation（证明）连接 Producer 与 Claim。三者都不能替代原始事实来源、适用范围或独立验证。

## 8. Verification 与信任边界

Verification Record 必须保留：

- Claim；
- Evidence；
- Verifier identity；
- method/version；
- environment；
- input digest；
- decision；
- limitations；
- timestamp；
- independence/conflict record；
- revocation path。

验证等级不能超过证据支持上限。V4 需要独立主体和利益冲突材料；V5 需要连续观测窗口、覆盖、漂移和撤销材料。

即使验证通过，也只能说“在指定方法、版本、环境和范围内通过”。不能扩展为全局安全、生产可靠、法规合规或未来持续有效。

## 9. 授权、权限与信任边界

Authorization（授权）是一个治理决定引用；Permission 是某个主体在某个上下文对某个动作的允许状态。两者都不由 Trust Package 自动产生。

消费者可以要求特定授权或权限材料，但 Trust Package 只能携带引用和状态陈述。商业合同、支付状态、订阅级别或客户身份不得自动变成 DBOS Permission。

## 10. 撤销、过期与更正

可信材料必须支持：

- 撤销 Verifier、Evidence、Authorization 或扩展；
- 通过新记录更正错误，不覆盖旧记录；
- 标记过期环境、版本和验证窗口；
- 说明 successor（后继）和 superseded（已替代）关系；
- 在 Trust Package 中携带最新已知撤销引用；
- 保留消费者当时使用的包版本和摘要。

撤销不会删除历史，但会改变当前消费者是否应依赖该材料。

## 11. 隐私与最小披露

Trust Package 应默认只包含引用、摘要、范围和必要元数据，不复制密钥、凭据、个人数据、专有输入或完整环境清单。

开发者应能：

- 对敏感 Evidence 使用受控引用；
- 声明访问条件和保留期；
- 区分公开、合作方和受限材料；
- 在不披露正文时证明特定摘要或验证结果；
- 记录因隐私限制而无法独立复现的范围。

最小披露不会降低验证要求；材料不足时结论必须缩小或保持 `unknown/pending`。

## 12. 商业信任服务边界

未来商业服务可以提供：

- Trust Package 托管和呈现；
- Evidence 保留与访问控制；
- 独立验证、审计支持或行业复核；
- 企业政策映射；
- 撤销监测和持续观察。

这些服务必须以独立身份和合同运行。DBOS Validator 不是认证机构；商业服务也不能通过付款获得更高 Evidence 或 Verification 等级。认证、审计意见、法律结论和 SLA（服务等级协议）属于提供者自身责任，不属于 DBOS 核心事实。

当前不存在 DBOS 官方 Trust Package 服务、认证计划或商业承诺。

## 13. 信任模型验收条件

未来 Trust Package 实现至少应通过：

- 缺失主体引用时失败；
- 引用主体版本不一致时失败；
- Evidence 摘要缺失或不匹配时失败；
- Verification 越过证据上限时失败；
- `pending` 记录伪装成 `pass` 时失败；
- Permission 或 Capability 被从 Verification 自动推导时失败；
- 撤销材料被遗漏时失败；
- V4/V5 独立性或连续观察材料不足时失败；
- Trust Package 尝试覆盖规范 Evidence 时失败；
- 消费者能读取范围、限制和未解决问题。

## 14. 不变量

```text
TRUST_IS_SCOPED=true
TRUST_IS_CONSUMER_DECISION=true
TRUST_NE_PERMISSION=true
TRUST_NE_AUTHORITY=true
TRUST_NE_CERTIFICATION=true
PACKAGE_DIGEST_NE_FACT_TRUTH=true
VERIFICATION_PASS_NE_GLOBAL_TRUST=true
COMMERCIAL_PAYMENT_NE_TRUST=true
HISTORY_PRESERVATION_REQUIRED=true
CURRENT_TRUST_PACKAGE_SCHEMA=false
CURRENT_TRUST_SERVICE=false
```

关联文档：

- `developer-kit-specification.md`
- `developer-quickstart-model.md`
- `developer-extension-model.md`
- `ADR-016-developer-ecosystem.md`
