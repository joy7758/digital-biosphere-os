"""Deterministic relevance admission tests for public capability discovery."""

from __future__ import annotations

import unittest

from discovery.pipeline import _matches_profile_relevance


class RelevanceGateTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "profile_id": "EVIDENCE_AND_PROVENANCE",
            "relevance_term_groups": [
                ["agent", "agentic", "multi-agent", "llm"],
                ["evidence", "provenance", "traceability", "audit"],
            ],
        }

    def test_relevant_agent_evidence_record_is_admitted(self):
        record = {
            "name": "Agent evidence ledger",
            "summary": "Traceability and provenance for agent actions.",
        }
        self.assertTrue(_matches_profile_relevance(record, self.profile))

    def test_non_agent_provenance_record_is_rejected(self):
        record = {
            "name": "Scientific image provenance",
            "summary": "Evidence retention for telescope observations.",
        }
        self.assertFalse(_matches_profile_relevance(record, self.profile))

    def test_agent_record_without_profile_capability_is_rejected(self):
        record = {
            "name": "Agent route planner",
            "summary": "An agent computes travel routes.",
        }
        self.assertFalse(_matches_profile_relevance(record, self.profile))

    def test_missing_relevance_configuration_fails_closed(self):
        record = {"name": "Agent evidence", "summary": "Provenance."}
        self.assertFalse(_matches_profile_relevance(record, {"profile_id": "UNKNOWN"}))

    def test_long_horizon_agent_without_memory_is_rejected(self):
        profile = {
            "profile_id": "AGENT_MEMORY_AND_CONTINUITY",
            "relevance_term_groups": [
                ["agent", "agentic", "multi-agent", "llm"],
                ["memory", "continuity"],
            ],
        }
        record = {
            "name": "Agentic GPU kernel optimizer",
            "summary": "A long-horizon agent edits assembly and verifies output.",
        }
        self.assertFalse(_matches_profile_relevance(record, profile))


if __name__ == "__main__":
    unittest.main()
