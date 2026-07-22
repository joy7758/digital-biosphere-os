# Telemetry Admission Foundation Review Entry

```text
decision_reference=DQ-018
review_gate=PR-G2A
source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
clean_clone_result=PASS
x86_64_execution_mode=EMULATED_LINUX_AMD64_ON_ARM64_HOST
x86_64_p003_result=PASS_OBSERVER_EFFECT_HARDENED_NATIVE_VALIDATION_STILL_REQUIRED
current_source_full_ta_p001_to_ta_p005_rebase_complete=false
pr_g2a_current_source_packet_refresh_required=true
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Agent Reading Order（智能体读取顺序）

1. [`DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json`](DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json)：当前精确源码 `23c8f08…`、measurement contract `0.1.1`、TA-P003 observer-effect 根因、同介质完整重跑和当前源码重基线缺口；
2. [`DBOS-PR-2A-LINUX-X86-64-EMULATED-COMPATIBILITY-VALIDATION-2026-07-23.json`](DBOS-PR-2A-LINUX-X86-64-EMULATED-COMPATIBILITY-VALIDATION-2026-07-23.json)：predecessor `d62b411…` 的五项模拟兼容基线和 426 个保留错误；
3. [`DBOS-PR-2A-LINUX-ARM64-CROSS-PLATFORM-VALIDATION-2026-07-22.json`](DBOS-PR-2A-LINUX-ARM64-CROSS-PLATFORM-VALIDATION-2026-07-22.json)：predecessor `57c7b9e…` 的原生 Linux arm64 固定参考验证；
4. [`DBOS-PR-2A-STREAMING-INTEGRITY-HARDENING-2026-07-22.json`](DBOS-PR-2A-STREAMING-INTEGRITY-HARDENING-2026-07-22.json)：predecessor 流式完整性修复和 macOS arm64 验证；
5. [`DBOS-PR-2A-PR-G2A-REVIEW-PACKET-2026-07-22.json`](DBOS-PR-2A-PR-G2A-REVIEW-PACKET-2026-07-22.json)：切片、闸门和完整 PR-G2 阻塞项；
6. [`DBOS-PR-2A-INDEPENDENT-TECHNICAL-REVIEW-2026-07-22.json`](DBOS-PR-2A-INDEPENDENT-TECHNICAL-REVIEW-2026-07-22.json)：predecessor 七项发现、关闭状态和剩余风险；
7. [`DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json`](DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json)：predecessor 精确远端源码、测试、OTel、恢复、供应链和 wheel；
8. [`DBOS-PR-2A-SBOM.cdx.json`](DBOS-PR-2A-SBOM.cdx.json)：依赖拓扑 SBOM；不代表签名或发布；
9. `fdda745c…`、`9a8c3546…`、`f09e99…` 及旧 `PR-G2` 文件：仅历史／已被替代回执。

## Current Boundary（当前边界）

当前候选是离线、metadata-only Telemetry Admission reference conformance（参考符合性），
对应 `PR-G2A`。没有 OTLP listener、Collector deployment、production persistence、canonical
Evidence、Agent、Runtime、Entity、Capability、Permission、Execution、Verification 或 SAEE
调用。DQ-020 的 23 个部署用例没有执行。

当前源码修正了并发 `tracemalloc` 对 QEMU 下 `TA-P003` 的观察者效应：同介质完整重跑
18,953 次成功、0 错误、integrity/source binding `PASS`。但其他四个 workload 尚未在当前
manifest 上重跑，真实 Linux x86_64 原生平台也未验证，所以当前 PR-G2A packet 需要刷新。

当前 source 的 `PR_G2A_CURRENT_SOURCE_PACKET_REFRESH_REQUIRED=true`。predecessor packet
只保留为历史审查材料；当前 source 在五项 workload 重基线完成前不标记为 review ready。
任何 packet ready 状态也不等于 Human Approval、完整 `PR-G2`、merge、release、deployment
或 Production Ready。

## Historical Boundary（历史边界）

旧 `PR-G2` 命名把 S1 离线切片误写为完整 gate，已由 `PR-G2A` 回执纠正。旧文件不删除，
但明确标记 `SUPERSEDED`。`fdda745c…` 一小时数据只作为流式修复比较基线；当前 Linux
arm64 predecessor 原始结果必须从
[`raw/linux-arm64-d0951d6c6252/`](raw/linux-arm64-d0951d6c6252/) 读取，且仍不是容量或
SLO 声明。当前 P003 修正材料从
[`raw/p003-observer-effect-43382e4274c1/`](raw/p003-observer-effect-43382e4274c1/)
读取；完整五项模拟 predecessor 从
[`raw/linux-amd64-emulated-6d1bcbbfc2cb/`](raw/linux-amd64-emulated-6d1bcbbfc2cb/)
读取；`raw/current-b6c03faf50bf/` 保留为 predecessor macOS arm64 参考材料。
