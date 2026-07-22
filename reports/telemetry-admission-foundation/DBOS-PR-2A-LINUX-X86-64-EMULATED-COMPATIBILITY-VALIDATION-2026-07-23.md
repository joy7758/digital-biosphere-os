# DBOS PR-2A Linux x86_64 Emulated Compatibility Validation

```text
decision_reference=DQ-018
review_gate=PR-G2A
implementation_source_commit=d62b411845b18af3ec79af67622666e96d1baed3
implementation_tree=109b2a9dcad86d1ff882ac472394a140f0dc5169
implementation_manifest=sha256:6d1bcbbfc2cba1add823d390e013d4c755047f1147e338a0a59bf8e4bac0d6e4
execution_mode=EMULATED_LINUX_AMD64_ON_ARM64_HOST
result=PARTIAL_EMULATED_COMPATIBILITY
native_linux_x86_64_validated=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

远端分支 `codex/telemetry-admission-foundation` 的精确提交 `d62b411…` 已在独立 clean
clone 中，使用固定 Linux amd64 镜像和 CPython 3.12 x86_64 哈希锁完成模拟兼容性验证。

功能、失败关闭和自动安全层通过：534/534 全量测试、200/200 Telemetry Admission 测试、
30 validators `PASS` + 5 external-source fail closed、25/25 Telemetry validator、Ruff 0、
Bandit 0、7 个运行依赖已知漏洞 0。

负载层不是全绿。`TA-P003` 在 QEMU 模拟环境的 32-worker 窗口中记录 426 个
`TA_STORAGE_UNAVAILABLE`；尽管数据完整性和源码绑定保持 `PASS`，该结果必须标记为
`PARTIAL`。它可能受模拟开销影响，但在真实 x86_64 原生主机重跑前不得归因结案。

因此本结果只证明 fixed amd64 userspace（固定 amd64 用户态）的有界兼容材料，不证明
Linux x86_64 原生平台、容量、SLO、生产持久性、PR-G2A 批准、完整 PR-G2 或生产就绪。

## Agent Recommendation Gate（智能体推荐闸门）

```text
AGENT_RECOMMENDATION=CONDITIONALLY_RECOMMENDED
RECOMMENDED_AS=OFFLINE_EMULATED_AMD64_COMPATIBILITY_AND_FAILURE_DISCOVERY_MATERIAL
NOT_RECOMMENDED_AS=NATIVE_X86_64_OR_PRODUCTION_READINESS_EVIDENCE
```

如果潜在用户需要离线审查固定 amd64 依赖、功能兼容性和失败行为，我会推荐本材料；如果
用户需要原生 Linux x86_64 性能、容量或生产可用性，我不会推荐当前结果。修正动作已经
包括 exact lock、534 tests、安全扫描、恢复和一小时完整性；剩余停止条件是原生 x86_64
重跑 `TA-P003` 并完成独立 `PR-G2A` 人工审查。

## Immutable Bindings（不可变绑定）

| binding | value |
|---|---|
| source commit | `d62b411845b18af3ec79af67622666e96d1baed3` |
| source tree | `109b2a9dcad86d1ff882ac472394a140f0dc5169` |
| implementation manifest | 58 files / 723,949 bytes / `sha256:6d1bcbbf…d6e4` |
| base image | `python:3.12.13-slim-bookworm@sha256:72d3d75f…488d` |
| runtime lock | `sha256:76746fc7…1ddf` |
| build lock | `sha256:1cea23a9…95c` |
| guest platform | `Linux-6.8.0-100-generic-x86_64-with-glibc2.36` |
| execution mode | `EMULATED_LINUX_AMD64_ON_ARM64_HOST` |
| Python / SQLite | `3.12.13` / `3.40.1` |

本报告是上述实现提交的 successor receipt（后继回执）。报告提交不属于被测 implementation
manifest，避免循环自证。

## Validation Results（验证结果）

| check | result |
|---|---|
| remote clean clone | `PASS`；remote / clone commit 一致，clone clean |
| exact runtime lock | `PASS`；7 个 wheel，`--require-hashes --only-binary=:all:` |
| full tests | `534/534 PASS`，16 个测试目录 |
| focused telemetry tests | `200/200 PASS` |
| hermetic validators | 35 个：30 `PASS`，5 external-source fail closed，0 unexpected |
| telemetry admission validator | `25/25 PASS` |
| Ruff | 0 findings；34 个 DQ-018 范围文件 format `PASS` |
| Bandit | 5,363 LOC，0 findings，0 `nosec`，0 skipped |
| pip-audit | 7 个锁定运行依赖，0 个已知漏洞 |
| pip check | `PASS` |

五个失败关闭 validator 为 `capability_claim_validator`、`capability_validator`、
`evidence_validator`、`federation_validator` 和 `identity_validator`。隔离 clone 不包含其
外部规范来源，所以结果不是 `35/35 PASS`。

## Load Characterization（负载表征）

| case | fixed parameters | observed result | interpretation |
|---|---|---|---|
| `TA-P001` | 10,000 unique / 1 worker | 10,000 ops；356.455s；p95 44.947ms；integrity/source `PASS` | emulated observation only |
| `TA-P002` | 1,000 originals / 10,000 retries | duplicate accuracy 1.0；lifecycle growth 0；integrity/source `PASS` | idempotency compatibility `PASS` |
| `TA-P003` | 32 workers / 300s / target 64 ops/s | 6,699 ops；22.282 ops/s；426 `TA_STORAGE_UNAVAILABLE`；integrity/source `PASS` | `PARTIAL`; native rerun required |
| `TA-P004` | 1,000 writes / 10 backups | 10/10 restores；writer errors `[]`；integrity/source `PASS` | restore compatibility `PASS` |
| `TA-P005` | 3,600s / target 5 ops/s / 60s checks | 13,171 ops；59/59 periodic + final integrity `PASS`；errors `{}` | long-run integrity `PASS`, not SLO |

`TA-P005` wall time 为 3,600.144s，p95 78.330ms，数据库末值 82,599,936 bytes，Linux
`ru_maxrss` 为 98,988 KiB，tracemalloc peak 为 4,967,450 bytes。以上是模拟环境描述值，
不能和原生平台性能直接比较，也不能证明无内存泄漏。

全部结果保持 source manifest 首尾一致；每个原始结果在 Linux tmpfs 中以 `0600`、拒绝覆盖
方式生成，receipt digest 与导出副本一致。公开安全材料见
[`raw/linux-amd64-emulated-6d1bcbbfc2cb/`](raw/linux-amd64-emulated-6d1bcbbfc2cb/)。

## Security Boundary（安全边界）

- 镜像和 x86_64 platform wheel 均绑定 exact digest/hash；
- 容器 read-only root，source mount read-only；
- `cap-drop ALL`、`no-new-privileges`、无 published port；
- 主功能测试和负载运行 `network=none`；
- 数据库和原始不可覆盖结果在 Linux tmpfs 中产生；
- 没有 listener、Collector、DBOS Runtime、Agent、Entity、Permission 或生产后端。

审计工具安装和 pip-audit 查询曾使用受限 outbound network；没有开放入站端口。Ruff、Bandit、
功能测试和全部负载均在无网络容器中运行。

## Failure Retention（失败保留）

1. 百度云候选主机 SSH 连接被服务端立即关闭，未进入主机，也未修改服务器；
2. Docker 默认 credential helper 缺失，改用无凭据临时配置和显式 Colima socket 拉取公开镜像；
3. Ruff 默认缓存写入 read-only source 失败，保留后将缓存迁移到隔离 work volume；
4. `TA-P001` 首次在 macOS bind mount 上因 `fchmod(0600)` 被拒绝而失败关闭；随后改用 Linux
   tmpfs，未降低权限检查；
5. `TA-P003` 记录 426 个 `TA_STORAGE_UNAVAILABLE`，本报告保持 `PARTIAL`；
6. 两次本地摘要读取使用了不存在的展示字段，未修改原始 JSON 或 receipt。

## Authority Boundary（权力边界）

本验证没有创建 Agent、Runtime、Entity、Capability、Permission、Execution、canonical
Evidence、Verification、Collector 或 network endpoint，没有调用 SAEE，也没有改变 gate。

```text
PR_G2A_HUMAN_REVIEW_APPROVED=false
FULL_PR_G2_READY=false
PRODUCTION_READY=false
DQ_019=BLOCKED_INPUT
DQ_020=BLOCKED_INPUT
DQ_021=BLOCKED_INPUT
```

## Remaining Gates（剩余闸门）

- 真实 Linux x86_64 原生 clean-clone 重跑，尤其复核 `TA-P003`；
- Windows 和真实 production backend 环境；
- `PR-G2A` 独立人工审查与明确批准；
- `DQ-019 / PR-G2B` production persistence；
- `DQ-020 / PR-G3` Collector staging；
- `DQ-021` Telemetry-to-Evidence admission；
- independent human security review 和 human rollback switch exercise。

机器可读结果见
[`DBOS-PR-2A-LINUX-X86-64-EMULATED-COMPATIBILITY-VALIDATION-2026-07-23.json`](DBOS-PR-2A-LINUX-X86-64-EMULATED-COMPATIBILITY-VALIDATION-2026-07-23.json)。
