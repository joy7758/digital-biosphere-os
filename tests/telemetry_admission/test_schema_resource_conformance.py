"""Execute the exact 36 DQ-018/PR-G2 Schema/Resource provenance cases."""

from __future__ import annotations

import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path

from dbos.telemetry_admission.contracts import (
    OTEL_SCHEMA_ARTIFACT_DIGEST,
    SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST,
    SCHEMA_RESOURCE_PR_G2_CASE_COUNT,
    SEMANTIC_CONVENTION_SCHEMA_URL,
)
from dbos.telemetry_admission.provenance import (
    DataGovernanceBinding,
    DetectorBinding,
    ProvenanceError,
    SchemaResourceProvenanceValidator,
    TransformerBinding,
)


ROOT = Path(__file__).resolve().parents[2]
CATALOG = (
    ROOT
    / "dbos"
    / "telemetry_admission"
    / "profiles"
    / "opentelemetry-schema-resource-conformance-cases.v0.1.json"
)
SCHEMA_OLD = "https://opentelemetry.io/schemas/1.36.0"
SCHEMA_TARGET = SEMANTIC_CONVENTION_SCHEMA_URL


def _digest(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _catalog() -> dict[str, object]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def _required_case_ids() -> frozenset[str]:
    return frozenset(
        case["case_id"] for case in _catalog()["cases"] if "PR-G2" in case["gate_refs"]
    )


def _transformer(valid: bool = True) -> TransformerBinding:
    return TransformerBinding(
        transformer_id="dbos.telemetry_admission.schema_transformer",
        transformer_version="0.1.0",
        artifact_digest=_digest("transformer") if valid else "UNKNOWN",
        environment_digest=_digest("python-3.12"),
    )


def _detector(
    name: str,
    order: int,
    source_class: str,
) -> DetectorBinding:
    return DetectorBinding(
        detector_name=name,
        detector_version="0.1.0",
        detector_artifact_digest=_digest(f"artifact:{name}"),
        detector_config_digest=_digest(f"config:{name}"),
        detector_order=order,
        source_class=source_class,
        source_reference=f"detector:{name}",
    )


def _governance(*, valid: bool = True) -> DataGovernanceBinding:
    return DataGovernanceBinding(
        tenant_scope_reference="tenant:synthetic-a",
        purpose_reference="purpose:conformance",
        retention_policy_reference="retention:bounded" if valid else "",
        access_policy_reference="access:isolated",
        encryption_policy_reference="encryption:test-key-ref",
        classification_status="PASS",
        redaction_status="PASS",
        isolation_status="PASS",
        retention_status="PASS" if valid else "NOT_ASSESSED",
    )


class SchemaResourceConformanceTests(unittest.TestCase):
    """Each generated method is bound one-to-one to a frozen DBA case ID."""

    maxDiff = None

    def test_metric_scoped_schema_operation_requires_exact_metric_context(self) -> None:
        validator = SchemaResourceProvenanceValidator()
        blocked = validator.transform_attributes(
            {"system.device": "eth0"},
            source_schema_url="https://opentelemetry.io/schemas/1.28.0",
            binding=_transformer(),
            signal_type="METRIC",
        )
        self.assertEqual(blocked.status, "BLOCKED")
        self.assertIn("OSR_TRANSFORMATION_UNSUPPORTED", blocked.reason_codes)
        transformed = validator.transform_attributes(
            {"system.device": "eth0"},
            source_schema_url="https://opentelemetry.io/schemas/1.28.0",
            binding=_transformer(),
            signal_type="METRIC",
            metric_name="system.network.io",
        )
        self.assertEqual(transformed.status, "TRANSFORMED")
        self.assertIn("network.interface.name", transformed.output_field_digests)

    def test_environment_percent_decoding_is_strict_and_atomic(self) -> None:
        validator = SchemaResourceProvenanceValidator()
        parsed = validator.parse_resource_environment(
            "service.name=service-a,service.namespace=%GG"
        )
        self.assertEqual(parsed.status, "DISCARDED")
        self.assertEqual(dict(parsed.attributes), {})

    def test_user_resource_precedence_survives_later_environment_merge(self) -> None:
        validator = SchemaResourceProvenanceValidator()
        result = validator.merge_resources(
            {"service.name": "user-value"},
            {"service.name": "environment-value"},
            old_schema_url=SCHEMA_TARGET,
            updating_schema_url=SCHEMA_TARGET,
            old_detector=_detector("user", 0, "USER_RESOURCE"),
            updating_detector=_detector("environment", 1, "ENVIRONMENT"),
        )
        self.assertEqual(result.status, "MERGED")
        self.assertEqual(
            result.attribute_source_classes["service.name"], "USER_RESOURCE"
        )
        self.assertFalse(any(result.effects.values()))

    def test_invalid_entity_source_reference_is_not_reflected(self) -> None:
        validator = SchemaResourceProvenanceValidator()
        record = validator.quarantine_otel_entities(
            "service:service.instance.id=node-1",
            source_reference="secret value with spaces",
            schema_url=SCHEMA_TARGET,
            governance=_governance(),
        )
        self.assertEqual(record.source_reference, "UNKNOWN")
        self.assertIn("OSR_ENTITY_SOURCE_REFERENCE_MISSING", record.diagnostic_codes)
        self.assertNotIn("secret value with spaces", repr(record))

    def run_case(self, case_id: str) -> None:
        validator = SchemaResourceProvenanceValidator()

        if case_id == "OSR-CF-SRC-001":
            info = validator.artifact_info()
            self.assertEqual(info.digest, OTEL_SCHEMA_ARTIFACT_DIGEST)
            self.assertEqual(info.schema_url, SCHEMA_TARGET)
            self.assertFalse(info.runtime_network_fetch_enabled)
            self.assertGreater(info.version_count, 1)
        elif case_id == "OSR-CF-SRC-002":
            result = validator.resolve_schema_precedence(
                "https://opentelemetry.io/schemas/latest", None
            )
            self.assertEqual(result.status, "BLOCKED")
            self.assertIsNone(result.effective_schema_url)
            self.assertFalse(any(result.effects.values()))
        elif case_id == "OSR-CF-SRC-004":
            with self.assertRaisesRegex(
                ProvenanceError, "TA_REFERENCE_DIGEST_MISMATCH"
            ):
                SchemaResourceProvenanceValidator(
                    expected_schema_digest=f"sha256:{'0' * 64}"
                )
        elif case_id == "OSR-CF-PRE-001":
            result = validator.resolve_schema_precedence(
                "https://opentelemetry.io/schemas/1.42.0", SCHEMA_TARGET
            )
            self.assertEqual(result.status, "RESOLVED")
            self.assertEqual(result.effective_schema_url, SCHEMA_TARGET)
            self.assertIn("SCOPE", result.precedence_reason)
            self.assertEqual(
                result.resource_schema_url_original,
                "https://opentelemetry.io/schemas/1.42.0",
            )
        elif case_id == "OSR-CF-PRE-002":
            result = validator.resolve_schema_precedence(SCHEMA_TARGET, "")
            self.assertEqual(result.status, "RESOLVED")
            self.assertEqual(result.effective_schema_url, SCHEMA_TARGET)
            self.assertEqual(result.scope_schema_url_original, "")
        elif case_id == "OSR-CF-PRE-003":
            result = validator.resolve_schema_precedence("", None)
            self.assertEqual(result.status, "UNKNOWN")
            self.assertIsNone(result.effective_schema_url)
            self.assertIn("OSR_SCHEMA_URL_UNKNOWN", result.reason_codes)
        elif case_id == "OSR-CF-PRE-004":
            result = validator.resolve_schema_precedence(
                SCHEMA_TARGET, "https://example.invalid/schema/1.43.0"
            )
            self.assertEqual(result.status, "BLOCKED")
            self.assertIsNone(result.effective_schema_url)
            self.assertFalse(any(result.effects.values()))
        elif case_id.startswith("OSR-CF-TRN-"):
            original = {"gen_ai.system": "provider-a"}
            if case_id == "OSR-CF-TRN-001":
                result = validator.transform_attributes(
                    original,
                    source_schema_url=SCHEMA_OLD,
                    binding=_transformer(),
                )
                self.assertEqual(result.status, "TRANSFORMED")
                self.assertIn("gen_ai.provider.name", result.output_field_digests)
                self.assertEqual(len(result.operations_applied), 1)
            elif case_id == "OSR-CF-TRN-002":
                result = validator.transform_attributes(
                    {"service.name": "service-a"},
                    source_schema_url=SCHEMA_TARGET,
                    target_schema_url=SCHEMA_OLD,
                    binding=_transformer(),
                )
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn(
                    "OSR_BREAKING_OR_REVERSE_TRANSFORM_BLOCKED", result.reason_codes
                )
            elif case_id == "OSR-CF-TRN-003":
                snapshot = deepcopy(original)
                result = validator.transform_attributes(
                    original,
                    source_schema_url=SCHEMA_OLD,
                    binding=_transformer(),
                )
                self.assertEqual(original, snapshot)
                self.assertTrue(
                    result.transformation_reference.startswith("ta:transform:")
                )
                self.assertNotEqual(
                    result.transformation_reference, result.input_projection_digest
                )
            elif case_id == "OSR-CF-TRN-004":
                result = validator.transform_attributes(
                    original,
                    source_schema_url=SCHEMA_OLD,
                    binding=_transformer(valid=False),
                )
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn("OSR_TRANSFORMER_BINDING_INCOMPLETE", result.reason_codes)
            elif case_id == "OSR-CF-TRN-005":
                result = validator.transform_attributes(
                    original,
                    source_schema_url=SCHEMA_OLD,
                    binding=_transformer(),
                    requested_operation_types=("delete_attributes",),
                )
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn(
                    "OSR_TRANSFORMATION_TYPE_UNSUPPORTED", result.reason_codes
                )
            else:
                result = validator.transform_attributes(
                    {"dbos.permission": "GRANTED"},
                    source_schema_url=SCHEMA_OLD,
                    binding=_transformer(),
                )
                self.assertEqual(result.status, "BLOCKED")
                self.assertIn("OSR_AUTHORITY_FIELD_REJECTED", result.reason_codes)
            self.assertFalse(any(result.effects.values()))
        elif case_id.startswith("OSR-CF-RES-"):
            old = _detector("old", 0, "SDK_DEFAULT")
            updating = _detector("updating", 1, "USER_RESOURCE")
            if case_id == "OSR-CF-RES-001":
                result = validator.merge_resources(
                    {"service.name": "old"},
                    {"service.name": "new"},
                    old_schema_url=SCHEMA_TARGET,
                    updating_schema_url=SCHEMA_TARGET,
                    old_detector=old,
                    updating_detector=updating,
                )
                self.assertEqual(result.status, "MERGED")
                self.assertEqual(result.schema_url, SCHEMA_TARGET)
                self.assertEqual(
                    result.attribute_source_classes["service.name"], "USER_RESOURCE"
                )
            elif case_id == "OSR-CF-RES-002":
                result = validator.merge_resources(
                    {"service.name": "old"},
                    {"service.version": "1"},
                    old_schema_url="",
                    updating_schema_url=SCHEMA_TARGET,
                    old_detector=old,
                    updating_detector=updating,
                )
                self.assertEqual(result.status, "MERGED")
                self.assertEqual(result.schema_url, SCHEMA_TARGET)
            elif case_id == "OSR-CF-RES-003":
                result = validator.merge_resources(
                    {"service.name": "old"},
                    {"service.version": "1"},
                    old_schema_url=SCHEMA_TARGET,
                    updating_schema_url="",
                    old_detector=old,
                    updating_detector=updating,
                )
                self.assertEqual(result.status, "MERGED")
                self.assertEqual(result.schema_url, SCHEMA_TARGET)
            elif case_id == "OSR-CF-RES-004":
                result = validator.merge_resources(
                    {},
                    {},
                    old_schema_url=SCHEMA_TARGET,
                    updating_schema_url="https://opentelemetry.io/schemas/1.42.0",
                    old_detector=old,
                    updating_detector=updating,
                )
                self.assertEqual(result.status, "REJECTED")
                self.assertIn("OSR_RESOURCE_SCHEMA_CONFLICT", result.reason_codes)
            elif case_id == "OSR-CF-RES-005":
                parsed = validator.parse_resource_environment(
                    "service.name=valid,malformed-segment"
                )
                self.assertEqual(parsed.status, "DISCARDED")
                self.assertEqual(dict(parsed.attributes), {})
            elif case_id == "OSR-CF-RES-006":
                result = validator.merge_resources(
                    {"service.name": "environment"},
                    {"service.name": "user"},
                    old_schema_url=SCHEMA_TARGET,
                    updating_schema_url=SCHEMA_TARGET,
                    old_detector=_detector("env", 0, "ENVIRONMENT"),
                    updating_detector=updating,
                )
                self.assertEqual(result.status, "MERGED")
                self.assertEqual(
                    result.attribute_source_classes["service.name"], "USER_RESOURCE"
                )
                self.assertFalse(any(result.effects.values()))
            else:  # pragma: no cover - not part of current PR-G2 subset
                self.fail(f"unexpected PR-G2 resource case: {case_id}")
        elif case_id.startswith("OSR-CF-ENT-"):
            values = {
                "OSR-CF-ENT-001": "service:service.instance.id=node-1",
                "OSR-CF-ENT-002": "service:entity_id=forbidden",
                "OSR-CF-ENT-003": "service:service.instance.id=node-1",
                "OSR-CF-ENT-004": "service:service.instance.id=node-1;malformed",
                "OSR-CF-ENT-005": (
                    "service:service.instance.id=one,service.instance.id=two"
                ),
                "OSR-CF-ENT-006": "service:service.instance.id=node-1",
                "OSR-CF-ENT-007": "service:service.instance.id=node-1",
                "OSR-CF-ENT-008": ("service:service.instance.id=node-1,host.id=host-1"),
            }
            record = validator.quarantine_otel_entities(
                values[case_id],
                source_reference="environment:OTEL_ENTITIES",
                schema_url=SCHEMA_TARGET,
                governance=_governance(),
            )
            if case_id == "OSR-CF-ENT-002":
                self.assertEqual(record.skipped_segment_count, 1)
            elif case_id == "OSR-CF-ENT-004":
                self.assertIn("OSR_ENTITY_PARTIAL_PARSE", record.diagnostic_codes)
            elif case_id == "OSR-CF-ENT-005":
                self.assertEqual(record.duplicate_count, 1)
                self.assertIn(
                    "OSR_ENTITY_DUPLICATE_LAST_OCCURRENCE_OBSERVED",
                    record.diagnostic_codes,
                )
            elif case_id == "OSR-CF-ENT-006":
                self.assertFalse(
                    validator.entity_merge_allowed(
                        SCHEMA_TARGET,
                        "https://opentelemetry.io/schemas/1.42.0",
                    )
                )
            elif case_id == "OSR-CF-ENT-007":
                self.assertTrue(
                    validator.entity_merge_allowed(SCHEMA_TARGET, SCHEMA_TARGET)
                )
            self.assertEqual(record.stability, "DEVELOPMENT")
            self.assertFalse(record.trusted_projection_created)
            self.assertFalse(any(record.effects.values()))
        elif case_id.startswith("OSR-CF-DATA-"):
            if case_id in {"OSR-CF-DATA-001", "OSR-CF-DATA-002"}:
                record = validator.quarantine_otel_entities(
                    "service:service.instance.id=secret-low-entropy",
                    source_reference="environment:OTEL_ENTITIES",
                    schema_url=SCHEMA_TARGET,
                    governance=_governance(valid=False),
                )
                self.assertEqual(record.status, "BLOCKED")
                self.assertIsNone(record.data_governance_binding_digest)
            elif case_id == "OSR-CF-DATA-004":
                record = validator.quarantine_otel_entities(
                    "service:entity_id=forbidden",
                    source_reference="environment:OTEL_ENTITIES",
                    schema_url=SCHEMA_TARGET,
                    governance=_governance(),
                )
                self.assertFalse(record.trusted_projection_created)
                self.assertFalse(any(record.effects.values()))
            elif case_id == "OSR-CF-DATA-006":
                secret = "secret-payload-not-for-result"
                record = validator.quarantine_otel_entities(
                    f"service:service.instance.id={secret}",
                    source_reference="environment:OTEL_ENTITIES",
                    schema_url=SCHEMA_TARGET,
                    governance=_governance(),
                )
                self.assertNotIn(secret, repr(record))
                self.assertRegex(record.payload_digest, r"^sha256:[0-9a-f]{64}$")
            elif case_id == "OSR-CF-DATA-007":
                decision = validator.validate_result_claim(
                    validator.valid_result_claim()
                )
                self.assertEqual(decision.status, "VALIDATED_INPUT")
                self.assertFalse(any(decision.effects.values()))
            else:  # pragma: no cover - not part of current PR-G2 subset
                self.fail(f"unexpected PR-G2 data case: {case_id}")
        elif case_id.startswith("OSR-CF-RSLT-"):
            claim = validator.valid_result_claim()
            if case_id == "OSR-CF-RSLT-001":
                claim["synthetic"] = True
                expected = "OSR_SYNTHETIC_RESULT_CANNOT_PASS"
            elif case_id == "OSR-CF-RSLT-002":
                claim["case_ids"] = claim["case_ids"][:-1]
                expected = "OSR_RESULT_CASE_SET_INCOMPLETE"
            elif case_id == "OSR-CF-RSLT-003":
                changed = deepcopy(claim["effects"])
                changed["evidence_created"] = True
                claim["effects"] = changed
                expected = "OSR_RESULT_SELF_AUTHORIZATION_REJECTED"
            else:
                claim["gate_state_change"] = True
                expected = "OSR_RESULT_GATE_EFFECT_REJECTED"
            decision = validator.validate_result_claim(claim)
            self.assertEqual(decision.status, "REJECTED")
            self.assertIn(expected, decision.reason_codes)
            self.assertFalse(any(decision.effects.values()))
        else:  # pragma: no cover - catalog expansion must fail loudly
            self.fail(f"unimplemented provenance conformance case: {case_id}")

    def test_catalog_binding_is_exact_and_deployment_cases_are_not_executed(
        self,
    ) -> None:
        required = _required_case_ids()
        self.assertEqual(len(required), SCHEMA_RESOURCE_PR_G2_CASE_COUNT)
        self.assertEqual(required, SchemaResourceProvenanceValidator().pr_g2_case_ids)
        all_cases = {case["case_id"] for case in _catalog()["cases"]}
        blocked = all_cases - required
        self.assertEqual(len(all_cases), 45)
        self.assertEqual(len(blocked), 9)
        self.assertTrue(
            all(
                "DQ-020" in case["gate_refs"]
                or "PR-G3" in case["gate_refs"]
                or "PR-G5" in case["gate_refs"]
                or "PR-G6" in case["gate_refs"]
                for case in _catalog()["cases"]
                if case["case_id"] in blocked
            )
        )
        claim = SchemaResourceProvenanceValidator().valid_result_claim()
        self.assertEqual(
            claim["catalog_digest"], SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST
        )
        self.assertEqual(claim["schema_artifact_digest"], OTEL_SCHEMA_ARTIFACT_DIGEST)
        self.assertEqual(claim["full_catalog_result"], "BLOCKED")


def _install_case_tests() -> None:
    for case_id in sorted(_required_case_ids()):
        method_name = f"test_{case_id.lower().replace('-', '_')}"

        def test_method(
            self: SchemaResourceConformanceTests,
            bound_case: str = case_id,
        ) -> None:
            self.run_case(bound_case)

        test_method.__name__ = method_name
        test_method.__doc__ = f"Execute frozen case {case_id}."
        setattr(SchemaResourceConformanceTests, method_name, test_method)


_install_case_tests()


if __name__ == "__main__":
    unittest.main()
