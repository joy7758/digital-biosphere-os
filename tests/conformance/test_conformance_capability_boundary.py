"""Conformance tests for Capability, Authorization, and Permission separation."""

from __future__ import annotations

import unittest

from entity_support.capability_boundary import build_capability_boundary_record


class CapabilityBoundaryConformanceTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "boundary_record_id": "fixture-boundary",
            "capability_id": "fixture-capability",
            "entity_id": "fixture-entity",
            "capability_name": "fixture-declaration",
            "scope": {"mode": "fixture-only"},
            "constraints": ["no permission"],
            "declaration_reference": "fixture-declaration-reference",
        }
        values.update(overrides)
        return build_capability_boundary_record(**values)

    def test_declared_capability_has_no_permission(self) -> None:
        record = self._build()
        self.assertEqual(record["capability_state"], "DECLARED")
        self.assertEqual(record["permission_effect"], "NONE")

    def test_authorized_record_requires_separate_references(self) -> None:
        record = self._build(
            capability_state="AUTHORIZED",
            verification_reference="fixture-verification",
            authorization_reference="fixture-authorization",
        )
        self.assertEqual(record["permission_effect"], "NONE")

    def test_capability_cannot_grant_permission(self) -> None:
        with self.assertRaises(ValueError):
            self._build(permission_effect="GRANTED")


if __name__ == "__main__":
    unittest.main()
