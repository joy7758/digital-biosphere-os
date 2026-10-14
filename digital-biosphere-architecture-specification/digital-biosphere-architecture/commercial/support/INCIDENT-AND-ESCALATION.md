# Incident and Escalation / 事件与升级

`STATUS=SECURITY_CONTACT_ASSIGNED_POLICY_STILL_HUMAN_REVIEW_DRAFT`

## Flow

```text
Finding -> Preserve bounded evidence -> Classify -> Human owner review
        -> Contain or stop -> Customer notice if contractually required
        -> Recovery assessment -> Closure or retained limitation
```

Every event record must identify the workspace, time, affected surface, reporter, evidence references, containment, known limitations and Human disposition. Raw customer content, credentials and secrets must not enter the governance repository.

Immediate stop conditions include suspected cross-tenant access, secret disclosure, unauthorized action effect, Receipt integrity failure, uncontrolled retention and inability to revoke access. Verification does not authorize recovery or reopening.

Notification timing and legal duties remain customer- and contract-specific.
The internal Security Contact is `human:zhangbin` through the private GitHub
owner and authorized operator channel. No public email address is invented by
this assignment. Until a second person accepts backup duty and a signed SOW
defines customer notice obligations:

```text
SECURITY_CONTACT_ASSIGNED=true
SECURITY_CONTACT_REF=human:zhangbin
BACKUP_SECURITY_CONTACT_ASSIGNED=false
INCIDENT_NOTIFICATION_COMMITMENT=false
```
