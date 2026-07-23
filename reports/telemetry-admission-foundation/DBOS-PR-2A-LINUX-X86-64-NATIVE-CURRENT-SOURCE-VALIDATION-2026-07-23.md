# DBOS PR-2A Native Linux x86_64 Current-source Validation

```text
decision_reference=DQ-018
review_gate=PR-G2A
exact_source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
execution_mode=NATIVE_LINUX_X86_64_IMMUTABLE_CONTAINER_NETWORK_NONE
native_linux_x86_64_direct_validation=PASS
receipt_remote_attested=false
human_security_review_complete=false
pr_g2a_ready_for_human_review=false
pr_g2a_human_review_approved=false
full_pr_g2_ready=false
production_ready=false
```

## Outcome（结果）

DQ-018 current source 已在原生 Linux x86_64 主机上完成直接验证。验证使用架构锁定的
`python:3.12.13-slim-bookworm` immutable digest（不可变摘要），runtime/build 依赖从
exact-hash wheelhouse 安装，所有测试和负载容器均使用 `--network none`。

534/534 全仓测试、200/200 telemetry tests、25/25 Telemetry validator、OpenTelemetry
授权子集 32/32 + 36/36、TA-P001—TA-P005、rollback、可重复 wheel 和隔离安装均通过。
五个跨项目 validator 因隔离环境不包含开发机绝对路径对应的外部项目而 fail closed；准确
结果是 `30 PASS + 5 EXPECTED_EXTERNAL_SOURCE_FAIL_CLOSED + 0 unexpected`，不是 35/35。

本结果关闭 native Linux x86_64 direct-validation blocker，但新回执尚未远端 attested，
Human Security Review 也未完成。因此 `PR_G2A_READY_FOR_HUMAN_REVIEW=false`，更不等于
PR-G2A Human Approval、完整 PR-G2、SLO、生产持久化、部署或 Production Ready。

## Exact Binding（精确绑定）

| surface | exact binding |
|---|---|
| source commit / tree | `23c8f0878058f29e733b6f164572ac157c6c7d1c` / `27703ed64d6e885a2933a5a39139a59bab83c3c1` |
| implementation manifest | 58 files / 726,068 bytes / `sha256:43382e42…abc8c` |
| native host / container | Linux `x86_64` / image `amd64` |
| Python / SQLite | `3.12.13` / `3.40.1` |
| base image | `sha256:72d3d75f…f488d` |
| test network | `none` |
| raw receipt | [`raw/linux-x86_64-native-43382e4274c1/`](raw/linux-x86_64-native-43382e4274c1/) |
| raw inventory | 32 entries / 316,531 bytes / canonical entries `sha256:4967bc67…8f28` |
| inventory file | `sha256:f434c833…b06a` |

## Direct Results（直接结果）

| surface | result | boundary |
|---|---|---|
| exact-hash runtime lock | `PASS`; `pip check` clean | exact Linux x86_64 / CPython 3.12 lock |
| full tests | `534/534 PASS` across 16 directories | synthetic/offline |
| focused telemetry tests | `200/200 PASS` | no listener or deployment |
| validators | `30 PASS + 5 expected external-source fail closed`; unexpected `0` | external paths not fabricated |
| Telemetry validator | `25/25 PASS` | authority effects `0` |
| OTel authorized subset | Semantic `32/32`; Schema/Resource `36/36 PASS` | 23 deployment cases remain `BLOCKED` |
| TA-P001 | 10,000 unique admissions; integrity/source `PASS` | characterization, not SLO |
| TA-P002 | 10,000 confirmed retries; duplicate accuracy `1.0`; integrity/source `PASS` | characterization, not SLO |
| TA-P003 | 19,200 operations / 300 s / 0 errors; integrity/source `PASS` | tracemalloc disabled by control; max RSS retained |
| TA-P004 | 10/10 backup/restore; integrity/source `PASS` | local SQLite only |
| TA-P005 | 3,600 s / 16,787 operations / 59 periodic integrity checks / 0 errors | one-hour characterization, not SLO |
| rollback | 25 receipts / 0 mismatch / failed source retained | no automatic switch; next gate human |
| wheel | two builds byte-identical, `sha256:03190078…155af9` | no publication or release |
| isolated install | `PASS`; 47 pinned OTel mappings readable | no deployment |

## Observer-effect Closure（观测器效应关闭）

predecessor QEMU amd64 `TA-P003` 的 426 个 `TA_STORAGE_UNAVAILABLE` 没有在本次原生运行
复现。本次 32-worker run 完成 19,200 operations，errors `{}`，SQLite integrity `PASS`，
`python_allocation_tracing=false`，`python_tracemalloc_peak_bytes=null`，且 process max RSS 仍保留。
这关闭当前 source 的 observer-effect 平台 blocker，不证明生产并发容量。

## Failure Preservation（失败保留）

首次 focused-test 编排因不兼容的 unittest `-t` 参数在执行测试前失败；纠正仅删除该参数。
TA-P003 成功负载后的首次摘要脚本取错字段而失败，既有 JSON/receipt 未重跑、未覆盖。两次
validator 编排分别在本地 shell quoting 和未附加容器 stdin 阶段未执行；最终执行结果保留
为 30 pass + 5 expected fail closed。详情见
[`attempt-history.json`](raw/linux-x86_64-native-43382e4274c1/attempt-history.json)。

## Agent Recommendation（智能体建议）

```text
verdict=CONDITIONALLY_RECOMMENDED
recommended_as=CURRENT_SOURCE_OFFLINE_TELEMETRY_ADMISSION_REFERENCE_SLICE_WITH_NATIVE_LINUX_X86_64_DIRECT_VALIDATION
next_recommended_gate=REMOTE_RECEIPT_ATTESTATION_THEN_HUMAN_SECURITY_REVIEW
not_recommended_as=PR_G2A_APPROVED_FULL_PR_G2_PRODUCTION_SERVICE_SLO_HA_OR_DURABILITY_EVIDENCE
```

如果潜在 Agent 开发者需要 OpenTelemetry-aligned、离线、可追溯且已有原生 Linux x86_64
直接验证的 Telemetry Admission 参考切片，我会条件推荐；如果需求包含 listener、Collector、
production persistence、HA、SLO、自动治理或已批准生产服务，我不会推荐当前切片满足该需求。

## Next Required Action（下一必需动作）

1. 提交并推送本 native receipt；
2. 从 GitHub 远端 clean clone 复验并在 DBA 形成 non-self-referential attestation；
3. 完成独立 Human Security Review；
4. 再重新评估是否可把 `PR_G2A_READY_FOR_HUMAN_REVIEW` 置为 `true`；
5. 只有明确 Human Decision 才能改变 `PR_G2A_HUMAN_REVIEW_APPROVED`。

本报告不创建 PR、不合并、不修改 main、不发布、不部署，也不创建 Collector、listener、
production database、Agent、DBOS Runtime、Entity、Permission、canonical Evidence 或 SAEE output。
