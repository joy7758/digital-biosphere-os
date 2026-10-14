# TITMAS Media Evidence v0.1.0 — Reproduction Guide

This guide describes the upstream local synthetic reference implementation. It is not a production service, certification result, or legal-evidence procedure.

## Environment

- Python 3.9 or later
- No network connection
- No third-party Python dependency

## Verify the reference implementation

From the root of a `titmas-media-guard` v0.1.0 checkout:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 demo/run_full_scenario.py
python3 demo/run_portable_verify.py
```

Reference commit:

```text
7eac452f66a2b7de525543f80b9a7cf1465ef9a1
```

## Verification boundary

The commands reproduce local schema, reference, lifecycle, hash, and package checks. They do not verify content truth, authenticate identity, create legal evidence, prove production deployment, certify an external standard, or guarantee security.
