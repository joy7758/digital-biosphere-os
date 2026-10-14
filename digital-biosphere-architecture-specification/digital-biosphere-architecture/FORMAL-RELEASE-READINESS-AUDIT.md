---
report_id: DBA-FORMAL-RELEASE-READINESS-AUDIT-2026-07-22
title: Trusted Multi-Agent Infrastructure Formal Release Audit
title_zh: 可信多智能体基础设施正式发布审计
status: pass-release-executed-with-disclosed-limitations
observed_at: 2026-07-22T03:21:54+08:00
formal_release_ready: true
release_authorized: true
developer_preview_released: true
production_ready: false
---

# Formal Release Audit（正式发布审计）

## Outcome（结果）

`ADR-022` 授权的 TMAI Developer Preview v0.1 发布交易已完成。GitHub Release、exact
DBOS wheel（精确 DBOS 安装包）、百度云正式站点和公开机器真相表面均通过外部复验。

```text
TRUSTED_MULTI_AGENT_INFRASTRUCTURE_DEVELOPER_PREVIEW_RELEASED=true
FORMAL_RELEASE_READY=true
RELEASE_AUTHORIZED=true
RELEASE_EXECUTED=true
PRODUCTION_READY=false
RELEASE_DECISION_REF=architecture/ADR-022-developer-preview-release.md
RELEASED_BY_REF=zhangbin
```

## Requirement audit（要求审计）

| Requirement | Authoritative evidence | Result |
|---|---|---|
| Human release decision | `ADR-022`；`released_by_ref=zhangbin` | `PASS` |
| DBA public source | Public `main@95fcc363581a053acddcaf09acdeacecb62ad90d` | `PASS` |
| GitHub formal Release | `v0.1-developer-preview`；non-draft；non-prerelease | `PASS` |
| Release source binding | Annotated tag peels to `1113130ca4213b70fcebd6247fec794854295e8c` | `PASS` |
| DBOS exact wheel | 45115 bytes；SHA-256 `edf92e…8f09` | `PASS` |
| Anonymous wheel access | Public URL download、bytes 和 SHA-256 | `PASS` |
| Clean wheel install | Fresh venv；`dbos-validate --help` | `PASS` |
| DBOS whole repository | GitHub visibility remains `PRIVATE` | `PASS_BOUNDARY_PRESERVED` |
| Static website artifact | 1714734 bytes；SHA-256 `c85dc4…bb55` | `PASS` |
| Baidu Cloud activation | `/srv/tmai/releases/1113130…`；atomic switch | `PASS` |
| On-host artifact integrity | 21/21 manifest entries | `PASS` |
| Public routes | 14/14 routes HTTP 200 with bounded retry | `PASS_WITH_TRANSIENT_TLS_OBSERVED` |
| Bilingual release markers | Chinese and English release wording | `PASS` |
| Agent-readable truth surfaces | `llms.txt`、Agent Index、status、DBOS manifest | `PASS` |
| HTTPS and security headers | HSTS、CSP、nosniff、frame denial | `PASS` |
| Rollback continuity | Previous immutable target preserved；prior actual rollback valid | `PASS` |
| Website dependency audit | 0 critical、0 high、2 moderate；static-only deployment | `PASS_WITH_BOUNDED_RESIDUAL` |
| Open-web discovery | Canonical-name discovery still absent | `PARTIAL_METADATA_ONLY_ACCEPTED_FOR_V0_1` |
| SAEE ↔ DBOS adapter | Frozen public read-only advisory path | `PASS_ADVISORY_ONLY` |
| Agent customer validation rerun | 12/12 sessions；0 failed thresholds | `PASS_NOT_CUSTOMER_ADOPTION` |

## Preserved limitations（保留限制）

1. `PARTIAL_METADATA_ONLY` 没有升级为 canonical-name discovery（规范名称自然发现）通过；
2. DBOS 整仓保持 `PRIVATE`，GitHub Release 只分发有界 wheel；
3. 没有公共 Runtime、托管 API、Permission 或生产 SLA；
4. 网站构建依赖保留 2 个 moderate PostCSS advisories，服务器不运行该构建树；
5. 公网复验出现两次瞬时 TLS 连接错误，有界重试后全套检查通过；
6. Agent API 验证不等于客户采用、market fit（市场匹配）或生产推荐。

## Non-effects（非效果）

本发布没有创建 Agent、Runtime、Digital Entity instance、Capability instance、Permission、
科研执行或 Evidence Truth。Release 不授权未来实现、生产部署或 DBOS 仓库公开。

完整执行证据见
[`DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md`](DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT.md)
和 [`PUBLIC-WEBSITE-DEPLOYMENT-REPORT.md`](PUBLIC-WEBSITE-DEPLOYMENT-REPORT.md)。
