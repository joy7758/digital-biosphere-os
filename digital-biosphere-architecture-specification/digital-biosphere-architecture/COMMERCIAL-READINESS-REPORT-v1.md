# TITMAS Commercial Readiness Report v1

## Executive result

```text
D29_STATUS=IN_PROGRESS_BLOCKED
COMMERCIAL_MODEL_COMPLETE=false
COMMERCIAL_PRIVATE_PILOT_READY=false
PAID_MONITOR_PILOT_AVAILABLE=false
PRODUCTION_READY=false
CUSTOMERS_VERIFIED=0
```

TITMAS 已形成四产品、四 Offering 草案、商业网站源码、私有平台候选、商业控制台参考、定价模型、17 个合同草案、支持/入驻/退出流程和 12 项售前材料。它仍不能通过中国境内 B2B 合同开始收费，因为主体、开票、律师、价格、独立安全评价、第二责任人和线上入口闸门未关闭。

## Product and architecture

- 产品表面：Gate、Receipt、Audit、Health；Observer 不是第五产品。
- 首个付费候选：Monitor Pilot；当前 `ENFORCEMENT_EFFECT=NONE`，尚不可售。
- 私有平台：`joy7758/titmas-sandbox-gateway` main `1a065f1702e355d5f5ed566bdfd3e895cdca2540`。
- 当前公网技术候选返回 HTTP 200，但运行发布仍为 `efdfc844...`，并明确 `commercial_technical_ready=false`、`security_tests_pass=false`、`agent_e2e_ready=false`。
- D29 商业网站源码已合并；实时商业 JSON 与路由仍为 404，未部署状态已保留。
- PR #51 已把 Tenant/Workspace/Agent 绑定的 Receipt read 与持久 Audit/Health 读投影合并到私有平台；三项 CI 通过。其初始 PostgreSQL Audit 只承诺带缺口披露的 Tenant subset；该历史限制已由后续 PR #54 的有界 Workspace 导出取代。PR #52 只增加安全工程闸门映射、机器合同和回归测试，不改变 Runtime、数据库、API 或部署。

PR #53 进一步补齐离线持久化凭据轮换和撤销：保持 Tenant、Agent、
Quota、Scope 与 operation boundary，且通过临时 PostgreSQL CI。PR #54
随后验证完整的声明 Workspace Audit 范围和全部 Tenant 链路见证，并关闭
该有界 Audit High finding。它仍不披露其他 Workspace 事件内容，也不提供
离线排除事件非成员关系的密码学证明或外部锚点；没有增加网络管理接口、
客户自助流程、Schema、迁移或部署。

PR #56 增加事件与回滚演练的机器可读准备契约。PR #57 修复加密备份输入，
PR #58 随后绑定 Human Decision 并执行有界事件与正式回滚演练。两个 High
finding 已由运行证据关闭，临时执行权限已撤销。CR-01 仍为
`FAIL_RETAINED`，安全闸门保持 `FAIL_CLOSED_RETAINED_CR01_LIMITATION`。

PR #55 又在既有离线管理员和既有 PostgreSQL 表上实现有界 Workspace 删除
请求、双人执行、独立验证以及 7/30/90 天托管保留策略。它撤销 Workspace
凭据与授权、清除可变客户引用，并把 Gate Decision、signed Receipt、Audit
chain、usage/billing preview 和 security event 保留为显式完整性、法律或安全
例外；原始客户内容本来就不持久化。该能力只在源码与临时 PostgreSQL CI
通过，尚未部署，也不创建客户自助删除承诺。

## Security

内部安全工程闸门已对 20 项控制完成显式映射：18 `PASS`、1 `FAIL_RETAINED`、1 `NOT_APPLICABLE`。当前开放 Blocker/High finding 均为 0，但 CR-01 以失败保留处置存在，因此闸门仍为 `FAIL_CLOSED_RETAINED_CR01_LIMITATION`，不是完整安全 PASS。脱敏独立安全评价 Kit 已齐备，可标记 `READY_TO_INVITE_NOT_EXECUTED`；尚未指派或联系评价者。Signed Receipt 与历史 D04/CR01 失败继续保留，未重开或改写。

