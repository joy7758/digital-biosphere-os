# DBOS PR-2A Streaming Integrity Hardening Receipt

```text
report_id=DBOS-PR-2A-STREAMING-INTEGRITY-HARDENING-2026-07-22
decision_reference=DQ-018
review_gate=PR-G2A
status=PASS_EXACT_REMOTE_CLEAN_CLONE_NOT_GATE_APPROVAL
source_commit=3a63161d3e04d785b4b04feadd4a0712bf6314fc
implementation_manifest=sha256:b6c03faf50bfab4ce25edaeb39b7ae36d2525df32519f82a8108c164162bd9fc
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

对 predecessor manifest `sha256:fdda745c…baa51` 执行精确一小时 `TA-P005` 时，
`SQLiteTelemetryAdmissionStore.integrity_report()` 会一次性 `fetchall()` 全部
`admission_records`，并再按 lifecycle 保留第二份 Python 容器。完整性语义保持正确，
但周期扫描内存会随数据库记录量增长，不适合作为长期运行参考实现。

`3a63161d3e04d785b4b04feadd4a0712bf6314fc` 将该路径改为 cursor streaming（游标逐行扫描），
同时逐行验证 record digest、sequence 和 previous-record continuity；foreign-key 检查改为
`fetchone()`，错误集合去重。修复没有放宽完整性条件，也没有改变 admission 状态机或 authority。

## Exact Bindings（精确绑定）

| surface | binding |
|---|---|
| predecessor source / receipt | `5c52c1c2…` / `aa6440e8…` |
| predecessor manifest | 56 files / 714,335 bytes / `sha256:fdda745c…baa51` |
| predecessor one-hour artifact | `sha256:ecf553dd…5dc1`, 48,829 bytes |
| hardened remote source | `origin/codex/telemetry-admission-foundation@3a63161d3e04d785b4b04feadd4a0712bf6314fc` |
| hardened manifest | 56 files / 716,453 bytes / `sha256:b6c03faf…d9fc` |
| hardened reproducible wheel | two builds / 126,088 bytes / 64 entries / `sha256:03190078…5af9` |
| hardened one-hour artifact | `sha256:048db60c…3499`, 48,828 bytes, mode `0600`, non-overwrite |
| environment | CPython 3.12.13 / SQLite 3.50.4 / macOS 26.5.2 arm64 / 10 CPUs |

Raw results are indexed in [`raw/current-b6c03faf50bf/`](raw/current-b6c03faf50bf/).
The predecessor one-hour artifact is retained in
[`raw/current-fdda745c3907/`](raw/current-fdda745c3907/) and is not overwritten.

## Validation（验证）

| check | result | boundary |
|---|---|---|
| remote clean-clone commit | local `HEAD` = remote branch = `3a63161…` | exact source before workloads |
| all DBOS tests | `532/532 PASS` in 16 directories | includes `198/198` telemetry tests |
| regression | rejects `fetchall()` on the admission-record cursor | old implementation would fail |
| validators | `35/35 PASS`; telemetry validator `25/25` | historical identity warning retained |
| Ruff 0.14.10 | 0 findings; changed files formatted | exact command scope recorded |
| Bandit 1.9.4 | 0 findings across 5,357 LOC; 0 `nosec` | automated scan, not human review |
| pip-audit 2.10.1 | 0 known vulnerabilities in 7 hash-locked runtime packages | one OS/arch lock only |
| reproducible wheel | two fixed-epoch builds byte-identical; clean install/import/package data `PASS` | not published or released |
| TA-P001–TA-P005 | all integrity and source binding `PASS` | characterization, not SLO |
| TA-P005 checks | 59 periodic checks + final check all `PASS` | 3,600.153086 seconds |
| authority effects | all 13 fields `false` in every result | no gate or governed state change |

## One-hour Comparison（同环境一小时比较）

| metric | predecessor `fdda745c…` | hardened `b6c03faf…` | observation |
|---|---:|---:|---|
| operations | 17,096 | 17,197 | comparable fixed-rate workload |
| database bytes | 107,118,592 | 107,786,240 | comparable final scale |
| p95 latency | 19.117333 ms | 18.489359 ms | measurement, not SLO |
| process max RSS | 192,724,992 | 38,223,872 | 80.166624% lower |
| Python tracemalloc peak | 81,218,785 | 6,676,129 | 91.780068% lower |
| final integrity | `PASS` | `PASS` | no validation weakening |
| errors | `{}` | `{}` | exact artifacts retained |

A separate read-only scan of the predecessor 107,118,592-byte database using the hardened code also
returned `PASS` in 4.679744 seconds with 36,069 bytes Python peak allocation and 30,162,944 native RSS
units. This isolates the integrity-scan improvement, but remains a single-platform observation.

## Agent Recommendation Gate（智能体推荐闸门）

```text
agent_recommendation=RECOMMENDED_FOR_PR_G2A_HUMAN_REVIEW
recommended_as=BOUNDED_OFFLINE_SQLITE_TELEMETRY_ADMISSION_REFERENCE_SLICE
not_recommended_as=PRODUCTION_PERSISTENCE_OR_TELEMETRY_SERVICE
corrected_issue=INTEGRITY_SCAN_MEMORY_SCALED_WITH_RECORD_COUNT
remaining_gaps=HUMAN_SECURITY_REVIEW,CROSS_PLATFORM_VALIDATION,PR_G2B,PR_G2T,PR_G2I,PR_G2C
```

如果潜在使用者需要一个可审查、失败关闭、无 listener 的 Telemetry Admission reference slice，
当前精确源码可以推荐进入人工 `PR-G2A` 审查。如果需求是生产持久化、Collector/OTLP 服务或
完整 Trusted Multi-Agent Infrastructure，则不推荐当前切片作为成品。

## Non-claims（非声明）

本回执不批准 `PR-G2A`，不关闭完整 `PR-G2`，不选择 DQ-019 backend，不创建 listener、
Collector、production database、Agent、Runtime、Entity、Capability、Permission、Execution、
canonical Evidence、Verification 或 SAEE output。`Telemetry != Evidence`，`Evidence != Truth`，
`PRODUCTION_READY=false`。
