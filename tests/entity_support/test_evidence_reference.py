"""Tests for references that do not replace canonical DBOS Evidence."""

from __future__ import annotations

import unittest

from entity_support.evidence_reference import (
    EVIDENCE_REFERENCE_FIELDS,
    build_evidence_reference,
)


class EvidenceReferenceTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "evidence_id": "fixture-evidence-reference",
            "execution_id": "fixture-execution",
            "reference": "fixture://not-canonical-evidence",
        }
        values.update(overrides)
        return build_evidence_reference(**values)

    def test_reference_defaults_to_unknown_integrity(self) -> None:
        record = self._build()
        self.assertEqual(record["integrity_status"], "UNKNOWN")
        self.assertEqual(tuple(record), EVIDENCE_REFERENCE_FIELDS)

    def test_reference_accepts_pending_integrity(self) -> None:
        record = self._build(integrity_status="PENDING")
        self.assertEqual(record["integrity_status"], "PENDING")

    def test_reference_rejects_validated_integrity(self) -> None:
        with self.assertRaises(ValueError):
            self._build(integrity_status="VALIDATED")

    def test_reference_contains_no_truth_or_payload_fields(self) -> None:
        record = self._build()
        self.assertNotIn("truth", record)
        self.assertNotIn("payload", record)
        self.assertNotIn("verification_result", record)


if __name__ == "__main__":
    unittest.main()
