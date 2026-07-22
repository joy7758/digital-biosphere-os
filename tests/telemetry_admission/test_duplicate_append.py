"""TA-D duplicate, context, delivery, and append-only lifecycle cases."""

from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


class DuplicateAppendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-duplicate-")
        self.store = SQLiteTelemetryAdmissionStore(
            Path(self.temp.name) / "admission.sqlite3"
        )
        self.service = TelemetryAdmissionService(self.store)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_original_admission_has_strict_three_record_chain(self) -> None:
        result = self.service.admit(
            make_envelope(), admission_id="ta:admission:original"
        )
        records = self.store.get_records(result.admission_id)
        self.assertEqual(
            [row["state"] for row in records],
            ["RECEIVED", "VALIDATING", "ACCEPTED_AS_MATERIAL"],
        )
        self.assertEqual([row["sequence"] for row in records], [1, 2, 3])
        self.assertIsNone(records[0]["previous_record_reference"])
        self.assertEqual(
            records[2]["previous_record_reference"], records[1]["admission_record_id"]
        )

    def test_ta_d001_valid_trace_context_is_correlation_only(self) -> None:
        envelope = make_envelope()
        result = self.service.admit(envelope)
        stored = self.store.get_envelope(result.observation_reference)
        self.assertEqual(stored["context"], envelope["context"])
        self.assertNotIn("authority", result.as_dict())

    def test_ta_d002_all_zero_context_is_rejected_without_parent_inference(
        self,
    ) -> None:
        envelope = make_envelope()
        envelope["context"] = {
            "trace_id": "0" * 32,
            "span_id": "0" * 16,
            "trace_flags": "00",
            "parent_state": "UNKNOWN",
        }
        result = self.service.admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertIn("TA_CONTEXT_INVALID", result.reason_codes)
        self.assertIsNone(self.store.get_envelope(result.observation_reference))

    def test_ta_d003_committed_receipt_replay_is_confirmed(self) -> None:
        envelope = make_envelope()
        first = self.service.admit(envelope, admission_id="ta:admission:replay")
        replay = self.service.admit(
            envelope,
            admission_id=first.admission_id,
            claimed_intake_receipt_reference=first.intake_receipt_reference,
        )
        self.assertEqual(replay.state, "DUPLICATE_CONFIRMED")
        self.assertEqual(replay.sequence, 4)
        self.assertEqual(len(self.store.get_records(first.admission_id)), 4)
        self.assertEqual(self.store.counts()["admission_lifecycles"], 1)

    def test_ta_d004_same_receipt_different_digest_is_rejected(self) -> None:
        original = make_envelope()
        first = self.service.admit(
            original, admission_id="ta:admission:conflict-original"
        )
        conflicting = make_envelope(
            observation_id="ta:observation:conflict",
            source_seed="different-source",
        )
        result = self.service.admit(
            conflicting,
            admission_id=first.admission_id,
            claimed_intake_receipt_reference=first.intake_receipt_reference,
        )
        self.assertEqual(result.state, "REJECTED")
        self.assertIn("TA_IDEMPOTENCY_CONFLICT", result.reason_codes)
        self.assertEqual(self.store.counts()["admission_lifecycles"], 2)

    def test_ta_d005_same_fingerprint_is_suspected_and_retained(self) -> None:
        first_envelope = make_envelope(idempotency_reference="UNKNOWN")
        second_envelope = make_envelope(
            observation_id="ta:observation:second",
            idempotency_reference="UNKNOWN",
        )
        first = self.service.admit(first_envelope)
        second = self.service.admit(second_envelope)
        self.assertEqual(first.state, "ACCEPTED_AS_MATERIAL")
        self.assertEqual(second.state, "DUPLICATE_SUSPECTED")
        self.assertEqual(self.store.counts()["observation_envelopes"], 2)
        self.assertEqual(self.store.counts()["admission_lifecycles"], 2)

    def test_same_untrusted_hint_is_suspected_not_confirmed(self) -> None:
        first = make_envelope(signal_reference="fixture:signal:first")
        second = make_envelope(
            observation_id="ta:observation:hint-second",
            source_seed="source-second",
            signal_reference="fixture:signal:second",
            idempotency_reference=first["idempotency_reference"],
        )
        self.service.admit(first)
        result = self.service.admit(second)
        self.assertEqual(result.state, "DUPLICATE_SUSPECTED")
        self.assertNotIn("TA_DUPLICATE_CONFIRMED", result.reason_codes)

    def test_same_trace_with_different_material_is_not_a_duplicate(self) -> None:
        first = make_envelope(idempotency_reference="fixture:attempt:first")
        second = make_envelope(
            observation_id="ta:observation:same-trace-second",
            source_seed="second-material",
            signal_reference="fixture:signal:second",
            idempotency_reference="fixture:attempt:second",
        )
        second["context"] = dict(first["context"])
        self.service.admit(first)
        result = self.service.admit(second)
        self.assertEqual(result.state, "ACCEPTED_AS_MATERIAL")

    def test_missing_claimed_receipt_is_rejected_and_retained(self) -> None:
        result = self.service.admit(
            make_envelope(),
            claimed_intake_receipt_reference="ta:receipt:not-committed",
        )
        self.assertEqual(result.state, "REJECTED")
        self.assertIn("TA_INTAKE_RECEIPT_INVALID", result.reason_codes)
        self.assertEqual(self.store.counts()["admission_lifecycles"], 1)

    def test_ta_d007_partial_counts_are_preserved_without_retry_invention(self) -> None:
        result = self.service.admit(
            make_envelope(delivery_state="PARTIAL"),
            accepted_item_count=7,
            rejected_item_count=2,
        )
        self.assertEqual(result.state, "PARTIAL")
        self.assertEqual(
            (result.accepted_item_count, result.rejected_item_count), (7, 2)
        )
        self.assertNotIn("retry", result.as_dict())

    def test_ta_d008_dropped_and_unknown_are_never_complete(self) -> None:
        dropped = self.service.admit(
            make_envelope(
                observation_id="ta:observation:dropped",
                source_seed="dropped",
                delivery_state="DROPPED",
            )
        )
        unknown = self.service.admit(
            make_envelope(
                observation_id="ta:observation:unknown",
                source_seed="unknown",
                delivery_state="UNKNOWN",
            )
        )
        self.assertEqual(dropped.state, "PARTIAL")
        self.assertEqual(unknown.state, "UNKNOWN")

    def test_ta_d009_clock_reversal_keeps_sequence_canonical(self) -> None:
        start = datetime(2026, 7, 22, 5, 0, tzinfo=UTC)
        counter = 0

        def reverse_clock() -> str:
            nonlocal counter
            counter += 1
            return (start - timedelta(seconds=counter)).isoformat()

        path = Path(self.temp.name) / "reverse-clock.sqlite3"
        store = SQLiteTelemetryAdmissionStore(path, clock=reverse_clock)
        envelope = make_envelope(observation_id="ta:observation:reverse-clock")
        envelope["observed_at"] = "2026-07-22T06:00:00Z"
        envelope["received_at"] = "2026-07-22T05:00:00Z"
        result = TelemetryAdmissionService(store).admit(envelope)
        self.assertEqual(result.state, "PARTIAL")
        self.assertIn("TA_CLOCK_UNCERTAIN", result.reason_codes)
        records = store.get_records(result.admission_id)
        self.assertEqual([record["sequence"] for record in records], [1, 2, 3])

    def test_ta_d010_fabricated_receipt_is_not_accepted(self) -> None:
        result = self.service.admit(
            make_envelope(),
            claimed_intake_receipt_reference="ta:receipt:producer-fabricated",
        )
        self.assertEqual(result.state, "REJECTED")
        self.assertIn("TA_INTAKE_RECEIPT_INVALID", result.reason_codes)

    def test_ta_d011_external_fingerprint_version_is_closed_shape_rejected(
        self,
    ) -> None:
        envelope = make_envelope()
        envelope["fingerprint_version"] = "future-fingerprint-policy"
        result = self.service.admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", result.reason_codes)

    def test_ta_d012_identical_metadata_remains_suspected_and_both_retained(
        self,
    ) -> None:
        first = make_envelope(idempotency_reference="UNKNOWN")
        second = make_envelope(
            observation_id="ta:observation:legitimate-identical",
            idempotency_reference="UNKNOWN",
        )
        self.service.admit(first)
        result = self.service.admit(second)
        self.assertEqual(result.state, "DUPLICATE_SUSPECTED")
        self.assertIn(
            "TA_FINGERPRINT_COLLISION_OR_LEGITIMATE_DUPLICATE",
            result.reason_codes,
        )
        self.assertEqual(self.store.counts()["observation_envelopes"], 2)

    def test_32_concurrent_replays_are_serialized_and_retained(self) -> None:
        envelope = make_envelope()
        original = self.service.admit(envelope, admission_id="ta:admission:race")

        def replay(_: int) -> str:
            service = TelemetryAdmissionService(
                SQLiteTelemetryAdmissionStore(self.store.path)
            )
            return service.admit(
                envelope,
                admission_id=original.admission_id,
                claimed_intake_receipt_reference=original.intake_receipt_reference,
            ).state

        with ThreadPoolExecutor(max_workers=8) as pool:
            states = list(pool.map(replay, range(32)))
        self.assertEqual(states, ["DUPLICATE_CONFIRMED"] * 32)
        records = self.store.get_records(original.admission_id)
        self.assertEqual([row["sequence"] for row in records], list(range(1, 36)))
        self.assertEqual(self.store.integrity_report()["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
