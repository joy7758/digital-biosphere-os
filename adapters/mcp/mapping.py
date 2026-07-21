"""Immutable mapping records for the synthetic MCP Tool Call adapter.

This module derives extension-scoped candidate identifiers and builds inert
ExecutionObject data. It performs no I/O, tool invocation, registration, or
external reference resolution.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from adapters.mcp.errors import AdapterError, MappingStatus
from sdk.objects import ExecutionObject
from sdk.objects.base import freeze_value
from sdk.serialization import object_to_dict
from validator import ValidationResult


ADAPTER_IMPLEMENTATION_VERSION = "v0.1"
SYNTHETIC_PROTOCOL_REVISION = "DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1"
SYNTHETIC_MAPPING_PROFILE_VERSION = "dbos.synthetic.mcp-tool-call/v0.1"
SYNTHETIC_SOURCE_NAMESPACE = "extension:dbos-mcp-synthetic"


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticMCPToolCall:
    """Preflight-approved fixture data, not a real MCP event or execution."""

    tool_call_id: str
    tool_name: str
    arguments_reference: Mapping[str, Any]
    context_reference: Mapping[str, Any]
    source_reference: Mapping[str, Any]
    entity_reference: Mapping[str, Any]
    protocol_revision: str
    mapping_profile_version: str

    def __post_init__(self) -> None:
        for name in (
            "arguments_reference",
            "context_reference",
            "source_reference",
            "entity_reference",
        ):
            object.__setattr__(self, name, freeze_value(getattr(self, name)))


@dataclass(frozen=True, slots=True)
class ToolCallMappingResult:
    """Adapter output envelope with an optional inert candidate."""

    mapping_status: MappingStatus
    candidate: ExecutionObject | None
    validation_result: ValidationResult
    validator_invoked: bool
    adapter_errors: tuple[AdapterError, ...] = ()
    limitations: tuple[str, ...] = (
        "Synthetic Tool Call fixture mapping only.",
        "A candidate is not a canonical DBOS object or execution fact.",
        "Validation creates no authority, permission, capability, or evidence.",
        "No real MCP protocol revision or production compatibility is claimed.",
    )

    def __post_init__(self) -> None:
        if self.mapping_status is MappingStatus.MAPPED:
            if self.candidate is None or not self.validator_invoked:
                raise ValueError("MAPPED requires a candidate and canonical validation")
        elif self.candidate is not None or self.validator_invoked:
            raise ValueError("A non-mapped result cannot contain or validate a candidate")
        if not self.limitations:
            raise ValueError("limitations must not be empty")

    @property
    def execution_candidate_id(self) -> str | None:
        """Expose the inert candidate ID without creating a canonical identity."""

        return self.candidate.execution_id if self.candidate is not None else None

    def to_dict(self) -> dict[str, Any]:
        """Return a detached result without writing a registry or evidence store."""

        return {
            "mapping_status": self.mapping_status.value,
            "execution_candidate_id": self.execution_candidate_id,
            "candidate": (
                object_to_dict(self.candidate) if self.candidate is not None else None
            ),
            "validation_result": self.validation_result.to_dict(),
            "validator_invoked": self.validator_invoked,
            "adapter_errors": [item.to_dict() for item in self.adapter_errors],
            "limitations": list(self.limitations),
        }


def _identifier_segment(value: str) -> str:
    return quote(value, safe="")


def _build_execution_candidate(fixture: SyntheticMCPToolCall) -> ExecutionObject:
    """Build one internal candidate after adapter preflight has completed."""

    source_id = str(fixture.source_reference["source_id"])
    namespace = str(fixture.source_reference["namespace"])
    candidate_id = (
        "extension:dbos-mcp-tool-call-candidate:"
        f"{_identifier_segment(source_id)}:"
        f"{_identifier_segment(fixture.tool_call_id)}:v0.1"
    )
    task_reference = {
        "reference_id": (
            f"{source_id}#synthetic-tool/{_identifier_segment(fixture.tool_name)}"
        ),
        "reference_type": "TOOL",
        "namespace": namespace,
        "version": fixture.mapping_profile_version,
        "source": source_id,
        "status": "DECLARED",
    }
    return ExecutionObject(
        object_id=candidate_id,
        execution_id=candidate_id,
        version="v0.1",
        source=fixture.source_reference,
        status="UNKNOWN",
        created_at=None,
        updated_at=None,
        limitations=(
            "Synthetic MCP Tool Call fixture candidate only.",
            "The Tool Call was not executed and no result was observed.",
            "The source, entity, context, and input references were not resolved.",
            "The synthetic profile is not a real MCP protocol compatibility claim.",
        ),
        entity_reference=fixture.entity_reference,
        task_reference=task_reference,
        context_reference=fixture.context_reference,
        input_reference=fixture.arguments_reference,
        output_reference=None,
    )
