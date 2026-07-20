"""Tests for Candidate Registration without Digital Entity creation."""

from __future__ import annotations

import unittest

from entity_support.candidate_registration import build_candidate_registration_record


class CandidateRegistrationTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "proposal_id": "fixture-proposal",
            "candidate_reference": "fixture-candidate",
            "requested_entity_type": "service",
            "owner_reference": "fixture-owner",
            "proposal_reference": "fixture-proposal-document",
        }
        values.update(overrides)
        return build_candidate_registration_record(**values)

    def test_default_is_review_pending_and_not_submitted(self) -> None:
        record = self._build()
        self.assertEqual(record["review_status"], "REVIEW_PENDING")
        self.assertEqual(record["registration_request_status"], "NOT_SUBMITTED")
        self.assertEqual(record["current_effect"], "NONE")

    def test_candidate_has_no_entity_id(self) -> None:
        record = self._build()
        self.assertNotIn("entity_id", record)
        self.assertNotIn("canonical_id", record)

    def test_review_requires_reference_when_started(self) -> None:
        with self.assertRaises(ValueError):
            self._build(review_status="UNDER_REVIEW")

    def test_pending_registration_requires_approved_review(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                registration_request_status="PENDING",
                registration_request_reference="fixture-request",
            )

    def test_approved_review_can_submit_pending_request(self) -> None:
        record = self._build(
            review_status="APPROVED",
            review_reference="fixture-review",
            registration_request_status="PENDING",
            registration_request_reference="fixture-request",
        )
        self.assertEqual(record["registration_request_status"], "PENDING")
        self.assertEqual(record["current_effect"], "NONE")

    def test_registration_request_cannot_be_approved_in_prototype(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                review_status="APPROVED",
                review_reference="fixture-review",
                registration_request_status="APPROVED",
                registration_request_reference="fixture-request",
            )

    def test_candidate_cannot_request_active(self) -> None:
        with self.assertRaises(ValueError):
            self._build(requested_lifecycle_state="ACTIVE")

    def test_candidate_cannot_create_current_effect(self) -> None:
        with self.assertRaises(ValueError):
            self._build(current_effect="ENTITY_CREATED")


if __name__ == "__main__":
    unittest.main()
