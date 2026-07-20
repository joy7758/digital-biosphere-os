# Evidence and workspace scan

本目录记录 Digital Biosphere OS v0.1 的真实扫描范围和发现边界。它不是对每个仓库的完整安全审计，也不把路径发现升级为能力验证、运行状态、发布状态或权限授权。

## Scan method

扫描时间：`2026-07-19T18:23:07+08:00`

扫描根：

- `/Users/zhangbin/GitHub`
- `/Users/zhangbin` 下与 `GitHub` 同级的非隐藏、非系统项目目录

方法：

- 通过 `.git` 目录或文件发现 Git repository/worktree（仓库/工作树）路径。
- 对路径名中的 `agent`、`protocol`、`mcp`、`governance`、`audit`、`persona`、`runtime`、`biosphere`、`saee` 关键词进行匹配。
- 额外核验 README/AGENTS/llms/BOUNDARY 等入口，补入名称未直接命中但内容明确相关的项目。
- 不读取密钥内容，不运行现有项目代码，不运行测试，不修改现有仓库。
- iCloud 镜像和迁移暂存路径仅做路径级发现；未对其 hydration（本地实体化）、hash（哈希）或 Git 状态作真实性升级。

排除的扫描根：用户主目录中的隐藏工具状态、`Library`、应用与媒体目录。非项目依赖目录（如 `node_modules`、虚拟环境、`DerivedData`）在同级目录扫描中被剪枝；`GitHub` 树内已发现的嵌套依赖仍保留在完整路径清单中，以免隐瞒扫描事实。

## Counts

- Git repository/worktree 发现路径：`266`
- 关键词或内容核验的相关路径：`169`
- 写入 `registry/agents.yaml` 的证据支持对象：`22`

路径数不是独立项目数，也不是 Agent 数。完整清单包含隔离工作树、镜像、迁移暂存、构建依赖、vendor（供应商）副本和生成目录中的嵌套仓库。

## Verified primary objects

以下对象已通过本地 README、AGENTS、llms、manifest 或 BOUNDARY 支撑并写入 registry：

- Digital Biosphere Architecture
- Persona Object Protocol (POP)
- Agent Intent Protocol (AIP)
- Token Governor
- FDO Kernel MVK
- Agent Evidence
- ARO-Audit
- Verifiable Agent Demo
- Execution Integrity Core
- Agent Evidence Receipt
- SAEE Agent Readiness Capability
- Agent Governance Toolkit
- Agent Governance Benchmark
- Agent Receipt Validator MCP
- Agent Accountability Evidence Layer
- Agent Object Protocol
- Execution Compact Layer
- CellCaps
- PRA-Server
- standalone Agent Object Protocol draft at `/Users/zhangbin/agent`
- Sovereign Agent local gate workflow
- mcp-agent external framework checkout

注：上面实际为 22 条 registry 记录；其中包含 meaning layer（含义层）、protocol（协议）、reference（参考实现）、benchmark（基准）、external checkout（外部检出）和 local workflow（本地工作流），不应全部称为 autonomous agents（自主智能体）。

## Same-level non-Git findings

- `/Users/zhangbin/AgentEvidence`：发现本地运行证据目录，无顶层 README、无 `.git`；未登记为 Agent。扫描仅查看文件名，未读取其中任何凭据内容。
- `/Users/zhangbin/sovereign-agent`：发现有内容的本地 gate workflow（门控工作流），无 `.git`；依据 `BOUNDARY.md` 登记为本地工作流。
- `/Users/zhangbin/pop-persona-cockpit-inbox`：空目录，未登记。
- `/Users/zhangbin/上帝之矛`：空目录，未登记。
- `/Users/zhangbin/Documents/宪法项目`：发现 Git 元数据但工作树无治理文件，保持未分类。
- `/Users/zhangbin/SAEE-c1-baseline-commit-isolated-001`、`SAEE-c1-baseline-recovery-001`、`SAEE-d1-baseline-recovery-001`、`SAEE-openai-build-week-2026`：发现为 SAEE 相关独立路径；初始 registry 不把它们升级为新的 canonical（规范）Agent 身份。

## Current governance gaps

1. **Canonical identity gap（规范身份缺口）**：主仓库、worktree、mirror、staging、vendor 和生成目录缺少统一去重键。
2. **Agent identity gap（智能体身份缺口）**：多数项目只声明仓库角色，没有跨项目统一的 Agent ID、owner、authority 和实例/类区分。
3. **Permission gap（权限缺口）**：没有证据表明已有跨项目 permission assignment（权限授予）或统一执行器；因此 registry 全部保持未授权。
4. **Risk gap（风险缺口）**：没有统一风险 rubric（量表）和人工签署结果；因此 risk_level 全部为 `unassessed`。
5. **Evidence normalization gap（证据规范化缺口）**：README、AGENTS、manifest、ledger、receipt 与本地 artifact（工件）的格式和状态语义不统一。
6. **Lifecycle gap（生命周期缺口）**：缺少统一的 discovered/verified/active/suspended/deprecated/retired 状态与变更规则。
7. **Sensitive-artifact boundary（敏感工件边界）**：在未版本化的本地证据目录中发现看似私钥/凭据的文件名；未读取内容。后续必须先定义隔离、轮换、保留与禁止登记规则。
8. **Public/private boundary（公开/私有边界）**：现有 Digital Biosphere Architecture 明确禁止将公开仓库拼接为可重建的端到端生产执行图，新治理层必须保持该边界。
9. **Enforcement gap（强制执行缺口）**：`permissions.yaml` 当前仅为声明，不是 OS、Git、CI、MCP 或 runtime 强制机制。

## Next recommendations

1. 为每个主项目建立 canonical ID、owner、authoritative repository、mirror/worktree relationship（镜像/工作树关系）和 lifecycle state。
2. 为 `agents.yaml` 与 `permissions.yaml` 增加 JSON Schema 和只读 validator（验证器），但在人工确认前不修改现有项目 schema。
3. 人工评审当前 23 条登记对象的 risk_level 和最小权限；不得由扫描程序自动授予。
4. 把敏感本地 evidence store（证据存储）从可发现 registry 元数据中分离，只登记受控引用，不复制私钥或凭据。
5. 完成去重和权限基线后，再设计 ARO execution credential layer；复用现有 POP、ARO、Token Governor 和 Execution Integrity Core，不另造同名实现。

## Canonical Identity Layer v0.1 evidence

初始身份升级严格复用原有 22 条扫描对象；在后续明确授权的 ACP identity-only registration（仅身份登记）之后，当前分类为：

- `protocol: 10`
- `agent: 0`
- `repository: 5`
- `artifact: 0`
- `service: 8`

扫描路径中有 163 条被登记为非实体 path observations（路径观察）：

- `duplicate: 5`
- `mirror: 24`
- `temporary: 113`
- `unknown: 21`

