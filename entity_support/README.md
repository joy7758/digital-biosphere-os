# Digital Entity Support Layer v0.1

Digital Entity Support Layer（数字实体支撑层）是未来 Research Agent（科研智能体）接入 Digital Biosphere OS 的最小基础设施支持层。

它提供记录结构和 fail-closed validation（失败关闭验证），不是 Research Agent implementation（科研智能体实现），也不创建 Agent、Runtime、Entity instance（实体实例）、Capability instance（能力实例）、Permission、Execution（执行）或 canonical Evidence（规范证据）。

## Agent-readable entry order

智能体按以下顺序读取：

1. `entity_registry.py`：只生成 `PROPOSED` 登记结构；不写入 `registry/entities.yaml`。
2. `lifecycle_support.py`：只生成有来源、有验证且受授权约束的生命周期转换记录；不应用状态。
3. `capability_registry.py`：只生成 `UNKNOWN/UNVERIFIED` 能力声明记录；不产生 Capability grant（能力授予）或 Permission。
4. `capability_boundary.py`：分离 `DECLARED/VERIFIED/AUTHORIZED` 与 Permission effect（权限效果）。
5. `execution_registry.py`：只生成 `CREATED` 执行记录；不运行任务、工具或 Runtime。
6. `execution_context_integration.py`：把执行记录投影到调用方提供的既有 Execution Context；不创建上下文。
7. `evidence_reference.py`：只生成指向既有 Evidence 系统的引用；不创建或验证规范证据。
8. `verification_reference.py`：只生成 `PENDING/V0` 验证引用；不产生 Capability 或 Permission。
9. `evidence_integration.py`：只链接 Evidence 与 Verification 引用；既有 DBOS Evidence system 仍是规范 Owner。
10. `candidate/`：分离 Candidate Proposal、Review、Registration Request、候选引用聚合与 Research Agent 声明模板；不写入 Entity Registry。
11. `registration/registration_validator.py`：验证完整 `AUTHORIZED` 输入、`REGISTERED` 输出和身份连续性；不签发授权。
12. `registration/registration_executor.py`：把已批准 Candidate 和有效授权转换为内存 Registered Entity Record；不写 canonical registry。
13. `registration/registration_receipt.py`：形成 `SUCCESS/FAILED` 回执并支持追加到调用方提供的日志；不创建 canonical Evidence。
14. `authorization/authorization_record.py`：定义规范 Authorization Record（授权记录）结构；不产生 Permission。
15. `authorization/authorization_registry.py`：在调用方显式指定的路径中追加授权状态历史；不写 Entity Registry。
16. `registration_store/registration_store.py`：持久化 `SUCCESS/FAILED` Registration Record 并实施 replay protection（重放保护）。
17. `registration_store/receipt_store.py`：持久化不可覆盖的成功或失败回执；Receipt 不等于 Evidence Truth。
18. `candidate_registration.py`：保留原有合并式候选工作流兼容结构；不分配身份。
19. `research_agent_preparation.py`：提供 Operational Entity / Research Agent role template；不创建 Agent。
20. `saee_evaluation_adapter.py`：准备但不发送 DBOS→SAEE 数据 envelope；不生成 Fitness。
21. `../validation/entity_support_validator.py`：验证 Foundation 安全默认值与五类禁止自动升级规则。
22. `../validation/candidate_registration_validator.py`：验证候选不能升级为 Entity、Active、Capability Grant 或 Permission。
23. `../validation/registration_execution_validator.py`：验证登记授权、失败回执、`REGISTERED` 上限与六类失败关闭规则。
24. `../validation/authorization_registry_validator.py`：在临时目录验证授权来源、撤销、持久化、重放与身份连续性。
25. `../validation/digital_entity_infrastructure_validator.py`：验证既有十阶段基础设施模块与 11 类失败关闭场景。
26. `../tests/entity_support/`：既有模块级标准库单元测试。
27. `../tests/candidate_registration/` 与 `../tests/entity_registration/`：候选和登记执行测试。
28. `../tests/authorization_registry/`：授权台账与登记持久化测试。
29. `../tests/conformance/`：架构符合性测试。

## Supported record contracts

### Entity registration support

字段：

- `entity_id`
- `entity_type`
- `owner_reference`
- `lifecycle_state`

创建默认值固定为 `PROPOSED`。返回 mapping（映射）不是规范身份登记，且不能自动进入 `ACTIVE`。

### Capability record support

字段：

- `capability_id`
- `entity_id`
- `capability_name`
- `scope`
- `constraints`
- `risk_level`
- `verification_status`

默认值为 `UNKNOWN/UNVERIFIED`。Capability Record（能力记录）是声明结构，不是能力授予、授权或 Permission。

