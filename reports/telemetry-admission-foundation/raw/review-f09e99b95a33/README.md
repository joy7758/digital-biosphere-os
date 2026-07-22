# DBOS PR-2A Direct Review Receipts

```text
implementation_manifest=sha256:f09e99b95a3332d40abc933eaee35ea8a646b11d330ffaa5213ee0bb28f339b4
source_state=UNCOMMITTED_LOCAL_WORKTREE
authorized_subset_result=PASS
full_catalog_result=BLOCKED
pr_g2_ready_for_review=false
production_ready=false
```

本目录把 DBOS PR-2A 的摘要结论拆回可独立读取的原始本地回执，供智能体和人工审查。
它们不是 canonical DBOS Evidence，也不授权 commit、push、deployment 或 DQ-020。

| artifact | purpose | result |
|---|---|---|
| [`all-tests.json`](all-tests.json) | 16 个 test directories 的全仓回归 | `523/523 PASS` |
| [`focused-telemetry-tests.json`](focused-telemetry-tests.json) | 遥测专项回归 | `189/189 PASS` |
| [`validator-aggregate.json`](validator-aggregate.json) | 所有 DBOS validators | `35/35 PASS` |
| [`telemetry-validator.json`](telemetry-validator.json) | DQ-018 结构、边界和供应链检查 | `25/25 PASS` |
| [`otel-conformance.json`](otel-conformance.json) | DQ-018 OpenTelemetry bindings | `32/32 + 36/36 PASS`; 23 blocked |
| [`bandit.json`](bandit.json) | 目标切片静态安全扫描 | 5,263 LOC / 0 findings |
| [`pip-audit.json`](pip-audit.json) | 精确锁定的运行依赖漏洞检查 | 7 dependencies / 0 known vulnerabilities |
| [`static-quality-receipt.json`](static-quality-receipt.json) | targeted Ruff/format 与全仓历史债务分离 | slice pass / repository debt 39 |
| [`whole-repository-ruff.json`](whole-repository-ruff.json) | 未隐藏的全仓 Ruff 结果 | 39 findings / 9 pre-existing files |
| [`coverage-summary.json`](coverage-summary.json) | 无事前阈值的覆盖率表征 | 82.45%; not a gate |
| [`rollback-drill.json`](rollback-drill.json) | failed source 保留与不同路径恢复 | `PASS`; human switch required |
| [`supply-chain-receipt.json`](supply-chain-receipt.json) | locks、双构建、隔离安装 | local pass; not independent attestation |
| [`wheel-build-input-manifest.json`](wheel-build-input-manifest.json) | 完整 wheel 的声明输入，而非只看 DQ-018 | 61 files / three manifests equal |
| [`wheel-content-manifest.json`](wheel-content-manifest.json) | 两个 wheel 的 entry-level 内容清单 | 64 entries / byte identical |
| [`review-evidence-inventory.json`](review-evidence-inventory.json) | 上述回执、负载结果、报告、SBOM 和 locks 的统一摘要 | 25 entries |

## Reading Order（智能体读取顺序）

1. [`../../DBOS-PR-2A-PR-G2-REVIEW-PACKET-2026-07-22.json`](../../DBOS-PR-2A-PR-G2-REVIEW-PACKET-2026-07-22.json)；
2. [`review-evidence-inventory.json`](review-evidence-inventory.json)；
3. 与问题相关的直接回执；
4. [`../current-f09e99b95a33/`](../current-f09e99b95a33/) 的五个负载结果。

审查者不得从任一 `PASS` 推导 Permission、Evidence Truth、PR-G2 approval 或
Production Ready。当前唯一 PR-G2 acceptance blocker 是 exact DBOS source commit 尚未获
授权和形成；后续 production persistence、安全、Collector 与 deployment 仍属于其他 gate。
