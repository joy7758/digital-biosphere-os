# Linux amd64 Emulated Compatibility Raw Artifacts

```text
implementation_source_commit=d62b411845b18af3ec79af67622666e96d1baed3
implementation_manifest=sha256:6d1bcbbfc2cba1add823d390e013d4c755047f1147e338a0a59bf8e4bac0d6e4
execution_mode=EMULATED_LINUX_AMD64_ON_ARM64_HOST
result=PARTIAL_COMPATIBILITY_VALIDATION_NOT_NATIVE_NOT_SLO_NOT_GATE_APPROVAL
production_ready=false
```

## Reading Order（读取顺序）

1. `source-manifest.json`、`environment.json`：精确源码与模拟环境；
2. `all-tests.json`、`focused-telemetry-tests.json`：534 个全量测试与 200 个 Telemetry
   Admission 测试；
3. `validator-summary.txt`、`validator-results.txt`：30 `PASS`、5 个外部来源
   fail closed、0 unexpected failures；
4. `telemetry_admission_validator.txt`：25/25 直接验证；
5. `ruff.json`、`ruff-format.txt`、`bandit.json`、`pip-audit.json`：静态质量与依赖安全；
6. `TA-P001.json`—`TA-P005.json` 及对应 receipt：不可覆盖的负载结果与哈希回执。

`TA-P001`、`TA-P002`、`TA-P004` 和 `TA-P005` 的 integrity/source binding 为 `PASS`。
`TA-P003` 虽保持 integrity/source binding `PASS`，但在 QEMU 模拟下记录 426 个
`TA_STORAGE_UNAVAILABLE`，因此整套负载结果是 `PARTIAL`，不是 x86_64 原生平台通过。

五个依赖外部规范来源的 validator 详细输出含开发机绝对路径，只保留在隔离验证目录，
不进入 Git。这里保留其失败关闭分类和汇总，不把它们改写为 `PASS`。

这些文件是 synthetic offline compatibility material（合成离线兼容材料），不是 canonical
Evidence、SLO、生产容量、原生平台验证、PR-G2A 批准、发布、部署或生产就绪声明。
