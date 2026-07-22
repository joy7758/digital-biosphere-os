"""TA-F transaction, failure, and corruption cases."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from dbos.telemetry_admission.models import TelemetryAdmissionError
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


class StorageFaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-fault-")
        self.path = Path(self.temp.name) / "admission.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _failing_store(self, point: str) -> SQLiteTelemetryAdmissionStore:
        def inject(actual: str) -> None:
            if actual == point:
                raise RuntimeError("synthetic-fault")

        return SQLiteTelemetryAdmissionStore(self.path, fault_injector=inject)

    def test_ta_f002_failure_after_lifecycle_insert_rolls_back(self) -> None:
        service = TelemetryAdmissionService(
            self._failing_store("after_lifecycle_insert")
        )
        with self.assertRaises(TelemetryAdmissionError) as caught:
            service.admit(make_envelope())
        self.assertEqual(caught.exception.reason_code, "TA_STORAGE_UNAVAILABLE")
        clean = SQLiteTelemetryAdmissionStore(self.path)
        self.assertEqual(clean.counts()["admission_lifecycles"], 0)
        self.assertEqual(clean.counts()["admission_records"], 0)

    def test_ta_f003_failure_before_commit_has_no_false_acknowledgement(self) -> None:
        service = TelemetryAdmissionService(self._failing_store("before_commit"))
        with self.assertRaises(TelemetryAdmissionError):
            service.admit(make_envelope())
        clean = SQLiteTelemetryAdmissionStore(self.path)
        self.assertEqual(clean.counts()["intake_receipts"], 0)
        self.assertEqual(clean.counts()["observation_envelopes"], 0)

    def test_ta_f004_committed_result_survives_reopen(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        result = TelemetryAdmissionService(store).admit(make_envelope())
        reopened = SQLiteTelemetryAdmissionStore(self.path)
        reopened.initialize()
        self.assertEqual(
            reopened.get_records(result.admission_id)[-1]["state"], result.state
        )

    def test_ta_f005_lock_timeout_fails_closed(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        lock = sqlite3.connect(self.path, isolation_level=None)
        try:
            lock.execute("BEGIN IMMEDIATE")
            constrained = SQLiteTelemetryAdmissionStore(self.path, busy_timeout_ms=10)
            with self.assertRaises(TelemetryAdmissionError):
                TelemetryAdmissionService(constrained).admit(make_envelope())
        finally:
            lock.rollback()
            lock.close()
        self.assertEqual(store.counts()["admission_records"], 0)

    def test_ta_f007_corrupt_header_fails_integrity_check(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        with self.path.open("r+b") as handle:
            handle.seek(0)
            handle.write(b"CORRUPTED-DBOS!!")
            handle.flush()
            os.fsync(handle.fileno())
        self.assertEqual(store.integrity_report()["status"], "FAIL")

    def test_rejected_input_is_retained_as_stub_not_raw_envelope(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        envelope = make_envelope()
        envelope["prompt"] = "synthetic-raw-payload"
        result = TelemetryAdmissionService(store).admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertIsNone(store.get_envelope(result.observation_reference))
        self.assertEqual(store.counts()["observation_envelopes"], 1)

    def test_store_files_are_owner_only(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        for path in Path(self.temp.name).iterdir():
            if path.is_file() and path.name.startswith("admission.sqlite3"):
                self.assertEqual(path.stat().st_mode & 0o077, 0)


if __name__ == "__main__":
    unittest.main()
