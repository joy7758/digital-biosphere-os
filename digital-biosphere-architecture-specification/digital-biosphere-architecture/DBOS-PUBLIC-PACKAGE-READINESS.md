---
review_id: TMAI-DBOS-PUBLIC-PACKAGE-READINESS-20260722-001
title: DBOS Public-safe Package Readiness Review
title_zh: DBOS 公开安全软件包就绪复核
status: public-safe-wheel-published-repository-private
source_revision: cd3f867c4379ec555c45e7d554088ad12ce08a24
whole_repository_public_recommended: false
public_safe_wheel_validated: true
public_safe_wheel_published: true
release_authorized: true
decision_reference: architecture/ADR-022-developer-preview-release.md
reviewed_at: 2026-07-22
---

# DBOS Public-safe Package Readiness（DBOS 公开安全软件包就绪）

## Outcome（结论）

DBOS 整仓公开当前不推荐。远端 `main` 没有 Gitleaks（密钥扫描器）命中，但 48 个跟踪
文件包含本机绝对路径，其中 `registry/agents.yaml` 暴露不必要的本地项目目录清单。
这些内容属于历史 registry/evidence（登记／证据）表面，不能为了发布而静默改写。

从同一 DBOS `main@cd3f867c4379ec555c45e7d554088ad12ce08a24` 构建的 bounded
wheel（有界 Python 分发包）已通过公开安全复核。它只包含最小 Object SDK（对象软件
开发工具包）、Validator（验证器）、MCP Adapter（MCP 适配器）和 Canonical Schema
（规范模式），不包含 registry、evidence、本机路径或治理状态。

```text
WHOLE_DBOS_REPOSITORY_PUBLIC_RECOMMENDED=false
PUBLIC_SAFE_WHEEL_VALIDATED=true
PUBLIC_SAFE_WHEEL_PUBLISHED=true
RELEASE_AUTHORIZED=true
```

## Agent Recommendation Review（智能体推荐复核）

既有 24 次 Agent Customer Validation（智能体客户验证）把 DBOS private access（私有
访问）识别为主要不推荐原因。复核发现首个 wheel 还缺失 YAML Schema，并安装了一个
无法在 wheel 中找到仓库测试的 `dbos-tests` 命令；因此原 wheel 不应发布。

DBOS PR `#2` 已完成最小修复：

- 7 个 YAML Schema 进入 wheel；
- `validate_object` 在隔离安装后返回 `PASS`；
- 仓库级测试入口保留在源码中，不再作为误导性的 wheel console script（控制台命令）；
- 新增 fail-closed distribution tests（失败关闭分发测试）；
- 文档明确 `wheel candidate != published package != production SDK`。

修复后 exact wheel 已按 `ADR-022` 通过 `v0.1-developer-preview` GitHub Release 提供
匿名下载、校验和安装。它只能推荐为 bounded Developer Preview package（有界开发者
预览包），不能推荐为生产 Runtime、托管 API 或 Permission system。

## Whole-repository Preflight（整仓预检）

| Check | Result |
|---|---|
| GitHub visibility | `PRIVATE` |
| Source revision | `cd3f867c4379ec555c45e7d554088ad12ce08a24` |
| Tracked files | `460` |
| Apache-2.0 | `PASS` |
| Gitleaks 8.30.1 reachable-history scan | `0 findings` |
| Gitleaks current-tree scan | `0 findings` |
| Sensitive filenames | `0` |
| Private IPv4 files | `0` |
| Blobs over 5 MiB | `0` |
| Files containing `/Users/...` paths | `48` |
| Whole-repository public recommendation | `NO` |

绝对路径计数不是 secret finding（密钥发现），但会披露设备目录结构和未纳入本次发布的
项目资产清单，因此整仓公开 gate（闸门）失败关闭。

## Public-safe Wheel（公开安全分发包）

| Field | Value |
|---|---|
| Package ID | `TMAI-DBOS-WHEEL-CANDIDATE-20260722-001` |
| Filename | `digital_biosphere_os_preview-0.1.0.dev0-py3-none-any.whl` |
| SHA-256 | `edf92e548860384b1416a612a7e319e0d994bb324f8621847d0d154624ae8f09` |
| Bytes | `45115` |
| Wheel files | `39` |
| Included YAML schemas | `7` |
| Included `tools/` files | `0` |
| Included registry files | `0` |
| Included evidence files | `0` |
| Absolute user path matches | `0` |
| Wheel Gitleaks findings | `0` |
| Clean install | `PASS` |
| Installed validation smoke | `PASS` |

The exact artifact is published only as the `v0.1-developer-preview` GitHub Release asset and is
referenced by the public manifest and Baidu Cloud site. It is not published to PyPI and the full
DBOS repository remains private. The pre-release local storage path is intentionally omitted from
the public manifest because it is not a public interface.

## Source Verification（源码验证）

| Check | Result |
|---|---|
| `python tools/run_tests.py` | `334/334 PASS` across 15 directories |
| All `validation/*_validator.py` | `34/34 PASS` |
| Multi-Agent Trust Demo | `PASS`; synthetic; 0 external side effect |
| MCP Reference Demo | `PASS`; `real_mcp_connected=false` |
| Agent created | `0` |
| Runtime created | `0` |
| Permission granted | `0` |

## Recorded Human Decision（已记录人工决定）

推荐的 access decision（访问决定）是：

```text
DQ-016=PUBLISH_PUBLIC_SAFE_DBOS_WHEEL
WHOLE_DBOS_REPOSITORY_VISIBILITY=KEEP_PRIVATE
decided_by_ref=zhangbin
decision_reference=architecture/ADR-022-developer-preview-release.md
```

该决定只允许把上述 exact wheel 作为 Developer Preview GitHub Release asset（开发者预览
GitHub 发布资产）公开。它不允许公开整个 DBOS 仓库，不授权 PyPI 发布，不产生 Agent、
Runtime、Entity、Permission、Evidence Truth 或生产兼容承诺。
