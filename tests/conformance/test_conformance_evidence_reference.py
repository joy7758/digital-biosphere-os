"""Conformance tests for Evidence references without a second Evidence store."""

from __future__ import annotations

import unittest

from entity_support.evidence_integration import build_evidence_integration_link
from entity_support.evidence_reference import build_evidence_reference
from entity_support.verification_reference import build_verification_reference


class EvidenceReferenceConformanceTests(unittest.TestCase):
    def _link(self) -> dict[str, str]:
        evidence = build_evidence_reference(
            evidence_id="fixture-evidence",
            execution_id="fixture-execution",
            reference="fixture://canonical-evidence-reference",
        )
        verification = build_verification_reference(
            verification_id="fixture-verification",
            evidence_id="fixture-evidence",
        )
        return build_evidence_integration_link(evidence, verification)

    def test_existing_dbos_evidence_system_remains_owner(self) -> None:
        link = self._link()
        self.assertEqual(
            link["canonical_evidence_owner"], "DBOS_EXISTING_EVIDENCE_SYSTEM"
        )

    def test_evidence_reference_has_no_truth_effect(self) -> None:
        link = self._link()
        self.assertEqual(link["evidence_truth_effect"], "NONE")

    def test_evidence_cannot_auto_validate(self) -> None:
        with self.assertRaises(ValueError):
            build_evidence_reference(
                evidence_id="fixture-evidence",
                execution_id="fixture-execution",
                reference="fixture://canonical-evidence-reference",
                integrity_status="VALIDATED",
            )


if __name__ == "__main__":
    unittest.main()
