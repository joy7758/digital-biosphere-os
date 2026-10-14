# Minimal Python Reference

This reference maps one synthetic Agent event to the TITMAS Development
interoperability surface:

```text
synthetic event
  → boundary check
  → existing Evidence reference binding
  → local structure Verification reference
  → read-only Evaluation handoff
  → limitations
```

Run:

```bash
python3 TITMAS/reference/minimal-python/titmas_reference.py \
  TITMAS/reference/minimal-python/example-input.json
python3 -m unittest discover -s TITMAS/reference/minimal-python/tests -v
```

The program performs no network request, writes no customer data, creates no
Agent or Runtime, and does not create a canonical Evidence object.

Field mapping:

| Input | Output |
|---|---|
| `identity` | `identity_ref` |
| `boundary` | `boundary` |
| `event` | `event` |
| `existing_evidence_ref` | `evidence_binding.evidence_ref` |
| `existing_verification_ref` | `verification_result.verification_ref` |
| event/evidence/verification refs | `evaluation_handoff.input_refs` |
| `limitations` | `limitations` |
