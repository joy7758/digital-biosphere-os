#!/usr/bin/env python3
"""Measure the SQLite telemetry-admission reference backend.

This is an offline, synthetic characterization harness. It does not expose a
listener, start a Runtime, create an Entity, grant Permission, create canonical
Evidence, or invoke SAEE. Results are measurements, never SLO claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import resource
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
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
from tools.telemetry_admission_otel_conformance import (  # noqa: E402
    git_observation,
    source_manifest,
)


CONTRACT_PATH = (
    ROOT / "tests" / "telemetry_admission" / "load_characterization.v0.1.json"
)
TIMESTAMP = "2026-07-22T04:00:00Z"


def _digest(seed: str) -> str:
    return f"sha256:{hashlib.sha256(seed.encode('utf-8')).hexdigest()}"


def _hex_id(seed: str, length: int) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:length]


def _envelope(index: int, *, invalid: bool = False) -> dict[str, Any]:
    seed = f"characterization-{index:012d}"
    value: dict[str, Any] = {
        "observation_id": f"ta:observation:{seed}",
        "object_kind": ENVELOPE_OBJECT_KIND,
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "profile_id": PROFILE_ID,
        "otel_spec_version": "1.59.0",
        "otlp_version": "1.11.0",
        "semantic_convention_version": "1.43.0",
        "semantic_convention_schema_url": "https://opentelemetry.io/schemas/1.43.0",
        "genai_semconv_ref": "NOT_USED",
        "producer_reference": "characterization:producer:synthetic",
        "transport_source_reference": "characterization:transport:offline",
        "resource": {
            "reference": "characterization:resource:service-a",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("characterization-resource"),
            "attribute_count": 3,
        },
        "instrumentation_scope": {
            "name": "characterization.scope",
            "version": "0.1.0",
            "schema_url": "https://opentelemetry.io/schemas/1.43.0",
            "attribute_set_digest": _digest("characterization-scope"),
        },
        "signal_type": "TRACE",
        "signal_reference": f"characterization:signal:{index:012d}",
        "context": {
            "trace_id": _hex_id(f"{seed}:trace", 32),
            "span_id": _hex_id(f"{seed}:span", 16),
            "trace_flags": "01",
            "parent_state": "ROOT",
        },
        "observed_at": TIMESTAMP,
        "received_at": TIMESTAMP,
        "clock_source": "INTAKE_CLOCK",
        "sampling_state": {
            "decision": "RECORD_AND_SAMPLE",
            "rule_reference": "characterization:sampling:default",
            "known_loss": False,
        },
        "redaction_state": {
            "policy_reference": "characterization:redaction:metadata-only",
            "result": "APPLIED",
            "removed_count": 0,
            "hashed_count": 0,
        },
        "content_capture_state": "METADATA_ONLY",
        "delivery_state": "RECEIVED",
        "source_digest": _digest(seed),
        "source_size_bytes": 1024,
        "idempotency_reference": f"characterization:attempt:{index:012d}",
        "limitations": [],
    }
    if invalid:
        value["evidence_status"] = "VALID"
    return value


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _latencies(values: list[float]) -> dict[str, float]:
    return {
        "p50_ms": round(_percentile(values, 0.50) * 1000, 6),
        "p95_ms": round(_percentile(values, 0.95) * 1000, 6),
        "p99_ms": round(_percentile(values, 0.99) * 1000, 6),
        "mean_ms": round(statistics.fmean(values) * 1000, 6) if values else 0.0,
        "max_ms": round(max(values) * 1000, 6) if values else 0.0,
    }


def _file_sizes(path: Path) -> dict[str, int]:
    return {
        "database_bytes": path.stat().st_size if path.exists() else 0,
        "wal_bytes": Path(f"{path}-wal").stat().st_size
        if Path(f"{path}-wal").exists()
        else 0,
        "shm_bytes": Path(f"{path}-shm").stat().st_size
        if Path(f"{path}-shm").exists()
        else 0,
    }


def _environment() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "sqlite_version": sqlite3.sqlite_version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }


def _authority_effects() -> dict[str, bool]:
    return {
        "agent_created": False,
        "runtime_created": False,
        "entity_created": False,
        "capability_created": False,
        "permission_created": False,
        "execution_created": False,
        "evidence_created": False,
        "verification_created": False,
        "collector_created": False,
        "network_endpoint_created": False,
        "saee_called": False,
        "gate_state_changed": False,
        "production_ready_declared": False,
    }


def _run_metrics(
    started_wall: float,
    started_cpu: float,
    *,
    python_allocation_tracing: bool,
) -> dict[str, Any]:
    peak: int | None = None
    if python_allocation_tracing:
        if not tracemalloc.is_tracing():
            raise RuntimeError("python allocation tracing was not started")
        _, peak = tracemalloc.get_traced_memory()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "wall_seconds": round(time.perf_counter() - started_wall, 6),
        "cpu_seconds": round(time.process_time() - started_cpu, 6),
        "python_allocation_tracing": python_allocation_tracing,
        "python_tracemalloc_peak_bytes": peak,
        "process_max_rss_native_units": usage.ru_maxrss,
    }


def _base_result(case_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "result_semantics": "CHARACTERIZATION_NOT_SLO",
        "backend_scope": "SQLITE_SINGLE_HOST_REFERENCE_ONLY",
        "parameters": parameters,
        "environment": _environment(),
        "authority_effects": _authority_effects(),
    }


def _contract_binding() -> dict[str, Any]:
    value = CONTRACT_PATH.read_bytes()
    return {
        "path": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "size_bytes": len(value),
        "digest": f"sha256:{hashlib.sha256(value).hexdigest()}",
    }


def _start_execution_binding() -> dict[str, Any]:
    return {
        "binding_schema_version": "0.1",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "git_observation": git_observation(),
        "contract": _contract_binding(),
        "implementation_manifest_at_start": source_manifest(),
    }


def _finish_execution_binding(binding: dict[str, Any]) -> dict[str, Any]:
    end_manifest = source_manifest()
    start_digest = binding["implementation_manifest_at_start"]["manifest_digest"]
    end_digest = end_manifest["manifest_digest"]
    return {
        **binding,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "implementation_manifest_at_end": end_manifest,
        "source_stable_during_run": start_digest == end_digest,
        "binding_result": "PASS" if start_digest == end_digest else "FAIL",
    }


def _result_artifact_target(path: Path) -> Path:
    provided = path.expanduser().absolute()
    resolved_parent = provided.parent.resolve(strict=True)
    if not resolved_parent.is_dir():
        raise NotADirectoryError(resolved_parent)
    target = resolved_parent / provided.name
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"result artifact already exists: {target}")
    return target


def write_result_artifact(path: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Create a private, immutable-by-contract result file without overwrite."""

    target = _result_artifact_target(path)
    resolved_parent = target.parent

    encoded = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=resolved_parent
    )
    temporary_path = Path(temporary_name)
    try:
        os.fchmod(file_descriptor, 0o600)
        view = memoryview(encoded)
        while view:
            written = os.write(file_descriptor, view)
            view = view[written:]
        os.fsync(file_descriptor)
        os.close(file_descriptor)
        file_descriptor = -1
        os.link(temporary_path, target, follow_symlinks=False)
        temporary_path.unlink()
        directory_descriptor = os.open(resolved_parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if file_descriptor >= 0:
            os.close(file_descriptor)
        temporary_path.unlink(missing_ok=True)

    return {
        "path": target.as_posix(),
        "size_bytes": len(encoded),
        "digest": f"sha256:{hashlib.sha256(encoded).hexdigest()}",
        "mode": oct(target.stat().st_mode & 0o777),
        "overwrite_permitted": False,
    }


def characterize_p001(directory: Path, count: int) -> dict[str, Any]:
    path = directory / "p001.sqlite3"
    store = SQLiteTelemetryAdmissionStore(path)
    store.initialize()
    service = TelemetryAdmissionService(store)
    latencies: list[float] = []
    tracemalloc.start()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    states: dict[str, int] = {}
    for index in range(count):
        started = time.perf_counter()
        result = service.admit(_envelope(index))
        latencies.append(time.perf_counter() - started)
        states[result.state] = states.get(result.state, 0) + 1
    metrics = _run_metrics(started_wall, started_cpu, python_allocation_tracing=True)
    tracemalloc.stop()
    return {
        **_base_result("TA-P001", {"unique_admissions": count, "workers": 1}),
        "measurements": {
            **metrics,
            **_latencies(latencies),
            **_file_sizes(path),
            "operations": count,
            "states": states,
            "store_counts": store.counts(),
            "integrity": store.integrity_report(),
        },
    }


def characterize_p002(directory: Path, originals: int, retries: int) -> dict[str, Any]:
    path = directory / "p002.sqlite3"
    store = SQLiteTelemetryAdmissionStore(path)
    store.initialize()
    service = TelemetryAdmissionService(store)
    bindings: list[tuple[str, str]] = []
    for index in range(originals):
        result = service.admit(_envelope(index))
        bindings.append((result.admission_id, result.intake_receipt_reference))
    before = store.counts()
    latencies: list[float] = []
    confirmed = 0
    tracemalloc.start()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    for index in range(retries):
        admission_id, receipt = bindings[index % originals]
        started = time.perf_counter()
        result = service.admit(
            _envelope(index % originals),
            admission_id=admission_id,
            claimed_intake_receipt_reference=receipt,
        )
        latencies.append(time.perf_counter() - started)
        confirmed += int(result.state == "DUPLICATE_CONFIRMED")
    metrics = _run_metrics(started_wall, started_cpu, python_allocation_tracing=True)
    tracemalloc.stop()
    after = store.counts()
    return {
        **_base_result(
            "TA-P002",
            {"original_admissions": originals, "confirmed_retries": retries},
        ),
        "measurements": {
            **metrics,
            **_latencies(latencies),
            **_file_sizes(path),
            "confirmed_retries": confirmed,
            "duplicate_accuracy": confirmed / retries if retries else 1.0,
            "before_counts": before,
            "after_counts": after,
            "record_growth": after["admission_records"] - before["admission_records"],
            "lifecycle_growth": after["admission_lifecycles"]
            - before["admission_lifecycles"],
            "integrity": store.integrity_report(),
        },
    }


def characterize_p003(
    directory: Path, workers: int, duration_seconds: float, target_rate: float
) -> dict[str, Any]:
    path = directory / "p003.sqlite3"
    SQLiteTelemetryAdmissionStore(path).initialize()
    stop_at = time.monotonic() + duration_seconds
    interval = workers / target_rate if target_rate > 0 else 0.0
    lock = threading.Lock()
    latencies: list[float] = []
    states: dict[str, int] = {}
    errors: dict[str, int] = {}
    counter = 0

    def worker(worker_id: int) -> None:
        nonlocal counter
        service = TelemetryAdmissionService(SQLiteTelemetryAdmissionStore(path))
        local_index = 0
        while time.monotonic() < stop_at:
            with lock:
                index = counter
                counter += 1
            started = time.perf_counter()
            try:
                result = service.admit(_envelope(index))
                elapsed = time.perf_counter() - started
                with lock:
                    latencies.append(elapsed)
                    states[result.state] = states.get(result.state, 0) + 1
            except TelemetryAdmissionError as exc:
                with lock:
                    errors[exc.reason_code] = errors.get(exc.reason_code, 0) + 1
            except Exception as exc:  # unexpected types are bounded measurements
                error_name = f"UNEXPECTED_{type(exc).__name__}"
                with lock:
                    errors[error_name] = errors.get(error_name, 0) + 1
            local_index += 1
            if interval:
                deadline = started + interval
                remaining = deadline - time.perf_counter()
                if remaining > 0:
                    time.sleep(remaining)

    started_wall, started_cpu = time.perf_counter(), time.process_time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, index) for index in range(workers)]
        for future in futures:
            future.result()
    metrics = _run_metrics(started_wall, started_cpu, python_allocation_tracing=False)
    store = SQLiteTelemetryAdmissionStore(path)
    return {
        **_base_result(
            "TA-P003",
            {
                "workers": workers,
                "duration_seconds": duration_seconds,
                "target_operations_per_second": target_rate,
            },
        ),
        "measurements": {
            **metrics,
            "observer_effect_control": (
                "CONCURRENT_TRACEMALLOC_DISABLED_PROCESS_MAX_RSS_RETAINED"
            ),
            **_latencies(latencies),
            **_file_sizes(path),
            "operations": len(latencies),
            "states": states,
            "errors": errors,
            "observed_operations_per_second": len(latencies) / metrics["wall_seconds"]
            if metrics["wall_seconds"]
            else 0.0,
            "store_counts": store.counts(),
            "integrity": store.integrity_report(),
        },
    }


