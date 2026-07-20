"""Build Capability Boundary records without granting permission.

Agent-readable contract:
- DECLARED, VERIFIED, and AUTHORIZED are record states, not executions.
- VERIFIED requires a verification reference.
- AUTHORIZED requires separate verification and authorization references.
- Authorization is never treated as Permission; ``permission_effect`` is
  fixed to ``NONE`` and grant fields fail closed.
- The module does not persist, assign, activate, revoke, or execute capability.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.capability_registry import SUPPORTED_RISK_LEVELS

CAPABILITY_BOUNDARY_STATES = ("DECLARED", "VERIFIED", "AUTHORIZED")
CAPABILITY_BOUNDARY_FIELDS = (
    "boundary_record_id",
    "capability_id",
    "entity_id",
    "capability_name",
    "scope",
    "constraints",
    "risk_level",
    "capability_state",
    "declaration_reference",
    "verification_reference",
    "authorization_reference",
    "permission_effect",
)
DEFAULT_CAPABILITY_STATE = "DECLARED"
NO_PERMISSION_EFFECT = "NONE"
PROHIBITED_PERMISSION_FIELDS = frozenset(
    {
        "permission",
        "permission_id",
        "permission_status",
        "permission_grant",
        "permissions",
    }
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_structure(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, (list, tuple, dict)) and bool(value)


def validate_capability_boundary(record: Mapping[str, Any]) -> list[str]:
    """Return boundary errors without changing capability or permission state."""

    errors: list[str] = []
    missing = [field for field in CAPABILITY_BOUNDARY_FIELDS if field not in record]
    extra = sorted(set(record) - set(CAPABILITY_BOUNDARY_FIELDS))
    prohibited = sorted(set(record) & PROHIBITED_PERMISSION_FIELDS)
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    if prohibited:
        errors.append(f"capability boundary cannot contain permission fields: {prohibited}")

    for field in (
        "boundary_record_id",
        "capability_id",
        "entity_id",
        "capability_name",
        "declaration_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    for field in ("scope", "constraints"):
        if not _is_non_empty_structure(record.get(field)):
            errors.append(f"{field} must be an explicit non-empty structure")

    state = record.get("capability_state")
    if state not in CAPABILITY_BOUNDARY_STATES:
        errors.append("capability_state must be DECLARED, VERIFIED, or AUTHORIZED")
    if record.get("risk_level") not in SUPPORTED_RISK_LEVELS:
        errors.append("risk_level must use the bounded DBOS risk vocabulary")
    if record.get("permission_effect") != NO_PERMISSION_EFFECT:
        errors.append("permission_effect must remain NONE")

    verification_reference = record.get("verification_reference")
    authorization_reference = record.get("authorization_reference")
    for field, value in (
        ("verification_reference", verification_reference),
        ("authorization_reference", authorization_reference),
    ):
        if value is not None and not _is_non_empty_string(value):
            errors.append(f"{field} must be null or a non-empty string")

    if state == "DECLARED":
        if verification_reference is not None or authorization_reference is not None:
            errors.append("DECLARED cannot claim verification or authorization")
    elif state == "VERIFIED":
        if not _is_non_empty_string(verification_reference):
            errors.append("VERIFIED requires verification_reference")
        if authorization_reference is not None:
            errors.append("VERIFIED cannot claim authorization")
    elif state == "AUTHORIZED":
        if not _is_non_empty_string(verification_reference):
            errors.append("AUTHORIZED requires verification_reference")
        if not _is_non_empty_string(authorization_reference):
            errors.append("AUTHORIZED requires authorization_reference")
    return errors


def build_capability_boundary_record(
    *,
    boundary_record_id: str,
    capability_id: str,
    entity_id: str,
    capability_name: str,
    scope: Any,
    constraints: Any,
    declaration_reference: str,
    risk_level: str = "UNKNOWN",
    capability_state: str = DEFAULT_CAPABILITY_STATE,
    verification_reference: str | None = None,
    authorization_reference: str | None = None,
    permission_effect: str = NO_PERMISSION_EFFECT,
) -> dict[str, Any]:
    """Return a capability boundary record, never a permission grant."""

    record = {
        "boundary_record_id": boundary_record_id,
        "capability_id": capability_id,
        "entity_id": entity_id,
        "capability_name": capability_name,
        "scope": scope,
        "constraints": constraints,
        "risk_level": risk_level,
        "capability_state": capability_state,
        "declaration_reference": declaration_reference,
        "verification_reference": verification_reference,
        "authorization_reference": authorization_reference,
        "permission_effect": permission_effect,
    }
    errors = validate_capability_boundary(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CAPABILITY_BOUNDARY_FIELDS",
    "CAPABILITY_BOUNDARY_STATES",
    "DEFAULT_CAPABILITY_STATE",
    "NO_PERMISSION_EFFECT",
    "PROHIBITED_PERMISSION_FIELDS",
    "build_capability_boundary_record",
    "validate_capability_boundary",
]