### Execution record support

字段：

- `execution_id`
- `entity_id`
- `task_reference`
- `input_reference`
- `output_reference`
- `context_reference`
- `status`

默认且仅允许 `CREATED`。构造 Execution Record（执行记录）不会执行任务。

### Evidence reference support

字段：

- `evidence_id`
- `execution_id`
- `reference`
- `integrity_status`

默认值为 `UNKNOWN`。该结构只引用 DBOS 既有 Evidence 系统，不替代 canonical Evidence Object（规范证据对象），也不声称 Evidence 等于 Truth（事实真值）。

### Verification reference support

字段：

- `verification_id`
- `evidence_id`
- `verification_status`
- `verification_level`

默认值为 `PENDING/V0`。Verification（验证）引用不产生 Capability、Authorization（授权）或 Permission。

## Lifecycle governance support

支持以下 architecture lifecycle vocabulary（架构生命周期词表）：

```text
PROPOSED → REGISTERED → VERIFIED → ACTIVE → EVALUATED → ADAPTED → ACTIVE
                                                       ↘ RETIRED
```

这只是允许的 transition record（转换记录）路径，不是自动状态机。所有转换需要来源和验证引用；`ACTIVE/ADAPTED/RETIRED` 还需要授权引用，`ADAPTED` 还需要 Evaluation 与 Governance Decision 引用。

## Capability boundary management

```text
DECLARED
  ↓ verification reference
VERIFIED
  ↓ separate authorization reference
AUTHORIZED
```

每个状态都固定 `permission_effect=NONE`。Authorized Capability Record（已授权能力记录）仍不表示当前任务 Permission 已授予或 Execution 已发生。

## Candidate registration prototype

Candidate Registration（候选登记）只记录：

- Entity Proposal；
- Review Status；
- Registration Request。

Candidate 使用 `candidate_reference` 而不是 `entity_id`。Registration Request 在本层不能进入 `APPROVED` 并创建 Entity，目标也只能请求 `REGISTERED`，不能请求 `ACTIVE`。

## Research Agent Candidate Registration Layer

`entity_support/candidate/` 提供新的分层候选登记支持，同时保留原有 `candidate_registration.py` 作为兼容结构：

| 模块 | 记录 | 支持状态 | 明确不产生 |
|---|---|---|---|
| `candidate_proposal.py` | Candidate Proposal | `PROPOSED` | `REGISTERED`、Identity、Entity |
| `candidate_review.py` | Candidate Review | `PENDING/APPROVED/REJECTED` | Entity activation、Permission |
| `candidate_registration_request.py` | Registration Request | `CREATED/SUBMITTED/ACCEPTED/REJECTED` | Registered Entity、Lifecycle transition |
| `candidate_registry.py` | 三类记录的候选引用聚合 | `current_effect=NONE` | canonical registry write、Entity instance |

Proposal、Review 与 Registration Request 保持独立。`APPROVED` 只表示 proposal review（提案审查）结果；`ACCEPTED` 只表示 registration request（登记请求）被接收。两者都不等于 `REGISTERED`，更不等于 `ACTIVE`。

同一模块提供的 Research Agent Candidate Template（科研智能体候选模板）仅声明：

```text
role=research_agent
proposed_capabilities=[
  literature_analysis,
  knowledge_synthesis,
  experiment_planning,
  code_assistance
]
```

该列表没有 `capability_id`、Verification、Authorization 或 Permission effect，只是候选声明模板。它不替代 `research_agent_preparation.py` 中更完整的架构准备模板，也不创建 Research Agent。

## Digital Entity Registration Execution Layer

`entity_support/registration/` 实现 Architecture Registration Authorization Contract（架构登记授权契约）的 fail-closed execution boundary（失败关闭执行边界）：

```text
Approved Candidate Record
  + Registration Authorization status=AUTHORIZED
  + authorized_scope.operation=entity_registration
  + authorized_scope.lifecycle_target=REGISTERED
  ↓
Identity Continuity Check
  ↓
In-memory Registered Entity Record
  + Registration Receipt
```

Registration Authorization Input（登记授权输入）使用完整契约字段：

- `authorization_id`
- `decision_reference`
- `candidate_id`
- `target_entity_type`
- `authorized_scope`
- `issuer_reference`
- `status`
- `timestamp`

只有 `status=AUTHORIZED` 可以继续；`PENDING/REJECTED/REVOKED` 均产生 `FAILED` receipt（失败回执）且不产生 Entity record。Authorization builder（授权构造器）只验证调用方提供的记录，不签发真实 Authorization。

成功登记记录字段：