def characterize_p004(
    directory: Path, unique_admissions: int, backup_count: int
) -> dict[str, Any]:
    path = directory / "p004.sqlite3"
    store = SQLiteTelemetryAdmissionStore(path)
    store.initialize()
    service = TelemetryAdmissionService(store)
    completed = threading.Event()
    errors: list[str] = []
    write_latencies: list[float] = []

    def writer() -> None:
        try:
            for index in range(unique_admissions):
                started = time.perf_counter()
                service.admit(_envelope(index))
                write_latencies.append(time.perf_counter() - started)
        except TelemetryAdmissionError as exc:
            errors.append(exc.reason_code)
        finally:
            completed.set()

    thread = threading.Thread(target=writer, name="ta-p004-writer")
    thread.start()
    backup_latencies: list[float] = []
    restore_passes = 0
    manifests: list[dict[str, Any]] = []
    for index in range(backup_count):
        if completed.is_set() and index > 0:
            break
        destination = directory / f"p004-backup-{index:03d}.sqlite3"
        started = time.perf_counter()
        manifest = store.backup(destination)
        backup_latencies.append(time.perf_counter() - started)
        manifests.append(manifest)
        restored = SQLiteTelemetryAdmissionStore.restore(
            destination,
            manifest,
            directory / f"p004-restored-{index:03d}.sqlite3",
        )
        restore_passes += int(restored.integrity_report()["status"] == "PASS")
    thread.join()
    final = store.integrity_report()
    return {
        **_base_result(
            "TA-P004",
            {
                "unique_admissions": unique_admissions,
                "backup_count": backup_count,
                "writer_workers": 1,
            },
        ),
        "measurements": {
            "writes": len(write_latencies),
            "writer_errors": errors,
            "write_latency": _latencies(write_latencies),
            "backups_completed": len(manifests),
            "backup_latency": _latencies(backup_latencies),
            "restore_passes": restore_passes,
            "restore_pass_rate": restore_passes / len(manifests) if manifests else 0.0,
            **_file_sizes(path),
            "store_counts": store.counts(),
            "integrity": final,
        },
    }


