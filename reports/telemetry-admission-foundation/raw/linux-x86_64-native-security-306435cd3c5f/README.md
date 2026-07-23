# Native Linux x86_64 Security-remediation Validation Artifacts

```text
decision_reference=DQ-018
review_gate=PR-G2A
exact_source_commit=ee90c0c84964f1f3e4dbeb8dffaf888f9822b6a5
exact_source_tree=a8f2768b707c467607d4939d3e797327af4e9d31
implementation_manifest=sha256:306435cd3c5fc65e46995f0e2a57b1322f950889af350f1b0bcbd13c35644fd9
execution_mode=NATIVE_LINUX_X86_64_IMMUTABLE_CONTAINER_NETWORK_NONE
result=PASS_REMEDIATION_VALIDATION_PENDING_INDEPENDENT_ATTESTATION
human_security_review_complete=false
pr_g2a_human_review_approved=false
production_ready=false
```

## Outcome（结果）

本目录绑定 DBOS commit `ee90c0c…` 的 58-file exact-source manifest。它记录
HSR-PRE-001 与 HSR-PRE-002 修复后的原生 Linux x86_64 直接验证：

- full tests `538/538`，Telemetry Admission tests `204/204`；
- Telemetry validator `25/25`；
- OpenTelemetry 授权子集 `32/32 + 36/36 PASS`，23 个部署用例仍为
  `BLOCKED_NOT_AUTHORIZED`；
- TA-P001—TA-P005 integrity/source binding 全部 `PASS`；
- TA-P003 为 19,199 operations / 0 errors；
- TA-P005 为 3,600.025 秒 / 16,797 operations / 59 次周期完整性检查 / 0 errors；
- rollback、可重复 wheel、隔离安装与 `pip check` 均为 `PASS`；
- Ruff 0、Bandit 5,422 LOC / 0 findings / 0 `nosec`、7 个锁定运行依赖已知漏洞 0。

HSR-PRE-001 与 HSR-PRE-002 已由直接代码修复和原生负向测试关闭，但仍等待独立远端
attestation。HSR-PRE-003 与 HSR-PRE-004 保持开放的 Medium scoped residual（中等范围残余）。

## Reading Order（读取顺序）

1. [`native-validation-summary.json`](native-validation-summary.json)：环境、源码和结果总表；
2. [`security-remediation-summary.json`](security-remediation-summary.json)：两项 High finding
   的修复与两项 Medium residual；
3. [`source-manifest.json`](source-manifest.json)、[`environment.json`](environment.json)：精确
   字节和原生执行环境；
4. [`all-tests.json`](all-tests.json)、[`focused-telemetry-tests.txt`](focused-telemetry-tests.txt)、
   [`telemetry-admission-validator.txt`](telemetry-admission-validator.txt)：测试与 validator；
5. [`validator-summary.json`](validator-summary.json)：脱敏后的 `30 PASS + 5 expected
   fail-closed + 0 unexpected`；详细绝对路径输出不进入 Git；
6. [`otel-conformance.json`](otel-conformance.json)：OpenTelemetry 授权子集和继续阻塞的部署用例；
7. `TA-P001.json`—`TA-P005.json` 及对应 `.receipt.json`：不可覆盖负载结果；
8. [`rollback-drill.json`](rollback-drill.json)、[`attempt-history.json`](attempt-history.json)：
   rollback 结果与首次错误编排历史；
9. [`wheel-hashes.txt`](wheel-hashes.txt)、[`wheel-install-smoke.json`](wheel-install-smoke.json)：
   可重复构建和隔离安装；
10. [`ruff.json`](ruff.json)、[`bandit.json`](bandit.json)、[`pip-audit.json`](pip-audit.json)：
    自动化静态与依赖安全检查。

## Failure and Privacy Boundary（失败与隐私边界）

首次 rollback 调用错误地预先创建了工具要求必须不存在的工作目录，因
`FileExistsError` 在 product workload 前失败。失败通过
[`attempt-1-rollback-orchestration.json`](attempt-1-rollback-orchestration.json) 和
[`attempt-history.json`](attempt-history.json) 保留；第二次使用新路径后通过，没有覆盖
失败事实。

隔离 validator 的五个预期 fail-closed 输出含开发机绝对路径。原始详细输出仅保留在隔离
服务器，不进入公开审查包；本目录只记录 validator 名称、分类和计数。

## Authority Boundary（权力边界）

```text
AUTOMATED_REMEDIATION_VALIDATION_NE_HUMAN_SECURITY_REVIEW=true
NATIVE_VALIDATION_NE_PR_G2A_APPROVAL=true
DIGEST_IS_SIGNATURE=false
LISTENER_AUTHORIZED=false
COLLECTOR_CREATED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
ENTITY_CREATED=false
PERMISSION_GRANTED=false
CANONICAL_EVIDENCE_CREATED=false
SAEE_CALLED=false
PRODUCTION_READY=false
```
