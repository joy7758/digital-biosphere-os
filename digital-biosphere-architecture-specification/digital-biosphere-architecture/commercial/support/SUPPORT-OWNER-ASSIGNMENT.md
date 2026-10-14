# Support Owner Assignment / 支持责任人指派

```text
STATUS=ASSIGNED_SINGLE_PERSON_BACKUP_REQUIRED
DECISION_ID=TITMAS-D29-SECURITY-FINDINGS-20260812-01
SUPPORT_OWNER_REF=human:zhangbin
SECURITY_CONTACT_REF=human:zhangbin
BACKUP_OWNER_REF=null
CUSTOMER_ESCALATION_CONTACT_REF=human:zhangbin
EFFECTIVE_AT=2026-08-12T13:34:52Z
REVIEW_BY=2026-09-11T23:59:59+08:00
EXPIRES_AT=2026-11-10T23:59:59+08:00
CONTACT_WINDOW=BEST_EFFORT_ASIA_SHANGHAI_NO_SLA
CONTACT_PATH=PRIVATE_GITHUB_OWNER_AND_AUTHORIZED_OPERATOR_CHANNEL
REVOCATION_PATH=RECORDED_HUMAN_DECISION_IN_DBA_COCKPIT
```

Owner 必须是可承担相应责任的人类或依法设立主体。Agent 可以整理和建议，不能成为合同责任人、安全联系人或付款主体。指派必须记录有效期、替补、可联系时段和撤销方式。

本次 Human Decision 将 `zhangbin` 同时指派为 Support Owner 与 Security
Contact，不虚构邮箱或第二责任人。该指派只建立内部责任路径，不激活客户支持、
SLA、事件通知承诺、合同义务或生产权限。

同一人承担两个角色属于明确保留的集中风险；在第二责任人完成独立接受前，
`BACKUP_OWNER_REF` 保持 `null`，不得把本文件解释为 7x24 支持能力。
