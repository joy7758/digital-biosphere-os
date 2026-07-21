#!/usr/bin/env python3
"""Success-path and contract tests for the three-role trust demo."""

from __future__ import annotations

import unittest

from examples.multi_agent_trust_demo.demo import ROLE_ORDER, build_demo


class MultiAgentTrustDemoContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.demo = build_demo()

    def test_role_order_is_research_analysis_review(self) -> None:
        self.assertEqual(
            self.demo["role_order"],
            ["research_agent", "analysis_agent", "review_agent"],
        )
        self.assertEqual(tuple(self.demo["role_order"]), ROLE_ORDER)

    def test_every_role_has_entity_execution_evidence_and_three_validations(self) -> None:
        self.assertEqual(len(self.demo["steps"]), 3)
        for step in self.demo["steps"]:
            self.assertEqual(step["entity"]["lifecycle_state"], "PROPOSED")
            self.assertEqual(step["execution"]["status"], "CREATED")
            self.assertEqual(step["evidence_reference"]["integrity_status"], "PENDING")
            self.assertTrue(
                all(
                    result["result"] == "PASS"
                    for result in step["validation_results"].values()
                )
            )

    def test_shared_saee_envelope_has_declared_inputs_only(self) -> None:
        envelope = self.demo["dbos_to_saee_envelope"]
        self.assertEqual(len(envelope["execution_history"]), 3)
        self.assertEqual(len(envelope["evidence_references"]), 3)
        self.assertEqual(len(envelope["validation_results"]), 9)
        self.assertEqual(envelope["resource_information"]["model_call_count"], 0)
        self.assertNotIn("fitness", envelope)
        self.assertNotIn("evolution_recommendation", envelope)

    def test_demo_contract_is_satisfied(self) -> None:
        self.assertTrue(self.demo["demo_contract_satisfied"])


if __name__ == "__main__":
    unittest.main()
