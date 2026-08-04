"""Offline minimal MCP Tool Call to DBOS Execution candidate adapter.

Only a synthetic, DBOS-owned fixture revision is accepted. The adapter never
connects to MCP, invokes a tool, repairs input, resolves references, writes
evidence, or creates governance authority.
"""

from collections.abc import Iterator, Mapping
from typing import Any

from adapters.mcp.errors import AdapterError, AdapterErrorCode, MappingStatus
from adapters.mcp.mapping import (
    SYNTHETIC_MAPPING_PROFILE_VERSION,
    SYNTHETIC_PROTOCOL_REVISION,
    SYNTHETIC_SOURCE_NAMESPACE,
    SyntheticMCPToolCall,
    ToolCallMappingResult,
    _build_execution_candidate,
)
from sdk.validation import validate_object
from validator import ValidationIssue, ValidationResult, ValidationStatus

PREFLIGHT_VALIDATOR_VERSION = "mcp-tool-call-adapter-preflight/v0.1"

REQUIRED_INPUT_FIELDS = frozenset(
    {
        "tool_call_id",
        "tool_name",
        "arguments_reference",
        "context_reference",
        "source_reference",
        "entity_reference",
        "protocol_revision",
        "mapping_profile_version",
    }
)

PROHIBITED_INPUT_FIELDS = frozenset(
    {
        "agent",
        "authority",
        "capabilities",
        "capability",
        "capability_grant",
        "evidence",
        "evidence_truth",
        "execute",
        "permission",
        "permissions",
        "permission_grant",
        "tool_permission",
        "tool_result",
        "result",
        "runtime",
    }
)

SOURCE_DESCRIPTOR_FIELDS = frozenset({"namespace", "source_id", "version", "status"})
REFERENCE_OBJECT_FIELDS = frozenset(
    {"reference_id", "reference_type", "namespace", "version", "source", "status"}
)


def _walk_keys(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key).lower()
            yield from _walk_keys(child, child_path)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _preflight_validation_result(
    *, status: ValidationStatus, issues: tuple[ValidationIssue, ...]
) -> ValidationResult:
    return ValidationResult(
        validator_version=PREFLIGHT_VALIDATOR_VERSION,
        target_reference=None,
        result=status,
        errors=issues,
        limitations=(
            "Adapter preflight only; the canonical object Validator was not invoked.",
            "No candidate, authority, permission, capability, execution, or evidence was created.",
            "No real MCP protocol revision or production compatibility is claimed.",
        ),
    )


def _result_without_candidate(
    *,
    mapping_status: MappingStatus,
    validation_status: ValidationStatus,
    issue: ValidationIssue,
    adapter_error: AdapterError | None = None,
) -> ToolCallMappingResult:
    errors = (adapter_error,) if adapter_error is not None else ()
    return ToolCallMappingResult(
        mapping_status=mapping_status,
        candidate=None,
        validation_result=_preflight_validation_result(
            status=validation_status,
            issues=(issue,),
        ),
        validator_invoked=False,
        adapter_errors=errors,
    )


def _unknown(field: str, message: str) -> ToolCallMappingResult:
    issue = ValidationIssue(
        code="UNKNOWN",
        path=f"$.{field}",
        message=message,
        rule=f"mcp_tool_call_required_{field}",
        resolution_hint=f"Provide an explicit synthetic {field} value.",
    )
    adapter_error = None
    if field in {"context_reference", "entity_reference"}:
        adapter_error = AdapterError(
            code=AdapterErrorCode.UNRESOLVED_CONTEXT,
            message=message,
            field_reference=f"$.{field}",
            resolution_hint=f"Provide a complete {field} Reference Object.",
        )
    return _result_without_candidate(
        mapping_status=MappingStatus.UNKNOWN,
        validation_status=ValidationStatus.UNKNOWN,
        issue=issue,
        adapter_error=adapter_error,
    )


