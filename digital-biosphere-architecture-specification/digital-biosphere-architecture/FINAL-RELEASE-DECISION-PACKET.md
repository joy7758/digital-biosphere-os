---
document_id: DBA-FINAL-RELEASE-DECISION-PACKET-0.1
title: Trusted Multi-Agent Infrastructure Developer Preview v0.1 Final Release Decision Packet
title_zh: 可信多智能体基础设施开发者预览版 v0.1 最终发布决策包
status: release-executed
release_authorized: true
release_executed: true
developer_preview_cloud_release_authorized: true
website_candidate_deployment_authorized: true
website_candidate_deployed: true
website_candidate_github_prerelease_published: true
license_selected: true
license_id: Apache-2.0
release_preparation_authorized: true
trial_execution_authorized: false
last_reviewed: 2026-07-22
---

# Final Release Decision Packet v0.1（最终发布决策包 v0.1）

## 1. Current Proven State（当前已证明状态）

| Surface（表面） | Current evidence（当前证据） | 状态 |
|---|---|---|
| DBA GitHub | public `main@95fcc363`；正式 tag `v0.1-developer-preview` 指向 `1113130c` | `FORMAL_RELEASE_PASS` |
| DBOS GitHub | `origin/main@cd3f867`；fresh install、334 tests、34 validators、两个 Demo | `REMOTE_CLEAN_CLONE_PASS_PRIVATE_REPO` |
| SAEE GitHub public layer | `origin/main@2173c25`；19/19 blobs、public smoke/demo、8 tests | `PUBLIC_SAFE_ADAPTER_PASS` |
| Cross-project Clean Clone | `CLEAN-CLONE-VALIDATION-REPORT.md` | `PASS_FROZEN_REMOTE_SOURCES` |
| Baidu website | `https://redcrag.cn/` 中英文正式站点；21/21 manifest、健康、安全头和回滚连续性通过 | `FORMAL_DEPLOYMENT_PASS` |
| External trial | 技术包 `TMAI-DP-v0.1-TRIAL-20260721-001` 已冻结；参与者 0；`participant_source` 仍是占位符 | `CONDITIONALLY_AUTHORIZED_NOT_EFFECTIVE` |
| Agent customer validation | `TMAI-ACV-20260721-001`；千帆／方舟 12/12；公开识别 6/6；权限错误 0 | `CONDITIONAL_REMEDIATION_REQUIRED` |
| Agent customer validation rerun | `TMAI-ACV-20260722-002`；相同阈值；12/12 sessions；全部阈值通过 | `PASS_NOT_RELEASE_AUTHORIZATION` |
| Open-web discovery | `TMAI-OWD-20260722-001`；规范英文名、中文名与公开搜索仍未命中；ADR-022 仅为 v0.1 接受限制 | `PARTIAL_METADATA_ONLY_ACCEPTED_FOR_V0_1` |
| GitHub Developer Preview | `v0.1-developer-preview`；non-draft；non-prerelease；两个 assets 匿名 hash PASS | `FORMAL_RELEASE_PASS` |
| DBOS repository visibility | GitHub API 返回 `PRIVATE`；exact wheel 已公开并隔离安装通过 | `WHOLE_REPOSITORY_PRIVATE_EXACT_WHEEL_PUBLISHED` |

## 2. DQ-011 — SAEE Adapter Publication Boundary（SAEE 适配器公开边界）

精确技术清单和隔离复验见
[`SAEE-PUBLIC-SAFE-EXTRACTION-REVIEW.md`](SAEE-PUBLIC-SAFE-EXTRACTION-REVIEW.md)。
现有候选在隔离目录中 8/8 tests 通过并能消费冻结 DBOS 演示输出，但最小闭包为
19 个文件，且 8 个 Python 实现／测试路径全部不在 SAEE public `main`。这使公开
边界修订成为真实 Decision，而不是缺少一次复制命令。

### Dependency audit（依赖审计）

当前内部、只读 Adapter 的最小 Python 依赖闭包为：

1. `scripts/saee_evaluate_dbos_preview.py`；
2. `saee_backend/services/dbos_developer_preview_adapter.py`；
3. `saee_backend/services/baidu_agent_readiness_service.py`；
4. `saee_backend/services/reliability_framework/assessment_adapter.py`；
5. `saee_backend/services/reliability_framework/failure_classifier.py`；
6. `saee_backend/services/evidence_adequacy.py`；
7. `saee_backend/services/resource_resolution_receipt.py`。

