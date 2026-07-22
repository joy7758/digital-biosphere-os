# Raw and Historical Receipt Index

```text
current_exact_source_receipt=review-fdda745c3907/
historical_receipts=review-9a8c3546a925/,review-f09e99b95a33/,current-f09e99b95a33/
raw_root_status=SUPERSEDED_PRE_SEMANTIC_MANIFEST
production_ready=false
```

## Current Exact Source（当前精确源码）

当前远端 commit 和 corrected manifest（修正清单）的入口是：

- [`review-fdda745c3907/`](review-fdda745c3907/)
- source commit `5c52c1c2f44767c0b13b4ac9670425721b9ea0dd`
- manifest `sha256:fdda745c3907e35ac92769740f07afc81483be674568879a3c0314c2a09baa51`

## Historical Receipts（历史回执）

`review-9a8c3546a925/`、`review-f09e99b95a33/`、`current-f09e99b95a33/` 和 raw 根部既有
JSON 保留用于审计，但不适用于当前 exact source。当前提交已重跑 `TA-P001`—`TA-P004`；
一小时 `TA-P005` 未重跑，任何历史数据都不能升级为当前容量或 SLO 声明。

所有文件都是 review artifacts（审查工件），不是 DBOS canonical Evidence，不产生
gate、Permission、Release Authorization 或 Production Ready 状态。
