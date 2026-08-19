#!/usr/bin/env python3
"""Validate the pending DBOS-EXP-0001 snapshot-capture contract.

Agent-readable contract:
- One pending filesystem capture references the registered experiment and its
  pending pre-execution snapshot.
- Four source-type methods are defined; definitions grant no source access.
- Artifact-digest and capture-evidence registries remain empty because no
  collection has occurred.
- Captured status requires non-empty valid digests, attributable collector and
  timestamp, and capture evidence; an identifier alone cannot satisfy it.
- Capture cannot create an event, runtime, Agent, organism, capability,
  permission, execution authority, or C/E/V promotion.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
SNAPSHOT_ID = "DBOS-EXP-0001-SNAPSHOT-0001"
CAPTURE_ID = "DBOS-EXP-0001-CAPTURE-0001"
FREEZE_ID = "DBOS-EXP-0001-FREEZE-0001"
AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
SOURCE_TYPES = ("filesystem", "git", "artifact_registry", "external_storage")
CAPTURE_STATUSES = {
    "pending",
    "captured",
    "validated",
    "partial",
    "invalid",
    "revoked",
    "superseded",
}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
FORBIDDEN_EFFECT_KEYS = {
    "capability_id",
    "capability_assignment",
    "capability_assignment_status",
    "permission",
    "permission_grant",
    "permission_status",
    "execution_result",
    "event_id",
    "runtime_id",
    "agent_id",
    "organism_id",
    "maturity_level",
    "evidence_level",
    "verification_level",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping without third-party packages."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def index_records(
    records: Any, key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    """Index mapping records and reject missing or duplicate identifiers."""
    if not isinstance(records, list):
        errors.append(f"{label} must be a list")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        where = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{where}.{key} must be a non-empty string")
            continue
        if identifier in indexed:
            errors.append(f"duplicate {key}: {identifier}")
            continue
        indexed[identifier] = record
    return indexed


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timestamp(value: Any) -> bool:
    """Return true only for ISO 8601 timestamps with an explicit timezone."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reject_effect_fields(record: Any, label: str, errors: list[str]) -> None:
    """Reject authority, execution, event, and maturity fields in capture data."""
    if isinstance(record, dict):
        present = sorted(FORBIDDEN_EFFECT_KEYS.intersection(record))
        if present:
            errors.append(
                f"{label}: capture cannot contain authority or result fields {present}"
            )
        for key, value in record.items():
            reject_effect_fields(value, f"{label}.{key}", errors)
    elif isinstance(record, list):
        for index, value in enumerate(record):
            reject_effect_fields(value, f"{label}[{index}]", errors)


