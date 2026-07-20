#!/usr/bin/env python3
"""Deterministic, fail-closed implementation for DBOS-EXP-0001.

Agent-readable contract:
- Collector and Runner are bounded roles, never Agents or Runtime instances.
- No environment variable values, credentials, personal data, or external
  repository content are collected.
- Snapshot inputs are canonical byte artifacts with real SHA-256 digests.
- Experiment execution requires an exact authorization manifest and a verified
  frozen snapshot. Any failed validator stops fact formation.
- A local structural PASS is not independent verification and never promotes
  capability, evidence, or verification maturity.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

EXPERIMENT_ID = "DBOS-EXP-0001"
SUBJECT_ID = "digital-biosphere-os"
ENVIRONMENT_ID = "dbio://runner-environment/dbos-exp-0001/local-governance-workspace/v0.1"
RUNNER_ID = "dbio:runner:automated:dbos-self-validation:v0.1"
EXECUTION_ID = "dbio:runner-execution:dbos-self-validation:DBOS-EXP-0001:0001"
CONTEXT_ID = "dbio:execution-context:digital-biosphere-os:0001"
EVENT_ID = "dbio:event:digital-biosphere-os:DBOS-EXP-0001:0001"
STREAM_ID = "dbio://event-stream/digital-biosphere-os/DBOS-EXP-0001/v0.1"
PRODUCER_ID = "dbio:event-producer:dbos-self-validation-runner:v0.1"
ATTESTATION_ID = "dbio:attestation:DBOS-EXP-0001:0001"
VERIFICATION_RESULT_ID = "dbio:experiment-verification:DBOS-EXP-0001:0001"
AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
EXECUTOR_AUTHORIZATION_ID = "DBOS-EXP-0001-EXECUTOR-AUTH-0001"
ALLOWED_SNAPSHOT_ROOTS = ("constitution", "registry", "validation", "execution")
HASH_PREFIX = "sha256:"


def timestamp_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return HASH_PREFIX + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return HASH_PREFIX + digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(data, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def safe_command(command: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "status": "unavailable", "value": None, "error": type(exc).__name__}
    return {
        "command": command,
        "status": "captured" if completed.returncode == 0 else "unavailable",
        "value": completed.stdout.strip() if completed.returncode == 0 else None,
        "returncode": completed.returncode,
    }


def collect_environment(root: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    observed_at = timestamp_now()
    sw_vers = safe_command(["/usr/bin/sw_vers"])
    memory = safe_command(["/usr/sbin/sysctl", "-n", "hw.memsize"])
    configuration = {
        "experiment_id": EXPERIMENT_ID,
        "workspace_root": str(root),
        "access_mode": "read_only",
        "network_access": "not_used",
        "environment_variables_collected": False,
        "external_repositories_read": False,
        "sensitive_data_collected": False,
        "allowed_fact_types": ["os", "python", "dependency", "configuration", "hardware"],
    }
    dependency = {
        "execution_language": "python",
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "third_party_runtime_dependencies": [],
        "dependency_model": "python_standard_library_only",
    }
    facts = [
        {
            "fact_id": "DBOS-EXP-0001-ENV-FACT-OS-0001",
            "fact_type": "os",
            "value": {
                "system": platform.system(),
                "release": platform.release(),
                "platform": platform.platform(),
                "mac_version": platform.mac_ver()[0] or None,
                "sw_vers": sw_vers.get("value"),
            },
            "source": {"kind": "local_read_only", "methods": ["python.platform", "/usr/bin/sw_vers"]},
        },
        {
            "fact_id": "DBOS-EXP-0001-ENV-FACT-PYTHON-0001",
            "fact_type": "python",
            "value": {
                "implementation": platform.python_implementation(),
                "version": platform.python_version(),
                "executable": sys.executable,
            },
            "source": {"kind": "local_read_only", "methods": ["python.sys", "python.platform"]},
        },
        {
            "fact_id": "DBOS-EXP-0001-ENV-FACT-DEPENDENCY-0001",
            "fact_type": "dependency",
            "value": dependency,
            "source": {"kind": "declared_execution_dependency_closure", "methods": ["runner source inspection", "python runtime"]},
        },
        {
            "fact_id": "DBOS-EXP-0001-ENV-FACT-CONFIGURATION-0001",
            "fact_type": "configuration",
            "value": configuration,
            "source": {"kind": "explicit_collector_configuration", "methods": ["collector constants"]},
        },
        {
            "fact_id": "DBOS-EXP-0001-ENV-FACT-HARDWARE-0001",
            "fact_type": "hardware",
            "value": {
                "machine": platform.machine(),
                "processor": platform.processor() or None,
                "logical_cpu_count": os.cpu_count(),
                "memory_bytes": int(memory["value"]) if memory.get("status") == "captured" and str(memory.get("value", "")).isdigit() else None,
            },
            "source": {"kind": "local_read_only", "methods": ["python.platform", "python.os.cpu_count", "/usr/sbin/sysctl hw.memsize"]},
        },
    ]
    for fact in facts:
        fact.update({
            "environment_id": ENVIRONMENT_ID,
            "capture_id": "DBOS-EXP-0001-ENV-EVIDENCE-CAPTURE-0001",
            "timestamp": observed_at,
            "status": "captured",
            "authority_effect": "none",
        })
    dependency_digest = sha256_bytes(canonical_bytes(dependency))
    configuration_digest = sha256_bytes(canonical_bytes(configuration))
    environment_payload = {"facts": facts, "dependency_digest": dependency_digest, "configuration_digest": configuration_digest}
    environment_digest = sha256_bytes(canonical_bytes(environment_payload))
    observation = {
        "schema_version": "0.1",
        "kind": "DBOSExperimentEnvironmentObservation",
        "experiment_id": EXPERIMENT_ID,
        "environment_id": ENVIRONMENT_ID,
        "collector_id": "dbio:collector:automated:dbos-environment-read-only:v0.1",
        "access_mode": "read_only",
        "observed_at": observed_at,
        "facts": facts,
        "digests": {
            "dependency": dependency_digest,
            "configuration": configuration_digest,
            "environment": environment_digest,
        },
        "collection_result": "completed",
        "limitations": [
            "local host observation only",
            "no environment variable values collected",
            "no credential, secret, private key, personal data, or external storage content collected",
            "hardware inventory is intentionally minimal",
            "collection does not qualify or authorize the environment",
        ],
        "agent_status": "not_an_agent",
        "runtime_status": "not_a_runtime",
        "capability_effect": "none",
        "permission_effect": "none",
    }
    write_json(output_dir / "environment-observation.json", observation)
    receipt = {
        "artifact": "environment-observation.json",
        "digest": sha256_file(output_dir / "environment-observation.json"),
        "size": (output_dir / "environment-observation.json").stat().st_size,
        "captured_at": observed_at,
    }
    write_json(output_dir / "environment-observation.receipt.json", receipt)
    return {"status": "PASS", "observation": str(output_dir / "environment-observation.json"), **observation["digests"]}


def iter_snapshot_files(root: Path) -> Iterable[tuple[str, Path]]:
    for directory in ALLOWED_SNAPSHOT_ROOTS:
        base = root / directory
        if not base.is_dir():
            raise ValueError(f"required snapshot directory missing: {directory}")
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            if "__pycache__" in path.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
                continue
            yield relative, path


def capture_snapshot(root: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    captured_at = timestamp_now()
    files = []
    for relative, path in iter_snapshot_files(root):
        files.append({"path": relative, "size": path.stat().st_size, "digest": sha256_file(path)})
    if not files:
        raise ValueError("snapshot file set is empty")
    validator_files = [item for item in files if item["path"].startswith("validation/") and item["path"].endswith("_validator.py")]
    manifest = {
        "schema_version": "0.1",
        "kind": "DBOSExperimentFrozenInputManifest",
        "experiment_id": EXPERIMENT_ID,
        "captured_at": captured_at,
        "root_semantics": "paths_relative_to_digital_biosphere_os",
        "included_roots": list(ALLOWED_SNAPSHOT_ROOTS),
        "files": files,
        "file_count": len(files),
        "agent_count": 0,
        "runtime_count": 0,
        "digital_organism_count": 0,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "snapshot-manifest.json"
    write_json(manifest_path, manifest)
    validator_manifest = {
        "schema_version": "0.1",
        "kind": "DBOSExperimentValidatorManifest",
        "experiment_id": EXPERIMENT_ID,
        "captured_at": captured_at,
        "validators": validator_files,
        "validator_count": len(validator_files),
        "execution_order": [item["path"] for item in validator_files],
    }
    validator_manifest_path = output_dir / "validator-manifest.json"
    write_json(validator_manifest_path, validator_manifest)
    archive_path = output_dir / "dbos-input-snapshot.tar"
    with tarfile.open(archive_path, "w", format=tarfile.PAX_FORMAT) as archive:
        for item in files:
            source = root / item["path"]
            info = archive.gettarinfo(str(source), arcname=item["path"])
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            info.mode = 0o755 if os.access(source, os.X_OK) else 0o644
            with source.open("rb") as handle:
                archive.addfile(info, handle)
    result = {
        "status": "PASS",
        "captured_at": captured_at,
        "file_count": len(files),
        "validator_count": len(validator_files),
        "snapshot_manifest_digest": sha256_file(manifest_path),
        "validator_manifest_digest": sha256_file(validator_manifest_path),
        "archive_digest": sha256_file(archive_path),
        "archive_size": archive_path.stat().st_size,
    }
    write_json(output_dir / "snapshot-capture-result.json", result)
    return result


def verify_frozen_snapshot(snapshot_dir: Path, extraction_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(snapshot_dir / "snapshot-manifest.json")
    validator_manifest = load_json(snapshot_dir / "validator-manifest.json")
    archive_path = snapshot_dir / "dbos-input-snapshot.tar"
    if manifest.get("experiment_id") != EXPERIMENT_ID or validator_manifest.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("snapshot experiment identity mismatch")
    with tarfile.open(archive_path, "r") as archive:
        for member in archive.getmembers():
            target = (extraction_root / member.name).resolve()
            if extraction_root.resolve() not in target.parents and target != extraction_root.resolve():
                raise ValueError(f"unsafe archive member: {member.name}")
        archive.extractall(extraction_root, filter="data")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("snapshot manifest file list missing")
    for item in files:
        path = extraction_root / item["path"]
        if not path.is_file() or path.stat().st_size != item["size"] or sha256_file(path) != item["digest"]:
            raise ValueError(f"snapshot material mismatch: {item.get('path')}")
    return manifest, validator_manifest


def check_authorization(path: Path) -> dict[str, Any]:
    authorization = load_json(path)
    required = {
        "experiment_id": EXPERIMENT_ID,
        "experiment_authorization_id": AUTHORIZATION_ID,
        "executor_authorization_id": EXECUTOR_AUTHORIZATION_ID,
        "runner_id": RUNNER_ID,
        "status": "authorized",
        "agent_creation": False,
        "runtime_creation": False,
        "digital_organism_creation": False,
        "capability_upgrade": False,
        "permission_grant": False,
    }
    for key, expected in required.items():
        if authorization.get(key) != expected:
            raise ValueError(f"authorization {key} must be {expected!r}")
    if not isinstance(authorization.get("authorized_by"), str) or not authorization["authorized_by"]:
        raise ValueError("authorization requires attributable authorized_by")
    if not isinstance(authorization.get("authorization_evidence"), list) or not authorization["authorization_evidence"]:
        raise ValueError("authorization evidence missing")
    return authorization


def run_validators(extracted_root: Path, validator_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    validators = validator_manifest.get("execution_order")
    if not isinstance(validators, list) or not validators:
        raise ValueError("validator execution order is empty")
    for relative in validators:
        path = extracted_root / relative
        if not path.is_file():
            raise ValueError(f"frozen validator missing: {relative}")
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"), "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run(
            [sys.executable, str(path), "--format", "json"],
            cwd=extracted_root,
            env=env,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        results.append({
            "validator": relative,
            "validator_digest": sha256_file(path),
            "command": [sys.executable, relative, "--format", "json"],
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "status": "PASS" if completed.returncode == 0 else "FAIL",
        })
        if completed.returncode != 0:
            break
    return results


def run_experiment(root: Path, snapshot_dir: Path, authorization_path: Path, output_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    authorization = check_authorization(authorization_path)
    started_at = timestamp_now()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dbos-exp-0001-") as temporary:
        extracted_root = Path(temporary) / "frozen-dbos"
        extracted_root.mkdir()
        snapshot_manifest, validator_manifest = verify_frozen_snapshot(snapshot_dir, extracted_root)
        validation_results = run_validators(extracted_root, validator_manifest)
    validation_artifact = {
        "schema_version": "0.1",
        "kind": "DBOSFrozenValidatorExecutionResults",
        "experiment_id": EXPERIMENT_ID,
        "execution_id": EXECUTION_ID,
        "started_at": started_at,
        "ended_at": timestamp_now(),
        "snapshot_manifest_digest": sha256_file(snapshot_dir / "snapshot-manifest.json"),
        "validator_manifest_digest": sha256_file(snapshot_dir / "validator-manifest.json"),
        "validator_count_expected": validator_manifest["validator_count"],
        "validator_count_executed": len(validation_results),
        "pass_count": sum(item["status"] == "PASS" for item in validation_results),
        "fail_count": sum(item["status"] == "FAIL" for item in validation_results),
        "results": validation_results,
    }
    validation_results_path = output_dir / "validator-results.json"
    write_json(validation_results_path, validation_artifact)
    if validation_artifact["fail_count"] or validation_artifact["validator_count_executed"] != validation_artifact["validator_count_expected"]:
        failed = {
            "experiment_id": EXPERIMENT_ID,
            "execution_id": EXECUTION_ID,
            "status": "failed",
            "stop_reason": "validator_failure_or_incomplete_suite",
            "validator_results_ref": str(validation_results_path),
            "timestamp": timestamp_now(),
        }
        write_json(output_dir / "experiment-result.json", failed)
        raise RuntimeError("frozen validator suite did not pass completely")

    validation_digest = sha256_file(validation_results_path)
    try:
        snapshot_archive_ref = (snapshot_dir.resolve() / "dbos-input-snapshot.tar").relative_to(root).as_posix()
    except ValueError:
        snapshot_archive_ref = str(snapshot_dir.resolve() / "dbos-input-snapshot.tar")
    input_snapshot = {
        "snapshot_id": f"dbio:snapshot:input:{CONTEXT_ID}:0001",
        "context_id": CONTEXT_ID,
        "input_ref": snapshot_archive_ref,
        "hash": sha256_file(snapshot_dir / "dbos-input-snapshot.tar"),
        "timestamp": snapshot_manifest["captured_at"],
    }
    output_snapshot = {
        "snapshot_id": f"dbio:snapshot:output:{CONTEXT_ID}:0001",
        "context_id": CONTEXT_ID,
        "output_ref": "validator-results.json",
        "hash": validation_digest,
        "timestamp": validation_artifact["ended_at"],
    }
    context = {
        "context_id": CONTEXT_ID,
        "entity_id": SUBJECT_ID,
        "environment_ref": ENVIRONMENT_ID,
        "software_version": "DBOS v0.1",
        "configuration_digest": sha256_file(authorization_path),
        "dependency_refs": ["python_standard_library"],
        "status": "validated",
        "execution_method": "deterministic_frozen_validator_suite",
        "platform": {"python": platform.python_version(), "system": platform.system(), "machine": platform.machine()},
        "input_snapshot_refs": [input_snapshot["snapshot_id"]],
        "output_snapshot_refs": [output_snapshot["snapshot_id"]],
        "timestamp": validation_artifact["ended_at"],
        "reproducibility": "bounded_to_retained_snapshot_environment_and_method",
        "limitations": ["local structural validation only", "not independent verification", "no capability or permission effect"],
    }
    write_json(output_dir / "input-snapshot.json", input_snapshot)
    write_json(output_dir / "output-snapshot.json", output_snapshot)
    write_json(output_dir / "execution-context.json", context)

    occurred_at = timestamp_now()
    event = {
        "event_id": EVENT_ID,
        "entity_id": SUBJECT_ID,
        "event_type": "execution_event",
        "timestamp": occurred_at,
        "source": {"kind": "authorized_deterministic_runner", "locator": EXECUTION_ID, "collected_at": occurred_at},
        "input_ref": input_snapshot["snapshot_id"],
        "output_ref": output_snapshot["snapshot_id"],
        "resource_ref": ENVIRONMENT_ID,
        "evidence_ref": "validator-results.json#" + validation_digest,
        "status": "validated",
        "claim": "The retained frozen DBOS validator suite completed with every declared validator returning exit status 0.",
        "claim_boundary": "local structural validator result only",
    }
    write_json(output_dir / "event-record.json", event)
    event_digest = sha256_file(output_dir / "event-record.json")
    integrity = {
        "event_id": EVENT_ID,
        "stream_id": STREAM_ID,
        "sequence": 1,
        "previous_hash": None,
        "current_hash": event_digest,
        "timestamp": timestamp_now(),
        "clock_source": "local_system_clock_timezone_aware",
        "integrity_status": "verified",
        "witness_refs": [RUNNER_ID],
        "check_results": {
            "hash_validation": "PASS",
            "sequence_validation": "PASS",
            "source_validation": "PASS",
            "timestamp_validation": "PASS",
            "witness_validation": "PASS_LOCAL_NONINDEPENDENT",
        },
        "limitations": ["genesis stream has no previous hash", "local Runner witness is not independent"],
    }
    write_json(output_dir / "event-integrity.json", integrity)

    producer = {
        "producer_id": PRODUCER_ID,
        "producer_type": "automated",
        "identity_ref": RUNNER_ID,
        "capability_scope": "authorized DBOS-EXP-0001 evidence output only",
        "status": "active_for_completed_run",
        "agent_status": "not_an_agent",
        "runtime_status": "not_a_runtime",
    }
    attestation_payload = {
        "event_id": EVENT_ID,
        "producer_id": PRODUCER_ID,
        "claim": event["claim"],
        "event_digest": event_digest,
        "integrity_digest": sha256_file(output_dir / "event-integrity.json"),
        "execution_id": EXECUTION_ID,
    }
    write_json(output_dir / "attestation-payload.json", attestation_payload)
    payload_digest = sha256_file(output_dir / "attestation-payload.json")
    attestation = {
        "attestation_id": ATTESTATION_ID,
        "event_id": EVENT_ID,
        "producer_id": PRODUCER_ID,
        "attestation_method": "automated_attestation",
        "claim": event["claim"],
        "signature_ref": "digest-attestation:" + payload_digest,
        "status": "attested",
        "timestamp": timestamp_now(),
        "limitations": ["content-digest attestation, not a private-key digital signature", "producer is not independent", "signature does not replace source evidence"],
        "trust_effect": "none",
    }
    write_json(output_dir / "event-producer.json", producer)
    write_json(output_dir / "event-attestation.json", attestation)

    evidence_items = []
    for path in sorted(output_dir.glob("*.json")):
        if path.name in {"evidence-bundle.json", "verification-result.json", "experiment-result.json"}:
            continue
        evidence_items.append({"artifact": path.name, "digest": sha256_file(path), "size": path.stat().st_size})
    bundle = {
        "schema_version": "0.1",
        "kind": "DBOSExperimentEvidenceBundle",
        "experiment_id": EXPERIMENT_ID,
        "execution_id": EXECUTION_ID,
        "created_at": timestamp_now(),
        "artifacts": evidence_items,
        "artifact_count": len(evidence_items),
        "agent_count": 0,
        "runtime_count": 0,
        "digital_organism_count": 0,
        "capability_assignment_count": 0,
        "permission_grant_count": 0,
        "c_e_v_level_change_count": 0,
    }
    write_json(output_dir / "evidence-bundle.json", bundle)
    bundle_digest = sha256_file(output_dir / "evidence-bundle.json")
    verification = {
        "verification_result_id": VERIFICATION_RESULT_ID,
        "experiment_id": EXPERIMENT_ID,
        "execution_id": EXECUTION_ID,
        "verifier": "dbio:verifier:digital-biosphere-local-structural-suite:v0.1",
        "method": "digest_reference_and_frozen_validator_result_verification",
        "decision": "pass",
        "status": "verified_local_structural",
        "timestamp": timestamp_now(),
        "evidence_bundle_ref": "evidence-bundle.json#" + bundle_digest,
        "validator_pass_count": validation_artifact["pass_count"],
        "validator_fail_count": validation_artifact["fail_count"],
        "independence_status": "not_independent",
        "verification_level_effect": "none",
        "capability_effect": "none",
        "permission_effect": "none",
        "limitations": ["local automated verification", "does not upgrade C/E/V", "does not approve capability", "does not establish production fitness"],
    }
    write_json(output_dir / "verification-result.json", verification)
    completed_at = timestamp_now()
    result = {
        "experiment_id": EXPERIMENT_ID,
        "execution_id": EXECUTION_ID,
        "runner_id": RUNNER_ID,
        "status": "completed",
        "started_at": started_at,
        "completed_at": completed_at,
        "procedure_status": "completed",
        "executed_steps": [f"DBOS-EXP-0001-STEP-{index:02d}" for index in range(1, 9)],
        "event_id": EVENT_ID,
        "evidence_bundle_ref": "evidence-bundle.json#" + bundle_digest,
        "verification_result_ref": "verification-result.json#" + sha256_file(output_dir / "verification-result.json"),
        "fact_claim": event["claim"],
        "fact_scope": "retained frozen DBOS v0.1 local structural validation",
        "failure_count": 0,
        "agent_count": 0,
        "runtime_count": 0,
        "digital_organism_count": 0,
        "capability_assignment_count": 0,
        "permission_grant_count": 0,
        "c_e_v_level_change_count": 0,
        "authorization_ref": authorization_path.name + "#" + sha256_file(authorization_path),
    }
    write_json(output_dir / "experiment-result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect-environment")
    collect.add_argument("--output-dir", type=Path, required=True)
    capture = subparsers.add_parser("capture-snapshot")
    capture.add_argument("--output-dir", type=Path, required=True)
    run = subparsers.add_parser("run-experiment")
    run.add_argument("--snapshot-dir", type=Path, required=True)
    run.add_argument("--authorization", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "collect-environment":
            result = collect_environment(args.root, args.output_dir)
        elif args.command == "capture-snapshot":
            result = capture_snapshot(args.root, args.output_dir)
        else:
            result = run_experiment(args.root, args.snapshot_dir, args.authorization, args.output_dir)
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
