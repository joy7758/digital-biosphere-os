"""Build and validate non-authorizing DBOS verification references.

Agent-readable contract:
- The safe defaults are ``PENDING`` and ``V0``.
- A reference does not perform verification or promote C/E/V levels.
- Verification never grants capability, authorization, or permission.
- Only the four contract fields are accepted; hidden grant fields fail closed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

VERIFICATION_REFERENCE_FIELDS = (
    "verification_id",
    "evidence_id",
    "verification_status",
    "verification_level",
)
DEFAULT_VERIFICATION_STATUS = "PENDING"
DEFAULT_VERIFICATION_LEVEL = "V0"
SUPPORTED_REFERENCE_VERIFICATION_STATUSES = frozenset({"UNKNOWN", "PENDING"})
SUPPORTED_REFERENCE_VERIFICATION_LEVELS = frozenset({"V0"})
PROHIBITED_GRANT_FIELDS = frozenset(
    {
        "permission",
        "permission_status",
        "authorization",
        "authorization_status",
        "capability",
        "capability_id",
        "capability_status",
    }
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_verification_reference(record: Mapping[str, Any]) -> list[str]:
    """Return errors and reject any capability or permission derivation."""

    errors: list[str] = []
    missing = [field for field in VERIFICATION_REFERENCE_FIELDS if field not in record]
    extra = sorted(set(record) - set(VERIFICATION_REFERENCE_FIELDS))
    prohibited = sorted(set(record) & PROHIBITED_GRANT_FIELDS)
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    if prohibited:
        errors.append(f"verification cannot derive grant fields: {prohibited}")
    for field in ("verification_id", "evidence_id"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("verification_status") not in SUPPORTED_REFERENCE_VERIFICATION_STATUSES:
        errors.append("verification_status must remain UNKNOWN or PENDING")
    if record.get("verification_level") not in SUPPORTED_REFERENCE_VERIFICATION_LEVELS:
        errors.append("verification_level must remain V0")
    return errors


def build_verification_reference(
    *,
    verification_id: str,
    evidence_id: str,
    verification_status: str = DEFAULT_VERIFICATION_STATUS,
    verification_level: str = DEFAULT_VERIFICATION_LEVEL,
) -> dict[str, str]:
    """Return a pending V0 reference without performing verification."""

    record = {
        "verification_id": verification_id,
        "evidence_id": evidence_id,
        "verification_status": verification_status,
        "verification_level": verification_level,
    }
    errors = validate_verification_reference(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "DEFAULT_VERIFICATION_LEVEL",
    "DEFAULT_VERIFICATION_STATUS",
    "PROHIBITED_GRANT_FIELDS",
    "SUPPORTED_REFERENCE_VERIFICATION_LEVELS",
    "SUPPORTED_REFERENCE_VERIFICATION_STATUSES",
    "VERIFICATION_REFERENCE_FIELDS",
    "build_verification_reference",
    "validate_verification_reference",
]
