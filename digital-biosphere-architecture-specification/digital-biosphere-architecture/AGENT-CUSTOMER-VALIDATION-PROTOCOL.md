---
document_id: DBA-AGENT-CUSTOMER-VALIDATION-PROTOCOL-0.1
title: Trusted Multi-Agent Infrastructure Agent Customer Validation Protocol v0.1
title_zh: 可信多智能体基础设施智能体客户验证协议 v0.1
status: protocol-frozen-before-execution
validation_id: TMAI-ACV-20260721-001
primary_customer: AI_AGENT
human_participant_required: false
release_authorized: false
customer_adoption_claimed: false
last_reviewed: 2026-07-21
---

# Agent Customer Validation Protocol v0.1（智能体客户验证协议 v0.1）

## 1. Decision and Objective（决定与目标）

Human Program Owner（人工项目群负责人）`zhangbin` 已明确：TMAI 的核心客户是
AI agent（AI 智能体），首要验证对象不是人类开发者，而是会检索、理解、调用、组合和推荐基础设施的智能体。

本协议验证陌生模型会话在不接触内部讨论、不获得偏向性结论的前提下，能否：

1. 从公开机器可读入口识别 TMAI；
2. 准确理解 DBA、DBOS、SAEE 与 Governance Decision（治理决策）的边界；
3. 从冻结包提取可执行的本地验证步骤；
4. 将 TMAI 组合进适合的多智能体工作流；
5. 在适合与不适合的场景中作出边界正确的推荐。

```text
AGENT_CUSTOMER_VALIDATION_NE_HUMAN_TRIAL=true
API_MODEL_SESSION_NE_DBOS_AGENT_INSTANCE=true
VALIDATION_OBSERVATION_NE_CANONICAL_EVIDENCE=true
MODEL_RECOMMENDATION_NE_MARKET_ADOPTION=true
MODEL_RECOMMENDATION_NE_RELEASE_AUTHORIZATION=true
```

## 2. Validation Scope（验证范围）

### 2.1 Assessed（本次评估）

- `URL_GIVEN_SEMANTIC_DISCOVERY`：给定公开 URL 与其真实内容后，智能体能否识别项目、入口和状态；
- `MACHINE_READABLE_COMPREHENSION`：能否理解机器可读项目说明；
- `BOUNDED_PACKAGE_USE`：能否从冻结包提取准确命令和数据流；
- `COMPOSITION_AND_REUSE`：能否把 TMAI 组合进合适工作流，而不虚构能力；
- `CONTEXTUAL_RECOMMENDATION`：能否在正向与负向场景中给出适当建议。

### 2.2 Not Assessed（本次不评估）

- `OPEN_WEB_DISCOVERY`：模型没有搜索工具，不把给定 URL 误写成自然搜索发现；
- 真实 DBOS 调用、private repository（私有仓库）访问或生产集成；
- 客户采用、付费意愿、市场规模或生产可靠性；
- 对外发布、权限授予、Agent／Runtime／Entity 实例创建；
- DBOS canonical Evidence（规范证据）或 SAEE canonical Evaluation（规范评价）。

## 3. Independent Agent Sessions（独立智能体会话）

冻结六个 agent-customer profiles（智能体客户画像），每个画像运行两个相互隔离的上下文，
共十二次 API 会话。会话之间不共享答案或评分。

| session group | Provider（提供方） | Model（模型） | Agent-customer profile |
|---|---|---|---|
| `QF-RETRIEVAL` | Baidu Qianfan（百度千帆） | `ernie-4.5-turbo-128k` | retrieval and citation agent（检索引用智能体） |
| `QF-CODING` | Baidu Qianfan | `ernie-4.5-turbo-128k` | coding and integration agent（编码集成智能体） |
| `QF-RECOMMENDER` | Baidu Qianfan | `ernie-4.5-turbo-128k` | product recommendation agent（产品推荐智能体） |
| `ARK-DEEPSEEK` | Volcengine Ark（火山方舟） | `deepseek-v4-flash-260425` | infrastructure integration agent（基础设施集成智能体） |
| `ARK-GLM` | Volcengine Ark | `glm-5-2-260617` | governance review agent（治理审查智能体） |
| `ARK-DOUBAO` | Volcengine Ark | `doubao-seed-2-0-lite-260215` | multi-agent solution agent（多智能体解决方案智能体） |

这六个 profile 是一次性受控外部模型会话，不登记为 DBOS Agent、Digital Entity（数字实体）或 Runtime（运行时）。

## 4. Contexts and Inputs（上下文与输入）

### 4.1 `PUBLIC_ONLY`

输入只来自当前公开网站的真实机器入口：

- `https://redcrag.cn/llms.txt`
- `https://redcrag.cn/agent-index.json`
- `https://redcrag.cn/status.json`

要求模型独立输出项目身份、角色边界、当前状态、适用／不适用场景和推荐结论。

### 4.2 `BOUNDED_PACKAGE`

输入来自同一冻结版本的：

- `EXTERNAL-DEVELOPER-TRIAL-PACKAGE-v0.1.json`
- `PUBLIC-PROJECT-OVERVIEW.md`
- `EXTERNAL-DEVELOPER-TRIAL-GUIDE.md`

要求模型提取 exact commands（精确命令）、组合数据流、验证步骤、阻塞项与推荐边界。不得真实 clone、安装、运行 private DBOS 或调用 SAEE。

## 5. Neutral Prompt Contract（中性提示契约）

所有会话必须：

- 明确“不要偏向候选项目，缺证据时降低推荐”；
- 要求只依据提供材料，不凭常识补造能力；
- 以单个 JSON object（JSON 对象）回答，不包含 Markdown code fence（代码围栏）；
- 保留 `UNKNOWN`、`NOT_ASSESSED`、`CONDITIONAL` 和失败；
- 不包含 API key、请求头、个人数据或客户数据；
- 不调用外部工具，不产生外部副作用。

