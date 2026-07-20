"""Build and validate references into the existing DBOS evidence system.

Agent-readable contract:
- This module creates references, not canonical Evidence Objects.
- The safe integrity state is ``UNKNOWN``; only ``UNKNOWN`` and ``PENDING``
  are accepted by this pre-evidence support layer.
- Evidence validation and integrity promotion remain with existing DBOS
  evidence and verification mechanisms.
- No evidence file, digest, observation, or truth claim is generated.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

EVIDENCE_REFERENCE_FIELDS = (
    "evidence_id",
    "execution_id",
    "reference",
    "integrity_status",
)
DEFAULT_INTEGRITY_STATUS = "UNKNOWN"
SUPPORTED_REFERENCE_INTEGRITY_STATUSES = frozenset({"UNKNOWN", "PENDING"})


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_evidence_reference(record: Mapping[str, Any]) -> list[str]:
    """Return errors without validating or promoting canonical evidence."""

    errors: list[str] = []
    missing = [field for field in EVIDENCE_REFERENCE_FIELDS if field not in record]
    extra = sorted(set(record) - set(EVIDENCE_REFERENCE_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("evidence_id", "execution_id", "reference"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("integrity_status") not in SUPPORTED_REFERENCE_INTEGRITY_STATUSES:
        errors.append("integrity_status must remain UNKNOWN or PENDING")
    return errors


def build_evidence_reference(
    *,
    evidence_id: str,
    execution_id: str,
    reference: str,
    integrity_status: str = DEFAULT_INTEGRITY_STATUS,
) -> dict[str, str]:
    """Return a non-canonical evidence-reference mapping."""

    record = {
        "evidence_id": evidence_id,
        "execution_id": execution_id,
        "reference": reference,
        "integrity_status": integrity_status,
    }
    errors = validate_evidence_reference(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "DEFAULT_INTEGRITY_STATUS",
    "EVIDENCE_REFERENCE_FIELDS",
    "SUPPORTED_REFERENCE_INTEGRITY_STATUSES",
    "build_evidence_reference",
    "validate_evidence_reference",
]
