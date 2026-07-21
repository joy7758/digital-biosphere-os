#!/usr/bin/env python3
"""Negative governance and side-effect tests for the trust demo."""

from __future__ import annotations

import inspect
import unittest

from examples.multi_agent_trust_demo import demo as demo_module
from examples.multi_agent_trust_demo.demo import build_demo
from validator import validate_object


class MultiAgentTrustDemoBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.demo = build_demo()

    def test_all_governance_side_effects_are_false(self) -> None:
        self.assertTrue(self.demo["non_effects"])
        self.assertFalse(any(self.demo["non_effects"].values()))

    def test_review_requires_human_and_claims_no_truth_or_authority(self) -> None:
        review = self.demo["steps"][2]["role_output"]
        self.assertEqual(review["review_result"], "HUMAN_REVIEW_REQUIRED")
        self.assertFalse(review["scientific_truth_claimed"])
        self.assertFalse(review["publication_approved"])
        self.assertFalse(review["execution_authorized"])

    def test_permission_injection_is_rejected_by_validator(self) -> None:
        execution = dict(self.demo["steps"][0]["execution"])
        execution["permission"] = "ALLOW"
        result = validate_object(execution)
        self.assertEqual(result.result.value, "FAIL")

    def test_demo_source_has_no_network_subprocess_or_dynamic_execution(self) -> None:
        source = inspect.getsource(demo_module)
        forbidden = ("import socket", "import requests", "import subprocess", "eval(", "exec(")
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
