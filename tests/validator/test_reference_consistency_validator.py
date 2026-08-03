import unittest
from validator.reference_consistency_validator import _validate_reference

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

if __name__ == '__main__':
    unittest.main()
