"""Inert Execution Object record; it cannot execute a task or tool."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from sdk.objects.base import BaseObject, freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class ExecutionObject(BaseObject):
    """Caller-supplied execution record, not an execution result or engine."""

    execution_id: str
    entity_reference: Mapping[str, Any]
    task_reference: Mapping[str, Any]
    context_reference: Mapping[str, Any]
    input_reference: Mapping[str, Any]
    output_reference: Mapping[str, Any] | None
    object_type: str = field(init=False, default="EXECUTION")

    def __post_init__(self) -> None:
        super(ExecutionObject, self).__post_init__()
        for field_name in (
            "entity_reference",
            "task_reference",
            "context_reference",
            "input_reference",
            "output_reference",
        ):
            object.__setattr__(self, field_name, freeze_value(getattr(self, field_name)))
