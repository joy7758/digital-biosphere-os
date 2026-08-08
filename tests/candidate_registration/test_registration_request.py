"""Tests for registration request workflow records without Entity creation."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_proposal import build_candidate_proposal
from entity_support.candidate.candidate_registration_request import (
    CANDIDATE_REGISTRATION_REQUEST_FIELDS,
    REGISTRATION_REQUEST_STATUSES,
    build_candidate_registration_request,
    validate_candidate_registration_request,
)
from entity_support.candidate.candidate_registry import build_candidate_registry_record
from entity_support.candidate.candidate_review import build_candidate_review


class RegistrationRequestTests(unittest.TestCase):
    def _proposal(self) -> dict[str, str]:
        return build_candidate_proposal(
            candidate_id="fixture-candidate",
            proposed_type="operational_entity",
            role="research_agent",
            description="fixture candidate proposal",
            proposer_reference="fixture-proposer",
        )

    def _review(self, status: str = "APPROVED") -> dict[str, str]:
        return build_candidate_review(
            review_id="fixture-review",
            candidate_id="fixture-candidate",
            reviewer_reference="fixture-reviewer",
            review_status=status,
            review_notes="fixture review",
        )

    def _request(self, **overrides: object) -> dict[str, str]:
        values: dict[str, object] = {
            "request_id": "fixture-request",
            "candidate_id": "fixture-candidate",
            "requested_entity_type": "service",
            "mapping_reference": "fixture-mapping",
        }
        values.update(overrides)
        return build_candidate_registration_request(**values)

    def test_default_status_is_created(self) -> None:
        self.assertEqual(self._request()["status"], "CREATED")

    def test_all_request_statuses_remain_request_states(self) -> None:
        for status in REGISTRATION_REQUEST_STATUSES:
            with self.subTest(status=status):
                request = self._request(status=status)
                self.assertEqual(request["status"], status)
                self.assertNotIn("entity_id", request)

    def test_request_contains_only_declared_fields(self) -> None:
        self.assertEqual(
            tuple(self._request()),
            CANDIDATE_REGISTRATION_REQUEST_FIELDS,
        )

    def test_request_rejects_unknown_entity_type(self) -> None:
        with self.assertRaises(ValueError):
            self._request(requested_entity_type="operational_entity")

    def test_request_requires_mapping_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._request(mapping_reference="")

    def test_submitted_request_requires_approved_review(self) -> None:
        request = self._request(status="SUBMITTED")
        with self.assertRaises(ValueError):
            build_candidate_registry_record(
                candidate_id="fixture-candidate",
                proposal=self._proposal(),
                review=self._review("PENDING"),
                registration_request=request,
            )

    def test_accepted_request_has_no_entity_effect(self) -> None:
        record = build_candidate_registry_record(
            candidate_id="fixture-candidate",
            proposal=self._proposal(),
            review=self._review(),
            registration_request=self._request(status="ACCEPTED"),
        )
        self.assertEqual(record["current_effect"], "NONE")
        self.assertNotIn("entity_id", record)

    def test_candidate_id_mismatch_is_rejected(self) -> None:
        request = self._request(candidate_id="different-candidate")
        with self.assertRaises(ValueError):
            build_candidate_registry_record(
                candidate_id="fixture-candidate",
                proposal=self._proposal(),
                review=self._review(),
                registration_request=request,
            )

    def test_validate_missing_fields(self) -> None:
        request = self._request()
        del request["request_id"]
        errors = validate_candidate_registration_request(request)
        self.assertTrue(any("missing fields" in e and "request_id" in e for e in errors))

    def test_validate_extra_fields(self) -> None:
        request = self._request()
        request["extra_field"] = "value"
        errors = validate_candidate_registration_request(request)
        self.assertTrue(any("unexpected fields" in e and "extra_field" in e for e in errors))

    def test_validate_unsupported_status(self) -> None:
        request = self._request()
        request["status"] = "UNSUPPORTED_STATUS"
        errors = validate_candidate_registration_request(request)
        self.assertTrue(any("status is not supported" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
