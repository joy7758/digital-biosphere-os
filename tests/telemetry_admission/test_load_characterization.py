"""Fast unit checks for the measurement-only TA-P harness."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from tools.telemetry_admission_characterize import (
    CONTRACT_PATH,
    _finish_execution_binding,
    _start_execution_binding,
    characterize_p001,
    characterize_p002,
    characterize_p003,
    characterize_p004,
    characterize_p005,
    main,
    write_result_artifact,
)


class LoadCharacterizationHarnessTests(unittest.TestCase):
    def test_contract_freezes_exact_workloads_without_posthoc_thresholds(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["contract_revision"], "0.1.1")
        self.assertEqual(
            contract["supersedes_contract_digest"],
            "sha256:b817493ba4c5381dfe26cb042832b75a7f4d4c75f3948ba8d104e37f49f54e91",
        )
        self.assertEqual(
            contract["change_reason"],
            "REMOVE_CONCURRENT_TRACEMALLOC_OBSERVER_EFFECT",
        )
        self.assertTrue(contract["frozen_before_execution"])
        self.assertEqual(contract["result_semantics"], "CHARACTERIZATION_NOT_SLO")
        self.assertIsNone(contract["pass_fail_thresholds"])
        self.assertEqual(
            contract["measurement_controls"]["concurrent_python_allocation_tracing"],
            "DISABLED_TO_AVOID_OBSERVER_EFFECT",
        )
        self.assertFalse(contract["workloads"]["TA-P003"]["python_allocation_tracing"])
        self.assertEqual(
            set(contract["workloads"]), {f"TA-P00{i}" for i in range(1, 6)}
        )
        self.assertFalse(any(contract["authority_effects"].values()))

    def test_small_p001_and_p002_runs_measure_without_authority_effects(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-ta-p001-test-") as temporary:
            result = characterize_p001(Path(temporary), 3)
        self.assertEqual(result["measurements"]["operations"], 3)
        self.assertEqual(result["measurements"]["integrity"]["status"], "PASS")
        self.assertFalse(any(result["authority_effects"].values()))

        with tempfile.TemporaryDirectory(prefix="dbos-ta-p002-test-") as temporary:
            result = characterize_p002(Path(temporary), 2, 4)
        self.assertEqual(result["measurements"]["confirmed_retries"], 4)
        self.assertEqual(result["measurements"]["duplicate_accuracy"], 1.0)
        self.assertEqual(result["measurements"]["lifecycle_growth"], 0)

    def test_small_concurrency_backup_and_soak_runs_remain_integral(self) -> None:
        with (
            tempfile.TemporaryDirectory(prefix="dbos-ta-p003-test-") as temporary,
            patch(
                "tools.telemetry_admission_characterize.tracemalloc.start"
            ) as tracing_start,
        ):
            result = characterize_p003(Path(temporary), 2, 0.1, 20)
        tracing_start.assert_not_called()
        self.assertEqual(result["measurements"]["integrity"]["status"], "PASS")
        self.assertFalse(result["measurements"]["python_allocation_tracing"])
        self.assertIsNone(result["measurements"]["python_tracemalloc_peak_bytes"])
        self.assertEqual(
            result["measurements"]["observer_effect_control"],
            "CONCURRENT_TRACEMALLOC_DISABLED_PROCESS_MAX_RSS_RETAINED",
        )

        with tempfile.TemporaryDirectory(prefix="dbos-ta-p004-test-") as temporary:
            result = characterize_p004(Path(temporary), 20, 2)
        self.assertEqual(result["measurements"]["integrity"]["status"], "PASS")
        self.assertEqual(result["measurements"]["restore_pass_rate"], 1.0)

        with tempfile.TemporaryDirectory(prefix="dbos-ta-p005-test-") as temporary:
            result = characterize_p005(Path(temporary), 0.2, 20, 0.05)
        self.assertEqual(result["measurements"]["final_integrity"]["status"], "PASS")
        self.assertFalse(any(result["authority_effects"].values()))

    def test_execution_binding_proves_source_stability(self) -> None:
        binding = _finish_execution_binding(_start_execution_binding())
        self.assertEqual(binding["binding_result"], "PASS")
        self.assertTrue(binding["source_stable_during_run"])
        self.assertEqual(
            binding["implementation_manifest_at_start"]["manifest_digest"],
            binding["implementation_manifest_at_end"]["manifest_digest"],
        )
        self.assertEqual(
            binding["contract"]["path"],
            "tests/telemetry_admission/load_characterization.v0.1.json",
        )

    def test_result_artifact_is_private_and_cannot_be_overwritten(self) -> None:
        result = {"case_id": "TA-P001", "status": "PASS"}
        with tempfile.TemporaryDirectory(prefix="dbos-ta-result-test-") as temporary:
            target = Path(temporary) / "result.json"
            receipt = write_result_artifact(target, result)
            self.assertEqual(receipt["mode"], "0o600")
            self.assertEqual(os.stat(target).st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), result)
            with self.assertRaises(FileExistsError):
                write_result_artifact(target, {"status": "REPLACED"})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), result)

    def test_cli_rejects_existing_result_before_workload_starts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-ta-preflight-test-") as temporary:
            target = Path(temporary) / "result.json"
            target.write_text("preserve", encoding="utf-8")
            work_dir = Path(temporary) / "work-must-not-exist"
            output = StringIO()
            arguments = [
                "telemetry_admission_characterize.py",
                "TA-P001",
                "--count",
                "1",
                "--work-dir",
                str(work_dir),
                "--output",
                str(target),
            ]
            with patch.object(sys, "argv", arguments), redirect_stdout(output):
                exit_code = main()
            receipt = json.loads(output.getvalue())
            self.assertEqual(exit_code, 2)
            self.assertEqual(receipt["error_code"], "RESULT_ARTIFACT_TARGET_REJECTED")
            self.assertFalse(receipt["workload_started"])
            self.assertFalse(work_dir.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