这些观察没有 `entity_id` 或 `canonical_id`。分类依据来自原扫描路径、仓库入口、版本文件和 Git remote namespace（远程命名空间）；远程命名空间只记录为 `repository_namespace_only`，不是所有权证明。

当前身份缺口：

1. 23 条身份均为 `lifecycle.state=proposed`，尚无 owner/authority 的完整人工确认。
2. 没有发现可验证的 runtime agent instance（运行时 Agent 实例），所以 `agent: 0`。
3. POP 和 Agent Evidence 等项目存在 package/schema/protocol/release version（包/模式/协议/发布版本）轴混合或冲突，不能压成一个未经证明的版本。
4. 当前没有证据支持新增 artifact identity（工件身份）；demo 与 benchmark 仍按扫描到的 repository surface（仓库表面）登记。
5. `parent_entity`、`child_entities` 与 `successor` 暂为空，避免根据生态邻接关系编造身份继承。

身份事实真源：`registry/entities.yaml`  
身份规则：`registry/identity-rules.yaml`  
验证器：`validation/identity_validator.py`

## Capability Constitution v0.1 evidence

能力层读取了当前 23 条实体登记及 `registry/agents.yaml` 中原有的 78 条功能描述；新增 ACP 记录没有功能描述或潜在能力证据。为避免把文档描述升级成自治能力，当前结果是：

- confirmed capability（已确认能力）：`0`
- assigned capability（已分配能力）：`0`
- unknown entity-capability relationships（未知实体—能力关系）：`23`
- potential capability evidence（潜在能力证据）：`78`
- permission derived（自动推导权限）：`0`

五类 taxonomy（分类法）当前计数均为零：

- `A information: 0`
- `B computation: 0`
- `C modification: 0`
- `D external_action: 0`
- `E self_evolution: 0`

风险发现：

1. 原 `agents.yaml` 的 capability 字段是扫描期摘要，不是安装、部署、可达、可调用或成功执行证据。
2. MCP、CLI、validator、demo、schema 和 package（MCP、命令行、验证器、演示、模式和包）混合出现在描述中，尚未拆分能力主体、环境与版本轴。
3. modification、external_action、self_evolution（修改、外部动作、自我演化）被设为危险类型，但没有任何实体被归入这些类型。
4. information 和 computation（信息、计算）在涉及凭据、隐私、生产、安全、财务、医疗、法律或身份时仍可能是高风险。
5. 当前只有 potential evidence，缺少统一 capability evidence bundle（能力证据包）、独立复核和人工批准记录。

能力宪法：`constitution/capability-constitution.yaml`  
能力登记：`registry/capabilities.yaml`  
实体关系：`registry/entity-capabilities.yaml`  
能力政策：`policies/capability-policy.yaml`  
验证器：`validation/capability_validator.py`

## Capability Verification Layer v0.1 evidence

能力验证层保留 `registry/entity-capabilities.yaml` 中全部 78 条原始 `potential_evidence_only` 记录，并在 `registry/capability-claims.yaml` 中进行一对一、可逆追踪转换：

- source potential evidence（源潜在证据）：`78`
- capability claims（能力声明）：`78`
- unique source evidence paths（唯一来源路径）：`44`
- 当前存在的来源路径：`44`
- 缺失来源路径：`0`
- `pending` 声明：`78`
- review（复核）记录：`0`
- approved review（通过复核）：`0`
- capability assignment（能力分配）：`0`
- permission grant（权限授予）：`0`

分类统计：

- `unknown: 78`
- `information: 0`
- `computation: 0`
- `modification: 0`
- `external_action: 0`
- `self_evolution: 0`

成熟度分布：

- `C0 Unknown: 0`
- `C1 Claimed: 78`
- `C2 Evidenced: 0`
- `C3 Verified: 0`
- `C4 Governed: 0`
- `C5 Autonomous: 0`

未解决问题与风险：

1. 78 条声明的 `capability_type`、`scope`、`environment` 和 `side_effect` 全部保持 `unknown`；未经证据充分性评估不得自动分类。
2. 44 个来源路径存在，但尚未逐条评估内容是否证明候选能力、对应哪个版本或处于 local/demo/released/deployed/production（本地/演示/发布/部署/生产）中的哪一层。
3. 当前没有 reviewer、review decision、limitations 或 timestamp（复核者、决定、限制或时间戳），所以没有声明可进入 `C3 Verified`。
4. 当前没有 policy binding、risk control、monitoring、revocation mechanism 或 runtime enforcement evidence（政策绑定、风险控制、监控、撤销机制或运行时强制证据），所以没有声明可进入 `C4` 或 `C5`。
5. 声明转换不创建 `capability_id`，不改变当前 23 条实体—能力关系的 `unknown` 状态，也不授予能力或权限。

能力验证宪法：`constitution/capability-verification-constitution.yaml`  
声明登记：`registry/capability-claims.yaml`  
复核登记：`registry/capability-reviews.yaml`  
成熟度登记：`registry/capability-maturity.yaml`  
验证器：`validation/capability_claim_validator.py`

## Evidence Constitution Layer v0.1 evidence

证据层将 78 条 `pending/C1` capability claims（能力声明）一对一登记为 `E1 Declaration`，没有改变 claim、review、capability、permission 或 Agent 状态：

- capability evidence records（能力证据记录）：`78`
- candidate capability profiles（候选能力画像）：`78`
- unique artifact reference paths（唯一工件引用路径）：`44`
- 当前存在的引用路径：`44`
- 缺失引用路径：`0`
- `pending` evidence：`78`
- approved review：`0`
- registered capability：`0`
- assigned capability：`0`
- permission grant：`0`
- new Agent：`0`

E 等级分布：

- `E0 Unknown: 0`
- `E1 Declaration: 78`
- `E2 Artifact Evidence: 0`
- `E3 Execution Evidence: 0`
- `E4 Independent Verification: 0`
- `E5 Continuous Observation: 0`

对应 capability maturity（能力成熟度）分布保持：

- `C0 Unknown: 0`
- `C1 Claimed: 78`
- `C2 Evidenced: 0`
- `C3 Verified: 0`
- `C4 Governed: 0`
- `C5 Autonomous: 0`

新风险与未解决问题：

1. 44 个文件路径存在只证明来源当前可检查；没有逐条完成内容相关性、hash（哈希）、签名、版本、范围或环境绑定，因此不能称为 E2。
2. 当前没有 inputs、outputs、result、timestamp、environment 或 side effects（输入、输出、结果、时间戳、环境或副作用）构成的执行记录，因此 E3 为零。
3. 当前没有满足独立性标准的 reviewer、方法、复现结果与 limitations（限制），因此 E4 为零。
4. 当前没有 observation window、coverage、drift、incident、expiry 或 revocation（观测窗口、覆盖率、漂移、事件、到期或撤销）记录，因此 E5 为零。
5. 78 条 capability profiles 只是未验证的候选画像；其中 scope 和 environment 仍为 `unknown`，不得用作能力目录、路由或执行授权。
6. E 等级与 C 等级是不同轴：E1 不能支持 C3，E2 不能支持 C4，E3 不能自动支持 C5；任何 E 等级都不授予权限。

