"""Conformance tests for non-authorizing Verification references."""

from __future__ import annotations

import unittest

from entity_support.verification_reference import (
    build_verification_reference,
    validate_verification_reference,
)


class VerificationBoundaryConformanceTests(unittest.TestCase):
    def test_verification_defaults_to_pending_v0(self) -> None:
        record = build_verification_reference(
            verification_id="fixture-verification",
            evidence_id="fixture-evidence",
        )
        self.assertEqual(record["verification_status"], "PENDING")
        self.assertEqual(record["verification_level"], "V0")

    def test_verification_rejects_permission_field(self) -> None:
        errors = validate_verification_reference(
            {
                "verification_id": "fixture-verification",
                "evidence_id": "fixture-evidence",
                "verification_status": "PENDING",
                "verification_level": "V0",
                "permission_status": "GRANTED",
            }
        )
        self.assertTrue(any("grant fields" in error for error in errors))

    def test_verification_cannot_auto_pass(self) -> None:
        with self.assertRaises(ValueError):
            build_verification_reference(
                verification_id="fixture-verification",
                evidence_id="fixture-evidence",
                verification_status="PASS",
            )


if __name__ == "__main__":
    unittest.main()
