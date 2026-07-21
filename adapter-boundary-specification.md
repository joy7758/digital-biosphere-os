# DBOS Adapter Boundary Specification v0.1（DBOS 适配器边界规范 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

实现状态：`NOT_IMPLEMENTED`

官方 Adapter（适配器）数量：`0`

## 1. Purpose（目的）

Adapter 是 Translation Boundary（转换边界）：它把调用方显式提供的外部框架表示转换为 DBOS Object Candidate（DBOS 对象候选表示）和可供现有 Validator（验证器）检查的输入。

```text
External Framework Representation（外部框架表示）
  -> Adapter Input（适配器输入）
  -> explicit transformation（显式转换）
  -> DBOS Object Candidate（DBOS 对象候选表示）
  -> canonical Validator（规范验证器）
  -> ValidationResult（验证结果）
```

Adapter 不运行外部框架，不拥有外部对象，不签发 DBOS 身份，不写入规范 registry（登记表），也不把候选表示升级为真实、已登记或已验证对象。

## 2. Definitions（定义）

### Adapter Input（适配器输入）

调用方显式提交的外部对象、事件或引用，以及解释它所需的来源、版本、范围和限制。输入默认是不可信声明，不是 Evidence Truth（证据事实结论）。

最低概念信息：

```text
external_namespace
external_system
external_system_version
external_object_type
external_object_id
source_reference
mapping_profile_reference
declared_scope
limitations
```

这些是规范字段方向，不是本阶段创建的 Schema（模式）、类或对象实例。

### Adapter Transformation（适配器转换）

按照显式、版本化 Mapping Profile（映射配置）执行的确定性字段转换。允许的转换步骤只有：

1. 读取调用方提交的值；
2. 保留外部 ID、Namespace（命名空间）和 Source（来源）；
3. 把已声明字段映射到现有五类 DBOS 对象契约；
4. 无法证明的值保持 `UNKNOWN`、`null` 或明确缺失；
5. 记录丢失信息、冲突、版本限制和转换限制；
6. 产生供 Validator 检查的分离表示。

转换不得查询或修改未声明来源，不得依据类名、目录、框架品牌或路径相似性推断规范身份。

### Adapter Output（适配器输出）

输出只能是：

- 一个或多个现有 DBOS Object Contract（对象契约）的候选表示；
- 对应的来源与映射限制；
- 供规范 Validator 使用的验证输入；
- 无法安全映射时的结构化失败。

候选表示不是新对象类型，也不是 `registry/entities.yaml` 中的规范记录：

```text
OBJECT_CANDIDATE_NE_CANONICAL_ENTITY=true
OBJECT_CANDIDATE_NE_REGISTRATION=true
OBJECT_CANDIDATE_NE_VERIFICATION=true
OBJECT_CANDIDATE_NE_PERMISSION=true
```

## 3. Allowed Behaviors（允许行为）

Adapter 可以：

- Convert External Events（转换外部事件）：把已发生事件中的显式字段映射为惰性执行候选表示；
- Map References（映射引用）：保留外部 Namespace 与 ID，并生成受限 DBOS Reference Object（引用对象）；
- Create DBOS Object Candidates（创建 DBOS 对象候选表示）：在内存或调用方草稿中形成五类现有对象契约的候选表示；
- Produce Validation Input（生成验证输入）：序列化候选表示并交给规范 Validator；
- Report Mapping Limitations（报告映射限制）：记录未映射字段、冲突、来源和版本边界。

“创建候选表示”不等于创建真实 Entity（实体）、Execution（执行）、Evidence（证据）或 Verification（事实验证）。

## 4. Forbidden Behaviors（禁止行为）

Adapter 禁止：

- Create Agent（创建智能体）；
- Create Runtime（创建运行时）或启动任务、模型、工具；
- Grant Permission（授予权限）、Capability Grant（能力授予）或 Authority（权力）；
- Modify Evidence Truth（修改证据事实），覆盖或删除历史材料；
- Override Validator（绕过验证器），伪造 `PASS` 或缩减核心规则；
- Execute Evolution（执行演化）、计算选择或改变生态状态；
- 使用 `dbio` Namespace 冒充规范来源；
- 自动登记 Entity、升级 Lifecycle（生命周期）或激活对象；
- 把外部框架的 role、tool、server、run 或 callback 自动解释为 DBOS Agent、Capability、Permission 或 Verification。

## 5. Validation Boundary（验证边界）

所有候选表示必须进入现有 `validator.validate_object()`。Adapter 可以展示原始映射错误，但不能复制一套较弱的 DBOS Validator，也不能把 Adapter 自测结果命名为 DBOS `ValidationResult`。

```text
ADAPTER_OUTPUT_REQUIRES_VALIDATION=true
ADAPTER_SELF_CHECK_NE_DBOS_VALIDATION=true
VALIDATION_PASS_NE_REGISTRATION=true
VALIDATION_PASS_NE_AUTHORIZATION=true
VALIDATION_PASS_NE_TRUTH=true
```

Validator 返回 `PASS` 后，候选表示仍需独立的身份、证据、复核、授权或登记过程。Adapter 本身没有这些权力。

## 6. Failure Semantics（失败语义）

Adapter 必须失败关闭：

