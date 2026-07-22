# Raw and Historical Receipt Index

```text
current_exact_source_full_load_rebase_receipt=current-source-rebase-43382e4274c1/
current_exact_source_p003_observer_effect_receipt=p003-observer-effect-43382e4274c1/
predecessor_full_emulated_amd64_receipt=linux-amd64-emulated-6d1bcbbfc2cb/
latest_native_linux_arm64_reference_receipt=linux-arm64-d0951d6c6252/
predecessor_macos_arm64_reference_receipt=current-b6c03faf50bf/
historical_receipts=current-fdda745c3907/,review-fdda745c3907/,review-9a8c3546a925/,review-f09e99b95a33/,current-f09e99b95a33/
raw_root_status=SUPERSEDED_PRE_SEMANTIC_MANIFEST
production_ready=false
```

## Current Exact Source（当前精确源码）

当前远端源码 `23c8f08…` 的完整 load rebase（负载重基线）入口是：

- [`current-source-rebase-43382e4274c1/`](current-source-rebase-43382e4274c1/)
- source commit `23c8f0878058f29e733b6f164572ac157c6c7d1c`
- manifest `sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c`
- measurement contract revision `0.1.1` / `sha256:80f37f4e…9fe6`
- TA-P001、TA-P002、TA-P004、TA-P005 原始结果及 receipts 在该目录；TA-P003 引用下列既有同源工件
- TA-P001—TA-P005 integrity/source binding 全部 `PASS`，authority effects 全部 false
- execution mode `EMULATED_LINUX_AMD64_ON_ARM64_HOST`，不是原生 x86_64、SLO 或生产验证

同一 current source 的 TA-P003 observer-effect hardening（观察者效应加固）入口是：

- [`p003-observer-effect-43382e4274c1/`](p003-observer-effect-43382e4274c1/)
- source commit `23c8f0878058f29e733b6f164572ac157c6c7d1c`
- manifest `sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c`
- 当前源码 534/534 tests；30 validators `PASS` + 5 external-source fail closed
- TA-P003 完整 tmpfs run：18,953 operations、0 errors、integrity/source `PASS`
- 当前源码的 TA-P001—TA-P005 已完整重跑；完整结果从上述 load rebase 回执读取
- execution mode `EMULATED_LINUX_AMD64_ON_ARM64_HOST`，不是原生 x86_64 验证

predecessor `d62b411…` 的 Linux amd64 emulated compatibility（模拟兼容）入口是：

- [`linux-amd64-emulated-6d1bcbbfc2cb/`](linux-amd64-emulated-6d1bcbbfc2cb/)
- source commit `d62b411845b18af3ec79af67622666e96d1baed3`
- manifest `sha256:6d1bcbbfc2cba1add823d390e013d4c755047f1147e338a0a59bf8e4bac0d6e4`
- 534 tests；30 validators `PASS` + 5 external-source fail closed；0 unexpected failures
- Ruff/Bandit/pip-audit 0 findings；`TA-P005` 59/59 + final integrity `PASS`
- `TA-P003` 含 426 个 `TA_STORAGE_UNAVAILABLE`，所以 overall `PARTIAL`
- execution mode `EMULATED_LINUX_AMD64_ON_ARM64_HOST`，不是原生 x86_64 验证

最新原生 Linux arm64 reference validation（参考验证）仍是 predecessor：

- [`linux-arm64-d0951d6c6252/`](linux-arm64-d0951d6c6252/)
- source commit `57c7b9e55dfcab84e81e7c5f61e9d8ea61045dbe`
- manifest `sha256:d0951d6c6252109261f7d2806082b850741df3d1decc4ff5c6418602dff69710`
- 533 tests；30 validators `PASS` + 5 external-source fail closed；0 unexpected failures
- `TA-P001`—`TA-P005` all integrity/source binding `PASS`

## Historical Receipts（历史回执）

`current-b6c03faf50bf/` 是 predecessor macOS arm64 参考材料。`current-fdda745c3907/`、
`review-fdda745c3907/`、`review-9a8c3546a925/`、
`review-f09e99b95a33/`、`current-f09e99b95a33/` 和 raw 根部既有 JSON 保留用于审计，
但不适用于当前 exact source。`current-fdda745c3907/TA-P005.json` 是修复前的一小时比较基线，
不能升级为当前容量或 SLO 声明。

所有文件都是 review artifacts（审查工件），不是 DBOS canonical Evidence，不产生
gate、Permission、Release Authorization 或 Production Ready 状态。