证据宪法：`constitution/evidence-constitution.yaml`  
证据类型：`registry/evidence-types.yaml`  
证据登记：`registry/capability-evidence.yaml`  
候选画像：`registry/capability-profiles.yaml`  
验证器：`validation/evidence_validator.py`

## Verification Constitution Layer v0.1 evidence

验证层建立一个真实存在但权力受限的 local structural validation suite（本地结构验证套件），并为现有 78 条 capability claim（能力声明）建立一对一的待验证记录。没有运行或模拟逐条验证决定：

- verifier：`1`
- verifier type：`automated: 1`
- trust level：`local_automated: 1`
- verification records：`78`
- referenced evidence records：`78`
- `decision=pending: 78`
- `pass/fail/inconclusive/revoked: 0`
- assigned capability：`0`
- permission grant：`0`
- new Agent：`0`

V 等级分布：

- `V0 Unknown: 78`
- `V1 Self Check: 0`
- `V2 Automated Validation: 0`
- `V3 Reproducible Verification: 0`
- `V4 Independent Verification: 0`
- `V5 Continuous Verification: 0`

新风险与未解决问题：

1. 唯一 verifier 只能核验本目录的 schema、引用、唯一性、层级与状态一致性；它不能批准能力、授予权限、认证外部项目或形成生产适用性结论。
2. 该 verifier 由本目录实现并运行，`independence_status=not_independent`；不能支撑 V4。
3. 78 条记录全部是 `V0/pending`、`timestamp=null`，没有伪造 method output、reviewer、独立性或执行完成证据。
4. 当前 E1 证据最高只允许进入 V1；达到支持上限不产生自动升级或 `pass`。
5. V3 尚缺可复现输入、方法、环境和结果；V4 尚缺独立主体与利益冲突记录；V5 尚缺观测窗口、覆盖、漂移、事件、到期和撤销材料。
6. `Verification != Review Approval != Capability != Permission`；验证结果不能改变当前 78 条 `C1/pending` claim、78 条 `E1/pending` evidence、0 review 和 0 capability 的事实。
7. v0.1 是每条 claim 一条 `V0` 基线记录；进入更高 V 等级前必须先定义追加式等级历史和 verifier run（验证运行）记录，不能原地覆盖待验证历史。

验证宪法：`constitution/verification-constitution.yaml`  
verifier 登记：`registry/verifiers.yaml`  
等级登记：`registry/verification-level.yaml`  
验证记录：`registry/verification-records.yaml`  
验证器：`validation/verification_validator.py`

## Verification Network Layer v0.1 evidence

本层在不新增 verifier 实例的前提下定义四种 verifier type，并把 78 条现有 verification record 一对一连接到 pending run：

- verifier type definitions：`4`
- registered verifiers：`1`
- `automated: 1`
- `maintainer/external/experimental: 0`
- verification runs：`78`
- `status=pending/result=pending: 78`
- completed run：`0`
- trust graph nodes：`258`
- trust graph relationships：`78`
- established trust：`0`
- assigned capability / permission grant / new Agent：均为 `0`

trust graph 节点分布：

- `entity: 23`
- `claim: 78`
- `evidence: 78`
- `verifier: 1`
- `verification_run: 78`

新风险与未解决问题：

1. 四种类型只是 taxonomy；没有证据支持新增 maintainer、external 或 experimental verifier 实例。
2. external verifier 未来必须提供可检查的 identity evidence（身份证据），但 external 类型本身仍不能证明 V4 独立性。
3. 所有 run 都没有 input digest、已执行 method、output evidence 或 timestamp，因此不能称为执行记录或验证结果。
4. 唯一 automated verifier 的 scope 仅为 `local_registry_only`；不能验证外部项目、runtime、deployment 或 production（运行时、部署或生产）事实。
5. trust graph 关系全部 pending 且 `trust_effect=none`；路径和邻接不能推导信任、独立性、能力、权限或认证。
6. verification run 与 trust graph 没有改变 `V0: 78`、`E1: 78`、`C1: 78`、0 review、0 capability 的基线。

网络宪法：`constitution/verification-network-constitution.yaml`  
类型登记：`registry/verifier-types.yaml`  
run 登记：`registry/verification-runs.yaml`  
trust graph：`registry/trust-graph.yaml`  
验证器：`validation/verification_network_validator.py`

## SAEE Ecological Constitution Layer v0.1 evidence

SAEE 映射使用当前 23 条 canonical identity（规范身份）事实和本地理论参考；ACP 仅作为明确授权的协议身份引用，未修改外部项目代码。保守映射结果：

- `Artifact: 5`
- `Protocol: 10`
- `Service: 8`
- `Runtime: 0`
- `Candidate Organism: 0`
- `Digital Organism: 0`

Evolution stage（演化阶段）分布：

- `pre-organism: 23`
- `candidate-organism: 0`
- `digital-organism: 0`
- `ecologically-retired: 0`

Fitness model 结构：

- `reliability: score=null`
- `evidence_quality: score=null`
- `efficiency: score=null`
- `adaptability: score=null`
- `stability: score=null`
- `aggregate_fitness: score=null`

新风险与未解决问题：

1. 当前只有 repository、protocol 和 service 身份证据，没有 active runtime principal（活动运行时主体）证据，因此 Runtime 为零。
2. 没有 entity 满足或申请 organism qualification（生命体资格）；Candidate Organism 和 Digital Organism 均为零。
3. interaction、resource flow、adaptation lineage 和 ecological stability（交互、资源流、适应谱系与生态稳定性）目前是理论维度，没有运行时观测数据。
4. fitness model 没有测量方法、权重、基线、窗口或独立复核，因此不得计算分数、排名或选择结果。
5. SAEE 只是最高生态解释层；Identity、Capability、Evidence、Verification 和 permission 的现有操作权威保持不变。
6. SAEE 整合没有改变 `C1: 78`、`E1: 78`、`V0: 78`、0 review、0 capability、0 permission 和 0 Agent 的事实。

SAEE 宪法：`constitution/saee-constitution.yaml`  
生态实体：`registry/ecological-entities.yaml`  
演化原则：`registry/evolution-principles.yaml`  
适应度模型：`registry/fitness-model.yaml`  
层级映射：`registry/evolution-mapping.yaml`  
验证器：`validation/saee_validator.py`

## Digital Organism Genesis Layer v0.1 evidence

Genesis（候选形成）层只把运行事实和候选资格所需的数据结构变成可审计登记入口，没有从项目描述、生态分类或验证器结果模拟任何运行实例：

- runtime instance（运行实例）：`0`
- resource flow（资源流）：`0`
- behavior trace（行为轨迹）：`0`
- organism candidate（生命体候选）：`0`
- Digital Organism（数字生命体）：`0`

当前 23 个实体的资格缺失分布：

