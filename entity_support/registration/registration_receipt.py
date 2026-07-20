"""Build append-only-compatible Registration Receipt mappings.

Agent-readable contract:
- A receipt records one registration attempt; it does not activate an Entity.
- ``SUCCESS`` requires an attributable ``entity_id`` and authorization reference.
- ``FAILED`` preserves the failed attempt and cannot contain an ``entity_id``.
- Receipt retention is caller-controlled through an explicit append-only sink.
- This module writes no registry, Evidence, Permission, Runtime, or Agent state.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence
from copy import deepcopy
from datetime import datetime
from typing import Any

REGISTRATION_RECEIPT_FIELDS = (
    "registration_id",
    "entity_id",
    "authorization_reference",
    "timestamp",
    "status",
)
REGISTRATION_RECEIPT_STATUSES = frozenset({"SUCCESS", "FAILED"})


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_timezone_aware_timestamp(value: object) -> bool:
    if not _is_non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_registration_receipt(receipt: Mapping[str, Any]) -> list[str]:
    """Return deterministic receipt errors without persisting the attempt."""

    errors: list[str] = []
    missing = [field for field in REGISTRATION_RECEIPT_FIELDS if field not in receipt]
    extra = sorted(set(receipt) - set(REGISTRATION_RECEIPT_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    if not _is_non_empty_string(receipt.get("registration_id")):
        errors.append("registration_id must be a non-empty string")
    if not _is_timezone_aware_timestamp(receipt.get("timestamp")):
        errors.append("timestamp must be a timezone-aware ISO 8601 string")

    status = receipt.get("status")
    if status not in REGISTRATION_RECEIPT_STATUSES:
        errors.append("status must be SUCCESS or FAILED")

    entity_id = receipt.get("entity_id")
    authorization_reference = receipt.get("authorization_reference")
    if status == "SUCCESS":
        if not _is_non_empty_string(entity_id):
            errors.append("SUCCESS requires entity_id")
        if not _is_non_empty_string(authorization_reference):
            errors.append("SUCCESS requires authorization_reference")
    if status == "FAILED" and entity_id is not None:
        errors.append("FAILED receipt must not claim entity_id")
    if authorization_reference is not None and not _is_non_empty_string(
        authorization_reference
    ):
        errors.append("authorization_reference must be null or a non-empty string")
    return errors


def build_registration_receipt(
    *,
    registration_id: str,
    entity_id: str | None,
    authorization_reference: str | None,
    timestamp: str,
    status: str,
) -> dict[str, str | None]:
    """Return one validated receipt without creating canonical Evidence."""

    receipt = {
        "registration_id": registration_id,
        "entity_id": entity_id,
        "authorization_reference": authorization_reference,
        "timestamp": timestamp,
        "status": status,
    }
    errors = validate_registration_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def retain_registration_receipt(
    receipt: Mapping[str, Any],
    receipt_log: MutableSequence[dict[str, str | None]],
) -> None:
    """Append a validated copy to a caller-provided receipt log.

    No delete or overwrite operation is supplied. The sink is deliberately
    injected so this support layer never writes a canonical DBOS registry.
    """

    errors = validate_registration_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    receipt_log.append(deepcopy(dict(receipt)))


__all__ = [
    "REGISTRATION_RECEIPT_FIELDS",
    "REGISTRATION_RECEIPT_STATUSES",
    "build_registration_receipt",
    "retain_registration_receipt",
    "validate_registration_receipt",
]