def require_zero(
    metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    """Require zero-effect metadata in this non-executing baseline."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def _validate_experiments_and_snapshots(
    experiment_doc: dict, snapshot_doc: dict, errors: list
) -> tuple[dict, dict, dict, dict]:
    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("snapshot capture requires exactly DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if (
        experiment.get("status") != "registered"
        or experiment.get("execution_status") != "not_executed"
    ):
        errors.append("snapshot capture cannot authorize or execute DBOS-EXP-0001")
    if (
        experiment.get("execution_context_ref") is not None
        or experiment.get("runtime_ref") is not None
        or experiment.get("run_ref") is not None
    ):
        errors.append(
            "snapshot capture cannot attach context, runtime, or run references"
        )

    snapshots = index_records(
        snapshot_doc.get("experiment_snapshots"),
        "snapshot_id",
        "experiment_snapshots",
        errors,
    )
    snapshot = snapshots.get(SNAPSHOT_ID)
    if snapshot is None:
        errors.append("snapshot capture requires DBOS-EXP-0001-SNAPSHOT-0001")
        snapshot = {}
    if snapshot.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{SNAPSHOT_ID}: snapshot must reference DBOS-EXP-0001")
    if snapshot.get("capture_reference") != CAPTURE_ID:
        errors.append(f"{SNAPSHOT_ID}: capture_reference must bind the pending capture")
    if snapshot.get("freeze_reference") != FREEZE_ID:
        errors.append(f"{SNAPSHOT_ID}: freeze_reference must remain unchanged")
    if snapshot.get("status") != "pending":
        errors.append(f"{SNAPSHOT_ID}: snapshot must remain pending and unfrozen")
    return experiments, experiment, snapshots, snapshot


def _validate_sources(source_doc: dict, errors: list) -> dict:
    source_records = source_doc.get("snapshot_sources")
    if not isinstance(source_records, list):
        errors.append("snapshot_sources must be a list")
        source_records = []
    source_types: dict[str, dict] = {}
    for index, source in enumerate(source_records):
        where = f"snapshot_sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{where} must be a mapping")
            continue
        source_type = source.get("source_type")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{where}: invalid source_type {source_type!r}")
            continue
        if source_type in source_types:
            errors.append(f"duplicate source_type: {source_type}")
            continue
        source_types[source_type] = source
        if not nonempty_string(source.get("description")):
            errors.append(f"{source_type}: description must be non-empty")
        if not nonempty_string(source.get("verification_method")):
            errors.append(f"{source_type}: verification_method must be non-empty")
    if tuple(source_types) != SOURCE_TYPES:
        errors.append(
            "snapshot source registry must preserve all four ordered source types"
        )
    source_meta = source_doc.get("metadata", {})
    if source_meta.get("source_type_count") != 4:
        errors.append("source type metadata count must be four")
    for source_type in SOURCE_TYPES:
        if source_meta.get("source_type_distribution", {}).get(source_type) != 1:
            errors.append(f"source type distribution must report one {source_type}")
    require_zero(
        source_meta,
        ("source_instance_count", "access_authority_count"),
        "snapshot source",
        errors,
    )
    return source_types


def _validate_captures(
    capture_doc: dict,
    experiments: dict,
    snapshots: dict,
    source_types: dict,
    root,
    errors: list,
) -> tuple[dict, dict, str]:
    captures = index_records(
        capture_doc.get("snapshot_captures"), "capture_id", "snapshot_captures", errors
    )
    if tuple(captures) != (CAPTURE_ID,):
        errors.append(
            "capture registry must contain exactly DBOS-EXP-0001-CAPTURE-0001"
        )
    capture = captures.get(CAPTURE_ID, {})
    expected_capture = {
        "experiment_id": EXPERIMENT_ID,
        "snapshot_id": SNAPSHOT_ID,
        "source_type": "filesystem",
        "source_ref": str(root),
        "authority_effect": "none",
    }
    for field, expected in expected_capture.items():
        if capture.get(field) != expected:
            errors.append(f"{CAPTURE_ID}: {field} must remain {expected!r}")
    if capture.get("experiment_id") not in experiments:
        errors.append(f"{CAPTURE_ID}: capture must reference an existing experiment")
    if capture.get("snapshot_id") not in snapshots:
        errors.append(f"{CAPTURE_ID}: capture must reference an existing snapshot")
    if capture.get("source_type") not in source_types:
        errors.append(f"{CAPTURE_ID}: capture must reference a defined source type")
    capture_status = capture.get("status")
    if capture_status not in CAPTURE_STATUSES:
        errors.append(f"{CAPTURE_ID}: invalid capture status {capture_status!r}")
    return captures, capture, capture_status


def _validate_digests(digest_doc: dict, snapshots: dict, errors: list) -> dict:
    digests = index_records(
        digest_doc.get("artifact_digests"), "digest_id", "artifact_digests", errors
    )
    digest_paths: set[tuple[str, str]] = set()
    for digest_id, digest in digests.items():
        snapshot_id = digest.get("snapshot_id")
        if snapshot_id not in snapshots:
            errors.append(f"{digest_id}: digest must belong to an existing snapshot")
        artifact_path = digest.get("artifact_path")
        if not nonempty_string(artifact_path):
            errors.append(f"{digest_id}: artifact_path must be non-empty")
        else:
            key = (snapshot_id, artifact_path)
            if key in digest_paths:
                errors.append(f"duplicate artifact digest path for snapshot: {key}")
            digest_paths.add(key)
        if digest.get("hash_algorithm") != "sha256":
            errors.append(f"{digest_id}: hash_algorithm must be sha256")
        hash_value = digest.get("hash_value")
        if not isinstance(hash_value, str) or DIGEST_RE.fullmatch(hash_value) is None:
            errors.append(f"{digest_id}: hash_value must be non-empty valid sha256")
        size = digest.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append(f"{digest_id}: size must be a non-negative integer")
        if not valid_timestamp(digest.get("captured_at")):
            errors.append(f"{digest_id}: captured_at must be timezone-aware")
    return digests


def _validate_evidence(
    capture_evidence_doc: dict, captures: dict, errors: list
) -> dict:
    evidence_records = index_records(
        capture_evidence_doc.get("capture_evidence"),
        "evidence_id",
        "capture_evidence",
        errors,
    )
    for evidence_id, evidence in evidence_records.items():
        capture_id = evidence.get("capture_id")
        if capture_id not in captures:
            errors.append(f"{evidence_id}: evidence must reference an existing capture")
        if not nonempty_string(evidence.get("method")):
            errors.append(f"{evidence_id}: method must be non-empty")
        if not nonempty_string(evidence.get("collector")):
            errors.append(f"{evidence_id}: collector must be attributable")
        result = evidence.get("result")
        if not isinstance(result, dict):
            errors.append(f"{evidence_id}: result must be a mapping")
        else:
            required_result_fields = {
                "status",
                "captured_count",
                "failed_count",
                "excluded_count",
                "errors",
            }
            missing = required_result_fields - set(result)
            if missing:
                errors.append(f"{evidence_id}: result missing fields {sorted(missing)}")
        if not valid_timestamp(evidence.get("timestamp")):
            errors.append(f"{evidence_id}: timestamp must be timezone-aware")
    return evidence_records


def _validate_capture_state(
    capture_status: str,
    capture: dict,
    digests: dict,
    evidence_records: dict,
    errors: list,
):
    if capture_status == "pending":
        if (
            capture.get("collector") is not None
            or capture.get("captured_at") is not None
        ):
            errors.append(
                f"{CAPTURE_ID}: pending capture requires collector=null and captured_at=null"
            )
        if (
            capture.get("artifact_digest_refs") != []
            or capture.get("evidence_refs") != []
        ):
            errors.append(
                f"{CAPTURE_ID}: pending capture requires empty digest and evidence references"
            )
    if capture_status in {"captured", "validated"}:
        if not nonempty_string(capture.get("collector")):
            errors.append(
                f"{CAPTURE_ID}: {capture_status} capture requires attributable collector"
            )
        if not valid_timestamp(capture.get("captured_at")):
            errors.append(
                f"{CAPTURE_ID}: {capture_status} capture requires captured_at"
            )
        digest_refs = capture.get("artifact_digest_refs")
        if not isinstance(digest_refs, list) or not digest_refs:
            errors.append(
                f"{CAPTURE_ID}: captured status requires non-empty artifact digests"
            )
            digest_refs = []
        for digest_ref in digest_refs:
            digest = digests.get(digest_ref)
            if digest is None:
                errors.append(f"{CAPTURE_ID}: missing digest reference {digest_ref}")
            elif digest.get("snapshot_id") != SNAPSHOT_ID:
                errors.append(
                    f"{CAPTURE_ID}: digest {digest_ref} does not belong to the capture snapshot"
                )
        evidence_refs = capture.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            errors.append(f"{CAPTURE_ID}: captured status requires capture evidence")
            evidence_refs = []
        for evidence_ref in evidence_refs:
            evidence = evidence_records.get(evidence_ref)
            if evidence is None:
                errors.append(
                    f"{CAPTURE_ID}: missing capture evidence reference {evidence_ref}"
                )
            elif evidence.get("capture_id") != CAPTURE_ID:
                errors.append(
                    f"{CAPTURE_ID}: evidence {evidence_ref} belongs to another capture"
                )
    if capture_status != "pending":
        errors.append(
            "v0.1 snapshot capture must remain pending and cannot claim material capture"
        )
    if digests:
        errors.append(
            "v0.1 artifact digest registry must remain empty until a real capture occurs"
        )
    if evidence_records:
        errors.append(
            "v0.1 capture evidence registry must remain empty until a real capture occurs"
        )


def _validate_metadata(
    capture_doc: dict, digest_doc: dict, capture_evidence_doc: dict, errors: list
):
    capture_meta = capture_doc.get("metadata", {})
    if (
        capture_meta.get("capture_count") != 1
        or capture_meta.get("capture_status_distribution", {}).get("pending") != 1
    ):
        errors.append("capture metadata must report one pending capture")
    if capture_meta.get("source_type_usage_distribution", {}).get("filesystem") != 1:
        errors.append("capture usage distribution must report one filesystem capture")
    require_zero(
        capture_meta,
        (
            "captured_material_count",
            "artifact_digest_count",
            "capture_evidence_count",
            "execution_authority_count",
            "event_created_count",
            "runtime_created_count",
            "agent_created_count",
            "organism_created_count",
            "capability_effect_count",
            "permission_grant_count",
            "c_e_v_level_change_count",
        ),
        "snapshot capture",
        errors,
    )
    digest_meta = digest_doc.get("metadata", {})
    require_zero(
        digest_meta,
        (
            "artifact_digest_count",
            "sha256_digest_count",
            "nonempty_hash_count",
            "retained_artifact_count",
            "event_created_count",
            "permission_grant_count",
        ),
        "artifact digest",
        errors,
    )
    capture_evidence_meta = capture_evidence_doc.get("metadata", {})
    require_zero(
        capture_evidence_meta,
        (
            "capture_evidence_count",
            "successful_capture_evidence_count",
            "verified_capture_evidence_count",
            "event_created_count",
            "trust_grant_count",
            "permission_grant_count",
            "c_e_v_level_change_count",
        ),
        "capture evidence",
        errors,
    )


def _validate_freeze_and_authorization(
    freeze_doc: dict, authorization_doc: dict, errors: list
) -> tuple[dict, dict]:
    freeze_manifests = index_records(
        freeze_doc.get("freeze_manifests"), "freeze_id", "freeze_manifests", errors
    )
    freeze_manifest = freeze_manifests.get(FREEZE_ID)
    if freeze_manifest is None:
        errors.append("snapshot capture requires the pending freeze manifest")
        freeze_manifest = {}
    requirement = freeze_manifest.get("snapshot_capture_requirement")
    expected_requirement = {
        "capture_ref": CAPTURE_ID,
        "required_status": "captured",
        "minimum_artifact_digest_count": 1,
        "capture_evidence_required": True,
        "current_status": "pending",
    }
    if requirement != expected_requirement:
        errors.append(
            f"{FREEZE_ID}: snapshot_capture_requirement must remain pending and exact"
        )
    if (
        freeze_manifest.get("status") != "pending"
        or freeze_manifest.get("frozen_at") is not None
    ):
        errors.append("snapshot capture cannot freeze the experiment")

    authorizations = index_records(
        authorization_doc.get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    authorization = authorizations.get(AUTHORIZATION_ID)
    if authorization is None:
        errors.append("snapshot capture requires the existing authorization record")
        authorization = {}
    if (
        authorization.get("status") != "pending"
        or authorization.get("authorized_by") is not None
        or authorization.get("decision_at") is not None
    ):
        errors.append("snapshot capture cannot grant experiment authorization")
    return freeze_manifest, authorization


def _validate_side_effects(
    event_doc: dict,
    context_doc: dict,
    runtime_doc: dict,
    candidate_doc: dict,
    ecological_doc: dict,
    entity_doc: dict,
    capability_doc: dict,
    claim_doc: dict,
    capability_evidence_doc: dict,
    verification_doc: dict,
    errors: list,
):
    if event_doc.get("events") != []:
        errors.append("snapshot capture cannot generate an event")
    if context_doc.get("execution_contexts") != []:
        errors.append("snapshot capture cannot create an execution context")
    if runtime_doc.get("runtime_instances") != []:
        errors.append("snapshot capture cannot create a runtime")
    if candidate_doc.get("organism_candidates") != []:
        errors.append("snapshot capture cannot create an organism candidate")
    if capability_doc.get("capabilities") != []:
        errors.append("snapshot capture cannot create a capability")

    entities = index_records(
        entity_doc.get("entities"), "entity_id", "entities", errors
    )
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("snapshot capture cannot create an Agent entity")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for record in ecological_entities:
        if not isinstance(record, dict):
            errors.append("ecological entity records must be mappings")
            continue
        if record.get("ecological_type") in {
            "Runtime",
            "Candidate Organism",
            "Digital Organism",
        }:
            errors.append("snapshot capture cannot promote ecological type")
        if record.get("evolution_stage") != "pre-organism":
            errors.append("snapshot capture cannot change evolution stage")

    claims = index_records(claim_doc.get("claims"), "claim_id", "claims", errors)
    capability_evidence = index_records(
        capability_evidence_doc.get("evidence"), "evidence_id", "evidence", errors
    )
    verifications = index_records(
        verification_doc.get("verification_records"),
        "verification_id",
        "verification_records",
        errors,
    )
    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(
                f"{claim_id}: snapshot capture must preserve claims at pending/C1"
            )
            break
    for evidence_id, evidence in capability_evidence.items():
        if evidence.get("status") != "pending" or evidence.get("evidence_type") != "E1":
            errors.append(
                f"{evidence_id}: snapshot capture must preserve capability evidence at pending/E1"
            )
            break
    for verification_id, verification in verifications.items():
        if (
            verification.get("status") != "pending"
            or verification.get("decision") != "pending"
            or verification.get("verification_level") != "V0"
        ):
            errors.append(
                f"{verification_id}: snapshot capture must preserve verification at pending/V0"
            )
            break


def _validate_constitutions(root, errors: list):
    capture_constitution = root / "constitution" / "snapshot-capture-constitution.yaml"
    freeze_constitution = root / "constitution" / "experiment-freeze-constitution.yaml"
    for path, tokens in (
        (
            capture_constitution,
            (
                "capture_scope:",
                "source_types:",
                "digest_rules:",
                "capture_evidence:",
                "retention:",
            ),
        ),
        (
            freeze_constitution,
            (
                'snapshot_capture_reference: "snapshot-capture-constitution.yaml"',
                'capture_registry: "../registry/snapshot-captures.yaml"',
                'digest_registry: "../registry/artifact-digests.yaml"',
                'evidence_registry: "../registry/capture-evidence.yaml"',
            ),
        ),
    ):
        if not path.is_file():
            errors.append(f"required constitution is missing: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(
                    f"{path.name}: missing snapshot capture integration token {token}"
                )


def validate(
    experiment_doc: dict[str, Any],
    snapshot_doc: dict[str, Any],
    capture_doc: dict[str, Any],
    digest_doc: dict[str, Any],
    capture_evidence_doc: dict[str, Any],
    source_doc: dict[str, Any],
    freeze_doc: dict[str, Any],
    authorization_doc: dict[str, Any],
    event_doc: dict[str, Any],
    context_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    capability_evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate the one pending capture and empty material registries."""
    errors: list[str] = []

    experiments, experiment, snapshots, snapshot = _validate_experiments_and_snapshots(
        experiment_doc, snapshot_doc, errors
    )
    source_types = _validate_sources(source_doc, errors)
    captures, capture, capture_status = _validate_captures(
        capture_doc, experiments, snapshots, source_types, root, errors
    )
    digests = _validate_digests(digest_doc, snapshots, errors)
    evidence_records = _validate_evidence(capture_evidence_doc, captures, errors)

    _validate_capture_state(capture_status, capture, digests, evidence_records, errors)
    _validate_metadata(capture_doc, digest_doc, capture_evidence_doc, errors)

    freeze_manifest, authorization = _validate_freeze_and_authorization(
        freeze_doc, authorization_doc, errors
    )

    _validate_side_effects(
        event_doc,
        context_doc,
        runtime_doc,
        candidate_doc,
        ecological_doc,
        entity_doc,
        capability_doc,
        claim_doc,
        capability_evidence_doc,
        verification_doc,
        errors,
    )

    reject_effect_fields(capture_doc, "snapshot capture registry", errors)
    reject_effect_fields(digest_doc, "artifact digest registry", errors)
    reject_effect_fields(capture_evidence_doc, "capture evidence registry", errors)
    reject_effect_fields(source_doc, "snapshot source registry", errors)

    _validate_constitutions(root, errors)

    remaining_gaps = [
        "pending capture has collector=null and captured_at=null",
        "artifact digest registry is empty",
        "capture evidence registry is empty",
        "experiment snapshot four aggregate hashes remain null",
        "validator manifest digest and locked_digest remain null",
        "environment lock remains pending with no version or digest material",
        "freeze manifest and certificate remain pending",
        "readiness reviews and experiment authorization remain pending",
        "DBOS root has no Git repository identity",
    ]
    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_id": EXPERIMENT_ID,
        "snapshot_capture_count": len(captures),
        "artifact_digest_count": len(digests),
        "capture_evidence_count": len(evidence_records),
        "source_type_count": len(source_types),
        "source_type_distribution": {
            source_type: 1 if source_type in source_types else 0
            for source_type in SOURCE_TYPES
        },
        "capture_source_type_distribution": dict(
            Counter(record.get("source_type") for record in captures.values())
        ),
        "capture_status": capture_status,
        "freeze_status": freeze_manifest.get("status"),
        "authorization_status": authorization.get("status"),
        "execution_status": experiment.get("execution_status"),
        "event_count": len(event_doc.get("events", []))
        if isinstance(event_doc.get("events"), list)
        else None,
        "runtime_count": len(runtime_doc.get("runtime_instances", []))
        if isinstance(runtime_doc.get("runtime_instances"), list)
        else None,
        "remaining_pre_execution_gaps": remaining_gaps,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiments", type=Path, default=root / "registry" / "experiments.yaml"
    )
    parser.add_argument(
        "--snapshots",
        type=Path,
        default=root / "registry" / "experiment-snapshots.yaml",
    )
    parser.add_argument(
        "--captures", type=Path, default=root / "registry" / "snapshot-captures.yaml"
    )
    parser.add_argument(
        "--digests", type=Path, default=root / "registry" / "artifact-digests.yaml"
    )
    parser.add_argument(
        "--capture-evidence",
        type=Path,
        default=root / "registry" / "capture-evidence.yaml",
    )
    parser.add_argument(
        "--sources", type=Path, default=root / "registry" / "snapshot-sources.yaml"
    )
    parser.add_argument(
        "--freeze-manifests",
        type=Path,
        default=root / "registry" / "freeze-manifests.yaml",
    )
    parser.add_argument(
        "--authorizations",
        type=Path,
        default=root / "registry" / "experiment-authorizations.yaml",
    )
    parser.add_argument(
        "--events", type=Path, default=root / "registry" / "events.yaml"
    )
    parser.add_argument(
        "--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml"
    )
    parser.add_argument(
        "--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml"
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=root / "registry" / "organism-candidates.yaml",
    )
    parser.add_argument(
        "--ecological",
        type=Path,
        default=root / "registry" / "ecological-entities.yaml",
    )
    parser.add_argument(
        "--entities", type=Path, default=root / "registry" / "entities.yaml"
    )
    parser.add_argument(
        "--capabilities", type=Path, default=root / "registry" / "capabilities.yaml"
    )
    parser.add_argument(
        "--claims", type=Path, default=root / "registry" / "capability-claims.yaml"
    )
    parser.add_argument(
        "--capability-evidence",
        type=Path,
        default=root / "registry" / "capability-evidence.yaml",
    )
    parser.add_argument(
        "--verification",
        type=Path,
        default=root / "registry" / "verification-records.yaml",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced

    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        result = validate(
            load_json_yaml(args.experiments),
            load_json_yaml(args.snapshots),
            load_json_yaml(args.captures),
            load_json_yaml(args.digests),
            load_json_yaml(args.capture_evidence),
            load_json_yaml(args.sources),
            load_json_yaml(args.freeze_manifests),
            load_json_yaml(args.authorizations),
            load_json_yaml(args.events),
            load_json_yaml(args.contexts),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.entities),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.capability_evidence),
            load_json_yaml(args.verification),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"SNAPSHOT_CAPTURE_VALIDATION: {result.get('status', 'FAIL')}")
        print(f"snapshot_captures={result.get('snapshot_capture_count', 0)}")
        print(f"artifact_digests={result.get('artifact_digest_count', 0)}")
        print(f"source_types={result.get('source_type_count', 0)}")
        print(f"capture_status={result.get('capture_status')}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
