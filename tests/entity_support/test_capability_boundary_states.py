"""Tests for declared, verified, and authorized capability record states."""

from __future__ import annotations

import unittest

from entity_support.capability_boundary import (
    build_capability_boundary_record,
    validate_capability_boundary,
)


class CapabilityBoundaryStateTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "boundary_record_id": "fixture-boundary",
            "capability_id": "fixture-capability",
            "entity_id": "fixture-entity",
            "capability_name": "fixture-declaration",
            "scope": {"mode": "fixture-only"},
            "constraints": ["no execution", "no permission"],
            "declaration_reference": "fixture-declaration-reference",
        }
        values.update(overrides)
        return build_capability_boundary_record(**values)

    def test_default_state_is_declared(self) -> None:
        record = self._build()
        self.assertEqual(record["capability_state"], "DECLARED")
        self.assertEqual(record["permission_effect"], "NONE")

    def test_declared_rejects_verification_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._build(verification_reference="fixture-verification")

    def test_verified_requires_verification_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._build(capability_state="VERIFIED")

    def test_verified_record_has_no_authorization_or_permission(self) -> None:
        record = self._build(
            capability_state="VERIFIED",
            verification_reference="fixture-verification",
        )
        self.assertIsNone(record["authorization_reference"])
        self.assertEqual(record["permission_effect"], "NONE")

    def test_authorized_requires_separate_authorization_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                capability_state="AUTHORIZED",
                verification_reference="fixture-verification",
            )

    def test_authorized_record_still_has_no_permission_effect(self) -> None:
        record = self._build(
            capability_state="AUTHORIZED",
            verification_reference="fixture-verification",
            authorization_reference="fixture-authorization",
        )
        self.assertEqual(record["capability_state"], "AUTHORIZED")
        self.assertEqual(record["permission_effect"], "NONE")
        self.assertNotIn("permission_status", record)

    def test_permission_effect_cannot_be_expanded(self) -> None:
        with self.assertRaises(ValueError):
            self._build(permission_effect="GRANTED")

    def test_embedded_permission_field_is_rejected(self) -> None:
        record = self._build()
        errors = validate_capability_boundary({**record, "permission_status": "GRANTED"})
        self.assertTrue(any("permission fields" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
