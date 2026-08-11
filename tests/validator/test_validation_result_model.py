import unittest
from validator.validation_result_model import ValidationResult, ValidationStatus, ValidationIssue

class TestValidationResultModel(unittest.TestCase):
    def test_passed_property_true(self):
        result = ValidationResult(
            validator_version="v0.1",
            target_reference="dbio://target/test",
            result=ValidationStatus.PASS,
            errors=()
        )
        self.assertTrue(result.passed)

    def test_passed_property_false(self):
        result = ValidationResult(
            validator_version="v0.1",
            target_reference="dbio://target/test",
            result=ValidationStatus.FAIL,
            errors=(ValidationIssue(code="test", path="test", message="test", rule="test"),)
        )
        self.assertFalse(result.passed)

    def test_timestamp_invalid_format(self):
        with self.assertRaisesRegex(ValueError, "timestamp must be an RFC 3339 string"):
            ValidationResult(
                validator_version="v0.1",
                target_reference="dbio://target/test",
                result=ValidationStatus.PASS,
                errors=(),
                timestamp="invalid-timestamp"
            )

if __name__ == '__main__':
    unittest.main()
