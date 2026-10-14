---
document_id: TITMAS-OPEN-PR-MAINLINE-REVIEW-D16
title: TITMAS Open Pull Request Mainline Review D16
title_zh: TITMAS 开放拉取请求主线审查 D16
status: point-in-time-read-only-classification
snapshot_at: 2026-08-02T11:20:53+08:00
open_pr_count: 217
repository_count: 24
merge_authorized: false
pr_closure_authorized: false
---

# TITMAS Open Pull Request Mainline Review D16

## 1. Scope and Method

This is a read-only GitHub snapshot for the query
`is:pr is:open user:joy7758`. It captured 217 open PRs across all 24 repositories
returned by GitHub; no repository or open PR was excluded. Each record includes
the observed diff size, Draft state, aggregate CI state and last-update time.

The complete per-PR record is machine-readable in
[`open-pr-classification.json`](open-pr-classification.json). This report does
not merge, close, edit, approve or reject a PR. The snapshot precedes any D16
governance PR, so a D16 PR is intentionally not recursively included in its own
input set.

## 2. Classification Result

| Category | Count | D16 disposition |
|---|---:|---|
| `MAINLINE_BLOCKER` | 1 | retain the fail-closed evidence; do not merge |
| `MAINLINE_SUPPORTING` | 0 | no open PR has direct supporting evidence |
| `ADJACENT_STRATEGIC` | 25 | `HOLD_NON_BLOCKING` |
| `MAINTENANCE_NON_BLOCKING` | 181 | defer until P0-10 closes |
| `ZERO_CHANGE_OR_INVALID` | 2 | human close recommended only |
| `STALE_OR_SUPERSEDED` | 8 | human review before any later disposition |

Observed CI aggregates are 114 `SUCCESS`, 30 `FAILURE` and 73
`NOT_REPORTED`. CI state is retained as repository evidence, not treated as a
merge recommendation or Agent onboarding result.

## 3. Mainline Blocker