它还需要 5 个 Qianfan request/response schemas、Evidence Adequacy schema、4 个
claim profiles 和 Resource Resolution Receipt schema。SAEE public `main` 的
`PUBLICATION_BOUNDARY.md` 已对精确 19 文件投影形成有界例外；general runtime、private
scoring、kernel、selection、mutation 和 lineage 仍被排除。

### Options（选项）

| Option | 说明 | 结论 |
|---|---|---|
| `A_PUBLIC_SAFE_EXTRACTION` | 以有来源、hash-bound（哈希绑定）的 public abstraction package（公共抽象包）迁移上述最小闭包；保留负向测试与非声明，不携带 kernel/selection/mutation/lineage/private backend | `APPROVED_EXACT_19_FILES_BY_ADR-020` |
| `B_HOSTED_EVALUATION_API` | 在百度部署远程 SAEE service（服务），开发者只调用接口 | `NOT_RECOMMENDED_V0_1`：会新增 Runtime/API/Auth/运营边界 |
| `C_REMOVE_EXECUTABLE_SAEE_ADAPTER` | v0.1 只发布 SAEE 文档和 toy demo | `NOT_RECOMMENDED`：无法满足已冻结跨项目试用目标 |

`ADR-020` 已由 Human Program Owner 和 SAEE Domain Owner `zhangbin` 明确批准
`A_PUBLIC_SAFE_EXTRACTION_EXACT_19_FILES`。迁移必须是同一 evaluator 的可验证投影，
不得手工重写为第二套算法。当前公共投影已通过 Clean Clone，但仍只是 read-only
Developer Preview evaluation entry（只读开发者预览评价入口）。

```text
AGENT_RECOMMENDATION=RECOMMENDED_FOR_RELEASE_PREPARATION_IMPLEMENTATION
SAEE_PUBLICATION_BOUNDARY_AMENDMENT_REQUIRED=false
PRIVATE_CORE_PUBLICATION_AUTHORIZED=false
PUBLIC_ADAPTER_MIGRATION_AUTHORIZED=true
PUBLIC_SAFE_EXTRACTION_IMPLEMENTED=true
PUBLIC_SAFE_EXTRACTION_REMOTE_COMMIT=2173c258f91aed03fc02c0097d4250a87be703aa
PUBLIC_SAFE_EXTRACTION_BLOB_MATCH=19/19
```

## 3. DQ-012 — Public License（公开许可证）

在 `ADR-020` 记录决定时，DBA、DBOS、SAEE 均无根 `LICENSE`。Human Owner 随后已在
三个最终远端基线采用 `Apache-2.0`，并由 Clean Clone 逐字节核验官方许可证全文。

该决定只覆盖 Owner-created public surfaces（负责人创作的公开表面），不自动重许可
第三方资产、依赖、数据、Evidence 或独立许可材料。

```text
RECOMMENDED_LICENSE=Apache-2.0
LICENSE_SELECTED=true
LICENSE_PUBLICATION_AUTHORIZED=true
LICENSE_ADOPTION_IMPLEMENTED_IN_ALL_REPOSITORIES=true
```

## 4. DQ-013 — Baidu Deployment Target（百度部署目标）

Human Owner 随后明确旧 SAEE 与 Agent Evidence Receipt 应用资产已经过期，授权在
保留系统、证书和安全配置的前提下完整清理，并要求建立中英文新网站。原独立路径问题
因此由 `ADR-019` 标记为 `SUPERSEDED`。

当前已执行：

```text
release_directory=/srv/tmai/releases/1113130ca4213b70fcebd6247fec794854295e8c
public_path=https://redcrag.cn/
website_candidate_deployed=true
atomic_rollback_required=true
atomic_rollback_validated=true
developer_preview_released=true
```

网站候选和 GitHub prerelease 继续作为历史记录。正式 Developer Preview 已由 ADR-022
单独授权并完成；该完成不授权 DBOS 整仓公开、SAEE 写回、Runtime 或 Permission。

