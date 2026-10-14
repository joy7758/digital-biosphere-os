# D29 Human Commercial Gate Decision Packet v1

## Purpose

本文件只把 D29 剩余商业闸门整理为可审计的人类决策包。它不替 Human Owner
作出决定，不授权报价、合同、收款、客户数据、部署、生产运行或安全认证。

```text
PACKET_STATUS=READY_FOR_HUMAN_REVIEW
D29_STATUS=IN_PROGRESS_BLOCKED
COMMERCIAL_MODEL_COMPLETE=false
COMMERCIAL_PRIVATE_PILOT_READY=false
PAID_MONITOR_PILOT_AVAILABLE=false
PRODUCTION_READY=false
```

## Verified inputs

- 四个产品表面、四份 Offering 草案、17 份合同草案、定价结构、支持、入驻、退出和
  12 项售前材料已经形成；这些均为草案，不是对外 Offer。
- 多智能体商业验证达到会话阈值：12 个 API 会话、10 个有效会话、4 个有效
  Provider、5 个模型家族和 3 个入口表面。结论仅为
  `PASS_WITH_LIMITATIONS_PREDEPLOYMENT`。
- 商业网站源码已合并，但实时商业机器入口仍返回 404；本工作未执行部署。
- 经营主体、开票能力、真实成本、价格和律师意见尚无可核验 Human 证据；
  Support Owner 与 Security Contact 已指派为 `human:zhangbin`，第二责任人未指派。
- 独立安全评价包为 `READY_TO_INVITE_NOT_EXECUTED`，尚无评价者、联系行为或
  Security PASS。
- FDO / PVS-0 仅为公开证据辅助线；2 个 Profile 是标准化候选，3 个 Demo 是
  非规范资产。它不构成产品、标准、认证或采用证明。

## Critical security blocker classification

```text
CRITICAL_FINDING_OPEN_COUNT=0
CRITICAL_FINDING_DISPOSITIONS_RETAINED=1
CRITICAL_FINDING_SOURCE=CR01_RESTORE_RECEIPT_INTEGRITY_FAILURE
RESTORED_RECEIPTS_CHECKED=1661
RESTORED_RECEIPT_SIGNATURES_VALID=1659
RESTORED_RECEIPT_SIGNATURES_INVALID=2
D04_FINAL_STATUS=CLOSED_FAILED_RETAINED
D04_REOPEN_AUTHORIZED=false
```

该阻塞来自历史实验 Ledger 的恢复验收：两个使用未保留随机公钥生成的合成 Receipt
无法完成签名验证。它不是本轮新发现的跨租户访问漏洞，也不能据此推断生产客户数据
已受影响；但它足以阻止把旧 Ledger 或当前候选叙述为可恢复的商业生产系统。

D29 不得改写历史 Receipt、重开 D04 或把 `1659/1661` 解释为完整恢复 PASS。未来若
Human Owner 选择继续，只能通过独立决定评估 clean-genesis（全新起点）生产 Ledger、
生产 Signer 和完整安全验证，不能继承旧 Ledger 的链、序列或例外。

## Human decisions required

### HG-01 — Business entity and invoice evidence

Human Owner 需提供或确认可核验的经营主体、经营范围、对公账户、税务和开票能力。
缺少证据时保持：

```text
BUSINESS_ENTITY_VERIFIED=false
INVOICE_CAPABILITY_VERIFIED=false
PAYMENT_COLLECTION_AUTHORIZED=false
```

### HG-02 — Support and security responsibility

Support Owner 与 Security Contact 已指派为 `human:zhangbin`，并记录有效期、
联系窗口与撤销方式。Backup Owner 仍需由第二名具备实际责任能力的人类接受；
Agent 不能承担合同或安全责任，单人指派不产生 SLA。

### HG-03 — Cost input and pricing approval

需提供真实基础设施、支持、交付、安全评估、税费与风险储备输入，再由 Human Finance
Owner 选择或拒绝 Pilot 价格。结构化价格选项不是报价。

### HG-04 — Chinese counsel review

需由中国执业律师审查合同包和适用性矩阵。特别覆盖主体、数据、跨境、电子签名、密码、
ICP/VATS、生成式 AI、责任限制、知识产权、终止和争议条款。当前文档不是法律意见。

### HG-05 — Blocker and High security disposition

Human Owner 必须在不重开 D04 的前提下选择：

1. 继续保持商业 Pilot 关闭；或
2. 单独授权 clean-genesis 候选和独立安全评价；或
3. 提出新的有界修复决策。

当前已完成 20 项控制映射。Gateway PR #53、#54 和 #55 的有界源码与
临时 PostgreSQL CI 先后关闭凭据生命周期、Workspace Audit、Workspace
删除和保留 findings。PR #57 修复备份前置，PR #58 执行有界事件与正式回滚
演练并关闭 2 个 High findings。当前开放 Blocker/High 均为 0，但 CR-01 控制
仍为 `FAIL_RETAINED`，闸门结果为 `FAIL_CLOSED_RETAINED_CR01_LIMITATION`；
完成处置不等于独立安全评价或商业放行。

Gateway PR #56 的准备契约由 Decision
`TITMAS-D29-SECURITY-FINDINGS-20260812-01` 使用一次。事件恢复、回滚及前滚均
低于 120 秒，精确原 release 已恢复，临时服务/回滚/Nginx 权限现已撤销。
任何未来演练仍需新的 Human Decision 与 fresh preflight。

### HG-06 — Commercial route deployment

只有单独部署决定可以把已合并源码发布到线上。部署前须记录精确 source commit、不可变
Release、回滚点、机器入口检查和安全检查。源码合并不等于部署。

### HG-07 — Customer-specific Monitor SOW

只有 HG-01 至 HG-06 满足后，才能审查一份客户特定、只读、
`ENFORCEMENT_EFFECT=NONE` 的 Monitor Pilot SOW。该决定仍不自动授权联系客户、签约、
收款、处理生产数据或 Enforce。

## Recommended order

```text
HG-01 BUSINESS_AND_INVOICE
  -> HG-02 RESPONSIBILITY
  -> HG-03 PRICING
  -> HG-04 COUNSEL
  -> HG-05 SECURITY_DISPOSITION
  -> HG-06 WEBSITE_DEPLOYMENT
  -> HG-07 CUSTOMER_SPECIFIC_MONITOR_SOW
```

顺序可以由 Human Owner 调整，但任何后置决定不得倒推前置 Gate 已通过。

## Required retained boundaries

```text
RECEIPT_NE_TRUTH=true
VERIFICATION_NE_AUTHORIZATION=true
MONITOR_NE_ENFORCE=true
AGENT_RECOMMENDATION_NE_HUMAN_DECISION=true
PUBLIC_PROOF_NE_ADOPTION=true
PVS0_NE_PRODUCT_OR_STANDARD=true
D04_MODIFIED=false
CUSTOMER_CONTACTED=false
CONTRACT_SENT_OR_SIGNED=false
PAYMENT_COLLECTED=false
CUSTOMER_DATA_PROCESSED=false
DEPLOYMENT_EXECUTED=false
```
