"""Tests for immutable Registration Authorization Records."""

from __future__ import annotations

import unittest

from entity_support.authorization.authorization_record import (
    AUTHORIZATION_RECORD_FIELDS,
    AUTHORIZATION_STATUSES,
    authorization_record_to_execution_input,
    build_authorization_record,
    validate_authorization_record,
)

CREATED_AT = "2026-07-20T12:00:00+08:00"
EXPIRES_AT = "2027-07-20T12:00:00+08:00"


def build_authorized(
    *,
    authorization_id: str = "fixture-authorization",
    candidate_id: str = "fixture-candidate",
) -> dict[str, object]:
    return build_authorization_record(
        authorization_id=authorization_id,
        decision_reference="fixture-decision",
        candidate_id=candidate_id,
        target_entity_type="service",
        scope={
            "operation": "entity_registration",
            "lifecycle_target": "REGISTERED",
        },
        issuer_reference="fixture-issuer",
        status="AUTHORIZED",
        created_at=CREATED_AT,
        expires_at=EXPIRES_AT,
    )


class AuthorizationRecordTests(unittest.TestCase):
    def test_authorized_record_has_exact_fields(self) -> None:
        self.assertEqual(tuple(build_authorized()), AUTHORIZATION_RECORD_FIELDS)

    def test_status_vocabulary_is_bounded(self) -> None:
        self.assertEqual(
            AUTHORIZATION_STATUSES,
            {"PENDING", "AUTHORIZED", "REJECTED", "REVOKED"},
        )

    def test_pending_record_can_preserve_unknown_governance_fields(self) -> None:
        record = build_authorization_record(
            authorization_id="fixture-pending",
            candidate_id="fixture-candidate",
            target_entity_type="service",
            status="PENDING",
            created_at=CREATED_AT,
        )
        self.assertIsNone(record["decision_reference"])
        self.assertIsNone(record["scope"])

    def test_authorized_requires_decision_reference(self) -> None:
        values = build_authorized()
        values["decision_reference"] = None
        self.assertTrue(validate_authorization_record(values))

    def test_authorized_requires_issuer_reference(self) -> None:
        values = build_authorized()
        values["issuer_reference"] = None
        self.assertTrue(validate_authorization_record(values))

    def test_authorized_requires_scope(self) -> None:
        values = build_authorized()
        values["scope"] = None
        self.assertTrue(validate_authorization_record(values))

    def test_revoked_requires_revocation_reference(self) -> None:
        with self.assertRaises(ValueError):
            build_authorization_record(
                authorization_id="fixture-revoked",
                candidate_id="fixture-candidate",
                target_entity_type="service",
                status="REVOKED",
                created_at=CREATED_AT,
            )

    def test_permission_effect_is_rejected(self) -> None:
        values = build_authorized()
        values["scope"]["permission_grant"] = "GRANTED"
        self.assertTrue(validate_authorization_record(values))

    def test_execution_projection_preserves_no_permission_field(self) -> None:
        projection = authorization_record_to_execution_input(build_authorized())
        self.assertEqual(projection["status"], "AUTHORIZED")
        self.assertNotIn("permission", projection)


if __name__ == "__main__":
    unittest.main()

