# Native Linux x86_64 Current-source Validation Raw Artifacts

```text
implementation_source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
implementation_source_tree=27703ed64d6e885a2933a5a39139a59bab83c3c1
implementation_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
environment=CPython-3.12.13_Linux-glibc-x86_64
base_image=python:3.12.13-slim-bookworm@sha256:72d3d75f2639ab82b34b29390ad3d6e0827c775befee94edda8e9976818f488d
execution_mode=NATIVE_LINUX_X86_64_IMMUTABLE_CONTAINER_NETWORK_NONE
result=PASS_REFERENCE_VALIDATION_NOT_SLO_NOT_GATE_APPROVAL
production_ready=false
```

## Outcome（结果）

DQ-018 current source 在原生 Linux x86_64 主机上使用架构锁定的官方 Python 镜像运行。
运行依赖和构建工具均从 exact-hash wheelhouse 离线安装；测试、负载、恢复和打包容器使用
`--network none`。源码 checkout 在运行前后保持 clean，58-file implementation manifest
前后一致。

本目录是 synthetic/offline validation（合成离线验证）回执，不是 canonical Evidence、SLO、
Human Security Review、PR-G2A approval、完整 PR-G2、发布、部署或 Production Ready。

## Reading Order（读取顺序）

1. [`native-validation-summary.json`](native-validation-summary.json)：机器可读总结果与永久边界；
2. [`environment.json`](environment.json)、[`source-manifest.json`](source-manifest.json)：原生环境与精确源码字节绑定；
3. [`all-tests.json`](all-tests.json)、[`focused-telemetry-tests.txt`](focused-telemetry-tests.txt)：534/534 全仓与 200/200 遥测专项测试；
4. [`validator-aggregate.json`](validator-aggregate.json)、[`validator-summary.txt`](validator-summary.txt)：30 `PASS`、5 个外部来源缺失时 fail closed、0 unexpected；
5. [`telemetry-admission-validator.txt`](telemetry-admission-validator.txt)、[`otel-conformance.json`](otel-conformance.json)：25/25 和 OTel 授权子集 32/32 + 36/36；
6. `TA-P001.json`—`TA-P005.json` 及 `.receipt.json`：完整五项不可覆盖负载结果；
7. [`rollback-drill.json`](rollback-drill.json)：25/25 receipts、0 mismatch、失败源保留、无自动切换；
8. [`wheel-hashes.txt`](wheel-hashes.txt)、[`wheel-install-smoke.json`](wheel-install-smoke.json)：可重复 wheel 与隔离安装；
9. [`attempt-history.json`](attempt-history.json)：编排错误、纠正和不重跑既有成功负载的保留记录。

五个 federation/identity/capability/evidence validator 的详细输出包含开发机绝对路径，只保留
在隔离验证目录，不进入 Git。仓库仅保留 validator 名称、失败类别和计数，避免把主机路径
混入可公开审查包。

## Authority Boundary（权力边界）

```text
NATIVE_VALIDATION_NE_SLO=true
NATIVE_VALIDATION_NE_HUMAN_SECURITY_REVIEW=true
NATIVE_VALIDATION_NE_PR_G2A_APPROVAL=true
TELEMETRY_NE_EVIDENCE=true
EVIDENCE_NE_TRUTH=true
AGENT_CREATED=false
RUNTIME_CREATED=false
ENTITY_CREATED=false
PERMISSION_GRANTED=false
COLLECTOR_CREATED=false
LISTENER_CREATED=false
PRODUCTION_DATABASE_CREATED=false
SAEE_CALLED=false
```
