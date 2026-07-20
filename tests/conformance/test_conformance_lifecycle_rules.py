"""Conformance tests for sourced and verified lifecycle transition records."""

from __future__ import annotations

import unittest

from entity_support.lifecycle_support import build_lifecycle_transition_record


class LifecycleConformanceTests(unittest.TestCase):
    def test_registration_transition_requires_source_and_verification(self) -> None:
        with self.assertRaises(ValueError):
            build_lifecycle_transition_record(
                transition_id="fixture-transition",
                entity_id="fixture-entity",
                from_state="PROPOSED",
                to_state="REGISTERED",
                source_reference="fixture-source",
                verification_reference="",
            )

    def test_active_requires_authorization(self) -> None:
        with self.assertRaises(ValueError):
            build_lifecycle_transition_record(
                transition_id="fixture-transition",
                entity_id="fixture-entity",
                from_state="VERIFIED",
                to_state="ACTIVE",
                source_reference="fixture-source",
                verification_reference="fixture-verification",
            )

    def test_adapted_requires_governance_decision(self) -> None:
        with self.assertRaises(ValueError):
            build_lifecycle_transition_record(
                transition_id="fixture-transition",
                entity_id="fixture-entity",
                from_state="EVALUATED",
                to_state="ADAPTED",
                source_reference="fixture-source",
                verification_reference="fixture-verification",
                evaluation_reference="fixture-evaluation",
                authorization_reference="fixture-authorization",
            )


if __name__ == "__main__":
    unittest.main()
