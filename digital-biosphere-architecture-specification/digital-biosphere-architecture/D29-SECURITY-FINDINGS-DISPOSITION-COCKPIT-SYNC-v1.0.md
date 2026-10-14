# D29 Security Findings Disposition Cockpit Sync v1.0

## Result

```text
D29_GATEWAY_MAIN=1a065f1702e355d5f5ed566bdfd3e895cdca2540
INCIDENT_DRILL=PASS
FORMAL_ROLLBACK_DRILL=PASS
HIGH_FINDINGS_OPEN=0
BLOCKER_FINDINGS_OPEN=0
BLOCKER_DISPOSITIONS_RETAINED=1
D29_SECURITY_ENGINEERING_GATE=FAIL_CLOSED_RETAINED_CR01_LIMITATION
SUPPORT_OWNER_REF=human:zhangbin
SECURITY_CONTACT_REF=human:zhangbin
BACKUP_OWNER_REF=null
COMMERCIAL_PRIVATE_PILOT_READY=false
PRODUCTION_READY=false
```

This cockpit record projects the exact merged Gateway evidence without taking
ownership of its implementation truth. The canonical child evidence is
`joy7758/titmas-sandbox-gateway` PR #58 and merge commit
`1a065f1702e355d5f5ed566bdfd3e895cdca2540`.

## Executed evidence

The bounded incident drill recovered the exact technical-candidate release in
2.166 seconds while the protected API failed closed and the separate Sandbox
route remained healthy. The immutable-release rollback reached the exact
preflighted rollback release in 2.604 seconds and forward recovery restored the
original release in 2.012 seconds. Read-only Tenant-isolation, current-key
Receipt verification, Quota, Idempotency and Billing-link checks passed.

PR #57 repaired the encrypted-backup unit and pinned CI's 45 KB public-safe
source snapshot to an exact source repository commit and SHA-256. Two fresh
encrypted backups passed integrity verification. The live Nginx IP-rate-limit
zone and location drift were corrected from the exact active release; a bounded
80-request synchronized probe produced 51 accepted and 29 HTTP 429 results with
no unexpected response, while Sandbox remained healthy.

The drills changed no database row, customer data, historical Receipt, Quota,
D04 state or application release. The temporary service, rollback and Nginx
execution authority is closed.

## CR-01 disposition

The historical synthetic restore result remains 1,659 valid and 2 unverifiable
Receipt signatures. Human Owner disposition keeps `D29-SEC-11=FAIL_RETAINED`,
keeps D04 closed, prohibits deletion, rewriting, allowlisting or re-signing,
and excludes that ledger from reuse as a future D29 launch baseline.

This closes the open action item by explicit scope disposition; it does not
convert the failed control to PASS. The commercial security gate therefore
remains fail-closed.

## Responsibility assignment

Decision `TITMAS-D29-SECURITY-FINDINGS-20260812-01` assigns
`human:zhangbin` as both Support Owner and Security Contact from 2026-08-12,
with review by 2026-09-11 and expiry on 2026-11-10. The contact path is the
private GitHub owner and authorized operator channel; no email address is
invented. There is no public SLA, Pilot Support Commitment or incident-notice
commitment.

The single-person concentration is retained as a blocker until a distinct
Backup Owner accepts responsibility.

## Agent recommendation boundary

The registered Qwen final-review route returned `insufficient_quota` and
produced no opinion. A fallback sanitized `gemini-3.5-flash` review recommended
only a bounded non-production Sandbox technical evaluation. It retained an
independent security evaluation, production/SLA/certification evidence and a
second-person support/security backup as blockers. The review creates no
Authority and does not recommend a paid pilot.

## Remaining gates

- independent security evaluation is not executed;
- business entity and invoice capability are not verified;
- pricing and a customer-specific SOW are not Human-approved;
- Chinese counsel review is incomplete;
- the second-person support/security backup is unassigned;
- corrected public commercial routes are not verified deployed.

No customer, contract, payment, production readiness, security certification
or commercial availability is inferred from this synchronization.