- `identity_verified: 23`
- `runtime_exists: 23`
- `capability_verified: 23`
- `evidence_level_at_least_E3: 23`
- `verification_level_at_least_V3: 23`
- `resource_flow_recorded: 23`
- `behavior_trace_available: 23`
- `evolution_record_available: 23`

缺失条件依据：

1. 23 条 canonical identity（规范身份）的当前验证状态均为 `evidence_backed_provisional`，不是 Genesis 所需的 `verified`。
2. 当前 78 条 capability claim 均为 `C1/pending`，没有达到 `C3 Verified` 的 capability evidence（能力证据）。
3. 当前证据等级为 `E1: 78`、验证等级为 `V0: 78`，低于 Genesis 的 `E3/V3` 最低门槛。
4. runtime、resource flow 与 behavior trace 登记均为空，不能从 README、协议或服务身份推导运行事实。
5. 追加式演化台账目前没有绑定某一实体与某一 runtime 的 `subject_entity_id` 演化记录。
6. `Runtime → Candidate Organism` 为 `automatic=false`；满足八项条件后仍须有单独的 qualification review（资格复核）。

Genesis 宪法：`constitution/organism-genesis-constitution.yaml`  
运行实例：`registry/runtime-instances.yaml`  
资源流：`registry/resource-flows.yaml`  
行为轨迹：`registry/behavior-traces.yaml`  
候选体：`registry/organism-candidates.yaml`  
验证器：`validation/organism_validator.py`

## ACP identity-only registration evidence

`2026-07-19T22:26:53+08:00` 按明确用户授权，将 Autonomous Cell Protocol（ACP，自治细胞协议）登记为 1 条 proposed protocol entity（拟议协议实体）。本记录是在初始 22 对象扫描之后追加，不改写初始扫描事实。

- `entity_id: autonomous-cell-protocol`
- `canonical_id: dbio://protocol/autonomous-cell-protocol/v0.1.0-alpha`
- `entity_type: protocol`
- `lifecycle.state: proposed`
- `owner.status: repository_namespace_only`
- repository：`/Users/zhangbin/GitHub/海洋/autonomous-cell-protocol`
- release evidence（发布证据）：`v0.1.0-alpha` tag、`VERSION`、`CITATION.cff` 中的版本 DOI `10.5281/zenodo.21442282`
- specification boundary（规范边界）：`ACP-0001` 仍为 Draft — Pending Human Approval；`ACP-0002` 至 `ACP-0005` 仍为占位草案

接入后当前身份总数为 `23`，其中 `protocol: 10`、`agent: 0`。ACP 的能力关系保持 `unknown`，`capabilities: []`、`assigned_capabilities: []`、`permissions: []`、`potential_capability_evidence: []`；没有创建 claim、E/V 等级、验证结果、Runtime、Candidate Organism 或 Digital Organism。

结构验证器的 `PASS` 只证明 DBOS 内部登记与引用一致，不证明 ACP 技术正确、身份已获治理批准、能力成立、实现存在或生产互操作完成。

## Ecological Environment Layer v0.1 evidence

环境层把当前 DBOS 治理工作目录登记为一个 `defined/not_active` 环境模型。证据仅为目录路径当前存在；这不证明任何实体、Runtime 或任务在该环境中运行。

- environment：`1`
- `defined: 1`
- `active: 0`
- resource model：`5`
- entity-bound resource model：`0`
- non-null resource limit：`0`
- selection pressure：`5`
- non-null threshold：`0`
- applied pressure：`0`
- ecological interaction：`0`
- known fitness score：`0`
- selection result：`0`

资源模型分布：

- `token: 1`
- `compute: 1`
- `storage: 1`
- `data_access: 1`
- `human_attention: 1`

选择压力分布：

- `reliability_pressure: 1`
- `evidence_pressure: 1`
- `efficiency_pressure: 1`
- `adaptability_pressure: 1`
- `stability_pressure: 1`

新风险与未解决问题：

1. 当前 measurement（测量）字段只是规范词汇，没有采集器、校准、基线、误差模型、观测窗口或独立复核。
2. 所有 resource limit（资源额度）和 pressure threshold（压力阈值）均为 `null`；`null` 表示未知，不表示无限或零成本。
3. `data_access` 只是测量类型，不授予数据访问；未来仍须经过独立的隐私、安全和 permission（权限）治理。
4. `human_attention` 尚无人员同意、角色、时间核算、隐私和劳动边界，不能被用于真实评价。
5. 当前没有 entity-environment interaction（实体—环境交互）、resource flow、Runtime 或行为轨迹，因此不能应用选择压力或计算 fitness。
6. `Environment → Evolution Pressure` 只是 SAEE 理论映射；环境定义和 validator `PASS` 都不构成生态选择或演化事实。

环境宪法：`constitution/environment-constitution.yaml`  
环境登记：`registry/environments.yaml`  
资源模型：`registry/resource-models.yaml`  
选择压力：`registry/selection-pressures.yaml`  
生态交互：`registry/ecological-interactions.yaml`  
验证器：`validation/environment_validator.py`

## Digital Biosphere Federation Layer v0.1 evidence

Federation 层复用当前 23 条 canonical entity identity（规范实体身份），没有新增实体或修改成员项目。所有成员只处于 proposed（拟议）状态：

- federation member：`23`
- `proposed: 23`
- `registered: 0`
- `verified: 0`
- central pending manifest：`23`
- project-local manifest：`0`
- dependency graph node：`23`
- evidence-bound relationship：`29`
- verified interoperability：`0`
- repository merge：`0`

关系类型分布：

- `depends_on: 6`
- `implements: 2`
- `verifies: 0`
- `extends: 1`
- `references: 20`

关系证据仅来自当前明确命名目标项目或架构角色的 README 片段。主要来源包括：

- AIP README 的 `Depends on`：POP、Token Governor、MVK、ARO-Audit。
- Agent Governance Benchmark README 的 local sibling repositories：Token Governor、ARO-Audit。
- Agent Evidence README 的 Architecture、Demo、Audit、FDO MVK bridge 说明。
- Verifiable Agent Demo README 的 Architecture、Agent Evidence 与 POP→AIP→ARO walkthrough 图。
- Execution Integrity Core README 的 POP profile binding 说明。
- SAEE README 的 Agent Evidence Receipt 架构归属说明，同时明确没有源代码或 runtime 迁移。

Federation 角色分布：

- `foundation: 3`
- `protocol: 6`
- `governance: 3`
- `evidence: 3`
- `verification: 4`
- `experimental: 3`
- `unknown: 1`

新风险与未解决问题：

1. 23 个 manifest 都是 DBOS 侧中央占位表，不是由成员仓库提交或采用；constitution reference（宪法引用）不等于项目同意。
2. 外部项目没有 project-local manifest 或 DBOS discovery pointer，因此 Codex 直接进入 POP、AIP、ARO、Token Governor 等仓库时仍不能自动发现联邦上下文。
3. 29 条关系是文档证据，不是版本绑定的 schema compatibility、conformance、执行成功或独立互操作验证。
4. `references` 边只表示文档引用；`implements` 和 `extends` 也不会自动产生能力、权限、身份继承、所有权或 verified interoperability。
5. Federation role 是中央非授权路由标签；CellCaps 的角色证据跨 foundation/evidence/verification，当前保持 `unknown`。
6. 跨项目 change request、逐仓库 authorization、rollback 和 execution evidence 仍未建立，Federation 当前不能执行跨仓库修改。

