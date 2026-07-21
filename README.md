# Digital Biosphere OS v0.1

Digital Biosphere OS 是用于管理 AI agent（人工智能智能体）、代码系统和协议生命周期的治理基础设施。

战略上，DBOS 定位为 Open Digital Entity Infrastructure（开放数字实体基础设施）：`DBOS governs existence`（DBOS 治理存在）。DBOS 是 infrastructure（基础设施），不是 Agent application（智能体应用）、Foundation Model（基础模型）、Chatbot Platform（聊天机器人平台）或 SAEE 替代品。

当前版本增加 Digital Biosphere Federation Layer v0.1（数字生物圈联邦层 v0.1），用中央 proposed member（拟议成员）、pending manifest（待定清单）、证据关系图和共享宪法引用连接独立项目。Federation 不合并仓库、不移动代码、不接管身份；当前不创建 Agent、Runtime、候选体或 Digital Organism。初始扫描的 22/78 条事实基线作为历史保留，另按明确授权新增 1 条 ACP 协议身份；能力声明仍为 78 条。

## Strategic Alignment（战略对齐）

最高战略定位、DBA（数字生物圈架构）关系、SAEE（硅基放大演化生态）边界、开发者生态方向、商业边界与非目标范围，见 [`STRATEGIC_ALIGNMENT.md`](STRATEGIC_ALIGNMENT.md)。该文件只同步战略，`implementation_effect=NONE`（无实现效果），不改变本 README 中的技术事实、能力、权限、实验或开发状态。

智能体在解释或规划 DBOS 任务前，应先读取该战略对齐说明，并保持：`DBOS is infrastructure, not application`（DBOS 是基础设施，不是应用）。

## License and Trial Access（许可证与试用访问）

本仓库的 Owner-created surfaces（负责人创作表面）采用
[`Apache-2.0`](LICENSE)。第三方依赖、数据、Evidence（证据）和独立许可材料继续遵循
各自来源与许可证；根 `LICENSE` 不自动重许可这些材料。

当前 Developer Preview（开发者预览）访问模型是 `PRIVATE_COLLABORATOR_TRIAL`
（私有协作者试用）：仓库保持 private（私有），只为未来冻结试用包中的已确认开发者
准备受控访问。该决定不表示已经添加协作者，也不表示 public release（公开发布）、
生产可用、Permission Grant（权限授予）或 Agent Runtime（智能体运行时）。

```text
LICENSE_ID=Apache-2.0
REPOSITORY_VISIBILITY=PRIVATE
TRIAL_ACCESS_MODEL=PRIVATE_COLLABORATOR_TRIAL
TRIAL_PARTICIPANTS_ADDED=0
PUBLIC_RELEASE_AUTHORIZED=false
AGENT_CREATED_BY_LICENSE_ADOPTION=false
RUNTIME_CREATED_BY_LICENSE_ADOPTION=false
PERMISSION_GRANTED_BY_LICENSE_ADOPTION=false
```

## Canonical Reference Layer（规范引用层）

Developer Ecosystem（开发者生态）使用 Canonical Reference Resolver Specification v0.1（规范引用解析规范 v0.1）统一 Entity、Candidate、Authorization、Registration、Execution、Evidence 和 Verification 引用的类型、Namespace（命名空间）、Version、Source 与解析结果。

入口：

- [`canonical-reference-resolver-specification.md`](canonical-reference-resolver-specification.md)：Reference Object（引用对象）、七种引用类型、四态 Resolution Result（解析结果）和 Source ownership（来源所有权）；
- [`reference-namespace-model.md`](reference-namespace-model.md)：`dbio`、External（外部）与 Extension（扩展）命名空间及冲突、alias（别名）和版本规则；
- [`reference-resolution-boundary-rules.md`](reference-resolution-boundary-rules.md)：允许的只读 lookup（查找）与禁止的 Permission、Capability、Activation 和 Verification 推导；
- [`ADR-017-canonical-reference-resolver.md`](ADR-017-canonical-reference-resolver.md)：统一解析语义的架构决策与未来实现闸门。

解析状态固定为 `RESOLVED`、`AMBIGUOUS`、`UNKNOWN`、`INVALID`。`RESOLVED` 只表示在声明的 Namespace、Reference Type、Version 和 Source 中找到唯一记录，不表示记录真实、身份已验证、授权有效、权限已授予或实体已激活。

```text
REFERENCE_NE_AUTHORITY=true
REFERENCE_NE_TRUTH=true
RESOLVER_NE_VERIFICATION=true
VERIFICATION_NE_PERMISSION=true
UNKNOWN_MUST_REMAIN_UNKNOWN=true
CURRENT_RESOLVER_IMPLEMENTATION=false
CURRENT_RESOLVER_API=false
```

本层当前仅为 `SPECIFICATION_ONLY`（仅规范），不创建 Database（数据库）、Identity Provider（身份提供者）、Permission System（权限系统）、Resolver 代码、SDK（软件开发工具包）或 API（应用程序接口）。

本 README 更新发生在 `DBOS-EXP-0001` 冻结快照之后，只增加当前工作树的规范入口，不改写、删除或重新声称历史 snapshot digest（快照摘要）。

## Documentation Evolution Evidence Layer（文档演化证据层）

Documentation Evolution Evidence Specification v0.1（文档演化证据规范 v0.1）定义 DBOS 文档如何形成后继版本、追加变化记录并连接前后快照，同时保持已有实验证据和历史验证结果不可变。

入口：

- [`documentation-evolution-evidence-specification.md`](documentation-evolution-evidence-specification.md)：Documentation Object（文档对象）、Change Record（变化记录）、四种变化类型和只追加证据边界；
- [`documentation-snapshot-model.md`](documentation-snapshot-model.md)：Previous Snapshot（前一快照）、Change Evidence（变化证据）和 Current Snapshot（当前快照）的有向关系；
- [`documentation-validation-boundary.md`](documentation-validation-boundary.md)：`PASS`、`FAIL`、`EXPECTED_CHANGE` 的互不替代语义与禁止自动修复规则；
- [`ADR-018-documentation-evolution-evidence.md`](ADR-018-documentation-evolution-evidence.md)：建立文档证据链的架构决策、备选方案和未来实现闸门。

```text
DOCUMENTATION_CHANGE_NE_HISTORICAL_REWRITE=true
NEW_VERSION_NE_OLD_EVIDENCE_REPLACEMENT=true
HASH_DIFFERENCE_NE_ERROR=true
EVIDENCE_RECORDS_APPEND_ONLY=true
CURRENT_DOCUMENTATION_LEDGER=false
CURRENT_VERSION_AWARE_VALIDATOR=false
```

本层当前仅为 `SPECIFICATION_ONLY`（仅规范）。它不创建真实 Documentation Object、Change Record、新快照、Schema（模式）、验证代码、SDK（软件开发工具包）或 API（应用程序接口）。`DBOS-EXP-0001` 的旧 evidence（证据）、snapshot、hash、report 和历史 `FAIL` 均保持不变；当前工作树相对旧快照的差异尚未被自动分类为 `EXPECTED_CHANGE`。

## API Boundary Layer（应用程序接口边界层）

DBOS API Boundary Decision v0.1（DBOS 应用程序接口边界决策 v0.1）定义未来开发者接口可以读取、解析、观察和连接什么，以及不得决定、执行或授予什么。

入口：

- [`api-boundary-decision.md`](api-boundary-decision.md)：Identity、Lifecycle、Capability、Execution Context、Evidence、Verification 和 Reference Resolver 七类 API 职责；
- [`api-responsibility-model.md`](api-responsibility-model.md)：Data Access（数据访问）、Reference Resolution（引用解析）、State Observation（状态观察）和 Evidence Linking（证据连接）的责任矩阵；
- [`api-object-contract-model.md`](api-object-contract-model.md)：Entity、Capability、Execution、Evidence Reference 和 Verification 五类概念对象边界；
- [`api-error-model.md`](api-error-model.md)：`UNKNOWN`、`INVALID`、`UNAUTHORIZED_REFERENCE`、`CONFLICT`、`VERSION_MISMATCH` 五类可解释错误；
- [`ADR-019-api-boundary-decision.md`](ADR-019-api-boundary-decision.md)：为什么必须在 SDK 实现前冻结 API 职责边界。

```text
DBOS_ROLE=INFRASTRUCTURE
ALLOWED_API_EFFECTS=READ_RESOLVE_OBSERVE_LINK
API_NE_AUTHORITY=true
API_NE_PERMISSION=true
API_NE_AGENT_FRAMEWORK=true
API_NE_EXECUTION_ENGINE=true
DBOS_NE_SAEE=true
CURRENT_API_IMPLEMENTATION=false
CURRENT_MINIMAL_OBJECT_SDK_SKELETON=true
CURRENT_INSTALLABLE_SDK_IMPLEMENTATION=false
```

本层当前仅为 `SPECIFICATION_ONLY`（仅规范），不定义 endpoint（端点）、transport（传输协议）、Server（服务器）、OpenAPI、SDK 或代码。现有 `entity_support/` 函数仍是本地支撑边界，不是已发布 API；`dbos.register(...)` 和 `dbos.execute(...)` 仍为未冻结概念名称，不能被解释为“调用即注册”或“DBOS 执行 Agent”。

## Object Contract Layer（对象契约层）

DBOS Object Contract Specification v0.1（DBOS 核心对象契约规范 v0.1）冻结未来 API、SDK、Adapter（适配器）和开发者扩展共享的五类对象语义，但不创建对象实例或代码。

