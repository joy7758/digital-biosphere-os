"""TA-M and TA-R migration, backup, restore, and rollback-boundary cases."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from dbos.telemetry_admission.models import TelemetryAdmissionError
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import (
    DATABASE_USER_VERSION,
    MIGRATION_VERSION,
    SQLiteTelemetryAdmissionStore,
    migration_checksum,
)
from fixtures import create_prior_compatible_store, make_envelope


class MigrationRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-recovery-")
        self.root = Path(self.temp.name)
        self.path = self.root / "admission.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_ta_m001_initial_store_has_exact_migration_checksum(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            row = connection.execute(
                "SELECT version,checksum FROM schema_migrations"
            ).fetchone()
            user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(row, (MIGRATION_VERSION, migration_checksum()))
        self.assertEqual(user_version, DATABASE_USER_VERSION)

    def test_ta_m002_reopen_is_non_mutating(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        before = store.counts()
        SQLiteTelemetryAdmissionStore(self.path).initialize()
        self.assertEqual(store.counts(), before)

    def test_ta_m003_newer_user_version_is_rejected_without_downgrade(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute(f"PRAGMA user_version={DATABASE_USER_VERSION + 1}")
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()
        connection = sqlite3.connect(self.path)
        try:
            self.assertEqual(
                connection.execute("PRAGMA user_version").fetchone()[0],
                DATABASE_USER_VERSION + 1,
            )
        finally:
            connection.close()

    def test_ta_m004_tampered_migration_checksum_is_rejected(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("DROP TRIGGER schema_migrations_no_update")
            connection.execute(
                "UPDATE schema_migrations SET checksum=? WHERE version=?",
                ("sha256:" + "0" * 64, MIGRATION_VERSION),
            )
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()

    def test_ta_m005_interrupted_initial_migration_rolls_back(self) -> None:
        def interrupt(point: str) -> None:
            if point == "after_migration_statement":
                raise RuntimeError("synthetic-migration-interruption")

        interrupted = SQLiteTelemetryAdmissionStore(self.path, fault_injector=interrupt)
        with self.assertRaises(TelemetryAdmissionError):
            interrupted.initialize()
        connection = sqlite3.connect(self.path)
        try:
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(tables, [])
        recovered = SQLiteTelemetryAdmissionStore(self.path)
        recovered.initialize()
        self.assertEqual(recovered.integrity_report()["status"], "PASS")

    def test_ta_m005_interrupted_compatibility_migration_preserves_prior(self) -> None:
        prior = create_prior_compatible_store(self.path)

        def interrupt(point: str) -> None:
            if point == "after_compatibility_migration_statement":
                raise RuntimeError("synthetic-compatibility-interruption")

        interrupted = SQLiteTelemetryAdmissionStore(self.path, fault_injector=interrupt)
        backup = self.root / "interrupted-pre-backup.sqlite3"
        with self.assertRaises(TelemetryAdmissionError):
            interrupted.migrate_compatible(backup)
        self.assertTrue(backup.exists())
        self.assertEqual(
            prior.migration_preflight()["classification"],
            "COMPATIBLE_MIGRATION_REQUIRED",
        )
        result = prior.migrate_compatible(self.root / "retry-pre-backup.sqlite3")
        self.assertEqual(result["status"], "MIGRATED")
        self.assertEqual(prior.integrity_report()["status"], "PASS")

    def test_ta_m006_compatible_fixture_backup_dry_run_apply_validate(self) -> None:
        prior = create_prior_compatible_store(self.path)
        self.assertEqual(
            prior.migration_preflight()["classification"],
            "COMPATIBLE_MIGRATION_REQUIRED",
        )
        backup = self.root / "compatible-pre-backup.sqlite3"
        result = prior.migrate_compatible(backup)
        self.assertEqual(result["status"], "MIGRATED")
        self.assertEqual(result["dry_run"], "PASS")
        self.assertTrue(result["backup_immutable"])
        report = prior.integrity_report()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(set(report["migration_checksums"]), {"0000", "0001-compat"})
        self.assertEqual(
            SQLiteTelemetryAdmissionStore(backup).migration_preflight()[
                "classification"
            ],
            "COMPATIBLE_MIGRATION_REQUIRED",
        )

    def test_ta_m009_restored_prior_backup_migrates_without_mutating_backup(
        self,
    ) -> None:
        prior = create_prior_compatible_store(self.path)
        original_backup = self.root / "prior-backup.sqlite3"
        prior.migrate_compatible(original_backup)
        before = original_backup.read_bytes()
        restored_prior = self.root / "restored-prior.sqlite3"
        shutil.copy2(original_backup, restored_prior)
        restored_prior.chmod(0o600)
        restored = SQLiteTelemetryAdmissionStore(restored_prior)
        self.assertEqual(
            restored.migration_preflight()["classification"],
            "COMPATIBLE_MIGRATION_REQUIRED",
        )
        result = restored.migrate_compatible(
            self.root / "restored-prior-pre-migration.sqlite3"
        )
        self.assertEqual(result["post_validation"], "PASS")
        self.assertEqual(restored.integrity_report()["status"], "PASS")
        self.assertEqual(original_backup.read_bytes(), before)

    def test_ta_m008_second_migration_execution_is_no_op(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        before = store.integrity_report()
        store.initialize()
        after = store.integrity_report()
        self.assertEqual(after["migration_checksums"], before["migration_checksums"])
        self.assertEqual(after["counts"], before["counts"])

    def test_ta_m010_older_application_blocks_newer_store(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute(f"PRAGMA user_version={DATABASE_USER_VERSION + 10}")
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()

    def test_ta_m011_missing_index_is_detected_before_use(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("DROP INDEX idx_observation_fingerprint")
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()

    def test_ta_m012_unknown_breaking_version_is_not_best_effort_converted(
        self,
    ) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        store.initialize()
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("DROP TRIGGER schema_migrations_no_update")
            connection.execute(
                "UPDATE schema_migrations SET version='9000', checksum=?",
                ("sha256:" + "9" * 64,),
            )
            connection.execute("PRAGMA user_version=9000")
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()
        connection = sqlite3.connect(self.path)
        try:
            row = connection.execute(
                "SELECT version,checksum FROM schema_migrations"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(row, ("9000", "sha256:" + "9" * 64))

    def test_ta_m011_nonempty_unknown_schema_is_rejected(self) -> None:
        os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600))
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("CREATE TABLE unknown_table(value TEXT)")
            connection.commit()
        finally:
            connection.close()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(self.path).initialize()

    def test_ta_r001_and_r003_backup_and_restore_preserve_chain(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        first = TelemetryAdmissionService(store).admit(make_envelope())
        backup = self.root / "backup.sqlite3"
        manifest = store.backup(backup)
        restored = SQLiteTelemetryAdmissionStore.restore(
            backup, manifest, self.root / "restored.sqlite3"
        )
        self.assertEqual(restored.integrity_report()["status"], "PASS")
        self.assertEqual(
            restored.get_records(first.admission_id),
            store.get_records(first.admission_id),
        )

    def test_ta_r004_tampered_manifest_is_rejected(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        backup = self.root / "backup.sqlite3"
        manifest = store.backup(backup)
        tampered = json.loads(json.dumps(manifest))
        tampered["counts"]["admission_records"] += 1
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore.restore(
                backup, tampered, self.root / "restored.sqlite3"
            )

    def test_malformed_manifest_types_fail_closed_with_stable_error(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        backup = self.root / "malformed-manifest-backup.sqlite3"
        manifest = store.backup(backup)
        for field, malformed in (
            ("migration_checksums", []),
            ("counts", []),
            ("counts", {"admission_records": True}),
        ):
            candidate = json.loads(json.dumps(manifest))
            candidate[field] = malformed
            with self.subTest(field=field, malformed=malformed):
                with self.assertRaises(TelemetryAdmissionError) as caught:
                    SQLiteTelemetryAdmissionStore.restore(
                        backup,
                        candidate,
                        self.root / f"malformed-{field}-{type(malformed).__name__}.sqlite3",
                    )
                self.assertEqual(
                    caught.exception.reason_code, "TA_STORAGE_INTEGRITY_FAILURE"
                )

    def test_ta_r005_truncated_backup_is_rejected(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        backup = self.root / "backup.sqlite3"
        manifest = store.backup(backup)
        with backup.open("r+b") as handle:
            handle.truncate(max(1, backup.stat().st_size // 2))
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore.restore(
                backup, manifest, self.root / "restored.sqlite3"
            )

    def test_ta_r007_restore_then_retry_is_confirmed_duplicate(self) -> None:
        envelope = make_envelope()
        store = SQLiteTelemetryAdmissionStore(self.path)
        first = TelemetryAdmissionService(store).admit(
            envelope, admission_id="ta:admission:restore-retry"
        )
        backup = self.root / "backup.sqlite3"
        manifest = store.backup(backup)
        restored = SQLiteTelemetryAdmissionStore.restore(
            backup, manifest, self.root / "restored.sqlite3"
        )
        retry = TelemetryAdmissionService(restored).admit(
            envelope,
            admission_id=first.admission_id,
            claimed_intake_receipt_reference=first.intake_receipt_reference,
        )
        self.assertEqual(retry.state, "DUPLICATE_CONFIRMED")
        self.assertEqual(restored.counts()["admission_lifecycles"], 1)

    def test_restore_refuses_to_overwrite_existing_destination(self) -> None:
        store = SQLiteTelemetryAdmissionStore(self.path)
        TelemetryAdmissionService(store).admit(make_envelope())
        backup = self.root / "backup.sqlite3"
        manifest = store.backup(backup)
        destination = self.root / "already-exists.sqlite3"
        destination.touch(mode=0o600)
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore.restore(backup, manifest, destination)

    def test_ta_r010_prior_compatible_store_is_explicit_migrate_or_block(self) -> None:
        prior = create_prior_compatible_store(self.path)
        with self.assertRaises(TelemetryAdmissionError):
            prior.initialize()
        preflight = prior.migration_preflight()
        self.assertEqual(preflight["classification"], "COMPATIBLE_MIGRATION_REQUIRED")
        self.assertFalse(preflight["mutation_performed"])

    def test_backup_manifest_preserves_compatible_migration_lineage(self) -> None:
        prior = create_prior_compatible_store(self.path)
        prior.migrate_compatible(self.root / "prior-pre-migration.sqlite3")
        backup = self.root / "compatible-history-backup.sqlite3"
        manifest = prior.backup(backup)
        actual_history = SQLiteTelemetryAdmissionStore(backup).integrity_report()[
            "migration_checksums"
        ]
        self.assertEqual(manifest["migration_checksums"], actual_history)
        self.assertEqual(set(actual_history), {"0000", "0001-compat"})
        restored = SQLiteTelemetryAdmissionStore.restore(
            backup,
            manifest,
            self.root / "compatible-history-restored.sqlite3",
        )
        self.assertEqual(restored.integrity_report()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
