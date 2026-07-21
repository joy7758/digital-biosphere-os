# Negative Validation Examples（负向验证示例）

`validate_negative_cases.py` 构造三份只存在于内存中的故意错误表示：

1. Capability Object（能力对象）包含禁止的 `permission` 字段，结果必须为 `FAIL`；
2. Entity Object（实体对象）包含未声明字段，结果必须为 `FAIL`；
3. 对象契约版本为 `v9.9`，结果必须为 `VERSION_MISMATCH`。

这些表示不是登记记录，不会创建 Permission（权限）、Entity（实体）或历史 Evidence（证据）。脚本只用于证明 Validator（验证器）失败关闭。