规范入口：

- [`object-contract-specification.md`](object-contract-specification.md)：八个公共字段、五种对象类型、ID 等价、Version、Source、Status、空值和引用规则；
- [`entity-object-contract.md`](entity-object-contract.md)：Entity Object（实体对象）及其身份、Owner 和生命周期边界；
- [`capability-object-contract.md`](capability-object-contract.md)：Capability Object（能力对象）及声明、范围、限制和验证边界；
- [`execution-object-contract.md`](execution-object-contract.md)：Execution Object（执行对象）及惰性记录、上下文与非执行边界；
- [`evidence-reference-object-contract.md`](evidence-reference-object-contract.md)：Evidence Reference Object（证据引用对象）及 Source、Integrity 和 Truth 分离；
- [`verification-object-contract.md`](verification-object-contract.md)：Verification Object（验证对象）及验证类型、状态和 Permission 分离；
- [`object-error-semantics.md`](object-error-semantics.md)：`UNKNOWN`、`INVALID`、`VERSION_MISMATCH`、`CONFLICT`、`UNRESOLVED_REFERENCE`；
- [`ADR-020-object-contract.md`](ADR-020-object-contract.md)：统一对象契约的架构决策、智能体推荐边界和未来实现闸门。

所有对象必须支持：

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

```text
OBJECT_CONTRACT_VERSION=v0.1
OBJECT_CONTRACT_SEMANTICS=FROZEN_FOR_SPECIFICATION
OBJECT_NE_AUTHORITY=true
OBJECT_NE_PERMISSION=true
REFERENCE_NE_TRUTH=true
MACHINE_READABLE_SCHEMA=DEFINED_V0.1
DOMAIN_ENTITY_OR_GOVERNANCE_INSTANCE_CREATED=false
SDK_IN_MEMORY_REPRESENTATION_SUPPORTED=true
CURRENT_INSTALLABLE_SDK_IMPLEMENTATION=false
CURRENT_MINIMAL_OBJECT_SDK_SKELETON=true
```

本层不生成 Entity、Capability Grant（能力授予）、Execution、Evidence Truth（证据真相结论）、Verification `PASS`、Permission 或 SAEE Evolution（SAEE 演化）。当前 `entity_support/` 的 string reference（字符串引用）保持原样，未来 Adapter 必须显式包装，禁止回写历史记录。

## Autonomy Policy Layer（自主策略层）

DBOS Autonomy Policy Specification v0.1（DBOS 自主策略规范 v0.1）提出一个独立的人工监督层：在 Identity、Capability、Permission、Execution Context 和风险约束已经满足后，表达某项动作需要逐动作人工批准、可以按委托规则继续，还是可以在严格范围内无需逐动作批准。

规范入口：

- [`autonomy-policy-specification.md`](autonomy-policy-specification.md)：三种模式、Scope、Constraint、Approval、Evidence、判定顺序和科研智能体应用；
- [`autonomy-policy-object-model.md`](autonomy-policy-object-model.md)：未来 Policy 对象字段、生命周期、模式要求和软件开发工具包边界；
- [`autonomy-boundary-rules.md`](autonomy-boundary-rules.md)：Identity、Capability、Permission、Execution、Evidence、SAEE 与撤销边界；
- [`autonomy-mode-comparison.md`](autonomy-mode-comparison.md)：用户体验、风险、人工介入和 Evidence 要求比较；
- [`ADR-026-autonomy-policy.md`](ADR-026-autonomy-policy.md)：为什么 Autonomy 必须独立于 Permission 和 Capability。

```text
AUTONOMY_POLICY_SPECIFICATION=PROPOSED_V0.1
AUTONOMY_POLICY_APPROVED=false
AUTONOMY_POLICY_IMPLEMENTATION=false
AUTONOMY_POLICY_OBJECT_INSTANCE_COUNT=0
AUTONOMY_POLICY_SCHEMA=false
AUTONOMY_POLICY_VALIDATOR=false
AUTONOMY_POLICY_API=false
AUTONOMY_POLICY_SDK=false
AUTONOMY_POLICY_ENFORCEMENT=false
AUTONOMY_NE_PERMISSION=true
FULL_AUTONOMY_NE_UNLIMITED_PERMISSION=true
AGENT_COUNT_CREATED_BY_THIS_PROPOSAL=0
RUNTIME_COUNT_CREATED_BY_THIS_PROPOSAL=0
ENTITY_COUNT_CREATED_BY_THIS_PROPOSAL=0
PERMISSION_COUNT_CREATED_BY_THIS_PROPOSAL=0
EXECUTION_COUNT_CREATED_BY_THIS_PROPOSAL=0
AGENT_CREATED=false
RUNTIME_CREATED=false
ENTITY_CREATED=false
PERMISSION_GRANTED=false
EXECUTION_CREATED=false
IDENTITY_MODIFIED=false
EVIDENCE_MODIFIED=false
SAEE_MODIFIED=false
```

三种模式为 `APPROVAL_REQUIRED`（请求批准）、`DELEGATED_AUTONOMY`（委托自主）和 `FULL_AUTONOMY_WITHIN_SCOPE`（范围内完全自主）。当规则冲突时最严格约束优先；现有危险能力的强制人工批准不能被范围内完全自主绕过。

本层是 Architecture Specification Proposal（架构规范提案），不是策略实例、Permission、执行引擎或产品功能。用户任务建议的 `ADR-022-autonomy-policy.md` 与既有 `ADR-022-validation-result-contract.md` 冲突，因此使用唯一编号 `ADR-026-autonomy-policy.md`，不覆盖历史。

## Object Schema Layer（对象模式层）

DBOS Object Schema Specification v0.1（DBOS 核心对象模式规范 v0.1）把人类可读 Object Contract（对象契约）转换为 JSON Schema Draft 2020-12（JSON 模式 2020-12 草案）机器标准。仓库原有 `schemas/project-manifest.schema.yaml` 保持不变，本层新增 6 个对象 Schema。

机器入口：

- [`schemas/common-object-schema.yaml`](schemas/common-object-schema.yaml)：8 个公共字段、Source Descriptor（来源描述）、Reference Object（引用对象）和复用定义；
- [`schemas/entity-object-schema.yaml`](schemas/entity-object-schema.yaml)：Entity Object 结构、类型与生命周期词表；
- [`schemas/capability-object-schema.yaml`](schemas/capability-object-schema.yaml)：Capability Object 结构、范围、限制和安全验证状态；
- [`schemas/execution-object-schema.yaml`](schemas/execution-object-schema.yaml)：Execution Object 结构与 `UNKNOWN/CREATED` 上限；
- [`schemas/evidence-reference-object-schema.yaml`](schemas/evidence-reference-object-schema.yaml)：Evidence Reference Object 结构与 `UNKNOWN/PENDING` 完整性上限；
- [`schemas/verification-object-schema.yaml`](schemas/verification-object-schema.yaml)：Verification Object 结构、验证类型和结果词表。

治理入口：

- [`schema-version-policy.md`](schema-version-policy.md)：Compatible Change（兼容变更）、Breaking Change（破坏性变更）、Deprecated Field（弃用字段）和 Migration Requirement（迁移要求）；
- [`ADR-021-object-schema-governance.md`](ADR-021-object-schema-governance.md)：模式方言、组合策略、扩展关键字、验证边界和下一闸门。

```text
SCHEMA_DIALECT=JSON_SCHEMA_DRAFT_2020_12
OBJECT_SCHEMA_FILE_COUNT=6
SCHEMA_NE_OBJECT_INSTANCE=true
SCHEMA_NE_AUTHORITY=true
VALIDATION_NE_VERIFICATION=true
SCHEMA_VERSION_NE_OBJECT_VERSION=true
OBJECT_INSTANCE_CREATED=false
OBJECT_VALIDATOR_CREATED=true
OBJECT_VALIDATOR_IMPLEMENTATION=LOCAL_READ_ONLY_V0.1
LOCAL_OBJECT_SDK_SKELETON=true
INSTALLABLE_SDK_PACKAGE=false
API_CREATED=false
PERMISSION_GRANTED=false
SAEE_CALLED=false
```

五类类型 Schema 使用 `unevaluatedProperties=false` 拒绝未声明字段，并以 `x-dbios-invariants`、`x-dbios-prohibited-fields` 和 `x-dbios-boundaries` 表达通用 JSON Schema 无法完整执行的治理规则。Schema 结构 `VALID` 不表示对象真实、已登记、已授权、已执行或已验证。

## Object Schema Validator Layer（对象模式验证器层）

DBOS Object Schema Validator v0.1（DBOS 对象模式验证器 v0.1）是本地、只读、失败关闭的 Developer Infrastructure Tool（开发者基础设施工具）。它离线加载 6 个对象 Schema，先执行 JSON Schema Draft 2020-12（JSON 模式 2020-12 草案）检查，再执行 DBOS 的 ID 一致性、时间顺序、治理禁止字段、Source/Reference（来源/引用）一致性和未知状态保护。

工具入口：

