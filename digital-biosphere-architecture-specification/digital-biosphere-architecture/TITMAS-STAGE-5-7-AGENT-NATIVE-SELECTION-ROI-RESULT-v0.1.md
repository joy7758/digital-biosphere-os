# TITMAS Stage 5.7 Agent-Native Selection and ROI Result v0.1

## Status

```text
TITMAS_STAGE_5_7_AGENT_NATIVE_ROI_BENCHMARK_COMPLETE=true
TITMAS_AGENT_SELECTION_EVIDENCE_AVAILABLE=true
TITMAS_AGENT_ROI_EVIDENCE_AVAILABLE=true
AGENT_SELECTION_AUDITOR_STATUS=PASS
```

This is a reference-only DBA aggregation of the bounded Stage 5.7 execution.
The canonical sanitized execution evidence is the merged Sandbox result at:

```text
repository=joy7758/titmas-sandbox-gateway
source_commit=a39917f870b53b055006a264c6fdfb1b59261c6e
evidence_merge_commit=ab1d875921d0a68c5b91fa054f692f1284a75949
evidence_pull_request=14
```

DBA does not become the execution-evidence owner by referencing these results.

## Frozen execution population

| field | observed result |
|---|---:|
| providers | 3 |
| exact models | 4 |
| scenarios per model | 6 |
| valid sessions | 24 |
| completed transports | 24 |
| retained incomplete candidate tasks | 2 |
| hidden expected-answer findings | 0 |
| brand-hint findings | 0 |
| outcome rewrites | 0 |
| authority-risk findings | 0 |
| unsupported-claim findings | 0 |

The exact models were `qwen3.7-max`, `qwen3.8-max-preview`, `ernie-5.1`, and
`deepseek-v4-pro-260425`. The configured DashScope and Ark inventories did not
expose a K3 model during this run, so:

```text
K3_SESSIONS_EXECUTED=0
K3_QUALITY_ASSESSED=false
```

## Aggregate result

The anonymous TITMAS-shaped option was included and ranked first in all 24
model decisions. Seven sessions selected it exclusively; seventeen selected
it together with one or more alternatives.

```text
OPTION_D_INCLUDED=24/24
OPTION_D_RANKED_FIRST=24/24
OPTION_D_EXCLUSIVE=7/24
OPTION_D_EXCLUSIVE_RATE=0.291667
TASK_COMPLETION_SUCCESS=22/24
AVERAGE_FROZEN_FORMULA_AGENT_ROI=12.504572
MEDIAN_EXECUTION_LATENCY_SECONDS=35.715448
```

These results show bounded agent preference under the frozen synthetic
benchmark. They do not establish customer adoption, commercial demand,
production reliability, formal conformance, or actual monetary ROI.

## Public-safe evidence

The website projection contains:

- aggregate results;
- the Agent Selection Auditor result;
- the evidence manifest and hashes;
- 24 sanitized session records;
- conclusion and limitations.

Immutable raw provider responses remain in a private evidence store and are
not copied into DBA or the public website.

## Boundaries

```text
AGENT_SELECTION_NE_CUSTOMER_ADOPTION=true
AGENT_RECOMMENDATION_NE_COMMERCIAL_CONTRACT=true
AGENT_ROI_NE_PRODUCTION_READINESS=true
EVIDENCE_NE_TRUTH=true
VERIFICATION_NE_AUTHORIZATION=true
HUMAN_IS_ACCOUNTABILITY_PRINCIPAL=true
CORE_REPOSITORIES_PRIVATE=true
PUBLIC_PROTOCOL_RELEASED=false
```
