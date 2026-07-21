"""Negative story tests for capability, permission, and version boundaries."""

from __future__ import annotations

import unittest

from examples.mcp_reference_demo import run_reference_demo


class DemoNegativeBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = {
            item["case_id"]: item
            for item in run_reference_demo()["negative_cases"]
        }

    def test_tool_to_capability_is_rejected(self) -> None:
        case = self.cases["TOOL_TO_CAPABILITY_REJECTED"]

        self.assertEqual(case["observed_mapping_status"], "REJECTED")
        self.assertEqual(case["observed_validation_result"], "FAIL")
        self.assertEqual(
            case["adapter_errors"][0]["error_code"],
            "INVALID_TOOL_REFERENCE",
        )

    def test_tool_permission_to_dbos_permission_is_rejected(self) -> None:
        case = self.cases["TOOL_PERMISSION_TO_DBOS_PERMISSION_REJECTED"]

        self.assertEqual(case["observed_mapping_status"], "REJECTED")
        self.assertEqual(case["observed_validation_result"], "FAIL")
        self.assertIn("tool_permission", case["adapter_errors"][0]["field_reference"])

    def test_unknown_version_returns_version_mismatch(self) -> None:
        case = self.cases["UNKNOWN_VERSION_REJECTED"]

        self.assertEqual(case["observed_mapping_status"], "VERSION_MISMATCH")
        self.assertEqual(case["observed_validation_result"], "VERSION_MISMATCH")
        self.assertEqual(
            case["adapter_errors"][0]["error_code"],
            "VERSION_MISMATCH",
        )

    def test_all_negative_cases_create_no_candidate(self) -> None:
        self.assertEqual(len(self.cases), 3)
        for case in self.cases.values():
            with self.subTest(case=case["case_id"]):
                self.assertTrue(case["expectation_met"])
                self.assertFalse(case["candidate_created"])


if __name__ == "__main__":
    unittest.main()
