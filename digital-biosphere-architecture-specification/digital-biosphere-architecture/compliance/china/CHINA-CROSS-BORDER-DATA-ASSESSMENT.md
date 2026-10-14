# China Cross-Border Data Assessment

Status: `HUMAN_LEGAL_REVIEW_REQUIRED`

Primary source: https://www.gov.cn/gongbao/2024/issue_11366/202405/content_6954192.html

## Default

```text
CUSTOMER_DATA_TO_FOREIGN_MODEL=false
CUSTOMER_PERSONAL_INFORMATION_TO_FOREIGN_MODEL=false
CUSTOMER_RAW_DATA_LOCAL_BY_DEFAULT=true
CROSS_BORDER_COMPLIANCE_CONCLUSION=NOT_ASSESSED
```

| Scenario | Candidate classification | Boundary |
|---|---|---|
| Public website content sent to an external model for synthetic testing | `CONDITIONALLY_APPLICABLE` | provider, region, retention and training-use record required |
| Synthetic data sent to an external model | `CONDITIONALLY_APPLICABLE` | no customer or personal data; provider contract still recorded |
| Properly anonymized, explicitly authorized non-customer test data | `HUMAN_LEGAL_REVIEW_REQUIRED` | anonymization and authorization evidence required |
| China customer metadata sent to a foreign control plane | `PROHIBITED_BY_DEFAULT` | requires separate data-flow, volume, recipient and mechanism review |
| China customer raw Trace or production content sent to a foreign model | `PROHIBITED_BY_DEFAULT` | not part of the initial commercial pilot |
| Personal or sensitive personal information sent abroad | `PROHIBITED_BY_DEFAULT` | cannot proceed without qualified legal assessment and required mechanism |

The initial Monitor Pilot must operate with Chinese-region metadata storage or
inside the customer environment. External models may only consume public or
synthetic validation packages. This design restriction does not itself prove
compliance with cross-border requirements.
