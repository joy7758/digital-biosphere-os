"""Build registration request records without registering Digital Entities.

Agent-readable contract:
- A request references a candidate and an existing DBOS entity classification.
- CREATED, SUBMITTED, ACCEPTED, and REJECTED are request workflow states.
- ACCEPTED means the request was accepted only; it is not REGISTERED or ACTIVE.
- No identity, lifecycle, capability, permission, runtime, or evidence is changed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.entity_registry import SUPPORTED_ENTITY_TYPES

CANDIDATE_REGISTRATION_REQUEST_FIELDS = (
    "request_id",
    "candidate_id",
    "requested_entity_type",
    "mapping_reference",
    "status",
)
REGISTRATION_REQUEST_STATUSES = ("CREATED", "SUBMITTED", "ACCEPTED", "REJECTED")


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_candidate_registration_request(record: Mapping[str, Any]) -> list[str]:
    """Return request errors without applying registration."""

    errors: list[str] = []
    missing = [
        field for field in CANDIDATE_REGISTRATION_REQUEST_FIELDS if field not in record
    ]
    extra = sorted(set(record) - set(CANDIDATE_REGISTRATION_REQUEST_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("request_id", "candidate_id", "mapping_reference"):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if record.get("requested_entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("requested_entity_type must use the existing DBOS classification")
    if record.get("status") not in REGISTRATION_REQUEST_STATUSES:
        errors.append("status is not supported")
    return errors


def build_candidate_registration_request(
    *,
    request_id: str,
    candidate_id: str,
    requested_entity_type: str,
    mapping_reference: str,
    status: str = "CREATED",
) -> dict[str, str]:
    """Return a request record with no registration or activation effect."""

    record = {
        "request_id": request_id,
        "candidate_id": candidate_id,
        "requested_entity_type": requested_entity_type,
        "mapping_reference": mapping_reference,
        "status": status,
    }
    errors = validate_candidate_registration_request(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANDIDATE_REGISTRATION_REQUEST_FIELDS",
    "REGISTRATION_REQUEST_STATUSES",
    "build_candidate_registration_request",
    "validate_candidate_registration_request",
]
