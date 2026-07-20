"""Integrated negative tests for candidate-to-Entity privilege escalation."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_proposal import build_candidate_proposal
from entity_support.candidate.candidate_registry import (
    build_candidate_registry_record,
    build_research_agent_candidate_template,
    validate_candidate_registry_record,
    validate_research_agent_candidate_template,
)
from validation.candidate_registration_validator import validate


class NegativeCandidateActivationTests(unittest.TestCase):
    def _candidate(self) -> dict[str, object]:
        proposal = build_candidate_proposal(
            candidate_id="fixture-candidate",
            proposed_type="operational_entity",
            role="research_agent",
            description="fixture candidate proposal",
            proposer_reference="fixture-proposer",
        )
        return build_candidate_registry_record(
            candidate_id="fixture-candidate",
            proposal=proposal,
        )

    def test_validator_passes(self) -> None:
        self.assertEqual(validate()["status"], "PASS")

    def test_all_required_negative_cases_are_rejected(self) -> None:
        result = validate()
        self.assertEqual(result["negative_case_count"], 5)
        self.assertEqual(result["rejected_negative_case_count"], 5)

    def test_all_side_effect_counts_remain_zero(self) -> None:
        result = validate()
        self.assertTrue(all(count == 0 for count in result["side_effect_counts"].values()))

    def test_candidate_rejects_entity_identity_injection(self) -> None:
        candidate = self._candidate()
        candidate["entity_id"] = "forbidden-entity"
        self.assertTrue(validate_candidate_registry_record(candidate))

    def test_candidate_rejects_permission_injection(self) -> None:
        candidate = self._candidate()
        candidate["permission_status"] = "GRANTED"
        self.assertTrue(validate_candidate_registry_record(candidate))

    def test_template_rejects_capability_instance_injection(self) -> None:
        template = build_research_agent_candidate_template()
        template["capability_id"] = "forbidden-capability"
        self.assertTrue(validate_research_agent_candidate_template(template))


if __name__ == "__main__":
    unittest.main()
