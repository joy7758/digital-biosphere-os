"""Tests for candidate registry structures."""

from __future__ import annotations

import unittest

from entity_support.candidate.candidate_registry import (
    build_candidate_registry_record,
    build_research_agent_candidate_template,
    validate_candidate_registry_record,
    validate_research_agent_candidate_template,
)


class TestResearchAgentCandidateTemplate(unittest.TestCase):
    def test_valid_template(self) -> None:
        template = {
            "role": "research_agent",
            "proposed_capabilities": [
                "literature_analysis",
                "knowledge_synthesis",
                "experiment_planning",
                "code_assistance",
            ],
        }
        errors = validate_research_agent_candidate_template(template)
        self.assertEqual(errors, [])

    def test_missing_fields(self) -> None:
        errors = validate_research_agent_candidate_template({})
        self.assertTrue(
            any("missing fields" in err and "role" in err for err in errors)
        )
        self.assertTrue(any("role must remain research_agent" in err for err in errors))
        self.assertTrue(
            any("proposed_capabilities must be a list" in err for err in errors)
        )

    def test_extra_fields(self) -> None:
        template = {
            "role": "research_agent",
            "proposed_capabilities": [
                "literature_analysis",
                "knowledge_synthesis",
                "experiment_planning",
                "code_assistance",
            ],
            "extra_field": "value",
        }
        errors = validate_research_agent_candidate_template(template)
        self.assertTrue(
            any("unexpected fields: ['extra_field']" in err for err in errors)
        )

    def test_invalid_role(self) -> None:
        template = {
            "role": "invalid_role",
            "proposed_capabilities": [
                "literature_analysis",
                "knowledge_synthesis",
                "experiment_planning",
                "code_assistance",
            ],
        }
        errors = validate_research_agent_candidate_template(template)
        self.assertIn("role must remain research_agent", errors)

    def test_invalid_capabilities(self) -> None:
        template1 = {
            "role": "research_agent",
            "proposed_capabilities": "not_a_list",
        }
        errors1 = validate_research_agent_candidate_template(template1)
        self.assertIn("proposed_capabilities must be a list", errors1)

        template2 = {
            "role": "research_agent",
            "proposed_capabilities": ["wrong_capability"],
        }
        errors2 = validate_research_agent_candidate_template(template2)
        self.assertIn(
            "proposed_capabilities must use the bounded declaration template", errors2
        )

    def test_build_template(self) -> None:
        template = build_research_agent_candidate_template()
        self.assertEqual(template["role"], "research_agent")
        self.assertEqual(
            template["proposed_capabilities"],
            [
                "literature_analysis",
                "knowledge_synthesis",
                "experiment_planning",
                "code_assistance",
            ],
        )


