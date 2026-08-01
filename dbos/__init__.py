"""Public DBOS Developer Preview facade.

This module exposes inert object representations, deterministic serialization,
and local validation. Importing or calling it does not create an Agent,
Runtime, Entity registration, Permission, canonical Evidence, or execution.

The v0.1 package contract supports local editable installation and a validated,
locally built wheel candidate. It is not a published distribution or a stable
production compatibility promise until a separate release record says so.
"""

from sdk import (
    BaseObject,
    CapabilityObject,
    EntityObject,
    EvidenceReferenceObject,
    ExecutionObject,
    object_to_dict,
    object_to_json,
    validate_object,
)
from validator import (
    SchemaReference,
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)

__version__ = "0.1.0.dev0"

__all__ = [
    "BaseObject",
    "CapabilityObject",
    "EntityObject",
    "EvidenceReferenceObject",
    "ExecutionObject",
    "SchemaReference",
    "ValidationIssue",
    "ValidationResult",
    "ValidationStatus",
    "object_to_dict",
    "object_to_json",
    "validate_object",
]
