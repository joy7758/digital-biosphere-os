#!/usr/bin/env python3
"""Validate the bounded DBOS Telemetry Admission Foundation v0.1.

The validator uses synthetic metadata and temporary SQLite files only. A PASS
does not create or validate real telemetry, Evidence, Verification, Identity,
Entity, Agent, Runtime, Permission, SAEE output, endpoint, or deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dbos.telemetry_admission.service import TelemetryAdmissionService  # noqa: E402
from dbos.telemetry_admission.semantic import (  # noqa: E402
    SemanticMetadataMapper,
)
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore  # noqa: E402
from dbos.telemetry_admission.validator import TelemetryEnvelopeValidator  # noqa: E402
from dbos.telemetry_admission.provenance import (  # noqa: E402
    DataGovernanceBinding,
    SchemaResourceProvenanceValidator,
    TransformerBinding,
)
from dbos.telemetry_admission.references import (  # noqa: E402
    SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
    SEMANTIC_RESULT_SCHEMA_FILENAME,
    ReferenceIntegrityError,
    read_pinned_json,
)


TIMESTAMP = "2026-07-22T04:00:00Z"
CONFORMANCE_CATALOG = (
    ROOT / "tests" / "telemetry_admission" / "conformance_catalog.v0.1.json"
)
LOAD_CONTRACT = (
    ROOT / "tests" / "telemetry_admission" / "load_characterization.v0.1.json"
)
SEMANTIC_BINDING = (
    ROOT / "tests" / "telemetry_admission" / "semantic_pr_g2_bindings.v0.1.json"
)
SCHEMA_RESOURCE_BINDING = (
    ROOT / "tests" / "telemetry_admission" / "schema_resource_pr_g2_bindings.v0.1.json"
)
SUPPLY_CHAIN_ARTIFACTS = {
    ROOT / "requirements" / "telemetry-admission-runtime-py312-macos-arm64.lock": (
        "13a50e3f657af397b77809c7e00ceaef343b26bd111781376de5d04af36ada8d"
    ),
    ROOT / "requirements" / "telemetry-admission-runtime-py312-linux-arm64.lock": (
        "b989823d32d406ce283b11500a8198155c56381adeb37a13c7dc2c58fb0b38b3"
    ),
    ROOT / "requirements" / "telemetry-admission-runtime-py312-linux-x86_64.lock": (
        "76746fc746c6e5e9e5bc2c4141d905809d0040296af4ab636a289cb6dc8c1ddf"
    ),
    ROOT / "requirements" / "telemetry-admission-build.lock": (
        "1cea23a952436c9e226278bb037a803510d3e5f16ae984891420de5a5dcea95c"
    ),
    ROOT / "requirements" / "README.md": (
        "aa6efea0d55e9b15a9de4366768c31e518dadac6698413346f1ebe61aa727988"
    ),
}
CASE_COUNTS = {"C": 12, "N": 7, "D": 12, "S": 11, "F": 14, "M": 12, "R": 10}


def _digest(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(
    signal: str = "TRACE", observation: str = "validator-trace"
) -> dict[str, Any]:
    context = (
        {
            "trace_id": hashlib.sha256(b"validator-trace").hexdigest()[:32],
            "span_id": hashlib.sha256(b"validator-span").hexdigest()[:16],
            "trace_flags": "01",
            "parent_state": "ROOT",
        }
        if signal == "TRACE"
        else {
            "trace_id": "NOT_APPLICABLE",
            "span_id": "NOT_APPLICABLE",
            "trace_flags": "NOT_APPLICABLE",
            "parent_state": "NOT_APPLICABLE",
        }
    )
    return {
        "observation_id": f"ta:observation:{observation}",
        "object_kind": "TelemetryObservationEnvelope",
        "schema_version": "0.1.0",
        "profile_id": "TMAI-OTEL-OBSERVABILITY-PROFILE-0.1",
        "otel_spec_version": "1.59.0",
        "otlp_version": "1.11.0",
        "semantic_convention_version": "1.43.0",
        "semantic_convention_schema_url": "https://opentelemetry.io/schemas/1.43.0",
        "genai_semconv_ref": "NOT_USED",
        "producer_reference": "validator:producer:declared",
        "transport_source_reference": "validator:transport:offline",
        "resource": {
            "reference": "validator:resource:service-a",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("validator-resource"),
            "attribute_count": 1,
        },
        "instrumentation_scope": {
            "name": "validator.scope",
            "version": "0.1.0",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("validator-scope"),
        },
        "signal_type": signal,
        "signal_reference": f"validator:signal:{signal.lower()}",
        "context": context,
        "observed_at": TIMESTAMP,
        "received_at": TIMESTAMP,
        "clock_source": "INTAKE_CLOCK",
        "sampling_state": {
            "decision": "RECORD_AND_SAMPLE" if signal == "TRACE" else "NOT_APPLICABLE",
            "rule_reference": "validator:sampling:default",
            "known_loss": False,
        },
        "redaction_state": {
            "policy_reference": "validator:redaction:metadata-only",
            "result": "APPLIED",
            "removed_count": 0,
            "hashed_count": 0,
        },
        "content_capture_state": "METADATA_ONLY",
        "delivery_state": "RECEIVED",
        "source_digest": _digest(f"validator-source:{signal}:{observation}"),
        "source_size_bytes": 512,
        "idempotency_reference": f"validator:attempt:{observation}",
        "limitations": [],
    }


def validate() -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    validator = TelemetryEnvelopeValidator()
    for signal in ("TRACE", "METRIC", "LOG"):
        decision = validator.validate(_fixture(signal, f"validator-{signal.lower()}"))
        checks[f"{signal.lower()}_accepted"] = decision.state == "ACCEPTED_AS_MATERIAL"

    authority = _fixture()
    authority["permission"] = "GRANTED"
    authority_decision = validator.validate(authority)
    checks["authority_rejected"] = (
        authority_decision.state == "REJECTED"
        and authority_decision.normalized_envelope is None
    )

    profile = _fixture()
    profile["signal_type"] = "PROFILE"
    checks["profile_rejected"] = validator.validate(profile).state == "REJECTED"

    catalog = json.loads(CONFORMANCE_CATALOG.read_text(encoding="utf-8"))
    expected_cases = {
        f"TA-{group}{index:03d}"
        for group, count in CASE_COUNTS.items()
        for index in range(1, count + 1)
    }
    observed_cases = {case["case_id"] for case in catalog.get("cases", [])}
    checks["conformance_catalog_exact"] = (
        catalog.get("case_count") == 78
        and len(catalog.get("cases", [])) == 78
        and observed_cases == expected_cases
    )
    load_contract = json.loads(LOAD_CONTRACT.read_text(encoding="utf-8"))
    checks["load_contract_frozen_without_posthoc_thresholds"] = (
        load_contract.get("frozen_before_execution") is True
        and load_contract.get("result_semantics") == "CHARACTERIZATION_NOT_SLO"
        and load_contract.get("pass_fail_thresholds") is None
        and set(load_contract.get("workloads", {}))
        == {f"TA-P00{index}" for index in range(1, 6)}
        and not any(load_contract.get("authority_effects", {}).values())
    )
    checks["supply_chain_artifact_digests_exact"] = all(
        path.is_file() and _file_sha256(path) == digest
        for path, digest in SUPPLY_CHAIN_ARTIFACTS.items()
    )
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    checks["build_backend_exact_pin"] = (
        'requires = ["setuptools==83.0.0"]' in pyproject_text
        and 'requires = ["setuptools>=69"]' not in pyproject_text
    )
    supply_chain_instructions = (ROOT / "requirements" / "README.md").read_text(
        encoding="utf-8"
    )
    checks["supply_chain_paths_fail_closed"] = all(
        required in supply_chain_instructions
        for required in (
            "--require-hashes",
            "--only-binary=:all:",
            "--no-deps",
            "SOURCE_DATE_EPOCH=1784678400",
            "--no-isolation",
        )
    )

    semantic = SemanticMetadataMapper()
    semantic_binding = json.loads(SEMANTIC_BINDING.read_text(encoding="utf-8"))
    checks["semantic_reference_inventory_exact"] = (
        semantic.mapping_count == 47
        and len(semantic.pr_g2_case_ids) == 32
        and semantic_binding.get("authorized_case_count") == 32
        and semantic_binding.get("blocked_not_authorized_case_count") == 14
    )
    semantic_result = semantic.map_attributes(
        {
            "service.name": "validator-service",
            "gen_ai.operation.name": "chat",
        }
    )
    checks["semantic_digest_only_zero_effect"] = (
        semantic_result.status == "PARTIAL"
        and len(semantic_result.projections) == 2
        and not any(semantic_result.effects.values())
        and semantic_result.as_dict().get("raw_values_present") is False
        and "validator-service" not in json.dumps(semantic_result.as_dict())
    )
    semantic_authority = semantic.map_attributes({"dbos.permission": "GRANTED"})
    checks["semantic_authority_injection_rejected"] = (
        semantic_authority.status == "REJECTED"
        and "SEM_AUTHORITY_FIELD_REJECTED" in semantic_authority.reason_codes
        and not any(semantic_authority.effects.values())
    )
    semantic_claim = semantic.valid_result_claim()
    semantic_claim["gate_state_change"] = True
    checks["semantic_result_cannot_close_gate"] = (
        semantic.validate_result_claim(semantic_claim).status == "REJECTED"
    )

    provenance = SchemaResourceProvenanceValidator()
    schema_binding = json.loads(SCHEMA_RESOURCE_BINDING.read_text(encoding="utf-8"))
    artifact_info = provenance.artifact_info()
    checks["schema_resource_reference_inventory_exact"] = (
        artifact_info.digest
        == "sha256:6ac5dd367ff707dbcdcb1e5b459d4ac2fd676fb44eb17a21f9494a9fee4233df"
        and artifact_info.runtime_network_fetch_enabled is False
        and len(provenance.pr_g2_case_ids) == 36
        and schema_binding.get("authorized_case_count") == 36
        and schema_binding.get("blocked_not_authorized_case_count") == 9
    )
    result_schemas_valid = True
    try:
        for filename in (
            SEMANTIC_RESULT_SCHEMA_FILENAME,
            SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
        ):
            Draft202012Validator.check_schema(read_pinned_json(filename))
    except (ReferenceIntegrityError, SchemaError):
        result_schemas_valid = False
    checks["otel_result_schemas_meta_valid"] = result_schemas_valid
    precedence = provenance.resolve_schema_precedence(
        "https://opentelemetry.io/schemas/1.42.0",
        "https://opentelemetry.io/schemas/1.43.0",
    )
    checks["schema_precedence_retains_both_sources"] = (
        precedence.status == "RESOLVED"
        and precedence.effective_schema_url == "https://opentelemetry.io/schemas/1.43.0"
        and precedence.resource_schema_url_original
        == "https://opentelemetry.io/schemas/1.42.0"
        and not any(precedence.effects.values())
    )
    transform = provenance.transform_attributes(
        {"gen_ai.system": "validator-provider"},
        source_schema_url="https://opentelemetry.io/schemas/1.36.0",
        binding=TransformerBinding(
            transformer_id="validator:offline-transformer",
            transformer_version="0.1.0",
            artifact_digest=_digest("validator-transformer"),
            environment_digest=_digest("validator-python"),
        ),
    )
    checks["schema_transform_lineage_digest_only"] = (
        transform.status == "TRANSFORMED"
        and "gen_ai.provider.name" in transform.output_field_digests
        and "validator-provider" not in repr(transform)
        and not any(transform.effects.values())
    )
    governance = DataGovernanceBinding(
        tenant_scope_reference="validator:tenant:synthetic",
        purpose_reference="validator:purpose:conformance",
        retention_policy_reference="validator:retention:bounded",
        access_policy_reference="validator:access:isolated",
        encryption_policy_reference="validator:encryption:key-ref",
        classification_status="PASS",
        redaction_status="PASS",
        isolation_status="PASS",
        retention_status="PASS",
    )
    quarantine = provenance.quarantine_otel_entities(
        "service:service.instance.id=validator-node",
        source_reference="validator:environment:OTEL_ENTITIES",
        schema_url="https://opentelemetry.io/schemas/1.43.0",
        governance=governance,
    )
    checks["otel_entity_quarantined_without_dbos_entity"] = (
        quarantine.status == "QUARANTINED"
        and quarantine.stability == "DEVELOPMENT"
        and quarantine.trusted_projection_created is False
        and "validator-node" not in repr(quarantine)
        and not any(quarantine.effects.values())
    )
    provenance_claim = provenance.valid_result_claim()
    provenance_claim["effects"]["evidence_created"] = True
    checks["provenance_result_cannot_create_evidence_or_gate"] = (
        provenance.validate_result_claim(provenance_claim).status == "REJECTED"
    )

    temporary_counts: dict[str, int] = {}
    canary_present = True
    recovery_pass = False
    with tempfile.TemporaryDirectory(prefix="dbos-ta-validator-") as temp:
        root = Path(temp)
        store = SQLiteTelemetryAdmissionStore(root / "admission.sqlite3")
        service = TelemetryAdmissionService(store)
        envelope = _fixture()
        first = service.admit(envelope, admission_id="ta:admission:validator")
        replay = service.admit(
            envelope,
            admission_id=first.admission_id,
            claimed_intake_receipt_reference=first.intake_receipt_reference,
        )
        checks["confirmed_replay"] = replay.state == "DUPLICATE_CONFIRMED"

        canary = f"sensitive-canary-{uuid.uuid4().hex}"
        rejected = _fixture(observation="validator-rejected")
        rejected["prompt"] = canary
        rejected_result = service.admit(rejected)
        checks["sensitive_rejected"] = rejected_result.state == "REJECTED"

        backup = root / "backup.sqlite3"
        manifest = store.backup(backup)
        restored = SQLiteTelemetryAdmissionStore.restore(
            backup, manifest, root / "restored.sqlite3"
        )
        recovery_report = restored.integrity_report(
            expected_receipt_references=(first.intake_receipt_reference,)
        )
        recovery_pass = recovery_report["status"] == "PASS"
        checks["acknowledged_receipt_continuity"] = (
            recovery_report["missing_expected_receipt_count"] == 0
            and restored.get_receipt_for_admission(first.admission_id)
            == first.intake_receipt_reference
        )
        temporary_counts = store.counts()
        canary_present = any(
            canary.encode("utf-8") in path.read_bytes()
            for path in root.iterdir()
            if path.is_file()
        )

    checks["recovery_pass"] = recovery_pass
    checks["canary_absent"] = not canary_present
    for name, passed in checks.items():
        if not passed:
            errors.append(f"check failed: {name}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "contract": "TMAI-DBOS-TELEMETRY-ADMISSION-FOUNDATION-0.1",
        "check_count": len(checks),
        "passed_check_count": sum(checks.values()),
        "checks": checks,
        "temporary_reference_store_counts": temporary_counts,
        "temporary_store_removed": True,
        "live_effect_counts": {
            "agent": 0,
            "runtime": 0,
            "entity": 0,
            "capability": 0,
            "permission": 0,
            "evidence": 0,
            "verification": 0,
            "saee_call": 0,
            "network_endpoint": 0,
            "collector": 0,
        },
        "production_ready": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    result = validate()
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"telemetry_admission_validator: {result['status']}")
        print(f"checks: {result['passed_check_count']}/{result['check_count']}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
