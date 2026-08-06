#!/usr/bin/env python3
"""Validate DBOS-EXP-0001 phase gates and the completed fact chain.

This validator is the post-baseline, agent-readable truth surface for the
experiment. It recomputes retained digests and follows references; it never
creates identity, evidence, authorization, events, capability, permission, an
Agent, a Runtime instance, or a Digital Organism.

After the execution chain is complete, historical subject-identity bytes are
checked through their retained append-only manifest bindings. A later working
tree is allowed to differ, but that drift is reported explicitly and is never
treated as the historical bytes. Before completion, the current path must still
match the declared identity digest exactly.

PASS is phase-scoped. In particular, a local structural PASS is not an
independent verification, capability approval, permission grant, production
fitness claim, or evidence/verification maturity promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
SUBJECT_ID = "digital-biosphere-os"
ENVIRONMENT_ID = "dbio://runner-environment/dbos-exp-0001/local-governance-workspace/v0.1"
RUNNER_ID = "dbio:runner:automated:dbos-self-validation:v0.1"
EXECUTION_ID = "dbio:runner-execution:dbos-self-validation:DBOS-EXP-0001:0002"
EVENT_ID = "dbio:event:digital-biosphere-os:DBOS-EXP-0001:0001"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
PHASES = ("environment", "freeze", "runner", "authorization", "completed")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def valid_time(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def records(document: dict[str, Any], field: str, identifier: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    value = document.get(field)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{field}[{index}] must be a mapping")
            continue
        key = item.get(identifier)
        if not isinstance(key, str) or not key:
            errors.append(f"{field}[{index}].{identifier} missing")
        elif key in result:
            errors.append(f"duplicate {identifier}: {key}")
        else:
            result[key] = item
    return result


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_zero_boundaries(root: Path, errors: list[str]) -> None:
    entities = load(root / "registry/entities.yaml").get("entities", [])
    require(isinstance(entities, list) and sum(isinstance(item, dict) and item.get("entity_type") == "agent" for item in entities) == 0, "Agent count must remain zero", errors)
    require(load(root / "registry/runtime-instances.yaml").get("runtime_instances") == [], "Runtime instance count must remain zero", errors)
    require(load(root / "registry/organism-candidates.yaml").get("organism_candidates") == [], "Organism candidate count must remain zero", errors)
    require(load(root / "registry/capabilities.yaml").get("capabilities") == [], "Capability registry must remain empty", errors)
    claims = load(root / "registry/capability-claims.yaml").get("claims", [])
    evidence = load(root / "registry/capability-evidence.yaml").get("evidence", [])
    verifications = load(root / "registry/verification-records.yaml").get("verification_records", [])
    require(len(claims) == 78 and all(item.get("status") == "pending" and item.get("maturity_level") == "C1" for item in claims), "78 capability claims must remain pending C1", errors)
    require(len(evidence) == 78 and all(item.get("status") == "pending" and item.get("evidence_type") == "E1" for item in evidence), "78 capability evidence records must remain pending E1", errors)
    require(len(verifications) == 78 and all(item.get("status") == "pending" and item.get("decision") == "pending" and item.get("verification_level") == "V0" for item in verifications), "78 verification records must remain pending V0", errors)


def retained_identity_binding_exists(
    evidence_root: Path,
    relative_path: str,
    expected_digest: str,
    expected_size: int,
) -> bool:
    """Find an append-only run manifest that preserves one historical binding.

    This checks record continuity only. It does not claim that a mutable current
    path still contains the historical bytes or that the recorded content is
    independently true.
    """
    for manifest_path in sorted(evidence_root.glob("*/auxiliary-input-manifest.json")):
        try:
            manifest = load(manifest_path)
        except ValueError:
            continue
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list):
            continue
        if any(
            isinstance(artifact, dict)
            and artifact.get("path") == relative_path
            and artifact.get("digest") == expected_digest
            and artifact.get("size") == expected_size
            for artifact in artifacts
        ):
            return True
    return False


def validate_subject_identity_evidence(
    root: Path,
    evidence_root: Path,
    identity: dict[str, Any],
    phase: str,
    errors: list[str],
    warnings: list[str],
) -> int:
    """Validate identity bindings without confusing history with the worktree."""
    drift_count = 0
    evidence_items = identity.get("evidence")
    if not isinstance(evidence_items, list) or not evidence_items:
        errors.append("subject identity evidence must contain retained evidence bindings")
        return drift_count

    for index, item in enumerate(evidence_items):
        label = f"subject identity evidence[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be a mapping")
            continue
        relative_path = item.get("path")
        expected_sha256 = item.get("sha256")
        expected_size = item.get("size")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(f"{label}.path must be a non-empty string")
            continue
        expected_digest = f"sha256:{expected_sha256}"
        require(HASH_RE.fullmatch(expected_digest) is not None, f"{label}.sha256 is invalid", errors)
        require(
            isinstance(expected_size, int) and not isinstance(expected_size, bool) and expected_size >= 0,
            f"{label}.size must be a non-negative integer",
            errors,
        )
        if HASH_RE.fullmatch(expected_digest) is None or not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
            continue

        current_path = root / relative_path
        current_matches = (
            current_path.is_file()
            and current_path.stat().st_size == expected_size
            and digest_file(current_path) == expected_digest
        )
        if current_matches:
            continue

        if phase != "completed":
            require(current_path.is_file(), f"identity evidence path missing: {relative_path}", errors)
            if current_path.is_file():
                require(current_path.stat().st_size == expected_size, f"identity evidence size mismatch: {relative_path}", errors)
                require(digest_file(current_path) == expected_digest, f"identity evidence digest mismatch: {relative_path}", errors)
            continue

        require(
            retained_identity_binding_exists(
                evidence_root,
                relative_path,
                expected_digest,
                expected_size,
            ),
            f"completed identity evidence has no retained manifest binding: {relative_path}",
            errors,
        )
        drift_count += 1
        warnings.append(
            "current workspace differs from retained historical identity binding: "
            f"{relative_path}; historical digest was not rewritten"
        )
    return drift_count


def validate_environment(
    root: Path,
    phase: str,
    errors: list[str],
    warnings: list[str],
) -> int:
    evidence_root = root / "evidence/experiments/DBOS-EXP-0001"
    identity_path = evidence_root / "identity/subject-identity-evidence.json"
    observation_path = evidence_root / "environment/environment-observation.json"
    receipt_path = evidence_root / "environment/environment-observation.receipt.json"
    identity = load(identity_path)
    require(identity.get("subject_id") == "DBOS-SUBJECT-0001" and identity.get("entity_id") == SUBJECT_ID, "bounded subject identity evidence mismatch", errors)
    identity_drift_count = validate_subject_identity_evidence(
        root,
        evidence_root,
        identity,
        phase,
        errors,
        warnings,
    )
    subjects = records(load(root / "registry/experiment-subjects.yaml"), "experiment_subjects", "subject_id", errors)
    subject = subjects.get("DBOS-SUBJECT-0001", {})
    require(subject.get("identity_status") == "verified" and subject.get("evidence_ref") == identity_path.relative_to(root).as_posix(), "experiment subject must be evidence-backed verified", errors)

    observation = load(observation_path)
    receipt = load(receipt_path)
    require(observation.get("collection_result") == "completed" and observation.get("access_mode") == "read_only", "environment observation must be completed read_only", errors)
    require(observation.get("environment_id") == ENVIRONMENT_ID and valid_time(observation.get("observed_at")), "environment observation identity or timestamp invalid", errors)
    require(receipt.get("digest") == digest_file(observation_path) and receipt.get("size") == observation_path.stat().st_size, "environment observation receipt mismatch", errors)
    fact_list = observation.get("facts")
    require(isinstance(fact_list, list) and len(fact_list) == 5, "environment observation must retain five facts", errors)
    if isinstance(fact_list, list) and len(fact_list) == 5:
        require({item.get("fact_type") for item in fact_list} == {"os", "python", "dependency", "configuration", "hardware"}, "environment fact type set mismatch", errors)
        dependency = next((item.get("value") for item in fact_list if item.get("fact_type") == "dependency"), None)
        configuration = next((item.get("value") for item in fact_list if item.get("fact_type") == "configuration"), None)
        require(observation.get("digests", {}).get("dependency") == digest_bytes(canonical_bytes(dependency)), "dependency digest mismatch", errors)
        require(observation.get("digests", {}).get("configuration") == digest_bytes(canonical_bytes(configuration)), "configuration digest mismatch", errors)
        payload = {"facts": fact_list, "dependency_digest": observation["digests"]["dependency"], "configuration_digest": observation["digests"]["configuration"]}
        require(observation.get("digests", {}).get("environment") == digest_bytes(canonical_bytes(payload)), "environment digest mismatch", errors)

    collectors = records(load(root / "registry/environment-collectors.yaml"), "environment_collectors", "collector_id", errors)
    collector = collectors.get("dbio:collector:automated:dbos-environment-read-only:v0.1", {})
    require(collector.get("collector_type") == "automated" and collector.get("access_mode") == "read_only" and collector.get("status") == "active", "active automated read-only collector missing", errors)
    require(collector.get("implementation_digest") == "sha256:3ece45ca3bba89e2628d0351cb8bd2032e2f709e88db3566a57897e9a68da6ed", "collector implementation digest must preserve the executed v0.1 bytes", errors)
    scopes = records(load(root / "registry/collector-scopes.yaml"), "collector_scopes", "scope_id", errors)
    scope = scopes.get("DBOS-EXP-0001-ENV-COLLECTOR-SCOPE-0001", {})
    require(scope.get("collector_id") in collectors and scope.get("status") == "approved" and ENVIRONMENT_ID in scope.get("environment_refs", []), "approved collector scope missing", errors)
    require(set(scope.get("excluded_data", [])) >= {"credential", "secret", "private_key", "personal_data", "external_storage_content"}, "collector privacy exclusions incomplete", errors)
    require(set(scope.get("allowed_facts", [])) == {"operating_system", "python_version", "dependency_information", "configuration_information", "hardware_information"}, "collector fact scope mismatch", errors)
    runs = records(load(root / "registry/collector-runs.yaml"), "collector_runs", "run_id", errors)
    run = runs.get("DBOS-EXP-0001-ENV-COLLECTOR-RUN-0001", {})
    require(run.get("status") == "completed" and run.get("collector_id") in collectors and run.get("scope_ref") in scopes, "completed collector run missing", errors)
    require(run.get("side_effects") == ["created_new_experiment_evidence_artifacts_only"], "collector side effects must be exact and bounded", errors)
    facts = records(load(root / "registry/environment-facts.yaml"), "environment_facts", "fact_id", errors)
    digests = records(load(root / "registry/environment-digests.yaml"), "environment_digests", "digest_id", errors)
    require(len(facts) == 5 and len(digests) == 3, "environment fact or digest registry count mismatch", errors)
    digest_by_type = {item.get("digest_type"): item.get("hash_value") for item in digests.values()}
    require(digest_by_type == observation.get("digests"), "registered environment digests do not match observation", errors)
    captures = records(load(root / "registry/environment-evidence-captures.yaml"), "environment_evidence_captures", "capture_id", errors)
    capture = captures.get("DBOS-EXP-0001-ENV-EVIDENCE-CAPTURE-0001", {})
    require(capture.get("status") == "validated" and capture.get("collector_run_ref") in runs, "validated environment capture missing", errors)
    qualifications = records(load(root / "registry/environment-qualifications.yaml"), "environment_qualifications", "qualification_id", errors)
    qualification = qualifications.get("DBOS-EXP-0001-RUNNER-ENV-QUAL-0001", {})
    require(qualification.get("result") == "verified" and valid_time(qualification.get("timestamp")), "environment qualification must be verified", errors)
    criteria = qualification.get("criteria", [])
    require(len(criteria) == 6 and all(item.get("status") == "passed" and item.get("evidence_refs") for item in criteria), "every environment qualification criterion must pass with evidence", errors)
    locks = records(load(root / "registry/environment-locks.yaml"), "environment_locks", "lock_id", errors)
    lock = locks.get("DBOS-EXP-0001-ENV-LOCK-0001", {})
    require(lock.get("status") == "frozen" and valid_time(lock.get("locked_at")), "environment lock must be frozen", errors)
    require(lock.get("dependencies_digest") == observation["digests"]["dependency"] and lock.get("configuration_digest") == observation["digests"]["configuration"], "environment lock digests mismatch", errors)
    return identity_drift_count


def validate_freeze(root: Path, errors: list[str]) -> None:
    freeze_dir = root / "evidence/experiments/DBOS-EXP-0001/freeze"
    manifest_path = freeze_dir / "snapshot-manifest.json"
    validator_manifest_path = freeze_dir / "validator-manifest.json"
    archive_path = freeze_dir / "dbos-input-snapshot.tar"
    result_path = freeze_dir / "snapshot-capture-result.json"
    for path in (manifest_path, validator_manifest_path, archive_path, result_path):
        require(path.is_file(), f"freeze artifact missing: {path.relative_to(root)}", errors)
    if not all(path.is_file() for path in (manifest_path, validator_manifest_path, archive_path, result_path)):
        return
    manifest = load(manifest_path)
    validator_manifest = load(validator_manifest_path)
    capture_result = load(result_path)
    require(capture_result.get("archive_digest") == digest_file(archive_path), "frozen archive digest mismatch", errors)
    require(capture_result.get("snapshot_manifest_digest") == digest_file(manifest_path), "snapshot manifest digest mismatch", errors)
    require(capture_result.get("validator_manifest_digest") == digest_file(validator_manifest_path), "validator manifest digest mismatch", errors)
    require(manifest.get("file_count") == len(manifest.get("files", [])) and manifest.get("file_count", 0) > 0, "snapshot manifest file count invalid", errors)
    for item in manifest.get("files", []):
        source = root / item.get("path", "")
        require(source.is_file(), f"snapshot source path missing: {item.get('path')}", errors)
    snapshots = records(load(root / "registry/experiment-snapshots.yaml"), "experiment_snapshots", "snapshot_id", errors)
    snapshot = snapshots.get("DBOS-EXP-0001-SNAPSHOT-0001", {})
    require(snapshot.get("status") == "frozen" and snapshot.get("file_tree_hash") == capture_result["archive_digest"], "experiment snapshot not frozen against archive", errors)
    validator_manifests = records(load(root / "registry/validator-manifests.yaml"), "validator_manifests", "manifest_id", errors)
    registered = validator_manifests.get("DBOS-EXP-0001-VALIDATOR-MANIFEST-0001", {})
    require(registered.get("status") == "frozen" and registered.get("locked_digest") == capture_result["validator_manifest_digest"], "validator manifest not frozen", errors)
    freeze_manifests = records(load(root / "registry/freeze-manifests.yaml"), "freeze_manifests", "freeze_id", errors)
    require(freeze_manifests.get("DBOS-EXP-0001-FREEZE-0001", {}).get("status") == "frozen", "freeze manifest status must be frozen", errors)
    certificates = records(load(root / "registry/freeze-certificates.yaml"), "freeze_certificates", "certificate_id", errors)
    certificate = certificates.get("DBOS-EXP-0001-FREEZE-CERT-0001", {})
    require(certificate.get("status") == "issued" and valid_time(certificate.get("created_at")) and certificate.get("issuer") == "dbio:verifier:digital-biosphere-local-structural-suite:v0.1", "attributable freeze certificate missing", errors)

    successor_dir = root / "evidence/experiments/DBOS-EXP-0001/freeze-run-0004"
    successor_archive = successor_dir / "dbos-input-snapshot.tar"
    successor_snapshot_manifest = successor_dir / "snapshot-manifest.json"
    successor_validator_manifest = successor_dir / "validator-manifest.json"
    successor_certificate = successor_dir / "freeze-certificate-run-0002.json"
    preflight_path = root / "evidence/experiments/DBOS-EXP-0001/preflight-run-0007/preflight-results.json"
    for path in (successor_archive, successor_snapshot_manifest, successor_validator_manifest, successor_certificate, preflight_path):
        require(path.is_file(), f"successor freeze artifact missing: {path.relative_to(root)}", errors)
    if all(path.is_file() for path in (successor_archive, successor_snapshot_manifest, successor_validator_manifest, successor_certificate, preflight_path)):
        require(digest_file(successor_archive) == capture_result["archive_digest"], "successor freeze must retain the original snapshot archive bytes", errors)
        require(digest_file(successor_snapshot_manifest) == capture_result["snapshot_manifest_digest"], "successor freeze must retain the original snapshot manifest bytes", errors)
        require(digest_file(successor_validator_manifest) == "sha256:eaf15f54b80bba9ff2062e0f06de57fe42e6eb46c4fbb13e8d5a29c51fcbbf89", "successor validator manifest digest mismatch", errors)
        successor_certificate_value = load(successor_certificate)
        require(successor_certificate_value.get("status") == "issued" and successor_certificate_value.get("validator_manifest", {}).get("digest") == digest_file(successor_validator_manifest), "successor freeze certificate invalid", errors)
        preflight = load(preflight_path)
        require(preflight.get("status") == "PASS" and preflight.get("pass_count") == preflight.get("validator_count_expected") == preflight.get("validator_count_executed") == 29 and preflight.get("fail_count") == 0, "successor frozen suite preflight is not 29/29 PASS", errors)
    successor_registered = validator_manifests.get("DBOS-EXP-0001-VALIDATOR-MANIFEST-0002", {})
    require(successor_registered.get("status") == "frozen" and successor_registered.get("locked_digest") == "sha256:eaf15f54b80bba9ff2062e0f06de57fe42e6eb46c4fbb13e8d5a29c51fcbbf89", "successor validator manifest registry record invalid", errors)
    require(freeze_manifests.get("DBOS-EXP-0001-FREEZE-0002", {}).get("status") == "frozen", "successor freeze manifest status must be frozen", errors)
    require(certificates.get("DBOS-EXP-0001-FREEZE-CERT-0002", {}).get("status") == "issued", "successor freeze certificate registry record missing", errors)


def validate_runner(root: Path, errors: list[str]) -> None:
    identities = records(load(root / "registry/executor-identities.yaml"), "executor_identities", "executor_identity_id", errors)
    identity = identities.get("dbio:executor-identity:automated:dbos-self-validation:v0.1", {})
    require(identity.get("identity_type") == "automated" and identity.get("verification_status") == "verified" and identity.get("lifecycle_state") == "verified", "verified automated executor identity missing", errors)
    verifications = records(load(root / "registry/executor-verifications.yaml"), "executor_verifications", "verification_id", errors)
    require(any(item.get("executor_identity_id") in identities and item.get("result") == "verified" and valid_time(item.get("timestamp")) for item in verifications.values()), "executor identity verification missing", errors)
    executors = records(load(root / "registry/executors.yaml"), "executors", "executor_id", errors)
    executor = executors.get("dbio:executor:automated-runner:dbos-self-validation:v0.1", {})
    require(executor.get("identity_ref") in identities and executor.get("status") == "active", "active experiment executor missing", errors)
    runners = records(load(root / "registry/runners.yaml"), "runners", "runner_id", errors)
    runner = runners.get(RUNNER_ID, {})
    require(runner.get("runner_type") == "automated_runner" and runner.get("execution_mode") == "deterministic" and runner.get("status") in {"registered", "ready"} and runner.get("qualification_status") == "qualified", "qualified deterministic Runner missing", errors)
    require(runner.get("identity_ref") in identities and runner.get("executor_ref") in executors, "Runner identity or executor reference invalid", errors)
    require(runner.get("implementation_digest") == digest_file(root / "execution/dbos_exp_0001_runner.py"), "Runner implementation digest mismatch", errors)
    scopes = records(load(root / "registry/runner-scopes.yaml"), "runner_scopes", "scope_id", errors)
    scope = scopes.get("DBOS-EXP-0001-RUNNER-SCOPE-0001", {})
    require(scope.get("status") == "approved" and scope.get("runner_id") == RUNNER_ID and scope.get("allowed_experiments") == [EXPERIMENT_ID], "approved Runner scope missing", errors)


def validate_authorization(root: Path, errors: list[str]) -> None:
    authorization_path = root / "evidence/experiments/DBOS-EXP-0001/authorization/execution-authorization-v3.json"
    require(authorization_path.is_file(), "execution authorization evidence missing", errors)
    if not authorization_path.is_file():
        return
    authorization = load(authorization_path)
    require(authorization.get("status") == "authorized" and authorization.get("runner_id") == RUNNER_ID, "execution authorization evidence invalid", errors)
    require(authorization.get("agent_creation") is False and authorization.get("runtime_creation") is False and authorization.get("digital_organism_creation") is False, "authorization must prohibit subject creation", errors)
    require(authorization.get("capability_upgrade") is False and authorization.get("permission_grant") is False, "authorization cannot upgrade capability or grant permission", errors)
    authorizations = records(load(root / "registry/experiment-authorizations.yaml"), "experiment_authorizations", "authorization_id", errors)
    require(authorizations.get("DBOS-EXP-0001-AUTH-0001", {}).get("status") == "expired", "first experiment authorization must be exhausted by the failed attempt", errors)
    require(authorizations.get("DBOS-EXP-0001-AUTH-0002", {}).get("status") == "expired", "second experiment authorization must be exhausted by the completed execution", errors)
    executor_authorizations = records(load(root / "registry/executor-authorizations.yaml"), "executor_authorizations", "authorization_id", errors)
    require(executor_authorizations.get("DBOS-EXP-0001-EXECUTOR-AUTH-0001", {}).get("status") == "expired", "first executor authorization must be exhausted by the failed attempt", errors)
    executor_authorization = executor_authorizations.get("DBOS-EXP-0001-EXECUTOR-AUTH-0002", {})
    require(executor_authorization.get("status") == "expired" and executor_authorization.get("executor_id") == "dbio:executor:automated-runner:dbos-self-validation:v0.1", "second executor authorization must be exhausted by the completed execution", errors)
    require(executor_authorization.get("current_effect") == "none_consumed_by_successful_execution", "executor authorization must have no remaining authority", errors)


def verify_bundle(output_dir: Path, errors: list[str]) -> None:
    bundle_path = output_dir / "evidence-bundle.json"
    bundle = load(bundle_path)
    artifacts = bundle.get("artifacts")
    require(isinstance(artifacts, list) and bundle.get("artifact_count") == len(artifacts), "evidence bundle artifact count mismatch", errors)
    if isinstance(artifacts, list):
        for item in artifacts:
            path = output_dir / item.get("artifact", "")
            require(path.is_file(), f"evidence bundle artifact missing: {item.get('artifact')}", errors)
            if path.is_file():
                require(item.get("digest") == digest_file(path) and item.get("size") == path.stat().st_size, f"evidence bundle artifact mismatch: {item.get('artifact')}", errors)


def validate_completed(root: Path, errors: list[str]) -> None:
    output_dir = root / "evidence/experiments/DBOS-EXP-0001/run-0002"
    required = ["experiment-result.json", "execution-context.json", "input-snapshot.json", "output-snapshot.json", "validator-results.json", "event-record.json", "event-integrity.json", "event-producer.json", "event-attestation.json", "evidence-bundle.json", "verification-result.json"]
    for name in required:
        require((output_dir / name).is_file(), f"completed experiment artifact missing: {name}", errors)
    if any(not (output_dir / name).is_file() for name in required):
        return
    result = load(output_dir / "experiment-result.json")
    require(result.get("status") == "completed" and result.get("execution_id") == EXECUTION_ID and result.get("executed_steps") == [f"DBOS-EXP-0001-STEP-{index:02d}" for index in range(1, 9)], "experiment result is not completed for all eight steps", errors)
    validation = load(output_dir / "validator-results.json")
    require(validation.get("fail_count") == 0 and validation.get("pass_count") == validation.get("validator_count_expected") == validation.get("validator_count_executed"), "frozen validator suite did not fully pass", errors)
    event = load(output_dir / "event-record.json")
    integrity = load(output_dir / "event-integrity.json")
    require(event.get("event_id") == EVENT_ID and event.get("status") == "validated", "validated event record missing", errors)
    require(integrity.get("event_id") == EVENT_ID and integrity.get("sequence") == 1 and integrity.get("previous_hash") is None, "genesis event ordering invalid", errors)
    require(integrity.get("current_hash") == digest_file(output_dir / "event-record.json") and integrity.get("integrity_status") == "verified", "event integrity digest mismatch", errors)
    attestation = load(output_dir / "event-attestation.json")
    require(attestation.get("event_id") == EVENT_ID and attestation.get("status") == "attested" and attestation.get("trust_effect") == "none", "bounded event attestation invalid", errors)
    verification = load(output_dir / "verification-result.json")
    require(verification.get("decision") == "pass" and verification.get("status") == "verified_local_structural" and verification.get("independence_status") == "not_independent", "bounded verification result invalid", errors)
    require(verification.get("verification_level_effect") == "none" and verification.get("capability_effect") == "none" and verification.get("permission_effect") == "none", "verification result must not promote C/E/V, capability, or permission", errors)
    verify_bundle(output_dir, errors)
    first_output_dir = root / "evidence/experiments/DBOS-EXP-0001/run-0001"
    require((first_output_dir / "experiment-result.json").is_file() and (first_output_dir / "validator-results.json").is_file(), "first failed attempt artifacts must remain retained", errors)
    if (first_output_dir / "experiment-result.json").is_file() and (first_output_dir / "validator-results.json").is_file():
        first_result = load(first_output_dir / "experiment-result.json")
        first_validation = load(first_output_dir / "validator-results.json")
        require(first_result.get("status") == "failed" and first_result.get("stop_reason") == "validator_failure_or_incomplete_suite", "first failed attempt result was altered", errors)
        require(first_validation.get("pass_count") == 3 and first_validation.get("fail_count") == 1 and first_validation.get("validator_count_executed") == 4 and first_validation.get("validator_count_expected") == 29, "first failed validator results were altered", errors)

    experiments = records(load(root / "registry/experiments.yaml"), "experiments", "experiment_id", errors)
    experiment = experiments.get(EXPERIMENT_ID, {})
    require(experiment.get("status") == "completed" and experiment.get("execution_status") == "completed" and experiment.get("run_ref") == EXECUTION_ID, "canonical experiment registry is not completed", errors)
    executions = records(load(root / "registry/runner-executions.yaml"), "runner_executions", "execution_id", errors)
    require(executions.get("dbio:runner-execution:dbos-self-validation:DBOS-EXP-0001:0001", {}).get("status") == "failed", "first failed Runner attempt must remain preserved", errors)
    require(executions.get(EXECUTION_ID, {}).get("status") == "succeeded", "Runner execution registry is not succeeded", errors)
    runner_evidence = records(load(root / "registry/runner-evidence.yaml"), "runner_evidence", "evidence_id", errors)
    require(len(runner_evidence) == 6, "Runner evidence registry must retain six attempt artifacts", errors)
    for item in runner_evidence.values():
        artifact = root / item.get("artifact", "")
        require(artifact.is_file(), f"Runner evidence artifact missing: {item.get('artifact')}", errors)
        if artifact.is_file():
            require(item.get("digest") == digest_file(artifact), f"Runner evidence digest mismatch: {item.get('evidence_id')}", errors)

    contexts = records(load(root / "registry/execution-contexts.yaml"), "execution_contexts", "context_id", errors)
    context = load(output_dir / "execution-context.json")
    require(contexts.get(context.get("context_id"), {}).get("evidence_ref", "").endswith(digest_file(output_dir / "execution-context.json")), "canonical execution context does not bind the retained artifact", errors)
    input_records = records(load(root / "registry/input-snapshots.yaml"), "input_snapshots", "snapshot_id", errors)
    output_records = records(load(root / "registry/output-snapshots.yaml"), "output_snapshots", "snapshot_id", errors)
    input_snapshot = load(output_dir / "input-snapshot.json")
    output_snapshot = load(output_dir / "output-snapshot.json")
    require(input_records.get(input_snapshot.get("snapshot_id"), {}).get("hash") == input_snapshot.get("hash"), "canonical input snapshot mismatch", errors)
    require(output_records.get(output_snapshot.get("snapshot_id"), {}).get("hash") == output_snapshot.get("hash"), "canonical output snapshot mismatch", errors)
    dependencies = load(root / "registry/execution-dependencies.yaml").get("execution_dependencies", [])
    require(any(item.get("context_id") == context.get("context_id") and item.get("dependency") == "python_standard_library" for item in dependencies), "canonical execution dependency missing", errors)

    canonical_events = records(load(root / "registry/events.yaml"), "events", "event_id", errors)
    require(canonical_events.get(EVENT_ID, {}).get("event_artifact_ref", "").endswith(digest_file(output_dir / "event-record.json")), "canonical event does not bind the retained event artifact", errors)
    streams = records(load(root / "registry/event-streams.yaml"), "event_streams", "stream_id", errors)
    stream_id = integrity.get("stream_id")
    require(streams.get(stream_id, {}).get("status") == "active" and streams.get(stream_id, {}).get("entity_id") == SUBJECT_ID, "active experiment event stream missing", errors)
    ordering = {item.get("stream_id"): item for item in load(root / "registry/event-ordering.yaml").get("event_ordering_rules", [])}
    require(stream_id in ordering, "event stream ordering rule missing", errors)
    canonical_integrity = records(load(root / "registry/event-integrity.yaml"), "event_integrity_records", "event_id", errors)
    require(canonical_integrity.get(EVENT_ID, {}).get("current_hash") == digest_file(output_dir / "event-record.json"), "canonical event integrity digest mismatch", errors)
    witnesses = records(load(root / "registry/event-witnesses.yaml"), "event_witnesses", "witness_id", errors)
    require(any(item.get("identity_ref") == RUNNER_ID and item.get("independence_status") == "not_independent" for item in witnesses.values()), "local non-independent event witness missing", errors)
    producers = records(load(root / "registry/event-producers.yaml"), "event_producers", "producer_id", errors)
    producer = load(output_dir / "event-producer.json")
    require(producers.get(producer.get("producer_id"), {}).get("identity_ref") == RUNNER_ID, "canonical event producer identity mismatch", errors)
    attestations = records(load(root / "registry/event-attestations.yaml"), "event_attestations", "attestation_id", errors)
    canonical_attestation = attestations.get(attestation.get("attestation_id"), {})
    require(canonical_attestation.get("status") == "signed" and canonical_attestation.get("trust_anchor_refs") == [] and canonical_attestation.get("evidence_ref", "").endswith(digest_file(output_dir / "event-attestation.json")), "canonical bounded attestation mismatch", errors)
    require(load(root / "registry/trust-anchors.yaml").get("trust_anchors") == [], "experiment must not create a trust anchor", errors)
    outputs = load(root / "registry/experiment-outputs.yaml").get("experiment_outputs", [])
    require(len(outputs) == 6 and all(item.get("status") == "validated" and (root / item.get("artifact_ref", "")).is_file() for item in outputs), "six canonical experiment outputs must be validated and retained", errors)


def validate(root: Path, phase: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    check_zero_boundaries(root, errors)
    identity_drift_count = validate_environment(root, phase, errors, warnings)
    if PHASES.index(phase) >= PHASES.index("freeze"):
        validate_freeze(root, errors)
    if PHASES.index(phase) >= PHASES.index("runner"):
        validate_runner(root, errors)
    if PHASES.index(phase) >= PHASES.index("authorization"):
        validate_authorization(root, errors)
    if phase == "completed":
        validate_completed(root, errors)
    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "execution_chain_validator",
        "phase": phase,
        "experiment_id": EXPERIMENT_ID,
        "agent_count": 0,
        "runtime_count": 0,
        "digital_organism_count": 0,
        "capability_assignment_count": 0,
        "permission_grant_count": 0,
        "c_e_v_level_change_count": 0,
        "historical_identity_validation_mode": (
            "retained_manifest_binding" if phase == "completed" else "current_path_exact_digest"
        ),
        "current_workspace_identity_drift_count": identity_drift_count,
        "warnings": warnings,
        "errors": errors,
    }


def automatic_phase(root: Path) -> str:
    chain_path = root / "registry/experiment-execution-chain.yaml"
    if not chain_path.is_file():
        return "environment"
    status = load(chain_path).get("metadata", {}).get("status", "")
    if isinstance(status, str):
        if status.startswith("completed") or status.startswith("phase_6") or status.startswith("phase_5"):
            return "completed"
        if status.startswith("phase_4"):
            return "authorization"
        if status.startswith("phase_3"):
            return "runner"
        if status.startswith("phase_2"):
            return "freeze"
    return "environment"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--phase", choices=("auto",) + PHASES, default="auto")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        phase = automatic_phase(root) if args.phase == "auto" else args.phase
        result = validate(root, phase)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"status": "FAIL", "validator": "execution_chain_validator", "phase": args.phase, "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
        for error in result.get("errors", []):
            print(f"- {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
