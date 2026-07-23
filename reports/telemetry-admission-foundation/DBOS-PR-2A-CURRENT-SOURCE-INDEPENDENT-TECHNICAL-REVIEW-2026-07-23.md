# DBOS PR-2A Current-source Independent Technical Review

```text
decision_reference=DQ-018
review_gate=PR-G2A
exact_source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
agent_review=CONDITIONALLY_RECOMMENDED_PENDING_NATIVE_X86_64
pr_g2a_ready_for_human_review=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

从远端分支重新 clone 并 checkout 精确 implementation commit 后，current source 的全仓
回归、OpenTelemetry 离线授权子集、fail-closed rollback、静态检查、hash-locked runtime、
可重复 wheel 和隔离安装均通过。相对最后一个独立审查源码 `3a63161…`，
`dbos/telemetry_admission` production package 与 schemas 没有变化；增量只包含平台锁、
测量契约／测量工具、对应测试和历史回执。

本轮结论是 Agent Recommendation（智能体建议）。它不等于 human security review、
PR-G2A Human Approval、merge、release、deployment 或 production authorization。

## Delta Findings（增量发现）

| ID | severity | finding | current disposition |
|---|---:|---|---|
| `CSR-01` | Medium | 并发 process-global `tracemalloc` 在 QEMU amd64 的 TA-P003 中形成 observer effect，并产生 426 个已保留 storage errors | contract `0.1.1` 只在 TA-P003 禁用 Python allocation tracing，保留 process max RSS，明确输出 null，并增加“不启动 tracing”的负向断言；模拟重基线已关闭，原生 x86_64 仍需复验 |
| `CSR-02` | Medium | 运行依赖闭包此前只有 macOS arm64 表达 | 已新增分别绑定 immutable image 的 Linux arm64 与 Linux x86_64 hash locks，且 `cross_platform_claim=false`；Linux x86_64 lock 尚未在原生平台直接安装 |
| `CSR-03` | High | current source 可能继承 predecessor packet 的 stale `READY` 声明 | 新 packet fail closed 为 `WAITING_NATIVE_LINUX_X86_64`；所有 approval、full PR-G2、release、deployment 和 production flags 保持 false |

## Direct Results（直接结果）

| surface | result | boundary |
|---|---|---|
| clean remote clone | exact commit/tree/manifest `PASS` | source commit `23c8f08…` |
| full tests | `534/534 PASS` across 16 directories | synthetic/offline |
| focused telemetry tests | `200/200 PASS` | no deployment cases |
| validators | `35/35 PASS`; telemetry `25/25` | live effects `0` |
| OpenTelemetry conformance | Semantic `32/32`, Schema/Resource `36/36 PASS` | 23 DQ-020 deployment cases remain `BLOCKED` |
| exact load rebase | TA-P001—TA-P005 integrity/source binding `PASS` | emulated amd64, not native or SLO |
| rollback | `PASS`; 25/25 receipts; mismatch `0` | no automatic caller switch; human gate retained |
| Ruff | 34-file target, 0 findings, formatting `PASS` | automated lint only |
| Bandit 1.9.4 | 5,374 LOC, 0 findings, nosec `0` | not human security review |
| pip-audit 2.10.1 | 7 locked dependencies, 0 known vulnerabilities | point-in-time database result |
| wheel | two fixed-epoch builds byte-identical, `sha256:03190078…155af9` | no publication/release |
| isolated install | `pip check` and package-data smoke `PASS` | macOS arm64 only |

Raw inventory：
[`raw/review-current-43382e4274c1/review-evidence-inventory.json`](raw/review-current-43382e4274c1/review-evidence-inventory.json)
（`sha256:e7ceb5aced0890b8243a442c02cb63dab2e5ce0ad7aca6e42a03b1e712fcfdf5`）。

## Agent Recommendation（智能体建议）

```text
verdict=CONDITIONALLY_RECOMMENDED
recommended_as=CURRENT_SOURCE_OFFLINE_TELEMETRY_ADMISSION_REFERENCE_SLICE_PENDING_NATIVE_X86_64
not_recommended_as=PR_G2A_HUMAN_REVIEW_READY_FULL_PR_G2_PRODUCTION_SERVICE_SLO_OR_DURABILITY_EVIDENCE
```

如果潜在 Agent 开发者需要离线、可追溯、OpenTelemetry-aligned 的准入参考切片，我会条件推荐；
如果其需求包含 native x86_64 capacity、production persistence、Collector deployment、SLO、HA
或自动治理，我不会推荐当前切片作为满足这些需求的产品。

## Remaining Gates（剩余闸门）

1. 在 native Linux x86_64 上安装对应 exact-hash lock，并直接重跑当前源码验证；
2. 形成当前 packet 的远端 attestation，再进入独立 human security review；
3. 只有明确 PR-G2A Human Approval 才能关闭 PR-G2A；
4. `PR-G2B`、`PR-G2T`、`PR-G2I`、`PR-G2C` 仍分别阻塞完整 PR-G2；
5. `DQ-019`、`DQ-020`、`DQ-021` 继续保持 `BLOCKED_INPUT`。
