"""Evidence Reference Object validation tests."""

from __future__ import annotations

import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_evidence_reference


class EvidenceSchemaValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_synthetic_evidence_reference(self) -> None:
        self.assertEqual(
            validate_object(synthetic_evidence_reference()).result,
            ValidationStatus.PASS,
        )

    def test_rejects_truth_claim(self) -> None:
        target = synthetic_evidence_reference()
        target["truth_confirmed"] = True
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_unsupported_integrity_upgrade(self) -> None:
        target = synthetic_evidence_reference()
        target["integrity_status"] = "VERIFIED"
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_reports_source_owner_conflict(self) -> None:
        target = synthetic_evidence_reference()
        target["source_reference"]["source"] = "registry/other-evidence.yaml"
        self.assertEqual(validate_object(target).result, ValidationStatus.CONFLICT)

    def test_preserves_unknown_source_status(self) -> None:
        target = synthetic_evidence_reference()
        target["source"]["status"] = "UNKNOWN"
        self.assertEqual(validate_object(target).result, ValidationStatus.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
