"""Execution Object inert-record validation tests."""

from __future__ import annotations

from copy import deepcopy
import unittest

from validator import ValidationStatus, validate_object

from fixtures import synthetic_execution


class ExecutionSchemaValidationTests(unittest.TestCase):
    def test_accepts_structurally_valid_synthetic_execution_record(self) -> None:
        self.assertEqual(validate_object(synthetic_execution()).result, ValidationStatus.PASS)

    def test_rejects_execution_result_claim(self) -> None:
        target = synthetic_execution()
        target["result"] = "PASS"
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_rejects_non_object_input_reference(self) -> None:
        target = synthetic_execution()
        target["input_reference"] = "dbio://evidence/not-an-envelope/v0.1"
        self.assertEqual(validate_object(target).result, ValidationStatus.FAIL)

    def test_reports_version_mismatch(self) -> None:
        target = synthetic_execution()
        target["version"] = "v9.9"
        self.assertEqual(validate_object(target).result, ValidationStatus.VERSION_MISMATCH)

    def test_does_not_mutate_input(self) -> None:
        target = synthetic_execution()
        before = deepcopy(target)
        validate_object(target)
        self.assertEqual(target, before)


if __name__ == "__main__":
    unittest.main()
