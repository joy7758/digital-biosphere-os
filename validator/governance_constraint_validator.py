"""Fail-closed DBOS governance constraints for object representations.

The checks inspect declarations only. They never infer, grant, revoke, repair,
or execute anything.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from validator.validation_result_model import ValidationIssue


GLOBAL_PROHIBITED_FIELDS = frozenset(
    {
        "agent_created",
        "authority",
        "authority_effect",
        "authority_grant",
        "authority_granted",
        "authorization",
        "authorization_grant",
        "authorization_granted",
        "authorized",
        "capability_assigned",
        "capability_grant",
        "certification_granted",
        "entity_activated",
        "evolution_decision",
        "execute",
        "execution_effect",
        "execution_trigger",
        "fitness_score",
        "grant_permission",
        "permission",
        "permission_effect",
        "permission_grant",
        "permission_granted",
        "permission_status",
        "permissions",
        "runtime_started",
        "saee_effect",
        "truth",
        "truth_confirmed",
        "truth_effect",
    }
)


def _walk_keys(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, str(key).lower()
            yield from _walk_keys(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def validate_schema_boundaries(schema: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
    """Reject a schema whose declared DBOS effects are not inert."""

    issues: list[ValidationIssue] = []
    boundaries = schema.get("x-dbios-boundaries")
    if not isinstance(boundaries, Mapping):
        return (
            ValidationIssue(
                code="INVALID",
                path="$schema.x-dbios-boundaries",
                message="The selected schema does not declare governance boundaries.",
                rule="schema_boundary_presence",
            ),
        )

    for name, value in boundaries.items():
        if name.endswith("_effect") and value != "NONE":
            issues.append(
                ValidationIssue(
                    code="INVALID",
                    path=f"$schema.x-dbios-boundaries.{name}",
                    message="A DBOS object schema must declare every governance effect as NONE.",
                    rule="schema_has_no_governance_effect",
                )
            )
        if name == "schema_creates_instance" and value is not False:
            issues.append(
                ValidationIssue(
                    code="INVALID",
                    path=f"$schema.x-dbios-boundaries.{name}",
                    message="A schema cannot create an object instance.",
                    rule="schema_ne_instance",
                )
            )
    return tuple(issues)


def validate_governance_constraints(
    target: Mapping[str, Any], schema: Mapping[str, Any]
) -> tuple[ValidationIssue, ...]:
    """Reject target fields that claim prohibited governance side effects."""

    schema_fields = schema.get("x-dbios-prohibited-fields", ())
    prohibited = GLOBAL_PROHIBITED_FIELDS | {
        str(field).lower() for field in schema_fields if isinstance(field, str)
    }
    issues = list(validate_schema_boundaries(schema))

    for path, normalized_key in _walk_keys(target):
        if normalized_key in prohibited:
            issues.append(
                ValidationIssue(
                    code="INVALID",
                    path=path,
                    message="The field declares a governance effect prohibited by DBOS v0.1.",
                    rule="object_has_no_governance_effect",
                )
            )

    return tuple(issues)
