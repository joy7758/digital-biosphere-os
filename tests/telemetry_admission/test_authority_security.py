"""TA-N and TA-S authority, sensitive-data, and resource abuse cases."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dbos.telemetry_admission.models import TelemetryAdmissionError, ValidationDecision
from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from dbos.telemetry_admission.validator import TelemetryEnvelopeValidator
from fixtures import make_envelope


class AuthoritySecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="dbos-ta-security-")
        self.store = SQLiteTelemetryAdmissionStore(
            Path(self.temp.name) / "admission.sqlite3"
        )
        self.service = TelemetryAdmissionService(self.store)
        self.validator = TelemetryEnvelopeValidator()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _assert_injected_key_rejected(self, key: str, value: object) -> None:
        envelope = make_envelope()
        envelope[key] = value
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIsNone(decision.normalized_envelope)

    def test_ta_n001_entity_claim_is_rejected(self) -> None:
        self._assert_injected_key_rejected("entity_id", "fixture-entity")

    def test_ta_n002_permission_claim_is_rejected(self) -> None:
        self._assert_injected_key_rejected("permission", "GRANTED")

    def test_ta_n003_evidence_claim_is_rejected(self) -> None:
        self._assert_injected_key_rejected("evidence_status", "VALID")

    def test_ta_n004_fitness_claim_is_rejected(self) -> None:
        self._assert_injected_key_rejected("fitness", 1.0)

    def test_ta_n005_verified_claim_is_rejected(self) -> None:
        self._assert_injected_key_rejected("verified", True)

    def test_ta_n006_trace_id_cannot_be_observation_id(self) -> None:
        envelope = make_envelope()
        envelope["observation_id"] = envelope["context"]["trace_id"]
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_CONTEXT_INVALID", decision.reason_codes)

    def test_content_capture_full_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["content_capture_state"] = "FULL"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_CONTENT_CAPTURE_PROHIBITED", decision.reason_codes)

    def test_sensitive_reference_marker_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["producer_reference"] = "fixture:bearer-token"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SENSITIVE_KEY_DETECTED", decision.reason_codes)

    def test_sensitive_canary_is_not_reflected_or_persisted(self) -> None:
        canary = "fixture-sensitive-canary-value"
        envelope = make_envelope()
        envelope["prompt"] = canary
        result = self.service.admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertNotIn(canary, repr(result))
        for path in Path(self.temp.name).iterdir():
            if path.is_file():
                self.assertNotIn(canary.encode("utf-8"), path.read_bytes())

    def test_ta_s001_each_raw_content_family_is_rejected(self) -> None:
        for key in ("prompt", "response", "tool_arguments", "tool_results"):
            with self.subTest(key=key):
                envelope = make_envelope(
                    observation_id=f"ta:observation:raw-{key.replace('_', '-')}",
                    source_seed=f"raw-{key}",
                )
                envelope[key] = "synthetic-content"
                decision = self.validator.validate(envelope)
                self.assertEqual(decision.state, "REJECTED")
                self.assertIsNone(decision.normalized_envelope)

    def test_ta_s003_nested_depth_overflow_is_bounded(self) -> None:
        envelope = make_envelope()
        nested: dict[str, object] = {"value": "fixture"}
        for _ in range(10):
            nested = {"nested": nested}
        envelope["extra"] = nested
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SIZE_LIMIT_EXCEEDED", decision.reason_codes)

    def test_ta_s004_reference_and_list_limits_are_bounded(self) -> None:
        long_reference = make_envelope()
        long_reference["producer_reference"] = "x" * 129
        long_decision = self.validator.validate(long_reference)
        self.assertEqual(long_decision.state, "REJECTED")
        self.assertIn("TA_PROVENANCE_INCOMPLETE", long_decision.reason_codes)

        too_many = make_envelope()
        too_many["limitations"] = [f"fixture:limit:{index}" for index in range(33)]
        size_decision = self.validator.validate(too_many)
        self.assertEqual(size_decision.state, "REJECTED")
        self.assertIn("TA_SIZE_LIMIT_EXCEEDED", size_decision.reason_codes)

    def test_ta_s007_control_character_is_not_reflected(self) -> None:
        envelope = make_envelope()
        envelope["producer_reference"] = "fixture\nforged-log-line"
        result = self.service.admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertNotIn("forged-log-line", repr(result))

    def test_ta_s009_hidden_extras_are_not_serialized(self) -> None:
        class EnvelopeWithExtras(dict):
            extras = {"evidence_status": "VALID"}

        envelope = EnvelopeWithExtras(make_envelope())
        envelope["extra"] = envelope.extras
        result = self.service.admit(envelope)
        self.assertEqual(result.state, "REJECTED")
        self.assertNotIn("evidence_status", repr(result))

    def test_ta_s010_user_text_url_email_and_path_references_are_rejected(self) -> None:
        values = (
            "free form user text",
            "https://example.invalid/path?secret=value",
            "person@example.invalid",
            "/private/tmp/research.txt",
        )
        for value in values:
            with self.subTest(value=value):
                envelope = make_envelope()
                envelope["producer_reference"] = value
                decision = self.validator.validate(envelope)
                self.assertEqual(decision.state, "REJECTED")
                self.assertIsNone(decision.normalized_envelope)

    def test_ta_s011_exception_canary_is_not_reflected_or_persisted(self) -> None:
        canary = "exception-only-sensitive-canary"

        def fail(point: str) -> None:
            if point == "before_commit":
                raise RuntimeError(canary)

        path = Path(self.temp.name) / "exception-canary.sqlite3"
        store = SQLiteTelemetryAdmissionStore(path, fault_injector=fail)
        with self.assertRaises(TelemetryAdmissionError) as caught:
            TelemetryAdmissionService(store).admit(make_envelope())
        self.assertNotIn(canary, str(caught.exception))
        for artifact in Path(self.temp.name).iterdir():
            if artifact.is_file():
                self.assertNotIn(canary.encode(), artifact.read_bytes())

    def test_unknown_schema_url_performs_no_network_call(self) -> None:
        envelope = make_envelope()
        envelope["semantic_convention_schema_url"] = "http://127.0.0.1/schema"
        with patch(
            "socket.create_connection", side_effect=AssertionError("network")
        ) as call:
            decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "UNKNOWN")
        self.assertFalse(call.called)

    def test_symlink_store_path_is_rejected(self) -> None:
        target = Path(self.temp.name) / "target.sqlite3"
        target.touch(mode=0o600)
        link = Path(self.temp.name) / "linked.sqlite3"
        link.symlink_to(target)
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(link)

    def test_symlink_in_store_parent_chain_is_rejected(self) -> None:
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        link = Path(self.temp.name) / "linked-directory"
        link.symlink_to(outside, target_is_directory=True)
        nested = link / "nested"
        nested.mkdir()
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(nested / "store.sqlite3")

    def test_world_readable_existing_store_is_rejected(self) -> None:
        path = Path(self.temp.name) / "world.sqlite3"
        path.touch(mode=0o644)
        os.chmod(path, 0o644)
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(path)

    def test_hsr_pre_001_world_writable_direct_parent_is_rejected(self) -> None:
        parent = Path(self.temp.name) / "world-writable-parent"
        parent.mkdir(mode=0o700)
        os.chmod(parent, 0o777)
        try:
            with self.assertRaises(TelemetryAdmissionError) as caught:
                SQLiteTelemetryAdmissionStore(parent / "admission.sqlite3")
            self.assertEqual(caught.exception.reason_code, "TA_STORAGE_UNAVAILABLE")
        finally:
            os.chmod(parent, 0o700)

    def test_hsr_pre_002_generated_reference_is_revalidated_before_persistence(
        self,
    ) -> None:
        canary = "ta:token:secret-canary"
        path = Path(self.temp.name) / "generated-reference.sqlite3"
        store = SQLiteTelemetryAdmissionStore(
            path,
            id_factory=lambda _kind: canary,
        )

        with self.assertRaises(TelemetryAdmissionError) as caught:
            TelemetryAdmissionService(store).admit(make_envelope())

        self.assertEqual(caught.exception.reason_code, "TA_STORAGE_INTEGRITY_FAILURE")
        self.assertNotIn(canary, str(caught.exception))
        for artifact in Path(self.temp.name).iterdir():
            if artifact.is_file():
                self.assertNotIn(canary.encode(), artifact.read_bytes())

    def test_hsr_pre_002_generated_timestamp_is_revalidated_before_persistence(
        self,
    ) -> None:
        canary = "Bearer-secret-clock"
        path = Path(self.temp.name) / "generated-timestamp.sqlite3"
        store = SQLiteTelemetryAdmissionStore(path, clock=lambda: canary)

        with self.assertRaises(TelemetryAdmissionError) as caught:
            store.initialize()

        self.assertEqual(caught.exception.reason_code, "TA_STORAGE_INTEGRITY_FAILURE")
        self.assertNotIn(canary, str(caught.exception))
        for artifact in Path(self.temp.name).iterdir():
            if artifact.is_file():
                self.assertNotIn(canary.encode(), artifact.read_bytes())

    def test_hsr_pre_002_callback_exception_is_not_reflected_or_persisted(
        self,
    ) -> None:
        canary = "callback-exception-secret-canary"
        path = Path(self.temp.name) / "callback-exception.sqlite3"

        def fail(_kind: str) -> str:
            raise RuntimeError(canary)

        store = SQLiteTelemetryAdmissionStore(path, id_factory=fail)
        with self.assertRaises(TelemetryAdmissionError) as caught:
            TelemetryAdmissionService(store).admit(make_envelope())

        self.assertEqual(caught.exception.reason_code, "TA_STORAGE_INTEGRITY_FAILURE")
        self.assertNotIn(canary, str(caught.exception))
        for artifact in Path(self.temp.name).iterdir():
            if artifact.is_file():
                self.assertNotIn(canary.encode(), artifact.read_bytes())

    def test_non_regular_store_path_is_rejected(self) -> None:
        directory = Path(self.temp.name) / "directory.sqlite3"
        directory.mkdir(mode=0o700)
        with self.assertRaises(TelemetryAdmissionError):
            SQLiteTelemetryAdmissionStore(directory)

    def test_forged_accepted_decision_without_envelope_is_rejected(self) -> None:
        forged = ValidationDecision(
            state="ACCEPTED_AS_MATERIAL",
            reason_codes=(),
            limitations=(),
            normalized_envelope=None,
            safe_observation_reference=None,
            safe_source_digest=None,
        )
        with self.assertRaises(TelemetryAdmissionError) as caught:
            self.store.record_decision(forged)
        self.assertEqual(caught.exception.reason_code, "TA_SHAPE_INVALID")
        self.store.initialize()
        self.assertEqual(self.store.counts()["admission_lifecycles"], 0)

    def test_forged_normalized_decision_cannot_bypass_closed_schema(self) -> None:
        envelope = make_envelope()
        envelope["prompt"] = "must-not-persist"
        forged = ValidationDecision(
            state="ACCEPTED_AS_MATERIAL",
            reason_codes=(),
            limitations=(),
            normalized_envelope=envelope,
            safe_observation_reference=envelope["observation_id"],
            safe_source_digest=envelope["source_digest"],
        )
        with self.assertRaises(TelemetryAdmissionError) as caught:
            self.store.record_decision(forged)
        self.assertEqual(caught.exception.reason_code, "TA_SHAPE_INVALID")
        self.store.initialize()
        self.assertNotIn(b"must-not-persist", self.store.path.read_bytes())

    def test_item_counts_cannot_contradict_admission_state(self) -> None:
        with self.assertRaises(TelemetryAdmissionError):
            self.service.admit(
                make_envelope(), accepted_item_count=1, rejected_item_count=1
            )
        self.assertEqual(self.store.counts()["admission_lifecycles"], 0)

    def test_result_has_no_governance_effect_fields(self) -> None:
        result = self.service.admit(make_envelope()).as_dict()
        for prohibited in (
            "entity_id",
            "evidence_id",
            "permission",
            "verification",
            "fitness",
            "agent_id",
            "runtime_id",
        ):
            self.assertNotIn(prohibited, result)

    def test_append_only_triggers_reject_update_and_delete(self) -> None:
        result = self.service.admit(make_envelope())
        connection = sqlite3.connect(self.store.path)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "UPDATE admission_records SET state='REJECTED' WHERE admission_id=?",
                    (result.admission_id,),
                )
            connection.rollback()
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "DELETE FROM admission_records WHERE admission_id=?",
                    (result.admission_id,),
                )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
