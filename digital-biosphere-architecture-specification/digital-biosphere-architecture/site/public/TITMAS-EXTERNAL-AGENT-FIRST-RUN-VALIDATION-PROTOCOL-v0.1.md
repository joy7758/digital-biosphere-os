---
document_id: TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-PROTOCOL-0.1
title: TITMAS External Agent First Run Validation Protocol v0.1
title_zh: TITMAS 外部智能体首次运行验证协议 v0.1
version: 0.1.0
status: development-validation-protocol
primary_customer: AI_AGENT
primary_repository: digital-biosphere-architecture
commercial_offering_available: false
production_ready: false
certification_available: false
---

# TITMAS External Agent First Run Validation Protocol v0.1

中文：**TITMAS 外部智能体首次运行验证协议 v0.1**。

## 1. Purpose（目的）

本协议验证一个没有 TITMAS 私有历史、未接触本地工作树的 AI 智能体，能否仅凭公开材料：

```text
Discover
  -> Understand
  -> Select the bounded evaluation path
  -> Validate a synthetic object
  -> Explain PASS and its limits
  -> Recommend or reject with reasons
```

验证对象是
[`TITMAS Commercial Evaluation Pack v0.1`](TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.md)，
不是 TITMAS 的生产 Runtime、商业产品、认证能力或客户采用。

## 2. Recommendation Target（推荐目标）

智能体必须分别回答两个问题，不得合并：

1. 是否推荐该包用于 **offline, read-only commercial evaluation**（离线只读商业评估）；
2. 是否推荐 TITMAS 用于 **production purchase or deployment**（生产采购或部署）。

在当前状态下，允许的正确结论包括：

```text
EVALUATION_USE=RECOMMENDED|CONDITIONALLY_RECOMMENDED|NOT_RECOMMENDED
PRODUCTION_OR_PURCHASE_USE=NOT_RECOMMENDED
```

`NOT_RECOMMENDED` 不自动表示验证失败。只要理由与公开事实一致、边界无抬升，它就是需要保留的有效商业证据。

## 3. Public-safe Input Boundary（公开安全输入边界）

只允许使用：

- `https://redcrag.cn/`；
- `https://redcrag.cn/llms.txt`；
- `https://redcrag.cn/commercial-evaluation/`；
- `https://redcrag.cn/TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.json`；
- `https://redcrag.cn/TITMAS-FIRST-RUN-v0.1.md`；
- 公开 synthetic fixture；
- 公开 DBOS wheel。

禁止输入：

- API key、环境变量值或私有路径内容；
- 未公开客户数据；
- 内部 Agent 输出历史；
- 未发布 DBOS/SAEE capability；
- 隐藏的正确答案或人工修复后的模型输出。

## 4. Validation Roles（验证角色）

| Role | Question |
|---|---|
| `AGENT_RECOMMENDER` | 面对潜在采用方需求，是否会推荐当前包，为什么？ |
| `AGENT_DEVELOPER` | 公开 First Run 是否足以被实现和复用？ |
| `PROCUREMENT_BOUNDARY_AUDITOR` | 是否错误暗示产品、SLA、认证、客户或生产能力？ |
| `INTEGRATION_REUSE_REVIEWER` | 能否在不依赖隐藏状态的前提下形成下一步集成判断？ |

模型输出是 advisory evidence（建议性证据），不是 Human Decision、Truth、认证或采用。

## 5. Deterministic First Run（确定性首次运行）

独立技术执行必须：

1. 从公开 URL 下载 synthetic fixture；
2. 从公开 GitHub Release 安装固定 DBOS wheel；
3. 在全新 Python virtual environment 中执行 `dbos-validate`；
4. 保存 command、exit code、stdout、wheel URL、fixture digest 和环境版本；
5. 明确 `PASS` 只表示本地结构和治理约束通过。

禁止启动 Agent Runtime、执行真实任务、创建 Entity、Capability、Permission 或 Evidence Truth。

## 6. Machine Review Contract（机器审查契约）

每个会话必须返回直接 JSON，并通过
[`agent-review-response.schema.v0.1.json`](commercial-evaluation-agent-first-run/agent-review-response.schema.v0.1.json)。

要求：

- exact provider 和 model identity；
- `retry=0`、`fallback=0`、`substitution=0`；
- 不从自由文本抽取或修复 JSON；
- 记录角色、request id、结果和边界；
- 请求失败或 Schema 失败时保持失败关闭。

## 7. Gate Criteria（闸门标准）

### 7.1 Technical gate

- public endpoints 可访问；
- clean environment install 成功；
- synthetic fixture 得到 expected `PASS`；
- fixture 和 wheel 可追溯；
- 没有 Runtime、Agent、Permission 或真实执行。

### 7.2 Agent gate

- 4 个预分配角色全部执行；
- 至少 3 个结果直接 JSON 且 Schema valid；
- 至少 2 个 provider identity；
- 0 个 critical boundary elevation；
- 所有有效结果都拒绝把当前包表述为 production offering 或 certification；
- 推荐或拒绝均提供可操作原因。

### 7.3 Result states

```text
PASS_EVALUATION_ENTRY_AGENT_RECOMMENDABLE
CONDITIONAL_REMEDIATION_REQUIRED
FAIL_CLOSED
```

即使得到 `PASS_EVALUATION_ENTRY_AGENT_RECOMMENDABLE`，以下仍保持 false：

```text
AVAILABLE_COMMERCIAL_OFFERING=false
PRODUCTION_READY=false
CUSTOMER_ADOPTION_VERIFIED=false
CERTIFICATION_AVAILABLE=false
```

## 8. Stop Conditions（停止条件）

任一情况发生即停止，不静默换模型或补写结果：

- secret 或私有内容可能进入请求；
- provider/model identity 不匹配；
- 输出需要 JSON repair；
- 模型把 Evidence、Validation 或 PASS 抬升为 Truth、Permission、Authority、Certification；
- clean First Run 依赖未公开本地状态；
- wheel 或 fixture digest 无法追溯。

## 9. Authority Boundary（权力边界）

```text
AGENT_REVIEW_NE_HUMAN_DECISION=true
VALIDATION_PASS_NE_COMMERCIAL_OFFERING=true
EVALUATION_RECOMMENDATION_NE_CUSTOMER_ADOPTION=true
STRUCTURAL_PASS_NE_TRUTH=true
SPECIFICATION_NE_RUNTIME=true
```

本协议不创建社区、产品、价格、SLA、合同、客户、Agent、Runtime、Permission 或认证。
