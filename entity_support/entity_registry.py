"""Build and validate non-persistent Digital Entity registration records.

Agent-readable contract:
- This module creates record mappings only; it does not write registry files.
- Registration defaults to ``PROPOSED`` and rejects every other lifecycle state.
- A returned mapping is not a Digital Entity, Agent, Runtime, or authorization.
- ``entity_id`` must already come from an accountable DBOS registration flow.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ENTITY_REGISTRATION_FIELDS = (
    "entity_id",
    "entity_type",
    "owner_reference",
    "lifecycle_state",
)
SUPPORTED_ENTITY_TYPES = frozenset(
    {"agent", "protocol", "repository", "service", "artifact", "governance_system"}
)
DEFAULT_LIFECYCLE_STATE = "PROPOSED"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_entity_registration(record: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for one registration record.

    The support layer intentionally accepts only ``PROPOSED`` registrations.
    Later lifecycle transitions belong to separately authorized DBOS lifecycle
    governance and are outside this module.
    """

    errors: list[str] = []
    missing = [field for field in ENTITY_REGISTRATION_FIELDS if field not in record]
    extra = sorted(set(record) - set(ENTITY_REGISTRATION_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    if not _is_non_empty_string(record.get("entity_id")):
        errors.append("entity_id must be a non-empty string")
    if record.get("entity_type") not in SUPPORTED_ENTITY_TYPES:
        errors.append("entity_type must use the existing DBOS controlled classification")
    if not _is_non_empty_string(record.get("owner_reference")):
        errors.append("owner_reference must be a non-empty string")
    if record.get("lifecycle_state") != DEFAULT_LIFECYCLE_STATE:
        errors.append("registration support requires lifecycle_state=PROPOSED")
    return errors


def build_entity_registration_record(
    *,
    entity_id: str,
    entity_type: str,
    owner_reference: str,
    lifecycle_state: str = DEFAULT_LIFECYCLE_STATE,
) -> dict[str, str]:
    """Return a validated, non-persistent registration record mapping."""

    record = {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "owner_reference": owner_reference,
        "lifecycle_state": lifecycle_state,
    }
    errors = validate_entity_registration(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "DEFAULT_LIFECYCLE_STATE",
    "ENTITY_REGISTRATION_FIELDS",
    "SUPPORTED_ENTITY_TYPES",
    "build_entity_registration_record",
    "validate_entity_registration",
]
