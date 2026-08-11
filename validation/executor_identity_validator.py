#!/usr/bin/env python3
"""Validate Executor identity enrollment without enrolling or appointing anyone.

Agent-readable contract:
- Executor Identity is an evidence-bound enrollment record, not an Agent,
  Runtime, Organism, Executor appointment, capability, or permission.
- The v0.1 identity and verification registries are empty.
- Two defined human/automated boundaries govern future enrollment only.
- A verification cannot pass automatically or expand authority.
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

IDENTITY_TYPES = {"human", "automated"}
IDENTITY_VERIFICATION_STATUSES = {
    "pending",
    "verified",
    "failed",
    "inconclusive",
    "revoked",
}
IDENTITY_LIFECYCLE_STATES = {
    "proposed",
    "enrolled",
    "verified",
    "suspended",
    "revoked",
    "retired",
}
VERIFICATION_RESULTS = {"pending", "verified", "failed", "inconclusive", "revoked"}
BOUNDARY_STATUSES = {"defined", "superseded", "revoked"}
BOUNDARY_IDS = {
    "human": "dbio:executor-boundary:human:v0.1",
    "automated": "dbio:executor-boundary:automated:v0.1",
}
MANDATORY_FORBIDDEN_ACTIONS = {
    "modify constitution",
    "modify historical evidence",
    "create agent",
    "grant permission",
}
ALLOWED_ACTION_VOCABULARY = {
    "submit executor identity enrollment request",
    "submit executor identity enrollment manifest",
    "provide bounded identity evidence",
    "provide versioned identity evidence",
    "participate in identity verification",
    "undergo bounded identity verification",
    "request suspension or revocation",
    "request suspension or revocation through accountable operator",
}
PROHIBITED_ALLOWED_ACTIONS = {
    "modify constitution",
    "modify historical evidence",
    "create agent",
    "grant permission",
    "execute experiment",
    "create runtime",
    "generate event",
    "capture snapshot",
    "self-verify identity",
    "self-appoint executor",
    "self-authorize execution",
}
FORBIDDEN_EFFECT_KEYS = {
    "agent_id",
    "runtime_id",
    "organism_id",
    "capability_id",
    "capability_assignment",
    "permission",
    "permission_grant",
    "permission_status",
    "execution_result",
    "event_id",
    "snapshot_hash",
    "authorization_status",
    "evidence_level",
    "verification_level",
    "maturity_level",
}
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML without third-party dependencies."""
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
        if not isinstance(identifier, str) or not identifier.strip():
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
    if not nonempty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reject_effect_keys(value: Any, label: str, errors: list[str]) -> None:
    """Reject fields that could smuggle authority or identity conversion."""
    if isinstance(value, dict):
        present = sorted(FORBIDDEN_EFFECT_KEYS.intersection(value))
        if present:
            errors.append(
                f"{label}: identity enrollment cannot contain authority or result fields {present}"
            )
        for key, child in value.items():
            reject_effect_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_effect_keys(child, f"{label}[{index}]", errors)