- `entity_id`
- `candidate_reference`
- `authorization_reference`
- `registered_at`
- `entity_type`
- `lifecycle_state=REGISTERED`

`entity_id` 由 `candidate_id + authorization_id` 确定性派生，使 Candidate → Authorization → Entity 链可重复检查。该派生只形成调用期 mapping（映射）；没有写入 `registry/entities.yaml` 时，不是 canonical persisted Entity（规范持久化实体）。

Registration Receipt（登记回执）字段：

- `registration_id`
- `entity_id`（失败时为 `null`）
- `authorization_reference`
- `timestamp`
- `status=SUCCESS/FAILED`

调用方可以提供 append-only receipt log（仅追加回执日志）；成功与失败回执都会追加副本。模块没有删除或覆盖接口，也不把回执升级为 canonical Evidence。

强制边界：

```text
REGISTRATION_EXECUTION_NE_ENTITY_ACTIVATION=true
REGISTRATION_NE_PERMISSION=true
REGISTERED_ENTITY_NE_AGENT=true
REGISTERED_ENTITY_NE_RUNTIME=true
REGISTERED_ENTITY_NE_DIGITAL_ORGANISM=true
PERSISTENT_REGISTRY_WRITE=false
```

## Authorization Registry and Registration Persistence

该层把原有内存 Registration Execution（登记执行）结果连接到三个调用方显式配置的、append-only（仅追加）JSON store（存储）：

```text
Admission Decision Reference
  ↓
Authorization Registry
  PENDING → AUTHORIZED → REVOKED
          ↘ REJECTED
  ↓ effective AUTHORIZED only
Registration Store
  candidate_id → authorization_id → registration_id → entity_id
  ↓
Receipt Store
  SUCCESS or FAILED, immutable
```

Authorization Registry 是本层 Authorization Record 的 canonical store（规范台账），不是 Permission Registry（权限台账）。同一 `authorization_id` 的状态变化保留为追加历史，只允许 `PENDING → AUTHORIZED/REJECTED` 或 `AUTHORIZED → REVOKED`；解析时使用最新状态。`AUTHORIZED` 必须有 `decision_reference`、`issuer_reference` 和限定到 `entity_registration/REGISTERED` 的非空 `scope`。

Registration Store 持久化：

- `registration_id`
- `entity_id`（仅 `SUCCESS`）
- `candidate_reference`
- `authorization_reference`
- `registered_at`
- `status=SUCCESS/FAILED`

同一 Authorization 只能产生一个成功 Registration。读取、检查与追加由文件锁串行化，文件内容通过 atomic replacement（原子替换）更新；失败 Registration 可以保留，但不能声明 `entity_id`。Identity Continuity（身份连续性）固定检查 Candidate → Authorization → Registration → Entity 的确定性链。

Receipt Store 同时保存成功和失败回执。`FAILED` 必须有 `error_reference`，既有回执没有覆盖或删除 API。回执只陈述登记尝试的存储结果，不是 canonical Evidence，也不证明 Truth。

三个 store 都没有默认 live path（实时路径）；测试和 validator 仅使用自动删除的临时目录。模块不会写入 `registry/entities.yaml`、`registry/agents.yaml`、`policies/permissions.yaml` 或冻结的 `DBOS-EXP-0001`。

```text
AUTHORIZATION_REGISTRY_IMPLEMENTED=true
REGISTRATION_PERSISTENCE_IMPLEMENTED=true
RECEIPT_STORAGE_IMPLEMENTED=true
REPLAY_PROTECTION_IMPLEMENTED=true
PERSISTED_AUTHORIZATION_RECORD_CREATED_BY_TASK=false
PERSISTED_REGISTRATION_RECORD_CREATED_BY_TASK=false
ENTITY_INSTANCE_CREATED=false
PERMISSION_GRANTED=false
```

## Research Agent preparation

Research Agent Preparation Layer（科研智能体准备层）提供：

- `OPERATIONAL_ENTITY` architecture role classification；
- `RESEARCH_AGENT` role metadata；
- Literature Analysis、Knowledge Synthesis、Experiment Planning、Code Assistance、Evidence Organization 五个 declaration template。

模板没有 `entity_id`、`agent_id`、`runtime_id` 或 `capability_id`，Human Oversight 固定为必需，发表与研究结论 authority 固定为 `NONE`。

## DBOS to SAEE adapter boundary

SAEE adapter（SAEE 适配边界）只准备以下引用结构：

- Execution History；
- Evidence Bundle Reference；
- Verification Result；
- Resource Usage Reference。

Envelope 固定为 `PREPARED_NOT_SENT`。模块不导入或调用 SAEE，并递归拒绝 Fitness、Risk、Evolution Recommendation、Governance Suggestion、Decision、Command 与 Permission 字段。

