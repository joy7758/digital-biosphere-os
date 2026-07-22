"""Self-observation, schema packaging, and absence-boundary tests."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker

from dbos.telemetry_admission.contracts import (
    ADMISSION_RECORD_FIELDS,
    ENVELOPE_FIELDS,
    REASON_CODE_SET,
)
from dbos.telemetry_admission.metrics import AdmissionMetrics
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


ROOT = Path(__file__).resolve().parents[2]


class MetricsSchemaBoundaryTests(unittest.TestCase):
    def test_both_new_schemas_are_draft_2020_12_meta_valid(self) -> None:
        for name in (
            "telemetry-observation-envelope-schema.yaml",
            "telemetry-admission-record-schema.yaml",
        ):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)

    def test_schema_fields_and_reason_codes_match_runtime_contract(self) -> None:
        envelope_schema = json.loads(
            (ROOT / "schemas" / "telemetry-observation-envelope-schema.yaml").read_text(
                encoding="utf-8"
            )
        )
        record_schema = json.loads(
            (ROOT / "schemas" / "telemetry-admission-record-schema.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(set(envelope_schema["required"]), set(ENVELOPE_FIELDS))
        self.assertEqual(set(envelope_schema["properties"]), set(ENVELOPE_FIELDS))
        self.assertEqual(set(record_schema["required"]), set(ADMISSION_RECORD_FIELDS))
        self.assertEqual(set(record_schema["properties"]), set(ADMISSION_RECORD_FIELDS))
        self.assertEqual(
            set(record_schema["$defs"]["reasonCode"]["enum"]), REASON_CODE_SET
        )

    def test_valid_fixture_and_committed_record_pass_machine_schemas(self) -> None:
        envelope_schema = json.loads(
            (ROOT / "schemas" / "telemetry-observation-envelope-schema.yaml").read_text(
                encoding="utf-8"
            )
        )
        record_schema = json.loads(
            (ROOT / "schemas" / "telemetry-admission-record-schema.yaml").read_text(
                encoding="utf-8"
            )
        )
        envelope = make_envelope()
        Draft202012Validator(envelope_schema, format_checker=FormatChecker()).validate(
            envelope
        )
        with tempfile.TemporaryDirectory(prefix="dbos-ta-schema-record-") as temp:
            store = SQLiteTelemetryAdmissionStore(Path(temp) / "store.sqlite3")
            result = TelemetryAdmissionService(store).admit(envelope)
            record = store.get_records(result.admission_id)[-1]
        Draft202012Validator(record_schema, format_checker=FormatChecker()).validate(
            record
        )

    def test_integrity_report_binds_required_sqlite_pragmas(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-ta-pragma-") as temp:
            store = SQLiteTelemetryAdmissionStore(Path(temp) / "store.sqlite3")
            TelemetryAdmissionService(store).admit(make_envelope())
            report = store.integrity_report()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            report["store_configuration"],
            {
                "journal_mode": "wal",
                "synchronous": 2,
                "foreign_keys": 1,
                "busy_timeout_ms": 5000,
            },
        )

    def test_integrity_report_streams_admission_records_without_fetchall(self) -> None:
        class StreamingCursor:
            def __init__(self, cursor: sqlite3.Cursor) -> None:
                self._cursor = cursor

            def __iter__(self):
                return iter(self._cursor)

            def fetchall(self):
                raise AssertionError("admission records must be streamed")

            def __getattr__(self, name: str):
                return getattr(self._cursor, name)

        class ConnectionProxy:
            def __init__(self, connection: sqlite3.Connection) -> None:
                self._connection = connection

            def execute(self, sql: str, *args: object):
                cursor = self._connection.execute(sql, *args)
                if "SELECT * FROM admission_records ORDER BY" in sql:
                    return StreamingCursor(cursor)
                return cursor

            def __getattr__(self, name: str):
                return getattr(self._connection, name)

        with tempfile.TemporaryDirectory(prefix="dbos-ta-integrity-stream-") as temp:
            store = SQLiteTelemetryAdmissionStore(Path(temp) / "store.sqlite3")
            service = TelemetryAdmissionService(store)
            for index in range(3):
                service.admit(
                    make_envelope(
                        observation_id=f"ta:observation:stream-{index}",
                        source_seed=f"stream-source-{index}",
                        signal_reference=f"fixture:signal:stream-{index}",
                        idempotency_reference=f"fixture:attempt:stream-{index}",
                    )
                )
            original_connect = store._connect
            with patch.object(
                store,
                "_connect",
                side_effect=lambda: ConnectionProxy(original_connect()),
            ):
                report = store.integrity_report()
        self.assertEqual(report["status"], "PASS")

    def test_metrics_have_only_bounded_dimensions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbos-ta-metrics-") as temp:
            metrics = AdmissionMetrics()
            service = TelemetryAdmissionService(
                SQLiteTelemetryAdmissionStore(Path(temp) / "store.sqlite3"),
                metrics=metrics,
            )
            service.admit(make_envelope())
            serialized = json.dumps(metrics.snapshot(), sort_keys=True)
            self.assertNotIn("ta:observation", serialized)
            self.assertNotIn("trace_id", serialized)
            self.assertIn("accepted_as_material|TRACE|0.1.0", serialized)

    def test_duration_observation_bookkeeping_has_constant_memory(self) -> None:
        metrics = AdmissionMetrics()
        for _ in range(10_000):
            metrics.observe(
                outcome="accepted_as_material",
                signal_type="TRACE",
                schema_version="0.1.0",
                accepted_items=1,
                rejected_items=0,
                duration_seconds=0.001,
            )
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["duration_observation_count"], 10_000)
        self.assertNotIn("_durations", vars(metrics))

    def test_metrics_sink_failure_does_not_change_committed_result(self) -> None:
        def fail_sink(name: str, labels: object, value: float) -> None:
            raise RuntimeError("synthetic-sink-failure")

        with tempfile.TemporaryDirectory(prefix="dbos-ta-metrics-failure-") as temp:
            metrics = AdmissionMetrics(sink=fail_sink)
            service = TelemetryAdmissionService(
                SQLiteTelemetryAdmissionStore(Path(temp) / "store.sqlite3"),
                metrics=metrics,
            )
            result = service.admit(make_envelope())
            self.assertTrue(result.committed)
            self.assertEqual(result.state, "ACCEPTED_AS_MATERIAL")
            self.assertEqual(
                metrics.snapshot()["diagnostics"], {"TA_METRICS_SINK_FAILURE": 1}
            )

    def test_source_has_no_listener_collector_saee_or_governed_store_import(
        self,
    ) -> None:
        package = ROOT / "dbos" / "telemetry_admission"
        source = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(package.glob("*.py"))
        )
        for forbidden in (
            "import socket",
            "http.server",
            "grpc.server",
            "opentelemetry.sdk",
            "from evidence",
            "from entity_support",
            "from evolution",
            "import saee",
        ):
            self.assertNotIn(forbidden, source)

    def test_public_dbos_facade_does_not_auto_export_admission_surface(self) -> None:
        import dbos

        self.assertNotIn("TelemetryAdmissionService", dbos.__all__)
        self.assertFalse(hasattr(dbos, "TelemetryAdmissionService"))

    def test_ta_n007_no_lifecycle_activation_callable_exists(self) -> None:
        from dbos.telemetry_admission.service import TelemetryAdmissionService

        for prohibited in ("activate", "grant", "execute", "promote_to_evidence"):
            self.assertFalse(hasattr(TelemetryAdmissionService, prohibited))


if __name__ == "__main__":
    unittest.main()
