"""Integrated fail-closed tests for Digital Entity Infrastructure."""

from __future__ import annotations

import unittest

from validation.digital_entity_infrastructure_validator import validate


class NegativeConformanceTests(unittest.TestCase):
    def test_all_integrated_negative_cases_are_rejected(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["negative_case_count"], 11)
        self.assertEqual(result["rejected_negative_case_count"], 11)

    def test_all_side_effect_counts_remain_zero(self) -> None:
        result = validate()
        self.assertTrue(all(count == 0 for count in result["side_effect_counts"].values()))

    def test_conformance_covers_all_roadmap_areas(self) -> None:
        result = validate()
        self.assertEqual(result["module_count"], 12)
        self.assertEqual(result["conformance_area_count"], 8)


if __name__ == "__main__":
    unittest.main()
