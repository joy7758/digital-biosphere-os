# DBOS PR-2A TA-P003 Observer-effect Hardening Receipt

```text
decision_reference=DQ-018
review_gate=PR-G2A
implementation_source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_tree=27703ed64d6e885a2933a5a39139a59bab83c3c1
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
measurement_contract_revision=0.1.1
measurement_contract_digest=sha256:80f37f4ec370b84f71da2615f43d170ecbb76f2fc296df93078be18941bf9fe6
p003_hardening_result=PASS_EMULATED_AMD64
current_source_full_ta_p001_to_ta_p005_rebase_complete=false
native_linux_x86_64_validated=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

`TA-P003` 的 426 个 `TA_STORAGE_UNAVAILABLE` 已被定位为 concurrent global
`tracemalloc`（并发全局 Python 分配跟踪）在 QEMU amd64 下造成的 observer effect（观察者
效应）。直接 A/B 诊断表明：相同固定镜像、tmpfs、32 workers 和 30 秒窗口中，关闭
`tracemalloc` 为 1,853/1,853 成功、0 错误；开启后只有 734 次成功并出现 38 个
`database is locked`，异常精确发生在 `BEGIN IMMEDIATE`。

修复没有扩大 SQLite busy timeout、重试失败写入或隐藏错误。它只把并发吞吐表征中的全局
Python allocation tracing 关闭，同时保留 `resource.getrusage(RUSAGE_SELF).ru_maxrss`。
结果中显式写入 `python_allocation_tracing=false`、`python_tracemalloc_peak_bytes=null` 和
observer-effect control，避免把缺失指标伪装为 0。

修正后的完整 300 秒、32-worker、target 64 ops/s 同介质 tmpfs 重跑完成 18,953 次成功、
0 错误、63.076 ops/s，p95 276.034ms；integrity 和 source binding 均为 `PASS`。这关闭的是
模拟环境中已知的测量工具扰动，不是 native Linux x86_64、容量 SLO 或生产持久性证明。

## Measurement Contract Evolution（测量契约演化）

| field | predecessor | successor |
|---|---|---|
| contract revision | `0.1` | `0.1.1` |
| contract digest | `sha256:b817493b…4e91` | `sha256:80f37f4e…9fe6` |
| concurrent allocation tracing | implicit enabled | explicit disabled |
| disabled metric representation | not declared | JSON `null` |
| process max RSS | retained | retained |
| result semantics | `CHARACTERIZATION_NOT_SLO` | unchanged |

该变更是 measurement correction（测量修正），不是 storage behavior、Capability、Permission、
Authority、Evidence 或 production gate 变更。

## Controlled Comparison（受控比较）

| run | medium | tracing | operations | errors | ops/s | p95 | integrity/source |
|---|---|---:|---:|---:|---:|---:|---|
| predecessor `d62b411…` full | Linux tmpfs | enabled | 6,699 | 426 | 22.282 | 3,787.476ms | `PASS/PASS` |
| diagnostic A, 30s | Linux tmpfs | disabled | 1,853 | 0 | not SLO | not SLO | integrity `PASS` |
| diagnostic B, 30s | Linux tmpfs | enabled | 734 | 38 | not SLO | not SLO | integrity `PASS` |
| successor `23c8f08…` full | Linux tmpfs | disabled | 18,953 | 0 | 63.076 | 276.034ms | `PASS/PASS` |
| successor corroboration | Linux named volume | disabled | 18,753 | 0 | 62.408 | 381.235ms | `PASS/PASS` |

相对旧 tmpfs 基线，successor tmpfs run 的 observed throughput 增加 183.078%，p95 降低
92.712%，错误从 426 降到 0。这些百分比只描述两个固定模拟执行，不是服务等级承诺。

## Exact Successor Binding（精确后继绑定）

| binding | value |
|---|---|
| source commit / tree | `23c8f0878058f29e733b6f164572ac157c6c7d1c` / `27703ed64d6e885a2933a5a39139a59bab83c3c1` |
| implementation manifest | 58 files / 726,068 bytes / `sha256:43382e42…bc8c` |
| base image | `python:3.12.13-slim-bookworm@sha256:72d3d75f…488d` |
| runtime lock | `sha256:76746fc7…1ddf` |
| tmpfs raw result | 29,092 bytes / `sha256:da031f64…9142` |
| original result mode | `0600`; overwrite disabled |
| exported public-safe copy | [`raw/p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json`](raw/p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json) |
| execution mode | `EMULATED_LINUX_AMD64_ON_ARM64_HOST` |

## Validation and Security（验证与安全）

```text
remote_clean_clone=PASS
full_tests=534/534_PASS
test_directories=16
focused_telemetry_tests=200/200_PASS
hermetic_validators=30_PASS_5_EXPECTED_EXTERNAL_SOURCE_FAIL_CLOSED_0_UNEXPECTED
telemetry_admission_validator=25/25_PASS
ruff=0_FINDINGS_34_FILES_FORMATTED
bandit=4650_LOC_0_FINDINGS_0_NOSEC_0_SKIPPED
pip_audit=7_DEPENDENCIES_0_KNOWN_VULNERABILITIES
pip_check=PASS
```

运行依赖通过 exact x86_64 lock、`--require-hashes`、`--only-binary=:all:` 和离线 wheelhouse
安装。Bandit `1.9.4` 与 pip-audit `2.10.1` 的扫描工具版本被固定，但扫描工具自身的完整
transitive hash lock 尚未形成；这是工具链供应链剩余缺口，不影响运行依赖 hash 结论。

## Agent Recommendation Gate（智能体推荐闸门）

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=OBSERVER_EFFECT_HARDENED_OFFLINE_EMULATED_CONCURRENCY_CHARACTERIZATION
NOT_RECOMMENDED_AS=NATIVE_X86_64_CAPACITY_SLO_OR_PRODUCTION_READINESS_EVIDENCE
```

