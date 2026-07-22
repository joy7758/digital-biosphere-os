#!/usr/bin/env python3
"""Exercise fail-closed telemetry-admission rollback without switching callers.

The drill uses only synthetic metadata in an explicit directory. It preserves
the failed source, restores a verified backup to a different path, validates
the acknowledged receipt inventory, and stops at a human decision gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dbos.telemetry_admission.contracts import (  # noqa: E402
    ENVELOPE_OBJECT_KIND,
    ENVELOPE_SCHEMA_VERSION,
    PROFILE_ID,
)
from dbos.telemetry_admission.models import TelemetryAdmissionError  # noqa: E402
from dbos.telemetry_admission.service import TelemetryAdmissionService  # noqa: E402
from dbos.telemetry_admission.store import (  # noqa: E402
    SQLiteTelemetryAdmissionStore,
)


TIMESTAMP = "2026-07-22T04:00:00Z"


def _digest(seed: str) -> str:
    return f"sha256:{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"


def _envelope(index: int) -> dict[str, Any]:
    seed = f"rollback-drill-{index:06d}"
    return {
        "observation_id": f"ta:observation:{seed}",
        "object_kind": ENVELOPE_OBJECT_KIND,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "profile_id": PROFILE_ID,
        "otel_spec_version": "1.59.0",
        "otlp_version": "1.11.0",
        "semantic_convention_version": "1.43.0",
        "semantic_convention_schema_url": "https://opentelemetry.io/schemas/1.43.0",
        "genai_semconv_ref": "NOT_USED",
        "producer_reference": "rollback:producer:synthetic",
        "transport_source_reference": "rollback:transport:offline",
        "resource": {
            "reference": "rollback:resource:service-a",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("rollback-resource"),
            "attribute_count": 1,
        },
        "instrumentation_scope": {
            "name": "rollback.scope",
            "version": "0.1.0",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("rollback-scope"),
        },
        "signal_type": "TRACE",
        "signal_reference": f"rollback:signal:{index:06d}",
        "context": {
            "trace_id": hashlib.sha256(f"{seed}:trace".encode()).hexdigest()[:32],
            "span_id": hashlib.sha256(f"{seed}:span".encode()).hexdigest()[:16],
            "trace_flags": "01",
            "parent_state": "ROOT",
        },
        "observed_at": TIMESTAMP,
        "received_at": TIMESTAMP,
        "clock_source": "INTAKE_CLOCK",
        "sampling_state": {
            "decision": "RECORD_AND_SAMPLE",
            "rule_reference": "rollback:sampling:default",
            "known_loss": False,
        },
        "redaction_state": {
            "policy_reference": "rollback:redaction:metadata-only",
            "result": "APPLIED",
            "removed_count": 0,
            "hashed_count": 0,
        },
        "content_capture_state": "METADATA_ONLY",
        "delivery_state": "RECEIVED",
        "source_digest": _digest(seed),
        "source_size_bytes": 256,
        "idempotency_reference": f"rollback:attempt:{index:06d}",
        "limitations": [],
    }


def run_drill(directory: Path, admission_count: int = 25) -> dict[str, Any]:
    """Run one local drill and return a bounded machine-readable result."""

    if admission_count < 1:
        raise ValueError("admission_count must be positive")
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    source_path = directory / "failed-source.sqlite3"
    backup_path = directory / "verified-pre-incident-backup.sqlite3"
    restored_path = directory / "restored-candidate.sqlite3"
    store = SQLiteTelemetryAdmissionStore(source_path)
    store.initialize()
    service = TelemetryAdmissionService(store)
    acknowledged: dict[str, str] = {}
    for index in range(admission_count):
        result = service.admit(_envelope(index))
        acknowledged[result.admission_id] = result.intake_receipt_reference
    pre_incident_integrity = store.integrity_report(
        expected_receipt_references=acknowledged.values()
    )
    manifest = store.backup(backup_path)

    # Synthetic incident: corrupt the failed source only after a verified backup.
    with source_path.open("r+b") as handle:
        handle.seek(0)
        handle.write(b"DBOS-FAILED-SOURCE-PRESERVED")
        handle.flush()
        os.fsync(handle.fileno())
    retained_paths = [source_path]
    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{source_path}{suffix}")
        if sidecar.exists():
            retained_paths.append(sidecar)
    for retained in retained_paths:
        retained.chmod(0o400)

    failed_source_classification = "FAIL_CLOSED"
    try:
        failed_report = SQLiteTelemetryAdmissionStore(source_path).integrity_report(
            expected_receipt_references=acknowledged.values()
        )
    except TelemetryAdmissionError:
        pass
    else:
        if failed_report["status"] != "FAIL":
            failed_source_classification = "UNEXPECTEDLY_READABLE"

    restored = SQLiteTelemetryAdmissionStore.restore(
        backup_path, manifest, restored_path
    )
    restored_integrity = restored.integrity_report(
        expected_receipt_references=acknowledged.values()
    )
    receipt_mismatches = [
        admission_id
        for admission_id, receipt in acknowledged.items()
        if restored.get_receipt_for_admission(admission_id) != receipt
    ]
    retained_modes = {
        path.name: oct(path.stat().st_mode & 0o777) for path in retained_paths
    }
    passed = (
        pre_incident_integrity["status"] == "PASS"
        and failed_source_classification == "FAIL_CLOSED"
        and restored_integrity["status"] == "PASS"
        and not receipt_mismatches
        and all(mode == "0o400" for mode in retained_modes.values())
    )
    return {
        "drill_id": "DBOS-TA-ROLLBACK-DRILL-0.1",
        "result": "PASS" if passed else "FAIL",
        "result_semantics": "LOCAL_SYNTHETIC_ROLLBACK_EXERCISE",
        "environment": {
            "python_version": platform.python_version(),
            "sqlite_version": sqlite3.sqlite_version,
            "platform": platform.platform(),
        },
        "admission_count": admission_count,
        "acknowledged_receipt_count": len(acknowledged),
        "pre_incident_integrity": pre_incident_integrity,
        "failed_source_classification": failed_source_classification,
        "failed_source_retained": True,
        "retained_modes": retained_modes,
        "backup_manifest": manifest,
        "restore_destination_is_distinct": restored_path != source_path,
        "restored_integrity": restored_integrity,
        "receipt_mismatch_count": len(receipt_mismatches),
        "automatic_switch_performed": False,
        "rollback_decision_recorded": False,
        "next_gate": "HUMAN_SWITCH_REQUIRED",
        "authority_effects": {
            "agent_created": False,
            "runtime_created": False,
            "entity_created": False,
            "permission_granted": False,
            "evidence_created": False,
            "saee_invoked": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_dir", type=Path)
    parser.add_argument("--admissions", type=int, default=25)
    args = parser.parse_args()
    result = run_drill(args.work_dir.resolve(), args.admissions)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
