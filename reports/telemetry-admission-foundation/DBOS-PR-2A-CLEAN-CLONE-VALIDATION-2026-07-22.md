# DBOS PR-2A Clean Clone Validation

```text
decision_reference=DQ-018
source_commit=a3e491c954e911d84baa09fd6d9466fb80280941
implementation_manifest=sha256:9a8c3546a925812f0da86dad6cd09aa4680b2b29b734cd07dcfa9bc51f8dfe95
clean_clone_result=PASS
pr_g2_ready_for_human_review=true
pr_g2_human_review_approved=false
production_ready=false
```

## Outcome（结果）

DBOS Telemetry Admission Foundation（遥测准入基础）已从 GitHub 远端分支的精确提交
`a3e491c…` 完成干净检出验证。该提交相对 `origin/main@cd3f867c…` 包含 56 个 DQ-018
源码／契约／测试文件，清单为 `9a8c3546…dfe95`。本结果使候选达到 **PR-G2 Human
Review Ready（可供 PR-G2 人工审查）**，不等于人工批准、合并、发布、部署或生产就绪。

旧 `f09e99…` 清单遗漏 3 个 SQL migration。旧回执继续保留为历史材料，但不再作为
当前 exact-source（精确源码）证据。

## Clean Clone Results（干净检出结果）

| check | result |
|---|---|
| 远端源码提交与本地推送提交一致 | `PASS`，`a3e491c954e911d84baa09fd6d9466fb80280941` |
| implementation manifest | `PASS`，56 files / 704010 bytes / `9a8c3546…dfe95` |
| 全量 tests | `523/523 PASS`，16/16 directories |
| telemetry tests | `189/189 PASS` |
| validators | `35/35 PASS` |
| telemetry validator | `25/25 PASS`，所有 live effect counts 为 0 |
| OTel Semantic cases | `32/32 PASS`；另 14 个未授权用例保持 blocked |
| OTel Schema/Resource cases | `36/36 PASS`；另 9 个未授权用例保持 blocked |
| rollback drill | `PASS`；失败源保留、恢复到新路径、不自动切换，下一 gate 为 `HUMAN_SWITCH_REQUIRED` |

OTel 工具自身只声明 `IMPLEMENTATION_MANIFEST_ONLY`，并刻意不声称 Git commit 包含关系；
commit、remote ref、clean clone 和 manifest 的外部对账由本报告单独完成，防止工具自证。

## Security and Supply Chain（安全与供应链）

- 生产切片 Bandit `1.9.4`：5,264 LOC，0 findings，0 `nosec`，0 skipped；
- 7 个精确锁定运行依赖：0 个当前已知漏洞；
- 测试目录额外扫描出现 3 个 Low 提示，分别是受控 subprocess 和故意构造的
  secret-shaped（形似密钥）负例夹具；未在源码中静默 suppress，生产切片 findings 为 0；
- 两份独立远端检出在 `SOURCE_DATE_EPOCH=1784678400` 下产生字节一致 wheel；
- wheel SHA-256 `49d193a2…e9853`，64 entries，0 symlink；
- 精确锁定运行环境安装、从 `site-packages` 导入和 `pip check` 均为 `PASS`；
- 当前锁仅覆盖 CPython 3.12.13 / macOS arm64，不产生跨平台声明；
- 独立安全审查仍未完成。

## Authority Boundary（权力边界）

本验证创建数量均为零：Agent、Runtime、Entity、Capability、Permission、Execution、
Evidence、Verification、Collector、network endpoint 和 SAEE call。`full_catalog_result`
继续为 `BLOCKED`，因为 23 个 DQ-020 / PR-G3 deployment cases 未获授权、未执行。

## Next Gate（下一闸门）

当前唯一允许的状态提升是提交 PR-G2 Human Review（人工审查）。在人工审查完成前：

- 不得合并到 `main`；
- 不得发布或部署；
- 不得创建 listener、Collector、生产数据库或 canonical Evidence；
- `DQ-019`、`DQ-020`、独立安全审查、跨平台锁和人工回退切换继续开放。

机器可读结果见
[`DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json`](DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json)。