如果潜在用户需要审查离线 SQLite reference backend 的并发失败行为和测量扰动控制，我会
推荐该后继材料。如果需要原生 Linux x86_64 容量、生产持久性或 SLO，我不会推荐当前结果。

## Failure Retention（失败保留）

1. predecessor 完整 run 的 426 个 `TA_STORAGE_UNAVAILABLE` 不删除；
2. root-cause 容器首次因缺少 `PyYAML` 在负载前停止；
3. 一次 PyPI 下载出现 TLS EOF；随后建立 exact-hash 离线 wheelhouse；
4. 一次诊断调用因工作目录未预创建而由路径安全检查失败关闭；
5. 首个 300 秒修正 run 使用 tmpfs 生成 `sha256:39cc207f…5402` 回执，但容器停止后
   tmpfs 工件不可提取；该回执不作为本报告原始证据；
6. Bandit 首次直接入口执行被拒绝，第二次摘要脚本有 shell quoting 错误；最终通过
   `python -m` 独立重跑并得到 0 findings。

## Current-source Limitation（当前源码限制）

当前 source `23c8f08…` 已通过全量测试、安全检查及 `TA-P003` 两种 Linux 介质的完整重跑，
但 `TA-P001`、`TA-P002`、`TA-P004` 和一小时 `TA-P005` 尚未在这个新 source manifest 上
重新执行。因此不得把 predecessor 的五项全套结果自动迁移到当前源码，也不得宣称当前
source 的 `TA-P001`—`TA-P005` 已全部重基线。

## Authority Boundary（权力边界）

```text
PR_G2A_CURRENT_SOURCE_REVIEW_PACKET_REFRESH_REQUIRED=true
PR_G2A_HUMAN_REVIEW_APPROVED=false
FULL_PR_G2_READY=false
PRODUCTION_READY=false
DQ_019=BLOCKED_INPUT
DQ_020=BLOCKED_INPUT
DQ_021=BLOCKED_INPUT
```

没有创建 Agent、Runtime、Entity、Capability、Permission、Execution、canonical Evidence、
Verification、Collector、listener 或 endpoint，没有调用 SAEE，也没有修改 `main`。

机器可读回执见
[`DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json`](DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json)。
