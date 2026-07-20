"""Build and validate inert Digital Entity execution records.

Agent-readable contract:
- The only construction state is ``CREATED``.
- Building a record never runs a task, tool, model, process, or Runtime.
- DBOS remains the canonical execution-record owner.
- Completion, success, failure, and retry transitions are deliberately absent.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

EXECUTION_RECORD_FIELDS = (
    "execution_id",
    "entity_id",
    "task_reference",
    "input_reference",
    "output_reference",
    "context_reference",
    "status",
)
DEFAULT_EXECUTION_STATUS = "CREATED"


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_execution_record(record: Mapping[str, Any]) -> list[str]:
    """Return errors for an inert execution-record declaration."""

    errors: list[str] = []
    missing = [field for field in EXECUTION_RECORD_FIELDS if field not in record]
    extra = sorted(set(record) - set(EXECUTION_RECORD_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    for field in (
        "execution_id",
        "entity_id",
        "task_reference",
        "input_reference",
        "context_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    output_reference = record.get("output_reference")
    if output_reference is not None and not _is_non_empty_string(output_reference):
        errors.append("output_reference must be null or a non-empty string")
    if record.get("status") != DEFAULT_EXECUTION_STATUS:
        errors.append("execution support requires status=CREATED")
    return errors


def build_execution_record(
    *,
    execution_id: str,
    entity_id: str,
    task_reference: str,
    input_reference: str,
    context_reference: str,
    output_reference: str | None = None,
    status: str = DEFAULT_EXECUTION_STATUS,
) -> dict[str, str | None]:
    """Return an inert DBOS execution-record mapping without executing."""

    record = {
        "execution_id": execution_id,
        "entity_id": entity_id,
        "task_reference": task_reference,
        "input_reference": input_reference,
        "output_reference": output_reference,
        "context_reference": context_reference,
        "status": status,
    }
    errors = validate_execution_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "DEFAULT_EXECUTION_STATUS",
    "EXECUTION_RECORD_FIELDS",
    "build_execution_record",
    "validate_execution_record",
]
