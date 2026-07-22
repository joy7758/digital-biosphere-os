# Linux arm64 DQ-018 Reference Validation Raw Artifacts

```text
implementation_source_commit=57c7b9e55dfcab84e81e7c5f61e9d8ea61045dbe
implementation_manifest=sha256:d0951d6c6252109261f7d2806082b850741df3d1decc4ff5c6418602dff69710
environment=CPython-3.12.13 Linux-glibc-arm64
result=PASS_REFERENCE_VALIDATION_NOT_SLO_NOT_GATE_APPROVAL
production_ready=false
```

## Reading Order（读取顺序）

1. `source-manifest.json`、`environment.json`：精确源码与环境；
2. `all-tests.json`：533 个测试及 16 个目录的逐目录结果；
3. `validator-summary.txt`、`validator-results.txt`：30 `PASS`、5 个外部来源
   fail closed、0 unexpected failures；
4. `telemetry_admission_validator.txt`：25/25 直接验证结果；
5. `ruff.json`、`ruff-format.txt`、`bandit.json`、`pip-audit.json`：静态质量和依赖安全；
6. `TA-P001.json`—`TA-P005.json` 及相应 `.receipt.json`：不可覆盖负载结果与哈希回执；
7. `validator-summary.txt` 中的五个外部来源 failure classes（失败类别）是规范结果；含
   host-specific absolute paths（主机绝对路径）的详细原始输出仅保留在隔离验证目录，
   不进入 Git 回执包。

`runtime-lock-install.txt`、`build-lock-install.txt` 和 `pip-check.txt` 保留锁定安装路径。

这些文件是 synthetic offline validation（合成离线验证）产物，不是 canonical Evidence、
SLO、生产容量、PR-G2A 批准、发布或部署授权。报告提交是实现提交的后继回执，不属于被测
implementation manifest。
