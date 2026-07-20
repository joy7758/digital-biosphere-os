"""Tests for DBOS-owned Evidence and Verification reference integration."""

from __future__ import annotations

import unittest

from entity_support.evidence_integration import build_evidence_integration_link
from entity_support.evidence_reference import build_evidence_reference
from entity_support.verification_reference import build_verification_reference


class EvidenceIntegrationTests(unittest.TestCase):
    def _evidence(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "evidence_id": "fixture-evidence",
            "execution_id": "fixture-execution",
            "reference": "fixture://canonical-evidence-reference",
        }
        values.update(overrides)
        return build_evidence_reference(**values)

    def _verification(self, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "verification_id": "fixture-verification",
            "evidence_id": "fixture-evidence",
        }
        values.update(overrides)
        return build_verification_reference(**values)

    def test_link_preserves_evidence_and_verification_references(self) -> None:
        link = build_evidence_integration_link(self._evidence(), self._verification())
        self.assertEqual(link["evidence_id"], "fixture-evidence")
        self.assertEqual(link["verification_id"], "fixture-verification")

    def test_verification_must_reference_same_evidence(self) -> None:
        with self.assertRaises(ValueError):
            build_evidence_integration_link(
                self._evidence(), self._verification(evidence_id="different-evidence")
            )

    def test_integrity_remains_unknown_or_pending(self) -> None:
        link = build_evidence_integration_link(
            self._evidence(integrity_status="PENDING"), self._verification()
        )
        self.assertEqual(link["integrity_status"], "PENDING")

    def test_verification_remains_pending_v0(self) -> None:
        link = build_evidence_integration_link(self._evidence(), self._verification())
        self.assertEqual(link["verification_status"], "PENDING")
        self.assertEqual(link["verification_level"], "V0")

    def test_link_has_no_truth_or_permission_effect(self) -> None:
        link = build_evidence_integration_link(self._evidence(), self._verification())
        self.assertEqual(link["evidence_truth_effect"], "NONE")
        self.assertEqual(link["permission_effect"], "NONE")

    def test_link_contains_no_evidence_payload(self) -> None:
        link = build_evidence_integration_link(self._evidence(), self._verification())
        self.assertNotIn("payload", link)
        self.assertNotIn("digest", link)
        self.assertNotIn("truth", link)

    def test_validated_evidence_is_rejected_by_reference_layer(self) -> None:
        with self.assertRaises(ValueError):
            self._evidence(integrity_status="VALIDATED")


if __name__ == "__main__":
    unittest.main()
