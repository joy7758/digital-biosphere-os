"""Tests for edge cases in capability record validation."""

from __future__ import annotations

import unittest
from typing import Any

from entity_support.capability_registry import (
    validate_capability_record,
)


class CapabilityValidationEdgeCaseTests(unittest.TestCase):
    def _valid_record(self) -> dict[str, Any]:
        return {
            "capability_id": "test-cap-123",
            "entity_id": "test-entity-456",
            "capability_name": "Test Capability",
            "scope": {"region": "us-east-1"},
            "constraints": ["time-bound"],
            "risk_level": "LOW",
            "verification_status": "PENDING",
        }

    def test_missing_fields(self) -> None:
        record = self._valid_record()
        del record["capability_id"]
        del record["scope"]

        errors = validate_capability_record(record)
        self.assertTrue(any("missing fields" in e and "capability_id" in e for e in errors))
        self.assertTrue(any("missing fields" in e and "scope" in e for e in errors))

    def test_unexpected_fields(self) -> None:
        record = self._valid_record()
        record["unknown_field"] = "value"
        record["another_one"] = 123

        errors = validate_capability_record(record)
        self.assertTrue(any("unexpected fields" in e and "unknown_field" in e for e in errors))

    def test_unexpected_mixed_type_fields(self) -> None:
        record = self._valid_record()
        record[123] = "numeric key"
        record[None] = "none key"

        # This would previously raise TypeError during sorting mixed types
        errors = validate_capability_record(record)
        self.assertTrue(any("unexpected fields" in e and "123" in e for e in errors))
        self.assertTrue(any("unexpected fields" in e and "None" in e for e in errors))

    def test_empty_string_fields(self) -> None:
        for field in ("capability_id", "entity_id", "capability_name"):
            record = self._valid_record()
            record[field] = "   "  # Only whitespace
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be a non-empty string" in e for e in errors))

            record[field] = ""  # Empty string
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be a non-empty string" in e for e in errors))

    def test_invalid_string_field_types(self) -> None:
        for field in ("capability_id", "entity_id", "capability_name"):
            record = self._valid_record()
            record[field] = 123  # Int instead of string
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be a non-empty string" in e for e in errors))

            record[field] = None
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be a non-empty string" in e for e in errors))

    def test_empty_structures(self) -> None:
        for field in ("scope", "constraints"):
            record = self._valid_record()

            # Empty dict
            record[field] = {}
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

            # Empty list
            record[field] = []
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

            # Empty string
            record[field] = "   "
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

    def test_invalid_structure_types(self) -> None:
        for field in ("scope", "constraints"):
            record = self._valid_record()

            # Integer
            record[field] = 123
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

            # Boolean
            record[field] = True
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

            # None
            record[field] = None
            errors = validate_capability_record(record)
            self.assertTrue(any(f"{field} must be an explicit non-empty structure" in e for e in errors))

    def test_invalid_risk_level(self) -> None:
        record = self._valid_record()
        record["risk_level"] = "SUPER_HIGH"
        errors = validate_capability_record(record)
        self.assertTrue(any("risk_level must use the bounded DBOS risk vocabulary" in e for e in errors))

    def test_invalid_verification_status(self) -> None:
        record = self._valid_record()
        record["verification_status"] = "DONE"
        errors = validate_capability_record(record)
        self.assertTrue(any("verification_status must remain UNVERIFIED or PENDING" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
