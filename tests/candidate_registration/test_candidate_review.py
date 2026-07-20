"""Tests for Candidate Review without registration or activation effects."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_review import (
    CANDIDATE_REVIEW_FIELDS,
    REVIEW_STATUSES,
    build_candidate_review,
    validate_candidate_review,
)


class CandidateReviewTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, str]:
        values: dict[str, object] = {
            "review_id": "fixture-review",
            "candidate_id": "fixture-candidate",
            "reviewer_reference": "fixture-reviewer",
            "review_notes": "fixture notes",
        }
        values.update(overrides)
        return build_candidate_review(**values)

    def test_default_status_is_pending(self) -> None:
        self.assertEqual(self._build()["review_status"], "PENDING")

    def test_supported_review_statuses_are_records_only(self) -> None:
        for status in REVIEW_STATUSES:
            with self.subTest(status=status):
                review = self._build(review_status=status)
                self.assertEqual(review["review_status"], status)
                self.assertNotIn("lifecycle_state", review)

    def test_review_contains_only_declared_fields(self) -> None:
        self.assertEqual(tuple(self._build()), CANDIDATE_REVIEW_FIELDS)

    def test_unsupported_review_status_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._build(review_status="ACTIVE")

    def test_review_notes_must_be_a_string(self) -> None:
        with self.assertRaises(ValueError):
            self._build(review_notes=None)

    def test_approved_review_rejects_injected_activation(self) -> None:
        review = self._build(review_status="APPROVED")
        review["lifecycle_state"] = "ACTIVE"
        self.assertTrue(validate_candidate_review(review))


if __name__ == "__main__":
    unittest.main()
