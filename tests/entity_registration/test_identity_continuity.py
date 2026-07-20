"""Tests for candidate → authorization → entity → receipt continuity."""

from __future__ import annotations

import unittest

from test_authorized_registration import build_authorization, build_candidate
from entity_support.registration.registration_executor import (
    execute_entity_registration,
)
from entity_support.registration.registration_validator import (
    validate_identity_continuity,
)

TIMESTAMP = "2026-07-20T12:00:00+08:00"


class IdentityContinuityTests(unittest.TestCase):
    def valid_chain(self) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        candidate = build_candidate()
        authorization = build_authorization()
        result = execute_entity_registration(
            candidate=candidate,
            authorization=authorization,
            registered_at=TIMESTAMP,
        )
        return candidate, authorization, result

    def errors_for(
        self,
        candidate: dict[str, object],
        authorization: dict[str, object],
        entity: dict[str, object],
        receipt: dict[str, object],
    ) -> list[str]:
        return validate_identity_continuity(
            candidate=candidate,
            authorization=authorization,
            entity_record=entity,
            receipt=receipt,
        )

    def test_valid_chain_has_no_errors(self) -> None:
        candidate, authorization, result = self.valid_chain()
        self.assertEqual(
            self.errors_for(candidate, authorization, result["entity_record"], result["receipt"]),
            [],
        )

    def test_authorization_candidate_mismatch_is_rejected(self) -> None:
        candidate, authorization, result = self.valid_chain()
        authorization["candidate_id"] = "different-candidate"
        self.assertTrue(
            self.errors_for(candidate, authorization, result["entity_record"], result["receipt"])
        )

    def test_entity_candidate_reference_mismatch_is_rejected(self) -> None:
        candidate, authorization, result = self.valid_chain()
        entity = dict(result["entity_record"])
        entity["candidate_reference"] = "different-candidate"
        self.assertTrue(self.errors_for(candidate, authorization, entity, result["receipt"]))

    def test_entity_authorization_reference_mismatch_is_rejected(self) -> None:
        candidate, authorization, result = self.valid_chain()
        entity = dict(result["entity_record"])
        entity["authorization_reference"] = "different-authorization"
        self.assertTrue(self.errors_for(candidate, authorization, entity, result["receipt"]))

    def test_unattributed_entity_id_is_rejected(self) -> None:
        candidate, authorization, result = self.valid_chain()
        entity = dict(result["entity_record"])
        entity["entity_id"] = "unattributed-entity"
        self.assertTrue(self.errors_for(candidate, authorization, entity, result["receipt"]))

    def test_receipt_entity_mismatch_is_rejected(self) -> None:
        candidate, authorization, result = self.valid_chain()
        receipt = dict(result["receipt"])
        receipt["entity_id"] = "different-entity"
        self.assertTrue(
            self.errors_for(candidate, authorization, result["entity_record"], receipt)
        )


if __name__ == "__main__":
    unittest.main()

