# DBOS PR-2A Telemetry Admission Foundation Implementation Validation

> Historical phase report（历史阶段报告）：本文件绑定 pre-semantic manifest，
> 已由 `DBOS-PR-2A-PRODUCTION-EVIDENCE-2026-07-22.md` 取代，不得作为当前
> OpenTelemetry-aligned implementation 的精确源码证据。

> Historical snapshot（历史快照）：本报告记录早期 `62-test` 实现候选，已由
> [`DBOS-PR-2A-PRODUCTION-EVIDENCE-2026-07-22.md`](DBOS-PR-2A-PRODUCTION-EVIDENCE-2026-07-22.md)
> 取代为当前工作树的验证入口。旧数字不得用于声称当前 artifact 或 gate 状态。

```text
slice_id=DBOS-PR-2A-TELEMETRY-ADMISSION-FOUNDATION
report_time=2026-07-22T05:10:28Z
result=LOCAL_IMPLEMENTATION_CANDIDATE_PASS
pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

DQ-018 授权的最小 Telemetry Admission Foundation（遥测准入基础）已在独立、
未提交的 DBOS 工作树中实现并完成本地验证。实现包含封闭 metadata-only（仅元数据）
Envelope、只追加 Admission Record、稳定 reason codes、提交后确认、重复／冲突分类、
SQLite 单机参考存储、不可变 migration、在线 backup、到新路径的 restore、完整性检查和
低基数 self-observation。

该结果只表示本地 implementation candidate（实现候选）通过当前直接测试。它不是
canonical Evidence（规范证据）、独立安全审查、PR-G2 批准、生产数据库选择、部署授权
或 Production Ready（生产就绪）声明。

## Exact Bindings（精确绑定）

| surface | binding |
|---|---|
| DBA content baseline | `264f3171c3dfa8a9f614c7d0c835e4be26870d01` |
| DBA freeze attestation | `248ba46b057b14ab9df07d4ab3787f58ee9cdf71` |
| DBOS base commit | `cd3f867c4379ec555c45e7d554088ad12ce08a24` |
| DBOS branch | `codex/telemetry-admission-foundation` |
| DBOS source state | `UNCOMMITTED_LOCAL_WORKTREE` |
| implementation manifest | `sha256:0d7a8a850e917840e863f44b98c3fd6f93f9f881324af51ae22ce4962d430557` |
| implementation files | `21` files / `207479` bytes, report files excluded |
| migration | `0001` / `sha256:a347ab62ff44635794ffa010e1a83251a1c0fc35f47f3cf3707aab5a49197760` |
| wheel candidate | `digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl` |
| wheel SHA-256 | `37f32a4815af31ed9cb5dcd95627c7e0bf9051ed60e1c38e4499575ff397b6ca` |
| wheel size | `69301` bytes |

DBOS commit、push、PR 和 deployment 均未获本切片授权，也未执行。

## Environment（环境）

```text
python_version=3.12.13
sqlite_version=3.50.4
platform=macOS-26.5.2-arm64-arm-64bit
filesystem=APFS
journal_mode=wal
synchronous=FULL
foreign_keys=ON
busy_timeout_ms=5000
```

默认 Homebrew Python 3.14 因本机 `_socket` 动态库代码签名被系统拒绝，首次基线运行
无法加载一个 MCP test module。该环境故障没有计为代码 PASS；随后使用满足项目
`requires-python >=3.11` 的隔离 Python 3.12.13 环境重新安装依赖并完整重跑。

## Before / After State（前后状态）

| gate | before | after |
|---|---:|---:|
| DBOS test directories | `15 PASS` | `16 PASS` |
| DBOS tests | `334/334 PASS` | `396/396 PASS` |
| validators | `34/34 PASS` | `35/35 PASS` |
| focused telemetry admission tests | `0` | `62/62 PASS` |
| telemetry admission validator checks | `0` | `9/9 PASS` |
| Draft 2020-12 schemas | `0` | `2 meta-valid` |
| wheel installed-store check | absent | `PASS` |

测试运行器同时报告：

```text
agent_created=false
runtime_created=false
permission_granted=false
governed_state_modified=false
```

## Implemented Surface（已实现表面）

- `dbos/telemetry_admission/`：常量、immutable result models、validator、service、
  bounded metrics、SQLite append-only store、migration、backup/restore；
- `schemas/telemetry-observation-envelope-schema.yaml`：闭合 Envelope schema；
- `schemas/telemetry-admission-record-schema.yaml`：闭合 Admission Record schema；
- `validation/telemetry_admission_validator.py`：只使用 synthetic fixtures 和自动移除
  temporary stores；
- `tests/telemetry_admission/`：62 项合规、负向、重复、并发、存储和恢复测试；
- `README.md` 与 `pyproject.toml`：智能体入口、非声明和 migration wheel packaging。

`dbos` 根 facade 不自动导出该内部预生产表面。

## Directly Executed Coverage（已直接执行覆盖）

- `TA-C`：TRACE/METRIC/LOG、PROFILE 拒绝、closed shape、Resource/Scope、版本、
  schema URL、GenAI pin、timestamp、limitations、partial/sampling；
- `TA-N`：Identity/Entity、Permission、Evidence、Fitness、Verification claim 注入，
  trace ID 权力／幂等误用；
- `TA-D`：严格 sequence、committed receipt replay、receipt conflict、suspected duplicate、
  same-trace non-duplicate、未提交 receipt、32 concurrent replay；
- `TA-S`：content capture、敏感 key/value、secret canary 不进入 store/WAL/backup/result、
  schema URL 不触发网络、symlink/world-readable path、append-only SQL triggers；
- `TA-F`：lifecycle insert 后中断、commit 前中断、commit 后 reopen、lock timeout、
  corrupt header、owner-only store files；
- `TA-M`：初始 checksum、reopen no mutation、newer version block、tampered checksum、
  unknown schema block；
- `TA-R`：backup/restore、manifest tamper、truncation、restore retry、no overwrite；
- packaging：wheel 包含两份 schema 与 `0001_initial.sql`，安装后 store integrity PASS；
- source audit：无 socket/server/OTel SDK/Collector/Evidence/Entity/SAEE runtime import，
  无 public update/delete/grant/activate/execute surface，常见秘密模式命中 `0`。

## Authority and Truth Boundary（权力与事实边界）

```text
AGENT_CREATED=0
RUNTIME_CREATED=0
ENTITY_CREATED=0
CAPABILITY_CREATED=0
PERMISSION_GRANTED=0
EVIDENCE_CREATED=0
VERIFICATION_CREATED=0
SAEE_CALLED=0
NETWORK_ENDPOINT_CREATED=0
COLLECTOR_DEPLOYED=0
RAW_TELEMETRY_PERSISTED=false
ACCEPTED_AS_MATERIAL_NE_EVIDENCE=true
ADMISSION_NE_PERMISSION=true
```

SQLite 是 `REFERENCE_CONFORMANCE_BACKEND`，不是已选择的 production persistence
backend。测试中的 Envelope、Admission Record 和 store 只存在于 temporary synthetic
fixtures，不形成 live DBOS governed objects。

## Open Gates and Residual Risk（开放闸门与残余风险）

以下内容尚未完成，因此 `PR_G2_READY_FOR_REVIEW=false`：

1. 完整预注册 `TA-F/M/R` 矩阵仍缺 separate-process abrupt termination、真实 disk-full、
   WAL frame corruption、async cancellation、32 conflicting digests、migration interruption、
   live-write backup 和更多 corruption variants；
2. `TA-P001` 至 `TA-P005` 的 10,000-item characterization、5-minute concurrency、
   repeated backup 和 60-minute soak 尚未执行，且 pass/fail thresholds 尚未事前冻结；
3. independent security review、dependency/SBOM scan、正式 Critical/High finding disposition
   尚未完成；
4. Human rollback switch exercise、声明范围内 RPO/RTO drill 尚未完成；
5. OTLP decoder/listener、Collector、real telemetry、multi-tenant、HA 和 production backend
   明确不在 DQ-018 范围，继续保持不存在；
6. source 仍是 uncommitted worktree；需要独立 review 和新的 DBOS commit/push gate。

## Exit State（退出状态）

```text
DQ_018_IMPLEMENTATION_SLICE_PRESENT=true
FOCUSED_TESTS_PASS=true
EXISTING_DBOS_REGRESSION_PASS=true
WHEEL_PACKAGING_PASS=true
ALL_PREREGISTERED_TESTS_PASS=false
INDEPENDENT_SECURITY_REVIEW_COMPLETE=false
RECOVERY_VALIDATED_PARTIAL=true
SECURITY_FINDINGS_CLOSED=false
PR_G2_READY_FOR_REVIEW=false
PRODUCTION_READY=false
```
