---
document_id: TITMAS-SAEP-PUBLIC-SITE-RELEASE-EVIDENCE-V15
artifact_type: saep-public-site-release-evidence
schema_version: "0.1"
publication_status: LIVE
deployment_date: 2026-07-29
sites_version: 15
production_commit: 4475e48a3dad4ea8f3613e526c8dee38c1553e4f
source_branch: feat/saep-industry-profile-site
evidence_scope: website-publication-governance-only
implementation_effect: none
protocol_effect: none
authority_effect: none
---

# SAEP Public Site Release Evidence — Version 15

# SAEP 公共网站发布证据——版本 15

This record preserves the human-readable publication evidence for the SAEP
industry application profile on the TITMAS public website.

本记录固化 TITMAS 公共网站上 SAEP 行业应用剖面的公开发布证据。它记录已发生的发布，
不修改 SAEP、EEOAP、Agent Evidence、协议、Schema、验证器、API 或网站功能。

## Status

## 状态

```text
PUBLICATION_STATUS=LIVE
DEPLOYMENT_DATE=2026-07-29
SITES_VERSION=15
PRODUCTION_COMMIT=4475e48a3dad4ea8f3613e526c8dee38c1553e4f
SOURCE_BRANCH=feat/saep-industry-profile-site
SAEP_VERSION=v0.1
SAEP_STATUS=RESEARCH_PROTOTYPE
```

The production commit is the exact website source revision recorded by the
active immutable Baidu Cloud release manifest.

生产提交与百度云当前不可变 release 中 `release-manifest.json` 记录的网站源码版本一致。

## Public Endpoints

## 公开入口

- 中文页面：<https://redcrag.cn/industry/space-agent-evidence/>
- English page: <https://redcrag.cn/en/industry/space-agent-evidence/>
- 机器可读入口：<https://redcrag.cn/space-agent-evidence-profile.json>
- GitHub 研究实现：<https://github.com/joy7758/agent-evidence/tree/main/extensions/space>
- SAEP v0.1 版本 DOI：<https://doi.org/10.5281/zenodo.21393369>
- Agent Evidence 项目 concept DOI：<https://doi.org/10.5281/zenodo.19334061>

The version DOI identifies the archived SAEP v0.1 research artifact. The
concept DOI identifies the evolving Agent Evidence project. They are not
interchangeable.

版本 DOI 指向已归档的 SAEP v0.1 研究工件；concept DOI 指向持续演进的 Agent Evidence
项目。两者不能互换。

## Architecture Position

## 架构定位

```text
TITMAS
  → Industry Application Profile（行业应用剖面）
    → SAEP
      → EEOAP
        → Runtime Verification（运行时验证）
```

- TITMAS does not own the specification authority of Agent Evidence.
- TITMAS 不拥有 Agent Evidence 的规范权威。
- SAEP is the TITMAS industry application profile for autonomous space
  systems.
- SAEP 是 TITMAS 面向自主航天系统的行业应用剖面。
- EEOAP provides the execution-evidence foundation used by SAEP.
- EEOAP 提供 SAEP 使用的执行证据基础。
- SAEP is not a spacecraft control system.
- SAEP 不是航天控制系统。

## Validation Evidence

## 验证证据

```text
TESTS_PASS=true
TEST_COUNT=23
STATIC_EXPORT_PASS=true
ZH_EN_CONTENT_PARITY_PASS=true
TRUTH_BOUNDARY_VALIDATION_PASS=true
INTERNAL_LINK_CHECK_PASS=true
SEO_METADATA_PASS=true
BUILD_PASS=true
GIT_DIFF_CHECK_PASS=true
BROWSER_VERIFICATION_PASS=true
MOBILE_LAYOUT_VERIFICATION_PASS=true
```

- ESLint: `0 errors`.
- Existing `<img>` warnings: `4`; they were not introduced as new release
  errors.
- The DOI resolver resolved the version DOI to the Zenodo record.
- The Zenodo destination was intermittently affected by the local network
  environment during release verification; this did not invalidate the DOI.
- `npm ci` reported `9` existing high-severity advisories. They were recorded
  and were not modified in the SAEP release.
- Browser verification covered the Chinese and English pages, navigation,
  architecture diagram, public research links, console errors, and a
  `390 × 844` mobile viewport.

These checks establish the bounded website release result only. They do not
constitute spacecraft validation, operational deployment, certification,
institutional adoption, mission assurance, or production readiness.

以上检查只证明有边界的网站发布结果，不构成航天器验证、实际运行部署、认证、机构采用、
任务安全保证或生产就绪证明。

## Claim Boundaries

## 声明边界

```text
NASA_ADOPTION_CLAIM=false
ESA_ADOPTION_CLAIM=false
FDO_ADOPTION_CLAIM=false
FLIGHT_CERTIFICATION_CLAIM=false
SPACE_QUALIFICATION_CLAIM=false
INDUSTRIAL_DEPLOYMENT_CLAIM=false
MISSION_SAFETY_GUARANTEE=false
REAL_SPACECRAFT_VALIDATION=false
```

`SYNTHETIC_VALIDATION_COMPLETED=true` describes bounded synthetic research
validation. It must not be interpreted as real spacecraft validation.

`SYNTHETIC_VALIDATION_COMPLETED=true` 只描述有边界的合成研究验证，不得解释为真实航天器
验证。

## Rollback

## 回滚

```text
ACTIVE_RELEASE=/srv/tmai/releases/4475e48a3dad4ea8f3613e526c8dee38c1553e4f--4c7c161016884224a3903205630afeb4fbe68f52a142a307e176d4cdbd095045
ROLLBACK_TARGET=/srv/tmai/releases/05bd697517acd4252e59b644b2c8bd537fe01e50--ce82b5bf720adad43cef35a55f0e668a93b2f9fb3d641728c8223db8e7d7a995
ROLLBACK_SOURCE_COMMIT=05bd697517acd4252e59b644b2c8bd537fe01e50
ROLLBACK_ENTRY=/srv/tmai/current
ROLLBACK_TARGET_RESOLVED=true
ROLLBACK_EXECUTED_IN_THIS_TASK=false
```

The established rollback path is to atomically repoint `/srv/tmai/current` to
the recorded immutable rollback target, run `nginx -t`, reload Nginx, and
repeat the required public health checks. A failed validation must preserve
the failed release and its evidence rather than delete or rewrite it.

既有回滚路径是将 `/srv/tmai/current` 原子切换至上述不可变回滚目标，执行 `nginx -t`，
重新加载 Nginx，并重复所需公开健康检查。验证失败时必须保留失败 release 及其证据，
不得删除或改写历史。

## Known Follow-up Items

## 已知后续事项

- The English page inherits `html lang="zh-CN"` from the root layout.
- 英文页面继承根布局的 `html lang="zh-CN"`。
- The existing dependency set reports `9` high-severity advisories.
- 现有依赖报告 `9` 个 high advisories。
- `feat/saep-industry-profile-site` has not been merged into the default branch
  through a Pull Request.
- 网站发布分支尚未通过 Pull Request 合并至默认分支。

These follow-up items do not change the verified fact that the bounded SAEP
pages and machine entry are live.

这些后续事项不改变 SAEP 中英文页面及机器入口已经上线的事实。

## Final Boundary

SAEP remains a research profile, not a flight certification or operational
spacecraft system.

SAEP 仍是研究剖面，不是飞行认证或实际航天器运行系统。