def _invalid(
    *, field_path: str, message: str, rule: str
) -> ToolCallMappingResult:
    adapter_error = AdapterError(
        code=AdapterErrorCode.INVALID_TOOL_REFERENCE,
        message=message,
        field_reference=field_path,
        resolution_hint="Remove the prohibited field or provide the required typed reference.",
    )
    return _result_without_candidate(
        mapping_status=MappingStatus.REJECTED,
        validation_status=ValidationStatus.FAIL,
        issue=ValidationIssue(
            code="INVALID",
            path=field_path,
            message=message,
            rule=rule,
            resolution_hint=adapter_error.resolution_hint,
        ),
        adapter_error=adapter_error,
    )


def _version_mismatch(field: str, observed: Any) -> ToolCallMappingResult:
    message = f"The declared {field} is not supported by this synthetic-only adapter."
    adapter_error = AdapterError(
        code=AdapterErrorCode.VERSION_MISMATCH,
        message=message,
        field_reference=f"$.{field}",
        resolution_hint="Use the exact DBOS synthetic fixture revision and mapping profile.",
    )
    return _result_without_candidate(
        mapping_status=MappingStatus.VERSION_MISMATCH,
        validation_status=ValidationStatus.VERSION_MISMATCH,
        issue=ValidationIssue(
            code="VERSION_MISMATCH",
            path=f"$.{field}",
            message=f"{message} Observed: {observed!r}.",
            rule="synthetic_profile_exact_version_match",
            resolution_hint=adapter_error.resolution_hint,
        ),
        adapter_error=adapter_error,
    )


