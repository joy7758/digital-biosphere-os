# DBOS Validation Result Boundary Rules v0.1（DBOS 验证结果边界规则 v0.1）

状态：`FROZEN_FOR_SPECIFICATION`

## 1. Purpose（目的）

本规则冻结 Validation Result（验证结果）的无权力、无执行、无历史改写边界。任何未来 SDK、API、Adapter 或存储层都必须保留这些边界。

## 2. Prohibited Derivations（禁止推导）

| 输入状态或对象 | 禁止推导 |
|---|---|
| `PASS` | Permission、Authorization、Capability Grant、Entity Activation、Verification Approval |
| `FAIL` | Historical deletion（历史删除）、输入修复、Evidence 覆盖、旧结果替换 |
| `UNKNOWN` | 默认成功、不存在结论、低风险结论、隐式允许 |
| `CONFLICT` | 自动合并、自动选择最新或最相似候选 |
| `VERSION_MISMATCH` | 自动升级、降级、迁移或选择 `latest` |
| Validation Error | 自动补丁、命令执行、权限请求 |
| Validation Warning | 主状态升级、审计豁免、真实性结论 |
| Validation Result | Entity、Agent、Runtime、Event、Evidence、Permission 或 SAEE Evolution |

## 3. Required Non-effects（必须无效果）

每个 Result consumer（结果消费者）必须保持：

```text
authority_effect=NONE
permission_effect=NONE
authorization_effect=NONE
capability_grant_effect=NONE
entity_creation_effect=NONE
execution_effect=NONE
history_rewrite_effect=NONE
saee_effect=NONE
```

这些是治理不变量，不要求把效果字段加入 ValidationResult Object；不得通过省略字段绕过规则。

## 4. Consumer Rules（消费者规则）

允许消费者：

- 展示结果；
- 按 `result` 分类；
- 链接对应 Schema 和目标引用；
- 保存追加式诊断；
- 请求人工补充信息；
- 在调用方自己的流程中选择停止。

禁止消费者：

- 因 `PASS` 调用受限工具；
- 因 `FAIL` 修改或删除目标；
- 因 `UNKNOWN` 使用默认权限；
- 因 `CONFLICT` 静默挑选一个身份；
- 因提示存在而自动运行修复；
- 把结果解释为独立 Verification、Certification 或 Truth。

## 5. Negative Boundary Cases（负向边界案例）

v0.1 测试至少必须拒绝或证明不存在：

1. Result 创建 Permission；
2. Result 创建 Entity；
3. Result 触发 Execution；
4. Result 调用 SAEE；
5. `PASS` 自动形成 Authorization；
6. `FAIL` 修改输入或历史；
7. `UNKNOWN` 自动变成 `PASS`；
8. `resolution_hint` 变成可执行修复命令。

## 6. Current State（当前状态）

```text
RESULT_NE_AUTHORITY=true
PASS_NE_AUTHORIZATION=true
FAIL_NE_HISTORY_REWRITE=true
UNKNOWN_NE_DEFAULT_SUCCESS=true
VALIDATION_NE_PERMISSION=true
RESULT_EXECUTION_EFFECT=NONE
RESULT_ENTITY_CREATION_EFFECT=NONE
RESULT_SAEE_EFFECT=NONE
```
