"""Build and validate non-granting Digital Entity capability records.

Agent-readable contract:
- A capability record is a declaration structure, not a capability grant.
- The safe default is ``UNVERIFIED``; ``AUTHORIZED`` is not a verification state.
- This module never creates permission, authorization, assignment, or execution.
- No registry or evidence file is read or written.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CAPABILITY_RECORD_FIELDS = (
    "capability_id",
    "entity_id",
    "capability_name",
    "scope",
    "constraints",
    "risk_level",
    "verification_status",
)
DEFAULT_RISK_LEVEL = "UNKNOWN"
DEFAULT_VERIFICATION_STATUS = "UNVERIFIED"
SUPPORTED_RISK_LEVELS = frozenset({"UNKNOWN", "LOW", "MODERATE", "HIGH", "CRITICAL"})
SUPPORTED_DECLARATION_VERIFICATION_STATUSES = frozenset({"UNVERIFIED", "PENDING"})


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_structure(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def validate_capability_record(record: Mapping[str, Any]) -> list[str]:
    """Return errors without deriving capability, authorization, or permission."""

    errors: list[str] = []
    missing = [field for field in CAPABILITY_RECORD_FIELDS if field not in record]
    extra = sorted(set(record) - set(CAPABILITY_RECORD_FIELDS), key=str)
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    for field in ("capability_id", "entity_id", "capability_name"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    for field in ("scope", "constraints"):
        if not _is_non_empty_structure(record.get(field)):
            errors.append(f"{field} must be an explicit non-empty structure")
    if record.get("risk_level") not in SUPPORTED_RISK_LEVELS:
        errors.append("risk_level must use the bounded DBOS risk vocabulary")
    if record.get("verification_status") not in SUPPORTED_DECLARATION_VERIFICATION_STATUSES:
        errors.append("verification_status must remain UNVERIFIED or PENDING")
    return errors


def build_capability_record(
    *,
    capability_id: str,
    entity_id: str,
    capability_name: str,
    scope: Any,
    constraints: Any,
    risk_level: str = DEFAULT_RISK_LEVEL,
    verification_status: str = DEFAULT_VERIFICATION_STATUS,
) -> dict[str, Any]:
    """Return one validated declaration record without granting capability."""

    record = {
        "capability_id": capability_id,
        "entity_id": entity_id,
        "capability_name": capability_name,
        "scope": scope,
        "constraints": constraints,
        "risk_level": risk_level,
        "verification_status": verification_status,
    }
    errors = validate_capability_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CAPABILITY_RECORD_FIELDS",
    "DEFAULT_RISK_LEVEL",
    "DEFAULT_VERIFICATION_STATUS",
    "SUPPORTED_DECLARATION_VERIFICATION_STATUSES",
    "SUPPORTED_RISK_LEVELS",
    "build_capability_record",
    "validate_capability_record",
]
