"""Execute bounded in-memory Digital Entity registration transitions.

Agent-readable contract:
- Input must be an approved Candidate record plus an independently issued,
  complete, current ``AUTHORIZED`` Registration Authorization.
- Success creates one in-memory ``REGISTERED`` record and one receipt mapping.
- Failure returns and optionally retains a ``FAILED`` receipt; it never silently
  drops the attempt and never creates a partial Entity record.
- This module does not write ``registry/entities.yaml``, activate an Entity,
  grant Capability or Permission, create Agent/Runtime, execute a task, produce
  canonical Evidence, or call SAEE.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, MutableSequence
from datetime import datetime, timezone
from typing import Any

from entity_support.registration.registration_receipt import (
    build_registration_receipt,
    retain_registration_receipt,
)
from entity_support.registration.registration_validator import (
    derive_entity_id,
    validate_candidate_registration_source,
    validate_identity_continuity,
    validate_registered_entity_record,
    validate_registration_authorization_input,
)

REGISTRATION_EXECUTION_RESULT_FIELDS = (
    "entity_record",
    "receipt",
    "errors",
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _event_timestamp(value: str | None) -> tuple[str, list[str]]:
    if value is None:
        return datetime.now(timezone.utc).isoformat(), []
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return datetime.now(timezone.utc).isoformat(), [
            "registered_at must be a timezone-aware ISO 8601 string"
        ]
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return datetime.now(timezone.utc).isoformat(), [
            "registered_at must be a timezone-aware ISO 8601 string"
        ]
    return value, []


def _derive_registration_id(
    candidate_id: object,
    authorization_id: object,
    status: str,
) -> str:
    candidate_component = candidate_id.strip() if _is_non_empty_string(candidate_id) else "missing-candidate"
    authorization_component = authorization_id.strip() if _is_non_empty_string(authorization_id) else "missing-authorization"
    material = f"{candidate_component}\0{authorization_component}\0{status}".encode("utf-8")
    return f"dbio:registration:{hashlib.sha256(material).hexdigest()[:24]}"


def _retain_if_requested(
    receipt: Mapping[str, Any],
    receipt_log: MutableSequence[dict[str, str | None]] | None,
) -> None:
    if receipt_log is not None:
        retain_registration_receipt(receipt, receipt_log)


def execute_entity_registration(
    *,
    candidate: Mapping[str, Any],
    authorization: Mapping[str, Any],
    registered_at: str | None = None,
    receipt_log: MutableSequence[dict[str, str | None]] | None = None,
) -> dict[str, object]:
    """Return a success or failure result without persistent DBOS side effects."""

    timestamp, timestamp_errors = _event_timestamp(registered_at)
    errors = list(timestamp_errors)
    errors.extend(validate_candidate_registration_source(candidate))
    errors.extend(validate_registration_authorization_input(authorization))

    candidate_id = candidate.get("candidate_id")
    authorization_id = authorization.get("authorization_id")
    request = candidate.get("registration_request")
    if authorization.get("candidate_id") != candidate_id:
        errors.append("authorization candidate_id must match candidate source")
    if isinstance(request, Mapping) and authorization.get(
        "target_entity_type"
    ) != request.get("requested_entity_type"):
        errors.append("authorization target_entity_type must match candidate request")

    if errors:
        receipt = build_registration_receipt(
            registration_id=_derive_registration_id(
                candidate_id, authorization_id, "FAILED"
            ),
            entity_id=None,
            authorization_reference=(
                str(authorization_id) if _is_non_empty_string(authorization_id) else None
            ),
            timestamp=timestamp,
            status="FAILED",
        )
        _retain_if_requested(receipt, receipt_log)
        return {
            "entity_record": None,
            "receipt": receipt,
            "errors": tuple(errors),
        }

    entity_id = derive_entity_id(str(candidate_id), str(authorization_id))
    entity_record = {
        "entity_id": entity_id,
        "candidate_reference": candidate_id,
        "authorization_reference": authorization_id,
        "registered_at": timestamp,
        "entity_type": authorization["target_entity_type"],
        "lifecycle_state": "REGISTERED",
    }
    output_errors = validate_registered_entity_record(entity_record)
    provisional_receipt = build_registration_receipt(
        registration_id=_derive_registration_id(
            candidate_id, authorization_id, "SUCCESS"
        ),
        entity_id=entity_id,
        authorization_reference=str(authorization_id),
        timestamp=timestamp,
        status="SUCCESS",
    )
    output_errors.extend(
        validate_identity_continuity(
            candidate=candidate,
            authorization=authorization,
            entity_record=entity_record,
            receipt=provisional_receipt,
        )
    )
    if output_errors:
        failed_receipt = build_registration_receipt(
            registration_id=_derive_registration_id(
                candidate_id, authorization_id, "FAILED"
            ),
            entity_id=None,
            authorization_reference=str(authorization_id),
            timestamp=timestamp,
            status="FAILED",
        )
        _retain_if_requested(failed_receipt, receipt_log)
        return {
            "entity_record": None,
            "receipt": failed_receipt,
            "errors": tuple(output_errors),
        }

    _retain_if_requested(provisional_receipt, receipt_log)
    return {
        "entity_record": entity_record,
        "receipt": provisional_receipt,
        "errors": (),
    }


__all__ = [
    "REGISTRATION_EXECUTION_RESULT_FIELDS",
    "execute_entity_registration",
]

