"""Validate Registration Authorization and identity continuity boundaries.

Agent-readable contract:
- Only a complete, current ``AUTHORIZED`` input may reach registration.
- The authorization scope is limited to ``entity_registration`` and
  ``REGISTERED``; it cannot carry activation, capability, or permission effects.
- Candidate, authorization, Entity record, and receipt identifiers must form a
  deterministic chain. An unattributed ``entity_id`` is rejected.
- Validation reads in-memory mappings only and creates no DBOS state.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from entity_support.candidate.candidate_registry import (
    validate_candidate_registry_record,
)
from entity_support.entity_registry import SUPPORTED_ENTITY_TYPES
from entity_support.registration.registration_receipt import (
    validate_registration_receipt,
)

REGISTRATION_AUTHORIZATION_FIELDS = (
    "authorization_id",
    "decision_reference",
    "candidate_id",
    "target_entity_type",
    "authorized_scope",
    "issuer_reference",
    "status",
    "timestamp",
)
REGISTRATION_AUTHORIZATION_STATUSES = frozenset(
    {"PENDING", "AUTHORIZED", "REJECTED", "REVOKED"}
)
REGISTERED_ENTITY_RECORD_FIELDS = (
    "entity_id",
    "candidate_reference",
    "authorization_reference",
    "registered_at",
    "entity_type",
    "lifecycle_state",
)
REQUIRED_SCOPE = {
    "operation": "entity_registration",
    "lifecycle_target": "REGISTERED",
}
PROHIBITED_EFFECT_KEYS = frozenset(
    {
        "active",
        "activation",
        "activation_status",
        "agent_id",
        "runtime_id",
        "permission",
        "permission_grant",
        "permission_status",
        "capability_grant",
        "capability_assignment",
        "execution_id",
        "evidence_id",
        "fitness_assessment",
    }
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_timezone_aware_timestamp(value: object) -> bool:
    if not _is_non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _find_prohibited_effect_keys(value: object, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            child_path = f"{path}.{key}"
            if normalized in PROHIBITED_EFFECT_KEYS:
                findings.append(child_path)
            findings.extend(_find_prohibited_effect_keys(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(_find_prohibited_effect_keys(child, f"{path}[{index}]"))
    return findings


def derive_entity_id(candidate_id: str, authorization_id: str) -> str:
    """Derive an opaque, deterministic identity from both source identifiers."""

    if not _is_non_empty_string(candidate_id):
        raise ValueError("candidate_id must be a non-empty string")
    if not _is_non_empty_string(authorization_id):
        raise ValueError("authorization_id must be a non-empty string")
    material = f"{candidate_id.strip()}\0{authorization_id.strip()}".encode("utf-8")
    digest = hashlib.sha256(material).hexdigest()[:24]
    return f"dbio:entity:registration:{digest}"


def validate_registration_authorization_input(
    authorization: Mapping[str, Any],
) -> list[str]:
    """Validate one executable registration authorization input."""

    errors: list[str] = []
    missing = [
        field for field in REGISTRATION_AUTHORIZATION_FIELDS if field not in authorization
    ]
    extra = sorted(set(authorization) - set(REGISTRATION_AUTHORIZATION_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    for field in (
        "authorization_id",
        "decision_reference",
        "candidate_id",
        "issuer_reference",
    ):
        if not _is_non_empty_string(authorization.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if authorization.get("target_entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("target_entity_type must use the existing DBOS classification")
    if not _is_timezone_aware_timestamp(authorization.get("timestamp")):
        errors.append("timestamp must be a timezone-aware ISO 8601 string")

    status = authorization.get("status")
    if status not in REGISTRATION_AUTHORIZATION_STATUSES:
        errors.append("status is not a Registration Authorization status")
    if status != "AUTHORIZED":
        errors.append("registration requires status=AUTHORIZED")

    scope = authorization.get("authorized_scope")
    if not isinstance(scope, Mapping):
        errors.append("authorized_scope must be a mapping")
    else:
        for key, expected in REQUIRED_SCOPE.items():
            if scope.get(key) != expected:
                errors.append(f"authorized_scope.{key} must be {expected}")
        prohibited = _find_prohibited_effect_keys(scope, "$.authorized_scope")
        if prohibited:
            errors.append(f"authorized_scope contains prohibited effect keys: {prohibited}")

    prohibited = _find_prohibited_effect_keys(authorization)
    if prohibited:
        errors.append(f"authorization contains prohibited effect keys: {prohibited}")
    return errors


def build_registration_authorization_input(
    *,
    authorization_id: str,
    decision_reference: str,
    candidate_id: str,
    target_entity_type: str,
    authorized_scope: Mapping[str, Any],
    issuer_reference: str,
    timestamp: str,
    status: str = "AUTHORIZED",
) -> dict[str, Any]:
    """Return an executable input mapping; it does not issue authorization."""

    authorization = {
        "authorization_id": authorization_id,
        "decision_reference": decision_reference,
        "candidate_id": candidate_id,
        "target_entity_type": target_entity_type,
        "authorized_scope": dict(authorized_scope),
        "issuer_reference": issuer_reference,
        "status": status,
        "timestamp": timestamp,
    }
    errors = validate_registration_authorization_input(authorization)
    if errors:
        raise ValueError("; ".join(errors))
    return authorization


def validate_candidate_registration_source(candidate: Mapping[str, Any]) -> list[str]:
    """Require an approved and accepted Candidate source without promoting it."""

    errors = [
        f"candidate: {error}" for error in validate_candidate_registry_record(candidate)
    ]
    review = candidate.get("review")
    if not isinstance(review, Mapping) or review.get("review_status") != "APPROVED":
        errors.append("candidate requires APPROVED review")
    request = candidate.get("registration_request")
    if not isinstance(request, Mapping) or request.get("status") != "ACCEPTED":
        errors.append("candidate requires ACCEPTED registration_request")
    return errors


def validate_registered_entity_record(record: Mapping[str, Any]) -> list[str]:
    """Validate a registration output without permitting activation effects."""

    errors: list[str] = []
    missing = [field for field in REGISTERED_ENTITY_RECORD_FIELDS if field not in record]
    extra = sorted(set(record) - set(REGISTERED_ENTITY_RECORD_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("entity_id", "candidate_reference", "authorization_reference"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("entity_type must use the existing DBOS classification")
    if record.get("lifecycle_state") != "REGISTERED":
        errors.append("registration output requires lifecycle_state=REGISTERED")
    if not _is_timezone_aware_timestamp(record.get("registered_at")):
        errors.append("registered_at must be a timezone-aware ISO 8601 string")
    prohibited = _find_prohibited_effect_keys(record)
    if prohibited:
        errors.append(f"registered entity record contains prohibited effect keys: {prohibited}")
    return errors


def validate_identity_continuity(
    *,
    candidate: Mapping[str, Any],
    authorization: Mapping[str, Any],
    entity_record: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> list[str]:
    """Validate candidate → authorization → entity → receipt continuity."""

    errors: list[str] = []
    candidate_id = candidate.get("candidate_id")
    authorization_id = authorization.get("authorization_id")
    if authorization.get("candidate_id") != candidate_id:
        errors.append("authorization candidate_id must match candidate source")
    if entity_record.get("candidate_reference") != candidate_id:
        errors.append("entity candidate_reference must match candidate source")
    if entity_record.get("authorization_reference") != authorization_id:
        errors.append("entity authorization_reference must match authorization source")
    if authorization.get("target_entity_type") != entity_record.get("entity_type"):
        errors.append("entity_type must match authorized target_entity_type")

    request = candidate.get("registration_request")
    if isinstance(request, Mapping) and request.get("requested_entity_type") != entity_record.get(
        "entity_type"
    ):
        errors.append("entity_type must match candidate registration request")

    if _is_non_empty_string(candidate_id) and _is_non_empty_string(authorization_id):
        expected_entity_id = derive_entity_id(str(candidate_id), str(authorization_id))
        if entity_record.get("entity_id") != expected_entity_id:
            errors.append("entity_id lacks deterministic candidate/authorization provenance")
    else:
        errors.append("identity continuity requires candidate_id and authorization_id")

    errors.extend(f"receipt: {error}" for error in validate_registration_receipt(receipt))
    if receipt.get("status") != "SUCCESS":
        errors.append("identity continuity requires SUCCESS receipt")
    if receipt.get("entity_id") != entity_record.get("entity_id"):
        errors.append("receipt entity_id must match registered entity record")
    if receipt.get("authorization_reference") != authorization_id:
        errors.append("receipt authorization_reference must match authorization source")
    return errors


__all__ = [
    "PROHIBITED_EFFECT_KEYS",
    "REGISTERED_ENTITY_RECORD_FIELDS",
    "REGISTRATION_AUTHORIZATION_FIELDS",
    "REGISTRATION_AUTHORIZATION_STATUSES",
    "REQUIRED_SCOPE",
    "build_registration_authorization_input",
    "derive_entity_id",
    "validate_candidate_registration_source",
    "validate_identity_continuity",
    "validate_registered_entity_record",
    "validate_registration_authorization_input",
]
