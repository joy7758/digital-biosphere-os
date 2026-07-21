# Basic Object Example（基础对象示例）

本目录展示最小本地流程：创建 Synthetic Entity Object（合成实体对象表示），然后通过 DBOS Validator（DBOS 验证器）得到 `ValidationResult`（验证结果）。

它不创建、登记、激活或验证真实 Entity（实体），也不创建 Agent（智能体）、Runtime（运行时）或 Permission（权限）。

从仓库根目录运行：

```bash
python3 examples/basic_object/create_entity_object.py
python3 examples/basic_object/validate_object.py
python3 examples/basic_object/negative/validate_negative_cases.py
```

预期结果：

- `create_entity_object.py` 输出一个 `object_type=ENTITY` 的 JSON（JavaScript 对象表示法）对象表示；
- `validate_object.py` 输出九字段验证结果，`result=PASS`；
- 负向脚本依次输出 `FAIL`、`FAIL`、`VERSION_MISMATCH`，自身退出码为 `0` 表示三种拒绝均符合预期。

`PASS` 只表示本地结构与治理约束通过，不表示来源真实、身份已验证、实体已激活或权限已授予。

完整说明见 [`../../docs/developer-quickstart.md`](../../docs/developer-quickstart.md)。
