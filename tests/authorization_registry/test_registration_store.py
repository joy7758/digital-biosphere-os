"""Tests for Authorization-linked Registration Record persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_authorization_record import CREATED_AT, build_authorized
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.registration.registration_validator import derive_entity_id
from entity_support.registration_store.registration_store import (
    REGISTRATION_RECORD_FIELDS,
    RegistrationStore,
    build_registration_record,
)


def build_success(
    *,
    registration_id: str = "fixture-registration",
    authorization_id: str = "fixture-authorization",
    candidate_id: str = "fixture-candidate",
) -> dict[str, str | None]:
    return build_registration_record(
        registration_id=registration_id,
        entity_id=derive_entity_id(candidate_id, authorization_id),
        candidate_reference=candidate_id,
        authorization_reference=authorization_id,
        registered_at=CREATED_AT,
        status="SUCCESS",
    )


class RegistrationStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-registration-test-")
        root = Path(self.temp.name)
        self.authorizations = AuthorizationRegistry(root / "authorizations.json")
        self.registrations = RegistrationStore(root / "registrations.json")
        self.authorizations.append(build_authorized())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_success_registration_is_persisted(self) -> None:
        stored = self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        self.assertEqual(tuple(stored), REGISTRATION_RECORD_FIELDS)
        self.assertEqual(self.registrations.successful_count(), 1)

    def test_persisted_record_survives_store_reopen(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        reopened = RegistrationStore(self.registrations.path)
        self.assertEqual(reopened.get("fixture-registration")["status"], "SUCCESS")

    def test_failed_registration_is_persisted_without_entity(self) -> None:
        record = build_registration_record(
            registration_id="fixture-failed-registration",
            entity_id=None,
            candidate_reference="fixture-candidate",
            authorization_reference="fixture-authorization",
            registered_at=CREATED_AT,
            status="FAILED",
        )
        stored = self.registrations.append(
            record,
            authorization_registry=self.authorizations,
        )
        self.assertIsNone(stored["entity_id"])

    def test_registration_requires_authorization_source(self) -> None:
        with self.assertRaises(ValueError):
            self.registrations.append(
                build_success(authorization_id="missing-authorization"),
                authorization_registry=self.authorizations,
            )

    def test_candidate_continuity_mismatch_is_rejected(self) -> None:
        record = build_success()
        record["candidate_reference"] = "different-candidate"
        with self.assertRaises(ValueError):
            self.registrations.append(
                record,
                authorization_registry=self.authorizations,
            )

    def test_unattributed_entity_id_is_rejected(self) -> None:
        record = build_success()
        record["entity_id"] = "orphan-entity"
        with self.assertRaises(ValueError):
            self.registrations.append(
                record,
                authorization_registry=self.authorizations,
            )


if __name__ == "__main__":
    unittest.main()