## 5. DQ-014 — DBOS Repository Visibility（DBOS 仓库可见性）

只读预检见
[`DBOS-PUBLIC-VISIBILITY-PREFLIGHT.md`](DBOS-PUBLIC-VISIBILITY-PREFLIGHT.md)。
当前 `main@cd3f867` 的 460 个 tracked files（已跟踪文件）中未发现高置信度密钥模式、
敏感文件名、私网地址或超过 5 MiB 的历史 blob；官方
`gitleaks/gitleaks@v8.30.1` 的历史和工作树扫描均为 0 findings。但 48 个跟踪文件包含
本机绝对路径，`registry/agents.yaml` 还列出未纳入发布的本地项目资产。因此整仓公开
失败关闭，不能把“无密钥命中”扩大为“适合公开”。

DBOS `cd3f867` 的 clean clone 使用当前 GitHub 凭据完成；这不是 anonymous clone
（匿名检出）证据。仓库当前为 `PRIVATE`。独立的 public-safe wheel（公开安全分发包）
已从该精确提交构建，排除 registry、evidence、reports、tests、tools 和本机路径；它在
隔离环境安装后返回 `PASS`，现有精确公开 URL：
<https://github.com/joy7758/digital-biosphere-architecture-specification/releases/download/v0.1-developer-preview/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl>。

`ADR-022` 已选择更适合 AI agent 客户的后继路线：DBOS 整仓继续 private，只将 exact
wheel 作为 Developer Preview GitHub Release asset（开发者预览 GitHub 发布资产）公开。
该决定不授权 PyPI、Runtime、Permission 或整仓 visibility 变化。

```text
DBOS_REPOSITORY_VISIBILITY=PRIVATE
ANONYMOUS_CLONE_VALIDATED=false
DBOS_PUBLICATION_AUTHORIZED=true
PRIVATE_COLLABORATOR_TRIAL_SELECTED=true
WHOLE_DBOS_REPOSITORY_PUBLIC_RECOMMENDED=false
DBOS_PUBLIC_SAFE_WHEEL_VALIDATED=true
DBOS_PUBLIC_SAFE_WHEEL_PUBLISHED=true
DBOS_PUBLIC_SAFE_WHEEL_PACKAGE_ID=TMAI-DBOS-WHEEL-CANDIDATE-20260722-001
```

## 6. Recorded Human Decision（已记录人工决定）

```text
decided_by_ref=zhangbin
dq_001_program_owner=zhangbin
dq_010_trial=AUTHORIZE_AFTER_CLEAN_CLONE_PASS
dq_011_saee_public_safe_extraction=A_PUBLIC_SAFE_EXTRACTION_EXACT_19_FILES
dq_012_license=Apache-2.0
dq_013_baidu_isolated_path=superseded_by_ADR-019
dq_014_dbos_visibility=PRIVATE_COLLABORATOR_TRIAL
dq_015_primary_customer_validation=ADOPT_AGENT_NATIVE_CUSTOMER_VALIDATION
dq_016_dbos_agent_distribution=PUBLISH_PUBLIC_SAFE_DBOS_WHEEL
whole_dbos_repository_visibility=KEEP_PRIVATE
open_web_limitation=ACCEPT_PARTIAL_METADATA_ONLY_FOR_V0_1
dq_009_release=AUTHORIZE_TRUSTED_MULTI_AGENT_INFRASTRUCTURE_DEVELOPER_PREVIEW_V0_1
released_by_ref=zhangbin
trial_coordinator=zhangbin
participant_source=PENDING_REAL_INPUT
decision_timestamp=2026-07-21T22:48:39+08:00
```

`ADR-021` 已把上面的人类参与者路线取代为可选次级研究；它没有把未发生的人类试用
改写成通过。首要验证修复已完成并通过，`R-015` 依赖复核也已完成并保留有界残余披露。
`ADR-022` 已处理 DBOS agent access／distribution（智能体访问／分发）、开放网络发现
限制、`released_by_ref` 和正式发布授权。tag、GitHub Release、匿名 wheel 校验、隔离
安装和百度 formal deployment 已通过外部复验。

本决策包与 `ADR-022` 构成 release execution authorization（发布执行授权）。Decision
仍不等于 Execution；本次完成证据见
[`DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md`](DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md)。
