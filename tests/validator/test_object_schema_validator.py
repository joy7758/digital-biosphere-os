import unittest

from validator.object_schema_validator import (
    ObjectSchemaValidator,
    SchemaRegistryError,
    validate_object,
)
from validator.validation_result_model import ValidationStatus
from tests.schema_validator.fixtures import (
    synthetic_entity,
    synthetic_verification,
)


class TestObjectSchemaValidator(unittest.TestCase):
    def test_initialization_invalid_schema_dir(self):
        with self.assertRaises(SchemaRegistryError):
            ObjectSchemaValidator(schema_directory="/invalid/path")

    def test_non_dictionary_target(self):
        result = validate_object("not-a-dict")
        self.assertEqual(result.result, ValidationStatus.FAIL)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].rule, "target_is_object")

    def test_missing_object_type(self):
        target = synthetic_entity()
        del target["object_type"]
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.FAIL)
        self.assertEqual(result.errors[0].rule, "core_object_type_allowlist")

    def test_invalid_object_type(self):
        target = synthetic_entity()
        target["object_type"] = "INVALID_TYPE"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.FAIL)
        self.assertEqual(result.errors[0].rule, "core_object_type_allowlist")

    def test_offline_schema_registry_unknown_schema(self):
        target = synthetic_entity()
        result = validate_object(target, schema_id="dbio://schema/unknown/v0.1")
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        self.assertEqual(result.errors[0].rule, "offline_schema_registry")

    def test_schema_object_type_consistency_conflict(self):
        target = synthetic_entity()
        # Entity object but validated against Capability schema
        result = validate_object(
            target, schema_id="dbio://schema/capability-object/v0.1"
        )
        self.assertEqual(result.result, ValidationStatus.CONFLICT)
        self.assertEqual(result.errors[0].rule, "schema_object_type_consistency")

    def test_id_consistency(self):
        target = synthetic_entity()
        target["object_id"] = "different-id"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.CONFLICT)
        errors_with_rule = [
            e for e in result.errors if e.rule == "object_id_equals_type_specific_id"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_timestamp_ordering(self):
        target = synthetic_entity()
        target["created_at"] = "2026-01-02T00:00:00Z"
        target["updated_at"] = "2026-01-01T00:00:00Z"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.FAIL)
        errors_with_rule = [
            e for e in result.errors if e.rule == "updated_at_not_before_created_at"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_empty_limitations(self):
        target = synthetic_entity()
        target["limitations"] = []
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e
            for e in result.errors
            if e.rule == "empty_limitations_require_attributed_source_assertion"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_entity_lifecycle_state(self):
        target = synthetic_entity()
        target["lifecycle_state"] = "ACTIVE"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e for e in result.errors if e.rule == "active_is_source_assertion_only"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_verification_invariants_non_pending(self):
        target = synthetic_verification()
        target["verification_status"] = "PASS"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e
            for e in result.errors
            if e.rule == "non_pending_results_require_resolvable_verification_record"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_verification_invariants_independent(self):
        target = synthetic_verification()
        target["verification_type"] = "INDEPENDENT_VERIFICATION"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e
            for e in result.errors
            if e.rule == "independent_type_requires_independence_evidence"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_unknown_value_field(self):
        target = synthetic_entity()
        target["status"] = "UNKNOWN"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e for e in result.errors if e.rule == "unknown_remains_unknown"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_unknown_in_limitations(self):
        target = synthetic_entity()
        target["limitations"] = ["UNKNOWN"]
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        errors_with_rule = [
            e for e in result.errors if e.rule == "unknown_limitation_remains_unknown"
        ]
        self.assertTrue(len(errors_with_rule) > 0)

    def test_version_mismatch(self):
        target = synthetic_entity()
        target["version"] = "v0.2"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.VERSION_MISMATCH)
        errors_with_rule = [
            e for e in result.errors if e.rule == "object_contract_version_v0_1"
        ]
        self.assertTrue(len(errors_with_rule) > 0)


if __name__ == "__main__":
    unittest.main()
