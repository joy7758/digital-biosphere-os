"""Link Evidence and Verification references without creating either object.

Agent-readable contract:
- Canonical Evidence remains owned by the existing DBOS evidence system.
- The link accepts only already validated support-layer reference mappings.
- Evidence integrity and Verification level remain UNKNOWN/PENDING/V0 here.
- The link has no truth, capability, permission, execution, or lifecycle effect.
- No evidence payload, digest, history, or verification decision is written.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.evidence_reference import validate_evidence_reference
from entity_support.verification_reference import validate_verification_reference

EVIDENCE_INTEGRATION_FIELDS = (
    "execution_id",
    "evidence_id",
    "evidence_reference",
    "integrity_status",
    "verification_id",
    "verification_status",
    "verification_level",
    "canonical_evidence_owner",
    "evidence_truth_effect",
    "permission_effect",
)
CANONICAL_EVIDENCE_OWNER = "DBOS_EXISTING_EVIDENCE_SYSTEM"
NO_EFFECT = "NONE"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_evidence_integration_link(record: Mapping[str, Any]) -> list[str]:
    """Return link errors without evaluating evidence or verification truth."""

    errors: list[str] = []
    missing = [field for field in EVIDENCE_INTEGRATION_FIELDS if field not in record]
    extra = sorted(set(record) - set(EVIDENCE_INTEGRATION_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("execution_id", "evidence_id", "evidence_reference", "verification_id"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("integrity_status") not in {"UNKNOWN", "PENDING"}:
        errors.append("integrity_status must remain UNKNOWN or PENDING")
    if record.get("verification_status") not in {"UNKNOWN", "PENDING"}:
        errors.append("verification_status must remain UNKNOWN or PENDING")
    if record.get("verification_level") != "V0":
        errors.append("verification_level must remain V0")
    if record.get("canonical_evidence_owner") != CANONICAL_EVIDENCE_OWNER:
        errors.append("canonical_evidence_owner must remain the existing DBOS evidence system")
    for field in ("evidence_truth_effect", "permission_effect"):
        if record.get(field) != NO_EFFECT:
            errors.append(f"{field} must remain NONE")
    return errors


def build_evidence_integration_link(
    evidence_record: Mapping[str, Any],
    verification_record: Mapping[str, Any],
) -> dict[str, str]:
    """Return a reference link without creating canonical Evidence."""

    evidence_errors = validate_evidence_reference(evidence_record)
    if evidence_errors:
        raise ValueError("invalid evidence reference: " + "; ".join(evidence_errors))
    verification_errors = validate_verification_reference(verification_record)
    if verification_errors:
        raise ValueError(
            "invalid verification reference: " + "; ".join(verification_errors)
        )
    if verification_record.get("evidence_id") != evidence_record.get("evidence_id"):
        raise ValueError("verification evidence_id must match evidence reference")

    record = {
        "execution_id": evidence_record["execution_id"],
        "evidence_id": evidence_record["evidence_id"],
        "evidence_reference": evidence_record["reference"],
        "integrity_status": evidence_record["integrity_status"],
        "verification_id": verification_record["verification_id"],
        "verification_status": verification_record["verification_status"],
        "verification_level": verification_record["verification_level"],
        "canonical_evidence_owner": CANONICAL_EVIDENCE_OWNER,
        "evidence_truth_effect": NO_EFFECT,
        "permission_effect": NO_EFFECT,
    }
    errors = validate_evidence_integration_link(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANONICAL_EVIDENCE_OWNER",
    "EVIDENCE_INTEGRATION_FIELDS",
    "NO_EFFECT",
    "build_evidence_integration_link",
    "validate_evidence_integration_link",
]
