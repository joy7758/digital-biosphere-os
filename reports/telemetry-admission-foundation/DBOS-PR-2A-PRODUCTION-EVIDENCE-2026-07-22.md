# DBOS PR-2A OpenTelemetry-Aligned Production Evidence

> Historical incomplete-scope report（历史不完整范围报告）：本文件绑定旧
> `f09e99…` 清单，该清单遗漏 3 个 SQL migrations。当前精确源码验证入口是
> [`DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.md`](DBOS-PR-2A-CLEAN-CLONE-VALIDATION-2026-07-22.md)，
> 本文件不得用于当前 exact-source、PR-G2 readiness 或 artifact 声明。

```text
slice_id=DBOS-PR-2A-TELEMETRY-ADMISSION-FOUNDATION
decision_reference=DQ-018
authorized_subset_result=PASS
full_catalog_result=BLOCKED
pr_g2_ready_for_review=false
production_ready=false
```

## Outcome（结果）

DQ-018 授权的离线 Telemetry Admission Foundation（遥测准入基础）已完成
OpenTelemetry-aligned（对齐 OpenTelemetry）的本地实现与证据收口。当前切片具备：

- metadata-only（仅元数据）、fail-closed（失败关闭）的准入 envelope；
- append-only SQLite reference store（追加式 SQLite 参考存储）；
- 确定性 replay/idempotency（重放/幂等）、迁移、备份、恢复、完整性和低基数指标；
- 固定摘要的 OTel Semantic Convention（语义约定）映射；
- Schema/Resource provenance（模式/资源来源链）、受限离线转换和 Development Entity 隔离；
- 授权用例到具体测试节点的一对一绑定；
- exact-hash runtime/build locks（精确摘要运行／构建锁）、两份干净源码快照的
  byte-identical wheel（字节一致 wheel）、CycloneDX SBOM、依赖审计、静态扫描、
  回滚演练和一小时耐久性表征；
- 不可覆盖、`0600` 权限并同时绑定运行前后源码清单的原始表征结果工件。

这是一份 local review input（本地审查输入），不是 PR-G2 批准、DBOS canonical
Evidence、独立安全审查或 Production Ready（生产就绪）声明。

## Exact Source Binding（精确源码绑定）

| surface | binding |
|---|---|
| DBOS base commit | `cd3f867c4379ec555c45e7d554088ad12ce08a24` |
| branch | `codex/telemetry-admission-foundation` |
| source state | `UNCOMMITTED_LOCAL_WORKTREE` |
| implementation manifest | `sha256:f09e99b95a3332d40abc933eaee35ea8a646b11d330ffaa5213ee0bb28f339b4` |
| manifest scope | `53` files / `698231` bytes；reports excluded |
| source commit includes implementation | `false` |
| wheel | `digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl` |
| wheel SHA-256 | `f15fb089b1dadcc1d8278cf0a8dbf4ff89ddfaf203f9f5b73fbecdce3b816660` |
| wheel size | `124813` bytes |
| SBOM | [`DBOS-PR-2A-SBOM.cdx.json`](DBOS-PR-2A-SBOM.cdx.json), CycloneDX `1.6`, SHA-256 `70c21af4…f62c95` |

DBOS commit、push、PR、merge 和 deployment 均未获 DQ-018 授权，也未执行。

## OpenTelemetry Reference Binding（参考基线）

| decision | adopted baseline |
|---|---|
| `DQ-022` | OTLP `1.11.0` |
| `DQ-023` | OTel Semantic Conventions `1.43.0` core + pinned GenAI mapping |
| `DQ-024` | OTel Specification/Schema Resource `1.59.0` + Development Entity quarantine |
| `DQ-025` | Collector `v0.156` custom minimal inventory（仅清单；本轮未部署） |
| `ADR-024` | staged telemetry production path（分阶段遥测生产路径） |

运行时只读取 vendored（随包固定）的参考制品并先校验 SHA-256；没有运行时网络获取。
当前固定来源为 OTel spec `v1.59.0@a824dc…`、core semconv
`v1.43.0@89aa8b…`、GenAI `2e994c…`、OTLP `v1.11.0@790608…`。

## Conformance（符合性）

| catalog | total | DQ-018 / PR-G2 authorized | result | blocked |
|---|---:|---:|---:|---:|
| Semantic mapping | 46 cases / 47 fields | 32 | `32/32 PASS` | 14 |
| Schema/Resource | 45 cases | 36 | `36/36 PASS` | 9 |

