"""Cross-module rejection tests for prohibited automatic state changes."""

from __future__ import annotations

import unittest

from entity_support.verification_reference import (
    VERIFICATION_REFERENCE_FIELDS,
    build_verification_reference,
    validate_verification_reference,
)
from validation.entity_support_validator import validate


class NegativeBoundaryTests(unittest.TestCase):
    def test_verification_defaults_to_pending_v0(self) -> None:
        record = build_verification_reference(
            verification_id="fixture-verification-reference",
            evidence_id="fixture-evidence-reference",
        )
        self.assertEqual(record["verification_status"], "PENDING")
        self.assertEqual(record["verification_level"], "V0")
        self.assertEqual(tuple(record), VERIFICATION_REFERENCE_FIELDS)

    def test_verification_contains_no_permission(self) -> None:
        record = build_verification_reference(
            verification_id="fixture-verification-reference",
            evidence_id="fixture-evidence-reference",
        )
        self.assertNotIn("permission", record)
        self.assertNotIn("capability_id", record)

    def test_verification_rejects_permission_derivation(self) -> None:
        errors = validate_verification_reference(
            {
                "verification_id": "fixture-verification-reference",
                "evidence_id": "fixture-evidence-reference",
                "verification_status": "PENDING",
                "verification_level": "V0",
                "permission_status": "GRANTED",
            }
        )
        self.assertTrue(any("grant fields" in error for error in errors))

    def test_verification_rejects_automatic_pass(self) -> None:
        with self.assertRaises(ValueError):
            build_verification_reference(
                verification_id="fixture-verification-reference",
                evidence_id="fixture-evidence-reference",
                verification_status="PASS",
            )

    def test_integrated_validator_rejects_all_required_negative_cases(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["negative_case_count"], 5)
        self.assertEqual(result["rejected_negative_case_count"], 5)
        self.assertTrue(all(result["negative_case_results"].values()))
        self.assertTrue(all(count == 0 for count in result["side_effect_counts"].values()))


if __name__ == "__main__":
    unittest.main()