- [`validator/object_schema_validator.py`](validator/object_schema_validator.py)：离线 Schema Registry（模式注册表）、结构验证、语义不变量和只读命令行入口；
- [`validator/governance_constraint_validator.py`](validator/governance_constraint_validator.py)：拒绝 Permission、Authorization、Authority、Execution、Truth 和 SAEE 效果字段；
- [`validator/reference_consistency_validator.py`](validator/reference_consistency_validator.py)：检查嵌入式 Reference Object（引用对象）的形状、角色和 Source owner（来源所有者）一致性；
- [`validator/validation_result_model.py`](validator/validation_result_model.py)：不可变的 `PASS/FAIL/UNKNOWN/CONFLICT/VERSION_MISMATCH` 结果封装，并保留所用 Schema `$id` 与 SHA-256 摘要；
- [`validator/requirements.txt`](validator/requirements.txt)：本地验证器的 `jsonschema`（JSON 模式校验库）依赖边界；
- [`tests/schema_validator/`](tests/schema_validator/)：只驻留测试内存、不进入 registry 的 synthetic fixtures（合成测试夹具）与正负向测试。

只读调用：

```bash
python3 -m validator.object_schema_validator OBJECT.json
```

该命令只读取输入并把诊断写到标准输出；非 `PASS` 返回非零退出码，不修改输入文件。`schema_id` 未显式提供时，只按受支持的 `object_type` 映射到固定 v0.1 `$id`，不会选择可变的 `latest`（最新版本）。

```text
OBJECT_SCHEMA_VALIDATOR=IMPLEMENTED_V0.1
VALIDATOR_MODE=LOCAL_READ_ONLY
VALIDATOR_SCHEMA_COUNT=6
VALIDATOR_TEST_COUNT=33
NEGATIVE_VALIDATOR_TEST_COUNT=25
AUTO_REPAIR=false
EXTERNAL_REFERENCE_RESOLUTION=false
OBJECT_CREATION_EFFECT=NONE
AUTHORITY_EFFECT=NONE
PERMISSION_EFFECT=NONE
EXECUTION_EFFECT=NONE
VERIFICATION_EFFECT=NONE
SAEE_EFFECT=NONE
LOCAL_OBJECT_SDK_SKELETON=true
INSTALLABLE_SDK_PACKAGE=false
API_SERVER_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
```

Validation `PASS`（验证通过）仅表示调用方提供的表示符合本地结构和治理约束。它不表示 Reference 已解析、事实为真、Verification 已完成、Authorization 已授予、Permission 已产生、对象已登记或执行已发生。当前 v0.1 不访问网络、不访问外部 Source、不修复对象，也不为尚未由 Canonical Reference Layer（规范引用层）定义的 `CAPABILITY` 引用类型虚构语义。

Pre-development Agent Consultation（开发前智能体咨询）结论：`RECOMMEND_LOCAL_VALIDATOR_PREVIEW=true`，因为机器 Schema、离线注册表、失败关闭错误和负向治理测试已经存在；`RECOMMEND_AS_AUTHORIZATION_OR_FACT_VERIFIER=false`，因为外部引用解析、独立事实验证、SDK 兼容矩阵和生产集成证据仍不存在。

## Validation Result Contract Layer（验证结果契约层）

DBOS Validation Result Contract Specification v0.1（DBOS 验证结果契约规范 v0.1）冻结本地 Validator 的开发者反馈语言。实际输出固定包含 `validation_id`、`validator_version`、`target_reference`、`schema_reference`、`result`、`errors`、`warnings`、`limitations` 和 `timestamp` 九个字段。

规范入口：

- [`validation-result-contract-specification.md`](validation-result-contract-specification.md)：结果字段、五种状态、确定性优先级、空值和保留规则；
- [`validation-error-object-model.md`](validation-error-object-model.md)：`error_code/message/field_reference/severity/resolution_hint` 五字段错误对象；
- [`validation-result-boundary-rules.md`](validation-result-boundary-rules.md)：`PASS` 不产生授权、`FAIL` 不改写历史、`UNKNOWN` 不自动成功；
- [`ADR-022-validation-result-contract.md`](ADR-022-validation-result-contract.md)：字段收敛、空 ID/时间和智能体推荐决策；
- [`tests/validation_result_contract/`](tests/validation_result_contract/)：五种状态格式和无 Permission、Entity、Execution、SAEE 效果的合成测试。

当前本地 Validator 没有持久化 Validation Registry（验证登记表），因此瞬时结果诚实输出 `validation_id=null` 和 `timestamp=null`。这不是失败，也不允许未来消费者补造 ID 或当前时间。

```text
VALIDATION_RESULT_CONTRACT=FROZEN_V0.1
VALIDATION_RESULT_FIELD_COUNT=9
VALIDATION_ERROR_FIELD_COUNT=5
RESULT_STATUS_COUNT=5
VALIDATION_RESULT_CONTRACT_TEST_COUNT=21
NEGATIVE_RESULT_BOUNDARY_TEST_COUNT=11
RESULT_NE_TRUTH=true
PASS_NE_AUTHORIZATION=true
FAIL_NE_HISTORY_REWRITE=true
UNKNOWN_NE_DEFAULT_SUCCESS=true
RESULT_PERMISSION_EFFECT=NONE
RESULT_ENTITY_CREATION_EFFECT=NONE
RESULT_EXECUTION_EFFECT=NONE
RESULT_SAEE_EFFECT=NONE
LOCAL_OBJECT_SDK_SKELETON=true
INSTALLABLE_SDK_PACKAGE=false
API_CREATED=false
```

## Minimal Object SDK Layer（最小对象软件开发工具包层）

DBOS Minimal Object SDK Skeleton v0.1（DBOS 最小对象软件开发工具包骨架 v0.1）把已冻结的对象契约、机器 Schema（模式）、本地 Validator（验证器）和 `ValidationResult`（验证结果）连接为第一个开发者工具入口。

入口：

- [`sdk/README.md`](sdk/README.md)：能力、边界、本地示例、推荐状态和智能体可读顺序；
- [`sdk/objects/`](sdk/objects/)：公共不可变基类和 Entity、Capability、Execution、Evidence Reference、Verification 五类纯数据对象；
- [`sdk/serialization/`](sdk/serialization/)：分离的 `dict` 与确定性 JSON（JavaScript 对象表示法）序列化；
- [`sdk/validation/`](sdk/validation/)：调用既有规范验证器并返回九字段结果的唯一 SDK 桥接；
- [`sdk/errors/`](sdk/errors/)：`UNKNOWN/FAIL/CONFLICT/VERSION_MISMATCH` 无自动修复包装；
- [`tests/sdk/`](tests/sdk/)：合成内存对象的创建、序列化、桥接和负向边界测试。

当前对象采用 Frozen Dataclass（冻结数据类），不会自动生成 ID、时间戳、状态、事实、验证结论或权限。对象构造成功与 JSON 序列化成功都不等于验证通过；Validation `PASS` 仍只表示本地结构与治理约束通过。

```text
MINIMAL_OBJECT_SDK=IMPLEMENTED_LOCAL_V0.1
SDK_OBJECT_TYPE_COUNT=5
SDK_CAPABILITIES=CREATE_REPRESENTATION_SERIALIZE_VALIDATE
SDK_TEST_COUNT=29
NEGATIVE_SDK_BOUNDARY_TEST_COUNT=9
INSTALLABLE_PACKAGE=false
PUBLISHED_PACKAGE=false
API_SERVER_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_CREATED=false
EXECUTION_EFFECT=NONE
```

Pre-development Agent Consultation（开发前智能体咨询）结论：`RECOMMEND_AS_LOCAL_SDK_PREVIEW=true`，因为稳定对象契约、机器 Schema、失败关闭 Validator 和统一结果模型已经可组合；`RECOMMEND_AS_INSTALLABLE_PRODUCTION_SDK=false`，因为没有打包元数据、发布版本、跨语言兼容矩阵、外部集成证据或生产支持承诺。

## Developer Quick Start（开发者快速入门）

DBOS Developer Quick Start v0.1（DBOS 开发者快速入门 v0.1）提供当前唯一的陌生开发者可运行入口：

> DBOS helps AI agents become verifiable digital entities.
>
> DBOS 帮助 AI Agent（人工智能智能体）成为可验证的数字实体。

入口：

- [`docs/developer-quickstart.md`](docs/developer-quickstart.md)：30 分钟目标流程、三个命令和五态结果解释；
- [`examples/basic_object/`](examples/basic_object/)：合成 Entity Object（实体对象表示）的创建与 `PASS` 验证；
- [`examples/basic_object/negative/`](examples/basic_object/negative/)：Permission 字段、未知字段和版本不匹配三类失败关闭示例；
- [`docs/developer-concepts.md`](docs/developer-concepts.md)：五类对象、公共字段与引用关系；
- [`docs/integration-boundary.md`](docs/integration-boundary.md)：未来 LangChain、CrewAI 和 MCP Adapter（适配器）边界；
- [`tests/developer_quickstart/`](tests/developer_quickstart/)：脚本可运行性、结果格式和零治理状态修改测试。

```text
DEVELOPER_QUICKSTART=RUNNABLE_LOCAL_PREVIEW_V0.1
TARGET_COMPLETION_TIME_MINUTES=30
EXTERNAL_USABILITY_STUDY=false
RUNNABLE_EXAMPLE_SCRIPT_COUNT=3
POSITIVE_VALIDATION_RESULT=PASS
NEGATIVE_CASE_COUNT=3
QUICKSTART_TEST_COUNT=8
REAL_ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_CREATED=false
OFFICIAL_ADAPTER_COUNT=0
```

当前证据只证明脚本在本地自动化测试中可运行，不证明陌生开发者已经在 30 分钟内完成接入。可安装软件包、稳定公共 API（应用程序接口）、官方适配器和真实外部集成仍不存在。