授权子集结果为 `PASS`；完整目录结果为 `BLOCKED`。14 个 sensitive/cardinality
语义用例与 9 个网络、Collector、部署及数据治理用例属于未授权的 DQ-020/PR-G3
等后续 gate，未执行。两份 DBA official result-set schema 只完成 meta-validation，
没有伪造全目录 `PASS` 结果集。

主要安全边界：

- 输出仅保留 digest/reference（摘要/引用），不持久化原始 telemetry 内容；
- sensitive 字段默认禁用；显式 opt-in 也只产生摘要；
- OTel Development Entity 永远进入 quarantine（隔离区），不创建 DBOS Entity；
- semantic/provenance 结果不能创建 Evidence、Permission 或关闭 gate；
- 未知版本、摘要漂移、authority injection（权力字段注入）和来源冲突失败关闭。

## Regression and Quality（回归与质量）

| evidence | result |
|---|---:|
| all DBOS tests | `523/523 PASS` |
| test directories | `16/16 PASS` |
| focused telemetry tests | `189/189 PASS` |
| validators | `35/35 PASS` |
| telemetry validator | `25/25 PASS` |
| targeted Ruff check / format | `PASS / PASS` |
| Bandit | `0` findings / `5263 LOC` / `0 nosec` / `0 skipped` |
| pip check | `PASS` |
| wheel runtime dependency audit | `7` dependencies / `0` known vulnerabilities |
| isolated wheel install | `PASS` |
| installed profile inventory | `47` fields / `46` semantic / `45` Schema-Resource / schema format `1.1.0` |

Whole-repository Ruff 仍有 `39` 条本切片之前已存在、且位于其他文件的 lint debt；
本次新增切片为 `0`。没有越权修改这些历史文件。

Coverage（覆盖率）没有事前冻结阈值，因此只能作 characterization（表征）：
`1827` statements、`252` missing、`658` branches、`172` partial，综合 `82%`；
不得把它写成覆盖率 gate 通过。

## Load Characterization（负载表征）

冻结契约为
[`load_characterization.v0.1.json`](../../tests/telemetry_admission/load_characterization.v0.1.json)，
SHA-256 `b817493ba4c5381dfe26cb042832b75a7f4d4c75f3948ba8d104e37f49f54e91`。
结果语义固定为 `CHARACTERIZATION_NOT_SLO`，范围仅为 macOS、Python `3.12.13`、
SQLite `3.50.4`、10 CPU 的单机 SQLite 参考后端。

| case | frozen workload | exact current-manifest result |
|---|---|---|
| `TA-P001` | 10,000 unique | `46.002s`; p95 `6.875ms`; errors `0`; integrity `PASS` |
| `TA-P002` | 1,000 originals + 10,000 retries | accuracy `1.0`; lifecycle growth `0`; p95 `4.412ms`; integrity `PASS` |
| `TA-P003` | 32 workers / 300s / target 64 ops/s | 19,061 ops; `63.430 ops/s`; p95 `79.958ms`; errors `0`; integrity `PASS` |
| `TA-P004` | 1,000 writes + 10 backups | restore `10/10`; writer errors `0`; integrity `PASS` |
| `TA-P005` | 3,600s / mixed 5 ops/s | 17,260 ops; 59 periodic checks + final `PASS`; errors `0`; p95 `16.093ms` |

`TA-P005` 精确状态：accepted `12,082`、rejected `3,452`、confirmed duplicate
`1,726`；wall time `3600.083674s`。拒绝与失败不会静默删除。由于没有 owner-frozen
阈值，这些数字不是吞吐、延迟或容量 SLO。

五个结果均绑定运行前后相同的 `f09e99b9…f339b4` manifest，绑定结果
`5/5 PASS`；原始 JSON 位于 [`raw/current-f09e99b95a33/`](raw/current-f09e99b95a33/)，
权限均为 `0o600`，工具拒绝覆盖既有目标。它们是 review artifacts（审查工件），
不是 DBOS canonical Evidence。

## Security and Supply Chain（安全与供应链）

- Bandit `1.9.4` 对 production package、validator 和运维工具扫描 `5263 LOC`，
  findings `0`、`nosec 0`、skipped `0`；
- pip-audit `2.10.1` 对 wheel 的全部 7 个固定第三方运行依赖报告已知漏洞 `0`；
- 根包 `digital-biosphere-os-preview` 尚未发布到 PyPI，无法按 PyPI 包记录审计；
  这项限制保留，不能把源码扫描等同独立安全认证；
