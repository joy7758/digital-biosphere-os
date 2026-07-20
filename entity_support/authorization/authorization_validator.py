"""Validate whether a persisted Authorization Record is usable for registration.

Agent-readable contract:
- Structural validity is separate from current authorization effectiveness.
- Only unexpired ``AUTHORIZED`` records with registration-only scope are usable.
- ``REVOKED``, ``REJECTED``, ``PENDING``, expired, or unknown records fail closed.
- A valid Authorization Record still grants no Permission or activation effect.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from entity_support.authorization.authorization_record import (
    validate_authorization_record,
)

REQUIRED_REGISTRATION_SCOPE = {
    "operation": "entity_registration",
    "lifecycle_target": "REGISTERED",
}


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def validate_authorization_for_registration(
    record: Mapping[str, Any],
    *,
    at_time: str | None = None,
) -> list[str]:
    """Return errors when a record cannot authorize one registration attempt."""

    errors = list(validate_authorization_record(record))
    if record.get("status") != "AUTHORIZED":
        errors.append("registration requires status=AUTHORIZED")
    if record.get("revocation_reference") is not None:
        errors.append("revoked authorization cannot be used")

    scope = record.get("scope")
    if not isinstance(scope, Mapping):
        errors.append("registration authorization requires scope mapping")
    else:
        for key, expected in REQUIRED_REGISTRATION_SCOPE.items():
            if scope.get(key) != expected:
                errors.append(f"scope.{key} must be {expected}")

    reference_time = _parse_timestamp(at_time) if at_time is not None else datetime.now(
        timezone.utc
    )
    if reference_time is None:
        errors.append("at_time must be a timezone-aware ISO 8601 string")
    expires_at = _parse_timestamp(record.get("expires_at"))
    if expires_at is not None and reference_time is not None and reference_time >= expires_at:
        errors.append("authorization is expired")
    return errors


def is_authorization_effective(
    record: Mapping[str, Any],
    *,
    at_time: str | None = None,
) -> bool:
    """Return True only for a currently usable registration authorization."""

    return not validate_authorization_for_registration(record, at_time=at_time)


__all__ = [
    "REQUIRED_REGISTRATION_SCOPE",
    "is_authorization_effective",
    "validate_authorization_for_registration",
]

