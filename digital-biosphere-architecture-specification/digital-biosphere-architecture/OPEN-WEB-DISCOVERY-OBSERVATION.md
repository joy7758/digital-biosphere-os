---
observation_id: TMAI-OWD-20260722-001
title: Trusted Multi-Agent Infrastructure Open-Web Discovery Observation
title_zh: 可信多智能体基础设施开放网络发现观察
status: partial-metadata-only-canonical-discovery-not-observed
observed_at: 2026-07-22T00:45:20+08:00
rechecked_at: 2026-07-22T00:57:19+08:00
result: PARTIAL_METADATA_ONLY
canonical_name_match_observed: false
github_metadata_description_match_observed: true
public_web_exact_match_observed: false
queries_executed: 6
recheck_queries_executed: 7
github_metadata_remediated: true
github_metadata_indexing_signal_observed: true
release_authorization_effect: none
---

# Open-Web Discovery Observation（开放网络发现观察）

## Outcome（结论）

```text
OPEN_WEB_DISCOVERY_OBSERVATION_ID=TMAI-OWD-20260722-001
OPEN_WEB_DISCOVERY_RESULT=PARTIAL_METADATA_ONLY
CANONICAL_NAME_MATCH_OBSERVED=false
GITHUB_METADATA_DESCRIPTION_MATCH_OBSERVED=true
PUBLIC_WEB_EXACT_MATCH_OBSERVED=false
GITHUB_METADATA_REMEDIATED=true
GITHUB_METADATA_INDEXING_SIGNAL_OBSERVED=true
```

首次观察时，真实公开搜索与 GitHub repository search（仓库检索）没有返回
Trusted Multi-Agent Infrastructure（可信多智能体基础设施）、`redcrag.cn` 或规范 GitHub
仓库的精确项目命中。元数据修复后的即时复查出现了部分索引信号：完整的新 description
（描述）查询已经能返回规范 GitHub 仓库，但规范英文名、中文名和四个公开搜索查询仍未命中。
因此结果是 `PARTIAL_METADATA_ONLY`，开放网络自然发现仍不能声明为 `PASS`。

这与 [`AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md`](AGENT-CUSTOMER-VALIDATION-RERUN-REPORT.md)
的结果属于两个不同事实：

- `TMAI-ACV-20260722-002=PASS`：智能体在获得公开材料后能够理解边界、提取命令并作出适用性判断；
- `TMAI-OWD-20260722-001=PARTIAL_METADATA_ONLY`：GitHub 新描述已可检索，但规范名称和公开搜索仍不可发现。

## Query Set（查询集合）

本次使用以下精确查询，不将近似行业结果计为项目命中：

| surface | query | exact project match |
|---|---|---|
| Public web search | `"Trusted Multi-Agent Infrastructure" redcrag` | `NO` |
| Public web search | `"可信多智能体基础设施" redcrag` | `NO` |
| Public web search | `site:redcrag.cn "Trusted Multi-Agent Infrastructure"` | `NO` |
| Public web search | `site:github.com/joy7758 "Trusted Multi-Agent Infrastructure"` | `NO` |
| GitHub repository search | `"Trusted Multi-Agent Infrastructure"` | `NO` |
| GitHub repository search | `可信多智能体基础设施` | `NO` |

搜索结果中出现的其他 multi-agent（多智能体）或 trust infrastructure（可信基础设施）
项目不属于 TMAI，不计为部分通过。

## Root Cause Signal（根因信号）

观察时 GitHub 规范仓库的公开元数据仍是旧的 Digital Biosphere 描述，并且：

```text
repository_description_contains_TMAI=false
repository_homepage_present=false
repository_topics_count=0
```

这不是搜索未命中的唯一因果证明，但它是直接可修复的 discoverability signal（可发现性信号）。

## Bounded Remediation（有界修复）

已更新 GitHub 规范仓库的公开元数据：

- description：明确 `Trustworthy multi-agent infrastructure governance and architecture`；
- homepage：`https://redcrag.cn/`；
- topics：`multi-agent-systems`、`ai-agents`、`trustworthy-ai`、
  `agent-governance`、`digital-biosphere`、`agent-infrastructure`。

该动作只提高 repository metadata（仓库元数据）的机器可读性；没有修改 DBOS、SAEE，
没有发布 Runtime、API 或 package，也没有证明规范名称或公开搜索已经可发现。

## Immediate Recheck（即时复查）

| surface | query | result |
|---|---|---|
| GitHub repository search | `"Trusted Multi-Agent Infrastructure"` | `NO MATCH` |
| GitHub repository search | `可信多智能体基础设施` | `NO MATCH` |
| GitHub repository search | `"Trustworthy multi-agent infrastructure governance and architecture"` | `MATCH` |
| Public web search | 原 4 个查询集合 | `NO EXACT MATCH` |

这证明 GitHub metadata indexing signal（元数据索引信号）已经出现，但不能证明智能体按
canonical name（规范名称）或公开搜索能够自然发现本项目。

## Recheck Gate（复查闸门）

只有在外部索引有合理刷新窗口后，用规范英文名或中文名观察到可验证的规范项目命中，
才可把本项改为 `OBSERVED`。任何后续结果必须记录查询、时间、结果 URL 和歧义项。

```text
METADATA_UPDATE_NE_DISCOVERY_PASS=true
METADATA_DESCRIPTION_MATCH_NE_CANONICAL_NAME_DISCOVERY=true
DIRECT_URL_ACCESS_NE_OPEN_WEB_DISCOVERY=true
API_MODEL_VALIDATION_NE_SEARCH_INDEX_OBSERVATION=true
OPEN_WEB_DISCOVERY_CLAIM_WITHHELD=true
DEVELOPER_PREVIEW_RELEASED=false
AGENT_CREATED=false
RUNTIME_CREATED=false
PERMISSION_GRANTED=false
```
