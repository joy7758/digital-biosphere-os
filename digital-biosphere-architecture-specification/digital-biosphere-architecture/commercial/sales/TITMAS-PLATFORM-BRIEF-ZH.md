# TITMAS 平台说明

## 定位

TITMAS 不是 Agent Framework、通用授权平台、可观测平台、AI 防火墙或认证机构。它复用现有身份、证据、策略、回执、审计和运行边界，提供跨 Agent/Runtime 的行动控制与证据互操作组合层。

## 逻辑链路

```text
Agent / Application
  -> Enforcement Adapter
  -> Gate (Monitor or Enforce)
  -> Customer Action System
  -> Receipt
  -> Audit and Health
```

客户原始内容默认留在客户环境；管理面只接收经批准的最小元数据。公共发现与 Proof 不开放私有核心、策略引擎、攻击材料或客户数据。

## 适合

- 需要关键行动前置检查和明确 Human Authority 的软件团队；
- 需要跨 Agent/Runtime 统一回执与审计的 AI SaaS 或自动化团队；
- 先 Monitor、后客户特定 Enforce 的有界试点。

## 不适合

只需要 Trace 调试、通用 RBAC/ABAC、提示词安全、Agent 编排或正式认证的团队，应优先选择相应专业产品。
