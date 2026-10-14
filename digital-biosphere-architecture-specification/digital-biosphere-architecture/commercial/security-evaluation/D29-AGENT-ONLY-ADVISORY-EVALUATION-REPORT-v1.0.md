# D29 Agent-only Security Advisory Evaluation Report v1.0

## Result

```text
AGENT_ONLY_ADVISORY_EVALUATION=COMPLETE_WITH_CALL_FAILURES
FORMAL_INDEPENDENT_SECURITY_AUDIT=false
STRUCTURED_CONSENSUS=NOT_RECOMMENDED
D29_SECURITY_ENGINEERING_GATE=FAIL_CLOSED
BLOCKER_FINDINGS_OPEN=1
HIGH_FINDINGS_OPEN=2
PAID_MONITOR_PILOT_RECOMMENDED_NOW=false
SECURITY_FINDINGS_CLOSED=0
```

This evaluation used only the existing sanitized private evaluation kit. It
contained no private core, customer data, Credential, production configuration,
complete attack corpus or bypass material.

## Model and Provider coverage

Nine bounded calls were attempted across five Providers. Four calls returned a
review, three of those matched the requested response Schema, and five calls
failed and remain recorded as failures.

| Provider | model | result | use in consensus |
|---|---|---|---|
| Alibaba DashScope | `qwen3.8-max` | valid `NOT_RECOMMENDED / FAIL_CLOSED` | included |
| Baidu Qianfan | `ernie-5.1` | valid `NOT_RECOMMENDED / FAIL_CLOSED` | included |
| DeepSeek | `deepseek-chat` | valid after one bounded retry; `NOT_RECOMMENDED / FAIL_CLOSED` | included |
| Baidu Qianfan | `kimi-k2.6` | semantically not recommended, response Schema invalid | excluded |
| Volcengine Ark | Doubao and Kimi identifiers | HTTP 404 | failure retained |
| Google | Gemini Pro and Flash identifiers | HTTP 429 / disconnect | failure retained |

Changing a model or retrying a call does not create an independent formal
auditor. Successful calls from Qianfan count as one successful Provider even
though two model families responded.

## Consensus

All three Schema-valid reviews retained the canonical result:

- one Blocker and two High findings remain;
- the historical D04 Ledger failure cannot be rewritten;
- incident and formal rollback drills have not been executed;
- the available package is sanitized and synthetic, not production evidence;
- the paid Monitor Pilot should not be offered now.

The Kimi response reached the same practical conclusion but did not follow the
required response contract, so it is qualitative evidence only.

## Authority boundary

This is Agent-only advisory evidence. It is not an independent formal security
audit, Security PASS, certification, legal conclusion, commercial approval,
deployment authorization or finding closure. Agent recommendation is not Human
decision; verification is not authorization; Receipt is not Truth.

The canonical state remains:

```text
INDEPENDENT_SECURITY_EVALUATION=READY_TO_INVITE_NOT_EXECUTED
COMMERCIAL_PRIVATE_PILOT_READY=false
PAID_MONITOR_PILOT_AVAILABLE=false
PRODUCTION_SECURITY_READY=false
```
