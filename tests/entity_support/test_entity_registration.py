"""Tests for non-persistent Digital Entity registration support."""

from __future__ import annotations

import unittest

from entity_support.entity_registry import (
    ENTITY_REGISTRATION_FIELDS,
    build_entity_registration_record,
    validate_entity_registration,
)


class EntityRegistrationTests(unittest.TestCase):
    def test_registration_defaults_to_proposed(self) -> None:
        record = build_entity_registration_record(
            entity_id="fixture-entity",
            entity_type="service",
            owner_reference="fixture-owner",
        )
        self.assertEqual(record["lifecycle_state"], "PROPOSED")
        self.assertEqual(tuple(record), ENTITY_REGISTRATION_FIELDS)

    def test_registration_rejects_active(self) -> None:
        with self.assertRaises(ValueError):
            build_entity_registration_record(
                entity_id="fixture-entity",
                entity_type="service",
                owner_reference="fixture-owner",
                lifecycle_state="ACTIVE",
            )

    def test_registration_rejects_unsupported_entity_type(self) -> None:
        with self.assertRaises(ValueError):
            build_entity_registration_record(
                entity_id="fixture-entity",
                entity_type="digital_organism",
                owner_reference="fixture-owner",
            )

    def test_registration_rejects_embedded_permission(self) -> None:
        errors = validate_entity_registration(
            {
                "entity_id": "fixture-entity",
                "entity_type": "service",
                "owner_reference": "fixture-owner",
                "lifecycle_state": "PROPOSED",
                "permission_status": "GRANTED",
            }
        )
        self.assertTrue(any("unexpected fields" in error for error in errors))

    def test_validation_reports_missing_fields(self) -> None:
        errors = validate_entity_registration(
            {
                "entity_id": "fixture-entity",
                "lifecycle_state": "PROPOSED",
            }
        )
        self.assertTrue(any("missing fields" in error for error in errors))

    def test_validation_rejects_empty_entity_id(self) -> None:
        errors = validate_entity_registration(
            {
                "entity_id": "   ",
                "entity_type": "service",
                "owner_reference": "fixture-owner",
                "lifecycle_state": "PROPOSED",
            }
        )
        self.assertTrue(any("entity_id must be a non-empty string" in error for error in errors))

    def test_validation_rejects_empty_owner_reference(self) -> None:
        errors = validate_entity_registration(
            {
                "entity_id": "fixture-entity",
                "entity_type": "service",
                "owner_reference": "",
                "lifecycle_state": "PROPOSED",
            }
        )
        self.assertTrue(any("owner_reference must be a non-empty string" in error for error in errors))

    def test_validation_accumulates_multiple_errors(self) -> None:
        errors = validate_entity_registration(
            {
                "entity_id": "",
                "entity_type": "invalid_type",
                "owner_reference": "  ",
                "lifecycle_state": "ACTIVE",
            }
        )
        self.assertEqual(len(errors), 4)
        self.assertTrue(any("entity_id must be a non-empty string" in error for error in errors))
        self.assertTrue(any("entity_type must use" in error for error in errors))
        self.assertTrue(any("owner_reference must be a non-empty string" in error for error in errors))
        self.assertTrue(any("registration support requires lifecycle_state=PROPOSED" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
