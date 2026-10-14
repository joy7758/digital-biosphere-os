---
document_id: TITMAS-COMMERCIAL-EVALUATION-PACK-0.2
title: TITMAS Commercial Evaluation Pack v0.2
title_zh: TITMAS 商业评估包 v0.2
status: agent-first-run-validated-not-available-offering
observed_at: 2026-07-27
supersedes: TITMAS-COMMERCIAL-EVALUATION-PACK-v0.1.md
commercial_offering_available: false
production_ready: false
certification_available: false
---

# TITMAS Commercial Evaluation Pack v0.2

中文：**TITMAS 商业评估包 v0.2**。

## 1. What changed（变化）

v0.2 保留 v0.1 的公开 wheel、五类对象契约、synthetic fixture 和离线 validator，
新增 External Agent First Run Validation（外部智能体首次运行验证）直接证据。

```text
TECHNICAL_FINAL_RUN=PASS
AGENT_SESSIONS=4/4
SCHEMA_VALID_SESSIONS=4/4
DISTINCT_PROVIDERS=2
EVALUATION_RECOMMENDED=4/4
PRODUCTION_NOT_RECOMMENDED=4/4
CRITICAL_BOUNDARY_FAILURES=0
```

因此，当前包可以被 AI 智能体推荐用于：

> offline, read-only evaluation of execution-accountability object contracts

仍然不能被推荐用于：

> production purchase, deployment, certification, permission or truth claims

## 2. First Run correction contract（首次运行修正规则）

验证发现两类 agent automation 常见错误：

1. wheel 下载后被改名为非规范的 `dbos.whl`；
2. 安装时擅自添加 `--no-deps`。

v0.2 明确：

```text
EXACT_WHEEL_FILENAME_REQUIRED=true
DEPENDENCY_INSTALLATION_REQUIRED=true
```

失败记录见
[`technical-first-run-receipt.v0.1.json`](commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json)。

## 3. Public availability limitation（公开可用性限制）

验证期间观察到 3 次 pre-model public transport failure，随后所有入口恢复 `HTTP 200`。

```text
PUBLIC_ENTRY_CURRENTLY_AVAILABLE=true
TRANSIENT_TRANSPORT_FAILURE_OBSERVED=true
AVAILABILITY_SLA_DEFINED=false
```

该发现不阻止当前离线评估入口通过，但阻止任何持续可用性或 SLA 声明。

## 4. Evidence package（证据包）

- [验证协议](TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-PROTOCOL-v0.1.md)
- [验证报告](TITMAS-EXTERNAL-AGENT-FIRST-RUN-VALIDATION-REPORT-v0.1.md)
- [机器结果](commercial-evaluation-agent-first-run/composite-result.v0.1.json)
- [技术回执](commercial-evaluation-agent-first-run/technical-first-run-receipt.v0.1.json)
- [v0.2 machine entry](TITMAS-COMMERCIAL-EVALUATION-PACK-v0.2.json)
- [v0.2 Schema](architecture/schemas/titmas-commercial-evaluation-pack.schema.v0.2.json)

模型输出是 advisory evidence，不是 Truth、Human Decision、Customer Adoption 或
commercial authority。

## 5. Commercial truth（商业事实）

```text
COMMERCIAL_EVALUATION_PACKAGE_PREPARED=true
EVALUATION_ENTRY_AGENT_RECOMMENDABLE=true
AVAILABLE_COMMERCIAL_OFFERING=false
CUSTOMERS_VERIFIED=0
CONTRACTS_CREATED=0
REVENUE_VERIFIED=false
SLA_DEFINED=false
PRODUCTION_READY=false
CERTIFICATION_AVAILABLE=false
```

## 6. Next gate（下一闸门）

下一阶段建议：

> Public Entry Availability and Agent Automation Hardening

只解决：

- exact wheel filename machine contract；
- dependency installation machine contract；
- 公开入口跨时间窗口只读可用性观测；
- 失败分类和机器可读恢复路径。

不创建 Agent、Runtime、Permission、商业报价、SLA、认证或客户采用声明。
