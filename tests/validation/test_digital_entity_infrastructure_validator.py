"""Tests for digital_entity_infrastructure_validator."""

from __future__ import annotations

import unittest
from unittest.mock import patch
import json
import io

from validation.digital_entity_infrastructure_validator import validate, _must_reject, main


class TestDigitalEntityInfrastructureValidator(unittest.TestCase):
    def test_must_reject_unexpected_exception(self) -> None:
        errors: list[str] = []

        def raiser() -> None:
            raise TypeError("test exception")

        result = _must_reject("test_name", raiser, errors)
        self.assertFalse(result)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "test_name: unexpected TypeError: test exception")

    def test_must_reject_prohibited_construction_accepted(self) -> None:
        errors: list[str] = []
        result = _must_reject("test_name", lambda: None, errors)
        self.assertFalse(result)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], "test_name: prohibited construction was accepted")

    @patch("validation.digital_entity_infrastructure_validator.build_entity_registration_record")
    def test_validate_expected_values_mismatch(self, mock_build) -> None:
        mock_build.return_value = {"lifecycle_state": "INVALID"}
        result = validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("entity.lifecycle_state: expected 'PROPOSED', found 'INVALID'", result["errors"])

    @patch("validation.digital_entity_infrastructure_validator.validate_research_agent_preparation_template")
    def test_research_template_entity_instance_accepted(self, mock_validate) -> None:
        mock_validate.return_value = []
        result = validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("research_template_entity_instance: entity_id was accepted", result["errors"])

    @patch("validation.digital_entity_infrastructure_validator.validate_saee_evaluation_envelope")
    def test_saee_adapter_fitness_generation_accepted(self, mock_validate) -> None:
        mock_validate.return_value = []
        result = validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("saee_adapter_fitness_generation: fitness field was accepted", result["errors"])

    @patch("validation.digital_entity_infrastructure_validator.validate_verification_reference")
    def test_verification_permission_derivation_accepted(self, mock_validate) -> None:
        mock_validate.return_value = []
        result = validate()
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("verification_permission_derivation: permission field was accepted", result["errors"])

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.argv", ["script", "--format", "json"])
    def test_main_json_format_pass(self, mock_stdout) -> None:
        return_code = main()
        self.assertEqual(return_code, 0)
        output = mock_stdout.getvalue()
        data = json.loads(output)
        self.assertEqual(data["status"], "PASS")

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.argv", ["script", "--format", "text"])
    def test_main_text_format_pass(self, mock_stdout) -> None:
        return_code = main()
        self.assertEqual(return_code, 0)
        output = mock_stdout.getvalue()
        self.assertIn("digital_entity_infrastructure_validator: PASS", output)

    @patch("validation.digital_entity_infrastructure_validator.validate")
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.argv", ["script", "--format", "text"])
    def test_main_text_format_fail(self, mock_stdout, mock_validate) -> None:
        mock_validate.return_value = {
            "status": "FAIL",
            "rejected_negative_case_count": 0,
            "negative_case_count": 1,
            "errors": ["test error"]
        }
        return_code = main()
        self.assertEqual(return_code, 1)
        output = mock_stdout.getvalue()
        self.assertIn("digital_entity_infrastructure_validator: FAIL", output)
        self.assertIn("- test error", output)

if __name__ == "__main__":
    unittest.main()
