# TITMAS Gate 产品说明

Gate 将声明动作与 `principal_ref`、`agent_ref`、`workspace_ref`、策略版本、授权版本、证据摘要、幂等键和有效期绑定。

## Monitor

输出 `WOULD_ALLOW`、`WOULD_BLOCK`、`WOULD_NEED_APPROVAL` 或 `NOT_ASSESSED`；不改变客户系统，不阻断，不执行。

## Enforce

只有客户特定书面范围、审批链、回滚、紧急停止和验收全部满足后，才可输出 `ALLOW`、`BLOCK`、`NEEDS_APPROVAL` 或 `NOT_ASSESSED`。默认 `NOT_ASSESSED -> BLOCK_OR_HOLD`。

Gate 不是结果正确性、合法性或安全性证明，也不替代客户现有身份和授权系统。
