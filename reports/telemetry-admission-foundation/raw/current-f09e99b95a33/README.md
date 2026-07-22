# Current Telemetry Admission Load Results

```text
result_semantics=CHARACTERIZATION_NOT_SLO
implementation_manifest=sha256:f09e99b95a3332d40abc933eaee35ea8a646b11d330ffaa5213ee0bb28f339b4
source_binding_result=5/5 PASS
source_stable_during_run=true
canonical_evidence=false
production_ready=false
```

这五个 JSON 是 DQ-018 离线 SQLite reference backend（参考后端）的原始负载表征
工件。每个文件都记录运行开始和结束时的完整 implementation manifest；两端摘要一致
才返回成功。工具以 `0o600` 创建文件并拒绝覆盖既有目标。

| case | SHA-256 | integrity | source binding |
|---|---|---|---|
| `TA-P001` | `bc9d97dc7627a71256362ba1b4773a5e0832a57e3d9a9a8ce267f2795c3b018e` | `PASS` | `PASS` |
| `TA-P002` | `92d8c5c362eb2c790c2d117ef99e994bd7970822a5137b25f4bb2c6444f64705` | `PASS` | `PASS` |
| `TA-P003` | `8650c4805127db373dcb83d31bd528c6bd7899eaf94ef04b370e7f4ffc80eb3f` | `PASS` | `PASS` |
| `TA-P004` | `0981676d5f9fd2a7c0f3eb6fab56e49c77997af610adf9e1b4308ee75045b81b` | `PASS` | `PASS` |
| `TA-P005` | `14dfdbada26bc60e32c77f510a11362ba3d2fbb523e68c695089bfbabf0f0536` | `PASS` | `PASS` |

这些结果不是吞吐、延迟或容量 SLO，不是 canonical DBOS Evidence，不批准 PR-G2，
也不创建 Agent、Runtime、Entity、Capability、Permission、Execution、Evidence、
Verification、Collector、network endpoint 或 SAEE result。
