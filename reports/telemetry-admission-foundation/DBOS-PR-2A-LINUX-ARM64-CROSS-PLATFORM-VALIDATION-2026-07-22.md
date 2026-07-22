# DBOS PR-2A Linux arm64 Cross-Platform Validation

```text
decision_reference=DQ-018
review_gate=PR-G2A
implementation_source_commit=57c7b9e55dfcab84e81e7c5f61e9d8ea61045dbe
implementation_tree=a044e54841f856df49e682f8a7a07d9b64a0db8b
implementation_manifest=sha256:d0951d6c6252109261f7d2806082b850741df3d1decc4ff5c6418602dff69710
linux_arm64_reference_validation=PASS
result_semantics=REFERENCE_VALIDATION_NOT_SLO_NOT_GATE_APPROVAL
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

远端分支 `codex/telemetry-admission-foundation` 的精确提交 `57c7b9e…` 已在独立 Linux
arm64 clean clone（干净检出）中完成锁定依赖安装、全量测试、失败关闭验证、安全扫描及
`TA-P001`—`TA-P005` 完整负载表征。该固定参考环境结果为 `PASS`。

本结果只补充 `CPython 3.12.13 / Linux glibc arm64` 的 reference evidence（参考验证材料）。
它不是 SLO、生产容量、PR-G2A 人工批准、完整 PR-G2、合并、发布、部署或生产就绪声明。

## Immutable Bindings（不可变绑定）

| binding | value |
|---|---|
| source commit | `57c7b9e55dfcab84e81e7c5f61e9d8ea61045dbe` |
| source tree | `a044e54841f856df49e682f8a7a07d9b64a0db8b` |
| implementation manifest | 57 files / 720,322 bytes / `sha256:d0951d6…9710` |
| base image | `python:3.12.13-slim-bookworm@sha256:d50fb761…aa30b` |
| runtime lock | `sha256:b989823d…38b3` |
| build lock | `sha256:1cea23a9…95c` |
| platform | `Linux-6.8.0-100-generic-aarch64-with-glibc2.36` |
| Python / SQLite | `3.12.13` / `3.40.1` |

结果报告是上述实现提交的后继回执。新增报告文件不会反向写入被测 implementation
manifest，避免循环自证。

## Validation Results（验证结果）

| check | result |
|---|---|
| remote clean clone | `PASS`；local / remote / clone commit 一致，clone clean |
| exact runtime lock install | `PASS`；7 个 wheel 依赖，`--require-hashes --only-binary=:all:` |
| full tests | `533/533 PASS`，16 个测试目录 |
| focused telemetry tests | `199/199 PASS` |
| hermetic validators | 35 个：30 `PASS`，5 个外部规范来源缺失时 fail closed，0 unexpected failures |
| telemetry admission validator | `25/25 PASS` |
| Ruff | 0 findings；34 个 DQ-018 范围文件 format check `PASS` |
| Bandit | 5,360 LOC，0 findings，0 `nosec`，0 skipped tests |
| pip-audit | 7 个锁定运行依赖，0 个已知漏洞 |
| pip check | `PASS` |

5 个 hermetic fail-closed validator 为 `capability_claim_validator`、
`capability_validator`、`evidence_validator`、`federation_validator` 和
`identity_validator`。它们依赖 clone 外部的规范来源；本验证没有忽略检查或伪造来源，
因此不写成 `35/35 PASS`。

## Load Characterization（负载表征）

| case | fixed parameters | observed result |
|---|---|---|
| `TA-P001` | 10,000 unique admissions / 1 worker | 10,000 ops；33.732s；p95 4.017ms；integrity `PASS` |
| `TA-P002` | 1,000 originals / 10,000 confirmed retries | duplicate accuracy `1.0`；lifecycle growth `0`；integrity `PASS` |
| `TA-P003` | 32 workers / 300s / target 64 ops/s | 19,036 ops；63.347 ops/s；errors `{}`；integrity `PASS` |
| `TA-P004` | 1,000 writes / 10 backups | 10/10 restores；restore pass rate `1.0`；integrity `PASS` |
| `TA-P005` | 3,600s / target 5 ops/s / 60s integrity interval | 17,410 ops；4.836 ops/s；59/59 periodic checks `PASS`；final integrity `PASS`；errors `{}` |

`TA-P005` 实际 wall time 为 `3600.033s`，p95 `18.491ms`，数据库末值
`109,092,864` bytes。Linux `ru_maxrss=49,228 KiB` 归一化为 `50,409,472` bytes；
Python tracemalloc peak 为 `6,624,510` bytes。以上均为描述性观察值，不是资源 SLO、
泄漏证明或生产容量承诺。

五个结果均保持 source manifest 前后一致，source binding 与 artifact integrity 为
`PASS`；结果文件模式为 `0600` 且拒绝覆盖。原始结果与回执见
[`raw/linux-arm64-d0951d6c6252/`](raw/linux-arm64-d0951d6c6252/)。

## Container Security Boundary（容器安全边界）

- 精确 digest 基础镜像，Linux arm64；
- 主验证进程 UID/GID `65532:65532`；
- read-only root filesystem；
- source mount read-only；
- `cap-drop ALL`；
- `no-new-privileges:true`；
- 临时测试数据库位于隔离 tmpfs；
- 没有 listener、Collector、DBOS Runtime 或 production backend。

容器默认网络只在主测试前用于按哈希下载锁定 wheels。负载工具本身离线运行且没有创建
network endpoint。

## Failure Retention（失败保留）

验证过程没有隐藏失败：

1. `noexec` tmpfs 阻止原生 wheel 映射，测试 fail closed；
2. clean clone 全量测试通过，但 5 个外部来源 validator 按预期 fail closed；
3. Ruff cache 在只读源码卷写入失败；
4. 全仓 Ruff 暴露 DQ-018 外历史问题，未擅自扩大范围；
5. DQ-018 范围发现一处格式漂移，修正并提交为 `57c7b9e…`；
6. 集成验证通过，但审计工具下载网络超时；
7. 重试安全审计后 Ruff、Bandit、pip-audit 全部通过。

以上失败均没有被改写为成功；最终结果来自新的、精确绑定的成功尝试。

## Authority Boundary（权力边界）

本验证没有创建 Agent、Runtime、Entity、Capability、Permission、Execution、canonical
Evidence、Verification、Collector 或 network endpoint，没有调用 SAEE，也没有改变任何
gate state。`PR_G2A_HUMAN_REVIEW_APPROVED=false`、`FULL_PR_G2_READY=false`、
`PRODUCTION_READY=false` 保持不变。

## Remaining Gates（剩余闸门）

- `PR-G2A` 独立人工审查及明确批准；
- `DQ-019 / PR-G2B` production persistence；
- `PR-G2T` telemetry deployment integration；
- `PR-G2I` identity continuity integration；
- `DQ-021 / PR-G2C` federation and durability；
- `DQ-020 / PR-G3` deployment case authorization；
- independent human security review；
- Windows、Linux x86_64 及真实生产后端验证；
- human rollback switch exercise。

因此 R-042 的 cross-platform unknown 只在 Linux arm64 固定参考环境获得局部缓解，不能
关闭。

机器可读结果见
[`DBOS-PR-2A-LINUX-ARM64-CROSS-PLATFORM-VALIDATION-2026-07-22.json`](DBOS-PR-2A-LINUX-ARM64-CROSS-PLATFORM-VALIDATION-2026-07-22.json)。
