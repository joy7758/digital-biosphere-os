"""Build fail-closed Digital Entity lifecycle transition records.

Agent-readable contract:
- This module records a requested transition; it never mutates entity state.
- Every transition requires an attributable source and verification reference.
- ACTIVE, ADAPTED, and RETIRED require explicit authorization references.
- EVALUATED and ADAPTED require an external evaluation reference; this module
  does not call SAEE or generate an evaluation.
- Historical transition records are append-only inputs to future DBOS
  governance; no deletion or overwrite operation is provided.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LIFECYCLE_STATES = (
    "PROPOSED",
    "REGISTERED",
    "VERIFIED",
    "ACTIVE",
    "EVALUATED",
    "ADAPTED",
    "RETIRED",
)
LIFECYCLE_TRANSITION_FIELDS = (
    "transition_id",
    "entity_id",
    "from_state",
    "to_state",
    "source_reference",
    "verification_reference",
    "authorization_reference",
    "evaluation_reference",
    "decision_reference",
)
ALLOWED_TRANSITIONS = {
    "PROPOSED": frozenset({"REGISTERED"}),
    "REGISTERED": frozenset({"VERIFIED", "RETIRED"}),
    "VERIFIED": frozenset({"ACTIVE", "RETIRED"}),
    "ACTIVE": frozenset({"EVALUATED", "RETIRED"}),
    "EVALUATED": frozenset({"ADAPTED", "RETIRED"}),
    "ADAPTED": frozenset({"ACTIVE", "RETIRED"}),
    "RETIRED": frozenset(),
}


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_optional_reference(
    record: Mapping[str, Any], field: str, errors: list[str]
) -> None:
    value = record.get(field)
    if value is not None and not _is_non_empty_string(value):
        errors.append(f"{field} must be null or a non-empty string")


def validate_lifecycle_transition(record: Mapping[str, Any]) -> list[str]:
    """Return errors without applying the lifecycle transition."""

    errors: list[str] = []
    missing = [field for field in LIFECYCLE_TRANSITION_FIELDS if field not in record]
    extra = sorted(set(record) - set(LIFECYCLE_TRANSITION_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    for field in (
        "transition_id",
        "entity_id",
        "source_reference",
        "verification_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    for field in (
        "authorization_reference",
        "evaluation_reference",
        "decision_reference",
    ):
        _validate_optional_reference(record, field, errors)

    from_state = record.get("from_state")
    to_state = record.get("to_state")
    if from_state not in LIFECYCLE_STATES:
        errors.append("from_state must use the Digital Entity lifecycle vocabulary")
    if to_state not in LIFECYCLE_STATES:
        errors.append("to_state must use the Digital Entity lifecycle vocabulary")
    if from_state in ALLOWED_TRANSITIONS and to_state not in ALLOWED_TRANSITIONS[from_state]:
        errors.append(f"transition {from_state!r} -> {to_state!r} is not allowed")

    if to_state in {"ACTIVE", "ADAPTED", "RETIRED"} and not _is_non_empty_string(
        record.get("authorization_reference")
    ):
        errors.append(f"{to_state} requires authorization_reference")
    if to_state in {"EVALUATED", "ADAPTED"} and not _is_non_empty_string(
        record.get("evaluation_reference")
    ):
        errors.append(f"{to_state} requires evaluation_reference")
    if to_state == "ADAPTED" and not _is_non_empty_string(record.get("decision_reference")):
        errors.append("ADAPTED requires decision_reference")
    return errors


def build_lifecycle_transition_record(
    *,
    transition_id: str,
    entity_id: str,
    from_state: str,
    to_state: str,
    source_reference: str,
    verification_reference: str,
    authorization_reference: str | None = None,
    evaluation_reference: str | None = None,
    decision_reference: str | None = None,
) -> dict[str, str | None]:
    """Return one validated transition record without changing entity state."""

    record = {
        "transition_id": transition_id,
        "entity_id": entity_id,
        "from_state": from_state,
        "to_state": to_state,
        "source_reference": source_reference,
        "verification_reference": verification_reference,
        "authorization_reference": authorization_reference,
        "evaluation_reference": evaluation_reference,
        "decision_reference": decision_reference,
    }
    errors = validate_lifecycle_transition(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "ALLOWED_TRANSITIONS",
    "LIFECYCLE_STATES",
    "LIFECYCLE_TRANSITION_FIELDS",
    "build_lifecycle_transition_record",
    "validate_lifecycle_transition",
]
