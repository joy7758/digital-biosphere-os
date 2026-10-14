"""Activation-report completeness tests for bounded capability discovery."""

from __future__ import annotations

import unittest
from pathlib import Path

from cockpit.weekly.cells.memory import MemoryCell


REPOSITORY = Path(__file__).resolve().parents[5]
WEEKLY = REPOSITORY / "digital-biosphere-architecture/cockpit/weekly"


class ActivationReportTests(unittest.TestCase):
    def test_report_records_run_and_artifact_identity(self):
        source = (WEEKLY / "run_weekly.py").read_text()
        self.assertIn("本轮运行 ID", source)
        self.assertIn("前次运行 ID", source)
        self.assertIn("前次 Artifact ID", source)
        self.assertIn("最新驾驶舱制品", source)

    def test_report_records_both_schedule_variables(self):
        source = (WEEKLY / "run_weekly.py").read_text()
        self.assertIn("DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED", source)
        self.assertIn("DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED", source)
        self.assertIn("自动发现定时变量", source)
        self.assertIn("完整周检定时变量", source)

    def test_workflow_injects_only_non_secret_schedule_state(self):
        workflow = (REPOSITORY / ".github/workflows/dba-weekly-cockpit.yml").read_text()
        self.assertIn(
            "DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED: ${{ vars.DBA_AUTOMATIC_CAPABILITY_DISCOVERY_ENABLED }}",
            workflow,
        )
        self.assertIn(
            "DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED: ${{ vars.DBA_WEEKLY_COCKPIT_SCHEDULE_ENABLED }}",
            workflow,
        )
        capability_job = workflow.split("  capability-discovery:\n", 1)[1]
        capability_job = capability_job.split("  schedule-disabled:\n", 1)[0]
        self.assertNotIn("DBA_COCKPIT_READ_TOKEN", capability_job)

    def test_memory_preserves_previous_artifact_identity(self):
        result = MemoryCell()._run({
            "snapshot_mode": "AUTOMATIC_CAPABILITY_DISCOVERY",
            "capability_memory_metadata": {
                "previous_registry_loaded": True,
                "previous_run_id": "33248431482",
                "artifact_id": "123456",
                "source_reference": "github-actions-run:33248431482/artifact:123456",
                "memory_bootstrap_source": "PREVIOUS_SUCCESSFUL_MAIN_ARTIFACT",
            },
            "capability_discovery_delta": {"counts": {}, "events": []},
        })
        memory = result.outputs["memory"]
        self.assertEqual("33248431482", memory["PREVIOUS_CAPABILITY_RUN_ID"])
        self.assertEqual("123456", memory["PREVIOUS_CAPABILITY_ARTIFACT_ID"])
        self.assertEqual(
            "github-actions-run:33248431482/artifact:123456",
            memory["PREVIOUS_CAPABILITY_SOURCE_REFERENCE"],
        )


if __name__ == "__main__":
    unittest.main()
