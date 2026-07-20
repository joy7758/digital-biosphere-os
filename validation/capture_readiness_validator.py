#!/usr/bin/env python3
"""Validate snapshot-capture readiness without authorizing or running capture.

Agent-readable contract:
- The collector registry is empty; no human or automated process is appointed.
- One deny-by-default local scope is defined but not approved or authorized.
- One capture authorization is pending with collector_id=null,
  authorized_by=null, decision_at=null, and current_effect=none.
- Collector, scope, authorization, and privacy reviews all remain pending.
- Readiness cannot create snapshot hashes, capture evidence, events, runtimes,
  Agents, organisms, capabilities, permissions, or C/E/V promotion.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
SNAPSHOT_ID = "DBOS-EXP-0001-SNAPSHOT-0001"
CAPTURE_ID = "DBOS-EXP-0001-CAPTURE-0001"
SCOPE_ID = "DBOS-EXP-0001-CAPTURE-SCOPE-0001"
AUTHORIZATION_ID = "DBOS-EXP-0001-CAPTURE-AUTH-0001"
EXPERIMENT_AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
CRITERIA = ("collector", "scope", "authorization", "privacy")
REVIEW_IDS = tuple(
    f"DBOS-EXP-0001-CAPTURE-READINESS-{index:04d}" for index in range(1, 5)
)
COLLECTOR_TYPES = {"human", "automated"}
COLLECTOR_STATUSES = {"proposed", "verified", "active", "suspended", "revoked", "retired"}
SCOPE_STATUSES = {"proposed", "defined", "approved", "invalid", "revoked", "superseded"}
AUTHORIZATION_STATUSES = {"pending", "authorized", "denied", "expired", "revoked"}
REVIEW_STATUSES = {"pending", "ready", "not_ready", "invalid", "revoked"}
INCLUDED_PATHS = (
    "README.md",
    "constitution/",
    "evidence/",
    "evolution/",
    "policies/",
    "references/",
    "registry/",
    "schemas/",
    "validation/",
)
MANDATORY_EXCLUSIONS = {
    "../",
    ".git/",
    "**/.env*",
    "**/*secret*",
    "**/*credential*",
    "**/*token*",
    "**/*key*",
    "**/__pycache__/",
    "**/*.pyc",
    "**/.DS_Store",
    "member-repositories-outside-root",
    "unapproved-external-storage",
    "dataless-or-non-materialized-files",
}
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
    "hash_value",
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
    """Reject capture output, authority, event, and level fields in readiness data."""
    if isinstance(record, dict):
        present = sorted(FORBIDDEN_EFFECT_KEYS.intersection(record))
        if present:
            errors.append(f"{label}: readiness cannot contain capture output or authority fields {present}")
        for key, value in record.items():
            reject_effect_fields(value, f"{label}.{key}", errors)
    elif isinstance(record, list):
        for index, value in enumerate(record):
            reject_effect_fields(value, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    """Require zero-effect metadata in this non-executing baseline."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(
    experiment_doc: dict[str, Any],
    collector_doc: dict[str, Any],
    scope_doc: dict[str, Any],
    capture_authorization_doc: dict[str, Any],
    review_doc: dict[str, Any],
    capture_doc: dict[str, Any],
    snapshot_doc: dict[str, Any],
    digest_doc: dict[str, Any],
    capture_evidence_doc: dict[str, Any],
    experiment_authorization_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    subject_doc: dict[str, Any],
    verifier_doc: dict[str, Any],
    event_doc: dict[str, Any],
    context_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    capability_evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate capture readiness while preserving the pending capture baseline."""
    errors: list[str] = []

    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("capture readiness requires exactly DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if experiment.get("status") != "registered" or experiment.get("execution_status") != "not_executed":
        errors.append("capture readiness cannot authorize or execute the experiment")
    if experiment.get("execution_context_ref") is not None or experiment.get("runtime_ref") is not None or experiment.get("run_ref") is not None:
        errors.append("capture readiness cannot attach context, runtime, or run references")

    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    subjects = index_records(
        subject_doc.get("experiment_subjects"), "subject_id", "experiment_subjects", errors
    )
    verifiers = index_records(
        verifier_doc.get("verifiers"), "verifier_id", "verifiers", errors
    )
    governed_identity_refs = set(entities) | set(subjects) | set(verifiers)
    governed_identity_refs.update(
        subject.get("entity_id")
        for subject in subjects.values()
        if nonempty_string(subject.get("entity_id"))
    )

    collectors = index_records(
        collector_doc.get("capture_collectors"), "collector_id", "capture_collectors", errors
    )
    collector_type_counts: Counter[str] = Counter()
    for collector_id, collector in collectors.items():
        collector_type = collector.get("collector_type")
        if collector_type not in COLLECTOR_TYPES:
            errors.append(f"{collector_id}: invalid collector_type {collector_type!r}")
        else:
            collector_type_counts[collector_type] += 1
        identity_ref = collector.get("identity_ref")
        if not nonempty_string(identity_ref) or identity_ref not in governed_identity_refs:
            errors.append(f"{collector_id}: collector must have a resolvable governed identity_ref")
        if not nonempty_string(collector.get("method")):
            errors.append(f"{collector_id}: collector method must be explicit")
        if collector.get("status") not in COLLECTOR_STATUSES:
            errors.append(f"{collector_id}: invalid collector status {collector.get('status')!r}")
    if collectors:
        errors.append("v0.1 collector registry must remain empty until an identity is explicitly appointed")
    collector_meta = collector_doc.get("metadata", {})
    if collector_meta.get("collector_count") != 0:
        errors.append("collector metadata count must remain zero")
    for collector_type in COLLECTOR_TYPES:
        if collector_meta.get("collector_type_distribution", {}).get(collector_type) != 0:
            errors.append(f"collector type distribution for {collector_type} must remain zero")
    require_zero(
        collector_meta,
        ("verified_collector_count", "active_collector_count", "agent_created_count", "capability_effect_count", "permission_grant_count"),
        "collector",
        errors,
    )

    scopes = index_records(
        scope_doc.get("capture_scopes"), "scope_id", "capture_scopes", errors
    )
    if tuple(scopes) != (SCOPE_ID,):
        errors.append("capture scope registry must contain exactly one defined scope")
    scope = scopes.get(SCOPE_ID, {})
    expected_scope_fields = {
        "experiment_id": EXPERIMENT_ID,
        "root_ref": str(root),
        "exclusion_precedence": "deny_overrides_allow",
        "privacy_status": "pending",
        "authority_effect": "none",
    }
    for field, expected in expected_scope_fields.items():
        if scope.get(field) != expected:
            errors.append(f"{SCOPE_ID}: {field} must remain {expected!r}")
    if scope.get("experiment_id") not in experiments:
        errors.append(f"{SCOPE_ID}: scope must reference an existing experiment")
    if scope.get("status") not in SCOPE_STATUSES:
        errors.append(f"{SCOPE_ID}: invalid scope status {scope.get('status')!r}")
    if scope.get("status") != "defined":
        errors.append(f"{SCOPE_ID}: v0.1 scope must remain defined and not approved")
    included_paths = scope.get("included_paths")
    if not isinstance(included_paths, list) or not included_paths:
        errors.append(f"{SCOPE_ID}: included_paths must be explicit and non-empty")
        included_paths = []
    if tuple(included_paths) != INCLUDED_PATHS:
        errors.append(f"{SCOPE_ID}: included_paths must preserve the bounded DBOS allowlist")
    for included_path in included_paths:
        if not nonempty_string(included_path):
            errors.append(f"{SCOPE_ID}: included path must be non-empty")
            continue
        if Path(included_path).is_absolute() or ".." in Path(included_path).parts:
            errors.append(f"{SCOPE_ID}: included path must be relative and stay inside DBOS: {included_path}")
            continue
        resolved = root / included_path.rstrip("/")
        if not resolved.exists():
            errors.append(f"{SCOPE_ID}: included path does not exist: {included_path}")
    excluded_paths = scope.get("excluded_paths")
    if not isinstance(excluded_paths, list) or not excluded_paths:
        errors.append(f"{SCOPE_ID}: excluded_paths must be explicit and non-empty")
        excluded_paths = []
    missing_exclusions = MANDATORY_EXCLUSIONS - set(excluded_paths)
    if missing_exclusions:
        errors.append(f"{SCOPE_ID}: missing mandatory exclusions {sorted(missing_exclusions)}")
    scope_meta = scope_doc.get("metadata", {})
    if scope_meta.get("scope_count") != 1 or scope_meta.get("scope_status_distribution", {}).get("defined") != 1:
        errors.append("scope metadata must report one defined scope")
    require_zero(
        scope_meta,
        ("approved_scope_count", "capture_authority_count", "external_project_path_count"),
        "capture scope",
        errors,
    )

    authorizations = index_records(
        capture_authorization_doc.get("capture_authorizations"),
        "authorization_id",
        "capture_authorizations",
        errors,
    )
    if tuple(authorizations) != (AUTHORIZATION_ID,):
        errors.append("capture authorization registry must contain exactly one pending record")
    authorization = authorizations.get(AUTHORIZATION_ID, {})
    if authorization.get("experiment_id") != EXPERIMENT_ID or authorization.get("experiment_id") not in experiments:
        errors.append(f"{AUTHORIZATION_ID}: authorization must reference DBOS-EXP-0001")
    if authorization.get("scope_ref") != SCOPE_ID or authorization.get("scope_ref") not in scopes:
        errors.append(f"{AUTHORIZATION_ID}: authorization must reference the defined scope")
    authorization_status = authorization.get("status")
    if authorization_status not in AUTHORIZATION_STATUSES:
        errors.append(f"{AUTHORIZATION_ID}: invalid authorization status {authorization_status!r}")
    if authorization_status == "pending":
        for field in ("collector_id", "authorized_by", "decision_at"):
            if authorization.get(field) is not None:
                errors.append(f"{AUTHORIZATION_ID}: pending authorization requires {field}=null")
        if authorization.get("current_effect") != "none":
            errors.append(f"{AUTHORIZATION_ID}: pending authorization requires current_effect=none")
    if authorization_status == "authorized":
        collector_id = authorization.get("collector_id")
        collector = collectors.get(collector_id)
        if collector is None or collector.get("status") not in {"verified", "active"}:
            errors.append(f"{AUTHORIZATION_ID}: authorized capture requires verified or active collector")
        if scope.get("status") not in {"defined", "approved"}:
            errors.append(f"{AUTHORIZATION_ID}: authorized capture requires usable scope")
        if not nonempty_string(authorization.get("authorized_by")):
            errors.append(f"{AUTHORIZATION_ID}: authorized capture requires attributable authorized_by")
        if not valid_timestamp(authorization.get("decision_at")):
            errors.append(f"{AUTHORIZATION_ID}: authorized capture requires timezone-aware decision_at")
    if authorization_status != "pending":
        errors.append("v0.1 capture authorization must remain pending and cannot be generated automatically")
    authorization_meta = capture_authorization_doc.get("metadata", {})
    if authorization_meta.get("capture_authorization_count") != 1 or authorization_meta.get("authorization_status_distribution", {}).get("pending") != 1:
        errors.append("capture authorization metadata must report one pending record")
    require_zero(
        authorization_meta,
        ("active_capture_authorization_count", "capture_execution_authority_count", "experiment_execution_authority_count", "permission_grant_count"),
        "capture authorization",
        errors,
    )

    reviews = index_records(
        review_doc.get("capture_readiness_reviews"),
        "review_id",
        "capture_readiness_reviews",
        errors,
    )
    if tuple(reviews) != REVIEW_IDS:
        errors.append("capture readiness must preserve four ordered review records")
    criterion_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    by_criterion: dict[str, dict[str, Any]] = {}
    for review_id, review in reviews.items():
        if review.get("experiment_id") != EXPERIMENT_ID:
            errors.append(f"{review_id}: review must reference DBOS-EXP-0001")
        criterion = review.get("criterion")
        if criterion not in CRITERIA:
            errors.append(f"{review_id}: invalid readiness criterion {criterion!r}")
        else:
            criterion_counts[criterion] += 1
            by_criterion[criterion] = review
        status = review.get("status")
        if status not in REVIEW_STATUSES:
            errors.append(f"{review_id}: invalid review status {status!r}")
        else:
            status_counts[status] += 1
        if status != "pending":
            errors.append(f"{review_id}: v0.1 capture readiness must remain pending")
        if not isinstance(review.get("missing_conditions"), list) or not review.get("missing_conditions"):
            errors.append(f"{review_id}: pending review requires explicit missing_conditions")
        if review.get("capture_effect") != "none":
            errors.append(f"{review_id}: readiness cannot produce capture authority")
    for criterion in CRITERIA:
        if criterion_counts.get(criterion, 0) != 1:
            errors.append(f"capture readiness criterion {criterion} must occur exactly once")
    expected_evidence_refs = {
        "collector": None,
        "scope": SCOPE_ID,
        "authorization": AUTHORIZATION_ID,
        "privacy": None,
    }
    for criterion, expected in expected_evidence_refs.items():
        if by_criterion.get(criterion, {}).get("evidence_ref") != expected:
            errors.append(f"{criterion}: evidence_ref must remain {expected!r}")
    if by_criterion.get("collector", {}).get("status") == "ready":
        evidence_ref = by_criterion["collector"].get("evidence_ref")
        if evidence_ref not in collectors or collectors[evidence_ref].get("status") not in {"verified", "active"}:
            errors.append("collector readiness requires verified or active collector identity")
    if by_criterion.get("scope", {}).get("status") == "ready" and scope.get("status") != "approved":
        errors.append("scope readiness requires approved scope")
    if by_criterion.get("authorization", {}).get("status") == "ready" and authorization_status != "authorized":
        errors.append("authorization readiness requires authorized capture record")
    if by_criterion.get("privacy", {}).get("status") == "ready":
        if scope.get("privacy_status") != "approved" or not nonempty_string(by_criterion["privacy"].get("evidence_ref")):
            errors.append("privacy readiness requires approved privacy status and evidence")
    review_meta = review_doc.get("metadata", {})
    if review_meta.get("review_count") != 4 or review_meta.get("capture_readiness_status") != "pending":
        errors.append("capture readiness metadata must report four reviews and pending aggregate status")
    for status in REVIEW_STATUSES:
        if review_meta.get("review_status_distribution", {}).get(status, 0) != status_counts.get(status, 0):
            errors.append(f"capture readiness status distribution mismatch for {status}")
    if review_meta.get("pending_criterion_count") != 4 or review_meta.get("ready_criterion_count") != 0:
        errors.append("capture readiness criterion counts must remain pending=4 and ready=0")
    require_zero(
        review_meta,
        ("capture_execution_authority_count", "snapshot_hash_created_count", "event_created_count", "runtime_created_count", "agent_created_count", "capability_effect_count", "permission_grant_count", "c_e_v_level_change_count"),
        "capture readiness",
        errors,
    )

    captures = index_records(
        capture_doc.get("snapshot_captures"), "capture_id", "snapshot_captures", errors
    )
    capture = captures.get(CAPTURE_ID)
    if capture is None:
        errors.append("capture readiness requires the existing pending capture record")
        capture = {}
    if capture.get("status") != "pending" or capture.get("collector") is not None or capture.get("captured_at") is not None:
        errors.append("capture readiness cannot execute or complete snapshot capture")
    if capture.get("artifact_digest_refs") != [] or capture.get("evidence_refs") != []:
        errors.append("capture readiness cannot attach digest or capture evidence")
    snapshots = index_records(
        snapshot_doc.get("experiment_snapshots"), "snapshot_id", "experiment_snapshots", errors
    )
    snapshot = snapshots.get(SNAPSHOT_ID)
    if snapshot is None:
        errors.append("capture readiness requires the existing experiment snapshot")
        snapshot = {}
    if snapshot.get("status") != "pending":
        errors.append("capture readiness cannot create or freeze a snapshot")
    for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash"):
        if snapshot.get(field) is not None:
            errors.append(f"capture readiness cannot generate snapshot hash {field}")
    if digest_doc.get("artifact_digests") != []:
        errors.append("capture readiness cannot create artifact digests")
    if capture_evidence_doc.get("capture_evidence") != []:
        errors.append("capture readiness cannot create capture evidence")

    experiment_authorizations = index_records(
        experiment_authorization_doc.get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    experiment_authorization = experiment_authorizations.get(EXPERIMENT_AUTHORIZATION_ID)
    if experiment_authorization is None:
        errors.append("capture readiness requires existing experiment authorization boundary")
        experiment_authorization = {}
    if experiment_authorization.get("status") != "pending" or experiment_authorization.get("authorized_by") is not None or experiment_authorization.get("decision_at") is not None:
        errors.append("capture readiness cannot grant experiment authorization")

    if event_doc.get("events") != []:
        errors.append("capture readiness cannot generate an event")
    if context_doc.get("execution_contexts") != []:
        errors.append("capture readiness cannot create an execution context")
    if runtime_doc.get("runtime_instances") != []:
        errors.append("capture readiness cannot create a runtime")
    if candidate_doc.get("organism_candidates") != []:
        errors.append("capture readiness cannot create an organism candidate")
    if capability_doc.get("capabilities") != []:
        errors.append("capture readiness cannot create a capability")
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("capture readiness cannot create an Agent entity")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for record in ecological_entities:
        if not isinstance(record, dict):
            errors.append("ecological entity records must be mappings")
            continue
        if record.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("capture readiness cannot promote ecological type")
        if record.get("evolution_stage") != "pre-organism":
            errors.append("capture readiness cannot change evolution stage")

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
            errors.append(f"{claim_id}: capture readiness must preserve claims at pending/C1")
            break
    for evidence_id, evidence in capability_evidence.items():
        if evidence.get("status") != "pending" or evidence.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: capture readiness must preserve evidence at pending/E1")
            break
    for verification_id, verification in verifications.items():
        if verification.get("status") != "pending" or verification.get("decision") != "pending" or verification.get("verification_level") != "V0":
            errors.append(f"{verification_id}: capture readiness must preserve verification at pending/V0")
            break

    reject_effect_fields(collector_doc, "collector registry", errors)
    reject_effect_fields(scope_doc, "capture scope registry", errors)
    reject_effect_fields(capture_authorization_doc, "capture authorization registry", errors)
    reject_effect_fields(review_doc, "capture readiness registry", errors)

    readiness_constitution = root / "constitution" / "snapshot-capture-readiness-constitution.yaml"
    capture_constitution = root / "constitution" / "snapshot-capture-constitution.yaml"
    experiment_readiness_constitution = root / "constitution" / "experiment-readiness-constitution.yaml"
    for path, tokens in (
        (
            readiness_constitution,
            ("collector_identity:", "capture_authorization:", "capture_scope:", "exclusion_rules:", "privacy_boundary:"),
        ),
        (
            capture_constitution,
            (
                'capture_readiness_reference: "snapshot-capture-readiness-constitution.yaml"',
                'collector_registry: "../registry/capture-collectors.yaml"',
                'scope_registry: "../registry/capture-scopes.yaml"',
                'authorization_registry: "../registry/capture-authorizations.yaml"',
                'readiness_review_registry: "../registry/capture-readiness-reviews.yaml"',
            ),
        ),
        (
            experiment_readiness_constitution,
            (
                'capture_readiness_reference: "snapshot-capture-readiness-constitution.yaml"',
                'capture_readiness_dependency:',
                'review_registry: "../registry/capture-readiness-reviews.yaml"',
            ),
        ),
    ):
        if not path.is_file():
            errors.append(f"required constitution is missing: {path.relative_to(root)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{path.name}: missing capture readiness integration token {token}")

    remaining_gaps = [
        "capture collector registry is empty",
        "defined capture scope lacks approval and privacy evidence",
        "capture authorization has collector_id=null, authorized_by=null, and decision_at=null",
        "collector, scope, authorization, and privacy reviews all remain pending",
        "snapshot capture remains pending with no collector or captured_at",
        "artifact digest and capture evidence registries remain empty",
        "experiment snapshot hashes remain null",
        "freeze, experiment readiness, and experiment authorization remain pending",
    ]
    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_id": EXPERIMENT_ID,
        "collector_count": len(collectors),
        "collector_type_distribution": {collector_type: collector_type_counts.get(collector_type, 0) for collector_type in ("human", "automated")},
        "scope_count": len(scopes),
        "scope_status": scope.get("status"),
        "capture_authorization_count": len(authorizations),
        "capture_authorization_status": authorization_status,
        "capture_readiness_status": review_meta.get("capture_readiness_status"),
        "readiness_distribution": {status: status_counts.get(status, 0) for status in ("pending", "ready", "not_ready", "invalid", "revoked")},
        "snapshot_capture_status": capture.get("status"),
        "artifact_digest_count": len(digest_doc.get("artifact_digests", [])) if isinstance(digest_doc.get("artifact_digests"), list) else None,
        "event_count": len(event_doc.get("events", [])) if isinstance(event_doc.get("events"), list) else None,
        "runtime_count": len(runtime_doc.get("runtime_instances", [])) if isinstance(runtime_doc.get("runtime_instances"), list) else None,
        "remaining_gaps": remaining_gaps,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", type=Path, default=root / "registry" / "experiments.yaml")
    parser.add_argument("--collectors", type=Path, default=root / "registry" / "capture-collectors.yaml")
    parser.add_argument("--scopes", type=Path, default=root / "registry" / "capture-scopes.yaml")
    parser.add_argument("--capture-authorizations", type=Path, default=root / "registry" / "capture-authorizations.yaml")
    parser.add_argument("--reviews", type=Path, default=root / "registry" / "capture-readiness-reviews.yaml")
    parser.add_argument("--captures", type=Path, default=root / "registry" / "snapshot-captures.yaml")
    parser.add_argument("--snapshots", type=Path, default=root / "registry" / "experiment-snapshots.yaml")
    parser.add_argument("--digests", type=Path, default=root / "registry" / "artifact-digests.yaml")
    parser.add_argument("--capture-evidence", type=Path, default=root / "registry" / "capture-evidence.yaml")
    parser.add_argument("--experiment-authorizations", type=Path, default=root / "registry" / "experiment-authorizations.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--subjects", type=Path, default=root / "registry" / "experiment-subjects.yaml")
    parser.add_argument("--verifiers", type=Path, default=root / "registry" / "verifiers.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--capability-evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
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
            load_json_yaml(args.collectors),
            load_json_yaml(args.scopes),
            load_json_yaml(args.capture_authorizations),
            load_json_yaml(args.reviews),
            load_json_yaml(args.captures),
            load_json_yaml(args.snapshots),
            load_json_yaml(args.digests),
            load_json_yaml(args.capture_evidence),
            load_json_yaml(args.experiment_authorizations),
            load_json_yaml(args.entities),
            load_json_yaml(args.subjects),
            load_json_yaml(args.verifiers),
            load_json_yaml(args.events),
            load_json_yaml(args.contexts),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
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
        print(f"CAPTURE_READINESS_VALIDATION: {result.get('status', 'FAIL')}")
        print(f"collectors={result.get('collector_count', 0)}")
        print(f"scopes={result.get('scope_count', 0)}")
        print(f"authorization_status={result.get('capture_authorization_status')}")
        print(f"readiness_status={result.get('capture_readiness_status')}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