## China legal and business applicability

适用性矩阵、数据流、个人信息、跨境、生成式 AI、ICP/VATS、电子签名、密码和 MLPS 文件已存在，但全部保留 Human 专业审查边界：

```text
ICP_STATUS=DISPLAYED_NOT_AUTHORITY_VERIFIED
VATS_APPLICABILITY=HUMAN_LEGAL_REVIEW_REQUIRED
CROSS_BORDER=NOT_ASSESSED
MLPS_LEVEL=NOT_ASSESSED
HUMAN_LEGAL_REVIEW_STATUS=NOT_COMPLETE
```

经营主体、统一社会信用代码、经营范围、对公账户、税务、开票能力、公章和财务联系人均未核验。网站名称或 GitHub Owner 不得替代工商事实。

## Pricing and contracts

- 人民币成本模型、单位经济模型和 Conservative/Reference/Premium 结构已形成；实际成本和价格为空。
- `PRICING_HUMAN_APPROVED=false`、`PUBLIC_PRICE=false`。
- 17 个合同草案齐备，并统一声明 `DRAFT_NOT_LEGAL_ADVICE=true`、`CHINESE_COUNSEL_REVIEW_REQUIRED=true`。
- Monitor SOW 未经 Human 批准；无合同被发送、签署或盖章。

## Deployment and support

现有百度云资源只能视为受控技术候选，不是生产服务。客户 VPC、本地和隔离部署仍处于参考设计或未完成状态。`human:zhangbin` 已被指派为 Support Owner 与 Security Contact；第二责任人仍未指派，且未形成对外 SLA 或 Pilot Support Commitment。

## External Agent validation

新验证运行了 12 个 API 会话，其中 10 个通过角色与结构要求，覆盖 4 个有效 Provider、5 个有效模型家族和 3 个脱敏入口表面。原 Developer Schema 与 Competitive Response 类型失败被保留，C2/H2 独立会话通过修复验证。

该结果证明预部署材料能支持多模型理解、边界识别、Schema 生成、竞争性放弃和对抗请求拒绝；不证明真实公网发现。redcrag.cn 新商业入口仍为 404，因此准确状态是：

`MULTI_AGENT_COMMERCIAL_VALIDATION=PASS_WITH_LIMITATIONS_PREDEPLOYMENT`。

## Known limitations and commercial blockers

1. 主体和开票未核验；
2. 中国律师审查未完成；
3. 定价与 SOW 未获 Human 批准；
4. Support Owner 与 Security Contact 集中于同一人，第二责任人未指派；
5. CR-01 仍为 `FAIL_RETAINED`，独立安全评价未执行；
6. 新商业入口未部署，真实公网 Agent discovery 未证明；
7. 独立安全评价尚未执行；
8. 无客户、付款、真实生产数据、正式采用或认证证据。

## Non-claims

Receipt ≠ Truth；Verification ≠ Authorization；Monitor ≠ Enforce；Agent recommendation ≠ Human decision；文档、测试、CI、公开 Proof 和 10 个模型会话均不等于商业可用、生产就绪、客户采用、法律合规或认证。

## Rollback

本阶段执行了有界服务停止/恢复、不可变 release 回滚/前滚和 Nginx
rate-limit 配置纠偏；原应用 release 已恢复，数据库、Receipt、Quota、D04 与
P0-10 均未改变。源码文档可通过对应 Git merge revert 回退；运行配置需按已
保留的 pre-D29 Nginx 片段单独回退，原始失败会话必须继续保留。

## Next Human decisions

1. 核验中国经营主体和开票能力；
2. 指派第二名 Support/Security Backup Owner；
3. 提供真实成本输入并批准价格；
4. 完成中国律师审查；
5. 完成独立安全评价并继续保留 CR-01 failed-retained 边界；
6. 单独授权网站商业路由部署；
7. 在上述 Gate 通过后批准一份客户特定 Monitor Pilot SOW。
