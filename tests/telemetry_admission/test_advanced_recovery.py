"""Advanced TA-F014 and TA-R backup/restore integrity cases."""

from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import shutil
import sqlite3
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dbos.telemetry_admission.models import TelemetryAdmissionError
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


def _manifest_digest(manifest: dict[str, object]) -> str:
    material = {
        key: value for key, value in manifest.items() if key != "manifest_digest"
    }
    encoded = json.dumps(
        material, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


class AdvancedRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-advanced-recovery-")
        self.root = Path(self.temp.name)
        self.path = self.root / "source.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _admit_unique(self, store: SQLiteTelemetryAdmissionStore, index: int) -> None:
        TelemetryAdmissionService(store).admit(
            make_envelope(
                observation_id=f"ta:observation:backup-{index}",
                source_seed=f"backup-source-{index}",
                signal_reference=f"fixture:signal:backup-{index}",
                idempotency_reference=f"fixture:attempt:backup-{index}",
            )
        )

    def test_ta_r002_live_write_backup_is_a_consistent_snapshot(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        for index in range(10):
            self._admit_unique(store, index)

        def writer(index: int) -> None:
            self._admit_unique(SQLiteTelemetryAdmissionStore(self.path), 1000 + index)

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [pool.submit(writer, index) for index in range(40)]
            manifest = store.backup(self.root / "live-backup.sqlite3")
            for future in futures:
                future.result(timeout=15)

        backup_store = SQLiteTelemetryAdmissionStore(self.root / "live-backup.sqlite3")
        backup_report = backup_store.integrity_report()
        self.assertEqual(backup_report["status"], "PASS")
        self.assertEqual(backup_report["counts"], manifest["counts"])
        self.assertLessEqual(
            backup_report["counts"]["admission_lifecycles"],
            store.counts()["admission_lifecycles"],
        )

    def test_ta_r006_wrong_schema_manifest_is_blocked_even_if_resigned(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        self._admit_unique(store, 1)
        backup = self.root / "wrong-schema-backup.sqlite3"
        manifest = store.backup(backup)
        wrong = json.loads(json.dumps(manifest))
        wrong["schema_version"] = "9.0.0"
        wrong["manifest_digest"] = _manifest_digest(wrong)
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore.restore(
                backup, wrong, self.root / "wrong-schema-restored.sqlite3"
            )

    def test_ta_r008_rejected_history_survives_restore(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        rejected = make_envelope(observation_id="ta:observation:rejected-history")
        rejected["evidence_status"] = "VALID"
        original = TelemetryAdmissionService(store).admit(rejected)
        self.assertEqual(original.state, "REJECTED")
        backup = self.root / "rejected-history-backup.sqlite3"
        manifest = store.backup(backup)
        restored = SQLiteTelemetryAdmissionStore.restore(
            backup, manifest, self.root / "rejected-history-restored.sqlite3"
        )
        records = restored.get_records(original.admission_id)
        self.assertEqual(records[-1]["state"], "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", records[-1]["reason_codes"])
        self.assertIsNone(restored.get_envelope(original.observation_reference))

    def test_ta_r009_corruption_variants_fail_and_verified_backup_restores(
        self,
    ) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        for index in range(3):
            self._admit_unique(store, index)
        backup = self.root / "verified-backup.sqlite3"
        manifest = store.backup(backup)

        variants: list[tuple[str, Path]] = []
        header = self.root / "corrupt-header.sqlite3"
        shutil.copy2(backup, header)
        header.chmod(0o600)
        with header.open("r+b") as handle:
            handle.seek(0)
            handle.write(b"CORRUPTED-HEADER")
        variants.append(("header", header))

        truncated = self.root / "corrupt-truncated.sqlite3"
        shutil.copy2(backup, truncated)
        truncated.chmod(0o600)
        with truncated.open("r+b") as handle:
            handle.truncate(max(1, truncated.stat().st_size // 2))
        variants.append(("truncated", truncated))

        missing_index = self.root / "corrupt-missing-index.sqlite3"
        shutil.copy2(backup, missing_index)
        missing_index.chmod(0o600)
        connection = sqlite3.connect(missing_index)
        try:
            connection.execute("DROP INDEX idx_observation_fingerprint")
            connection.commit()
        finally:
            connection.close()
        variants.append(("missing_index", missing_index))

        for name, corrupt_path in variants:
            with self.subTest(name=name):
                corrupt_report = SQLiteTelemetryAdmissionStore(
                    corrupt_path
                ).integrity_report()
                self.assertEqual(corrupt_report["status"], "FAIL")
                restored = SQLiteTelemetryAdmissionStore.restore(
                    backup,
                    manifest,
                    self.root / f"restored-from-{name}.sqlite3",
                )
                self.assertEqual(restored.integrity_report()["status"], "PASS")
                self.assertTrue(corrupt_path.exists())

    def test_ta_f014_async_backup_and_restore_cancellation_preserves_paths(
        self,
    ) -> None:
        source = SQLiteTelemetryAdmissionStore(self.path)
        for index in range(5):
            self._admit_unique(source, index)

        backup_reached = threading.Event()
        backup_release = threading.Event()

        def backup_pause(point: str) -> None:
            if point == "after_backup_copy":
                backup_reached.set()
                if not backup_release.wait(timeout=5):
                    raise RuntimeError("backup-pause-timeout")

        pausing_store = SQLiteTelemetryAdmissionStore(
            self.path, fault_injector=backup_pause
        )
        backup = self.root / "cancelled-backup.sqlite3"

        async def cancel_backup() -> None:
            task = asyncio.create_task(asyncio.to_thread(pausing_store.backup, backup))
            await asyncio.to_thread(backup_reached.wait, 5)
            task.cancel()
            backup_release.set()
            with self.assertRaises(asyncio.CancelledError):
                await task

        asyncio.run(cancel_backup())
        deadline = time.monotonic() + 5
        while source.counts()["backup_manifests"] == 0 and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(backup.exists())
        self.assertEqual(
            SQLiteTelemetryAdmissionStore(backup).integrity_report()["status"], "PASS"
        )

        manifest = source.backup(self.root / "restore-source-backup.sqlite3")
        restore_backup = self.root / "restore-source-backup.sqlite3"
        restore_reached = threading.Event()
        restore_release = threading.Event()

        def restore_pause(point: str) -> None:
            if point == "after_restore_copy":
                restore_reached.set()
                if not restore_release.wait(timeout=5):
                    raise RuntimeError("restore-pause-timeout")

        restored_path = self.root / "cancelled-restore.sqlite3"
        operation = functools.partial(
            SQLiteTelemetryAdmissionStore.restore,
            restore_backup,
            manifest,
            restored_path,
            fault_injector=restore_pause,
        )

        async def cancel_restore() -> None:
            task = asyncio.create_task(asyncio.to_thread(operation))
            await asyncio.to_thread(restore_reached.wait, 5)
            task.cancel()
            restore_release.set()
            with self.assertRaises(asyncio.CancelledError):
                await task

        asyncio.run(cancel_restore())
        self.assertTrue(self.path.exists())
        self.assertTrue(restore_backup.exists())
        self.assertTrue(restored_path.exists())
        self.assertEqual(
            SQLiteTelemetryAdmissionStore(restored_path).integrity_report()["status"],
            "PASS",
        )


if __name__ == "__main__":
    unittest.main()
