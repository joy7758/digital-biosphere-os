"""Read-only DBOS Object Schema Validator v0.1 public surface.

This package validates synthetic or caller-supplied object representations. It
does not create, repair, register, authorize, execute, or verify an entity.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from validator.validation_result_model import (
    SchemaReference,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)

if TYPE_CHECKING:
    from validator.object_schema_validator import ObjectSchemaValidator


def validate_object(
    target: Mapping[str, Any] | Any, *, schema_id: str | None = None
) -> ValidationResult:
    """Lazily load the local validator and preserve a warning-free CLI."""

    from validator.object_schema_validator import validate_object as _validate_object

    return _validate_object(target, schema_id=schema_id)


def __getattr__(name: str) -> Any:
    if name == "ObjectSchemaValidator":
        from validator.object_schema_validator import ObjectSchemaValidator

        return ObjectSchemaValidator
    raise AttributeError(name)


__all__ = [
    "ObjectSchemaValidator",
    "SchemaReference",
    "ValidationIssue",
    "ValidationResult",
    "ValidationStatus",
    "validate_object",
]
