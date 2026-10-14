# Threat Model Reference

Canonical threat-model source: `TITMAS/agent-native/security/threat-model.md`.

Evaluation must at least cover tenant crossing, credential theft/over-scope, replay, idempotency collision, authorization/policy revision mismatch, Receipt tamper, Audit tamper, deletion/retention failure, backup/restore inconsistency, secret leakage, dependency/container risk, rate-limit bypass and unauthorized Enforce effect.

The open Critical finding and unknown High-finding count must be supplied to the named evaluator in the private review channel. This public-safe reference does not disclose exploitation material or imply remediation.
