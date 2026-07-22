# Current-source Load Rebase Raw Receipt Index

```text
source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
measurement_contract_revision=0.1.1
measurement_contract_digest=sha256:80f37f4ec370b84f71da2615f43d170ecbb76f2fc296df93078be18941bf9fe6
execution_mode=EMULATED_LINUX_AMD64_ON_ARM64_HOST
result=PASS_EMULATED_AMD64_CURRENT_SOURCE_LOAD_REBASE
canonical_evidence_created=false
production_ready=false
```

本目录保存 current source `23c8f08…` 上新执行的 `TA-P001`、`TA-P002`、
`TA-P004`、`TA-P005` 原始结果和不可覆盖 receipt。每个 receipt 的 digest、size、
integrity、source binding 和 authority effects 已与导出文件逐项核对。

`TA-P003` 不在这里复制；其相同 source/manifest/contract 原始结果继续由
[`../p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json`](../p003-observer-effect-43382e4274c1/TA-P003.tmpfs.json)
提供，治理回执为
[`../../DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json`](../../DBOS-PR-2A-P003-OBSERVER-EFFECT-HARDENING-2026-07-23.json)。

这些文件是 public-safe review artifacts（公开安全审查工件），不是 DBOS canonical
Evidence，不证明 native x86_64、SLO、production durability、PR-G2A approval 或
Production Ready。
