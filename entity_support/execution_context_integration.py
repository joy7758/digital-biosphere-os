"""Project an inert execution record onto an existing DBOS context record.

Agent-readable contract:
- The caller supplies an already recorded context mapping; this module does not
  create or persist an Execution Context.
- The execution record must remain in CREATED state.
- The projection records IDs and references only; it does not start a Runtime,
  invoke a tool, create an Event, or claim an Execution Result.
- Invalid, revoked, or superseded contexts fail closed.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from entity_support.execution_registry import validate_execution_record

EXECUTION_CONTEXT_LINK_FIELDS = (
    "execution_id",
    "task_reference",
    "input_reference",
    "output_reference",
    "context_reference",
    "context_status",
    "execution_status",
    "runtime_effect",
)
USABLE_CONTEXT_STATUSES = frozenset({"proposed", "recorded", "validated"})
NO_RUNTIME_EFFECT = "NONE"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_execution_context_link(record: Mapping[str, Any]) -> list[str]:
    """Return errors without resolving, creating, or executing a context."""

    errors: list[str] = []
    missing = [field for field in EXECUTION_CONTEXT_LINK_FIELDS if field not in record]
    extra = sorted(set(record) - set(EXECUTION_CONTEXT_LINK_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in (
        "execution_id",
        "task_reference",
        "input_reference",
        "context_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    output_reference = record.get("output_reference")
    if output_reference is not None and not _is_non_empty_string(output_reference):
        errors.append("output_reference must be null or a non-empty string")
    if record.get("context_status") not in USABLE_CONTEXT_STATUSES:
        errors.append("context_status must be proposed, recorded, or validated")
    if record.get("execution_status") != "CREATED":
        errors.append("execution_status must remain CREATED")
    if record.get("runtime_effect") != NO_RUNTIME_EFFECT:
        errors.append("runtime_effect must remain NONE")
    return errors


def build_execution_context_link(
    execution_record: Mapping[str, Any],
    *,
    context_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a read-only projection onto one supplied existing context."""

    execution_errors = validate_execution_record(execution_record)
    if execution_errors:
        raise ValueError("invalid execution record: " + "; ".join(execution_errors))

    context_reference = execution_record.get("context_reference")
    if context_record.get("context_id") != context_reference:
        raise ValueError("context_record.context_id must match context_reference")
    context_status = context_record.get("status")
    if context_status not in USABLE_CONTEXT_STATUSES:
        raise ValueError("context record is not usable for a support-layer link")

    record = {
        "execution_id": execution_record.get("execution_id"),
        "task_reference": execution_record.get("task_reference"),
        "input_reference": execution_record.get("input_reference"),
        "output_reference": execution_record.get("output_reference"),
        "context_reference": context_reference,
        "context_status": context_status,
        "execution_status": execution_record.get("status"),
        "runtime_effect": NO_RUNTIME_EFFECT,
    }
    errors = validate_execution_context_link(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "EXECUTION_CONTEXT_LINK_FIELDS",
    "NO_RUNTIME_EFFECT",
    "USABLE_CONTEXT_STATUSES",
    "build_execution_context_link",
    "validate_execution_context_link",
]
