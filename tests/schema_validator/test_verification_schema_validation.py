"""Verification Object structural and evidence-boundary tests."""

from __future__ import annotations

import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_verification


class VerificationSchemaValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_pending_verification(self) -> None:
        self.assertEqual(validate_object(synthetic_verification()).result, ValidationStatus.PASS)

    def test_non_pending_result_requires_external_record(self) -> None:
        target = synthetic_verification()
        target["verification_status"] = "PASS"
        self.assertEqual(validate_object(target).result, ValidationStatus.UNKNOWN)

    def test_independent_type_requires_external_independence_evidence(self) -> None:
        target = synthetic_verification()
        target["verification_type"] = "INDEPENDENT_VERIFICATION"
        self.assertEqual(validate_object(target).result, ValidationStatus.UNKNOWN)

    def test_rejects_malformed_target_reference(self) -> None:
        target = synthetic_verification()
        del target["target_reference"]["source"]
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)


if __name__ == "__main__":
    unittest.main()
