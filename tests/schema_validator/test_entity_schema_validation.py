"""Entity Object structural and semantic validation tests."""

from __future__ import annotations

from copy import deepcopy
import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_entity


class EntitySchemaValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_synthetic_entity(self) -> None:
        result = validate_object(synthetic_entity())
        self.assertEqual(result.result, ValidationStatus.PASS)
        self.assertEqual(
            result.schema_reference.schema_id,
            "dbio://schema/entity-object/v0.1",
        )
        self.assertTrue(result.schema_reference.schema_digest.startswith("sha256:"))

    def test_rejects_missing_required_field(self) -> None:
        target = synthetic_entity()
        del target["owner_reference"]
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_wrong_identifier_type(self) -> None:
        target = synthetic_entity()
        target["entity_id"] = 42
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_reports_identifier_conflict(self) -> None:
        target = synthetic_entity()
        target["entity_id"] = "dbio://repository/conflicting-fixture/v0.1"
        self.assertEqual(validate_object(target).result, ValidationStatus.CONFLICT)

    def test_preserves_elevated_state_as_unknown_without_evidence(self) -> None:
        target = synthetic_entity()
        target["lifecycle_state"] = "ACTIVE"
        self.assertEqual(validate_object(target).result, ValidationStatus.UNKNOWN)

    def test_does_not_mutate_input(self) -> None:
        target = synthetic_entity()
        before = deepcopy(target)
        validate_object(target)
        self.assertEqual(target, before)


if __name__ == "__main__":
    unittest.main()
