# Historical Trusted Multi-Agent Infrastructure Website

本目录保存曾发布在 `redcrag.cn` 的中英文、agent-readable（智能体可读）Trusted
Multi-Agent Infrastructure（可信多智能体基础设施）门户源码。它现在是历史网站资产，
不再是当前公开入口；当前权威域名是 `https://dcell.net`，当前产品是红岩公文。

```text
SITE_ROLE=LEGACY_HISTORICAL_SITE_SOURCE
CURRENT_CANONICAL_DOMAIN=https://dcell.net
REDCRAG_CN_ROLE=LEGACY_HISTORICAL_DOMAIN
ACTIVE_DEPLOYMENT_AUTHORIZED=false
```

## Historical publication truth status

```text
SITE_IMPLEMENTED=true
STATIC_SITE_BUILD_PASS=true
ZH_EN_CONTENT_PARITY_PASS=true
AGENT_READABLE_ENTRY_PASS=true
SITE_DEPLOYED=true
SITE_URL=https://redcrag.cn/
SITE_HEALTH_PASS=true
SITE_ROLLBACK_VALIDATED=true
DEVELOPER_PREVIEW_RELEASED=true
CURRENT_STAGE=TITMAS_AGENT_NATIVE_COMMERCIAL_MATURITY_PROGRAM
COMMERCIAL_PROGRAM_STATUS=WAITING_FOR_HUMAN_DECISION
CR01_STATUS=BLOCKED_LEDGER_INTEGRITY
CR01_D02_STATUS=ACCEPTED_DESIGN_ONLY
LEDGER_TRANSITION_IMPLEMENTATION_AUTHORIZED=false
PUBLIC_TRIAL_INTEREST_ENTRY_ACTIVE=true
FIRST_EXTERNAL_HUMAN_DEVELOPER_TRIAL_COMPLETE=false
PUBLIC_PROTOCOL_RELEASED=false
PRODUCTION_READY=false
COMMERCIAL_PUBLIC_ENTRY_IMPLEMENTED_CANDIDATE=true
COMMERCIAL_PUBLIC_ENTRY_DEPLOYED=false
AVAILABLE_COMMERCIAL_OFFERING_COUNT=0
COMMUNITY_MATERIAL_STATUS=HISTORICAL_NON_CURRENT
```

这个目录是网站实现，不是 DBOS Runtime（运行时）、SAEE Evaluation
Runtime（评价运行时）或 Agent（智能体）实现。页面将当前项目称为
`Developer Preview v0.1`（开发者预览版 v0.1）。正式发布不构成生产可用性、
客户采用、Runtime 或 Permission 声明。

## Routes

| Route | Purpose |
|---|---|
| `/` | 中文首页 |
| `/en` | English home |
| `/status` | 中文状态页 |
| `/en/status` | English status page |
| `/llms.txt` | LLM-readable（大模型可读）项目入口 |
| `/agent-index.json` | Agent discovery（智能体发现）索引 |
| `/status.json` | 机器可读验证状态 |
| `/products/gate`, `/products/receipt`, `/products/audit`, `/products/health` | 四个公开产品信息页；不表示 Offering 可用 |
| `/monitor-pilot`, `/enforce-pilot`, `/private-evaluation`, `/design-partner` | 商业试点边界与人工入口候选 |
| `/security`, `/trust-center`, `/privacy`, `/terms` | 安全、信任、隐私和条款边界 |
| `/product-catalog.json`, `/solution-catalog.json`, `/proof-catalog.json` | Agent-readable 商业目录 |
| `/commercial-offerings.json`, `/deployment-options.json`, `/recommendation-policy.json` | Offering、部署和推荐边界 |
| `/agent-customer-package.json` | AI agent 的适用／不适用、精确验证命令、组合流和当前阻塞 |
| `/dbos-public-package-manifest.json` | DBOS exact wheel 的验证、匿名下载、公开边界和已发布状态 |
| `/downloads/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl` | 已批准 public-safe SDK 的 redcrag.cn 镜像；SHA-256 保持不变 |
| `/sdk/v0.1/manifest.json` | 七个对象 Schema、合成示例、SDK digest 和非效果边界 |
| `/sdk/v0.1/examples/synthetic-entity.json` | 可由 `dbos-validate` 本地验证的惰性合成对象 |

## Local validation

Requires Node.js `>=22.13.0`.

```bash
npm ci
npm run dev
npm test
npm run release:formal
```

`npm test` 会重新构建网站，并验证中英文入口、10 项机器事实一致性、状态边界、机器可读资源及
candidate/formal release mode（候选／正式发布模式）的失败关闭规则。
`npm run release:formal` 使用 `ADR-022`、`released_by_ref=zhangbin`、固定 tag 和
exact wheel URL 执行失败关闭的正式导出，并生成带 SHA-256 清单的 `out/` 静态部署包；该目录
被 Git 忽略，不作为源码事实提交。

正式静态导出还会检查本地链接、公开内容泄露、SDK/Schema digest 和 release
manifest。每次构建都会先清空 `dist/` 和 `.vinext/`，避免旧资源混入新的发布清单。

## Design boundary

视觉系统重度参考 OpenTelemetry 官网的明亮信息架构：白色与浅灰页面、紫色主色、
琥珀色与青色强调、清晰导航、模块化能力卡片、有限的高饱和状态区和多语言入口。
不复制其 Logo、插图、文案或项目事实。

## Commercial entry boundary

当前商业入口采用 `closed core + public discovery + bounded proof`。四产品和试点页面是静态、
双语、公开安全的信息入口；`request-access` 不包含表单后端，不创建客户、Workspace、Key、
Permission、合同、支付或部署。早期 Community 页面仅作为 `HISTORICAL_NON_CURRENT`
资料保留。该候选尚未部署，也不构成可用 Offering、客户采用、生产就绪或法律通过。

本次候选实现与验证限制记录见
[`docs/releases/d29-commercial-public-entry-candidate-v1.md`](docs/releases/d29-commercial-public-entry-candidate-v1.md)。
生产依赖与完整开发工具依赖审计均为 0 个漏洞。审计结果是时间点证据，仍不能仅凭
页面测试和依赖审计通过，把商业入口候选升级为部署授权或商业可用。

## Deployment boundary

Developer Preview v0.1 已部署到 `https://redcrag.cn/`。正式部署必须继续通过
manifest hash、Nginx、健康、安全头和回滚边界验证。Deployment（部署）不等于
Production Readiness（生产就绪）或 Adoption（采用）。
