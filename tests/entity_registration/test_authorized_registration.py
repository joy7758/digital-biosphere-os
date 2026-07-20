"""Tests for an authorized Candidate becoming a REGISTERED record mapping."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_proposal import build_candidate_proposal
from entity_support.candidate.candidate_registration_request import (
    build_candidate_registration_request,
)
from entity_support.candidate.candidate_registry import build_candidate_registry_record
from entity_support.candidate.candidate_review import build_candidate_review
from entity_support.registration.registration_executor import (
    REGISTRATION_EXECUTION_RESULT_FIELDS,
    execute_entity_registration,
)
from entity_support.registration.registration_validator import (
    REGISTERED_ENTITY_RECORD_FIELDS,
    build_registration_authorization_input,
    derive_entity_id,
)

TIMESTAMP = "2026-07-20T12:00:00+08:00"


def build_candidate() -> dict[str, object]:
    candidate_id = "fixture-authorized-candidate"
    return build_candidate_registry_record(
        candidate_id=candidate_id,
        proposal=build_candidate_proposal(
            candidate_id=candidate_id,
            proposed_type="operational_entity",
            role="fixture_role",
            description="ephemeral authorized registration fixture",
            proposer_reference="fixture-proposer",
        ),
        review=build_candidate_review(
            review_id="fixture-review",
            candidate_id=candidate_id,
            reviewer_reference="fixture-reviewer",
            review_status="APPROVED",
            review_notes="fixture review",
        ),
        registration_request=build_candidate_registration_request(
            request_id="fixture-request",
            candidate_id=candidate_id,
            requested_entity_type="service",
            mapping_reference="fixture-mapping",
            status="ACCEPTED",
        ),
    )


def build_authorization() -> dict[str, object]:
    return build_registration_authorization_input(
        authorization_id="fixture-authorization",
        decision_reference="fixture-admission-decision",
        candidate_id="fixture-authorized-candidate",
        target_entity_type="service",
        authorized_scope={
            "operation": "entity_registration",
            "lifecycle_target": "REGISTERED",
        },
        issuer_reference="fixture-issuer",
        timestamp=TIMESTAMP,
    )


class AuthorizedRegistrationTests(unittest.TestCase):
    def execute(self, **kwargs: object) -> dict[str, object]:
        return execute_entity_registration(
            candidate=build_candidate(),
            authorization=build_authorization(),
            registered_at=TIMESTAMP,
            **kwargs,
        )

    def test_authorized_registration_succeeds_as_registered_only(self) -> None:
        result = self.execute()
        self.assertEqual(result["errors"], ())
        self.assertEqual(result["entity_record"]["lifecycle_state"], "REGISTERED")
        self.assertEqual(result["receipt"]["status"], "SUCCESS")

    def test_result_and_entity_fields_are_bounded(self) -> None:
        result = self.execute()
        self.assertEqual(tuple(result), REGISTRATION_EXECUTION_RESULT_FIELDS)
        self.assertEqual(tuple(result["entity_record"]), REGISTERED_ENTITY_RECORD_FIELDS)

    def test_entity_id_is_derived_from_candidate_and_authorization(self) -> None:
        result = self.execute()
        self.assertEqual(
            result["entity_record"]["entity_id"],
            derive_entity_id("fixture-authorized-candidate", "fixture-authorization"),
        )

    def test_registered_record_has_no_activation_or_grant_fields(self) -> None:
        record = self.execute()["entity_record"]
        for field in (
            "active",
            "agent_id",
            "runtime_id",
            "permission",
            "capability_grant",
            "execution_id",
            "evidence_id",
        ):
            self.assertNotIn(field, record)

    def test_success_receipt_is_retained_when_log_is_supplied(self) -> None:
        log: list[dict[str, str | None]] = []
        result = self.execute(receipt_log=log)
        self.assertEqual(log, [result["receipt"]])

    def test_same_sources_produce_same_identity_and_registration_id(self) -> None:
        first = self.execute()
        second = self.execute()
        self.assertEqual(
            first["entity_record"]["entity_id"], second["entity_record"]["entity_id"]
        )
        self.assertEqual(
            first["receipt"]["registration_id"],
            second["receipt"]["registration_id"],
        )


if __name__ == "__main__":
    unittest.main()

