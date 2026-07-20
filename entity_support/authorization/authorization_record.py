"""Build immutable Registration Authorization record mappings.

Agent-readable contract:
- An Authorization Record permits only a bounded registration attempt.
- Authorization is not Permission, Capability Grant, Entity activation, or task execution.
- ``AUTHORIZED`` requires an attributable decision, issuer, and non-empty scope.
- ``REVOKED`` requires a revocation reference and cannot be used for registration.
- This module builds mappings only; it does not issue or persist authorization.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from entity_support.entity_registry import SUPPORTED_ENTITY_TYPES

AUTHORIZATION_RECORD_FIELDS = (
    "authorization_id",
    "decision_reference",
    "candidate_id",
    "target_entity_type",
    "scope",
    "issuer_reference",
    "status",
    "created_at",
    "expires_at",
    "revocation_reference",
)
AUTHORIZATION_STATUSES = frozenset(
    {"PENDING", "AUTHORIZED", "REJECTED", "REVOKED"}
)
PROHIBITED_AUTHORIZATION_EFFECT_KEYS = frozenset(
    {
        "permission",
        "permission_grant",
        "permission_status",
        "capability_grant",
        "capability_assignment",
        "active",
        "activation",
        "runtime_id",
        "agent_id",
        "execution_id",
        "evidence_id",
    }
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_timestamp(value: object) -> datetime | None:
    if not _is_non_empty_string(value):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _validate_optional_reference(
    record: Mapping[str, Any], field: str, errors: list[str]
) -> None:
    value = record.get(field)
    if value is not None and not _is_non_empty_string(value):
        errors.append(f"{field} must be null or a non-empty string")


def _find_prohibited_keys(value: object, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            child_path = f"{path}.{key}"
            if normalized in PROHIBITED_AUTHORIZATION_EFFECT_KEYS:
                findings.append(child_path)
            findings.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            findings.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return findings


def validate_authorization_record(record: Mapping[str, Any]) -> list[str]:
    """Return deterministic errors without granting any authority effect."""

    errors: list[str] = []
    missing = [field for field in AUTHORIZATION_RECORD_FIELDS if field not in record]
    extra = sorted(set(record) - set(AUTHORIZATION_RECORD_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    for field in ("authorization_id", "candidate_id"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    for field in (
        "decision_reference",
        "issuer_reference",
        "revocation_reference",
    ):
        _validate_optional_reference(record, field, errors)

    if record.get("target_entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("target_entity_type must use the existing DBOS classification")
    status = record.get("status")
    if status not in AUTHORIZATION_STATUSES:
        errors.append("status is not an Authorization Record status")

    created_at = _parse_timestamp(record.get("created_at"))
    if created_at is None:
        errors.append("created_at must be a timezone-aware ISO 8601 string")
    expires_at_value = record.get("expires_at")
    expires_at = _parse_timestamp(expires_at_value) if expires_at_value is not None else None
    if expires_at_value is not None and expires_at is None:
        errors.append("expires_at must be null or a timezone-aware ISO 8601 string")
    if created_at is not None and expires_at is not None and expires_at <= created_at:
        errors.append("expires_at must be later than created_at")

    scope = record.get("scope")
    if scope is not None and not isinstance(scope, Mapping):
        errors.append("scope must be null or a mapping")

    if status == "AUTHORIZED":
        for field in ("decision_reference", "issuer_reference"):
            if not _is_non_empty_string(record.get(field)):
                errors.append(f"AUTHORIZED requires {field}")
        if not isinstance(scope, Mapping) or not scope:
            errors.append("AUTHORIZED requires non-empty scope")
    if status == "REVOKED" and not _is_non_empty_string(
        record.get("revocation_reference")
    ):
        errors.append("REVOKED requires revocation_reference")
    if status != "REVOKED" and record.get("revocation_reference") is not None:
        errors.append("revocation_reference is allowed only for REVOKED status")

    prohibited = _find_prohibited_keys(record)
    if prohibited:
        errors.append(f"authorization contains prohibited effect keys: {prohibited}")
    return errors


def build_authorization_record(
    *,
    authorization_id: str,
    candidate_id: str,
    target_entity_type: str,
    status: str,
    created_at: str,
    decision_reference: str | None = None,
    scope: Mapping[str, Any] | None = None,
    issuer_reference: str | None = None,
    expires_at: str | None = None,
    revocation_reference: str | None = None,
) -> dict[str, Any]:
    """Return one immutable authorization record mapping."""

    record = {
        "authorization_id": authorization_id,
        "decision_reference": decision_reference,
        "candidate_id": candidate_id,
        "target_entity_type": target_entity_type,
        "scope": dict(scope) if scope is not None else None,
        "issuer_reference": issuer_reference,
        "status": status,
        "created_at": created_at,
        "expires_at": expires_at,
        "revocation_reference": revocation_reference,
    }
    errors = validate_authorization_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def authorization_record_to_execution_input(
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Project a valid Authorization Record into the existing executor input."""

    errors = validate_authorization_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "authorization_id": record["authorization_id"],
        "decision_reference": record["decision_reference"],
        "candidate_id": record["candidate_id"],
        "target_entity_type": record["target_entity_type"],
        "authorized_scope": dict(record["scope"] or {}),
        "issuer_reference": record["issuer_reference"],
        "status": record["status"],
        "timestamp": record["created_at"],
    }


__all__ = [
    "AUTHORIZATION_RECORD_FIELDS",
    "AUTHORIZATION_STATUSES",
    "PROHIBITED_AUTHORIZATION_EFFECT_KEYS",
    "authorization_record_to_execution_input",
    "build_authorization_record",
    "validate_authorization_record",
]