class TestCandidateRegistryRecord(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal_fixture = {
            "candidate_id": "test_id",
            "proposed_type": "agent",
            "role": "research_agent",
            "description": "desc",
            "proposer_reference": "ref",
            "status": "PROPOSED",
        }
        self.review_fixture = {
            "review_id": "rev-1",
            "candidate_id": "test_id",
            "reviewer_reference": "ref",
            "review_status": "APPROVED",
            "review_notes": "notes",
        }
        self.request_fixture = {
            "request_id": "req-1",
            "candidate_id": "test_id",
            "requested_entity_type": "agent",
            "mapping_reference": "ref",
            "status": "CREATED",
        }

    def test_valid_record_no_review(self) -> None:
        record = build_candidate_registry_record(
            candidate_id="test_id",
            proposal=self.proposal_fixture,
        )
        self.assertEqual(record["candidate_id"], "test_id")
        self.assertEqual(record["proposal"], self.proposal_fixture)
        self.assertIsNone(record["review"])
        self.assertIsNone(record["registration_request"])
        self.assertEqual(record["current_effect"], "NONE")

    def test_valid_record_with_review_and_request(self) -> None:
        record = build_candidate_registry_record(
            candidate_id="test_id",
            proposal=self.proposal_fixture,
            review=self.review_fixture,
            registration_request=self.request_fixture,
        )
        self.assertEqual(record["candidate_id"], "test_id")
        self.assertEqual(record["proposal"], self.proposal_fixture)
        self.assertEqual(record["review"], self.review_fixture)
        self.assertEqual(record["registration_request"], self.request_fixture)
        self.assertEqual(record["current_effect"], "NONE")

    def test_missing_fields(self) -> None:
        errors = validate_candidate_registry_record({})
        self.assertTrue(any("missing fields" in err for err in errors))
        self.assertTrue(
            any("candidate_id must be a non-empty string" in err for err in errors)
        )
        self.assertTrue(any("proposal must be a mapping" in err for err in errors))

    def test_extra_fields(self) -> None:
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": None,
            "registration_request": None,
            "current_effect": "NONE",
            "extra_field": "val",
        }
        errors = validate_candidate_registry_record(record)
        self.assertTrue(
            any("unexpected fields: ['extra_field']" in err for err in errors)
        )

    def test_invalid_candidate_id(self) -> None:
        record = {
            "candidate_id": "",
            "proposal": self.proposal_fixture,
            "review": None,
            "registration_request": None,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("candidate_id must be a non-empty string", errors)

    def test_invalid_proposal_mapping(self) -> None:
        record = {
            "candidate_id": "test_id",
            "proposal": "not_a_mapping",
            "review": None,
            "registration_request": None,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("proposal must be a mapping", errors)

    def test_proposal_candidate_id_mismatch(self) -> None:
        mismatched_proposal = dict(self.proposal_fixture)
        mismatched_proposal["candidate_id"] = "other_id"
        record = {
            "candidate_id": "test_id",
            "proposal": mismatched_proposal,
            "review": None,
            "registration_request": None,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("proposal candidate_id must match registry candidate_id", errors)

    def test_invalid_review_mapping(self) -> None:
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": "not_a_mapping",
            "registration_request": None,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("review must be null or a mapping", errors)

    def test_review_candidate_id_mismatch(self) -> None:
        mismatched_review = dict(self.review_fixture)
        mismatched_review["candidate_id"] = "other_id"
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": mismatched_review,
            "registration_request": None,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("review candidate_id must match registry candidate_id", errors)

    def test_invalid_request_mapping(self) -> None:
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": self.review_fixture,
            "registration_request": "not_a_mapping",
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("registration_request must be null or a mapping", errors)

    def test_request_candidate_id_mismatch(self) -> None:
        mismatched_request = dict(self.request_fixture)
        mismatched_request["candidate_id"] = "other_id"
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": self.review_fixture,
            "registration_request": mismatched_request,
            "current_effect": "NONE",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn(
            "registration request candidate_id must match registry candidate_id", errors
        )

    def test_submitted_request_requires_approved_review(self) -> None:
        submitted_request = dict(self.request_fixture)
        submitted_request["status"] = "SUBMITTED"

        # Test with no review
        record1 = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": None,
            "registration_request": submitted_request,
            "current_effect": "NONE",
        }
        errors1 = validate_candidate_registry_record(record1)
        self.assertIn(
            "SUBMITTED or ACCEPTED request requires an APPROVED review", errors1
        )

        # Test with pending review
        pending_review = dict(self.review_fixture)
        pending_review["review_status"] = "PENDING"
        record2 = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": pending_review,
            "registration_request": submitted_request,
            "current_effect": "NONE",
        }
        errors2 = validate_candidate_registry_record(record2)
        self.assertIn(
            "SUBMITTED or ACCEPTED request requires an APPROVED review", errors2
        )

    def test_invalid_current_effect(self) -> None:
        record = {
            "candidate_id": "test_id",
            "proposal": self.proposal_fixture,
            "review": None,
            "registration_request": None,
            "current_effect": "CREATED",
        }
        errors = validate_candidate_registry_record(record)
        self.assertIn("current_effect must remain NONE", errors)


if __name__ == "__main__":
    unittest.main()
