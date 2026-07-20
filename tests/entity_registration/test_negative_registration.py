"""Negative registration tests for authorization and authority boundaries."""

from __future__ import annotations

import unittest

from test_authorized_registration import build_authorization, build_candidate
from entity_support.registration.registration_executor import (
    execute_entity_registration,
)

TIMESTAMP = "2026-07-20T12:00:00+08:00"


class NegativeRegistrationTests(unittest.TestCase):
    def assert_rejected(
        self,
        candidate: dict[str, object],
        authorization: dict[str, object],
    ) -> None:
        log: list[dict[str, str | None]] = []
        result = execute_entity_registration(
            candidate=candidate,
            authorization=authorization,
            registered_at=TIMESTAMP,
            receipt_log=log,
        )
        self.assertIsNone(result["entity_record"])
        self.assertEqual(result["receipt"]["status"], "FAILED")
        self.assertTrue(result["errors"])
        self.assertEqual(log, [result["receipt"]])

    def test_pending_authorization_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["status"] = "PENDING"
        self.assert_rejected(build_candidate(), authorization)

    def test_rejected_authorization_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["status"] = "REJECTED"
        self.assert_rejected(build_candidate(), authorization)

    def test_revoked_authorization_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["status"] = "REVOKED"
        self.assert_rejected(build_candidate(), authorization)

    def test_automatic_active_scope_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["authorized_scope"]["lifecycle_target"] = "ACTIVE"
        self.assert_rejected(build_candidate(), authorization)

    def test_automatic_permission_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["permission_status"] = "GRANTED"
        self.assert_rejected(build_candidate(), authorization)

    def test_automatic_capability_grant_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["authorized_scope"]["capability_grant"] = "GRANTED"
        self.assert_rejected(build_candidate(), authorization)

    def test_missing_candidate_source_is_rejected(self) -> None:
        candidate = build_candidate()
        candidate.pop("candidate_id")
        self.assert_rejected(candidate, build_authorization())

    def test_missing_authorization_source_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization.pop("authorization_id")
        self.assert_rejected(build_candidate(), authorization)

    def test_entity_type_mismatch_is_rejected(self) -> None:
        authorization = build_authorization()
        authorization["target_entity_type"] = "protocol"
        self.assert_rejected(build_candidate(), authorization)


if __name__ == "__main__":
    unittest.main()