| PR | Draft | CI | Changed files | Retained fact | Action |
|---|---|---|---:|---|---|
| [`titmas-integrations#5`](https://github.com/joy7758/titmas-integrations/pull/5) | yes | `SUCCESS` | 21 | `P0_10_RESULT=FAIL_CLOSED_AFTER_RUNTIME_ALIGNMENT` | `RETAIN_OPEN_FAIL_CLOSED` |

The PR proves that machine discovery, both MCP and SDK paths, preflight calls
and Receipt fetch were reached. It also retains `OBJECT_INVALID` and
`TYPE_MISMATCH`, no two Schema-valid PASS objects, no two VALID Receipt
verifications and no second-task reuse. It is therefore the sole current
mainline blocker, not a PASS candidate.

## 4. Mainline Supporting

No open PR was classified as `MAINLINE_SUPPORTING`. Frozen API v1, runtime
alignment, generated SDK and MCP Adapter facts already exist on their accepted
baselines; the remaining open PRs do not directly establish the missing P0-10
acceptance conditions or a high-confidence single-layer root cause.

## 5. Adjacent Strategic PRs

The following PRs are retained but frozen because they concern reference
models, standards, profiles, Demos, Portfolio admission, promotion or adjacent
product surfaces rather than the unique P0-10 closure path:

```text
joy7758/agent-accountability-evidence-layer#21
joy7758/agent-evidence#68
joy7758/agent-evidence#114
joy7758/agent-evidence#123
joy7758/digital-biosphere-architecture-specification#96
joy7758/digital-biosphere-architecture-specification#99
joy7758/digital-biosphere-architecture-specification#101
joy7758/joy7758#7
joy7758/joy7758#10
joy7758/joy7758#13
joy7758/persona-object-protocol#8
joy7758/persona-object-protocol#9
joy7758/persona-object-protocol#11
joy7758/persona-object-protocol#14
joy7758/persona-object-protocol#15
joy7758/persona-object-protocol#16
joy7758/persona-object-protocol#21
joy7758/persona-object-protocol#24
joy7758/tek-system#1
joy7758/tek-system#2
joy7758/tek-system#3
joy7758/titmas-action-gate-demo-sandbox#1
joy7758/titmas-action-gate-demo-sandbox#2
joy7758/titmas-action-gate-demo-sandbox#3
joy7758/titmas-demo#4
```

This classification does not reject their content and does not change project
Ownership. It only records that they are not the current technical mainline.

## 6. Maintenance and Security PRs

The 181 `MAINTENANCE_NON_BLOCKING` records include dependency updates, tests,
cleanup, performance work, unused-code changes and small corrections. None has
current evidence tying it directly to a D15-proven single-layer P0-10 root
cause, so all receive:

```text
MERGE_RECOMMENDED=false
DEFER_UNTIL_P0_10_CLOSED=true
```

Security-titled maintenance remains visible in the machine record and may
require a separate security disposition. D16 does not claim that deferral makes
a reported security issue safe; it only declines to smuggle unrelated changes
into P0-10 closure.

## 7. Zero-change and Invalid PRs

| PR | Changed files | Recommendation |
|---|---:|---|
| `joy7758/digital-biosphere-architecture-specification#79` | 0 | `CLOSE_RECOMMENDED=true` |
| `joy7758/digital-biosphere-architecture-specification#102` | 0 | `CLOSE_RECOMMENDED=true` |

No closure was performed. The recommendation requires a later human-authorized
GitHub action.

## 8. Stale or Superseded Candidates

```text
joy7758/SAEE#1
joy7758/agent-evidence#23
joy7758/agent-evidence#28
joy7758/digital-biosphere-architecture-specification#5
joy7758/digital-biosphere-architecture-specification#25
joy7758/digital-biosphere-architecture-specification#26
joy7758/digital-biosphere-architecture-specification#37
joy7758/digital-biosphere-architecture-specification#44
```

These are old strategic or broad-diff branches that predate substantial later
governance and content on their base branches. `STALE_OR_SUPERSEDED` is a review
classification, not deletion or closure authority.

## 9. Repository Distribution

| Repository | Total | Blocker | Supporting | Adjacent | Maintenance | Zero | Stale |
|---|---:|---:|---:|---:|---:|---:|---:|
| `joy7758/AASP-Core` | 4 | 0 | 0 | 0 | 4 | 0 | 0 |
| `joy7758/China-Precision-Mold-FDO-Standard` | 4 | 0 | 0 | 0 | 4 | 0 | 0 |
| `joy7758/ISAS-Core` | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| `joy7758/Kinetic-Robotics-FDO-Sovereignty` | 2 | 0 | 0 | 0 | 2 | 0 | 0 |
| `joy7758/MCP-Legal-China` | 8 | 0 | 0 | 0 | 8 | 0 | 0 |
| `joy7758/RedRock-Constitution` | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| `joy7758/SAEE` | 27 | 0 | 0 | 0 | 26 | 0 | 1 |
| `joy7758/agent-accountability-evidence-layer` | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| `joy7758/agent-evidence` | 36 | 0 | 0 | 3 | 31 | 0 | 2 |
| `joy7758/aro-audit` | 6 | 0 | 0 | 0 | 6 | 0 | 0 |
| `joy7758/digital-biosphere-architecture-specification` | 34 | 0 | 0 | 3 | 24 | 2 | 5 |
| `joy7758/digital-biosphere-os` | 27 | 0 | 0 | 0 | 27 | 0 | 0 |
| `joy7758/ecl-execution-compact-layer` | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| `joy7758/fdo-kernel-mvk` | 3 | 0 | 0 | 0 | 3 | 0 | 0 |
| `joy7758/joy7758` | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| `joy7758/pFDO-Specification` | 8 | 0 | 0 | 0 | 8 | 0 | 0 |
| `joy7758/persona-object-protocol` | 14 | 0 | 0 | 8 | 6 | 0 | 0 |
| `joy7758/safety-valve-spec` | 7 | 0 | 0 | 0 | 7 | 0 | 0 |
| `joy7758/tek-system` | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| `joy7758/titmas-action-gate-demo-sandbox` | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| `joy7758/titmas-demo` | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| `joy7758/titmas-integrations` | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `joy7758/token-governor` | 10 | 0 | 0 | 0 | 10 | 0 | 0 |
| `joy7758/verifiable-agent-demo` | 8 | 0 | 0 | 0 | 8 | 0 | 0 |

## 10. Conclusion

```text
OPEN_PR_COUNT=217
MAINLINE_BLOCKER_PRS=joy7758/titmas-integrations#5
MAINLINE_SUPPORTING_PRS=NONE
ADJACENT_STRATEGIC_PRS=25
MAINTENANCE_NON_BLOCKING_PRS=181
ZERO_CHANGE_OR_INVALID_PRS=2
STALE_OR_SUPERSEDED_PRS=8
PR_MERGES_EXECUTED=0
PR_CLOSURES_EXECUTED=0
NEW_FEATURE_FREEZE=true
```
