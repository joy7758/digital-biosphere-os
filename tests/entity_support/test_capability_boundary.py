"""Tests for capability declarations that do not grant capability or permission."""

from __future__ import annotations

import unittest

from entity_support.capability_registry import (
    CAPABILITY_RECORD_FIELDS,
    build_capability_record,
    validate_capability_record,
)


class CapabilityBoundaryTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "capability_id": "fixture-capability",
            "entity_id": "fixture-entity",
            "capability_name": "fixture-declaration",
            "scope": {"mode": "fixture-only"},
            "constraints": ["no execution", "no permission"],
        }
        values.update(overrides)
        return build_capability_record(**values)

    def test_capability_has_safe_defaults(self) -> None:
        record = self._build()
        self.assertEqual(record["risk_level"], "UNKNOWN")
        self.assertEqual(record["verification_status"], "UNVERIFIED")
        self.assertEqual(tuple(record), CAPABILITY_RECORD_FIELDS)

    def test_capability_record_has_no_grant_fields(self) -> None:
        record = self._build()
        self.assertNotIn("permission", record)
        self.assertNotIn("authorization", record)

    def test_capability_rejects_authorized_status(self) -> None:
        with self.assertRaises(ValueError):
            self._build(verification_status="AUTHORIZED")

    def test_capability_rejects_embedded_permission(self) -> None:
        record = self._build()
        errors = validate_capability_record({**record, "permission": "GRANTED"})
        self.assertTrue(any("unexpected fields" in error for error in errors))

    def test_capability_rejects_unbounded_risk_vocabulary(self) -> None:
        with self.assertRaises(ValueError):
            self._build(risk_level="AUTO_APPROVED")


if __name__ == "__main__":
    unittest.main()
