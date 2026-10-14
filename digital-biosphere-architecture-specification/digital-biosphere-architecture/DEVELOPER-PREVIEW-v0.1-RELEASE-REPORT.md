---
report_id: TMAI-DEVELOPER-PREVIEW-v0.1-RELEASE-REPORT
title: Trusted Multi-Agent Infrastructure Developer Preview v0.1 Release Report
title_zh: 可信多智能体基础设施开发者预览版 v0.1 发布报告
status: pass-released-not-production-ready
observed_at: 2026-07-22T03:21:54+08:00
release_decision_reference: architecture/ADR-022-developer-preview-release.md
released_by_ref: zhangbin
developer_preview_released: true
production_ready: false
---

# Trusted Multi-Agent Infrastructure Developer Preview v0.1 Release Report

## Outcome（结果）

`Trusted Multi-Agent Infrastructure Developer Preview v0.1` 已按 `ADR-022`
完成 GitHub Release（GitHub 正式发布）、DBOS exact public-safe wheel（精确公开安全安装包）
匿名复验和百度云正式静态部署。

```text
DEVELOPER_PREVIEW_RELEASED=true
RELEASE_TAG=v0.1-developer-preview
RELEASED_BY_REF=zhangbin
PRODUCTION_READY=false
CUSTOMER_ADOPTION_CLAIMED=false
```

## GitHub Release（GitHub 发布）

- Release：<https://github.com/joy7758/digital-biosphere-architecture-specification/releases/tag/v0.1-developer-preview>
- Tag：`v0.1-developer-preview`
- Tag commit：`1113130ca4213b70fcebd6247fec794854295e8c`
- Main merge commit：`95fcc363581a053acddcaf09acdeacecb62ad90d`
- `draft=false`
- `prerelease=false`
- Published at：`2026-07-21T19:18:13Z`

### Exact DBOS wheel

```text
filename=digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
bytes=45115
sha256=edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09
source_revision=cd3f867c4379ec555c45e7d554088ad12ce08a24
anonymous_download_pass=true
clean_install_pass=true
dbos_validate_entrypoint_pass=true
```

公开 URL：
<https://github.com/joy7758/digital-biosphere-architecture-specification/releases/download/v0.1-developer-preview/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl>

GitHub metadata、匿名下载后的本地 byte size（字节数）和 SHA-256 三者一致。
DBOS 整仓复核仍为 `PRIVATE`；本发布没有改变仓库可见性。

### Static website artifact（静态网站工件）

```text
filename=trusted-multi-agent-infrastructure-site-v0.1-developer-preview.tar.gz
bytes=1714734
sha256=c85dc4eb84ceb6e5210f2ecb57ebbff696eb3dad6b508184f36894aab176bb55
source_revision=1113130ca4213b70fcebd6247fec794854295e8c
anonymous_download_pass=true
macos_xattrs_in_formal_archive=false
```

## Baidu Cloud deployment（百度云部署）

```text
PUBLIC_URL=https://redcrag.cn/
HOST=180.76.115.193
ACTIVE_RELEASE=/srv/tmai/releases/1113130ca4213b70fcebd6247fec794854295e8c
PREVIOUS_RELEASE=/srv/tmai/releases/1c4bf032878193609e8f55f0ebd5606b8ebe2c1c
MANIFEST_FILES=21
ON_HOST_MANIFEST_PASS=true
NGINX_CONFIG_PASS=true
NGINX_ACTIVE=true
ATOMIC_SWITCH_PASS=true
```

13 个公开入口连续在 bounded retry（有界重试）内返回 HTTP `200`，包括中英文首页、
中英文状态页、`llms.txt`、三类 agent-readable JSON（智能体可读 JSON）、
`release.json` 和 `release-manifest.json`。`release.json` 的 source revision、tag、
release decision 和 `released_by_ref` 与 GitHub Release 一致。

公网检查观察到多次瞬时 `SSL_ERROR_SYSCALL`；有界重试后全部入口通过。该现象保留为
网络观察，不被改写为从未发生。HSTS、CSP、`nosniff` 和 frame-denial 安全头均通过。

本次使用 immutable release directory + atomic symlink switch（不可变发布目录 + 原子
符号链接切换）。旧候选目录仍在服务器，既有实际回滚验证保持有效；本次没有为了形式
重复制造一次线上回滚。

## Verification boundary（验证边界）

- `OPEN_WEB_DISCOVERY=PARTIAL_METADATA_ONLY`，只作为 v0.1 已接受限制，不是自然发现通过；
- `R-015` 保留 0 critical、0 high、2 moderate PostCSS 通告；服务器只运行静态内容；
- Agent Customer Validation 证明有界 agent-readable（智能体可读）理解，不等于客户采用；
- wheel 安装和入口可调用不等于 Runtime、Permission、Entity 或 Agent 已创建；
- Evidence 不等于 Truth；Evaluation 不等于 Authority。

```text
AGENT_CREATED=0
RUNTIME_CREATED=0
ENTITY_INSTANCE_CREATED=0
CAPABILITY_INSTANCE_CREATED=0
PERMISSION_CREATED=0
RESEARCH_EXECUTION_CREATED=0
```

## Next gate（下一闸门）

发布后只进入 observation（观察）、发现性复查、匿名安装反馈和复用信号收集。任何
生产部署、托管 Runtime、Permission、Agent 实例或 DBOS 整仓公开均需新的明确决策，
不能从 `DQ-009` 或 `DQ-016` 自动推导。
