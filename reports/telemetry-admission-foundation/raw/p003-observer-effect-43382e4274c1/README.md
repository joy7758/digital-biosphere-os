# TA-P003 Observer-effect Hardening Raw Result

```text
source_commit=23c8f0878058f29e733b6f164572ac157c6c7d1c
source_manifest=sha256:43382e4274c19ef6b10ee6e76f36ddddc18f05b7dfaedfdca43ddd8d3f2abc8c
measurement_contract_revision=0.1.1
measurement_contract_digest=sha256:80f37f4ec370b84f71da2615f43d170ecbb76f2fc296df93078be18941bf9fe6
execution_mode=EMULATED_LINUX_AMD64_ON_ARM64_HOST
p003_result=PASS_EMULATED_AMD64
native_linux_x86_64_validated=false
production_ready=false
```

[`TA-P003.tmpfs.json`](TA-P003.tmpfs.json) 是修正后 32-worker、300 秒、target 64 ops/s
在 Linux tmpfs 中产生的完整机器结果：

- 18,953 operations；
- errors `{}`；
- 63.076 observed ops/s；
- p95 276.034ms；
- integrity/source binding `PASS/PASS`；
- 原始结果文件 29,092 bytes、mode `0600`、拒绝覆盖；
- `sha256:da031f6446fa9041e354ab7458a0f65197b88ca3b2c631a4d3eff52533ec9142`。

Git 公开安全副本使用普通仓库文件权限，但字节和 SHA-256 与原始 `0600` 文件一致。该文件
包含相对源码路径、公开 commit、环境和合成指标；公开安全扫描未发现用户主目录、凭据、
真实客户数据或真实遥测内容。

这是 synthetic offline characterization（合成离线表征），不是 canonical Evidence、原生
x86_64 验证、容量 SLO、PR-G2A 批准、部署或生产就绪声明。
