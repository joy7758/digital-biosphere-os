"""Tests for proposal records and the Research Agent declaration template."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_proposal import (
    CANDIDATE_PROPOSAL_FIELDS,
    build_candidate_proposal,
)
from entity_support.candidate.candidate_registry import (
    RESEARCH_AGENT_PROPOSED_CAPABILITIES,
    build_research_agent_candidate_template,
    validate_research_agent_candidate_template,
)


class CandidateProposalTests(unittest.TestCase):
    def _build(self, **overrides: object) -> dict[str, str]:
        values: dict[str, object] = {
            "candidate_id": "fixture-candidate",
            "proposed_type": "operational_entity",
            "role": "research_agent",
            "description": "fixture candidate proposal",
            "proposer_reference": "fixture-proposer",
        }
        values.update(overrides)
        return build_candidate_proposal(**values)

    def test_default_status_is_proposed(self) -> None:
        self.assertEqual(self._build()["status"], "PROPOSED")

    def test_proposal_contains_only_declared_fields(self) -> None:
        self.assertEqual(tuple(self._build()), CANDIDATE_PROPOSAL_FIELDS)

    def test_proposal_cannot_become_registered(self) -> None:
        with self.assertRaises(ValueError):
            self._build(status="REGISTERED")

    def test_proposal_cannot_become_active(self) -> None:
        with self.assertRaises(ValueError):
            self._build(status="ACTIVE")

    def test_research_agent_template_is_bounded_declaration(self) -> None:
        template = build_research_agent_candidate_template()
        self.assertEqual(template["role"], "research_agent")
        self.assertEqual(
            tuple(template["proposed_capabilities"]),
            RESEARCH_AGENT_PROPOSED_CAPABILITIES,
        )

    def test_research_agent_template_has_no_instance_or_grant_fields(self) -> None:
        template = build_research_agent_candidate_template()
        for key in ("agent_id", "entity_id", "capability_id", "permission"):
            self.assertNotIn(key, template)

    def test_research_agent_template_rejects_capability_grant(self) -> None:
        template = build_research_agent_candidate_template()
        template["capability_grant"] = "GRANTED"
        self.assertTrue(validate_research_agent_candidate_template(template))


if __name__ == "__main__":
    unittest.main()
