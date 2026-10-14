---
document_id: TMAI-DEVELOPER-PREVIEW-v0.1-RELEASE-NOTES
title: Trusted Multi-Agent Infrastructure Developer Preview v0.1 Release Notes
title_zh: 可信多智能体基础设施开发者预览版 v0.1 发布说明
status: released-developer-preview-not-production-ready
release_tag: v0.1-developer-preview
released_by_ref: zhangbin
decision_reference: architecture/ADR-022-developer-preview-release.md
release_date: 2026-07-22
---

# Trusted Multi-Agent Infrastructure Developer Preview v0.1

中文：可信多智能体基础设施开发者预览版 v0.1。

## Release scope（发布范围）

本版本公开：

- DBA Program Governance and Architecture Specification（项目群治理与架构规范）；
- 中英文、agent-readable（智能体可读）的 `https://redcrag.cn/` 门户；
- DBOS exact public-safe wheel（精确公开安全安装包）；
- SAEE 的 public-safe read-only evaluation surface（公开安全只读评价表面）；
- Agent Customer Validation、Clean Clone、公开发现观察和边界证据。

它不是 Agent Platform、Runtime、Permission System、生产 API、客户采用或生产就绪版本。

## Exact DBOS artifact（精确 DBOS 产物）

```text
package_id=TMAI-DBOS-WHEEL-CANDIDATE-20260722-001
source_revision=cd3f867c4379ec555c45e7d554088ad12ce08a24
filename=digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
bytes=45115
sha256=edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09
```

下载地址：

<https://github.com/joy7758/digital-biosphere-architecture-specification/releases/download/v0.1-developer-preview/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl>

DBOS 整仓继续为 `PRIVATE`。本发布没有公开 registry、evidence、reports、tests、tools
或包含本机绝对路径的历史材料。

### Verify and install（校验与安装）

```bash
curl -fL -o digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl \
  https://github.com/joy7758/digital-biosphere-architecture-specification/releases/download/v0.1-developer-preview/digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
printf '%s  %s\n' \
  edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09 \
  digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl | shasum -a 256 -c -
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install ./digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl
dbos-validate --help
```

安装不会创建 Agent、Runtime、Entity、Capability、Permission、Evidence Truth 或授权。

### Frozen metadata note（冻结元数据说明）

exact wheel 在发布授权前完成冻结，因此其内嵌 README 和 package summary 仍使用
`candidate` / `not published` 的构建时措辞。为保持 ADR-022 授权的精确 hash，不重建或
静默改写该 wheel。当前发布状态以本说明、GitHub Release、`status.json` 和
`dbos-public-package-manifest.json` 为准。

## Validated evidence（已验证证据）

- DBOS source tests：`334/334 PASS`；
- DBOS validators：`34/34 PASS`；
- wheel Gitleaks findings：`0`；
- wheel absolute user-path matches：`0`；
- clean wheel install and installed validation：`PASS`；
- SAEE read-only Adapter：`8/8 PASS`；
- Agent Customer Validation rerun：`12/12 sessions`、`0 failed thresholds`；
- authority safety failures：`0`；
- 百度云候选网站健康、安全头和真实回滚：`PASS`。

这些结果只证明声明范围内的 Developer Preview，不能外推为生产安全、科学 Truth、
客户采用或自动 Authority。

## Known limitations（已知限制）

1. `OPEN_WEB_DISCOVERY=PARTIAL_METADATA_ONLY`：GitHub 完整描述已命中，但规范英文名、
   中文名和公开搜索尚未精确命中；`ADR-022` 仅为 v0.1 接受并披露该限制。
2. DBOS 整仓保持 private；公开的是有界 wheel，不是完整实现仓库。
3. 没有公共 DBOS Runtime、托管 API、Permission grant 或生产 SLA。
4. Agent Customer Validation 的 12/12 overall verdict 均为边界正确的 `CONDITIONAL`，
   不等于市场采用。
5. 网站构建树保留 `R-015` 的 2 项 moderate PostCSS 通告
   (`GHSA-qx2v-qp2m-jg93`)；0 critical、0 high。服务器只部署静态 `out/`，不运行
   Node.js、Next.js、Vite 或 PostCSS；等待非破坏性上游修复。

## Architecture boundary（架构边界）

```text
DBA != DBOS != SAEE
DBOS governs existence.
SAEE governs evolution.
Evidence != Truth
Evaluation != Authority
Recommendation != Decision
Decision != Execution
Capability != Permission
```

Release（发布）不等于 Deployment（部署）、Adoption（采用）或 Production Readiness
（生产就绪）。
