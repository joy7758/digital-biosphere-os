"""Local rollback drill preserves failure and stops at human switch gate."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.telemetry_admission_rollback_drill import run_drill


class RollbackDrillTests(unittest.TestCase):
    def test_drill_restores_acknowledged_inventory_without_automatic_switch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-ta-rollback-test-") as temporary:
            result = run_drill(Path(temporary) / "drill", admission_count=3)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["receipt_mismatch_count"], 0)
        self.assertTrue(result["failed_source_retained"])
        self.assertTrue(result["restore_destination_is_distinct"])
        self.assertFalse(result["automatic_switch_performed"])
        self.assertEqual(result["next_gate"], "HUMAN_SWITCH_REQUIRED")
        self.assertFalse(any(result["authority_effects"].values()))


if __name__ == "__main__":
    unittest.main()
