# Stage 5.7 Sanitized Evidence

PR A froze the anonymous options, scenarios, randomization, scoring policy,
Harness, and tests before execution. PR B records only sanitized results from
the exact merged Harness commit
`a39917f870b53b055006a264c6fdfb1b59261c6e`.

```text
REAL_AGENT_SESSIONS_EXECUTED=24
AGENT_SELECTION_AUDITOR=PASS
OPTION_D_INCLUDED=24/24
OPTION_D_RANKED_FIRST=24/24
OPTION_D_EXCLUSIVELY_SELECTED=7/24
AVERAGE_FROZEN_FORMULA_ROI=12.504572
```

Read:

- `aggregate-results.json` for machine-readable aggregates;
- `agent-selection-audit.json` for the independent deterministic audit;
- `evidence-manifest.json` for session hashes;
- `sessions/` for sanitized per-session records;
- `CONCLUSION.md` for the bounded interpretation;
- `LIMITATIONS.md` before citing any result.

Raw prompts, responses, and tool traces are retained in a private local evidence
store and are not committed. The committed session records contain hashes,
metrics, exact model identities, scenario identities, randomized label maps,
and bounded outcomes.

This result is selection evidence from a synthetic benchmark. It is not
customer adoption, commercial proof, formal Conformance, Certification,
Standard Adoption, or production readiness.
