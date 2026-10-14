# Customer Onboarding Runbook / 客户入驻运行手册

`STATUS=INTERNAL_DRAFT_NO_CUSTOMER_AUTHORIZED`

```text
Lead -> Qualification -> NDA -> Data Boundary Review -> Architecture Review
-> SOW -> Security Review -> Workspace Provisioning -> Synthetic First Value
-> Monitor Integration -> Baseline -> Findings Review -> Acceptance -> Renewal or Exit
```

每一步必须记录 Human Owner、输入、退出条件、证据引用和禁止动作。任何失败或 `NOT_ASSESSED` 不得被改写为通过。

Provisioning 前至少要求：已核验合同主体、签署适用协议、批准数据边界、指定支持与安全联系人、批准价格、验证撤销路径。首个运行必须使用合成数据；真实数据需要新的书面授权。

当前状态：`CUSTOMER_ONBOARDING_AUTHORIZED=false`。