class MCPToolCallAdapter:
    """Deterministic synthetic Tool Call mapper with no external I/O."""

    def adapt(self, value: Mapping[str, Any] | Any) -> ToolCallMappingResult:
        """Map one strict synthetic fixture and invoke the existing Validator."""

        if not isinstance(value, Mapping):
            return _invalid(
                field_path="$",
                message="The synthetic Tool Call fixture must be a mapping.",
                rule="synthetic_tool_call_is_mapping",
            )

        prohibited = sorted(
            (path, key)
            for path, key in _walk_keys(value)
            if key in PROHIBITED_INPUT_FIELDS
        )
        if prohibited:
            path, key = prohibited[0]
            return _invalid(
                field_path=path,
                message=f"The field {key!r} would cross a prohibited DBOS boundary.",
                rule="mcp_tool_call_has_no_governance_or_evidence_effect",
            )

        unknown_fields = sorted(set(value) - REQUIRED_INPUT_FIELDS)
        if unknown_fields:
            field = str(unknown_fields[0])
            return _invalid(
                field_path=f"$.{field}",
                message="Unknown Tool Call fixture fields are rejected fail-closed.",
                rule="synthetic_tool_call_field_allowlist",
            )

        for field in ("source_reference", "context_reference", "protocol_revision"):
            if (
                field not in value
                or value.get(field) is None
                or value.get(field) == ""
            ):
                return _unknown(field, f"The required {field} is unknown.")
        if "entity_reference" not in value or value.get("entity_reference") is None:
            return _unknown(
                "entity_reference",
                "An existing entity_reference is required and cannot be inferred.",
            )

        for field in ("tool_call_id", "tool_name"):
            if not isinstance(value.get(field), str) or not value.get(field):
                return _invalid(
                    field_path=f"$.{field}",
                    message=f"{field} must be a non-empty string.",
                    rule="synthetic_tool_call_required_string",
                )

        for field in (
            "arguments_reference",
            "context_reference",
            "source_reference",
            "entity_reference",
        ):
            if not isinstance(value.get(field), Mapping):
                return _invalid(
                    field_path=f"$.{field}",
                    message=f"{field} must be a typed reference mapping.",
                    rule="synthetic_tool_call_reference_shape",
                )

        if value.get("protocol_revision") != SYNTHETIC_PROTOCOL_REVISION:
            return _version_mismatch("protocol_revision", value.get("protocol_revision"))
        if value.get("mapping_profile_version") != SYNTHETIC_MAPPING_PROFILE_VERSION:
            return _version_mismatch(
                "mapping_profile_version", value.get("mapping_profile_version")
            )

        source_reference = value["source_reference"]
        missing_source_fields = sorted(SOURCE_DESCRIPTOR_FIELDS - set(source_reference))
        if missing_source_fields:
            return _invalid(
                field_path=f"$.source_reference.{missing_source_fields[0]}",
                message="The synthetic source descriptor is incomplete.",
                rule="synthetic_source_descriptor_shape",
            )
        extra_source_fields = sorted(set(source_reference) - SOURCE_DESCRIPTOR_FIELDS)
        if extra_source_fields:
            return _invalid(
                field_path=f"$.source_reference.{extra_source_fields[0]}",
                message="Unknown synthetic source descriptor fields are rejected.",
                rule="synthetic_source_descriptor_field_allowlist",
            )
        if any(
            not isinstance(source_reference.get(field), str)
            or not source_reference.get(field)
            for field in SOURCE_DESCRIPTOR_FIELDS
        ):
            return _invalid(
                field_path="$.source_reference",
                message="Every synthetic source descriptor field must be non-empty text.",
                rule="synthetic_source_descriptor_value_shape",
            )
        if source_reference.get("namespace") != SYNTHETIC_SOURCE_NAMESPACE:
            return _invalid(
                field_path="$.source_reference.namespace",
                message="Only the isolated DBOS synthetic source namespace is accepted.",
                rule="synthetic_source_namespace_isolation",
            )
        if (
            not isinstance(source_reference.get("source_id"), str)
            or not source_reference.get("source_id")
        ):
            return _invalid(
                field_path="$.source_reference.source_id",
                message="The synthetic source descriptor requires a non-empty source_id.",
                rule="synthetic_source_descriptor_shape",
            )

        expected_reference_types = {
            "arguments_reference": "INPUT",
            "context_reference": "CONTEXT",
            "entity_reference": "ENTITY",
        }
        for field, expected_type in expected_reference_types.items():
            reference = value[field]
            missing_reference_fields = sorted(REFERENCE_OBJECT_FIELDS - set(reference))
            if missing_reference_fields:
                return _invalid(
                    field_path=f"$.{field}.{missing_reference_fields[0]}",
                    message=f"{field} is not a complete Reference Object.",
                    rule="synthetic_reference_object_shape",
                )
            extra_reference_fields = sorted(set(reference) - REFERENCE_OBJECT_FIELDS)
            if extra_reference_fields:
                return _invalid(
                    field_path=f"$.{field}.{extra_reference_fields[0]}",
                    message=f"Unknown {field} fields are rejected.",
                    rule="synthetic_reference_object_field_allowlist",
                )
            if any(
                not isinstance(reference.get(name), str) or not reference.get(name)
                for name in REFERENCE_OBJECT_FIELDS
            ):
                return _invalid(
                    field_path=f"$.{field}",
                    message=f"Every {field} field must be non-empty text.",
                    rule="synthetic_reference_object_value_shape",
                )
            if reference.get("namespace") != SYNTHETIC_SOURCE_NAMESPACE:
                return _invalid(
                    field_path=f"$.{field}.namespace",
                    message=f"{field} must remain in the isolated synthetic namespace.",
                    rule="synthetic_reference_namespace_isolation",
                )
            if reference.get("reference_type") != expected_type:
                return _invalid(
                    field_path=f"$.{field}.reference_type",
                    message=f"{field} must use reference_type={expected_type}.",
                    rule="synthetic_reference_role_consistency",
                )

        fixture = SyntheticMCPToolCall(
            tool_call_id=value["tool_call_id"],
            tool_name=value["tool_name"],
            arguments_reference=value["arguments_reference"],
            context_reference=value["context_reference"],
            source_reference=value["source_reference"],
            entity_reference=value["entity_reference"],
            protocol_revision=value["protocol_revision"],
            mapping_profile_version=value["mapping_profile_version"],
        )
        candidate = _build_execution_candidate(fixture)
        validation_result = validate_object(candidate)
        return ToolCallMappingResult(
            mapping_status=MappingStatus.MAPPED,
            candidate=candidate,
            validation_result=validation_result,
            validator_invoked=True,
        )


def adapt_tool_call(value: Mapping[str, Any] | Any) -> ToolCallMappingResult:
    """Public one-shot adapter entry point with no retained mutable state."""

    return MCPToolCallAdapter().adapt(value)
