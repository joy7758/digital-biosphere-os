"""Tests for one-success-per-authorization replay protection."""

from __future__ import annotations

import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from test_authorization_record import CREATED_AT, build_authorized
from test_registration_store import build_success
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.registration_store.registration_store import (
    RegistrationStore,
    build_registration_record,
)


class ReplayProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-replay-test-")
        root = Path(self.temp.name)
        self.authorizations = AuthorizationRegistry(root / "authorizations.json")
        self.registrations = RegistrationStore(root / "registrations.json")
        self.authorizations.append(build_authorized())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_second_success_for_same_authorization_is_rejected(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        with self.assertRaises(ValueError):
            self.registrations.append(
                build_success(registration_id="fixture-replay"),
                authorization_registry=self.authorizations,
            )

    def test_duplicate_registration_id_is_rejected(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        with self.assertRaises(ValueError):
            self.registrations.append(
                build_success(),
                authorization_registry=self.authorizations,
            )

    def test_failed_attempt_does_not_consume_success_slot(self) -> None:
        failed = build_registration_record(
            registration_id="fixture-failure",
            entity_id=None,
            candidate_reference="fixture-candidate",
            authorization_reference="fixture-authorization",
            registered_at=CREATED_AT,
            status="FAILED",
        )
        self.registrations.append(
            failed,
            authorization_registry=self.authorizations,
        )
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        self.assertEqual(self.registrations.successful_count(), 1)

    def test_replay_protection_survives_store_reopen(self) -> None:
        self.registrations.append(
            build_success(),
            authorization_registry=self.authorizations,
        )
        reopened = RegistrationStore(self.registrations.path)
        with self.assertRaises(ValueError):
            reopened.append(
                build_success(registration_id="fixture-replay"),
                authorization_registry=self.authorizations,
            )

    def test_concurrent_success_attempts_are_serialized(self) -> None:
        barrier = threading.Barrier(2)

        def attempt(registration_id: str) -> str:
            store = RegistrationStore(self.registrations.path)
            barrier.wait()
            try:
                store.append(
                    build_success(registration_id=registration_id),
                    authorization_registry=self.authorizations,
                )
            except ValueError:
                return "REJECTED"
            return "SUCCESS"

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(
                executor.map(attempt, ("fixture-concurrent-a", "fixture-concurrent-b"))
            )
        self.assertEqual(sorted(results), ["REJECTED", "SUCCESS"])
        self.assertEqual(self.registrations.successful_count(), 1)

    def test_duplicate_authorization_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.authorizations.append(build_authorized())


if __name__ == "__main__":
    unittest.main()
