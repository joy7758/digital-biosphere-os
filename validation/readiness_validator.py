#!/usr/bin/env python3
"""Validate DBOS-EXP-0001 pre-execution readiness without executing it.

Agent-readable contract:
- One bounded governance_system subject is registered for DBOS-EXP-0001.
- One snapshot and one validator manifest remain pending and unfrozen.
- The five readiness criteria remain pending and grant no execution authority.
- A snapshot or validator manifest cannot become ready before it is frozen with
  complete attributable material.
- Pending authorization blocks execution regardless of any other criterion.
- Readiness registration cannot create events, runtimes, Agents, organisms,
  capabilities, permissions, or C/E/V promotion.
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
SUBJECT_ID = "DBOS-SUBJECT-0001"
SUBJECT_ENTITY_ID = "digital-biosphere-os"
SNAPSHOT_ID = "DBOS-EXP-0001-SNAPSHOT-0001"
MANIFEST_ID = "DBOS-EXP-0001-VALIDATOR-MANIFEST-0001"
AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
ENVIRONMENT_ID = "dbio://environment/local-governance-workspace/v0.1"
CRITERIA = (
    "subject_readiness",
    "snapshot_readiness",
    "validator_freeze",
    "environment_readiness",
    "authorization_readiness",
)
REVIEW_IDS = tuple(f"DBOS-EXP-0001-READINESS-{index:04d}" for index in range(1, 6))
VALID_SUBJECT_TYPES = {"governance_system", "repository", "protocol", "service", "artifact"}
PROHIBITED_SUBJECT_TYPES = {"agent", "runtime", "organism"}
VALID_IDENTITY_STATUSES = {"registered_pending_verification", "verified", "invalid", "revoked"}
VALID_SNAPSHOT_STATUSES = {"pending", "frozen", "ready", "invalid", "revoked"}
VALID_MANIFEST_STATUSES = {"pending", "frozen", "ready", "invalid", "revoked"}
VALID_REVIEW_STATUSES = {"pending", "ready", "not_ready", "invalid", "revoked"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SNAPSHOT_HASH_FIELDS = (
    "file_tree_hash",
    "config_hash",
    "dependency_hash",
    "environment_hash",
)
FORBIDDEN_AUTHORITY_KEYS = {
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
    "verification_level",
    "evidence_level",
    "maturity_level",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping with no third-party packages."""
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
    """Index mapping records while rejecting missing or duplicate identifiers."""
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


