# Evaluation Rollback Guide

Rollback must be versioned, bounded and reversible:

1. stop evaluation intake;
2. revoke evaluation credentials and verify access is absent;
3. switch only to a previously verified immutable release if separately authorized;
4. verify status, readiness, tenant isolation, Receipt and Audit boundaries;
5. preserve failed evidence and incident records;
6. delete or return evaluation data only under exact Human authorization;
7. record `RECOVERED`, `PARTIALLY_RECOVERED`, `NOT_RECOVERED` or `NOT_ASSESSED`.

No direct server editing, schema migration, D04 reopening, receipt rewrite, force push or destructive broad deletion is authorized by this guide.
