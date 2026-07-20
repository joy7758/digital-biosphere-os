"""Build candidate proposal records without registering Digital Entities.

Agent-readable contract:
- A candidate_id identifies a proposal subject only; it is not an entity_id.
- PROPOSED is the only proposal state supported by this layer.
- The record declares no registration, activation, capability, or permission effect.
- The builder returns an in-memory mapping and writes no registry or evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CANDIDATE_PROPOSAL_FIELDS = (
    "candidate_id",
    "proposed_type",
    "role",
    "description",
    "proposer_reference",
    "status",
)
PROPOSAL_STATUSES = ("PROPOSED",)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_candidate_proposal(record: Mapping[str, Any]) -> list[str]:
    """Return proposal errors without creating identity or lifecycle state."""

    errors: list[str] = []
    missing = [field for field in CANDIDATE_PROPOSAL_FIELDS if field not in record]
    extra = sorted(set(record) - set(CANDIDATE_PROPOSAL_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in (
        "candidate_id",
        "proposed_type",
        "role",
        "description",
        "proposer_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("status") not in PROPOSAL_STATUSES:
        errors.append("status must remain PROPOSED")
    return errors


def build_candidate_proposal(
    *,
    candidate_id: str,
    proposed_type: str,
    role: str,
    description: str,
    proposer_reference: str,
    status: str = "PROPOSED",
) -> dict[str, str]:
    """Return a proposal-only record with no Entity registration effect."""

    record = {
        "candidate_id": candidate_id,
        "proposed_type": proposed_type,
        "role": role,
        "description": description,
        "proposer_reference": proposer_reference,
        "status": status,
    }
    errors = validate_candidate_proposal(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANDIDATE_PROPOSAL_FIELDS",
    "PROPOSAL_STATUSES",
    "build_candidate_proposal",
    "validate_candidate_proposal",
]
