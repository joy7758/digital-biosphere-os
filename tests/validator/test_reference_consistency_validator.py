import unittest
from validator.reference_consistency_validator import (
    _validate_reference,
    validate_reference_consistency,
)

class TestReferenceConsistencyValidator(unittest.TestCase):
    def test_dbio_reference_type_allowlist_invalid(self):
        """Test that a dbio namespace reference must have a known reference type."""
        reference = {
            "reference_id": "ref-1",
            "reference_type": "UNKNOWN_TYPE",
            "namespace": "dbio",
            "version": "v0.1",
            "source": "source-1",
            "status": "ACTIVE"
        }

        issues = _validate_reference(reference, "$.test_path", expected_type=None)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "INVALID")
        self.assertEqual(issues[0].rule, "dbio_reference_type_allowlist")
        self.assertEqual(issues[0].path, "$.test_path.reference_type")
        self.assertIn("does not define this canonical reference type", issues[0].message)

    def test_dbio_reference_type_allowlist_valid(self):
        """Test that a valid dbio reference type passes validation."""
        reference = {
            "reference_id": "ref-1",
            "reference_type": "ENTITY",
            "namespace": "dbio",
            "version": "v0.1",
            "source": "source-1",
            "status": "ACTIVE"
        }

        issues = _validate_reference(reference, "$.test_path", expected_type="ENTITY")

        self.assertEqual(len(issues), 0)

    def test_validate_reference_consistency_happy_path(self):
        """Test happy path where reference fields are valid."""
        target = {
            "object_type": "ENTITY",
            "source_reference": {
                "reference_id": "ref-1",
                "reference_type": "ENTITY",
                "namespace": "dbio",
                "version": "v0.1",
                "source": "source-1",
                "status": "ACTIVE"
            }
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 0)

    def test_validate_reference_consistency_missing_fields(self):
        """Test target missing reference fields."""
        target = {
            "object_type": "ENTITY"
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 0)

    def test_validate_reference_consistency_execution_null_output(self):
        """Test that output_reference can be None for EXECUTION."""
        target = {
            "object_type": "EXECUTION",
            "output_reference": None
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 0)

    def test_validate_reference_consistency_expected_type_mismatch(self):
        """Test validation failure due to expected_type mismatch."""
        target = {
            "object_type": "ENTITY",
            "source_reference": {
                "reference_id": "ref-1",
                "reference_type": "CANDIDATE",
                "namespace": "dbio",
                "version": "v0.1",
                "source": "source-1",
                "status": "ACTIVE"
            }
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "INVALID")
        self.assertEqual(issues[0].rule, "reference_role_consistency")

    def test_validate_reference_consistency_source_conflict_namespace(self):
        """Test conflict when source namespace differs from source_reference namespace."""
        target = {
            "object_type": "ENTITY",
            "source": {
                "namespace": "dbio",
                "source_id": "source-1"
            },
            "source_reference": {
                "reference_id": "ref-1",
                "reference_type": "ENTITY",
                "version": "v0.1",
                "status": "ACTIVE",
                "namespace": "other",
                "source": "source-1"
            }
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "CONFLICT")
        self.assertEqual(issues[0].rule, "source_reference_owner_consistency")
        self.assertIn("namespace", issues[0].message)

    def test_validate_reference_consistency_source_conflict_source(self):
        """Test conflict when source_id differs from source_reference source."""
        target = {
            "object_type": "ENTITY",
            "source": {
                "namespace": "dbio",
                "source_id": "source-1"
            },
            "source_reference": {
                "reference_id": "ref-1",
                "reference_type": "ENTITY",
                "version": "v0.1",
                "status": "ACTIVE",
                "namespace": "dbio",
                "source": "source-2"
            }
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].code, "CONFLICT")
        self.assertEqual(issues[0].rule, "source_reference_owner_consistency")
        self.assertIn("owner", issues[0].message)

    def test_validate_reference_consistency_source_success(self):
        """Test successful combination of source and source_reference without conflict."""
        target = {
            "object_type": "ENTITY",
            "source": {
                "namespace": "dbio",
                "source_id": "source-1"
            },
            "source_reference": {
                "reference_id": "ref-1",
                "reference_type": "ENTITY",
                "version": "v0.1",
                "status": "ACTIVE",
                "namespace": "dbio",
                "source": "source-1"
            }
        }
        issues = validate_reference_consistency(target)
        self.assertEqual(len(issues), 0)


if __name__ == '__main__':
    unittest.main()
