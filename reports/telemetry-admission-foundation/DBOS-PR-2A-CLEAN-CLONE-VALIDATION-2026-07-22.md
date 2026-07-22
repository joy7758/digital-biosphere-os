# DBOS PR-2A Clean Clone Validation

```text
decision_reference=DQ-018
review_gate=PR-G2A
source_commit=5c52c1c2f44767c0b13b4ac9670425721b9ea0dd
implementation_manifest=sha256:fdda745c3907e35ac92769740f07afc81483be674568879a3c0314c2a09baa51
clean_clone_result=PASS
pr_g2a_ready_for_human_review=true
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

DBOS Telemetry Admission Foundation（遥测准入基础）的精确远端源码提交
`5c52c1c2…` 已从两个独立 clean clone（干净检出）完成测试、构建与安装验证。
当前候选达到 **PR-G2A Human Review Ready（PR-G2A 可供人工审查）**，不等于
PR-G2A 已批准，也不等于完整 `PR-G2`、合并、发布、部署或生产就绪。

`PR-G2` 仍由 `PR-G2B`、`PR-G2T`、`PR-G2I`、`PR-G2C` 阻塞。

## Clean Clone Results（干净检出结果）

| check | result |
|---|---|
| remote/local/clone commit | `PASS`，均为 `5c52c1c2f44767c0b13b4ac9670425721b9ea0dd` |
| implementation manifest | `PASS`，56 files / 714335 bytes / `fdda745c…baa51` |
| full tests | `531/531 PASS`，16 directories |
| focused telemetry tests | `197/197 PASS` |
| validators | `35/35 PASS` |
| telemetry validator | `25/25 PASS`，live effect counts 均为 0 |
| OTel Semantic cases | `32/32 PASS`；14 个未授权用例保持 blocked |
| OTel Schema/Resource cases | `36/36 PASS`；9 个未授权用例保持 blocked |
| rollback drill | `25` acknowledgements，`PASS`；失败源保留、独立路径恢复、mismatch `0`、不自动切换 |
| reproducible wheel | 两个独立 clone 产物字节一致，SHA-256 `24082849…e41` |
| installed wheel | 锁定依赖安装、`pip check`、离开源码树导入、migration/profile 资源读取均 `PASS` |

OTel 工具只声明 `IMPLEMENTATION_MANIFEST_ONLY`。Git commit、remote ref、clean clone 和
manifest 的对账由本报告独立完成，避免实现工具自证。

## Independent Hardening（独立加固）

本轮审查复现并修复了七类问题：兼容迁移备份 lineage、祖先 symlink 逃逸、非普通文件
store、无界时长样本、伪造 accepted decision、state/count 矛盾及 bool count、畸形恢复
manifest 的非稳定错误。修复后：

- full tests `531/531`，新增 8 个负向／恢复测试；
- telemetry package focused coverage `86%`；
- Bandit `1.9.4` 扫描生产切片 5,352 LOC，0 findings；
- `pip-audit 2.10.0` 审计 7 个锁定运行依赖，0 个已知漏洞；
- 四个完整负载画像 `TA-P001`—`TA-P004` 在新清单上保持 source stable 和 integrity
  `PASS`；`TA-P005` 的 1 小时画像未在新提交上重跑，因此不作当前长时性能声明。

以上是离线、单机 SQLite reference backend（参考后端）的直接证据，不是 SLO、容量、
高可用或生产持久性声明。

## Authority Boundary（权力边界）

本验证没有创建 Agent、Runtime、Entity、Capability、Permission、Execution、Evidence、
Verification、Collector、network endpoint，也没有调用 SAEE。完整 OTel catalog 继续
`BLOCKED`，因为 23 个 DQ-020 / PR-G3 deployment cases 未获授权、未执行。

## Next Gate（下一闸门）

下一状态提升只能由 `PR-G2A Human Review` 明确决定。在此之前不得把本结果表述为完整
`PR-G2` 或生产就绪。`DQ-019` production persistence、`DQ-020` deployment cases、独立
人工安全审查、跨平台锁和 Human rollback switch 继续开放。

机器可读结果见
[`DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json`](DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.json)。
