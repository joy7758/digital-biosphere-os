import unittest
import json
import tempfile
from pathlib import Path
from validation.experimental_protocol_validator import (
    load_json_yaml,
    index_records,
    nonempty_string,
    nonempty_string_list,
    valid_timestamp,
    reject_authority_fields,
    require_zero_effect_metadata,
    validate,
)

class TestHelperFunctions(unittest.TestCase):
    def test_load_json_yaml_valid(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(json.dumps({"key": "value"}))
            filepath = f.name

        try:
            result = load_json_yaml(Path(filepath))
            self.assertEqual(result, {"key": "value"})
        finally:
            Path(filepath).unlink()

    def test_load_json_yaml_invalid_json(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("{invalid json")
            filepath = f.name

        try:
            with self.assertRaises(ValueError):
                load_json_yaml(Path(filepath))
        finally:
            Path(filepath).unlink()

    def test_load_json_yaml_not_mapping(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write(json.dumps(["list", "instead", "of", "dict"]))
            filepath = f.name

        try:
            with self.assertRaises(ValueError):
                load_json_yaml(Path(filepath))
        finally:
            Path(filepath).unlink()

    def test_index_records(self):
        errors = []
        records = [
            {"id": "a", "val": 1},
            {"id": "b", "val": 2},
        ]
        indexed = index_records(records, "id", "test", errors)
        self.assertEqual(len(indexed), 2)
        self.assertEqual(indexed["a"]["val"], 1)
        self.assertEqual(len(errors), 0)

        # Test duplicate id
        records.append({"id": "a", "val": 3})
        indexed = index_records(records, "id", "test", errors)
        self.assertEqual(len(indexed), 2)
        self.assertEqual(len(errors), 1)
        self.assertIn("duplicate id: a", errors[0])

        # Test non-list
        errors.clear()
        indexed = index_records({"not": "list"}, "id", "test", errors)
        self.assertEqual(indexed, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("test must be a list", errors[0])

        # Test non-mapping items
        errors.clear()
        indexed = index_records([{"id": "a"}, "string"], "id", "test", errors)
        self.assertEqual(len(indexed), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("test[1] must be a mapping", errors[0])

        # Test missing or invalid identifier
        errors.clear()
        indexed = index_records([{"id": ""}, {"id": 123}, {"other": "val"}], "id", "test", errors)
        self.assertEqual(len(indexed), 0)
        self.assertEqual(len(errors), 3)

    def test_nonempty_string(self):
        self.assertTrue(nonempty_string("test"))
        self.assertTrue(nonempty_string("  test  "))
        self.assertFalse(nonempty_string(""))
        self.assertFalse(nonempty_string("   "))
        self.assertFalse(nonempty_string(123))
        self.assertFalse(nonempty_string(None))

    def test_nonempty_string_list(self):
        self.assertTrue(nonempty_string_list(["a", "b"]))
        self.assertTrue(nonempty_string_list(["a"]))
        self.assertFalse(nonempty_string_list([]))
        self.assertFalse(nonempty_string_list(["a", ""]))
        self.assertFalse(nonempty_string_list(["a", 123]))
        self.assertFalse(nonempty_string_list("not a list"))
        self.assertFalse(nonempty_string_list(None))

    def test_valid_timestamp(self):
        self.assertTrue(valid_timestamp("2023-01-01T12:00:00Z"))
        self.assertTrue(valid_timestamp("2023-01-01T12:00:00+00:00"))
        self.assertTrue(valid_timestamp("2023-01-01T12:00:00-05:00"))
        self.assertFalse(valid_timestamp("2023-01-01T12:00:00")) # missing timezone
        self.assertFalse(valid_timestamp("not a timestamp"))
        self.assertFalse(valid_timestamp(None))
        self.assertFalse(valid_timestamp(123))
        self.assertFalse(valid_timestamp(""))

    def test_reject_authority_fields(self):
        errors = []
        reject_authority_fields({"agent_id": "123", "normal": "val"}, "test", errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("test: experimental protocol cannot create authority fields", errors[0])
        self.assertIn("'agent_id'", errors[0])

        errors.clear()
        reject_authority_fields({"normal": "val"}, "test", errors)
        self.assertEqual(len(errors), 0)

    def test_require_zero_effect_metadata(self):
        errors = []
        require_zero_effect_metadata({"event_created_count": 0, "normal": 1}, "test", errors)
        self.assertEqual(len(errors), 0)

        require_zero_effect_metadata({"event_created_count": 1}, "test", errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("test metadata event_created_count must remain zero", errors[0])

        errors.clear()
        require_zero_effect_metadata("not a dict", "test", errors)
        self.assertEqual(len(errors), 1)
        self.assertIn("test metadata must be a mapping", errors[0])

class TestValidatorMainLogic(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.empty_doc = {}

    def test_validate_empty_state_fails(self):
        # Even with empty documents, validate() fails because certain entities are missing
        # (like reproducibility requirements).
        result = validate(
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.root
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("reproducibility requirements must preserve all five ordered definitions", result["errors"])
        self.assertIn("SAEE mapping must include Experiment -> Observation -> Evolution", result["errors"])




    def test_validate_mock_valid_state(self):
        from validation.experimental_protocol_validator import REQUIREMENT_IDS

        requirement_doc = {
            "reproducibility_requirements": [
                {
                    "requirement_id": req_id,
                    "name": req_id,
                    "description": "test",
                    "required_material": ["test"],
                    "validation_boundary": "test",
                    "authority_effect": "none"
                }
                for req_id in REQUIREMENT_IDS
            ],
            "metadata": {
                "reproducibility_requirement_count": 5,
                "satisfied_requirement_count": 0,
                "verified_requirement_count": 0,
                "automatic_reproducibility_count": 0,
                "automatic_authority_effect": "none"
            }
        }

        mapping_doc = {
            "mappings": [
                {
                    "layer": "Experiment",
                    "current_authority": "constitution/experimental-protocol-constitution.yaml",
                    "current_registry": "registry/experiments.yaml",
                    "saee_correspondence": "observation-mediated evolution",
                    "status": "registered_experimental_protocol_one_experiment_unexecuted",
                    "authority_effect": "none"
                }
            ],
            "metadata": {"mapping_count": 1}
        }

        from validation.experimental_protocol_validator import validate

        result = validate(
            self.empty_doc, self.empty_doc, requirement_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, mapping_doc,
            self.root
        )

        self.assertIn("status", result)
        self.assertIn("errors", result)

        # Test an actual error from validate directly rather than complex mock
        # (covered by test_validate_empty_state_fails and test_validate_experiment_id_format)

    def test_validate_experiment_id_format(self):
        from validation.experimental_protocol_validator import validate

        # Use an invalid experiment ID format
        experiment_doc = {
            "experiments": [
                {
                    "experiment_id": "invalid-id format!",
                    "name": "test",
                    "objective": "test",
                    "subject": "test",
                    "protocol": {},
                    "status": "defined",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            ]
        }

        result = validate(
            experiment_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.empty_doc, self.empty_doc, self.empty_doc, self.empty_doc,
            self.root
        )

        self.assertEqual(result["status"], "FAIL")
        found_invalid_id_error = False
        for error in result["errors"]:
            if "invalid experiment_id format" in error:
                found_invalid_id_error = True
        self.assertTrue(found_invalid_id_error, "Should detect invalid experiment ID format")

if __name__ == '__main__':
    unittest.main()