def require_zero(
    metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def _validate_identities(
    identities: dict[str, dict[str, Any]],
    verification_by_identity: dict[str, list[dict[str, Any]]],
    identity_doc: dict[str, Any],
    identity_type_counts: Counter[str],
    verification_status_counts: Counter[str],
    lifecycle_counts: Counter[str],
    errors: list[str],
) -> None:
    for identity_id, identity in identities.items():
        identity_type = identity.get("identity_type")
        if identity_type not in IDENTITY_TYPES:
            errors.append(f"{identity_id}: invalid identity_type {identity_type!r}")
        else:
            identity_type_counts[identity_type] += 1

        evidence = identity.get("identity_evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{identity_id}: identity_evidence must be a mapping")
            evidence = {}
        source = evidence.get("source")
        if not isinstance(source, dict):
            errors.append(
                f"{identity_id}: identity evidence must contain a source mapping"
            )
            source = {}
        for field in ("kind", "reference"):
            if not nonempty_string(source.get(field)):
                errors.append(
                    f"{identity_id}: identity source {field} must be non-empty"
                )
        if "issuer" not in source:
            errors.append(
                f"{identity_id}: identity source must declare issuer, including null while pending"
            )
        evidence_refs = evidence.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            errors.append(f"{identity_id}: identity evidence_refs must be a list")
            evidence_refs = []
        if not nonempty_string(evidence.get("integrity_status")):
            errors.append(
                f"{identity_id}: identity evidence integrity_status must be explicit"
            )
        limitations = evidence.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            errors.append(
                f"{identity_id}: identity evidence limitations must be explicit and non-empty"
            )

        verification_status = identity.get("verification_status")
        if verification_status not in IDENTITY_VERIFICATION_STATUSES:
            errors.append(
                f"{identity_id}: invalid verification_status {verification_status!r}"
            )
        else:
            verification_status_counts[verification_status] += 1
        lifecycle_state = identity.get("lifecycle_state")
        if lifecycle_state not in IDENTITY_LIFECYCLE_STATES:
            errors.append(f"{identity_id}: invalid lifecycle_state {lifecycle_state!r}")
        else:
            lifecycle_counts[lifecycle_state] += 1

        expected_boundary = BOUNDARY_IDS.get(identity_type)
        if identity.get("boundary_ref") != expected_boundary:
            errors.append(f"{identity_id}: boundary_ref must match identity_type")
        if identity.get("authority_effect", "none") != "none":
            errors.append(f"{identity_id}: identity enrollment cannot create authority")
        if identity.get("agent_status") not in (None, "not_an_agent"):
            errors.append(f"{identity_id}: Executor Identity cannot become an Agent")
        if identity.get("runtime_status") not in (None, "not_a_runtime"):
            errors.append(f"{identity_id}: Executor Identity cannot become a Runtime")
        if identity.get("organism_status") not in (None, "not_an_organism"):
            errors.append(f"{identity_id}: Executor Identity cannot become an Organism")

        terminal_verified = [
            record
            for record in verification_by_identity.get(identity_id, [])
            if record.get("result") == "verified"
        ]
        if verification_status == "verified":
            if lifecycle_state != "verified":
                errors.append(
                    f"{identity_id}: verified status requires lifecycle_state=verified"
                )
            if len(terminal_verified) != 1:
                errors.append(
                    f"{identity_id}: verified identity requires exactly one verified verification record"
                )
            if not evidence_refs or evidence.get("integrity_status") != "verified":
                errors.append(
                    f"{identity_id}: verified identity requires verified non-empty identity evidence"
                )
        elif lifecycle_state == "verified":
            errors.append(
                f"{identity_id}: lifecycle_state=verified cannot precede identity verification"
            )
        reject_effect_keys(identity, f"executor identity {identity_id}", errors)

    if identities:
        errors.append(
            "v0.1 executor identity registry must remain empty until real identity evidence is submitted"
        )
    identity_meta = identity_doc.get("metadata", {})
    if identity_meta.get("executor_identity_count") != 0:
        errors.append("executor identity metadata count must remain zero")
    if identity_meta.get("enrollment_status") != "not_started_no_identity":
        errors.append("executor enrollment status must remain not_started_no_identity")
    for identity_type in IDENTITY_TYPES:
        if identity_meta.get("identity_type_distribution", {}).get(identity_type) != 0:
            errors.append(
                f"identity type distribution for {identity_type} must remain zero"
            )
    require_zero(
        identity_meta,
        (
            "verified_identity_count",
            "appointed_executor_count",
            "agent_created_count",
            "runtime_created_count",
            "organism_created_count",
            "capability_effect_count",
            "permission_grant_count",
        ),
        "executor identity",
        errors,
    )


def _validate_boundaries(
    boundaries: dict[str, dict[str, Any]],
    boundary_doc: dict[str, Any],
    boundary_type_counts: Counter[str],
    errors: list[str],
) -> None:
    expected_boundary_ids = {BOUNDARY_IDS["human"], BOUNDARY_IDS["automated"]}
    if set(boundaries) != expected_boundary_ids:
        errors.append(
            "executor boundary registry must contain exactly human and automated v0.1 boundaries"
        )
    for boundary_id, boundary in boundaries.items():
        executor_type = boundary.get("executor_type")
        if executor_type not in IDENTITY_TYPES:
            errors.append(f"{boundary_id}: invalid executor_type {executor_type!r}")
        else:
            boundary_type_counts[executor_type] += 1
            if BOUNDARY_IDS.get(executor_type) != boundary_id:
                errors.append(
                    f"{boundary_id}: boundary_id does not match executor_type"
                )
        allowed_actions = boundary.get("allowed_actions")
        if not isinstance(allowed_actions, list) or not allowed_actions:
            errors.append(
                f"{boundary_id}: allowed_actions must be explicit and non-empty"
            )
            allowed_actions = []
        unknown_allowed = sorted(set(allowed_actions) - ALLOWED_ACTION_VOCABULARY)
        if unknown_allowed:
            errors.append(
                f"{boundary_id}: boundary cannot expand allowed actions {unknown_allowed}"
            )
        prohibited_allowed = sorted(
            set(allowed_actions).intersection(PROHIBITED_ALLOWED_ACTIONS)
        )
        if prohibited_allowed:
            errors.append(
                f"{boundary_id}: boundary allowed_actions contain prohibited authority {prohibited_allowed}"
            )
        forbidden_actions = boundary.get("forbidden_actions")
        if not isinstance(forbidden_actions, list):
            errors.append(f"{boundary_id}: forbidden_actions must be a list")
            forbidden_actions = []
        missing_forbidden = sorted(MANDATORY_FORBIDDEN_ACTIONS - set(forbidden_actions))
        if missing_forbidden:
            errors.append(
                f"{boundary_id}: missing mandatory forbidden actions {missing_forbidden}"
            )
        overlap = sorted(set(allowed_actions).intersection(forbidden_actions))
        if overlap:
            errors.append(
                f"{boundary_id}: allowed and forbidden actions overlap {overlap}"
            )
        if boundary.get("status") not in BOUNDARY_STATUSES:
            errors.append(
                f"{boundary_id}: invalid boundary status {boundary.get('status')!r}"
            )
        if boundary.get("status") != "defined":
            errors.append(f"{boundary_id}: v0.1 boundary must remain defined")
        if boundary.get("authority_effect") != "none":
            errors.append(
                f"{boundary_id}: boundary cannot expand permission or execution authority"
            )
        reject_effect_keys(boundary, f"executor boundary {boundary_id}", errors)

    if boundary_type_counts != Counter({"human": 1, "automated": 1}):
        errors.append(
            "executor boundary type distribution must be human=1 and automated=1"
        )
    if (
        set(boundary_doc.get("mandatory_forbidden_actions", []))
        != MANDATORY_FORBIDDEN_ACTIONS
    ):
        errors.append(
            "executor boundary registry must preserve all mandatory forbidden actions"
        )
    if (
        set(boundary_doc.get("allowed_action_vocabulary", []))
        != ALLOWED_ACTION_VOCABULARY
    ):
        errors.append(
            "executor boundary registry must preserve the controlled enrollment action vocabulary"
        )
    boundary_meta = boundary_doc.get("metadata", {})
    if boundary_meta.get("boundary_count") != 2:
        errors.append("executor boundary metadata must report two definitions")
    if boundary_meta.get("boundary_status_distribution", {}).get("defined") != 2:
        errors.append("executor boundary metadata must report two defined boundaries")
    require_zero(
        boundary_meta,
        (
            "permission_expansion_count",
            "execution_authority_count",
            "appointed_executor_count",
        ),
        "executor boundary",
        errors,
    )


def _validate_verifications(
    verifications: dict[str, dict[str, Any]],
    identities: dict[str, dict[str, Any]],
    verification_doc: dict[str, Any],
    governed_identity_refs: set[str],
    result_counts: Counter[str],
    errors: list[str],
) -> None:
    for verification_id, verification in verifications.items():
        identity_id = verification.get("executor_identity_id")
        if not nonempty_string(identity_id) or identity_id not in identities:
            errors.append(
                f"{verification_id}: verification must reference an existing executor identity"
            )
        method = verification.get("method")
        if not nonempty_string(method):
            errors.append(f"{verification_id}: verification method must be explicit")
        result = verification.get("result")
        if result not in VERIFICATION_RESULTS:
            errors.append(f"{verification_id}: invalid verification result {result!r}")
        else:
            result_counts[result] += 1
        evidence_refs = verification.get("evidence_refs", [])
        if not isinstance(evidence_refs, list):
            errors.append(f"{verification_id}: evidence_refs must be a list")
            evidence_refs = []
        verifier_ref = verification.get("verifier_ref")
        timestamp = verification.get("timestamp")
        if result == "pending":
            if timestamp is not None:
                errors.append(
                    f"{verification_id}: pending verification requires timestamp=null"
                )
            if verifier_ref is not None:
                errors.append(
                    f"{verification_id}: pending verification cannot claim a completed verifier"
                )
            if evidence_refs:
                errors.append(
                    f"{verification_id}: pending verification cannot contain terminal evidence"
                )
        elif result in {"verified", "failed", "inconclusive", "revoked"}:
            if (
                not nonempty_string(verifier_ref)
                or verifier_ref not in governed_identity_refs
            ):
                errors.append(
                    f"{verification_id}: terminal result requires attributable governed verifier_ref"
                )
            if verifier_ref in {
                identity_id,
                identities.get(identity_id, {})
                .get("identity_evidence", {})
                .get("source", {})
                .get("reference"),
            }:
                errors.append(f"{verification_id}: identity cannot verify itself")
            if not evidence_refs:
                errors.append(
                    f"{verification_id}: terminal result requires non-empty evidence_refs"
                )
            if not valid_timestamp(timestamp):
                errors.append(
                    f"{verification_id}: terminal result requires timezone-aware timestamp"
                )
        if verification.get("authority_effect", "none") != "none":
            errors.append(
                f"{verification_id}: identity verification cannot create authority"
            )
        reject_effect_keys(
            verification, f"executor verification {verification_id}", errors
        )

    if verifications:
        errors.append(
            "v0.1 executor verification registry must remain empty while no executor identity exists"
        )
    verification_meta = verification_doc.get("metadata", {})
    if verification_meta.get("executor_verification_count") != 0:
        errors.append("executor verification metadata count must remain zero")
    require_zero(
        verification_meta,
        (
            "verified_result_count",
            "automatic_pass_count",
            "appointed_executor_count",
            "execution_authority_count",
            "capability_effect_count",
            "permission_grant_count",
        ),
        "executor verification",
        errors,
    )


def _validate_immutable_effects(
    docs: dict[str, dict[str, Any]],
    agent_count: int,
    errors: list[str],
) -> None:
    executors = docs["executors"].get("executors")
    if (
        executors != []
        or docs["executors"].get("metadata", {}).get("executor_count") != 0
    ):
        errors.append("identity enrollment cannot appoint or create an Executor")
    executor_authorizations = docs["executor_authorizations"].get(
        "executor_authorizations"
    )
    if (
        not isinstance(executor_authorizations, list)
        or len(executor_authorizations) != 1
    ):
        errors.append(
            "identity enrollment must preserve one pending executor authorization slot"
        )
    else:
        authorization = executor_authorizations[0]
        if authorization.get("status") != "pending" or any(
            authorization.get(field) is not None
            for field in ("executor_id", "authorized_by", "scope_ref", "timestamp")
        ):
            errors.append("identity enrollment cannot authorize an Executor")
        if authorization.get("current_effect") != "none":
            errors.append(
                "pending executor authorization must retain current_effect=none"
            )

    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != []:
        errors.append("identity enrollment cannot create a capability")
    claims = docs["claims"].get("claims")
    if (
        not isinstance(claims, list)
        or len(claims) != 78
        or any(
            not isinstance(claim, dict)
            or claim.get("status") != "pending"
            or claim.get("maturity_level") != "C1"
            for claim in claims
        )
    ):
        errors.append(
            "identity enrollment must preserve 78 pending C1 capability claims"
        )
    evidence = docs["capability_evidence"].get("evidence")
    if (
        not isinstance(evidence, list)
        or len(evidence) != 78
        or any(
            not isinstance(record, dict)
            or record.get("evidence_type") != "E1"
            or record.get("status") != "pending"
            for record in evidence
        )
    ):
        errors.append(
            "identity enrollment cannot alter 78 pending E1 capability evidence records"
        )
    capability_verifications = docs["verification_records"].get("verification_records")
    if (
        not isinstance(capability_verifications, list)
        or len(capability_verifications) != 78
        or any(
            not isinstance(record, dict)
            or record.get("verification_level") != "V0"
            or record.get("decision") != "pending"
            or record.get("status") != "pending"
            for record in capability_verifications
        )
    ):
        errors.append(
            "identity enrollment cannot alter 78 pending V0 capability verification records"
        )

    if docs["events"].get("events") != []:
        errors.append("identity enrollment cannot generate an Event")
    if docs["runtimes"].get("runtime_instances") != []:
        errors.append("identity enrollment cannot create a Runtime")
    snapshots = docs["snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1:
        errors.append("identity enrollment must preserve one pending snapshot slot")
    else:
        snapshot = snapshots[0]
        if snapshot.get("status") != "pending" or any(
            snapshot.get(field) is not None
            for field in (
                "file_tree_hash",
                "config_hash",
                "dependency_hash",
                "environment_hash",
                "captured_at",
            )
        ):
            errors.append("identity enrollment cannot capture or generate a Snapshot")
    if (
        agent_count != 0
        or docs["entities"]
        .get("metadata", {})
        .get("classification_counts", {})
        .get("agent")
        != 0
    ):
        errors.append("identity enrollment cannot create or convert an Agent")


def _validate_texts_and_ledger(texts: dict[str, str], errors: list[str]) -> None:
    required_tokens = {
        "identity_constitution": [
            "Executor != Agent",
            "Executor != Runtime",
            "Executor != Candidate Organism",
            "executor_identity:",
            "identity_evidence:",
            "enrollment:",
            "verification:",
            "revocation:",
        ],
        "executor_constitution": [
            "identity_enrollment_requirement:",
            "executor-identities.yaml",
            "Executor Identity Verification != Executor Appointment",
        ],
        "readiness_constitution": [
            "verified_executor_requirement:",
            "executor-verifications.yaml",
            'current_status: "pending"',
        ],
    }
    for text_name, tokens in required_tokens.items():
        for token in tokens:
            if token not in texts[text_name]:
                errors.append(f"{text_name} missing required boundary token: {token}")

    evolution_ids = [
        int(value) for value in EVOLUTION_ID_RE.findall(texts["evolution_ledger"])
    ]
    if (
        not evolution_ids
        or len(evolution_ids) != len(set(evolution_ids))
        or sorted(evolution_ids) != list(range(1, max(evolution_ids) + 1))
        or max(evolution_ids) < 28
        or 28 not in evolution_ids
        or evolution_ids[-1] != max(evolution_ids)
    ):
        errors.append(
            "evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0028, and append the latest ID last"
        )
    if "executor_identity_enrollment_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append(
            "evolution ledger must contain the executor identity enrollment record"
        )


def validate(
    docs: dict[str, dict[str, Any]], texts: dict[str, str], root: Path
) -> dict[str, Any]:
    """Validate empty enrollment, defined boundaries, and no-effect invariants."""
    errors: list[str] = []

    entities = index_records(
        docs["entities"].get("entities"), "entity_id", "entities", errors
    )
    subjects = index_records(
        docs["subjects"].get("experiment_subjects"),
        "subject_id",
        "experiment_subjects",
        errors,
    )
    verifiers = index_records(
        docs["verifiers"].get("verifiers"), "verifier_id", "verifiers", errors
    )
    governed_identity_refs = set(entities) | set(subjects) | set(verifiers)
    governed_identity_refs.update(
        entity.get("canonical_id")
        for entity in entities.values()
        if nonempty_string(entity.get("canonical_id"))
    )
    governed_identity_refs.update(
        subject.get("entity_id")
        for subject in subjects.values()
        if nonempty_string(subject.get("entity_id"))
    )

    identity_doc = docs["executor_identities"]
    identities = index_records(
        identity_doc.get("executor_identities"),
        "executor_identity_id",
        "executor_identities",
        errors,
    )
    identity_type_counts: Counter[str] = Counter()
    verification_status_counts: Counter[str] = Counter()
    lifecycle_counts: Counter[str] = Counter()

    boundary_doc = docs["executor_boundaries"]
    boundaries = index_records(
        boundary_doc.get("executor_boundaries"),
        "boundary_id",
        "executor_boundaries",
        errors,
    )

    verification_doc = docs["executor_verifications"]
    verifications = index_records(
        verification_doc.get("executor_verifications"),
        "verification_id",
        "executor_verifications",
        errors,
    )
    verification_by_identity: dict[str, list[dict[str, Any]]] = {}
    for verification in verifications.values():
        identity_id = verification.get("executor_identity_id")
        if isinstance(identity_id, str):
            verification_by_identity.setdefault(identity_id, []).append(verification)

    _validate_identities(
        identities,
        verification_by_identity,
        identity_doc,
        identity_type_counts,
        verification_status_counts,
        lifecycle_counts,
        errors,
    )

    boundary_type_counts: Counter[str] = Counter()
    _validate_boundaries(boundaries, boundary_doc, boundary_type_counts, errors)

    result_counts: Counter[str] = Counter()
    _validate_verifications(
        verifications,
        identities,
        verification_doc,
        governed_identity_refs,
        result_counts,
        errors,
    )

    agent_count = sum(
        1 for entity in entities.values() if entity.get("entity_type") == "agent"
    )
    _validate_immutable_effects(docs, agent_count, errors)

    _validate_texts_and_ledger(texts, errors)

    identity_meta = identity_doc.get("metadata", {})
    executors = docs["executors"].get("executors")
    capabilities = docs["capabilities"].get("capabilities")
    claims = docs["claims"].get("claims")
    evidence = docs["capability_evidence"].get("evidence")
    capability_verifications = docs["verification_records"].get("verification_records")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "executor_identity_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "executor_identity_count": len(identities),
            "identity_type_distribution": {
                identity_type: identity_type_counts[identity_type]
                for identity_type in sorted(IDENTITY_TYPES)
            },
            "executor_verification_count": len(verifications),
            "verification_result_distribution": {
                result: result_counts[result] for result in sorted(VERIFICATION_RESULTS)
            },
            "executor_boundary_count": len(boundaries),
            "boundary_type_distribution": {
                identity_type: boundary_type_counts[identity_type]
                for identity_type in sorted(IDENTITY_TYPES)
            },
            "enrollment_status": identity_meta.get("enrollment_status"),
            "appointed_executor_count": len(executors)
            if isinstance(executors, list)
            else None,
            "active_executor_authorization_count": 0,
            "capability_count": len(capabilities)
            if isinstance(capabilities, list)
            else None,
            "claim_count": len(claims) if isinstance(claims, list) else None,
            "evidence_count": len(evidence) if isinstance(evidence, list) else None,
            "capability_verification_count": len(capability_verifications)
            if isinstance(capability_verifications, list)
            else None,
            "event_count": len(docs["events"].get("events", [])),
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "agent_count": agent_count,
            "permission_grant_count": 0,
            "remaining_gaps": [
                "no human or automated executor identity evidence has been submitted",
                "no executor identity verification record exists",
                "no executor identity is verified",
                "no Executor is appointed",
                "no Executor scope exists",
                "executor and experiment authorizations remain pending",
                "snapshot capture, freeze, environment, and experiment readiness remain pending",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "executor_identities": registry / "executor-identities.yaml",
        "executor_boundaries": registry / "executor-boundaries.yaml",
        "executor_verifications": registry / "executor-verifications.yaml",
        "executors": registry / "executors.yaml",
        "executor_authorizations": registry / "executor-authorizations.yaml",
        "entities": registry / "entities.yaml",
        "subjects": registry / "experiment-subjects.yaml",
        "verifiers": registry / "verifiers.yaml",
        "capabilities": registry / "capabilities.yaml",
        "claims": registry / "capability-claims.yaml",
        "capability_evidence": registry / "capability-evidence.yaml",
        "verification_records": registry / "verification-records.yaml",
        "events": registry / "events.yaml",
        "runtimes": registry / "runtime-instances.yaml",
        "snapshots": registry / "experiment-snapshots.yaml",
    }
    docs = {name: load_json_yaml(path) for name, path in paths.items()}
    text_paths = {
        "identity_constitution": root
        / "constitution"
        / "executor-identity-constitution.yaml",
        "executor_constitution": root / "constitution" / "executor-constitution.yaml",
        "readiness_constitution": root
        / "constitution"
        / "experiment-readiness-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {
        name: path.read_text(encoding="utf-8") for name, path in text_paths.items()
    }
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate DBOS v0.1 Executor identity enrollment"
    )
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    root = args.root.resolve()
    from execution_chain_compat import delegate_if_advanced

    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        docs, texts = load_inputs(root)
        result = validate(docs, texts, root)
    except (OSError, ValueError) as exc:
        result = {
            "status": "FAIL",
            "validator": "executor_identity_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS executor_identity_validator: "
            f"identities={summary['executor_identity_count']}, "
            f"verifications={summary['executor_verification_count']}, "
            f"boundaries={summary['executor_boundary_count']}, authority=none"
        )
    else:
        print("FAIL executor_identity_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
