---
document_id: DBA-PUBLIC-OVERVIEW-0.1
title: Digital Biosphere Public Project Overview v0.1
title_zh: 数字生物圈公开项目总览 v0.1
status: developer-preview-v0.1-public-entry
release_status: released-not-production-ready
public_positioning: Trusted Multi-Agent Infrastructure
implementation_authorized: false
runtime_effect: none
last_reviewed: 2026-07-22
---

# Digital Biosphere Public Project Overview v0.1（数字生物圈公开项目总览 v0.1）

> 我们提供可信多智能体基础设施，让 AI Agent（人工智能智能体）能够长期运行、协作并产生可验证证据。

Digital Biosphere（数字生物圈）是总项目；Trusted Multi-Agent Infrastructure（可信多智能体基础设施）是统一对外定位。它不是新的 Agent Framework（智能体框架），而是把身份、生命周期、执行记录、证据引用、验证、评价和受控演化连接起来的基础设施方向。

本页是 `Trusted Multi-Agent Infrastructure Developer Preview v0.1`（可信多智能体基础设施开发者预览版 v0.1）的单一理解入口。AI agent 是首要客户；人类仍保留发布、权限和重大外部动作的最终权力。当前状态是 `RELEASED_NOT_PRODUCTION_READY`：Developer Preview 已正式发布，但不声称三项目已经完成生产端到端集成、客户采用或生产部署。

Developer Preview 也是 DBOS 与 SAEE 的跨项目测试工程：同一个受控协作场景既用于展示，也用于发现记录、验证、接口和评价缺口。测试发现的缺口经过 DBA 归属与重复建设审查后，可以在 DBOS 或 SAEE 中补最小功能；这不允许 Demo 自己成为新的基础设施权威。

## 1. Architecture at a Glance（架构总览）

```text
Digital Biosphere
  public positioning: Trusted Multi-Agent Infrastructure
  |
  +-- DBA   Program Governance and Architecture Cockpit
  |         项目群治理、架构边界、路线图、风险、决策与集成闸门
  |
  +-- DBOS  Existence Infrastructure
  |         身份、生命周期、能力边界、执行记录、证据引用与验证
  |
  +-- SAEE  Evolution Intelligence Layer
            可靠性、稳定性、风险评价与演化建议
```

三者共同服务一个项目目标，但保持独立责任域：

```text
DBA_NE_DBOS=true
DBA_NE_SAEE=true
DBOS_NE_SAEE=true
SAEE_NE_DBOS=true
DBOS_NE_AGENT_FRAMEWORK=true
SAEE_NE_AUTOMATIC_CONTROLLER=true
```

## 2. What the Developer Preview Must Demonstrate（开发者预览必须展示什么）

Developer Preview v0.1 只有在以下连续链路可运行并可复核时才成立：

```text
Three governed role simulations（三个受治理角色模拟）
  Research Agent -> Analysis Agent -> Review Agent
        |
        v
DBOS trust records（DBOS 可信记录）
  Identity -> Execution -> Evidence Reference -> Validation
        |
        v
SAEE bounded evaluation（SAEE 受限评价）
  Reliability -> Stability -> Risk -> Evolution Recommendation
        |
        v
Governance Decision（治理决策，保留人工权力）
```

角色名用于演示协作语义，不自动创建生产 Agent、Runtime、Permission 或 Digital Organism（数字有机体）。SAEE 的 Recommendation（建议）不是 Decision（决策），Decision 也不是 Execution（执行）。

## 3. Current Truth（当前事实）

截至 2026-07-22：

- DBA 已建立项目群驾驶舱、路线图、项目组合和集成闸门；Developer Preview v0.1 已按 `ADR-022` 发布，但不构成生产就绪或客户采用；
- DBOS 已形成 local editable install（本地可编辑安装）、单一测试入口、Quick Start（快速入门）和三角色 synthetic demo（合成演示）；334/334 tests 与 34/34 validators 在冻结源码通过；
- `DBOS-EXP-0001` 历史 Evidence 没有被改写；版本感知校验能保留旧 binding 并显式警告当前文档漂移；
- SAEE 已形成只读 DBOS Developer Preview adapter（开发者预览适配器），复用现有 Reliability Framework 与 `saee.evaluate_agent_run`；
- DBOS → SAEE 本地合成链路已通过 scoped conformance（限定范围符合性），但结果诚实保持 `Reliability=NOT_ASSESSED`、`Stability=NOT_ASSESSED`、`EvolutionRecommendation=HOLD`；
- 首轮 Agent Customer Validation（智能体客户验证）完成 12/12 个跨千帆／方舟会话并得到 `CONDITIONAL`；修复后复测 `TMAI-ACV-20260722-002` 再完成 12/12，会话与全部预冻结阈值通过，12/12 overall verdict 为边界正确的 `CONDITIONAL`；
- 开放网络观察 `TMAI-OWD-20260722-001` 已得到 GitHub 新 description 的部分索引命中，但规范英文名、中文名和公开搜索仍无精确命中，因此保持 `PARTIAL_METADATA_ONLY`；
- 旧的 3–5 名人类开发者试用路线已由 `ADR-021` 取代为可选次级研究，不再是本次首要发布前置条件；
- DBOS 整仓继续为 private（私有）；exact public-safe wheel 已作为 v0.1 GitHub Release asset 公开，但没有 public Runtime、托管 API、Permission 或生产兼容声明。

时间点事实以 [`PROGRAM-STATUS.md`](PROGRAM-STATUS.md) 为准；本页不把 Developer Preview 发布升级为生产实现、客户采用或运行授权。