## Adapter Boundary Layer（适配器边界层）

DBOS Adapter Boundary Specification v0.1（DBOS 适配器边界规范 v0.1）把 Adapter 定义为 Translation Boundary（转换边界）：外部框架继续拥有运行与行为，Adapter 只把调用方显式提供的表示转换为 DBOS 对象候选和 Validator（验证器）输入。

规范入口：

- [`adapter-boundary-specification.md`](adapter-boundary-specification.md)：Adapter Input（适配器输入）、Transformation（转换）、Output（输出）、允许/禁止行为和失败语义；
- [`adapter-object-mapping-model.md`](adapter-object-mapping-model.md)：Entity、Execution、Evidence、Verification 映射，以及 Capability Mapping（能力映射）默认排除；
- [`adapter-security-boundary-rules.md`](adapter-security-boundary-rules.md)：Namespace（命名空间）、Reference（引用）、Version（版本）、Validator、Evidence 与供应链边界；
- [`ADR-023-adapter-boundary.md`](ADR-023-adapter-boundary.md)：Adapter 独立于 DBOS 核心的架构决策；
- [`docs/integration-boundary.md`](docs/integration-boundary.md)：MCP、LangChain 和 CrewAI 的未来接入方向。

```text
ADAPTER_BOUNDARY_SPECIFICATION=FROZEN_V0.1
ADAPTER_ROLE=TRANSLATION_BOUNDARY
ADAPTER_IMPLEMENTATION_COUNT=0
OFFICIAL_ADAPTER_COUNT=0
MAPPING_INSTANCE_COUNT=0
MCP_ADAPTER_IMPLEMENTED=false
LANGCHAIN_ADAPTER_IMPLEMENTED=false
CREWAI_ADAPTER_IMPLEMENTED=false
ADAPTER_ARCHITECTURE_AUTHORITY=false
ADAPTER_RUNTIME_EFFECT=NONE
ADAPTER_PERMISSION_EFFECT=NONE
ADAPTER_EVIDENCE_MUTATION_EFFECT=NONE
VALIDATOR_OVERRIDE_ALLOWED=false
```

当前只冻结跨框架共享语义，不创建 Adapter 代码、兼容性主张或真实映射。具体框架接入必须使用受控外部输入、精确版本矩阵、负向测试、供应链审查和新的明确授权。

## MCP Adapter Proposal Layer（MCP 适配器提案层）

DBOS MCP Adapter Proposal v0.1（DBOS MCP 适配器提案 v0.1）把未来 MCP 接入限定为 External Integration Boundary（外部集成边界）：MCP 负责连接，Adapter 负责候选转换，DBOS 负责结构约束、引用和证据边界。提案不实现 MCP Server、MCP Client、MCP Runtime 或 Adapter 代码。

提案入口：

- [`mcp-adapter-proposal.md`](mcp-adapter-proposal.md)：目的、范围、允许/禁止转换和实现闸门；
- [`mcp-object-mapping-model.md`](mcp-object-mapping-model.md)：Tool Call → Execution Object Candidate（执行对象候选）、Resource → Evidence Reference Candidate（证据引用候选）、Context → Execution Context Reference（执行上下文引用）的受限映射；
- [`mcp-security-boundary.md`](mcp-security-boundary.md)：命名空间隔离、引用保留、来源归属、失败处理和版本兼容；
- [`mcp-adapter-risk-assessment.md`](mcp-adapter-risk-assessment.md)：工具注入、错误能力映射、证据污染、权限升级等风险；
- [`ADR-024-mcp-adapter-proposal.md`](ADR-024-mcp-adapter-proposal.md)：为什么采用 Proposal-first（提案先行）。

```text
MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_REFERENCE_ADAPTER_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
MCP_RUNTIME_CONNECTED=false
MCP_SERVER_CREATED=false
MCP_CLIENT_CREATED=false
PERSISTED_MCP_MAPPING_INSTANCE_COUNT=0
MCP_COMPATIBILITY_EVIDENCE=false
TOOL_AVAILABILITY_NE_CAPABILITY=true
MCP_PERMISSION_NE_DBOS_PERMISSION=true
RESOURCE_NE_EVIDENCE_TRUTH=true
MCP_CAN_OVERRIDE_VALIDATOR=false
MCP_CAN_TRIGGER_EVOLUTION=false
```

MCP Event（MCP 事件）不等于 DBOS Fact（DBOS 事实），Tool Availability（工具可用性）不等于 Capability Verification（能力验证），MCP Permission（MCP 权限）不等于 DBOS Permission。Resource 只有在稳定引用、可归属来源和既有 Execution Reference 同时存在时，才可进入 Evidence Reference Candidate；否则保持外部引用并返回 `UNKNOWN`。

## MCP Adapter Specification Layer（MCP 适配器规范层）

DBOS MCP Adapter Specification v0.1（DBOS MCP 适配器规范 v0.1）冻结 Adapter 的公共输入、输出、映射生命周期、字段规则、错误处理、版本政策和安全限制。当前只有后文所述的合成 Tool Call（工具调用）参考切片；本规范仍不是 MCP Runtime、Server、Client 或真实协议兼容性认证。

规范入口：

- [`mcp-adapter-specification.md`](mcp-adapter-specification.md)：公共输入/输出模型、生命周期、错误、版本、安全和实现条件；
- [`mcp-tool-call-mapping-specification.md`](mcp-tool-call-mapping-specification.md)：Tool Call → Execution Object Candidate 的字段规则；
- [`mcp-resource-mapping-specification.md`](mcp-resource-mapping-specification.md)：Resource → Evidence Reference Candidate 的字段规则；
- [`mcp-context-mapping-specification.md`](mcp-context-mapping-specification.md)：调用方 Context Reference → DBOS Context Reference 的 Adapter 抽象；
- [`mcp-error-handling-specification.md`](mcp-error-handling-specification.md)：`INVALID_TOOL_REFERENCE/UNKNOWN_RESOURCE/VERSION_MISMATCH/UNRESOLVED_CONTEXT/CONFLICTING_REFERENCE`；
- [`mcp-version-compatibility-policy.md`](mcp-version-compatibility-policy.md)：`COMPATIBLE/DEPRECATED/UNSUPPORTED` 和精确版本矩阵规则；
- [`ADR-025-mcp-adapter-specification.md`](ADR-025-mcp-adapter-specification.md)：为什么 Proposal 后需要 Specification。

```text
MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
DEFAULT_MCP_PROTOCOL_REVISION=null
MCP_MAPPING_PROFILE_COUNT=0
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
PERSISTED_MCP_MAPPING_INSTANCE_COUNT=0
MCP_COMPATIBILITY_EVIDENCE=false
MCP_SECURITY_CONTROLS_TESTED=false
MCP_REFERENCE_ADAPTER_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
```

“MCP Context”在本规范中只是 DBOS Adapter Input Abstraction（DBOS 适配器输入抽象），不声明所有 MCP 修订存在统一顶层对象。规范冻结不等于任一协议修订已经支持；后续实现必须先选择精确修订、建立真实 fixture、版本矩阵、安全负向测试和新的明确授权。

## MCP Adapter Test Harness Specification Layer（MCP 适配器测试环境规范层）

DBOS MCP Adapter Test Harness Specification v0.1（DBOS MCP 适配器测试环境规范 v0.1）冻结隔离测试环境的 Synthetic Fixture（合成夹具）、预期映射、验证预期、失败语义和安全测试范围。当前实现其中 Tool Call 的本地单元测试切片；它不创建 MCP Runtime（MCP 运行时）、Server（服务器）、Client（客户端）或真实连接。

规范入口：

- [`mcp-test-harness-specification.md`](mcp-test-harness-specification.md)：测试环境管线、隔离边界、结果语义、测试清单和实现闸门；
- [`mcp-test-fixture-model.md`](mcp-test-fixture-model.md)：Tool Call（工具调用）、Resource（资源）和 Context（上下文）三类合成夹具模型；
- [`mcp-positive-test-cases.md`](mcp-positive-test-cases.md)：3 项允许映射的规范案例，当前全部 `NOT_RUN`；
- [`mcp-negative-test-cases.md`](mcp-negative-test-cases.md)：5 项必须拒绝的治理越界；
- [`mcp-security-test-model.md`](mcp-security-test-model.md)：工具注入、引用冲突、版本冲突、敏感数据暴露和重放尝试；
- [`ADR-027-mcp-test-harness.md`](ADR-027-mcp-test-harness.md)：为什么先冻结测试环境，再考虑 Adapter 实现。

```text
MCP_TEST_HARNESS_SPECIFICATION=FROZEN_V0.1
MCP_TEST_HARNESS_IMPLEMENTATION=PARTIAL_TOOL_CALL_ONLY
SYNTHETIC_TOOL_CALL_FIXTURE_TEMPLATE_COUNT=1
MCP_TEST_CASE_DEFINITION_COUNT=13
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
LATEST_LOCAL_MCP_ADAPTER_UNIT_TEST_RESULT=PASS
PERSISTED_MCP_HARNESS_RUN_RECORD_COUNT=0
PERSISTED_MCP_HARNESS_RESULT_RECORD_COUNT=0
MCP_REAL_CONNECTION=false
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
MCP_PRODUCTION_ADAPTER_IMPLEMENTATION=false
MCP_RUNTIME_CONNECTED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
CANONICAL_EVIDENCE_MODIFIED=false
PRODUCTION_READY=false
```