def characterize_p005(
    directory: Path,
    duration_seconds: float,
    target_rate: float,
    integrity_interval_seconds: float,
) -> dict[str, Any]:
    path = directory / "p005.sqlite3"
    store = SQLiteTelemetryAdmissionStore(path)
    store.initialize()
    service = TelemetryAdmissionService(store)
    cycle = (
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "ACCEPTED_AS_MATERIAL",
        "REJECTED",
        "REJECTED",
        "DUPLICATE_CONFIRMED",
    )
    states: dict[str, int] = {}
    errors: dict[str, int] = {}
    latencies: list[float] = []
    integrity_checks: list[dict[str, Any]] = []
    accepted_bindings: list[tuple[int, str, str]] = []
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    stop_at = time.monotonic() + duration_seconds
    next_integrity = time.monotonic() + integrity_interval_seconds
    interval = 1 / target_rate if target_rate > 0 else 0.0
    index = 0
    tracemalloc.start()
    while time.monotonic() < stop_at:
        operation_started = time.perf_counter()
        expected = cycle[index % len(cycle)]
        try:
            if expected == "DUPLICATE_CONFIRMED" and accepted_bindings:
                original_index, admission_id, receipt = accepted_bindings[
                    index % len(accepted_bindings)
                ]
                result = service.admit(
                    _envelope(original_index),
                    admission_id=admission_id,
                    claimed_intake_receipt_reference=receipt,
                )
            else:
                result = service.admit(_envelope(index, invalid=expected == "REJECTED"))
                if result.state == "ACCEPTED_AS_MATERIAL":
                    accepted_bindings.append(
                        (
                            index,
                            result.admission_id,
                            result.intake_receipt_reference,
                        )
                    )
            latencies.append(time.perf_counter() - operation_started)
            states[result.state] = states.get(result.state, 0) + 1
        except TelemetryAdmissionError as exc:
            errors[exc.reason_code] = errors.get(exc.reason_code, 0) + 1
        index += 1
        now = time.monotonic()
        if now >= next_integrity:
            report = store.integrity_report()
            integrity_checks.append(
                {
                    "elapsed_seconds": round(time.perf_counter() - started_wall, 6),
                    "status": report["status"],
                    "counts": report["counts"],
                }
            )
            next_integrity = now + integrity_interval_seconds
        if interval:
            remaining = operation_started + interval - time.perf_counter()
            if remaining > 0:
                time.sleep(remaining)
    metrics = _run_metrics(started_wall, started_cpu, python_allocation_tracing=True)
    tracemalloc.stop()
    final = store.integrity_report()
    return {
        **_base_result(
            "TA-P005",
            {
                "duration_seconds": duration_seconds,
                "target_operations_per_second": target_rate,
                "integrity_interval_seconds": integrity_interval_seconds,
                "mix_cycle": list(cycle),
            },
        ),
        "measurements": {
            **metrics,
            **_latencies(latencies),
            **_file_sizes(path),
            "operations": len(latencies),
            "states": states,
            "errors": errors,
            "integrity_checks": integrity_checks,
            "final_integrity": final,
            "store_counts": store.counts(),
        },
    }


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def main() -> int:
    contract = _contract()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=tuple(contract["workloads"]))
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--count", type=int)
    parser.add_argument("--originals", type=int)
    parser.add_argument("--retries", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--rate", type=float)
    parser.add_argument("--backups", type=int)
    parser.add_argument("--integrity-interval", type=float)
    parser.add_argument(
        "--output",
        type=Path,
        help="create one private JSON result artifact; existing paths are rejected",
    )
    args = parser.parse_args()
    if args.output is not None:
        try:
            _result_artifact_target(args.output)
        except (
            FileExistsError,
            NotADirectoryError,
            FileNotFoundError,
            OSError,
        ) as error:
            print(
                json.dumps(
                    {
                        "status": "FAIL",
                        "error_code": "RESULT_ARTIFACT_TARGET_REJECTED",
                        "error_class": type(error).__name__,
                        "message": str(error),
                        "workload_started": False,
                        "authority_effects": _authority_effects(),
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 2
    workload = contract["workloads"][args.scenario]
    execution_binding = _start_execution_binding()
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.work_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="dbos-ta-characterization-")
        directory = Path(temporary.name)
    else:
        directory = args.work_dir.resolve()
        directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        if args.scenario == "TA-P001":
            result = characterize_p001(
                directory, args.count or workload["unique_admissions"]
            )
        elif args.scenario == "TA-P002":
            result = characterize_p002(
                directory,
                args.originals or workload["original_admissions"],
                args.retries or workload["confirmed_retries"],
            )
        elif args.scenario == "TA-P003":
            result = characterize_p003(
                directory,
                args.workers or workload["workers"],
                args.duration or workload["duration_seconds"],
                args.rate or workload["target_operations_per_second"],
            )
        elif args.scenario == "TA-P004":
            result = characterize_p004(
                directory,
                args.count or workload["unique_admissions"],
                args.backups or workload["backup_count"],
            )
        else:
            result = characterize_p005(
                directory,
                args.duration or workload["duration_seconds"],
                args.rate or workload["target_operations_per_second"],
                args.integrity_interval or workload["integrity_interval_seconds"],
            )
        result["execution_binding"] = _finish_execution_binding(execution_binding)
        integrity = result["measurements"].get(
            "integrity", result["measurements"].get("final_integrity")
        )
        valid = bool(
            integrity
            and integrity["status"] == "PASS"
            and result["execution_binding"]["binding_result"] == "PASS"
        )
        if args.output is None:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            receipt = write_result_artifact(args.output, result)
            print(
                json.dumps(
                    {
                        "case_id": result["case_id"],
                        "integrity_status": integrity["status"] if integrity else None,
                        "source_binding_result": result["execution_binding"][
                            "binding_result"
                        ],
                        "result_artifact": receipt,
                        "authority_effects": result["authority_effects"],
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
        return 0 if valid else 1
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
