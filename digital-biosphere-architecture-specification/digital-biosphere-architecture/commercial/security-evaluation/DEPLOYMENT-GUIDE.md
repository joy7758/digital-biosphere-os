# Evaluation Deployment Guide

Only an isolated synthetic environment is permitted before a separate Human deployment decision. The evaluator receives a version-pinned package, synthetic tenant, minimum scopes, short TTL, no production/customer data, no admin scope and an explicit rollback point.

Required preflight: source revision, manifest digest, dependency/secret scan, port and data-path scope, credential expiry/revocation, tenant isolation, log redaction and stop contact. Runtime secrets remain out of Git and evaluation reports.

This guide does not authorize server changes, deployment, paid resources, customer access or publication.