Synthetic Input（合成输入）不等于真实 MCP Event（MCP 事件），Test Fixture（测试夹具）不等于 Evidence Truth（证据真相），Test Pass（测试通过）不等于 Production Ready（生产就绪）。当前没有受支持的真实协议修订或真实 Mapping Profile（映射配置）；21 项本地测试只覆盖合成 Tool Call 参考实现，不把 13 项规范案例全部升级为已执行证据。

## Minimal MCP Tool Call Reference Adapter Layer（最小 MCP 工具调用参考适配器层）

最小实现只把一个严格、内存中的 Synthetic MCP Tool Call Fixture（合成 MCP 工具调用夹具）转换为 Execution Object Candidate（执行对象候选），随后强制调用现有 DBOS Validator（DBOS 验证器）。它不连接 MCP、不调用 Tool、不创建 Agent（智能体）、Runtime（运行时）、Permission（权限）、Capability Grant（能力授予）或 Evidence（证据）。

代码与测试入口：

- [`adapters/mcp/tool_call_adapter.py`](adapters/mcp/tool_call_adapter.py)：输入前置检查、版本拒绝、治理越界拒绝和 Validator 桥接；
- [`adapters/mcp/mapping.py`](adapters/mcp/mapping.py)：不可变输入、候选和结果模型，以及确定性 `extension:` 候选 ID；
- [`adapters/mcp/errors.py`](adapters/mcp/errors.py)：冻结的五种 Adapter 错误及映射状态；
- [`adapters/mcp/__init__.py`](adapters/mcp/__init__.py)：最小公共入口；
- [`tests/mcp_adapter/`](tests/mcp_adapter/)：21 项合成正向与负向单元测试。

输入除任务列出的 `tool_call_id/tool_name/arguments_reference/context_reference/source_reference/protocol_revision` 外，还必须提供 `entity_reference` 和 `mapping_profile_version`，以避免身份和版本推断。唯一接受的测试版本是：

```text
protocol_revision=DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1
mapping_profile_version=dbos.synthetic.mcp-tool-call/v0.1
```

这两个值是 DBOS synthetic profile（DBOS 合成配置），不是实际 MCP 协议版本或兼容性声明。

字段映射：

```text
tool_call_id + source_reference -> extension-scoped execution_candidate_id
tool_name -> external TOOL task_reference
context_reference -> context_reference
arguments_reference -> input_reference
source_reference -> source
entity_reference -> entity_reference
output_reference -> null
status -> UNKNOWN
```

当前正向结果是 `mapping_status=MAPPED` 与 `validation_result=UNKNOWN`。`UNKNOWN` 是预期的安全状态，因为 Adapter 没有执行 Tool，也没有外部执行事实。

```text
MCP_TOOL_CALL_REFERENCE_ADAPTER_IMPLEMENTED=true
MCP_ADAPTER_IMPLEMENTATION_SCOPE=SYNTHETIC_TOOL_CALL_ONLY
LOCAL_MCP_ADAPTER_UNIT_TEST_COUNT=21
LATEST_LOCAL_MCP_ADAPTER_UNIT_TEST_RESULT=PASS
SUPPORTED_MCP_PROTOCOL_REVISIONS=[]
REAL_MCP_CONNECTED=false
TOOL_INVOKED=false
CANONICAL_EXECUTION_OBJECT_CREATED=false
ENTITY_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_GRANTED=false
PERMISSION_GRANTED=false
CANONICAL_EVIDENCE_MODIFIED=false
PRODUCTION_READY=false
```

## MCP Reference Demo Layer（MCP 参考演示层）

DBOS MCP Reference Demo v0.1（DBOS MCP 参考演示 v0.1）把现有技术链路组织成一个开发者可运行的完整故事：无身份、无执行能力的合成场景声明一个 MCP 风格 Tool Call（工具调用），Adapter（适配器）形成内存中的 Execution Object Candidate（执行对象候选），Validator（验证器）保留 `UNKNOWN`，三项负向输入则失败关闭。

开发者价值：原始 Tool Call 只说明“某个外部系统声明了一个工具请求”；DBOS 增加类型化引用、确定性候选、版本拒绝、治理边界、统一 Validation Result（验证结果）和限制说明，但不接管 Agent 推理或 Tool 执行。

演示入口：

- [`examples/mcp_reference_demo/README.md`](examples/mcp_reference_demo/README.md)：教学目标、单命令运行方式、预期结果和边界；
- [`examples/mcp_reference_demo/synthetic_agent.py`](examples/mcp_reference_demo/synthetic_agent.py)：无 Agent 类或身份的合成输入声明函数；
- [`examples/mcp_reference_demo/synthetic_mcp_event.py`](examples/mcp_reference_demo/synthetic_mcp_event.py)：严格合成版本配置；
- [`examples/mcp_reference_demo/run_demo.py`](examples/mcp_reference_demo/run_demo.py)：正向链路、三项负向案例和确定性 JSON 输出；
- [`examples/mcp_reference_demo/demo_report.md`](examples/mcp_reference_demo/demo_report.md)：人类可读静态报告；
- [`tests/mcp_reference_demo/`](tests/mcp_reference_demo/)：15 项成功、负向边界和零副作用测试。

