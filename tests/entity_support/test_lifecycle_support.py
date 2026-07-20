"""Tests for non-mutating Digital Entity lifecycle records."""

from __future__ import annotations

import unittest

from entity_support.lifecycle_support import (
    LIFECYCLE_STATES,
    build_lifecycle_transition_record,
)


class LifecycleSupportTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "transition_id": "fixture-transition",
            "entity_id": "fixture-entity",
            "from_state": "PROPOSED",
            "to_state": "REGISTERED",
            "source_reference": "fixture-source",
            "verification_reference": "fixture-verification",
        }
        values.update(overrides)
        return build_lifecycle_transition_record(**values)

    def test_supports_all_architecture_states(self) -> None:
        self.assertEqual(
            LIFECYCLE_STATES,
            (
                "PROPOSED",
                "REGISTERED",
                "VERIFIED",
                "ACTIVE",
                "EVALUATED",
                "ADAPTED",
                "RETIRED",
            ),
        )

    def test_proposed_can_record_registration_transition(self) -> None:
        record = self._build()
        self.assertEqual(record["from_state"], "PROPOSED")
        self.assertEqual(record["to_state"], "REGISTERED")

    def test_state_skipping_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._build(to_state="ACTIVE", authorization_reference="fixture-authorization")

    def test_active_requires_authorization(self) -> None:
        with self.assertRaises(ValueError):
            self._build(from_state="VERIFIED", to_state="ACTIVE")

    def test_active_with_authorization_is_only_a_record(self) -> None:
        record = self._build(
            from_state="VERIFIED",
            to_state="ACTIVE",
            authorization_reference="fixture-authorization",
        )
        self.assertEqual(record["to_state"], "ACTIVE")
        self.assertNotIn("applied", record)

    def test_evaluated_requires_evaluation_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._build(from_state="ACTIVE", to_state="EVALUATED")

    def test_adapted_requires_evaluation_decision_and_authorization(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                from_state="EVALUATED",
                to_state="ADAPTED",
                evaluation_reference="fixture-evaluation",
            )

    def test_adapted_record_accepts_all_required_references(self) -> None:
        record = self._build(
            from_state="EVALUATED",
            to_state="ADAPTED",
            evaluation_reference="fixture-evaluation",
            decision_reference="fixture-decision",
            authorization_reference="fixture-authorization",
        )
        self.assertEqual(record["to_state"], "ADAPTED")

    def test_retired_is_terminal(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                from_state="RETIRED",
                to_state="ACTIVE",
                authorization_reference="fixture-authorization",
            )

    def test_transition_requires_verification_reference(self) -> None:
        with self.assertRaises(ValueError):
            self._build(verification_reference="")


if __name__ == "__main__":
    unittest.main()
