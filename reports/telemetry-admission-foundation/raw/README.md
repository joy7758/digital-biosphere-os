# Raw and Historical Receipt Index

```text
current_exact_source_receipt=current-b6c03faf50bf/
historical_receipts=current-fdda745c3907/,review-fdda745c3907/,review-9a8c3546a925/,review-f09e99b95a33/,current-f09e99b95a33/
raw_root_status=SUPERSEDED_PRE_SEMANTIC_MANIFEST
production_ready=false
```

## Current Exact Source（当前精确源码）

当前远端 hardened commit（加固提交）和 manifest（清单）的入口是：

- [`current-b6c03faf50bf/`](current-b6c03faf50bf/)
- source commit `3a63161d3e04d785b4b04feadd4a0712bf6314fc`
- manifest `sha256:b6c03faf50bfab4ce25edaeb39b7ae36d2525df32519f82a8108c164162bd9fc`
- `TA-P001`—`TA-P005` all integrity/source binding `PASS`

## Historical Receipts（历史回执）

`current-fdda745c3907/`、`review-fdda745c3907/`、`review-9a8c3546a925/`、
`review-f09e99b95a33/`、`current-f09e99b95a33/` 和 raw 根部既有 JSON 保留用于审计，
但不适用于当前 exact source。`current-fdda745c3907/TA-P005.json` 是修复前的一小时比较基线，
不能升级为当前容量或 SLO 声明。

所有文件都是 review artifacts（审查工件），不是 DBOS canonical Evidence，不产生
gate、Permission、Release Authorization 或 Production Ready 状态。