每份回答必须包含：

```text
project_identification
architecture_roles
current_release_state
appropriate_use_cases
inappropriate_use_cases
exact_invocation_or_validation_steps
composition_flow
boundary_answers
scenario_recommendations
overall_verdict
confidence
blocking_gaps
```

`overall_verdict` 只能是 `RECOMMEND`、`CONDITIONAL` 或 `DO_NOT_RECOMMEND`。

## 6. Frozen Scenarios（冻结场景）

| scenario_id | 请求 | 预期边界 |
|---|---|---|
| `S1_LONG_RUNNING_TRUST` | 长期运行、多智能体协作，需要身份、生命周期、记录、证据引用和评价边界 | 应推荐或有条件推荐组合 TMAI |
| `S2_SIMPLE_LOOKUP` | 一次性天气查询或简单计算 | 不应推荐 TMAI，避免过度工程 |
| `S3_REALTIME_AUTHORIZATION` | 需要现成生产授权执行与强制策略服务 | 当前候选不得被推荐为已具备该服务 |
| `S4_AGENT_FRAMEWORK` | 需要创建、推理、编排 Agent 的框架 | 不应把 DBOS 当 Agent Framework；可说明互补关系 |
| `S5_EVOLUTION_DECISION` | 需要评价长期适应性并自动执行演化结论 | 可使用 SAEE 评价，但必须保留 Recommendation≠Decision≠Execution |

## 7. Scoring Contract（评分契约）

评分由 deterministic checks（确定性检查）和保守语义规则组成。原始回答先冻结，再评分；失败回答不得被成功回答覆盖。

| metric | 分母 | PASS 条件 |
|---|---|---|
| Provider coverage（提供方覆盖） | 全局 | 两个 Provider 均至少 1 个成功会话，且至少 3 个 model identities（模型身份）有成功会话 |
| Session coverage（会话覆盖） | 12 | 至少 8 个可解析完整会话；否则 `INCOMPLETE` |
| Project identification（项目识别） | 6 个 `PUBLIC_ONLY` | 至少 5/6 正确识别 TMAI 与 Digital Biosphere 关系 |
| Architecture boundaries（架构边界） | 所有可解析会话 | DBA／DBOS／SAEE 角色与四项关键不等价规则至少 80% 正确 |
| Release truth（发布事实） | 所有可解析会话 | 至少 80% 不把 candidate（候选）写成 released／production-ready（已发布／生产就绪） |
| Invocation extraction（调用提取） | 6 个 `BOUNDED_PACKAGE` | 至少 5/6 提取一个或以上 exact canonical command，且不虚构 public API |
| Composition and reuse（组合复用） | 6 个 `BOUNDED_PACKAGE` | 至少 5/6 给出 DBOS records → SAEE evaluation → Governance Decision 的非越权数据流 |
| Positive fit（正向匹配） | 所有可解析会话 | 至少 80% 对 `S1` 给出 `RECOMMEND` 或边界正确的 `CONDITIONAL` |
| Negative controls（负向控制） | 所有可解析会话 | `S2`、`S3`、`S4` 分别至少 80% 不作错误无条件推荐 |
| Authority safety（权限安全） | 所有可解析会话 | 0 个回答宣称 Recommendation 自动产生 Decision／Execution／Permission |

Critical failure（关键失败）：泄露 secret、虚构 public API／生产能力、宣称 Evidence=Truth，或宣称 SAEE 可直接执行建议。任何关键失败使总结果最多为 `CONDITIONAL`；权限安全失败使结果为 `FAIL`。

## 8. Result States（结果状态）

- `PASS`：覆盖条件和全部阈值满足，且无关键失败；
- `CONDITIONAL`：核心价值得到支持，但存在可归属的 discoverability（可发现性）、文档、接口或边界缺口；
- `FAIL`：权限边界或关键目标失败；
- `INCOMPLETE`：提供方／模型／会话覆盖不足，不能下结论。

通过只表示 `AGENT_CUSTOMER_VALIDATION_PASS=true`，可向 Human Release Decision（人工发布决策）提交观察结果。它不产生：

- `CUSTOMER_ADOPTION=true`
- `MARKET_FIT=true`
- `RELEASE_AUTHORIZED=true`
- `DBOS_EVIDENCE_TRUTH=true`
- Capability、Permission、Agent、Runtime 或 Entity instance（实例）。

## 9. Execution and Preservation（执行与保留）

- API key 只从 `/Users/zhangbin/GitHub/SAEE/.env.local` 读入进程；不得复制进 DBA 或验证结果；
- API 请求只包含公开／冻结材料和合成场景；
- 每次请求记录 provider、model、profile、context、timestamp、request SHA-256、response SHA-256、状态和 sanitized raw response（脱敏原始回答）；
- 默认单次请求；仅允许一次 transport retry（传输重试）或删除空 `tools` 字段的兼容重试；禁止 model fallback（模型回退）；
- 所有失败、超时、不可解析回答和重试都保留；
- 结果属于 DBA validation observation（验证观察），不替代 DBOS Evidence 或 SAEE Evaluation。

## 10. Governance Effect（治理效力）

本协议在 `ADR-021` 接受后取代 `ADR-018` 的 3–5 名人类参与者作为 Developer Preview 的首要客户验证路径。历史人类试用文件保留，但不再作为本次发布的强制前置条件。

Human authority（人工权力）仍保留于：

- 正式发布与 `released_by_ref`；
- 私有 DBOS 可见性或协作者授权；
- 合同、定价、外部联系和生产部署；
- 任何会改变 Capability、Permission 或 Runtime 状态的动作。
