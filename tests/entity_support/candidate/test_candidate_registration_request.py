"""Tests for candidate registration request validation."""

import unittest

from entity_support.candidate.candidate_registration_request import (
    validate_candidate_registration_request,
)


class TestCandidateRegistrationRequestValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_record = {
            "request_id": "req-123",
            "candidate_id": "cand-456",
            "requested_entity_type": "agent",
            "mapping_reference": "map-789",
            "status": "CREATED",
        }

    def test_valid_request(self) -> None:
        errors = validate_candidate_registration_request(self.valid_record)
        self.assertEqual(errors, [])

    def test_missing_fields(self) -> None:
        del self.valid_record["request_id"]
        errors = validate_candidate_registration_request(self.valid_record)
        # We expect a missing fields error and also a non-empty string error for request_id
        self.assertEqual(len(errors), 2)
        self.assertTrue(errors[0].startswith("missing fields: ['request_id']"))
        self.assertEqual(errors[1], "request_id must be a non-empty string")

    def test_unexpected_fields(self) -> None:
        self.valid_record["extra_field"] = "value"
        errors = validate_candidate_registration_request(self.valid_record)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("unexpected fields: ['extra_field']"))

    def test_invalid_string_fields(self) -> None:
        for field in ("request_id", "candidate_id", "mapping_reference"):
            with self.subTest(field=field):
                invalid_record = self.valid_record.copy()
                invalid_record[field] = ""
                errors = validate_candidate_registration_request(invalid_record)
                self.assertIn(f"{field} must be a non-empty string", errors)

                invalid_record[field] = None
                errors = validate_candidate_registration_request(invalid_record)
                self.assertIn(f"{field} must be a non-empty string", errors)

    def test_invalid_entity_type(self) -> None:
        self.valid_record["requested_entity_type"] = "invalid_type"
        errors = validate_candidate_registration_request(self.valid_record)
        self.assertIn(
            "requested_entity_type must use the existing DBOS classification", errors
        )

    def test_invalid_status(self) -> None:
        self.valid_record["status"] = "INVALID_STATUS"
        errors = validate_candidate_registration_request(self.valid_record)
        self.assertIn("status is not supported", errors)


if __name__ == "__main__":
    unittest.main()
