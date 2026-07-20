"""Build review records for candidates without approving Entity activation.

Agent-readable contract:
- Review status is independent from proposal, registration, and lifecycle state.
- APPROVED means the proposal review passed only.
- APPROVED does not register an Entity, assign identity, activate lifecycle,
  grant a capability, or grant permission.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CANDIDATE_REVIEW_FIELDS = (
    "review_id",
    "candidate_id",
    "reviewer_reference",
    "review_status",
    "review_notes",
)
REVIEW_STATUSES = ("PENDING", "APPROVED", "REJECTED")


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_candidate_review(record: Mapping[str, Any]) -> list[str]:
    """Return review errors without producing approval side effects."""

    errors: list[str] = []
    missing = [field for field in CANDIDATE_REVIEW_FIELDS if field not in record]
    extra = sorted(set(record) - set(CANDIDATE_REVIEW_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("review_id", "candidate_id", "reviewer_reference"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if not isinstance(record.get("review_notes"), str):
        errors.append("review_notes must be a string")
    if record.get("review_status") not in REVIEW_STATUSES:
        errors.append("review_status is not supported")
    return errors


def build_candidate_review(
    *,
    review_id: str,
    candidate_id: str,
    reviewer_reference: str,
    review_notes: str,
    review_status: str = "PENDING",
) -> dict[str, str]:
    """Return an independent candidate review record."""

    record = {
        "review_id": review_id,
        "candidate_id": candidate_id,
        "reviewer_reference": reviewer_reference,
        "review_status": review_status,
        "review_notes": review_notes,
    }
    errors = validate_candidate_review(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANDIDATE_REVIEW_FIELDS",
    "REVIEW_STATUSES",
    "build_candidate_review",
    "validate_candidate_review",
]