| 条件 | 结果上限 | 禁止行为 |
|---|---|---|
| 输入形状或 Namespace 非法 | `INVALID/FAIL` | 猜测正确字段 |
| 来源、Owner 或必需信息缺失 | `UNKNOWN` | 填入默认身份或成功 |
| 外部 ID、映射目标或 Source 冲突 | `CONFLICT` | 按顺序选择任一目标 |
| 外部系统、映射配置或对象契约版本不兼容 | `VERSION_MISMATCH` | 自动选择 `latest` |
| Validator 拒绝候选 | 原样保留结果 | 自动修复后静默重试 |

错误提示可以建议人工修正输入，但不得改写输入、历史记录或 Validator 结果。

## 7. Independence from DBOS Core（与 DBOS 核心独立）

Adapter 必须：

- 独立版本化、可替换、可撤销；
- 声明 Owner（所有者）、Source repository（来源仓库）、License（许可证）和支持版本；
- 不成为 DBOS 核心依赖或单点规范来源；
- 不因维护、发布或商业支持获得 Architecture Authority（架构权力）；
- 在不可用、撤销或受攻击时，不影响 DBOS 规范身份与历史 Evidence。

第三方 Adapter 的 `PASS` 最多证明其声明范围内的映射或结构检查，不证明 DBOS、外部框架或生产环境兼容。

## 8. Framework-neutral Rule（框架中立规则）

MCP（Model Context Protocol，模型上下文协议）、LangChain 和 CrewAI 必须分别提案、分别版本化、分别提供输入样本与负向证据。三者共享本规范，但任何一方都不能改变通用对象语义。

```text
CURRENT_MCP_ADAPTER=false
CURRENT_MCP_ADAPTER_PROPOSAL=ACCEPTED_V0.1
CURRENT_MCP_ADAPTER_SPECIFICATION=FROZEN_V0.1
CURRENT_LANGCHAIN_ADAPTER=false
CURRENT_CREWAI_ADAPTER=false
CURRENT_ADAPTER_CODE=false
CURRENT_ADAPTER_COMPATIBILITY_EVIDENCE=false
```

## 9. Pre-development Agent Consultation（开发前智能体咨询）

结论：

```text
RECOMMEND_ADAPTER_BOUNDARY_SPECIFICATION=true
RECOMMEND_CONCRETE_ADAPTER_IMPLEMENTATION=false
RECOMMEND_AS_RUNTIME=false
RECOMMEND_AS_PERMISSION_SYSTEM=false
```

推荐先冻结公共边界，因为外部框架到 DBOS 对象模型的转换是可复用基础设施问题。不推荐立即实现具体 Adapter，因为当前没有受控外部样本、框架版本矩阵、映射兼容证据、供应链审查或外部试点授权。

## 10. MCP Proposal Entry（MCP 提案入口）

MCP Adapter Proposal v0.1（MCP 适配器提案 v0.1）是本通用边界下的框架专属提案，不是 Adapter 实现、MCP Runtime（MCP 运行时）、MCP Server（MCP 服务器）或 MCP Client（MCP 客户端）。

- `mcp-adapter-proposal.md`：定位、范围、禁止效果和未来实现闸门；
- `mcp-object-mapping-model.md`：Tool Call（工具调用）、Resource（资源）与 Context（上下文）的候选映射；
- `mcp-security-boundary.md`：命名空间、引用、来源、失败和版本安全边界；
- `mcp-adapter-risk-assessment.md`：工具注入、错误能力映射、证据污染和权限升级等风险；
- `ADR-024-mcp-adapter-proposal.md`：采用 Proposal-first（提案先行）而不直接实现的决策。

该提案不改变 `CURRENT_MCP_ADAPTER=false`。MCP Resource 只有在具备稳定引用、可归属来源和既有 Execution Reference（执行引用）时，才可成为 Evidence Reference Candidate（证据引用候选）；否则必须保留为外部资源引用并返回 `UNKNOWN`。

## 11. MCP Specification Entry（MCP 规范入口）

MCP Adapter Specification v0.1（MCP 适配器规范 v0.1）冻结具体转换合同，但不创建 Adapter 实现或协议兼容性声明：

- `mcp-adapter-specification.md`：公共输入、输出、生命周期、安全和无效果规则；
- `mcp-tool-call-mapping-specification.md`：Tool Call 到 Execution Object Candidate 的字段规则；
- `mcp-resource-mapping-specification.md`：Resource 到 Evidence Reference Candidate 的字段规则；
- `mcp-context-mapping-specification.md`：调用方上下文引用的 Adapter 抽象；
- `mcp-error-handling-specification.md`：五种错误、确定性优先级和失败关闭规则；
- `mcp-version-compatibility-policy.md`：`COMPATIBLE/DEPRECATED/UNSUPPORTED` 及空兼容矩阵；
- `ADR-025-mcp-adapter-specification.md`：为什么 Proposal 后必须冻结 Specification。

当前 `SUPPORTED_MCP_PROTOCOL_REVISIONS=[]`、`MCP_MAPPING_INSTANCE_COUNT=0`、`CURRENT_MCP_ADAPTER=false`。规范存在不能被解释为支持任一协议修订、已经实现或可用于生产。

## 12. Related Specifications（关联规范）

- `adapter-object-mapping-model.md`
- `adapter-security-boundary-rules.md`
- `ADR-023-adapter-boundary.md`
- `object-contract-specification.md`
- `canonical-reference-resolver-specification.md`
- `reference-namespace-model.md`
- `docs/integration-boundary.md`
- `developer-extension-model.md`
- `mcp-adapter-proposal.md`
- `ADR-024-mcp-adapter-proposal.md`
- `mcp-adapter-specification.md`
- `ADR-025-mcp-adapter-specification.md`
