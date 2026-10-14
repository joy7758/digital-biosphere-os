---
report_id: DBA-WEB-DEPLOY-004
title: TITMAS Infrastructure Developer Community Public Website Deployment Report
title_zh: TITMAS 可信多智能体基础设施开发者社区公开网站部署报告
status: pass-titmas-community-homepage-synchronized-community-not-established
observed_at: 2026-07-23T22:02:46+08:00
public_url: https://redcrag.cn/
github_release_url: https://github.com/joy7758/digital-biosphere-architecture-specification/releases/tag/v0.1-developer-preview
github_release_tag: v0.1-developer-preview
host: 180.76.115.193
current_validated_source_revision: 2d3fa4bea19cd64b4ff4656dfdba5f01922397e0
deployment_state: developer-preview-v0.1-released
developer_preview_released: true
technical_validation_design_complete: true
technical_validation_pilot_execution_authorized: false
complete_vertical_slice_executed: false
titmas_community_direction_adopted: true
titmas_contributor_entry_prepared: true
titmas_public_contribution_surface_authorized: false
titmas_developer_community_established: false
titmas_foundation_in_scope: false
production_ready: false
agent_created: false
runtime_created: false
permission_created: false
---

# TITMAS Infrastructure Developer Community Public Website Deployment Report

## Conclusion（结论）

`https://redcrag.cn/` 已从 immutable Baidu Cloud release directory（百度云不可变
发布目录）提供以 TITMAS Infrastructure Developer Community 为第一身份的中英文、
agent-readable（智能体可读）正式静态站点。首页首先解释社区使命、共同建设表面、
目标参与者和当前治理状态，再呈现 DBA／DBOS／SAEE 架构及 Technical Validation
Pilot。国内访问者不依赖 GitHub 即可获得同等核心信息。

```text
PUBLIC_WEBSITE_DEPLOYED=true
PUBLIC_WEBSITE_HEALTH_PASS=true
PUBLIC_WEBSITE_SECURITY_HEADERS_PASS=true
PUBLIC_WEBSITE_ROLLBACK_TARGET_PRESERVED=true
DEVELOPER_PREVIEW_RELEASED=true
TITMAS_INFRASTRUCTURE_DEVELOPER_COMMUNITY_DIRECTION_ADOPTED=true
TITMAS_CONTRIBUTOR_ENTRY_PREPARED=true
TITMAS_PUBLIC_CONTRIBUTION_SURFACE_AUTHORIZED=false
TITMAS_DEVELOPER_COMMUNITY_ESTABLISHED=false
TITMAS_FOUNDATION_IN_SCOPE=false
TITMAS_TECHNICAL_VALIDATION_DESIGN_COMPLETE=true
TITMAS_PILOT_EXECUTION_AUTHORIZED=false
COMPLETE_VERTICAL_SLICE_EXECUTED=false
PRODUCTION_READY=false
```

正式发布不等于生产 Runtime、客户采用、Permission、Agent 或 Digital Entity 实例。

## Published routes（公开入口）

以下 14 个入口在正式切换后返回 HTTP `200`：

| Route | Role |
|---|---|
| `/` | 中文首页 |
| `/en/` | English home |
| `/status/` | 中文状态页 |
| `/en/status/` | English status |
| `/llms.txt` | LLM-readable project entry |
| `/agent-index.json` | Agent discovery index |
| `/status.json` | Machine-readable program status |
| `/agent-customer-package.json` | Agent recommendation and boundary package |
| `/dbos-public-package-manifest.json` | Exact DBOS wheel manifest |
| `/release.json` | Active release source and state |
| `/release-manifest.json` | SHA-256 artifact inventory |
| `/robots.txt` | Crawler policy |
| `/sitemap.xml` | Public route index |
| `/og.png` | Social preview asset |

中英文页面包含各自的正式发布标识。`release.json`、`status.json`、Agent Index 和 DBOS
manifest 的 tag、decision reference、release state 与 package URL 一致。

## Artifact integrity（工件完整性）

```text
SOURCE_REVISION=2d3fa4bea19cd64b4ff4656dfdba5f01922397e0
ACTIVE_RELEASE_DIRECTORY=/srv/tmai/releases/2d3fa4bea19cd64b4ff4656dfdba5f01922397e0
SITE_ARCHIVE_BYTES=1467693
SITE_ARCHIVE_SHA256=14ac298b3d96d5d46c100f2487c68acd06b6e0816da79c089d28186d83d481dd
MANIFEST_FILES=21
ON_HOST_MANIFEST_PASS=true
```

正式 archive（压缩包）使用 `--no-xattrs` 构建，不包含候选包曾出现的 macOS provenance
扩展属性头。服务器逐一验证 21 个清单文件的 byte size 和 SHA-256，随后才执行原子切换。

## Transport and security（传输与安全）

- HTTP 重定向至 `https://redcrag.cn/`；
- Nginx 配置检查通过且服务为 `active`；
- HSTS、CSP、`nosniff`、frame denial、referrer policy 和 permissions policy 保留；
- 系统、SSH、证书、防火墙和安全配置未修改；
- 公网多路检查观察到多次瞬时 `SSL_ERROR_SYSCALL`，有界重试后全部通过。

## Rollback（回滚）

正式站点通过 atomic symlink switch（原子符号链接切换）激活。前一候选版本仍保留：

```text
PREVIOUS_RELEASE=/srv/tmai/releases/e087fa8f2ebc7c6fca0cbc094bf45f03e3d32d46
ROLLBACK_MECHANISM=ATOMIC_SYMLINK_SWITCH
PRIOR_ACTUAL_ROLLBACK_VALIDATION=true
```

既有候选部署曾完成实际切回和恢复；本次复用相同机制并保留精确旧目标，没有为了报告
再次制造线上回滚。

## GitHub source and release binding（GitHub 来源与发布绑定）

- Homepage source merge：`2d3fa4bea19cd64b4ff4656dfdba5f01922397e0`
- Pull request：<https://github.com/joy7758/digital-biosphere-architecture-specification/pull/16>
- 网站内容同步不创建新产品版本；Developer Preview v0.1 的既有 release identity 保持不变。

- Release：<https://github.com/joy7758/digital-biosphere-architecture-specification/releases/tag/v0.1-developer-preview>
- `draft=false`
- `prerelease=false`
- Tag commit：`1113130ca4213b70fcebd6247fec794854295e8c`
- DBOS wheel SHA-256：`edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09`
- DBOS repository visibility：`PRIVATE`

候选 tag `v0.1-public-website-candidate.7` 及更早候选版本继续作为历史记录，不被改写成
正式 Developer Preview。

## Truth boundary（事实边界）

- `OPEN_WEB_DISCOVERY=PARTIAL_METADATA_ONLY`；
- `R-015` 为 0 critical、0 high、2 disclosed moderate advisories；
- DBOS 整仓不公开，只公开 exact public-safe wheel；
- 没有公共 Runtime、托管 API、Permission grant 或生产 SLA；
- Technical Validation Pilot 只完成设计，尚未获执行授权，14 项符合性负例执行数仍为 0；
- TITMAS 开发者社区方向已采纳，贡献入口已准备，但公共贡献面未授权；
- 没有成立正式社区、建立 SIG、指派 Maintainer、采纳 Code of Conduct 或创建 Foundation；
- 第一位外部角色定义为 Reviewer；没有招募 Contributor 或声明上游采用；
- 没有创建 Agent、Runtime、Entity、Capability instance、Permission 或科研 Evidence。