## 4. Developer Navigation（开发者导航）

| 需要了解 | 入口 | 当前效力 |
|---|---|---|
| 项目是什么 | 本页 | Developer Preview v0.1 公开定位 |
| 当前做到哪里 | [`PROGRAM-STATUS.md`](PROGRAM-STATUS.md) | 时间点治理快照 |
| 智能体如何发现、评估和推荐 | [`AGENT-CUSTOMER-PACKAGE-v0.1.1.json`](AGENT-CUSTOMER-PACKAGE-v0.1.1.json) | 机器可读入口与复测结果；不等于 Runtime 发布 |
| 智能体客户验证协议 | [`AGENT-CUSTOMER-VALIDATION-PROTOCOL.md`](AGENT-CUSTOMER-VALIDATION-PROTOCOL.md) | 预冻结 Provider、场景、阈值和非效果 |
| 首轮智能体客户验证结果 | [`AGENT-CUSTOMER-VALIDATION-REPORT.md`](AGENT-CUSTOMER-VALIDATION-REPORT.md) | 历史基线 `CONDITIONAL`；失败保留 |
| 修复后智能体客户验证结果 | [`AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md`](AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md) | `PASS`；不等于采用或发布授权 |
| 开放网络自然发现观察 | [`OPEN-WEB-DISCOVERY-OBSERVATION.md`](OPEN-WEB-DISCOVERY-OBSERVATION.md) | `PARTIAL_METADATA_ONLY`；描述命中不等于规范名称自然发现 |
| Developer Preview 如何完成 | [`DEVELOPER-PREVIEW-PLAN.md`](DEVELOPER-PREVIEW-PLAN.md) | 交付与 gate 计划 |
| 如何发布 | [`DEVELOPER-PREVIEW-RELEASE-PLAN.md`](DEVELOPER-PREVIEW-RELEASE-PLAN.md) | 发布治理计划 |
| 正式发布证据 | [`DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md`](DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md) | GitHub、匿名安装与百度云外部复验 |
| 本地符合性结果 | [`DEVELOPER-PREVIEW-CONFORMANCE-REPORT.md`](DEVELOPER-PREVIEW-CONFORMANCE-REPORT.md) | 当前工作树本地通过；不是 release |
| 可选人类可用性研究 | [`EXTERNAL-DEVELOPER-TRIAL-PLAN.md`](EXTERNAL-DEVELOPER-TRIAL-PLAN.md) | 已由 `ADR-021` 取代为非阻塞次级路线 |
| 可选人类试用操作 | [`EXTERNAL-DEVELOPER-TRIAL-GUIDE.md`](EXTERNAL-DEVELOPER-TRIAL-GUIDE.md) | 历史／可选手册，不是首要 gate |
| 反馈格式 | [`DEVELOPER-FEEDBACK-TEMPLATE.md`](DEVELOPER-FEEDBACK-TEMPLATE.md) | 模板已准备；不是采用证明 |
| DBOS public-safe wheel | [`DBOS-PUBLIC-PACKAGE-MANIFEST-v0.1.json`](DBOS-PUBLIC-PACKAGE-MANIFEST-v0.1.json) | 已发布的有界 Developer Preview 包；不是 Runtime 或生产 SDK |
| 架构与责任边界 | [`README.md`](README.md) 与 [`architecture/`](architecture/) | DBA 规范表面 |
| 为什么进入此阶段 | [`architecture/ADR-017-trusted-multi-agent-infrastructure-developer-preview.md`](architecture/ADR-017-trusted-multi-agent-infrastructure-developer-preview.md) | 已接受的阶段决策 |
| 为什么允许发布 | [`architecture/ADR-022-developer-preview-release.md`](architecture/ADR-022-developer-preview-release.md) | exact artifact 和公开边界的人工发布决定 |

## 5. Public Claim Boundary（对外声明边界）

Release Gate（发布闸门）已经通过。当前允许使用：

> Trusted Multi-Agent Infrastructure Developer Preview v0.1 is released（可信多智能体基础设施开发者预览版 v0.1 已发布）。

仍不得使用：

- production-ready（生产就绪）；
- end-to-end integration verified（端到端集成已验证）；
- autonomous evolution（自主演化）；
- Agent platform（智能体平台）；
- production SDK（生产 SDK）；
- evidence proves truth（证据证明真相）。

```text
PUBLIC_ENTRY_DEFINED=true
DEVELOPER_PREVIEW_RELEASED=true
SCOPED_LOCAL_DEMO_CONFORMANCE_PASS=true
FULL_END_TO_END_INTEGRATION_VERIFIED=false
PRIMARY_CUSTOMER=AI_AGENT
AGENT_CUSTOMER_VALIDATION_BASELINE=CONDITIONAL
AGENT_CUSTOMER_VALIDATION_RERUN=PASS
AGENT_CUSTOMER_API_SESSIONS=24
HUMAN_DEVELOPER_TRIAL_REQUIRED_FOR_PRIMARY_ROUTE=false
OPEN_WEB_DISCOVERY=PARTIAL_METADATA_ONLY
OPEN_WEB_DISCOVERY_OBSERVATION_ID=TMAI-OWD-20260722-001
GITHUB_DISCOVERY_METADATA_REMEDIATED=true
GITHUB_METADATA_DESCRIPTION_MATCH=true
OPEN_WEB_CANONICAL_NAME_MATCH=false
PRODUCTION_RUNTIME_CREATED=false
AGENT_INSTANCE_CREATED=false
PERMISSION_GRANTED=false
EVIDENCE_NE_TRUTH=true
```
