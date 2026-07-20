"""Conformance tests for Entity and candidate registration boundaries."""

from __future__ import annotations

import unittest

from entity_support.candidate_registration import build_candidate_registration_record
from entity_support.entity_registry import build_entity_registration_record


class EntityRegistrationConformanceTests(unittest.TestCase):
    def test_support_registration_is_proposed_only(self) -> None:
        record = build_entity_registration_record(
            entity_id="fixture-entity",
            entity_type="service",
            owner_reference="fixture-owner",
        )
        self.assertEqual(record["lifecycle_state"], "PROPOSED")

    def test_candidate_does_not_receive_entity_identity(self) -> None:
        record = build_candidate_registration_record(
            proposal_id="fixture-proposal",
            candidate_reference="fixture-candidate",
            requested_entity_type="service",
            owner_reference="fixture-owner",
            proposal_reference="fixture-proposal-document",
        )
        self.assertNotIn("entity_id", record)
        self.assertEqual(record["current_effect"], "NONE")

    def test_active_registration_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            build_entity_registration_record(
                entity_id="fixture-entity",
                entity_type="service",
                owner_reference="fixture-owner",
                lifecycle_state="ACTIVE",
            )


if __name__ == "__main__":
    unittest.main()
