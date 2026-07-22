"""TA-C schema and object conformance cases."""

from __future__ import annotations

import unittest

from dbos.telemetry_admission.contracts import ENVELOPE_FIELDS
from dbos.telemetry_admission.validator import TelemetryEnvelopeValidator
from fixtures import make_envelope


class ContractValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = TelemetryEnvelopeValidator()

    def test_ta_c001_minimum_trace_metadata_is_accepted_material(self) -> None:
        decision = self.validator.validate(make_envelope())
        self.assertEqual(decision.state, "ACCEPTED_AS_MATERIAL")
        self.assertEqual(decision.reason_codes, ())
        self.assertEqual(set(decision.normalized_envelope or {}), set(ENVELOPE_FIELDS))

    def test_ta_c002_metric_not_applicable_context_is_accepted(self) -> None:
        decision = self.validator.validate(
            make_envelope(
                signal_type="METRIC", observation_id="ta:observation:metric-001"
            )
        )
        self.assertEqual(decision.state, "ACCEPTED_AS_MATERIAL")

    def test_ta_c003_log_metadata_has_no_body(self) -> None:
        decision = self.validator.validate(
            make_envelope(signal_type="LOG", observation_id="ta:observation:log-001")
        )
        self.assertEqual(decision.state, "ACCEPTED_AS_MATERIAL")
        self.assertNotIn("body", decision.normalized_envelope or {})

    def test_ta_c004_profile_signal_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["signal_type"] = "PROFILE"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SIGNAL_UNSUPPORTED", decision.reason_codes)

    def test_ta_c005_unknown_top_level_field_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["extra"] = "fixture"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", decision.reason_codes)

    def test_ta_c005_unknown_nested_field_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["resource"]["service_name"] = "fixture-service"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", decision.reason_codes)

    def test_ta_c006_missing_resource_has_stable_reason(self) -> None:
        envelope = make_envelope()
        envelope.pop("resource")
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_RESOURCE_MISSING", decision.reason_codes)

    def test_ta_c007_missing_scope_has_stable_reason(self) -> None:
        envelope = make_envelope()
        envelope.pop("instrumentation_scope")
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_INSTRUMENTATION_SCOPE_MISSING", decision.reason_codes)

    def test_ta_c008_unsupported_profile_fails_closed(self) -> None:
        envelope = make_envelope()
        envelope["profile_id"] = "future-profile"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_PROFILE_UNSUPPORTED", decision.reason_codes)

    def test_ta_c009_unknown_schema_url_remains_unknown(self) -> None:
        envelope = make_envelope()
        envelope["semantic_convention_schema_url"] = "UNKNOWN"
        envelope["resource"]["schema_url"] = "UNKNOWN"
        envelope["instrumentation_scope"]["schema_url"] = "UNKNOWN"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "UNKNOWN")
        self.assertIn("TA_SCHEMA_URL_UNKNOWN", decision.reason_codes)

    def test_ta_c010_unpinned_genai_mapping_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["genai_semconv_ref"] = "latest"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_GENAI_SEMCONV_UNPINNED", decision.reason_codes)

    def test_ta_c011_naive_timestamp_is_rejected(self) -> None:
        envelope = make_envelope()
        envelope["observed_at"] = "2026-07-22T04:00:00"
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", decision.reason_codes)

    def test_ta_c012_duplicate_limitations_are_rejected(self) -> None:
        envelope = make_envelope()
        envelope["limitations"] = ["fixture:limitation", "fixture:limitation"]
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "REJECTED")
        self.assertIn("TA_SHAPE_INVALID", decision.reason_codes)

    def test_partial_delivery_is_not_complete(self) -> None:
        decision = self.validator.validate(make_envelope(delivery_state="PARTIAL"))
        self.assertEqual(decision.state, "PARTIAL")
        self.assertIn("TA_PARTIAL_INPUT", decision.reason_codes)

    def test_sampling_loss_is_not_complete(self) -> None:
        envelope = make_envelope()
        envelope["sampling_state"]["known_loss"] = True
        decision = self.validator.validate(envelope)
        self.assertEqual(decision.state, "PARTIAL")
        self.assertIn("TA_SAMPLING_LIMITATION", decision.reason_codes)


if __name__ == "__main__":
    unittest.main()
