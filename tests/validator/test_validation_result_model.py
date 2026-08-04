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

if __name__ == '__main__':
    unittest.main()
