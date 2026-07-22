# DBOS PR-2A Current-source Load Rebase Receipt

```text
decision_reference=DQ-018
review_gate=PR-G2A
implementation_source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_tree=27703ed64d6e885a2933a5a39139a59bab83c3c1
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
measurement_contract_revision=0.1.1
measurement_contract_digest=sha256:80f37f4ec370b84f71da2615f43d170ecbb76f2fc296df93078be18941bf9fe6
result=PASS_EMULATED_AMD64_CURRENT_SOURCE_LOAD_REBASE
current_source_full_ta_p001_to_ta_p005_rebase_complete=true
native_linux_x86_64_validated=false
pr_g2a_ready_for_human_review=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

current source `23c8f08…` 的 `TA-P001`—`TA-P005` 已在同一固定 `linux/amd64`
镜像、同一 measurement contract `0.1.1` 和同一 implementation manifest 上完成完整
重基线。五项 integrity 和 source binding 均为 `PASS`，全部 authority effects 为 false。

这只关闭“当前 exact source 的五项模拟负载尚未重跑”缺口。执行仍是 ARM64 host 上的
amd64 emulation（模拟），不是原生 Linux x86_64、容量 SLO、production persistence、
PR-G2A Human Approval、完整 PR-G2 或 Production Ready 证明。

## Agent Recommendation Gate（智能体推荐闸门）

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=CURRENT_EXACT_SOURCE_OFFLINE_OBSERVER_EFFECT_HARDENED_EMULATED_AMD64_LOAD_CHARACTERIZATION
NOT_RECOMMENDED_AS=NATIVE_X86_64_CAPACITY_SLO_PRODUCTION_DURABILITY_OR_PRODUCTION_READINESS_EVIDENCE
```

如果潜在用户需要审查 SQLite reference backend 在固定模拟环境中的负载、幂等、并发、
恢复和一小时完整性行为，我会推荐本材料。如果需要原生 x86_64、生产后端、SLO 或生产可用性，
我不会推荐当前结果。

## Immutable Bindings（不可变绑定）

| binding | value |
|---|---|
| source commit / tree | `23c8f0878058f29e733b6f164572ac157c6c7d1c` / `27703ed64d6e885a2933a5a39139a59bab83c3c1` |
| implementation manifest | 58 files / 726,068 bytes / `sha256:43382e42…bc8c` |
| measurement contract | revision `0.1.1` / 2,054 bytes / `sha256:80f37f4e…9fe6` |
| base image | `python:3.12.13-slim-bookworm@sha256:72d3d75f…488d` |
| execution mode | `EMULATED_LINUX_AMD64_ON_ARM64_HOST` |
| container limits | 4 CPUs / 2 GiB memory / 1 GiB work tmpfs / network none |

每项 source manifest 在运行首尾一致。原始结果在容器内以 `0600`、拒绝覆盖方式生成；
导出后的 SHA-256 和字节数与 receipt 一致。该报告是 implementation commit 的 successor
receipt，不属于被测 manifest，避免循环自证。

## Load Characterization（负载表征）

| case | fixed parameters | observed result | interpretation |
|---|---|---|---|
| `TA-P001` | 10,000 unique / 1 worker | 10,000 ops；301.217s；p95 35.770ms；integrity/source `PASS` | serial reference observation |
| `TA-P002` | 1,000 originals / 10,000 retries | duplicate accuracy 1.0；lifecycle growth 0；integrity/source `PASS` | idempotency reference `PASS` |
| `TA-P003` | 32 workers / 300s / target 64 ops/s | 18,953 ops；63.076 ops/s；errors `{}`；p95 276.034ms；integrity/source `PASS` | observer-effect hardened emulated concurrency |
| `TA-P004` | 1,000 writes / 10 backups | 10/10 restore；writer errors `[]`；integrity/source `PASS` | restore reference `PASS` |
| `TA-P005` | 3,600s / target 5 ops/s / 60s checks | 13,532 ops；59/59 periodic + final `PASS`；errors `{}`；p95 70.085ms | one-hour integrity reference, not SLO |

`TA-P005` wall time 为 3,600.194s，数据库末值 84,762,624 bytes，Linux `ru_maxrss`
为 100,780 KiB，tracemalloc peak 为 5,031,829 bytes。原始结果没有
`observed_operations_per_second` 字段；`13,532 / 3,600.194 = 3.758686 ops/s` 仅作为显式
标注的派生描述值，不伪装成原始观测字段，也不证明无内存泄漏。

## Raw Receipt Routing（原始回执路由）

- P001/P002/P004/P005：
  [`raw/current-source-rebase-43382e4274c1/`](raw/current-source-rebase-43382e4274c1/)；
- P003：
  [`raw/p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json`](raw/p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json)；
- P003 root-cause 和 predecessor failure retention：
  [`DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json`](DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json)。

这些文件是 review artifacts，不是 canonical Evidence，不产生 Verification、Permission、
Authority 或 Truth。

## Security Boundary（安全边界）

- fixed image digest 和 exact-hash x86_64 wheelhouse；
- read-only root filesystem 和 read-only source；
- 4 CPU、2 GiB memory、1 GiB tmpfs；
- `network=none`，没有 published port；
- 没有 listener、Collector、DBOS Runtime、Agent、Entity、Permission 或生产后端；
- 没有调用 SAEE，也没有生成 Fitness、Risk 或 Evolution Recommendation。

## Failure Retention（失败保留）

1. predecessor `TA-P003` 的 426 个 `TA_STORAGE_UNAVAILABLE` 保留，不删除；
2. 本机规范 SSH alias `hongyan-4cj` 连接原生 x86_64 候选机时，服务端在 key exchange
   前关闭连接；未认证、未进入主机、未产生远程写入；
3. `TA-P005` 缺少原始 observed-rate 字段，报告保留缺失并仅提供显式派生值。

## Authority and Review Boundary（权力与审查边界）

```text
PR_G2A_CURRENT_SOURCE_TA_P001_TO_TA_P005_REBASE_COMPLETE=true
PR_G2A_CURRENT_SOURCE_REVIEW_PACKET_REFRESH_REQUIRED=true
PR_G2A_READY_FOR_HUMAN_REVIEW=false
PR_G2A_HUMAN_REVIEW_APPROVED=false
FULL_PR_G2_READY=false
PRODUCTION_READY=false
DQ_019=BLOCKED_INPUT
DQ_020=BLOCKED_INPUT
DQ_021=BLOCKED_INPUT
```

当前仍缺 native Linux x86_64 直接证据及新的 current-source independent review packet。
本回执不选择任何 Human Decision token，不创建 PR，不修改 `main`，不授权 merge、release、
deployment、production persistence、Collector 或 Telemetry-to-Evidence admission。

机器可读回执见
[`DBOS-PR-2A-CURRENT-SOURCE-LOAD-REBASE-2026-07-23.json`](DBOS-PR-2A-CURRENT-SOURCE-LOAD-REBASE-2026-07-23.json)。
