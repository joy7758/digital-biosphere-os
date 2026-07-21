"""Local consistency checks for embedded DBOS Reference Objects.

This module does not resolve a reference, contact a source, create a target,
or treat a reference as truth, verification, authorization, or permission.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from validator.validation_result_model import ValidationIssue


DBIO_REFERENCE_TYPES = frozenset(
    {
        "ENTITY",
        "CANDIDATE",
        "AUTHORIZATION",
        "REGISTRATION",
        "EXECUTION",
        "EVIDENCE",
        "VERIFICATION",
    }
)

REFERENCE_FIELDS_BY_OBJECT_TYPE: dict[str, dict[str, str | None]] = {
    "ENTITY": {"owner_reference": None, "source_reference": "ENTITY"},
    "CAPABILITY": {"entity_reference": "ENTITY"},
    "EXECUTION": {
        "entity_reference": "ENTITY",
        "task_reference": None,
        "context_reference": None,
        "input_reference": None,
        "output_reference": None,
    },
    "EVIDENCE_REFERENCE": {
        "execution_reference": "EXECUTION",
        "source_reference": "EVIDENCE",
    },
    "VERIFICATION": {"target_reference": None},
}

REFERENCE_REQUIRED_FIELDS = frozenset(
    {"reference_id", "reference_type", "namespace", "version", "source", "status"}
)


def _validate_reference(
    reference: Any, path: str, expected_type: str | None
) -> list[ValidationIssue]:
    if not isinstance(reference, Mapping):
        return [
            ValidationIssue(
                code="INVALID",
                path=path,
                message="A reference field must contain a Reference Object or an explicitly allowed null.",
                rule="reference_object_shape",
            )
        ]

    issues: list[ValidationIssue] = []
    missing = sorted(REFERENCE_REQUIRED_FIELDS - set(reference))
    if missing:
        issues.append(
            ValidationIssue(
                code="INVALID",
                path=path,
                message="The Reference Object is missing required fields.",
                rule="reference_required_fields",
            )
        )
        return issues

    reference_type = reference.get("reference_type")
    namespace = reference.get("namespace")
    if expected_type is not None and reference_type != expected_type:
        issues.append(
            ValidationIssue(
                code="INVALID",
                path=f"{path}.reference_type",
                message="The reference type is inconsistent with the containing object field.",
                rule="reference_role_consistency",
            )
        )
    if namespace == "dbio" and reference_type not in DBIO_REFERENCE_TYPES:
        issues.append(
            ValidationIssue(
                code="INVALID",
                path=f"{path}.reference_type",
                message="The dbio namespace does not define this canonical reference type in v0.1.",
                rule="dbio_reference_type_allowlist",
            )
        )
    return issues


def validate_reference_consistency(target: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
    """Check embedded reference shape, role, and source-owner consistency."""

    object_type = target.get("object_type")
    reference_fields = REFERENCE_FIELDS_BY_OBJECT_TYPE.get(str(object_type), {})
    issues: list[ValidationIssue] = []

    for field, expected_type in reference_fields.items():
        if field not in target:
            continue
        reference = target[field]
        if field == "output_reference" and reference is None:
            continue
        issues.extend(_validate_reference(reference, f"$.{field}", expected_type))

    source = target.get("source")
    source_reference = target.get("source_reference")
    if isinstance(source, Mapping) and isinstance(source_reference, Mapping):
        if source.get("namespace") != source_reference.get("namespace"):
            issues.append(
                ValidationIssue(
                    code="CONFLICT",
                    path="$.source_reference.namespace",
                    message="The source reference namespace conflicts with the object source namespace.",
                    rule="source_reference_owner_consistency",
                )
            )
        if source.get("source_id") != source_reference.get("source"):
            issues.append(
                ValidationIssue(
                    code="CONFLICT",
                    path="$.source_reference.source",
                    message="The source reference owner conflicts with the object source identifier.",
                    rule="source_reference_owner_consistency",
                )
            )

    return tuple(issues)
