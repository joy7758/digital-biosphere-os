"""Read-only validation bridge for DBOS SDK objects."""

from __future__ import annotations

from validator import ValidationResult
from validator import validate_object as validate_serialized_object

from sdk.objects.base import BaseObject
from sdk.serialization import object_to_dict


def validate_object(
    target: BaseObject, *, schema_id: str | None = None
) -> ValidationResult:
    """Serialize one SDK object and invoke the canonical local validator.

    This function cannot skip structural or governance checks. A returned PASS
    remains a local validation result and creates no authority or permission.
    """

    if not isinstance(target, BaseObject):
        raise TypeError("target must be a DBOS SDK BaseObject")
    return validate_serialized_object(object_to_dict(target), schema_id=schema_id)
