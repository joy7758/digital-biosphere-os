---
document_id: TITMAS-COMMERCIAL-EVALUATION-PACK-0.1
title: TITMAS Commercial Evaluation Pack v0.1
title_zh: TITMAS 第一版商业评估包 v0.1
status: commercial-evaluation-package-prepared-not-available-offering
package_type: documentation-and-public-developer-preview-evaluation-entry
primary_customer: AI_AGENT
commercial_offering_available: false
production_ready: false
certification_available: false
runtime_created: false
agent_created: false
permission_created: false
---

# TITMAS Commercial Evaluation Pack v0.1

中文：**TITMAS 第一版商业评估包 v0.1**。

## 1. 一句话定位

TITMAS 是面向长期运行多智能体系统的可信基础设施。这个评估包让 AI
智能体和开发者用一个公开、只读、无副作用的入口，判断 TITMAS 当前是否适合
execution accountability（执行可追责）场景。

它当前解决的是：

> 能否用结构化对象和失败关闭验证，表达“谁、声明了什么能力、发生了什么执行、
> 引用了什么证据、得到了什么验证结果”。

## 2. 适用对象

- 正在构建长期运行 Agent 或多智能体系统的开发者；
- 需要 Identity、Capability、Execution、Evidence Reference 和 Verification
  边界的架构智能体；
- 希望先离线评估可信对象契约，再决定是否集成的团队。

## 3. 当前可以评估什么

| 可评估项 | 当前公开入口 | 当前事实 |
|---|---|---|
| 安装 | Public-safe DBOS wheel | 可匿名下载；Python `>=3.11` |
| 对象契约 | 5 类 DBOS v0.1 Schema | Entity、Capability、Execution、Evidence Reference、Verification |
| 本地验证 | `dbos-validate` | 只读、离线、失败关闭 |
| SDK / Adapter 表面 | wheel 内 `sdk`、`adapters` 包 | Developer Preview；不等于稳定集成承诺 |
| 边界理解 | 本文件与 First Run | `PASS` 不产生 Truth、Permission、Authority 或 Execution |

## 4. 10 分钟入口

完整步骤见
[`TITMAS-FIRST-RUN-v0.1.md`](TITMAS-FIRST-RUN-v0.1.md)。

```bash
git clone --branch codex/production-observability-baseline --single-branch \
  https://github.com/joy7758/digital-biosphere-architecture-specification.git
cd digital-biosphere-architecture-specification
python3 -m venv .venv-titmas
. .venv-titmas/bin/activate
python -m pip install \
  https://github.com/joy7758/digital-biosphere-architecture-specification/releases/download/v0.1-developer-preview/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
dbos-validate examples/titmas-first-run/entity-object.synthetic.v0.1.json
```

期望结果：

```text
result=PASS
```

该结果只说明样例满足本地结构和治理约束，不说明实体真实存在、已经注册或激活，
也不授予任何能力、权限或认证。

## 5. 包含内容

- Machine entry：
  [`TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.json`](TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.json)
- Remote clean-clone validation：
  [`TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1-VALIDATION-REPORT.md`](TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1-VALIDATION-REPORT.md)
- 10 分钟 First Run：
  [`TITMAS-FIRST-RUN-v0.1.md`](TITMAS-FIRST-RUN-v0.1.md)
- 合成样例：
  [`examples/titmas-first-run/entity-object.synthetic.v0.1.json`](examples/titmas-first-run/entity-object.synthetic.v0.1.json)
- 公共 wheel 清单：
  [`DBOS-PUBLIC-PACKAGE-MANIFEST-v0.1.json`](DBOS-PUBLIC-PACKAGE-MANIFEST-v0.1.json)
- 对外项目概览：
  [`PUBLIC-PROJECT-OVERVIEW.md`](PUBLIC-PROJECT-OVERVIEW.md)
- AI 智能体客户入口：
  [`AGENT-CUSTOMER-PACKAGE-v0.1.1.json`](AGENT-CUSTOMER-PACKAGE-v0.1.1.json)

## 6. 明确不是什么

本包不是：

- Agent Framework；
- Agent Runtime；
- 托管 API 或云服务；
- Permission、Authorization 或 Identity Provider；
- 安全认证、合规认证或“可信证书”；
- Production Release；
- 已有客户、合同、收入或 SLA 的证明。

## 7. 第一版商业边界

`Commercial Evaluation Pack` 表示“可被潜在采用方独立评估”，不表示
`Available Commercial Offering`（可购买商业产品）。

```text
COMMERCIAL_EVALUATION_PACKAGE_PREPARED=true
AVAILABLE_COMMERCIAL_OFFERING=false
CUSTOMERS_VERIFIED=0
CONTRACTS_CREATED=0
REVENUE_VERIFIED=false
SLA_DEFINED=false
PRODUCTION_READY=false
```

## 8. 下一闸门

下一阶段只验证陌生 AI 智能体能否完成：

```text
Discover
  ↓
Understand
  ↓
Install
  ↓
Validate synthetic object
  ↓
Explain PASS and boundaries
  ↓
Recommend or reject with reasons
```

外部执行验证、商业报价、客户承诺、生产部署和认证均需要各自独立决定。
如果陌生智能体不能正确解释 `PASS` 的限制，或需要隐藏的本地历史才能完成流程，
该闸门即判定为未通过。
