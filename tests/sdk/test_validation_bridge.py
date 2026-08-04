"""Canonical Validator bridge and error-wrapper tests."""

from __future__ import annotations

import unittest

from fixtures import all_objects, entity_object
from sdk.errors import SDKErrorCode, validation_failure_from_result
from sdk.validation import validate_object
from validator import ValidationStatus


class ValidationBridgeTests(unittest.TestCase):
    def test_all_five_synthetic_objects_pass_local_validation(self) -> None:
        for target in all_objects():
            with self.subTest(object_type=target.object_type):
                self.assertEqual(validate_object(target).result, ValidationStatus.PASS)

    def test_returns_nine_field_validation_result_contract(self) -> None:
        result = validate_object(entity_object()).to_dict()
        self.assertEqual(
            set(result),
            {
                "validation_id",
                "validator_version",
                "target_reference",
                "schema_reference",
                "result",
                "errors",
                "warnings",
                "limitations",
                "timestamp",
            },
        )

    def test_identifier_conflict_is_not_repaired(self) -> None:
        target = entity_object(entity_id="dbio://repository/conflict/v0.1")
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.CONFLICT)
        self.assertEqual(target.entity_id, "dbio://repository/conflict/v0.1")

    def test_unknown_remains_unknown(self) -> None:
        result = validate_object(entity_object(lifecycle_state="UNKNOWN"))
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)

    def test_version_mismatch_remains_version_mismatch(self) -> None:
        result = validate_object(entity_object(version="v9.9"))
        self.assertEqual(result.result, ValidationStatus.VERSION_MISMATCH)

    def test_pass_maps_to_no_failure(self) -> None:
        self.assertIsNone(validation_failure_from_result(validate_object(entity_object())))

    def test_non_pass_statuses_map_without_auto_repair(self) -> None:
        cases = (
            (entity_object(entity_id="conflict"), SDKErrorCode.CONFLICT),
            (entity_object(lifecycle_state="UNKNOWN"), SDKErrorCode.UNKNOWN),
            (entity_object(version="v9.9"), SDKErrorCode.VERSION_MISMATCH),
            (entity_object(status="NOT_ALLOWED"), SDKErrorCode.FAIL),
        )
        for target, expected in cases:
            with self.subTest(expected=expected):
                failure = validation_failure_from_result(validate_object(target))
                self.assertIsNotNone(failure)
                self.assertEqual(failure.code, expected)
                self.assertFalse(failure.auto_repair_performed)


    def test_unmapped_base_object_fails_validation(self) -> None:
        from sdk.objects.base import BaseObject

        target = BaseObject(
            object_id="dbio://repository/unmapped/v0.1",
            source={},
            status="ACTIVE",
            limitations=["none"],
        )
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.FAIL)
        self.assertEqual(result.errors[0].code, "INVALID")
        self.assertEqual(result.errors[0].path, "$.object_type")

    def test_rejects_raw_mapping_to_prevent_bridge_bypass(self) -> None:
        with self.assertRaises(TypeError):
            validate_object({"object_type": "ENTITY"})  # type: ignore[arg-type]

    def test_rejects_unmapped_base_object_type(self) -> None:
        from sdk.objects.base import BaseObject

        # BaseObject sets object_type="UNKNOWN" by default.
        target = BaseObject(
            object_id="dbio://test/invalid/v0.1",
            source={"namespace": "dbio", "source_id": "test", "version": "v0.1", "status": "DECLARED"},
            status="DECLARED",
            limitations=[],
        )
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.FAIL)

        # Verify that we correctly get an error complaining about $.object_type
        object_type_errors = [e for e in result.errors if e.path == "$.object_type"]
        self.assertGreater(len(object_type_errors), 0, "Expected an error pointing to $.object_type")
        self.assertEqual(object_type_errors[0].code, "INVALID")



    def test_schema_id_is_passed_to_validator(self) -> None:
        target = entity_object()
        result = validate_object(target, schema_id="dbio://schema/capability-object/v0.1")
        self.assertEqual(result.result, ValidationStatus.CONFLICT)


if __name__ == "__main__":
    unittest.main()