- CycloneDX `1.6` SBOM 通过生成期 schema validation，包含 8 components 和
  9 dependency entries；
- runtime closure（运行依赖闭包）7 个包和 build toolchain（构建工具链）5 个包均
  exact-version + exact-hash 锁定；运行锁 SHA-256 `13a50e3f…ada8d`，构建锁
  SHA-256 `1cea23a9…a95c`；
- 两份独立干净源码快照在固定 `SOURCE_DATE_EPOCH=1784678400`、离线锁定构建环境中
  生成相同 wheel SHA-256 `f15fb089…16660`；锁定运行环境的 isolated install 与
  `pip check` 均为 `PASS`；
- 当前锁只声明 CPython `3.12` / macOS `11+` / arm64；`cross_platform_claim=false`，
  其他平台必须生成并审查独立锁；
- independent security review（独立安全审查）仍为 `false`。

当前 wheel 是完整 `digital-biosphere-os-preview` package，不是 DQ-018-only
distribution。为避免把 53-file DQ-018 manifest 冒充完整制品输入，现另行绑定：

- full wheel build inputs：61 files，manifest `cc217f3f…65fb59`；当前工作树和两个
  clean snapshots 三者一致；
- wheel content：64 entries，manifest `47b86162…c0b87`；两次构建一致且 symlink 0；
- wheel bytes：SHA-256 `f15fb089…16660`。

## Recovery and Rollback（恢复与回退）

25 条 synthetic admission（合成准入）的回退演练结果：pre-incident integrity
`PASS`、receipt mismatch `0`、失败源以 `0o400` 保留、恢复到不同路径、恢复完整性
`PASS`。工具不自动切换 caller，停在 `HUMAN_SWITCH_REQUIRED`；因此 Human rollback
switch exercise 尚未完成。

## Authority Effects（权力副作用）

```text
AGENT_CREATED=0
RUNTIME_CREATED=0
ENTITY_CREATED=0
CAPABILITY_CREATED=0
PERMISSION_CREATED=0
EXECUTION_CREATED=0
EVIDENCE_CREATED=0
VERIFICATION_CREATED=0
COLLECTOR_CREATED=0
NETWORK_ENDPOINT_CREATED=0
SAEE_CALLED=0
GATE_STATE_CHANGED=0
PRODUCTION_READY_DECLARED=0
```

## Open Gates（开放闸门）

`PR_G2_READY_FOR_REVIEW=false`、`PRODUCTION_READY=false`，原因：

1. 当前实现只有 exact manifest，没有 exact source commit；
2. DBOS commit/push 未授权，DBA PR-G2 Human Review 未发生；
3. DQ-020/PR-G3 网络、Collector、部署用例未授权且未执行；
4. 完整 Semantic 与 Schema/Resource catalogs 仍为 `BLOCKED`；
5. independent security review 未完成；
6. 性能阈值未事前冻结，结果只是表征；
7. Human rollback switch exercise 未完成；
8. production persistence backend 尚未选择；SQLite 只是 reference backend；
9. 全仓库仍有 39 条历史 Ruff debt。
10. 当前还没有跨平台 dependency locks（依赖锁），本轮结论仅适用于已声明平台。
11. Git 只保留 executable bit，不保留本地 `0o600`；若未来纳入提交，必须另定受控
    artifact storage（工件存储）或 checkout 后权限恢复/验证规则。

## Artifact Truth（工件事实）

机器可读完整摘要位于
[`DBOS-PR-2A-PRODUCTION-EVIDENCE-2026-07-22.json`](DBOS-PR-2A-PRODUCTION-EVIDENCE-2026-07-22.json)。
PR-G2 十项验收映射和直接回执入口位于
[`DBOS-PR-2A-PR-G2-REVIEW-PACKET-2026-07-22.md`](DBOS-PR-2A-PR-G2-REVIEW-PACKET-2026-07-22.md)。
[`raw/`](raw/) 根部早期 JSON 绑定的是 pre-semantic manifest，已由
[`raw/README.md`](raw/README.md) 标记为 historical/superseded；当前精确结果位于
[`raw/current-f09e99b95a33/`](raw/current-f09e99b95a33/)，五个文件均绑定当前
manifest，但仍不得升级为 canonical Evidence、PR-G2 批准或生产声明。