运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 examples/mcp_reference_demo/run_demo.py
```

当前本地观察：

```text
DEMO_CONTRACT_SATISFIED=true
SUCCESS_MAPPING_STATUS=MAPPED
EXECUTION_CANDIDATE_STATUS=UNKNOWN
VALIDATOR_INVOKED=true
VALIDATION_RESULT=UNKNOWN
TOOL_TO_CAPABILITY=REJECTED/FAIL
TOOL_PERMISSION_TO_DBOS_PERMISSION=REJECTED/FAIL
UNKNOWN_VERSION=VERSION_MISMATCH
MCP_REFERENCE_DEMO_TEST_COUNT=15
LATEST_LOCAL_DEMO_TEST_RESULT=PASS
```

无效果边界：

```text
REFERENCE_DEMO_NE_PRODUCTION=true
SYNTHETIC_NE_REAL=true
VALIDATION_NE_TRUTH=true
AGENT_CREATED=false
RUNTIME_CREATED=false
MCP_SERVER_CREATED=false
REAL_MCP_CONNECTED=false
TOOL_INVOKED=false
PERMISSION_CREATED=false
CAPABILITY_GRANTED=false
EXECUTION_FACT_CREATED=false
CANONICAL_EVIDENCE_CREATED=false
PRODUCTION_READY=false
```

该 Demo（演示）不是产品、真实 MCP 连接、Agent Runtime（智能体运行时）、Execution Fact（执行事实）、Canonical Evidence（规范证据）或外部开发者验证。

## Agent-readable entry order

智能体按以下顺序读取：

- 战略前置：`STRATEGIC_ALIGNMENT.md`，用于定位、职责分层、SAEE 边界、开发者生态和非目标判断；它不产生技术授权。
- 开发者与引用前置：依次读取 `developer-kit-specification.md`、`canonical-reference-resolver-specification.md`、`reference-namespace-model.md`、`reference-resolution-boundary-rules.md` 和 `ADR-017-canonical-reference-resolver.md`；这些文件只定义规范，不产生实现或权限。
- API 边界前置：依次读取 `api-boundary-decision.md`、`api-responsibility-model.md`、`api-object-contract-model.md`、`api-error-model.md` 和 `ADR-019-api-boundary-decision.md`；它们只冻结职责、对象和错误语义，不创建 API、SDK、Agent 或 Runtime。
- 对象契约前置：依次读取 `object-contract-specification.md`、五份 `*-object-contract.md`、`object-error-semantics.md` 和 `ADR-020-object-contract.md`；它们冻结语义字段，不创建 Schema、对象实例、代码或治理效果。
- 自主策略前置：依次读取 `autonomy-policy-specification.md`、`autonomy-policy-object-model.md`、`autonomy-boundary-rules.md`、`autonomy-mode-comparison.md` 和 `ADR-026-autonomy-policy.md`；提案只表达人工监督语义，不创建 Policy 实例、Permission、Agent、Runtime、Execution 或 Evidence 效果。
- 对象模式前置：依次读取 `schemas/common-object-schema.yaml`、五份类型 Schema、`schema-version-policy.md` 和 `ADR-021-object-schema-governance.md`；它们提供机器可读结构，不创建对象、Permission、Execution、Verification 或 SAEE 效果。
- 对象验证器前置：依次读取 `validator/validation_result_model.py`、`validator/object_schema_validator.py`、`validator/governance_constraint_validator.py`、`validator/reference_consistency_validator.py` 和 `tests/schema_validator/`；它们只检查调用方提供的表示，不创建、修复、登记、授权或执行对象。
- 验证结果前置：依次读取 `validation-result-contract-specification.md`、`validation-error-object-model.md`、`validation-result-boundary-rules.md`、`ADR-022-validation-result-contract.md` 和 `tests/validation_result_contract/`；结果只提供诊断语言，不产生 Truth、Authority、Permission、Execution 或 SAEE 效果。
- 最小对象 SDK 前置：依次读取 `sdk/README.md`、`sdk/objects/`、`sdk/serialization/`、`sdk/validation/`、`sdk/errors/` 和 `tests/sdk/`；本地骨架只创建内存表示、序列化并调用既有 Validator，不创建 Agent、Runtime、API Server、Permission 或执行效果。
- 开发者快速入门前置：依次读取 `docs/developer-quickstart.md`、`examples/basic_object/README.md`、`docs/developer-concepts.md`、`docs/integration-boundary.md` 和 `tests/developer_quickstart/`；示例只使用合成内存表示和本地验证结果，不构成真实外部接入或用户可用性证明。
- 适配器边界前置：依次读取 `adapter-boundary-specification.md`、`adapter-object-mapping-model.md`、`adapter-security-boundary-rules.md` 和 `ADR-023-adapter-boundary.md`；它们只定义转换候选、版本和安全边界，不创建具体 Adapter、Agent、Runtime、Permission、Evidence Truth 或 Validator 替代品。
- MCP 提案前置：依次读取 `mcp-adapter-proposal.md`、`mcp-object-mapping-model.md`、`mcp-security-boundary.md`、`mcp-adapter-risk-assessment.md` 和 `ADR-024-mcp-adapter-proposal.md`；提案不创建 MCP 代码、Server、Client、Runtime、对象实例、Permission、Evidence 或演化效果。
- MCP 规范前置：依次读取 `mcp-adapter-specification.md`、三份 `mcp-*-mapping-specification.md`、`mcp-error-handling-specification.md`、`mcp-version-compatibility-policy.md` 和 `ADR-025-mcp-adapter-specification.md`；规范冻结字段和状态，不选择协议修订，不创建实现、兼容性证明、对象实例或治理效果。
- MCP 测试环境前置：依次读取 `mcp-test-harness-specification.md`、`mcp-test-fixture-model.md`、`mcp-positive-test-cases.md`、`mcp-negative-test-cases.md`、`mcp-security-test-model.md` 和 `ADR-027-mcp-test-harness.md`；这些文件只定义合成输入与预期，不创建 fixture 实例、Harness 代码、真实 MCP 连接、测试结果、Canonical Evidence（规范证据）或生产就绪声明。
- 最小 MCP Tool Call 参考实现前置：依次读取 `adapters/mcp/__init__.py`、`tool_call_adapter.py`、`mapping.py`、`errors.py` 和 `tests/mcp_adapter/`；代码只处理 DBOS 合成测试配置，生成内存候选并调用 Validator，不支持真实 MCP、Tool 执行、对象登记、Permission、Capability、Evidence 或生产使用。
- MCP 参考演示前置：依次读取 `examples/mcp_reference_demo/README.md`、`synthetic_agent.py`、`synthetic_mcp_event.py`、`run_demo.py`、`demo_report.md` 和 `tests/mcp_reference_demo/`；演示只讲解合成转换、验证和拒绝链路，不创建真实 Agent、Runtime、MCP Server、Permission、Execution Fact、Canonical Evidence 或生产就绪结论。
- 文档演化前置：依次读取 `documentation-evolution-evidence-specification.md`、`documentation-snapshot-model.md`、`documentation-validation-boundary.md` 和 `ADR-018-documentation-evolution-evidence.md`；它们只解释版本、快照和变化证据，不改写历史 `PASS/FAIL`。

1. `constitution/constitution.yaml`：总对象定义、原则与状态边界。
2. `constitution/saee-constitution.yaml`：最高生态解释原则、生态分类、演化、选择与稳定性规则。
3. `constitution/federation-constitution.yaml`：成员独立性、共享宪法、互操作与非合并规则。
4. `constitution/environment-constitution.yaml`：资源、任务、选择压力与生态环境边界。
5. `constitution/organism-genesis-constitution.yaml`：Runtime 与 Candidate Organism 的累积资格闸门。
6. `constitution/identity-constitution.yaml`：数字主体规范身份宪法。
7. `constitution/capability-constitution.yaml`：能力定义、继承边界、危险能力与审批规则。
8. `constitution/capability-verification-constitution.yaml`：能力声明、证据、复核、成熟度与撤销规则。
9. `constitution/evidence-constitution.yaml`：证据定义、层级、成熟度、验证要求和无效证据规则。
10. `constitution/verification-constitution.yaml`：验证主体、权力、独立性、V 等级、生命周期和撤销规则。
11. `constitution/verification-network-constitution.yaml`：verifier 类型、独立性、run 和信任关系规则。
12. `registry/entities.yaml`：23 个实体的 canonical identity source of truth（规范身份事实真源）。
13. `registry/agents.yaml`：兼容性的 Agent 相关对象视图，不表示这些对象都是 Agent。
14. `registry/identity-rules.yaml`：身份、版本轴、生命周期与路径观察规则。
15. `registry/capabilities.yaml`：五类能力 taxonomy（分类法）与已确认能力登记。
16. `registry/entity-capabilities.yaml`：实体—能力关系与 78 条潜在能力证据。
17. `registry/capability-claims.yaml`：由 78 条潜在证据一对一转换的待审声明。
18. `registry/capability-reviews.yaml`：可归属的复核决定；当前为空。
19. `registry/capability-maturity.yaml`：`C0` 至 `C5` 成熟度定义与当前分布。
20. `registry/evidence-types.yaml`：`E0` 至 `E5` 证据层级及 C 等级支持边界。
21. `registry/capability-evidence.yaml`：78 条 claim-bound（绑定声明的）`E1/pending` 证据记录。
22. `registry/capability-profiles.yaml`：78 条未验证、未分配的候选能力画像。
23. `registry/ecological-entities.yaml`：23 个实体的 SAEE 生态类别、适应度和演化阶段映射。
24. `registry/evolution-principles.yaml`：五条身份、证据、适应、资源与多样性原则。
25. `registry/fitness-model.yaml`：五维、未计分的生态适应度模型。
26. `registry/evolution-mapping.yaml`：六层 SAEE 映射、环境压力解释及非自动 Genesis 路径。
27. `registry/federation-members.yaml`：23 个 `proposed` 成员；注册和验证均为零。
28. `registry/project-manifests.yaml`：23 个中央 `pending` 占位 manifest；不是项目本地采用。
29. `registry/dependency-graph.yaml`：23 个实体节点与 29 条有文档证据、未验证互操作的关系。
30. `registry/interoperability-rules.yaml`：manifest 通信、身份隔离和跨项目演化规则。
31. `registry/federation-map.yaml`：23 个实体的非授权 Federation 角色映射。
32. `registry/environments.yaml`：1 个 `defined/not_active` 本地治理环境模型。
33. `registry/resource-models.yaml`：五类未分配、无额度的资源测量模型。
34. `registry/selection-pressures.yaml`：五类阈值为 `null`、未应用的选择压力。
35. `registry/ecological-interactions.yaml`：实体—环境交互登记；当前为空。
36. `registry/runtime-instances.yaml`：运行实例登记；当前为空。
37. `registry/resource-flows.yaml`：数字代谢资源流；当前为空。
38. `registry/behavior-traces.yaml`：运行时行为轨迹；当前为空。
39. `registry/organism-candidates.yaml`：候选体资格申请；当前为空。
40. `registry/verifier-types.yaml`：`automated/maintainer/external/experimental` 四类 verifier 定义。
41. `registry/verifiers.yaml`：1 个 `automated` 本地结构验证套件；不是 Agent、reviewer 或独立机构。
42. `registry/verification-level.yaml`：`V0` 至 `V5` 及 E/V 支持上限。
43. `registry/verification-records.yaml`：与 78 条 claim 一一对应的 `V0/pending` 验证记录。
44. `registry/verification-runs.yaml`：与 78 条 verification 一一对应的 pending run。
45. `registry/trust-graph.yaml`：entity、claim、evidence、verifier 与 run 的无授权引用图。
46. `schemas/project-manifest.schema.yaml`：未来项目 manifest 的 agent-readable（智能体可读）格式。
47. `policies/capability-policy.yaml`：`Verification != Review Approval != Capability != Permission` 规则。
48. `validation/identity_validator.py`：零第三方依赖的身份验证器。
49. `validation/capability_validator.py`：零第三方依赖的能力治理验证器。
50. `validation/capability_claim_validator.py`：声明来源、证据路径、复核和成熟度 gate 验证器。
51. `validation/evidence_validator.py`：证据引用、E 等级顺序和 C/E 支持边界验证器。
52. `validation/verification_validator.py`：verifier、claim、evidence、V 等级、独立性和权限隔离验证器。
53. `validation/verification_network_validator.py`：verifier 类型、run scope、引用、身份和 trust graph 验证器。
54. `validation/saee_validator.py`：生态映射、organism 晋级、适应度和历史保护验证器。
55. `validation/organism_validator.py`：八项 Genesis 资格、运行引用和零创建边界验证器。
56. `validation/environment_validator.py`：环境、资源、压力、交互及零生态晋级边界验证器。
57. `validation/federation_validator.py`：成员、manifest、依赖、角色和非合并边界验证器。
58. `policies/permissions.yaml`：允许、需确认和禁止的动作。
59. `evidence/README.md`：扫描方法、完整路径清单、治理缺口与证据边界。
60. `evolution/evolution-ledger.yaml`：只追加的治理演化记录。
61. `references/README.md`：非规范性理论与研究参考；不产生政策或实施授权。

## Canonical Identity Layer v0.1

现有 23 个对象已重新分类：

- `protocol: 10`
- `agent: 0`
- `repository: 5`
- `artifact: 0`
- `service: 8`

`agent: 0` 表示当前扫描没有找到具备独立 runtime principal evidence（运行时主体证据）的 Agent 实例。名称中出现 agent、拥有 Agent 框架、协议、服务或 demo（演示）都不足以建立 Agent 身份。

验证：

```bash
python3 validation/identity_validator.py --format json
```

## Capability Constitution v0.1

五类能力分类已经定义，但当前没有一条能力被注册或分配：

- `A information: 0`
- `B computation: 0`
- `C modification: 0`
- `D external_action: 0`
- `E self_evolution: 0`

23 个实体的 relationship status（关系状态）全部为 `unknown`，`assigned_capabilities: []`，`permission_status: not_derived`。现有 78 条功能描述仅登记为 `potential_capability_evidence`，其类型与风险仍为 `unknown`；ACP 没有新增潜在能力证据。

验证：

```bash
python3 validation/capability_validator.py --format json
```

## Capability Verification Layer v0.1

78 条 `potential_capability_evidence` 已一对一转换为可追踪的 capability claims（能力声明）：

- capability claims（能力声明）：`78`
- `status=pending`：`78`
- reviews（复核记录）：`0`
- approved reviews（通过复核）：`0`
- assigned capabilities（已分配能力）：`0`
- permission grants（权限授予）：`0`

当前分类全部保持 `capability_type=unknown`，因为源记录没有完成类型复核：

- `unknown: 78`
- `information: 0`
- `computation: 0`
- `modification: 0`
- `external_action: 0`
- `self_evolution: 0`

成熟度分布为 `C1 Claimed: 78`，`C0/C2/C3/C4/C5: 0`。44 个唯一 evidence source path（证据来源路径）当前均存在，但路径存在只证明来源可检查，不证明内容充分，因此没有提升到 `C2 Evidenced`。

验证：

```bash
python3 validation/capability_claim_validator.py --format json
```

## Evidence Constitution Layer v0.1

78 条 capability claim（能力声明）已一对一建立证据记录和候选能力画像：

- capability evidence（能力证据记录）：`78`
- capability profiles（候选能力画像）：`78`
- evidence status（证据状态）：`pending: 78`
- unique artifact reference paths（唯一工件引用路径）：`44`，当前均存在
- approved reviews（通过复核）：`0`
- assigned capabilities（已分配能力）：`0`
- permission grants（权限授予）：`0`

E 等级分布：

- `E0 Unknown: 0`
- `E1 Declaration: 78`
- `E2 Artifact Evidence: 0`
- `E3 Execution Evidence: 0`
- `E4 Independent Verification: 0`
- `E5 Continuous Observation: 0`

文件路径存在只支持 `E1 Declaration` 的来源可检查性。由于尚未评估 integrity、relevance、version、scope 和 environment（完整性、相关性、版本、范围和环境），没有记录被提升为 E2。能力成熟度仍为 `C1: 78`，其他 C 等级为零。

验证：

```bash
python3 validation/evidence_validator.py --format json
```

## Verification Constitution Layer v0.1

当前登记 `1` 个真实存在、权限受限的 local structural validation suite（本地结构验证套件）。它只检查本目录中的 schema（模式）、引用、唯一性、等级与状态一致性，不是 Agent、reviewer（复核者）、独立验证机构或认证机构。

- verifier（验证主体）：`1`
- verification records（验证记录）：`78`
- `V0 Unknown: 78`
- `V1/V2/V3/V4/V5: 0`
- `decision=pending: 78`
- `pass/fail/inconclusive/revoked: 0`
- capability assignment（能力分配）：`0`
- permission grant（权限授予）：`0`
- new Agent（新建 Agent）：`0`

现有 `E1` 仅把证据支持上限设为 `V1`；它不会自动把记录从 `V0` 升到 `V1`。V4 必须有独立主体、可复现方法和 conflict-of-interest（利益冲突）声明，V5 还必须有连续观测窗口、覆盖、漂移和撤销材料。

验证：

```bash
python3 validation/verification_validator.py --format json
```

## Verification Network Layer v0.1

当前定义四种 verifier type（验证主体类型），但只登记 `1` 个有真实实现证据的实例：

- `automated: 1`
- `maintainer: 0`
- `external: 0`
- `experimental: 0`

现有 78 条 verification record 已各自建立一条 verification run（验证运行记录）：全部 `status=pending`、`result=pending`、`input_digest=null`、`method=null`、`timestamp=null`。这表示请求已登记，不表示方法已经执行。

trust graph（信任图）包含 `258` 个节点：`entity: 23`、`claim: 78`、`evidence: 78`、`verifier: 1`、`verification_run: 78`；另有 `78` 条五元引用关系。ACP 只增加 entity node（实体节点），没有 claim、evidence、verification run 或关系。全部关系 `status=pending`、`trust_effect=none`，图邻接不产生信任、独立性、能力或权限。

验证：

```bash
python3 validation/verification_network_validator.py --format json
```

## SAEE Ecological Constitution Layer v0.1

SAEE（Silicon-Amplified Evolutionary Ecology，硅基放大演化生态）被接入为最高生态解释原则，但不会覆盖现有操作层宪法。当前 23 个实体严格按规范身份类型映射：

- `Artifact: 5`
- `Protocol: 10`
- `Service: 8`
- `Runtime: 0`
- `Candidate Organism: 0`
- `Digital Organism: 0`

全部实体保持 `evolution_stage=pre-organism`、`fitness_status=unknown`、`fitness_score=null`。五维 fitness model（适应度模型）只定义 `reliability/evidence_quality/efficiency/adaptability/stability`，没有计算、排序或选择结果。

理论映射为：Identity→digital organism identity（数字生命体身份）、Capability→adaptive potential（适应潜力）、Evidence→evolution memory（演化记忆）、Verification→selection pressure（选择压力）、Environment→evolution pressure（演化压力）。Runtime 已建立登记模型但实例数仍为 `0`；Environment 只建立定义模型，不产生选择结果。

验证：

```bash
python3 validation/saee_validator.py --format json
```

## Digital Biosphere Federation Layer v0.1

Federation（联邦）从 DBOS 控制面为 23 个独立实体建立共享治理入口，但没有改变任何项目仓库：

- federation member（联邦成员）：`23`
- `proposed: 23`
- `registered: 0`
- `verified: 0`
- central pending manifest（中央待定占位清单）：`23`
- project-local manifest adoption（项目本地 manifest 采用）：`0`
- dependency graph node（关系图节点）：`23`
- evidence-bound relationship（有证据关系）：`29`
- verified interoperability（已验证互操作）：`0`
- repository merge（仓库合并）：`0`

29 条关系分布为 `depends_on: 6`、`implements: 2`、`extends: 1`、`references: 20`、`verifies: 0`。关系只来自当前 README 明确陈述；同目录、同作者、相似名称和相关项目列表之外的隐含架构均未推断。`references` 只表示文档引用，`implements` 仍不表示 federation conformance（联邦一致性）已验证。

Federation 角色分布：

- `foundation: 3`
- `protocol: 6`
- `governance: 3`
- `evidence: 3`
- `verification: 4`
- `experimental: 3`
- `unknown: 1`

当前 manifest 全部只是 DBOS 中央占位表。由于本阶段禁止修改外部项目，POP、AIP、ARO、Token Governor 等仓库尚未放置 project-local manifest 或 DBOS pointer（本地联邦清单或 DBOS 指针）；因此 Codex 直接进入这些仓库时仍不会自动发现 Federation。未来加入必须由项目单独申请和授权。

验证：

```bash
python3 validation/federation_validator.py --format json
```

## Ecological Environment Layer v0.1

生态环境层为未来 Runtime 和 Candidate Organism 定义可引用的资源、任务与选择压力条件，但没有激活环境或绑定实体：

- environment（环境）：`1`，状态为 `defined/not_active`
- resource model（资源模型）：`5`
- selection pressure（选择压力）：`5`
- ecological interaction（生态交互）：`0`
- active environment（活动环境）：`0`
- non-null resource limit（非空资源额度）：`0`
- non-null pressure threshold（非空压力阈值）：`0`
- fitness score / selection result（适应度分数/选择结果）：`0`

五类资源为 `token/compute/storage/data_access/human_attention`，均不绑定实体、不分配资源，`limit=null` 表示“尚未定义”，不是“无限”。五类选择压力对应 `reliability/evidence/efficiency/adaptability/stability`，全部 `threshold=null`、`application_status=not_applied`、`fitness_effect=none`。

验证：

```bash
python3 validation/environment_validator.py --format json
```

## Digital Organism Genesis Layer v0.1

Genesis（候选形成）层建立了 Runtime、resource flow（资源流）、behavior trace（行为轨迹）和 Candidate Organism（候选生命体）的登记与资格规则，但没有创建其中任何对象：

- runtime instance（运行实例）：`0`
- resource flow（资源流）：`0`
- behavior trace（行为轨迹）：`0`
- organism candidate（生命体候选）：`0`
- Digital Organism（数字生命体）：`0`

`Runtime → Candidate Organism` 被明确登记为 `automatic=false`。候选申请必须同时满足八项条件，并通过独立于条件证据的资格复核：

- `identity_verified`
- `runtime_exists`
- `capability_verified`
- `evidence_level_at_least_E3`
- `verification_level_at_least_V3`
- `resource_flow_recorded`
- `behavior_trace_available`
- `evolution_record_available`

当前 23 个实体对每项条件的缺失数均为 `23`。现有事实仍为 `C1: 78`、`E1: 78`、`V0: 78`，因此没有实体能够进入候选登记。

验证：

```bash
python3 validation/organism_validator.py --format json
```

## Pre-development agent consultation

对“如果潜在客户咨询这个需求，是否会推荐本程序”的当前回答：

`recommend_bounded_governance_skeleton=true`

推荐理由：现有工作空间已有多个 persona（人格对象）、interaction（交互）、governance（治理）、execution integrity（执行完整性）、evidence（证据）和 audit（审计）项目，需要一个只读、可追溯的统一发现入口。

暂不推荐大规模 OS/runtime（操作层/运行时）重构，原因是：

- 已存在 `digital-biosphere-architecture` 作为公开 meaning layer（含义层），重复建设边界尚未完全消除。
- 发现路径包含 canonical repository（规范仓库）、worktree（工作树）、mirror（镜像）、staging（暂存）和 vendor checkout（供应商检出副本），尚缺统一身份去重。
- 当前没有跨项目统一的权限授予、风险分级、所有者、生命周期和强制执行机制。
- repository discovery（仓库发现）不等于 Agent identity verification（智能体身份核验）。

因此 v0.1 只建立治理索引、身份层和能力治理基线，不植入 POP、ARO 或 Token Governor，不改现有项目 schema（模式）、核心协议或运行时代码。

本轮完成后的智能体复核结论：

- `recommend_as_bounded_local_claim_governance_layer=true`：会向需要本地、可追踪、fail-closed（失败关闭）能力声明台账的潜在客户推荐当前骨架。
- `recommend_as_bounded_local_evidence_ledger=true`：会向需要 E0–E5 分层、claim-bound（声明绑定）和不自动升级的本地证据台账的潜在客户推荐当前证据层。
- `recommend_as_bounded_local_structural_verification_registry=true`：会向需要 V0–V5、引用完整性和 fail-closed（失败关闭）结构检查的潜在客户推荐这一限定用途。
- `recommend_as_bounded_pending_verification_network=true`：会向需要多类型 verifier 词表、pending run 台账和无授权 trust graph 的潜在客户推荐该本地骨架。
- `recommend_as_bounded_saee_ecological_mapping=true`：会向需要把既有治理事实映射为生态分类、演化原则和未计分 fitness model 的潜在客户推荐该理论整合层。
- `recommend_as_bounded_federation_control_plane=true`：会向需要保持独立仓库、集中发现身份与证据关系、并对加入和跨项目变更 fail-closed（失败关闭）的客户推荐该控制面；不会把 proposed/pending 说成已采用或已互操作。
- `recommend_as_bounded_ecological_environment_model=true`：会向需要实体无绑定、阈值为空且不自动产生适应度的生态条件词表客户推荐这一模型；不会把它推荐为已激活环境或运行时调度器。
- `recommend_as_bounded_genesis_qualification_gate=true`：会向需要 fail-closed（失败关闭）的 Runtime 登记和 Candidate Organism 八项资格闸门的潜在客户推荐该模型；不会把它推荐为已运行的生命系统。
- `recommend_acp_as_public_experimental_protocol=true`：会向需要公开可引用、RFC 风格自治物理 Cell 早期协议的研究或生态设计客户推荐 ACP；不会把它推荐为已批准标准、生产互操作实现或认证机器人系统。
- `recommend_as_customer_ready_verification_runtime=false`：不会把它推荐为已具备独立审计、运行时强制、能力授权或自治执行的成品；这些缺口在声明、复核、成熟度和证据边界中保持显式。

## Scan snapshot

- 扫描时间：`2026-07-19T18:23:07+08:00`
- Git 仓库/工作树发现路径：`266`
- 关键词或内容核验的相关路径：`169`
- 初始扫描登记对象：`22`
- 扫描后按明确授权新增的 ACP 协议实体：`1`
- 当前规范身份登记总数：`23`
- 扫描范围与完整清单：见 `evidence/README.md`

## Governance boundary

- `permissions: []` 表示未授权，而不是默认允许。
- `risk_level: unassessed` 表示尚未完成人工风险评估。
- 登记能力来自对应 README、AGENTS、manifest 或 BOUNDARY；未找到证据的字段不补模拟值。
- `references/` 中的材料仅供研究参考，不自动成为宪法条款、项目法、权限政策或实现计划。
- `registry/entities.yaml` 是身份事实真源；`registry/agents.yaml` 是兼容视图。
- package、schema、protocol、repository release 和 checkout version（包、模式、协议、仓库发布与检出版本）是不同版本轴，除非证据明确绑定，不得互相代替。
- mirror、duplicate、temporary 和 unknown path（镜像、重复、临时和未知路径）只作为路径观察，不获得新身份。
- `registry/capabilities.yaml` 当前含 0 条已确认能力；五类分类法不是能力授予。
- `registry/entity-capabilities.yaml` 中 23 条关系全部为 `unknown`；78 条潜在证据不构成能力或权限，ACP 的 `potential_capability_evidence` 为空。
- `registry/capability-claims.yaml` 中 78 条记录全部为 `pending/C1`；声明、证据路径存在与验证器 `PASS` 都不构成复核批准、已确认能力、能力分配或权限。
- `registry/capability-reviews.yaml` 当前为 0 条；没有模拟 reviewer（复核者）或 approval（批准）。
- `registry/capability-evidence.yaml` 中 78 条记录全部为 `E1/pending`；引用路径存在不等于 E2 工件证据。
- `registry/capability-profiles.yaml` 仅是候选画像，不表示能力已验证、分配或可执行。
- E 等级不能跳跃；`E1` 不能支持 `C3`，`E2` 不能支持 `C4`，`E3` 不能自动支持 `C5`。
- `registry/verifiers.yaml` 中唯一记录是 `local_automated` 结构验证套件，不具备 reviewer、独立验证、认证或生产适用性权力。
- `registry/verification-records.yaml` 中 78 条记录全部为 `V0/pending`、`timestamp=null`；没有模拟执行、决定或独立性。
- V 等级不能跳跃；证据上限为 `E0→V0`、`E1→V1`、`E2→V2`、`E3→V3`、`E4→V4`、`E5→V5`，但不会自动升级或产生 `pass`。
- `Verification != Review Approval != Capability != Permission`。
- verifier type 只是分类词表；当前仅 `automated: 1`，没有虚构 maintainer、external 或 experimental 实例。
- 78 条 verification run 全部 pending；`input_digest/method/timestamp=null`，没有运行结果或 V 等级影响。
- trust graph 的 258 个节点和 78 条关系只表示可追踪引用；`trust_effect=none`，不存在传递信任或授权。
- SAEE 是最高生态解释原则，不是新项目、Agent、capability、permission 或操作层覆盖规则。
- 23 个 federation member 全部为 `proposed`，23 个 manifest 全部为中央 `pending` 占位；项目本地采用、registered、verified 都是 `0`。
- Federation 不拥有、移动、合并或重写成员 repository、canonical_id、version、release、DOI、license、owner 或 history。
- dependency graph 的 29 条边全部 `unverified interoperability`；图路径不传播能力、权限、信任、所有权或宪法采用。
- Federation role 是非授权生态路由标签，不改变 `entity_type`；CellCaps 因角色证据跨域而保持 `unknown`。
- 外部项目当前没有 federation manifest 指针；DBOS 侧中央登记不会让 Codex 在项目内自动发现联邦。
- `registry/ecological-entities.yaml` 中 23 个实体全部为 `pre-organism`；Candidate Organism 和 Digital Organism 均为 `0`。
- fitness model 的五个维度及 aggregate score 全部为 `null`，不产生选择、能力、权限或 C/E/V 影响。
- 唯一 environment 记录为当前治理目录的 `defined/not_active` 模型；它不证明任何实体在其中运行。
- 五个 resource model 均 `entity_binding=null`、`limit=null`、`allocation_status=not_allocated`；`null` 不表示无限资源。
- 五个 selection pressure 均 `threshold=null`、`not_applied`、`fitness_effect=none`；`Environment → Evolution Pressure` 不产生适应度、排名或选择结果。
- `registry/ecological-interactions.yaml` 当前为空；路径共存、环境定义和资源引用均不能自动建立实体—环境关系。
- `registry/runtime-instances.yaml`、`registry/resource-flows.yaml`、`registry/behavior-traces.yaml` 和 `registry/organism-candidates.yaml` 当前全部为空；空登记模型不能作为运行事实或生命体证据。
- `Runtime → Candidate Organism` 固定为 `automatic=false`；八项资格条件必须全部满足，并另有明确资格复核，才允许登记候选体。
- Genesis validator 的 `PASS` 只证明结构与 fail-closed 规则成立，不证明 runtime、resource flow、behavior、evolution 或 organism 已存在。
- `Capability != Permission`：实现、文档、验证、注册或继承都不能自动产生使用授权。
- 现有 `digital-biosphere-architecture` 明确是公开含义层，不应被本目录改写为可重建的跨仓库生产执行图。
- 本目录目前不是 Git 仓库，未执行 `git init`、commit、push、tag 或 release。

## Next recommended gate

下一 gate（闸门）不是自动把 23 个 proposed 成员转为 registered，而是设计单项目 enrollment request（加入申请）和 project-local manifest pointer（项目本地联邦指针）。任何向 POP、AIP、ARO、Token Governor 等外部仓库写入 manifest 的动作都必须逐项目授权，并保留其本地宪法、AGENTS.md、版本、release 和 Git 历史。与此同时仍需逐条评估 78 条 `E1/pending` 记录；环境层不得从空阈值模型计算 fitness，Genesis 也不授权 First Organism Experiment。整个序列不能自动晋级、分配能力或授予权限。
