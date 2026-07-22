# Raw and Historical Receipt Index

```text
current_exact_source_receipt=review-9a8c3546a925/
historical_incomplete_scope_receipts=review-f09e99b95a33/,current-f09e99b95a33/
raw_root_status=SUPERSEDED_PRE_SEMANTIC_MANIFEST
production_ready=false
```

## Current Exact Source（当前精确源码）

当前远端 commit 和 corrected manifest（修正清单）的入口是：

- [`review-9a8c3546a925/`](review-9a8c3546a925/)
- source commit `a3e491c954e911d84baa09fd6d9466fb80280941`
- manifest `sha256:9a8c3546a925812f0da86dad6cd09aa4680b2b29b734cd07dcfa9bc51f8dfe95`

## Historical Receipts（历史回执）

`review-f09e99b95a33/`、`current-f09e99b95a33/` 和 raw 根部既有 JSON 保留用于审计，
但不适用于当前 exact source，因为旧 manifest 漏掉 3 个 SQL migrations。旧五项 load
characterization 没有在精确 commit 上重跑，不能证明当前性能、容量或 SLO。

所有文件都是 review artifacts（审查工件），不是 DBOS canonical Evidence，不产生
gate、Permission、Release Authorization 或 Production Ready 状态。
