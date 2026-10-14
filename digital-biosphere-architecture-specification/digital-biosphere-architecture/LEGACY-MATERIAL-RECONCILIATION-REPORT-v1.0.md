---
document_id: DBA-LEGACY-MATERIAL-RECONCILIATION-REPORT-1.0
title: DBA Legacy Material Reconciliation Report v1.0
title_zh: DBA 旧目录材料解析与合并报告 v1.0
status: completed-selective-reconciliation
observed_at: 2026-07-31
canonical_base_revision: e848ade1f937c7a36cc90308c7af63f20c131d7e
source_files_observed: 76
canonical_control_documents_replaced_wholesale: false
legacy_checkout_modified: false
authority_effect: none
---

# DBA Legacy Material Reconciliation Report v1.0

中文：DBA 旧目录材料解析与合并报告 v1.0。

## Scope

本轮将旧工作目录视为 candidate source（候选来源），将干净检出的当前 `main` 视为唯一
canonical merge target（规范合并目标）。解析范围包括：

- 旧目录中 75 个 tracked-modified 或 untracked 路径；
- 当前 `main` 已引用、但只存在于旧分支的 `ADR-032`；
- 当前 `main` 的强制驾驶舱、TITMAS、商业状态和权力边界；
- 旧目录与当前 `main` 的 tracked inventory divergence（跟踪清单分歧）。

旧分支另有 442 个 tracked-only 历史路径，当前 `main` 有 451 个 clean-only 当前路径。
这说明二者不是可以直接 `git add .` 或整树覆盖的同一代目录。本轮不合并两条历史树，
只处理旧目录的未提交候选内容和一个被当前规范引用的缺失决策。

## Reconciliation result

| disposition | count | treatment |
|---|---:|---|
| `PROMOTED_CURRENT` | 2 | `ADR-032` 与 `ADR-033` 作为有界、无执行效果的当前架构决策纳入 |
| `EXTRACTED_CURRENT_CONTENT_ONLY` | 2 | 从旧 Charter / Constitution 只提取组合式规模与注意力原则，不覆盖当前状态 |
| `NOT_IMPORTED_STALE_CONTROL_PROJECTION` | 4 | 旧 `AGENTS`、`PROGRAM-STATUS`、`README`、风险台账不覆盖当前规范投影 |
| `SUPERSEDED_NOT_IMPORTED` | 6 | 旧情报与能力来源材料由 `intelligence/2026-07-29/` 的一手来源纠正版取代 |
| `NOT_IMPORTED` | 2 | TITMAS v0.2 未跟踪章程候选与 Digital Immune 候选不创建第二套宪法 |
| `RETAINED_IN_LEGACY_NOT_IMPORTED` | 60 | DEB、Digital Survival、Self-Governance 和其他候选／审查材料继续留在旧目录 |

逐文件路径、SHA-256、大小、分类、去向和理由见
[`LEGACY-MATERIAL-RECONCILIATION-MANIFEST-v1.0.json`](LEGACY-MATERIAL-RECONCILIATION-MANIFEST-v1.0.json)。

## Material promoted into the canonical baseline

### Compositional Scale

[`ADR-032`](architecture/ADR-032-compositional-scale-over-unbounded-center.md)
固定以下长期原则：

> 不追求制造一个无限强的中心，而通过大量简单、受限、可替换主体的结构组合形成覆盖能力。

该原则已同步到 [`PROGRAM-CHARTER.md`](PROGRAM-CHARTER.md) 和
[`open-infrastructure-strategy-constitution.md`](architecture/open-infrastructure-strategy-constitution.md)。
组合不聚合 Authority，覆盖不等于 Correctness 或 Truth。

### Attention

[`ADR-033`](architecture/ADR-033-attention-principle-for-dynamic-coordination.md)
把 Attention 定义为动态资源分配和候选参与选择，而不是中央调度权、Permission、
Evidence、Truth 或 SAEE 控制器。该原则同样进入 Program Charter 与战略宪法。

```text
Attention decides candidate participation.
Authorization governs actual participation.
Evidence supports bounded claims.
SAEE evaluates without controlling execution.
```

## Material not promoted

### Control-plane projections

旧 `PROGRAM-STATUS`、README、Risk Register 和 AGENTS 记录的是较早的 Telemetry、
PR-G2A、Community 或 Production-path 状态。当前 `main` 已进入 Agent-native commercial
maturity 主线，并保持：

```text
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY
PROGRAM_STATUS=WAITING_FOR_HUMAN_DECISION
NEXT_HUMAN_DECISION=CR01_D03_OPTION_C_IMPLEMENTATION_AND_CAP_EXCEPTION
```

因此旧状态没有被复制或拼接进当前控制面。

### Intelligence

2026-07-24 至 2026-07-27 的旧简报，以及旧 MCP / Capability Provenance 候选，均早于
[`2026-07-29 primary-source-corrected brief`](intelligence/2026-07-29/intelligence-brief.md)。
旧材料只作为本地历史保留，不成为新的公开事实来源。

### DEB and Digital Survival research

DEB-001、Digital Survival Theory、Digital Ecology Box、Digital Cell 和 Self-Governance
材料包含 theory、design、review、pre-registration、dry-run、closure 和 hash-preparation
等不同状态，不能合并为“实验已经执行”或“理论已经成为当前标准”。当前规范只保留
[`Agent-Native Ecology Box 001 research archive`](TITMAS/research/agent-native-ecology-box-001/README.md)
中的有界结论；旧材料继续留在旧目录，等待独立的研究谱系与证据核验。

### TITMAS constitution candidates

当前规范章程是
[`titmas-architecture-charter-v1.0.md`](architecture/titmas-architecture-charter-v1.0.md)。
旧 `titmas-architecture-charter-v0.2.md` 和 Digital Immune Constitution candidate 不得
创建平行核心宪法；Digital Immune 继续只是 explanatory layer（解释层）。

## Validation boundary

```text
LEGACY_SOURCE_FILES_OBSERVED=76
LEGACY_SOURCE_FILES_COPIED_VERBATIM=2
CURRENT_CONTROL_DOCUMENTS_REPLACED_WHOLESALE=false
LEGACY_CHECKOUT_MODIFIED=false
DBOS_MODIFIED=false
SAEE_MODIFIED=false
RUNTIME_CREATED=false
EXECUTOR_CREATED=false
AUTHORITY_CREATED=false
PERMISSION_GRANTED=false
EVIDENCE_TRUTH_CHANGED=false
CURRENT_CR01_GATE_CHANGED=false
```

本报告证明材料已被逐项路由，不证明所有旧材料都应进入当前规范，也不关闭任何当前
Decision、Risk、Gate、Commercial、Release 或 Adoption 状态。

## TITMAS Drift Check

```text
TITMAS_DRIFT_CHECK
CORE_INTEROPERABILITY_OBJECTIVE_PRESERVED=true
NEW_CONTROL_AUTHORITY_CREATED=false
NEW_TRUTH_SOURCE_CREATED=false
DUPLICATE_EVIDENCE_OR_VERIFICATION_CREATED=false
RUNTIME_OR_EXECUTOR_CREATED=false
CURRENT_CAPABILITY_OVERCLAIMED=false
PUBLIC_LAUNCH_AUTHORIZED=false
COMMUNITY_ESTABLISHED=false
TITMAS_DRIFT_CHECK_RESULT=PASS_WITH_RECORDED_LIMITATIONS
```
