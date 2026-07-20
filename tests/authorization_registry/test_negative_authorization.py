"""Negative tests for expired, revoked, incomplete, and overpowered authorization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_authorization_record import CREATED_AT, EXPIRES_AT, build_authorized
from test_registration_store import build_success
from entity_support.authorization.authorization_record import build_authorization_record
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.authorization.authorization_validator import (
    validate_authorization_for_registration,
)
from entity_support.registration_store.registration_store import RegistrationStore


class NegativeAuthorizationTests(unittest.TestCase):
    def test_pending_authorization_is_not_effective(self) -> None:
        record = build_authorization_record(
            authorization_id="fixture-pending",
            candidate_id="fixture-candidate",
            target_entity_type="service",
            status="PENDING",
            created_at=CREATED_AT,
        )
        self.assertTrue(validate_authorization_for_registration(record, at_time=CREATED_AT))

    def test_rejected_authorization_is_not_effective(self) -> None:
        record = build_authorization_record(
            authorization_id="fixture-rejected",
            candidate_id="fixture-candidate",
            target_entity_type="service",
            status="REJECTED",
            created_at=CREATED_AT,
        )
        self.assertTrue(validate_authorization_for_registration(record, at_time=CREATED_AT))

    def test_expired_authorization_is_not_effective(self) -> None:
        record = build_authorized()
        record["expires_at"] = "2026-07-20T12:00:01+08:00"
        self.assertTrue(
            validate_authorization_for_registration(
                record, at_time="2026-07-20T12:00:01+08:00"
            )
        )

    def test_revoked_authorization_cannot_persist_success(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-revoked-test-") as temp:
            root = Path(temp)
            authorizations = AuthorizationRegistry(root / "authorizations.json")
            registrations = RegistrationStore(root / "registrations.json")
            authorizations.append(build_authorized())
            revoked = build_authorization_record(
                authorization_id="fixture-authorization",
                decision_reference="fixture-decision",
                candidate_id="fixture-candidate",
                target_entity_type="service",
                scope={
                    "operation": "entity_registration",
                    "lifecycle_target": "REGISTERED",
                },
                issuer_reference="fixture-issuer",
                status="REVOKED",
                created_at="2026-07-20T12:00:01+08:00",
                expires_at=EXPIRES_AT,
                revocation_reference="fixture-revocation",
            )
            authorizations.append(revoked)
            self.assertEqual(
                authorizations.get("fixture-authorization")["status"], "REVOKED"
            )
            self.assertEqual(authorizations.authorization_count(), 1)
            self.assertEqual(authorizations.count(), 2)
            with self.assertRaises(ValueError):
                registrations.append(
                    build_success(),
                    authorization_registry=authorizations,
                )

    def test_authorization_scope_cannot_target_active(self) -> None:
        record = build_authorized()
        record["scope"]["lifecycle_target"] = "ACTIVE"
        self.assertTrue(validate_authorization_for_registration(record, at_time=CREATED_AT))

    def test_authorization_scope_cannot_grant_permission(self) -> None:
        record = build_authorized()
        record["scope"]["permission_grant"] = "GRANTED"
        self.assertTrue(validate_authorization_for_registration(record, at_time=CREATED_AT))

    def test_naive_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_authorization_record(
                authorization_id="fixture-time",
                candidate_id="fixture-candidate",
                target_entity_type="service",
                status="PENDING",
                created_at="2026-07-20T12:00:00",
            )


if __name__ == "__main__":
    unittest.main()
