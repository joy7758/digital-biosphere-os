"""Tests for a prepared-not-sent DBOS-to-SAEE data envelope."""

from __future__ import annotations

import unittest

from entity_support.saee_evaluation_adapter import (
    build_saee_evaluation_envelope,
    validate_saee_evaluation_envelope,
)


class SaeeEvaluationAdapterTests(unittest.TestCase):
    def _verification(self) -> dict[str, str]:
        return {
            "verification_reference": "fixture-verification",
            "verification_status": "PENDING",
            "verification_level": "V0",
        }

    def _build(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "execution_history": ["fixture-execution"],
            "evidence_bundle_reference": "fixture-evidence-bundle",
            "verification_result": self._verification(),
            "resource_usage_reference": "fixture-resource-usage",
        }
        values.update(overrides)
        return build_saee_evaluation_envelope(**values)

    def test_envelope_contains_required_dba_inputs(self) -> None:
        envelope = self._build()
        self.assertEqual(envelope["execution_history"], ["fixture-execution"])
        self.assertEqual(envelope["evidence_bundle_reference"], "fixture-evidence-bundle")
        self.assertEqual(envelope["resource_usage_reference"], "fixture-resource-usage")

    def test_envelope_is_prepared_but_not_sent(self) -> None:
        envelope = self._build()
        self.assertEqual(envelope["producer"], "DBOS")
        self.assertEqual(envelope["consumer"], "SAEE")
        self.assertEqual(envelope["payload_status"], "PREPARED_NOT_SENT")

    def test_envelope_has_no_evaluation_effect(self) -> None:
        envelope = self._build()
        self.assertEqual(envelope["evaluation_effect"], "NONE")
        self.assertEqual(envelope["authority_class"], "DATA_TRANSFER_PREPARATION")

    def test_explicit_empty_execution_history_is_allowed(self) -> None:
        envelope = self._build(execution_history=[])
        self.assertEqual(envelope["execution_history"], [])

    def test_duplicate_execution_references_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self._build(execution_history=["fixture-execution", "fixture-execution"])

    def test_verification_must_remain_pending_v0(self) -> None:
        with self.assertRaises(ValueError):
            self._build(
                verification_result={
                    "verification_reference": "fixture-verification",
                    "verification_status": "PASS",
                    "verification_level": "V1",
                }
            )

    def test_fitness_injection_is_rejected(self) -> None:
        envelope = self._build()
        envelope["fitness_assessment"] = {"reliability": 1.0}
        errors = validate_saee_evaluation_envelope(envelope)
        self.assertTrue(any("prohibited evaluation key" in error for error in errors))

    def test_resource_usage_can_remain_unknown(self) -> None:
        envelope = self._build(resource_usage_reference=None)
        self.assertIsNone(envelope["resource_usage_reference"])


if __name__ == "__main__":
    unittest.main()