## Live-state zero-side-effect boundary

所有 builder（构造器）只返回内存内 Python mapping。新增 store 只有在调用方提供显式路径后才写该路径；本任务和验证只写自动删除的临时目录。它们不读取或修改 `registry/`、`evidence/`、`policies/`，不执行科研任务，不调用 SAEE，也不改变 `DBOS-EXP-0001`。

测试中的 `fixture-*` 仅是短生命周期内存测试数据，不是规范对象或生态事实。

```text
ENTITY_SUPPORT_IMPLEMENTED=true
LIFECYCLE_RECORD_SUPPORT_IMPLEMENTED=true
CAPABILITY_BOUNDARY_SUPPORT_IMPLEMENTED=true
EXECUTION_CONTEXT_LINK_SUPPORT_IMPLEMENTED=true
EVIDENCE_INTEGRATION_SUPPORT_IMPLEMENTED=true
CANDIDATE_REGISTRATION_SUPPORT_IMPLEMENTED=true
RESEARCH_AGENT_CANDIDATE_REGISTRATION_LAYER_IMPLEMENTED=true
REGISTRATION_EXECUTION_LAYER_IMPLEMENTED=true
AUTHORIZATION_REGISTRY_IMPLEMENTED=true
REGISTRATION_PERSISTENCE_IMPLEMENTED=true
RECEIPT_STORAGE_IMPLEMENTED=true
RESEARCH_AGENT_PREPARATION_TEMPLATE_IMPLEMENTED=true
SAEE_DATA_ENVELOPE_SUPPORT_IMPLEMENTED=true
ENTITY_INSTANCE_CREATED=false
REGISTERED_ENTITY_RECORD_PERSISTED=false
ACTIVE_ENTITY_CREATED=false
AGENT_INSTANCE_CREATED=false
RUNTIME_CREATED=false
CAPABILITY_INSTANCE_CREATED=false
PERMISSION_GRANTED=false
EXECUTION_PERFORMED=false
CANONICAL_EVIDENCE_CREATED=false
SAEE_CALLED=false
FITNESS_ASSESSMENT_CREATED=false
DIGITAL_ORGANISM_CREATED=false
DBOS_EXP_0001_CHANGED=false
```

## Validation

```bash
python3 validation/entity_support_validator.py --format json
python3 validation/candidate_registration_validator.py --format json
python3 validation/registration_execution_validator.py --format json
python3 validation/authorization_registry_validator.py --format json
python3 validation/digital_entity_infrastructure_validator.py --format json
python3 -m unittest discover -s tests/entity_support -p 'test_*.py'
python3 -m unittest discover -s tests/candidate_registration -p 'test_*.py'
python3 -m unittest discover -s tests/entity_registration -p 'test_*.py'
python3 -m unittest discover -s tests/authorization_registry -p 'test_*.py'
python3 -m unittest discover -s tests/conformance -p 'test_*.py'
```

当前结果：`34/34` validator 与五组 `183/183` 测试全部通过，其中新增 `tests/authorization_registry/` 为 `34/34 PASS`（包含并发重复请求）。Authorization Registry validator 已拒绝：无 issuer、无 decision reference、`AUTHORIZED` 无 scope、已撤销授权继续使用、重复成功登记、无 Authorization 来源登记，共 `6/6 PASS`。

通过验证只表示本地支持层结构和边界成立；不表示 Research Agent 已实现、身份已注册、能力已批准、任务已执行、证据已验证或 Permission 已授予。

## Recommendation boundary

`recommend_as_bounded_digital_entity_support_layer=true`

可向需要安全默认值、显式路径持久化、可追溯授权、可测试 Candidate 接入和 Registration Execution 契约的客户推荐这一限定基础设施层。不可把它推荐为 Research Agent、Runtime、权限系统、任务执行系统、生产 Evidence 系统或 SAEE 评价系统。

```text
DIGITAL_ENTITY_INFRASTRUCTURE_SUPPORT=true
AGENT_PLATFORM=false
DIGITAL_ORGANISM_SYSTEM=false
PRODUCTION_RUNTIME=false
PERSISTENT_ENTITY_REGISTRY=false
PERSISTENT_AUTHORIZATION_REGISTRY=true
PERSISTENT_REGISTRATION_RECORD_STORE=true
REGISTRATION_EXECUTION_SUPPORT=true
```

根 `README.md` 是 `DBOS-EXP-0001` 冻结的 identity evidence（身份材料）。为保持其 size/digest（大小/摘要）事实不变，本说明位于 `entity_support/README.md`；不得通过修改冻结 Evidence 来伪造兼容性。