Federation 宪法：`constitution/federation-constitution.yaml`  
成员登记：`registry/federation-members.yaml`  
中央 manifest：`registry/project-manifests.yaml`  
依赖图：`registry/dependency-graph.yaml`  
互操作规则：`registry/interoperability-rules.yaml`  
角色映射：`registry/federation-map.yaml`  
manifest schema：`schemas/project-manifest.schema.yaml`  
验证器：`validation/federation_validator.py`

## All discovered Git repository/worktree paths

- `/Users/zhangbin/Documents/宪法项目`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/AB-AEB`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-c1-agent-evidence-baseline-isolated-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-c1-agent-evidence-baseline-isolated-002`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-f1-complete-isolated-construction-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-f1-isolated-construction-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-p1-contract-baseline-isolated-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/atu`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/卫星通讯`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/数字生物圈`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/科研证据链`
- `/Users/zhangbin/GitHub/4.10/research-os-private`
- `/Users/zhangbin/GitHub/4.16zonghe`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/.build/checkouts/swift-syntax`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/.build/checkouts/swift-testing`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/mac/release/DerivedData/SourcePackages/checkouts/swift-syntax`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/mac/release/DerivedData/SourcePackages/checkouts/swift-testing`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/release/DerivedData/SourcePackages/checkouts/swift-syntax`
- `/Users/zhangbin/GitHub/4.16zonghe/mac/release/DerivedData/SourcePackages/checkouts/swift-testing`
- `/Users/zhangbin/GitHub/AASP-Core`
- `/Users/zhangbin/GitHub/China-Precision-Mold-FDO-Standard`
- `/Users/zhangbin/GitHub/DOIP-Segments-Specification`
- `/Users/zhangbin/GitHub/ISAS-Core`
- `/Users/zhangbin/GitHub/Kinetic-Robotics-FDO-Sovereignty`
- `/Users/zhangbin/GitHub/MCP-Legal-China`
- `/Users/zhangbin/GitHub/OEO-Base-v0.1-command-mode`
- `/Users/zhangbin/GitHub/RedRock-Constitution`
- `/Users/zhangbin/GitHub/SAEE`
- `/Users/zhangbin/GitHub/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/ToolAgents-ei`
- `/Users/zhangbin/GitHub/_oss/cosign-digest-docfix/cosign`
- `/Users/zhangbin/GitHub/_outward-pass/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/_surface-pass/agent-evidence`
- `/Users/zhangbin/GitHub/_surface-pass/aro-audit`
- `/Users/zhangbin/GitHub/_surface-pass/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/_surface-pass/verifiable-agent-demo`
- `/Users/zhangbin/GitHub/ad-traffic-evidence-case`
- `/Users/zhangbin/GitHub/afdor-schema`
- `/Users/zhangbin/GitHub/agent-accountability-evidence-layer`
- `/Users/zhangbin/GitHub/agent-debugger`
- `/Users/zhangbin/GitHub/agent-evidence`
- `/Users/zhangbin/GitHub/agent-evidence-agt-double-merged-status`
- `/Users/zhangbin/GitHub/agent-evidence-agt-eeoap-adapter`
- `/Users/zhangbin/GitHub/agent-evidence-agt-upstream-copy-pack`
- `/Users/zhangbin/GitHub/agent-evidence-codex-link-udi-dicom-total-plan`
- `/Users/zhangbin/GitHub/agent-evidence-computer-standards-interfaces-journal`
- `/Users/zhangbin/GitHub/agent-evidence-csi-editor-riskfix`
- `/Users/zhangbin/GitHub/agent-evidence-csi-submission-materials`
- `/Users/zhangbin/GitHub/agent-evidence-desktop`
- `/Users/zhangbin/GitHub/agent-evidence-docs-link-check`
- `/Users/zhangbin/GitHub/agent-evidence-edc-java-spike`
- `/Users/zhangbin/GitHub/agent-evidence-job-search-resume-and-pins`
- `/Users/zhangbin/GitHub/agent-evidence-layer`
- `/Users/zhangbin/GitHub/agent-evidence-link-cleanup`
- `/Users/zhangbin/GitHub/agent-evidence-main-entry`
- `/Users/zhangbin/GitHub/agent-evidence-p10`
- `/Users/zhangbin/GitHub/agent-evidence-p11`
- `/Users/zhangbin/GitHub/agent-evidence-p11-review`
- `/Users/zhangbin/GitHub/agent-evidence-p12`
- `/Users/zhangbin/GitHub/agent-evidence-p12-review`
- `/Users/zhangbin/GitHub/agent-evidence-p14-audit`
- `/Users/zhangbin/GitHub/agent-evidence-p15`
- `/Users/zhangbin/GitHub/agent-evidence-p17-review`
- `/Users/zhangbin/GitHub/agent-evidence-p18`
- `/Users/zhangbin/GitHub/agent-evidence-p21`
- `/Users/zhangbin/GitHub/agent-evidence-p22`
- `/Users/zhangbin/GitHub/agent-evidence-p24`
- `/Users/zhangbin/GitHub/agent-evidence-p26-review`
- `/Users/zhangbin/GitHub/agent-evidence-p28-1`
- `/Users/zhangbin/GitHub/agent-evidence-p28-audit`
- `/Users/zhangbin/GitHub/agent-evidence-p30`
- `/Users/zhangbin/GitHub/agent-evidence-p33`
- `/Users/zhangbin/GitHub/agent-evidence-p39`
- `/Users/zhangbin/GitHub/agent-evidence-p40-review`
- `/Users/zhangbin/GitHub/agent-evidence-p41`
- `/Users/zhangbin/GitHub/agent-evidence-p42-review`
- `/Users/zhangbin/GitHub/agent-evidence-p43`
- `/Users/zhangbin/GitHub/agent-evidence-p44-review`
- `/Users/zhangbin/GitHub/agent-evidence-p45`
- `/Users/zhangbin/GitHub/agent-evidence-p46-review`
- `/Users/zhangbin/GitHub/agent-evidence-p47`
- `/Users/zhangbin/GitHub/agent-evidence-p47-review`
- `/Users/zhangbin/GitHub/agent-evidence-p48`
- `/Users/zhangbin/GitHub/agent-evidence-p49-review`
- `/Users/zhangbin/GitHub/agent-evidence-p50`
- `/Users/zhangbin/GitHub/agent-evidence-p51-review`
- `/Users/zhangbin/GitHub/agent-evidence-p52`
- `/Users/zhangbin/GitHub/agent-evidence-p54`
- `/Users/zhangbin/GitHub/agent-evidence-p55`
- `/Users/zhangbin/GitHub/agent-evidence-p55-review`
- `/Users/zhangbin/GitHub/agent-evidence-p56`
- `/Users/zhangbin/GitHub/agent-evidence-p57-review`
- `/Users/zhangbin/GitHub/agent-evidence-p58`
- `/Users/zhangbin/GitHub/agent-evidence-p58-review`
- `/Users/zhangbin/GitHub/agent-evidence-p59`
- `/Users/zhangbin/GitHub/agent-evidence-p60`
- `/Users/zhangbin/GitHub/agent-evidence-p60-review`
- `/Users/zhangbin/GitHub/agent-evidence-p61`
- `/Users/zhangbin/GitHub/agent-evidence-p62`
- `/Users/zhangbin/GitHub/agent-evidence-p62-review`
- `/Users/zhangbin/GitHub/agent-evidence-p63`
- `/Users/zhangbin/GitHub/agent-evidence-p63-review`
- `/Users/zhangbin/GitHub/agent-evidence-p7-review`
- `/Users/zhangbin/GitHub/agent-evidence-p8`
- `/Users/zhangbin/GitHub/agent-evidence-p9`
- `/Users/zhangbin/GitHub/agent-evidence-paper-bib-format`
- `/Users/zhangbin/GitHub/agent-evidence-paper-rc`
- `/Users/zhangbin/GitHub/agent-evidence-paper-source-verify`
- `/Users/zhangbin/GitHub/agent-evidence-paper-text-polish`
- `/Users/zhangbin/GitHub/agent-evidence-readme-only`
- `/Users/zhangbin/GitHub/agent-evidence-sync`
- `/Users/zhangbin/GitHub/agent-evidence-v0.5.0-pypi`
- `/Users/zhangbin/GitHub/agent-evidence-validator-error`
- `/Users/zhangbin/GitHub/agent-governance-benchmark`
- `/Users/zhangbin/GitHub/agent-governance-toolkit`
- `/Users/zhangbin/GitHub/agent-governance-toolkit-audit-entry-accountability-export`
- `/Users/zhangbin/GitHub/agent-intent-protocol`
- `/Users/zhangbin/GitHub/agent-object-protocol`
- `/Users/zhangbin/GitHub/agent-receipt-validator-mcp`
- `/Users/zhangbin/GitHub/agent-receipt-validator-space`
- `/Users/zhangbin/GitHub/agno-ei`
- `/Users/zhangbin/GitHub/aro-audit`
- `/Users/zhangbin/GitHub/aro-audit-langchain-receipt`
- `/Users/zhangbin/GitHub/cellcaps`
- `/Users/zhangbin/GitHub/cellcaps-rc6-review`
- `/Users/zhangbin/GitHub/course-video-factory`
- `/Users/zhangbin/GitHub/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/docs`
- `/Users/zhangbin/GitHub/docs-sparse`
- `/Users/zhangbin/GitHub/ecl-execution-compact-layer`
- `/Users/zhangbin/GitHub/edo-architecture-index`
- `/Users/zhangbin/GitHub/eeoap-dogfood-demo`
- `/Users/zhangbin/GitHub/embodied-sidecar`
- `/Users/zhangbin/GitHub/execution-integrity-core`
- `/Users/zhangbin/GitHub/fdo-kernel-mvk`
- `/Users/zhangbin/GitHub/freeact-ei`
- `/Users/zhangbin/GitHub/gies-afdo-paper`
- `/Users/zhangbin/GitHub/gitlink-agent-evidence-skill`
- `/Users/zhangbin/GitHub/god-spear`
- `/Users/zhangbin/GitHub/god-spear-mcp-gate`
- `/Users/zhangbin/GitHub/gptme`
- `/Users/zhangbin/GitHub/hongyan-trust-console`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Desktop`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/Origin`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/boshi`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/卫星通讯`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/孙小娟老师`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/AB-AEB`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/AFAC`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/Codex/2026-06-29/codex-vep-section-1-6-1/outputs/vep-minimal-runtime`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-c1-agent-evidence-baseline-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-c1-agent-evidence-baseline-isolated-002`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-contract-alignment-attempt-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-d1-external-governance-evidence-anchor-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-f1-complete-isolated-construction-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-f1-isolated-construction-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-p1-contract-baseline-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/VEP`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/atu`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/卫星通讯`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/数字生物圈`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/科研证据链`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/海南数字纪检`
- `/Users/zhangbin/GitHub/joy7758`
- `/Users/zhangbin/GitHub/joy7758-agt-double-merged-profile`
- `/Users/zhangbin/GitHub/joy7758-agt-upstream-homepage-line`
- `/Users/zhangbin/GitHub/joy7758-profile`
- `/Users/zhangbin/GitHub/langchain-aro`
- `/Users/zhangbin/GitHub/langchain-pop`
- `/Users/zhangbin/GitHub/lerobot`
- `/Users/zhangbin/GitHub/maniskill`
- `/Users/zhangbin/GitHub/mcp-agent-ei`
- `/Users/zhangbin/GitHub/minimal-profile-demo`
- `/Users/zhangbin/GitHub/odysseus`
- `/Users/zhangbin/GitHub/pFDO-Specification`
- `/Users/zhangbin/GitHub/paper-aep-specimen`
- `/Users/zhangbin/GitHub/paper-afdo-deterministic-governance`
- `/Users/zhangbin/GitHub/paper-ai-act-compliance-evidence`
- `/Users/zhangbin/GitHub/paper-ai-act-operation-accountability`
- `/Users/zhangbin/GitHub/paper-sovereign-pfdo`
- `/Users/zhangbin/GitHub/paper-template`
- `/Users/zhangbin/GitHub/paper-udi-dicom-profile`
- `/Users/zhangbin/GitHub/paper_20260407_sids_execution_evidence_fdo`
- `/Users/zhangbin/GitHub/papers-index`
- `/Users/zhangbin/GitHub/pd-oap-icsme2026-artifact`
- `/Users/zhangbin/GitHub/persona-object-protocol`
- `/Users/zhangbin/GitHub/pop-persona-cockpit`
- `/Users/zhangbin/GitHub/pop-persona-pack`
- `/Users/zhangbin/GitHub/pydantic-ai-ei`
- `/Users/zhangbin/GitHub/redcrag-aep`
- `/Users/zhangbin/GitHub/redrock-opendpp-core`
- `/Users/zhangbin/GitHub/research-pulse-cn`
- `/Users/zhangbin/GitHub/reverse-audq9j/tools/spidermonkey-dumper`
- `/Users/zhangbin/GitHub/risk-linked-aep-demo`
- `/Users/zhangbin/GitHub/rlcp-experiments`
- `/Users/zhangbin/GitHub/saee-datahub-capability-router`
- `/Users/zhangbin/GitHub/safety-valve-spec`
- `/Users/zhangbin/GitHub/sonogym`
- `/Users/zhangbin/GitHub/token-governor`
- `/Users/zhangbin/GitHub/token-governor-langchain-middleware`
- `/Users/zhangbin/GitHub/tse-submission-private`
- `/Users/zhangbin/GitHub/verifiable-agent-demo`
- `/Users/zhangbin/GitHub/verifiable-agent-demo-ai-entry`
- `/Users/zhangbin/GitHub/verifiable-tool-invocation-flow`
- `/Users/zhangbin/GitHub/verify-agent-receipt-action`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/AFAC`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/Codex/2026-06-29/codex-vep-section-1-6-1/outputs/vep-minimal-runtime`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/SAEE-d1-external-governance-evidence-anchor-isolated-001`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/VEP`
- `/Users/zhangbin/SAEE-c1-baseline-commit-isolated-001`
- `/Users/zhangbin/SAEE-c1-baseline-recovery-001`
- `/Users/zhangbin/SAEE-d1-baseline-recovery-001`
- `/Users/zhangbin/SAEE-openai-build-week-2026`
- `/Users/zhangbin/agent`
- `/Users/zhangbin/ags-theory`
- `/Users/zhangbin/cosmos-metabolic-hijack`
- `/Users/zhangbin/cosmos-metabolic-hijack/lib/forge-std`
- `/Users/zhangbin/joy7758`
- `/Users/zhangbin/joy7758-repo-cleanup/work/digital-biosphere-architecture`
- `/Users/zhangbin/joy7758-repo-cleanup/work/joy7758`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/DOIP-Segments-Specification`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/RedRock-Constitution`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/ToolAgents`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/agent-object-protocol`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/agno`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/aro-audit`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/aro-audit-langchain-receipt`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/docs`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/execution-integrity-core`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/freeact`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/god-spear-mcp-gate`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/gptme`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/langchain-aro`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/langchain-pop`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/mcp-agent`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/pop-persona-pack`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/pydantic-ai`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/token-governor`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/token-governor-langchain-middleware`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/verifiable-agent-demo`
- `/Users/zhangbin/opensea-poc`
- `/Users/zhangbin/opensea-poc/lib/forge-std`
- `/Users/zhangbin/pra-server`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T074548Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T075402Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T080000Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/academic-research-skills-codex`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/research-paper-writing-skills`
- `/Users/zhangbin/projects/hongyan-workbench`
- `/Users/zhangbin/projects/hongyan-workbench/vendor/paper-trace-assistant`
- `/Users/zhangbin/projects/hongyan-workbench/vendor/paper-trace-assistant/vendor/agent-evidence`
- `/Users/zhangbin/projects/paper-trace-assistant`
- `/Users/zhangbin/projects/paper-trace-assistant/vendor/agent-evidence`
- `/Users/zhangbin/projects/udi-dicom-evidence/udi-dicom-conformance-suite-private`
- `/Users/zhangbin/projects/udi-dicom-evidence/udi-dicom-evidence-validator`
- `/Users/zhangbin/projects/udi-dicom-evidence/udi-dicom-sample-validation-service-private`
- `/Users/zhangbin/research/aep-swhid-code-reference-extension-v0_1_standalone`
- `/Users/zhangbin/research/robot-benchmark-execution-evidence`

