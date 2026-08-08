"""Tests for candidate registration request validation."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_registration_request import (
    build_candidate_registration_request,
    validate_candidate_registration_request,
)


class CandidateRegistrationRequestTests(unittest.TestCase):
    def test_valid_request(self) -> None:
        record = {
            "request_id": "req-1",
            "candidate_id": "cand-1",
            "requested_entity_type": "service",
            "mapping_reference": "map-1",
            "status": "CREATED",
        }
        errors = validate_candidate_registration_request(record)
        self.assertEqual(errors, [])

    def test_missing_fields(self) -> None:
        record = {
            "request_id": "req-1",
            "candidate_id": "cand-1",
            "requested_entity_type": "service",
            # missing mapping_reference and status
        }
        errors = validate_candidate_registration_request(record)
        self.assertTrue(any("missing fields" in e for e in errors))

    def test_extra_fields(self) -> None:
        record = {
            "request_id": "req-1",
            "candidate_id": "cand-1",
            "requested_entity_type": "service",
            "mapping_reference": "map-1",
            "status": "CREATED",
            "extra_field": "foo",
        }
        errors = validate_candidate_registration_request(record)
        self.assertTrue(any("unexpected fields" in e for e in errors))

    def test_invalid_strings(self) -> None:
        record = {
            "request_id": "",
            "candidate_id": "   ",
            "requested_entity_type": "service",
            "mapping_reference": None,
            "status": "CREATED",
        }
        errors = validate_candidate_registration_request(record)
        self.assertTrue(any("request_id must be a non-empty string" in e for e in errors))
        self.assertTrue(any("candidate_id must be a non-empty string" in e for e in errors))
        self.assertTrue(any("mapping_reference must be a non-empty string" in e for e in errors))

    def test_invalid_requested_entity_type(self) -> None:
        record = {
            "request_id": "req-1",
            "candidate_id": "cand-1",
            "requested_entity_type": "invalid_type",
            "mapping_reference": "map-1",
            "status": "CREATED",
        }
        errors = validate_candidate_registration_request(record)
        self.assertTrue(any("requested_entity_type must use the existing DBOS classification" in e for e in errors))

    def test_invalid_status(self) -> None:
        record = {
            "request_id": "req-1",
            "candidate_id": "cand-1",
            "requested_entity_type": "service",
            "mapping_reference": "map-1",
            "status": "INVALID_STATUS",
        }
        errors = validate_candidate_registration_request(record)
        self.assertTrue(any("status is not supported" in e for e in errors))

    def test_build_success(self) -> None:
        record = build_candidate_registration_request(
            request_id="req-1",
            candidate_id="cand-1",
            requested_entity_type="service",
            mapping_reference="map-1",
            status="SUBMITTED",
        )
        self.assertEqual(record["request_id"], "req-1")
        self.assertEqual(record["status"], "SUBMITTED")

    def test_build_default_status(self) -> None:
        record = build_candidate_registration_request(
            request_id="req-1",
            candidate_id="cand-1",
            requested_entity_type="service",
            mapping_reference="map-1",
        )
        self.assertEqual(record["status"], "CREATED")

    def test_build_failure_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as context:
            build_candidate_registration_request(
                request_id="",
                candidate_id="cand-1",
                requested_entity_type="service",
                mapping_reference="map-1",
                status="CREATED",
            )
        self.assertIn("request_id must be a non-empty string", str(context.exception))


if __name__ == "__main__":
    unittest.main()
