"""Build candidate registration records without creating Digital Entities.

Agent-readable contract:
- A candidate_reference is not an entity_id or canonical identity.
- Proposal review and registration request are separate states.
- Registration requests may be NOT_SUBMITTED, PENDING, or REJECTED here;
  this prototype cannot approve or apply registration.
- The only requestable lifecycle target is REGISTERED, never ACTIVE.
- No canonical registry, lifecycle, capability, permission, or evidence is changed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.entity_registry import SUPPORTED_ENTITY_TYPES

CANDIDATE_REGISTRATION_FIELDS = (
    "proposal_id",
    "candidate_reference",
    "requested_entity_type",
    "owner_reference",
    "proposal_reference",
    "review_status",
    "review_reference",
    "registration_request_status",
    "registration_request_reference",
    "requested_lifecycle_state",
    "current_effect",
)
REVIEW_STATUSES = ("REVIEW_PENDING", "UNDER_REVIEW", "APPROVED", "REJECTED")
REGISTRATION_REQUEST_STATUSES = ("NOT_SUBMITTED", "PENDING", "REJECTED")
NO_CURRENT_EFFECT = "NONE"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _optional_reference_is_valid(value: object) -> bool:
    return value is None or _is_non_empty_string(value)


def validate_candidate_registration(record: Mapping[str, Any]) -> list[str]:
    """Return errors without creating identity or applying registration."""

    errors: list[str] = []
    missing = [field for field in CANDIDATE_REGISTRATION_FIELDS if field not in record]
    extra = sorted(set(record) - set(CANDIDATE_REGISTRATION_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in (
        "proposal_id",
        "candidate_reference",
        "owner_reference",
        "proposal_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("requested_entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("requested_entity_type must use the existing DBOS classification")
    for field in ("review_reference", "registration_request_reference"):
        if not _optional_reference_is_valid(record.get(field)):
            errors.append(f"{field} must be null or a non-empty string")

    review_status = record.get("review_status")
    request_status = record.get("registration_request_status")
    review_reference = record.get("review_reference")
    request_reference = record.get("registration_request_reference")
    if review_status not in REVIEW_STATUSES:
        errors.append("review_status is not supported")
    if request_status not in REGISTRATION_REQUEST_STATUSES:
        errors.append("registration_request_status is not supported")
    if review_status in {"UNDER_REVIEW", "APPROVED", "REJECTED"} and not _is_non_empty_string(
        review_reference
    ):
        errors.append(f"{review_status} requires review_reference")
    if review_status == "REVIEW_PENDING" and review_reference is not None:
        errors.append("REVIEW_PENDING cannot claim a review_reference")
    if request_status == "NOT_SUBMITTED" and request_reference is not None:
        errors.append("NOT_SUBMITTED cannot claim a registration_request_reference")
    if request_status in {"PENDING", "REJECTED"} and not _is_non_empty_string(
        request_reference
    ):
        errors.append(f"{request_status} requires registration_request_reference")
    if request_status == "PENDING" and review_status != "APPROVED":
        errors.append("PENDING registration request requires APPROVED proposal review")
    if record.get("requested_lifecycle_state") != "REGISTERED":
        errors.append("candidate request may target REGISTERED only")
    if record.get("current_effect") != NO_CURRENT_EFFECT:
        errors.append("current_effect must remain NONE")
    return errors


def build_candidate_registration_record(
    *,
    proposal_id: str,
    candidate_reference: str,
    requested_entity_type: str,
    owner_reference: str,
    proposal_reference: str,
    review_status: str = "REVIEW_PENDING",
    review_reference: str | None = None,
    registration_request_status: str = "NOT_SUBMITTED",
    registration_request_reference: str | None = None,
    requested_lifecycle_state: str = "REGISTERED",
    current_effect: str = NO_CURRENT_EFFECT,
) -> dict[str, str | None]:
    """Return a candidate workflow record with no identity or lifecycle effect."""

    record = {
        "proposal_id": proposal_id,
        "candidate_reference": candidate_reference,
        "requested_entity_type": requested_entity_type,
        "owner_reference": owner_reference,
        "proposal_reference": proposal_reference,
        "review_status": review_status,
        "review_reference": review_reference,
        "registration_request_status": registration_request_status,
        "registration_request_reference": registration_request_reference,
        "requested_lifecycle_state": requested_lifecycle_state,
        "current_effect": current_effect,
    }
    errors = validate_candidate_registration(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANDIDATE_REGISTRATION_FIELDS",
    "NO_CURRENT_EFFECT",
    "REGISTRATION_REQUEST_STATUSES",
    "REVIEW_STATUSES",
    "build_candidate_registration_record",
    "validate_candidate_registration",
]
