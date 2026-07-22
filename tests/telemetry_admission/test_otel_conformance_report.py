"""Machine-readable report preserves subset and full-catalog boundaries."""

from __future__ import annotations

import unittest

from tools.telemetry_admission_otel_conformance import build_report


class OTelConformanceReportTests(unittest.TestCase):
    def test_authorized_subsets_pass_while_full_catalog_remains_blocked(self) -> None:
        report = build_report("2026-07-22T07:00:00+00:00")
        self.assertEqual(report["authorized_subset_result"], "PASS")
        self.assertEqual(report["full_catalog_result"], "BLOCKED")
        self.assertEqual(
            (
                report["semantic"]["authorized_passed"],
                report["semantic"]["authorized_case_count"],
                report["semantic"]["blocked_not_authorized_count"],
            ),
            (32, 32, 14),
        )
        self.assertEqual(
            (
                report["schema_resource"]["authorized_passed"],
                report["schema_resource"]["authorized_case_count"],
                report["schema_resource"]["blocked_not_authorized_count"],
            ),
            (36, 36, 9),
        )
        self.assertFalse(report["independent_review_complete"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(any(report["effects"].values()))
        self.assertFalse(
            report["source"]["source_commit_includes_current_implementation"]
        )


if __name__ == "__main__":
    unittest.main()