def valid_timestamp(value: Any) -> bool:
    """Return true only for ISO 8601 timestamps with an explicit timezone."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reject_authority_fields(record: Any, label: str, errors: list[str]) -> None:
    """Reject result and authority fields anywhere in readiness records."""
    if isinstance(record, dict):
        present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(record))
        if present:
            errors.append(f"{label}: readiness cannot contain authority or result fields {present}")
        for key, value in record.items():
            reject_authority_fields(value, f"{label}.{key}", errors)
    elif isinstance(record, list):
        for index, value in enumerate(record):
            reject_authority_fields(value, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    """Require zero-effect metadata for the non-executing readiness layer."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(
    experiment_doc: dict[str, Any],
    subject_doc: dict[str, Any],
    snapshot_doc: dict[str, Any],
    manifest_doc: dict[str, Any],
    review_doc: dict[str, Any],
    authorization_doc: dict[str, Any],
    environment_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    event_doc: dict[str, Any],
    context_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate the current pending, non-authorizing readiness baseline."""
    errors: list[str] = []

    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("readiness layer requires exactly DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if experiment.get("subject") != SUBJECT_ENTITY_ID:
        errors.append("DBOS-EXP-0001 subject must remain digital-biosphere-os")
    if experiment.get("status") != "registered":
        errors.append("DBOS-EXP-0001 must remain registered and not authorized or executed")
    if experiment.get("execution_status") != "not_executed":
        errors.append("readiness cannot change experiment execution_status")
    if experiment.get("execution_context_ref") is not None or experiment.get("runtime_ref") is not None or experiment.get("run_ref") is not None:
        errors.append("readiness cannot attach context, runtime, or run references")

    canonical_entities = index_records(
        entity_doc.get("entities"), "entity_id", "entities", errors
    )
    subjects = index_records(
        subject_doc.get("experiment_subjects"), "subject_id", "experiment_subjects", errors
    )
    if tuple(subjects) != (SUBJECT_ID,):
        errors.append("readiness subject registry must contain exactly DBOS-SUBJECT-0001")
    subject = subjects.get(SUBJECT_ID, {})
    expected_subject = {
        "entity_id": SUBJECT_ENTITY_ID,
        "entity_type": "governance_system",
        "identity_status": "registered_pending_verification",
        "evidence_ref": "constitution/constitution.yaml",
        "experiment_refs": [EXPERIMENT_ID],
        "canonical_entity_status": "not_registered",
        "agent_status": "not_an_agent",
        "runtime_status": "not_a_runtime",
        "organism_status": "not_an_organism",
        "authority_effect": "none",
    }
    for field, expected in expected_subject.items():
        if subject.get(field) != expected:
            errors.append(f"{SUBJECT_ID}: {field} must remain {expected!r}")
    subject_type = subject.get("entity_type")
    if subject_type not in VALID_SUBJECT_TYPES:
        errors.append(f"{SUBJECT_ID}: invalid experiment subject type {subject_type!r}")
    if subject_type in PROHIBITED_SUBJECT_TYPES:
        errors.append(f"{SUBJECT_ID}: readiness cannot register an Agent, runtime, or organism subject")
    if subject.get("identity_status") not in VALID_IDENTITY_STATUSES:
        errors.append(f"{SUBJECT_ID}: invalid identity_status")
    evidence_ref = subject.get("evidence_ref")
    if not isinstance(evidence_ref, str) or not (root / evidence_ref).is_file():
        errors.append(f"{SUBJECT_ID}: evidence_ref must resolve within DBOS")
    if SUBJECT_ENTITY_ID in canonical_entities:
        errors.append("experiment-subject registration must not silently create a canonical digital-biosphere-os entity")
    subject_meta = subject_doc.get("metadata", {})
    if subject_meta.get("subject_count") != 1:
        errors.append("experiment subject metadata count must be one")
    if subject_meta.get("subject_type_distribution", {}).get("governance_system") != 1:
        errors.append("experiment subject type distribution must report one governance_system")
    if subject_meta.get("identity_status_distribution", {}).get("registered_pending_verification") != 1:
        errors.append("experiment subject identity distribution must remain pending verification")
    require_zero(
        subject_meta,
        (
            "canonical_entity_registration_count",
            "agent_created_count",
            "runtime_created_count",
            "organism_created_count",
            "permission_grant_count",
        ),
        "experiment subject",
        errors,
    )

    snapshots = index_records(
        snapshot_doc.get("experiment_snapshots"), "snapshot_id", "experiment_snapshots", errors
    )
    if tuple(snapshots) != (SNAPSHOT_ID,):
        errors.append("readiness snapshot registry must contain exactly one snapshot slot")
    snapshot = snapshots.get(SNAPSHOT_ID, {})
    if snapshot.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{SNAPSHOT_ID}: snapshot must reference DBOS-EXP-0001")
    snapshot_status = snapshot.get("status")
    if snapshot_status not in VALID_SNAPSHOT_STATUSES:
        errors.append(f"{SNAPSHOT_ID}: invalid snapshot status {snapshot_status!r}")
    if snapshot_status == "pending":
        for field in SNAPSHOT_HASH_FIELDS:
            if snapshot.get(field) is not None:
                errors.append(f"{SNAPSHOT_ID}: pending snapshot requires {field}=null")
        if snapshot.get("captured_at") is not None:
            errors.append(f"{SNAPSHOT_ID}: pending snapshot requires captured_at=null")
        if snapshot.get("retained_material_refs") != [] or snapshot.get("freeze_evidence_ref") is not None:
            errors.append(f"{SNAPSHOT_ID}: pending snapshot cannot claim frozen material or evidence")
    if snapshot_status in {"frozen", "ready"}:
        for field in SNAPSHOT_HASH_FIELDS:
            if not isinstance(snapshot.get(field), str) or not DIGEST_RE.fullmatch(snapshot[field]):
                errors.append(f"{SNAPSHOT_ID}: {snapshot_status} snapshot requires valid {field}")
        if not valid_timestamp(snapshot.get("captured_at")):
            errors.append(f"{SNAPSHOT_ID}: {snapshot_status} snapshot requires captured_at")
        if not isinstance(snapshot.get("retained_material_refs"), list) or not snapshot.get("retained_material_refs"):
            errors.append(f"{SNAPSHOT_ID}: {snapshot_status} snapshot requires retained material")
        if not isinstance(snapshot.get("freeze_evidence_ref"), str) or not snapshot.get("freeze_evidence_ref"):
            errors.append(f"{SNAPSHOT_ID}: {snapshot_status} snapshot requires freeze evidence")
    if snapshot_status != "pending":
        errors.append("v0.1 readiness baseline snapshot must remain pending and unfrozen")
    snapshot_meta = snapshot_doc.get("metadata", {})
    if snapshot_meta.get("snapshot_count") != 1:
        errors.append("snapshot metadata count must be one")
    if snapshot_meta.get("snapshot_status_distribution", {}).get("pending") != 1:
        errors.append("snapshot status distribution must remain pending:1")
    require_zero(
        snapshot_meta,
        ("frozen_snapshot_count", "ready_snapshot_count", "execution_count", "event_created_count", "permission_grant_count"),
        "snapshot",
        errors,
    )

    manifests = index_records(
        manifest_doc.get("validator_manifests"), "manifest_id", "validator_manifests", errors
    )
    if tuple(manifests) != (MANIFEST_ID,):
        errors.append("validator manifest registry must contain exactly one manifest")
    manifest = manifests.get(MANIFEST_ID, {})
    if manifest.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{MANIFEST_ID}: manifest must reference DBOS-EXP-0001")
    validators = manifest.get("validators")
    expected_validators = sorted(
        str(path.relative_to(root)) for path in (root / "validation").glob("*_validator.py")
    )
    if validators != expected_validators:
        errors.append(f"{MANIFEST_ID}: validators must exactly match current validator paths")
    if isinstance(validators, list) and len(validators) != len(set(validators)):
        errors.append(f"{MANIFEST_ID}: validator paths must be unique")
    manifest_status = manifest.get("status")
    if manifest_status not in VALID_MANIFEST_STATUSES:
        errors.append(f"{MANIFEST_ID}: invalid manifest status {manifest_status!r}")
    if manifest_status == "pending":
        for field in (
            "digest",
            "locked_digest",
            "frozen_at",
            "retained_manifest_ref",
            "freeze_evidence_ref",
        ):
            if manifest.get(field) is not None:
                errors.append(f"{MANIFEST_ID}: pending manifest requires {field}=null")
    if manifest_status in {"frozen", "ready"}:
        if not isinstance(manifest.get("digest"), str) or not DIGEST_RE.fullmatch(manifest["digest"]):
            errors.append(f"{MANIFEST_ID}: {manifest_status} manifest requires a valid digest")
        if manifest.get("locked_digest") != manifest.get("digest"):
            errors.append(f"{MANIFEST_ID}: {manifest_status} manifest requires locked_digest=digest")
        if not valid_timestamp(manifest.get("frozen_at")):
            errors.append(f"{MANIFEST_ID}: {manifest_status} manifest requires frozen_at")
        for field in ("retained_manifest_ref", "freeze_evidence_ref"):
            if not isinstance(manifest.get(field), str) or not manifest.get(field):
                errors.append(f"{MANIFEST_ID}: {manifest_status} manifest requires {field}")
    if manifest_status != "pending":
        errors.append("v0.1 validator manifest must remain pending and unfrozen")
    manifest_meta = manifest_doc.get("metadata", {})
    if manifest_meta.get("manifest_count") != 1:
        errors.append("validator manifest metadata count must be one")
    if manifest_meta.get("declared_validator_count") != len(expected_validators):
        errors.append("declared validator count must match current validator paths")
    if manifest_meta.get("manifest_status_distribution", {}).get("pending") != 1:
        errors.append("validator manifest status distribution must remain pending:1")
    require_zero(
        manifest_meta,
        ("frozen_manifest_count", "ready_manifest_count", "execution_count", "event_created_count", "permission_grant_count"),
        "validator manifest",
        errors,
    )

    authorizations = index_records(
        authorization_doc.get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    if tuple(authorizations) != (AUTHORIZATION_ID,):
        errors.append("readiness requires exactly the registered genesis authorization record")
    authorization = authorizations.get(AUTHORIZATION_ID, {})
    if authorization.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"{AUTHORIZATION_ID}: authorization must reference DBOS-EXP-0001")
    if authorization.get("status") != "pending":
        errors.append("v0.1 readiness baseline authorization must remain pending")
    if authorization.get("authorized_by") is not None or authorization.get("decision_at") is not None:
        errors.append("pending authorization requires authorized_by=null and decision_at=null")
    scope = authorization.get("scope")
    if not isinstance(scope, dict) or scope.get("current_effect") != "none":
        errors.append("pending authorization scope must have current_effect=none")
    authorization_meta = authorization_doc.get("metadata", {})
    require_zero(
        authorization_meta,
        ("active_authorization_count", "execution_authority_count", "permission_grant_count", "runtime_creation_authority_count"),
        "authorization",
        errors,
    )

    environments = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    environment = environments.get(ENVIRONMENT_ID)
    if environment is None:
        errors.append("readiness requires the local governance environment definition")
        environment = {}
    if environment.get("status") != "defined" or environment.get("activation_status") != "not_active":
        errors.append("v0.1 readiness baseline environment must remain defined and not_active")

    reviews = index_records(
        review_doc.get("readiness_reviews"), "review_id", "readiness_reviews", errors
    )
    if tuple(reviews) != REVIEW_IDS:
        errors.append("readiness registry must preserve five ordered review records")
    status_counts: Counter[str] = Counter()
    criterion_counts: Counter[str] = Counter()
    review_by_criterion: dict[str, dict[str, Any]] = {}
    for review_id, review in reviews.items():
        if review.get("experiment_id") != EXPERIMENT_ID:
            errors.append(f"{review_id}: review must reference DBOS-EXP-0001")
        criterion = review.get("criterion")
        if criterion not in CRITERIA:
            errors.append(f"{review_id}: invalid readiness criterion {criterion!r}")
        else:
            criterion_counts[criterion] += 1
            review_by_criterion[criterion] = review
        status = review.get("status")
        if status not in VALID_REVIEW_STATUSES:
            errors.append(f"{review_id}: invalid readiness status {status!r}")
        else:
            status_counts[status] += 1
        if status != "pending":
            errors.append(f"{review_id}: v0.1 readiness review must remain pending")
        if not isinstance(review.get("evidence"), list) or not review.get("evidence"):
            errors.append(f"{review_id}: review evidence inputs must be a non-empty list")
        if not isinstance(review.get("missing_conditions"), list) or not review.get("missing_conditions"):
            errors.append(f"{review_id}: pending review must retain explicit missing conditions")
        if review.get("execution_effect") != "none":
            errors.append(f"{review_id}: readiness review cannot create execution authority")
        reject_authority_fields(review, review_id, errors)
    for criterion in CRITERIA:
        if criterion_counts.get(criterion, 0) != 1:
            errors.append(f"readiness criterion {criterion} must occur exactly once")

    expected_evidence = {
        "subject_readiness": [SUBJECT_ID, "constitution/constitution.yaml"],
        "snapshot_readiness": [SNAPSHOT_ID],
        "validator_freeze": [MANIFEST_ID],
        "environment_readiness": [ENVIRONMENT_ID],
        "authorization_readiness": [AUTHORIZATION_ID],
    }
    for criterion, evidence in expected_evidence.items():
        if review_by_criterion.get(criterion, {}).get("evidence") != evidence:
            errors.append(f"{criterion}: evidence inputs must resolve to the declared readiness record")

    if review_by_criterion.get("snapshot_readiness", {}).get("status") == "ready" and snapshot_status not in {"frozen", "ready"}:
        errors.append("snapshot cannot be ready before it is frozen")
    if review_by_criterion.get("validator_freeze", {}).get("status") == "ready" and manifest_status not in {"frozen", "ready"}:
        errors.append("validator manifest cannot be ready before it is frozen")
    if review_by_criterion.get("subject_readiness", {}).get("status") == "ready" and subject.get("identity_status") != "verified":
        errors.append("subject readiness requires verified identity")
    if review_by_criterion.get("environment_readiness", {}).get("status") == "ready" and environment.get("activation_status") not in {"active", "qualified_for_experiment"}:
        errors.append("environment readiness requires activation or experiment qualification")
    if review_by_criterion.get("authorization_readiness", {}).get("status") == "ready":
        if authorization.get("status") != "authorized" or not isinstance(authorization.get("authorized_by"), str) or not valid_timestamp(authorization.get("decision_at")):
            errors.append("authorization readiness requires an attributable authorized decision")

    review_meta = review_doc.get("metadata", {})
    if review_meta.get("review_count") != 5:
        errors.append("readiness review metadata count must be five")
    if review_meta.get("readiness_status") != "pending":
        errors.append("aggregate readiness_status must remain pending")
    for status in VALID_REVIEW_STATUSES:
        if review_meta.get("review_status_distribution", {}).get(status, 0) != status_counts.get(status, 0):
            errors.append(f"readiness review status distribution mismatch for {status}")
    if review_meta.get("ready_criterion_count") != 0 or review_meta.get("pending_criterion_count") != 5:
        errors.append("readiness criterion counts must remain ready=0 and pending=5")
    require_zero(
        review_meta,
        (
            "execution_authority_count",
            "event_created_count",
            "runtime_created_count",
            "agent_created_count",
            "organism_created_count",
            "capability_effect_count",
            "permission_grant_count",
            "c_e_v_level_change_count",
        ),
        "readiness review",
        errors,
    )

    # The current layer is a review contract only; execution surfaces stay empty.
    if event_doc.get("events") != []:
        errors.append("readiness cannot create an event")
    if context_doc.get("execution_contexts") != []:
        errors.append("readiness cannot create an execution context")
    if runtime_doc.get("runtime_instances") != []:
        errors.append("readiness cannot create a runtime")
    if candidate_doc.get("organism_candidates") != []:
        errors.append("readiness cannot create an organism candidate")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity records must be mappings")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("readiness cannot promote runtime or organism ecological type")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("readiness cannot change evolution stage")
    capabilities = capability_doc.get("capabilities")
    if capabilities != []:
        errors.append("readiness cannot create a capability")
    if any(entity.get("entity_type") == "agent" for entity in canonical_entities.values()):
        errors.append("readiness cannot create an Agent entity")

    claims = index_records(claim_doc.get("claims"), "claim_id", "claims", errors)
    evidence_records = index_records(evidence_doc.get("evidence"), "evidence_id", "evidence", errors)
    verifications = index_records(verification_doc.get("verification_records"), "verification_id", "verification_records", errors)
    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(f"{claim_id}: readiness must preserve capability claim at pending/C1")
            break
    for evidence_id, evidence in evidence_records.items():
        if evidence.get("status") != "pending" or evidence.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: readiness must preserve evidence at pending/E1")
            break
    for verification_id, verification in verifications.items():
        if verification.get("status") != "pending" or verification.get("decision") != "pending" or verification.get("verification_level") != "V0":
            errors.append(f"{verification_id}: readiness must preserve verification at pending/V0")
            break

    identity_constitution = root / "constitution" / "identity-constitution.yaml"
    protocol_constitution = root / "constitution" / "experimental-protocol-constitution.yaml"
    readiness_constitution = root / "constitution" / "experiment-readiness-constitution.yaml"
    if not readiness_constitution.is_file():
        errors.append("experiment readiness constitution must exist")
    for path, tokens in (
        (
            identity_constitution,
            (
                'governance_system:',
                'experiment_subject_registry: "../registry/experiment-subjects.yaml"',
            ),
        ),
        (
            protocol_constitution,
            (
                'readiness_reference: "experiment-readiness-constitution.yaml"',
                'readiness_review_registry: "../registry/readiness-reviews.yaml"',
            ),
        ),
    ):
        if not path.is_file():
            errors.append(f"required constitution does not exist: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{path.name}: missing readiness integration token {token}")

    reject_authority_fields(subject_doc, "experiment-subject registry", errors)
    reject_authority_fields(snapshot_doc, "experiment-snapshot registry", errors)
    reject_authority_fields(manifest_doc, "validator-manifest registry", errors)

    missing_conditions = [
        "subject identity is registered_pending_verification and not a canonical entity record",
        "snapshot is pending with four null hashes and no freeze evidence",
        "validator manifest is pending with digest=null and no freeze evidence",
        "environment is defined with activation_status=not_active",
        "authorization is pending with authorized_by=null and decision_at=null",
    ]
    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_id": EXPERIMENT_ID,
        "subject_count": len(subjects),
        "subject_type_distribution": {"governance_system": 1 if subject.get("entity_type") == "governance_system" else 0},
        "snapshot_status": snapshot_status,
        "validator_manifest_status": manifest_status,
        "validator_count": len(expected_validators),
        "readiness_status": review_meta.get("readiness_status"),
        "readiness_distribution": {status: status_counts.get(status, 0) for status in ("pending", "ready", "not_ready", "invalid", "revoked")},
        "authorization_status": authorization.get("status"),
        "execution_status": experiment.get("execution_status"),
        "event_count": len(event_doc.get("events", [])) if isinstance(event_doc.get("events"), list) else None,
        "runtime_count": len(runtime_doc.get("runtime_instances", [])) if isinstance(runtime_doc.get("runtime_instances"), list) else None,
        "missing_conditions": missing_conditions,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", type=Path, default=root / "registry" / "experiments.yaml")
    parser.add_argument("--subjects", type=Path, default=root / "registry" / "experiment-subjects.yaml")
    parser.add_argument("--snapshots", type=Path, default=root / "registry" / "experiment-snapshots.yaml")
    parser.add_argument("--manifests", type=Path, default=root / "registry" / "validator-manifests.yaml")
    parser.add_argument("--reviews", type=Path, default=root / "registry" / "readiness-reviews.yaml")
    parser.add_argument("--authorizations", type=Path, default=root / "registry" / "experiment-authorizations.yaml")
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced
    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        result = validate(
            load_json_yaml(args.experiments),
            load_json_yaml(args.subjects),
            load_json_yaml(args.snapshots),
            load_json_yaml(args.manifests),
            load_json_yaml(args.reviews),
            load_json_yaml(args.authorizations),
            load_json_yaml(args.environments),
            load_json_yaml(args.entities),
            load_json_yaml(args.events),
            load_json_yaml(args.contexts),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"EXPERIMENT_READINESS_VALIDATION: {result.get('status', 'FAIL')}")
        print(f"subjects={result.get('subject_count', 0)}")
        print(f"snapshot_status={result.get('snapshot_status')}")
        print(f"validator_manifest_status={result.get('validator_manifest_status')}")
        print(f"readiness_status={result.get('readiness_status')}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
