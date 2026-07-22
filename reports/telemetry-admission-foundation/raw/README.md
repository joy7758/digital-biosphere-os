# Raw and Historical Receipt Index

```text
current_linux_arm64_reference_receipt=linux-arm64-d0951d6c6252/
predecessor_macos_arm64_reference_receipt=current-b6c03faf50bf/
historical_receipts=current-fdda745c3907/,review-fdda745c3907/,review-9a8c3546a925/,review-f09e99b95a33/,current-f09e99b95a33/
raw_root_status=SUPERSEDED_PRE_SEMANTIC_MANIFEST
production_ready=false
```

## Current Exact Source（当前精确源码）

当前远端 Linux arm64 reference validation（参考验证）入口是：

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