## Keyword or content-verified related paths

- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/AB-AEB`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-c1-agent-evidence-baseline-isolated-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-c1-agent-evidence-baseline-isolated-002`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-f1-complete-isolated-construction-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-f1-isolated-construction-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE-p1-contract-baseline-isolated-001`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/atu`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/卫星通讯`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/数字生物圈`
- `/Users/zhangbin/GitHub/.runtime-node-01-migration-staging/科研证据链`
- `/Users/zhangbin/GitHub/MCP-Legal-China`
- `/Users/zhangbin/GitHub/SAEE`
- `/Users/zhangbin/GitHub/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/ToolAgents-ei`
- `/Users/zhangbin/GitHub/_outward-pass/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/_surface-pass/agent-evidence`
- `/Users/zhangbin/GitHub/_surface-pass/aro-audit`
- `/Users/zhangbin/GitHub/_surface-pass/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/_surface-pass/verifiable-agent-demo`
- `/Users/zhangbin/GitHub/agent-accountability-evidence-layer`
- `/Users/zhangbin/GitHub/agent-debugger`
- `/Users/zhangbin/GitHub/agent-evidence`
- `/Users/zhangbin/GitHub/agent-evidence-agt-double-merged-status`
- `/Users/zhangbin/GitHub/agent-evidence-agt-eeoap-adapter`
- `/Users/zhangbin/GitHub/agent-evidence-agt-upstream-copy-pack`
- `/Users/zhangbin/GitHub/agent-evidence-codex-link-udi-dicom-total-plan`
- `/Users/zhangbin/GitHub/agent-evidence-computer-standards-interfaces-journal`
- `/Users/zhangbin/GitHub/agent-evidence-csi-editor-riskfix`
- `/Users/zhangbin/GitHub/agent-evidence-csi-submission-materials`
- `/Users/zhangbin/GitHub/agent-evidence-desktop`
- `/Users/zhangbin/GitHub/agent-evidence-docs-link-check`
- `/Users/zhangbin/GitHub/agent-evidence-edc-java-spike`
- `/Users/zhangbin/GitHub/agent-evidence-job-search-resume-and-pins`
- `/Users/zhangbin/GitHub/agent-evidence-layer`
- `/Users/zhangbin/GitHub/agent-evidence-link-cleanup`
- `/Users/zhangbin/GitHub/agent-evidence-main-entry`
- `/Users/zhangbin/GitHub/agent-evidence-p10`
- `/Users/zhangbin/GitHub/agent-evidence-p11`
- `/Users/zhangbin/GitHub/agent-evidence-p11-review`
- `/Users/zhangbin/GitHub/agent-evidence-p12`
- `/Users/zhangbin/GitHub/agent-evidence-p12-review`
- `/Users/zhangbin/GitHub/agent-evidence-p14-audit`
- `/Users/zhangbin/GitHub/agent-evidence-p15`
- `/Users/zhangbin/GitHub/agent-evidence-p17-review`
- `/Users/zhangbin/GitHub/agent-evidence-p18`
- `/Users/zhangbin/GitHub/agent-evidence-p21`
- `/Users/zhangbin/GitHub/agent-evidence-p22`
- `/Users/zhangbin/GitHub/agent-evidence-p24`
- `/Users/zhangbin/GitHub/agent-evidence-p26-review`
- `/Users/zhangbin/GitHub/agent-evidence-p28-1`
- `/Users/zhangbin/GitHub/agent-evidence-p28-audit`
- `/Users/zhangbin/GitHub/agent-evidence-p30`
- `/Users/zhangbin/GitHub/agent-evidence-p33`
- `/Users/zhangbin/GitHub/agent-evidence-p39`
- `/Users/zhangbin/GitHub/agent-evidence-p40-review`
- `/Users/zhangbin/GitHub/agent-evidence-p41`
- `/Users/zhangbin/GitHub/agent-evidence-p42-review`
- `/Users/zhangbin/GitHub/agent-evidence-p43`
- `/Users/zhangbin/GitHub/agent-evidence-p44-review`
- `/Users/zhangbin/GitHub/agent-evidence-p45`
- `/Users/zhangbin/GitHub/agent-evidence-p46-review`
- `/Users/zhangbin/GitHub/agent-evidence-p47`
- `/Users/zhangbin/GitHub/agent-evidence-p47-review`
- `/Users/zhangbin/GitHub/agent-evidence-p48`
- `/Users/zhangbin/GitHub/agent-evidence-p49-review`
- `/Users/zhangbin/GitHub/agent-evidence-p50`
- `/Users/zhangbin/GitHub/agent-evidence-p51-review`
- `/Users/zhangbin/GitHub/agent-evidence-p52`
- `/Users/zhangbin/GitHub/agent-evidence-p54`
- `/Users/zhangbin/GitHub/agent-evidence-p55`
- `/Users/zhangbin/GitHub/agent-evidence-p55-review`
- `/Users/zhangbin/GitHub/agent-evidence-p56`
- `/Users/zhangbin/GitHub/agent-evidence-p57-review`
- `/Users/zhangbin/GitHub/agent-evidence-p58`
- `/Users/zhangbin/GitHub/agent-evidence-p58-review`
- `/Users/zhangbin/GitHub/agent-evidence-p59`
- `/Users/zhangbin/GitHub/agent-evidence-p60`
- `/Users/zhangbin/GitHub/agent-evidence-p60-review`
- `/Users/zhangbin/GitHub/agent-evidence-p61`
- `/Users/zhangbin/GitHub/agent-evidence-p62`
- `/Users/zhangbin/GitHub/agent-evidence-p62-review`
- `/Users/zhangbin/GitHub/agent-evidence-p63`
- `/Users/zhangbin/GitHub/agent-evidence-p63-review`
- `/Users/zhangbin/GitHub/agent-evidence-p7-review`
- `/Users/zhangbin/GitHub/agent-evidence-p8`
- `/Users/zhangbin/GitHub/agent-evidence-p9`
- `/Users/zhangbin/GitHub/agent-evidence-paper-bib-format`
- `/Users/zhangbin/GitHub/agent-evidence-paper-rc`
- `/Users/zhangbin/GitHub/agent-evidence-paper-source-verify`
- `/Users/zhangbin/GitHub/agent-evidence-paper-text-polish`
- `/Users/zhangbin/GitHub/agent-evidence-readme-only`
- `/Users/zhangbin/GitHub/agent-evidence-sync`
- `/Users/zhangbin/GitHub/agent-evidence-v0.5.0-pypi`
- `/Users/zhangbin/GitHub/agent-evidence-validator-error`
- `/Users/zhangbin/GitHub/agent-governance-benchmark`
- `/Users/zhangbin/GitHub/agent-governance-toolkit`
- `/Users/zhangbin/GitHub/agent-governance-toolkit-audit-entry-accountability-export`
- `/Users/zhangbin/GitHub/agent-intent-protocol`
- `/Users/zhangbin/GitHub/agent-object-protocol`
- `/Users/zhangbin/GitHub/agent-receipt-validator-mcp`
- `/Users/zhangbin/GitHub/agent-receipt-validator-space`
- `/Users/zhangbin/GitHub/aro-audit`
- `/Users/zhangbin/GitHub/aro-audit-langchain-receipt`
- `/Users/zhangbin/GitHub/cellcaps`
- `/Users/zhangbin/GitHub/digital-biosphere-architecture`
- `/Users/zhangbin/GitHub/ecl-execution-compact-layer`
- `/Users/zhangbin/GitHub/execution-integrity-core`
- `/Users/zhangbin/GitHub/fdo-kernel-mvk`
- `/Users/zhangbin/GitHub/gitlink-agent-evidence-skill`
- `/Users/zhangbin/GitHub/god-spear-mcp-gate`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/AB-AEB`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/AFAC`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/Codex/2026-06-29/codex-vep-section-1-6-1/outputs/vep-minimal-runtime`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-c1-agent-evidence-baseline-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-c1-agent-evidence-baseline-isolated-002`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-contract-alignment-attempt-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-d1-external-governance-evidence-anchor-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-f1-complete-isolated-construction-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-f1-isolated-construction-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE-p1-contract-baseline-isolated-001`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE/build/external-publication/saee-github-public`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/SAEE/sites/saee-commercial`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/VEP`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/atu`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/卫星通讯`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/数字生物圈`
- `/Users/zhangbin/GitHub/iCloud-Drive-local/Documents/文稿 - runtime-node-01/科研证据链`
- `/Users/zhangbin/GitHub/mcp-agent-ei`
- `/Users/zhangbin/GitHub/paper-afdo-deterministic-governance`
- `/Users/zhangbin/GitHub/persona-object-protocol`
- `/Users/zhangbin/GitHub/pop-persona-cockpit`
- `/Users/zhangbin/GitHub/pop-persona-pack`
- `/Users/zhangbin/GitHub/saee-datahub-capability-router`
- `/Users/zhangbin/GitHub/token-governor`
- `/Users/zhangbin/GitHub/verifiable-agent-demo`
- `/Users/zhangbin/GitHub/verifiable-agent-demo-ai-entry`
- `/Users/zhangbin/GitHub/verify-agent-receipt-action`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/AFAC`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/Codex/2026-06-29/codex-vep-section-1-6-1/outputs/vep-minimal-runtime`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/SAEE-d1-external-governance-evidence-anchor-isolated-001`
- `/Users/zhangbin/GitHub/文稿 - runtime-node-01/VEP`
- `/Users/zhangbin/SAEE-c1-baseline-commit-isolated-001`
- `/Users/zhangbin/SAEE-c1-baseline-recovery-001`
- `/Users/zhangbin/SAEE-d1-baseline-recovery-001`
- `/Users/zhangbin/SAEE-openai-build-week-2026`
- `/Users/zhangbin/agent`
- `/Users/zhangbin/joy7758-repo-cleanup/work/digital-biosphere-architecture`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/ToolAgents`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/agent-object-protocol`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/aro-audit`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/aro-audit-langchain-receipt`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/god-spear-mcp-gate`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/mcp-agent`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/pop-persona-pack`
- `/Users/zhangbin/joy7758-repo-cleanup/work/repos/verifiable-agent-demo`
- `/Users/zhangbin/pra-server`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T074548Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T075402Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/_failed-clones/paper-qa.partial-20260526T080000Z`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/academic-research-skills-codex`
- `/Users/zhangbin/pra-server/projects/fdo-agent-evidence/12-skill-integration/vendor-sandbox/research-paper-writing-skills`
- `/Users/zhangbin/projects/hongyan-workbench/vendor/paper-trace-assistant/vendor/agent-evidence`
- `/Users/zhangbin/projects/paper-trace-assistant/vendor/agent-evidence`
