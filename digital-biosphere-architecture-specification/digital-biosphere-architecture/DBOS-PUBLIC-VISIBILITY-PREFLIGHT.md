---
document_id: DBA-DBOS-PUBLIC-VISIBILITY-PREFLIGHT-2026-07-21
title: DBOS Repository Public Visibility Preflight
title_zh: DBOS 仓库公开可见性预检
status: whole-repository-public-not-recommended-public-safe-wheel-pass-not-authorized
source_commit: cd3f867c4379ec555c45e7d554088ad12ce08a24
history_scan_commit: cd3f867c4379ec555c45e7d554088ad12ce08a24
repository_visibility: private
repository_visibility_changed: false
decision_reference: architecture/ADR-020-release-preparation-owner-decisions.md
child_repository_modified: true
last_reviewed: 2026-07-22
---

# DBOS Public Visibility Preflight（DBOS 公开可见性预检）

## 1. Scope（范围）

本报告为 `DQ-014` 提供只读预检。它检查当前 DBOS 冻结提交的已跟踪文件、Git 历史
文件名、常见高置信度密钥标记、超大 blob（内容对象）、GitHub 安全功能和许可证状态。
它不改变 GitHub visibility（可见性），不替代专业 secret scan（密钥扫描）、法律审查
或 Domain Owner 的公开决定。

```text
PRIMARY_REPOSITORY=DBA
OBSERVED_CHILD_REPOSITORY=DBOS
DBOS_MODIFIED_FOR_LICENSE_AND_TRIAL_BOUNDARY=true
GITHUB_VISIBILITY_CHANGED=false
```

## 2. Observed Snapshot（观察快照）

| 项目 | 结果 |
|---|---|
| GitHub repository | `joy7758/digital-biosphere-os` |
| Current trial commit | `cd3f867c4379ec555c45e7d554088ad12ce08a24` |
| Gitleaks scanned commit | `cd3f867c4379ec555c45e7d554088ad12ce08a24` |
| Visibility | `PRIVATE` |
| Tracked files | 460 |
| Root `LICENSE` | `Apache-2.0`；官方全文匹配 |
| Sensitive filename patterns | 0 个命中 |
| Private-key PEM markers | 0 个命中 |
| High-confidence AWS/GitHub/OpenAI/Google token patterns | 0 个命中 |
| Generic credential assignment patterns | 0 个命中 |
| Sensitive filenames in reachable Git history | 0 个命中 |
| Reachable Git blobs over 5 MiB | 0 个命中 |
| Independent scanner | `gitleaks/gitleaks@v8.30.1`；官方 checksum（校验和）通过 |
| Reachable Git history scanned | 4 non-merge changesets；约 3.89 MB；full clone `rev-list --all=6` |
| Gitleaks findings | 0 |
| Files containing local `/Users/...` paths | 48 |
| GitHub Secret Scanning | `DISABLED` |
| GitHub Dependabot Alerts | `DISABLED` |

扫描只报告文件和模式计数，不输出任何可能的 secret value（密钥值）。

## 3. Interpretation（解释）

当前快照与独立 Gitleaks 历史扫描均未发现密钥，是 `DQ-014` 的正向信号，
但不足以证明仓库可以立即公开：

- Gitleaks 覆盖当前可达 Git 历史，但任何规则型 scanner（扫描器）都不能证明不存在
  未知格式、外部存储、运行时 secret 或未纳入 Git 的私有材料；
- GitHub Secret Scanning 当前禁用，没有平台侧 alert evidence（告警证据）；
- Dependabot Alerts 当前禁用，没有平台侧依赖漏洞告警面；
- 根 `Apache-2.0` 许可证已存在并由 GitHub 识别；
- `PRIVATE` 仓库的 authenticated clean clone（认证检出）不等于匿名开发者可访问；
- 48 个跟踪文件包含本机绝对路径，`registry/agents.yaml` 还列出未纳入发布的本地项目
  目录；这不是 secret finding，但构成不必要的设备和资产清单披露；
- 因此整仓公开当前不推荐。独立的 public-safe wheel（公开安全分发包）复核见
  [`DBOS-PUBLIC-PACKAGE-READINESS.md`](DBOS-PUBLIC-PACKAGE-READINESS.md)。

## 4. Decision and Future Public Gate（决定与未来公开闸门）

`ADR-020` 已选择 `PRIVATE_COLLABORATOR_TRIAL`。刷新预检没有把 DBOS 切换为 public，
不把认证检出写成匿名可用，也不授权具体协作者。整仓公开因本机路径和项目资产清单
披露而失败关闭。若未来重新提出整仓 public visibility 变化，仍必须完成下列闸门并
形成新决定：

1. 保持 `DQ-012` 的 Apache-2.0 许可证和第三方材料边界；
2. 在未来最终 remote commit 与 tag 上重跑相同 Gitleaks 版本；
3. 明确 GitHub Secret Scanning / Dependabot 的启用策略；
4. 对个人数据、私有域名、内部地址、凭据占位符和第三方资产做人工抽样复核；
5. 决定先进行 private collaborator trial（私有协作者试用）还是直接 public；
6. 公开后从无认证环境执行 anonymous clone、安装、测试、Validator 和 Demo；
7. 保留 visibility rollback（可见性回退）和 incident response（事件响应）责任人。

当前更安全的发布路径是保持仓库 private，只发布
`TMAI-DBOS-WHEEL-CANDIDATE-20260722-001`。该 wheel 已排除 registry、evidence、reports、
tests、tools 和本机路径，并通过隔离安装；它仍需新的 Human Decision（人工决定）。

## 5. Decision State（决策状态）

```text
DQ_014_PRELIMINARY_TECHNICAL_INPUT_COMPLETE=true
HIGH_CONFIDENCE_SECRET_PATTERN_HITS=0
GITLEAKS_FULL_REACHABLE_HISTORY_SCAN_PASS=true
GITLEAKS_FINDINGS=0
LOCAL_ABSOLUTE_PATH_FILES=48
FULL_SECRET_HISTORY_AUDIT_COMPLETE=false
LICENSE_SELECTED=true
LICENSE_ID=Apache-2.0
DBOS_PUBLIC=false
DBOS_PUBLICATION_AUTHORIZED=false
WHOLE_DBOS_REPOSITORY_PUBLIC_RECOMMENDED=false
PUBLIC_SAFE_WHEEL_VALIDATED=true
PUBLIC_SAFE_WHEEL_PUBLISHED=false
PRIVATE_COLLABORATOR_TRIAL_SELECTED=true
COLLABORATORS_ADDED=0
DEVELOPER_PREVIEW_RELEASED=false
```

结论：`PRIVATE_COLLABORATOR_TRIAL` 仍是已生效决定；本预检不批准添加协作者、改变
仓库可见性、公开 wheel 或正式发布。下一项推荐决定是只公开 exact public-safe wheel，
同时保持 DBOS repository private。
