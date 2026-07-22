"""Advanced TA-F transaction, crash, conflict, and cancellation cases."""

from __future__ import annotations

import asyncio
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dbos.telemetry_admission.metrics import AdmissionMetrics
from dbos.telemetry_admission.models import TelemetryAdmissionError
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


ROOT = Path(__file__).resolve().parents[2]
WORKER = Path(__file__).with_name("subprocess_fault_worker.py")


class AdvancedFaultConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-advanced-fault-")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _run_crash_worker(
        self, path: Path, fault_point: str
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONPATH"] = os.pathsep.join(
            (str(ROOT), str(Path(__file__).parent), environment.get("PYTHONPATH", ""))
        )
        return subprocess.run(
            [sys.executable, str(WORKER), str(path), fault_point],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )

    def test_ta_f001_before_transaction_failure_has_no_record(self) -> None:
        path = self.root / "before-transaction.sqlite3"

        def fail(point: str) -> None:
            if point == "before_transaction":
                raise RuntimeError("synthetic-before-transaction")

        store = SQLiteTelemetryAdmissionStore(path, fault_injector=fail)
        with self.assertRaises(TelemetryAdmissionError):
            TelemetryAdmissionService(store).admit(make_envelope())
        clean = SQLiteTelemetryAdmissionStore(path)
        self.assertEqual(clean.counts()["admission_records"], 0)
        self.assertEqual(clean.counts()["intake_receipts"], 0)

    def test_ta_f006_disk_full_failure_rolls_back_and_is_bounded(self) -> None:
        path = self.root / "disk-full.sqlite3"
        metrics = AdmissionMetrics()

        def disk_full(point: str) -> None:
            if point == "before_commit":
                raise sqlite3.OperationalError(
                    "database or disk is full: synthetic payload"
                )

        store = SQLiteTelemetryAdmissionStore(path, fault_injector=disk_full)
        service = TelemetryAdmissionService(store, metrics=metrics)
        with self.assertRaises(TelemetryAdmissionError) as caught:
            service.admit(make_envelope())
        self.assertEqual(str(caught.exception), "TA_STORAGE_UNAVAILABLE")
        self.assertNotIn("synthetic payload", str(caught.exception))
        self.assertEqual(
            SQLiteTelemetryAdmissionStore(path).counts()["admission_records"], 0
        )
        self.assertIn("storage_failure|TRACE|0.1.0", metrics.snapshot()["requests"])

    def test_ta_f009_32_conflicting_digests_cannot_replace_original(self) -> None:
        path = self.root / "conflicting-digests.sqlite3"
        store = SQLiteTelemetryAdmissionStore(path)
        service = TelemetryAdmissionService(store)
        original_envelope = make_envelope()
        original = service.admit(
            original_envelope, admission_id="ta:admission:conflict-race"
        )

        def conflict(index: int) -> str:
            envelope = make_envelope(
                observation_id=f"ta:observation:conflict-{index}",
                source_seed=f"conflict-source-{index}",
                signal_reference=f"fixture:signal:conflict-{index}",
                idempotency_reference=f"fixture:attempt:conflict-{index}",
            )
            return (
                TelemetryAdmissionService(SQLiteTelemetryAdmissionStore(path))
                .admit(
                    envelope,
                    admission_id=original.admission_id,
                    claimed_intake_receipt_reference=original.intake_receipt_reference,
                )
                .state
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            states = list(pool.map(conflict, range(32)))
        self.assertEqual(states, ["REJECTED"] * 32)
        records = store.get_records(original.admission_id)
        self.assertEqual(records[-1]["state"], "ACCEPTED_AS_MATERIAL")
        self.assertEqual(store.counts()["admission_lifecycles"], 33)
        self.assertEqual(store.integrity_report()["status"], "PASS")

    def test_ta_f011_missing_wal_is_detected_against_ack_inventory(self) -> None:
        path = self.root / "missing-wal.sqlite3"
        completed = self._run_crash_worker(path, "after_commit")
        self.assertEqual(completed.returncode, 73, completed.stderr)
        wal = Path(f"{path}-wal")
        self.assertTrue(wal.is_file())
        preserved_wal = self.root / "missing-wal.preserved-wal"
        wal.rename(preserved_wal)
        store = SQLiteTelemetryAdmissionStore(path)
        report = store.integrity_report(
            expected_receipt_references=("ta:receipt:subprocess-1",)
        )
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["missing_expected_receipt_count"], 1)
        self.assertTrue(path.exists())
        self.assertTrue(preserved_wal.exists())

    def test_ta_f012_abrupt_process_exit_is_atomic_at_each_fault_point(self) -> None:
        for point in (
            "before_transaction",
            "after_lifecycle_insert",
            "before_commit",
            "after_commit",
        ):
            with self.subTest(point=point):
                path = self.root / f"crash-{point}.sqlite3"
                completed = self._run_crash_worker(path, point)
                self.assertEqual(completed.returncode, 73, completed.stderr)
                store = SQLiteTelemetryAdmissionStore(path)
                counts = store.counts()
                if point == "after_commit":
                    self.assertEqual(counts["admission_lifecycles"], 1)
                    self.assertEqual(counts["admission_records"], 3)
                    self.assertEqual(counts["intake_receipts"], 1)
                else:
                    self.assertEqual(counts["admission_lifecycles"], 0)
                    self.assertEqual(counts["admission_records"], 0)
                    self.assertEqual(counts["intake_receipts"], 0)
                self.assertEqual(store.integrity_report()["status"], "PASS")

    def test_ta_f013_async_cancellation_leaves_committed_retry_deterministic(
        self,
    ) -> None:
        path = self.root / "async-cancel.sqlite3"
        reached = threading.Event()
        release = threading.Event()

        def pause(point: str) -> None:
            if point == "before_commit":
                reached.set()
                if not release.wait(timeout=5):
                    raise RuntimeError("synthetic-timeout")

        store = SQLiteTelemetryAdmissionStore(path, fault_injector=pause)
        envelope = make_envelope()

        async def scenario() -> None:
            task = asyncio.create_task(
                asyncio.to_thread(
                    TelemetryAdmissionService(store).admit,
                    envelope,
                    admission_id="ta:admission:async-cancel",
                )
            )
            await asyncio.to_thread(reached.wait, 5)
            task.cancel()
            release.set()
            with self.assertRaises(asyncio.CancelledError):
                await task

        asyncio.run(scenario())
        deadline = time.monotonic() + 5
        while (
            store.counts()["admission_lifecycles"] == 0 and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        receipt = store.get_receipt_for_admission("ta:admission:async-cancel")
        self.assertIsNotNone(receipt)
        retry = TelemetryAdmissionService(SQLiteTelemetryAdmissionStore(path)).admit(
            envelope,
            admission_id="ta:admission:async-cancel",
            claimed_intake_receipt_reference=receipt,
        )
        self.assertEqual(retry.state, "DUPLICATE_CONFIRMED")
        self.assertEqual(store.integrity_report()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
