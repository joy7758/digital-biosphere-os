"""Negative non-effect tests for the Validation Result Contract."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import unittest

from validator import ValidationIssue, ValidationResult, ValidationStatus, validate_object

from fixtures import synthetic_entity


PROHIBITED_RESULT_FIELDS = {
    "agent",
    "authorization",
    "entity",
    "execution",
    "permission",
    "runtime",
    "saee",
}


class NegativeBoundaryTests(unittest.TestCase):
    def test_result_creates_no_permission(self) -> None:
        self.assertTrue(PROHIBITED_RESULT_FIELDS.isdisjoint(validate_object(synthetic_entity()).to_dict()))

    def test_result_creates_no_entity(self) -> None:
        payload = validate_object(synthetic_entity()).to_dict()
        self.assertNotIn("entity", payload)
        self.assertNotIn("entity_created", payload)

    def test_result_triggers_no_execution(self) -> None:
        payload = validate_object(synthetic_entity()).to_dict()
        self.assertNotIn("execution", payload)
        self.assertNotIn("execute", payload)

    def test_result_calls_no_saee(self) -> None:
        payload = validate_object(synthetic_entity()).to_dict()
        self.assertNotIn("saee", payload)
        self.assertNotIn("evolution", payload)

    def test_pass_creates_no_authorization(self) -> None:
        payload = validate_object(synthetic_entity()).to_dict()
        self.assertEqual(payload["result"], "PASS")
        self.assertNotIn("authorization", payload)

    def test_fail_does_not_modify_target_or_history(self) -> None:
        target = synthetic_entity()
        target["unexpected_field"] = True
        before = deepcopy(target)
        validate_object(target)
        self.assertEqual(target, before)

    def test_unknown_cannot_be_used_as_pass(self) -> None:
        target = synthetic_entity()
        target["status"] = "UNKNOWN"
        result = validate_object(target)
        self.assertEqual(result.result, ValidationStatus.UNKNOWN)
        self.assertFalse(result.passed)

    def test_resolution_hint_is_data_not_executable_repair(self) -> None:
        target = synthetic_entity()
        del target["entity_id"]
        payload = validate_object(target).to_dict()
        for issue in payload["errors"]:
            self.assertIsInstance(issue["resolution_hint"], str)
            self.assertNotIn("command", issue)
            self.assertNotIn("patch", issue)

    def test_warning_cannot_change_primary_result(self) -> None:
        warning = ValidationIssue(
            code="UNKNOWN",
            path="$.source",
            message="Synthetic warning only.",
            rule="synthetic_warning",
            severity="WARNING",
        )
        result = ValidationResult(
            validator_version="v0.1",
            target_reference="dbio://repository/synthetic-warning/v0.1",
            result=ValidationStatus.PASS,
            errors=(),
            warnings=(warning,),
        )
        self.assertEqual(result.result, ValidationStatus.PASS)
        self.assertEqual(result.to_dict()["warnings"][0]["severity"], "WARNING")

    def test_result_is_immutable(self) -> None:
        result = validate_object(synthetic_entity())
        with self.assertRaises(FrozenInstanceError):
            result.result = ValidationStatus.FAIL

    def test_non_pass_without_error_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ValidationResult(
                validator_version="v0.1",
                target_reference=None,
                result=ValidationStatus.UNKNOWN,
                errors=(),
            )


if __name__ == "__main__":
    unittest.main()
