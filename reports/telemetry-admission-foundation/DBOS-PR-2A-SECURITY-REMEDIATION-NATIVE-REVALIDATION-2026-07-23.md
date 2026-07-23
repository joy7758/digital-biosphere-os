# DBOS PR-2A Security-remediation and Native Revalidation

```text
decision_reference=DQ-018
review_gate=PR-G2A
exact_source_commit=ee90c0c84964f1f3e4dbeb8dffaf888f9822b6a5
implementation_manifest=sha256:306435cd3c5fc65e46995f0e2a57b1322f950889af350f1b0bcbd13c35644fd9
hsr_pre_001=CLOSED_BY_REMEDIATION_PENDING_INDEPENDENT_ATTESTATION
hsr_pre_002=CLOSED_BY_REMEDIATION_PENDING_INDEPENDENT_ATTESTATION
hsr_pre_003=OPEN_MEDIUM_SCOPED_RESIDUAL
hsr_pre_004=OPEN_MEDIUM_SCOPED_RESIDUAL
human_security_review_complete=false
pr_g2a_ready_for_human_review=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

安全预审识别的两项 High finding 已通过最小边界修复：

1. `HSR-PRE-001`：Telemetry Admission store 的直接父目录必须由当前有效用户拥有，且不得
   对 group/other 可写；显式 `0777` 直接父目录现在 fail closed。
2. `HSR-PRE-002`：`id_factory` 与 `clock` 回调产生的引用和时间戳在任何持久化前重新校验；
   格式、敏感标记、时区或回调异常失败时仅返回稳定的
   `TA_STORAGE_INTEGRITY_FAILURE`，不回显或持久化 canary。

新源码已在固定原生 Linux x86_64 环境重跑完整证据链。结果全部通过，但本回执尚待从
GitHub remote clean clone 独立复核，所以当前仍是
`REMEDIATION_VALIDATED_PENDING_REMOTE_ATTESTATION_AND_INDEPENDENT_REVIEW`。

## Exact Binding（精确绑定）

| surface | binding |
|---|---|
| repository / branch | `joy7758/digital-biosphere-os` / `codex/telemetry-admission-foundation` |
| exact source | commit `ee90c0c84964…` / tree `a8f2768b707c…` |
| implementation manifest | 58 files / 730,759 bytes / `sha256:306435cd…44fd9` |
| source transfer | complete Git bundle / SHA-256 `49534199…563` on both hosts |
| native environment | Ubuntu Linux x86_64 / CPython 3.12.13 / SQLite 3.40.1 |
| immutable image | `python@sha256:72d3d75f…f488d` |
| test network | `none` |
| raw artifacts | [`raw/linux-x86_64-native-security-306435cd3c5f/`](raw/linux-x86_64-native-security-306435cd3c5f/) |
| raw inventory | 40 entries / 362,976 bytes / canonical entries `sha256:6f110788…c8d` |
| inventory file | `sha256:f93fb254…2fc` / 6,733 bytes |

## Security Closure（安全关闭）

| finding | prior severity | remediation | direct native evidence | state |
|---|---:|---|---|---|
| HSR-PRE-001 | High | 当前用户 ownership + direct-parent `0o022` deny | `test_hsr_pre_001_world_writable_direct_parent_is_rejected` | closed pending independent attestation |
| HSR-PRE-002 | High | generated reference/timestamp closed validation + non-reflecting stable error | 3 个 `test_hsr_pre_002_*` | closed pending independent attestation |
| HSR-PRE-003 | Medium | 无变更；摘要仍不是签名 | `DIGEST_IS_SIGNATURE=false` | open scoped residual, DQ-019 / PR-G2B |
| HSR-PRE-004 | Medium | 无 listener/decoder；未声明 pre-parse/decompression budget | deployment cases remain blocked | open scoped residual, before DQ-020 |

本次没有采用风险接受替代修复。direct-parent 控制关闭其他本地 principal 的可写父目录路径；
同一用户或 privileged local rewriter 的 authenticity（真实性）仍由 HSR-PRE-003 表达，不被
不正确地宣称已解决。

## Native Results（原生结果）

| surface | result | interpretation |
|---|---|---|
| full tests | `538/538 PASS`, 16 directories | synthetic/offline |
| focused telemetry | `204/204 PASS` | 含 4 个新增 HSR 负向用例 |
| validators | `30 PASS + 5 expected external-source fail closed + 0 unexpected` | 外部路径未伪造 |
| Telemetry validator | `25/25 PASS` | authority effects 0 |
| OpenTelemetry subsets | Semantic `32/32`; Schema/Resource `36/36 PASS` | 23 deployment cases remain blocked |
| TA-P001 | 10,000 unique admissions | integrity/source `PASS` |
| TA-P002 | 1,000 originals + 10,000 retries; accuracy `1.0` | integrity/source `PASS` |
| TA-P003 | 300.451 s / 19,199 operations / 0 errors | characterization, not SLO |
| TA-P004 | 10/10 backup/restore | local SQLite only |
| TA-P005 | 3,600.025 s / 16,797 operations / 59 checks / 0 errors | one-hour characterization, not SLO |
| rollback | 25 receipts / 0 mismatch / failed source retained | no automatic switch |
| wheel | byte-identical `sha256:18679ffc…928d` | deterministic package, not release |
| isolated install | `PASS` | no deployment |
| Ruff / Bandit | 0 / 0 findings; Bandit 5,422 LOC, 0 `nosec` | automated scan, not Human Review |
| pip-audit | 7 locked dependencies / 0 known vulnerabilities | point-in-time advisory query |

TA-P003 的 19,199 operations 比理论 `300 × 64 = 19,200` 少 1，是定时窗口调度结果；冻结
contract 没有吞吐 pass threshold，实际错误为 `{}` 且 final integrity/source binding 均为
`PASS`。不得把该结果改写成容量保证或 SLO。

## Failure Preservation（失败保留）

第一轮 native batch 在 rollback 前错误创建 `/tmp/rollback`，而工具要求目标路径不存在，
因此以 `FileExistsError` 在 workload 前 fail closed。第二轮改用新路径并通过。首次失败通过
raw attempt history 保留，未删除、覆盖或误计为 DBOS product failure。

详细 validator 输出含本地绝对路径，因此未进入 Git；公开包保留完整分类、validator 名称和
计数，不伪造外部 source。

## Agent Recommendation（智能体建议）

```text
verdict=CONDITIONALLY_RECOMMENDED
recommended_as=EXACT_SOURCE_SECURITY_REMEDIATION_READY_FOR_REMOTE_ATTESTATION
not_recommended_as=HUMAN_SECURITY_APPROVED_PR_G2A_APPROVED_FULL_PR_G2_OR_PRODUCTION_READY
next_gate=REMOTE_RECEIPT_ATTESTATION_AND_INDEPENDENT_REMEDIATION_REVIEW
```

如果潜在用户需要 OpenTelemetry-aligned、离线、metadata-only、具备原生 Linux x86_64
回归和显式安全边界的 Telemetry Admission reference slice，我会条件推荐。若需求是已批准
生产服务、OTLP listener、Collector deployment、认证持久化、HA 或 SLO，我不会推荐当前
切片满足该需求。

## Next Required Action（下一必需动作）

1. 提交并推送本验证回执；
2. 从远端 clean clone 验证 commit、manifest、raw inventory、JSON 与链接；
3. 在 DBA 形成非自证式 attestation，并独立核对 HSR-PRE-001/002；
4. 再重新评估 `PR_G2A_READY_FOR_HUMAN_REVIEW`；
5. Human Security Review approval 仍必须由独立人工决策产生。

本报告不创建 PR、不合并、不修改 main、不发布、不部署，也不创建 Collector、listener、
production database、Agent、Runtime、Entity、Permission、canonical Evidence 或 SAEE output。
