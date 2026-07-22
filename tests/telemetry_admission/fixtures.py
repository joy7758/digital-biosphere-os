"""Deterministic synthetic fixtures for telemetry admission tests."""

from __future__ import annotations

import copy
import hashlib
import sqlite3
from pathlib import Path
from typing import Any

from dbos.telemetry_admission.contracts import (
    ENVELOPE_OBJECT_KIND,
    ENVELOPE_SCHEMA_VERSION,
    PROFILE_ID,
)
from dbos.telemetry_admission.store import (
    PRIOR_COMPATIBLE_FIXTURE_RESOURCE,
    SQLiteTelemetryAdmissionStore,
    prior_compatible_fixture_checksum,
)


TIMESTAMP = "2026-07-22T04:00:00Z"


def digest(seed: str) -> str:
    return f"sha256:{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"


def hex_id(seed: str, length: int) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:length]


def make_envelope(
    *,
    signal_type: str = "TRACE",
    observation_id: str = "ta:observation:fixture-trace-001",
    source_seed: str = "fixture-source-001",
    signal_reference: str = "fixture:signal:001",
    idempotency_reference: str = "fixture:attempt:001",
    delivery_state: str = "RECEIVED",
) -> dict[str, Any]:
    context = (
        {
            "trace_id": hex_id(f"{source_seed}:trace", 32),
            "span_id": hex_id(f"{source_seed}:span", 16),
            "trace_flags": "01",
            "parent_state": "ROOT",
        }
        if signal_type == "TRACE"
        else {
            "trace_id": "NOT_APPLICABLE",
            "span_id": "NOT_APPLICABLE",
            "trace_flags": "NOT_APPLICABLE",
            "parent_state": "NOT_APPLICABLE",
        }
    )
    return {
        "observation_id": observation_id,
        "object_kind": ENVELOPE_OBJECT_KIND,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "profile_id": PROFILE_ID,
        "otel_spec_version": "1.59.0",
        "otlp_version": "1.11.0",
        "semantic_convention_version": "1.43.0",
        "semantic_convention_schema_url": "https://opentelemetry.io/schemas/1.43.0",
        "genai_semconv_ref": "NOT_USED",
        "producer_reference": "fixture:producer:declared",
        "transport_source_reference": "fixture:transport:offline",
        "resource": {
            "reference": "fixture:resource:service-a",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": digest("resource-attributes"),
            "attribute_count": 3,
        },
        "instrumentation_scope": {
            "name": "fixture.scope",
            "version": "0.1.0",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": digest("scope-attributes"),
        },
        "signal_type": signal_type,
        "signal_reference": signal_reference,
        "context": context,
        "observed_at": TIMESTAMP,
        "received_at": TIMESTAMP,
        "clock_source": "INTAKE_CLOCK",
        "sampling_state": {
            "decision": "RECORD_AND_SAMPLE"
            if signal_type == "TRACE"
            else "NOT_APPLICABLE",
            "rule_reference": "fixture:sampling:default",
            "known_loss": False,
        },
        "redaction_state": {
            "policy_reference": "fixture:redaction:metadata-only",
            "result": "APPLIED",
            "removed_count": 0,
            "hashed_count": 0,
        },
        "content_capture_state": "METADATA_ONLY",
        "delivery_state": delivery_state,
        "source_digest": digest(source_seed),
        "source_size_bytes": 1024,
        "idempotency_reference": idempotency_reference,
        "limitations": [],
    }


def changed(envelope: dict[str, Any], **values: Any) -> dict[str, Any]:
    result = copy.deepcopy(envelope)
    result.update(values)
    return result


def create_prior_compatible_store(path: Path) -> SQLiteTelemetryAdmissionStore:
    """Create the exact synthetic prior fixture declared by migration resources."""

    current = SQLiteTelemetryAdmissionStore(path)
    current.initialize()
    script = PRIOR_COMPATIBLE_FIXTURE_RESOURCE.read_text(encoding="utf-8").replace(
        "{{PRIOR_CHECKSUM}}", prior_compatible_fixture_checksum()
    )
    connection = sqlite3.connect(path, isolation_level=None)
    try:
        connection.executescript(script)
    finally:
        connection.close()
    return SQLiteTelemetryAdmissionStore(path)
