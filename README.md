# Digital Biosphere OS v0.1

Digital Biosphere OS 是用于管理 AI agent（人工智能智能体）、代码系统和协议生命周期的治理基础设施。

战略上，DBOS 定位为 Open Digital Entity Infrastructure（开放数字实体基础设施）：`DBOS governs existence`（DBOS 治理存在）。DBOS 是 infrastructure（基础设施），不是 Agent application（智能体应用）、Foundation Model（基础模型）、Chatbot Platform（聊天机器人平台）或 SAEE 替代品。

当前版本增加 Digital Biosphere Federation Layer v0.1（数字生物圈联邦层 v0.1），用中央 proposed member（拟议成员）、pending manifest（待定清单）、证据关系图和共享宪法引用连接独立项目。Federation 不合并仓库、不移动代码、不接管身份；当前不创建 Agent、Runtime、候选体或 Digital Organism。初始扫描的 22/78 条事实基线作为历史保留，另按明确授权新增 1 条 ACP 协议身份；能力声明仍为 78 条。

## Strategic Alignment（战略对齐）

最高战略定位、DBA（数字生物圈架构）关系、SAEE（硅基放大演化生态）边界、开发者生态方向、商业边界与非目标范围，见 [`STRATEGIC_ALIGNMENT.md`](STRATEGIC_ALIGNMENT.md)。该文件只同步战略，`implementation_effect=NONE`（无实现效果），不改变本 README 中的技术事实、能力、权限、实验或开发状态。

智能体在解释或规划 DBOS 任务前，应先读取该战略对齐说明，并保持：`DBOS is infrastructure, not application`（DBOS 是基础设施，不是应用）。

## Agent-readable entry order

智能体按以下顺序读取：

- 战略前置：`STRATEGIC_ALIGNMENT.md`，用于定位、职责分层、SAEE 边界、开发者生态和非目标判断；它不产生技术授权。

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
