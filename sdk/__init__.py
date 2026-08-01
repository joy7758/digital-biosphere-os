"""Local DBOS Object SDK Skeleton v0.1.

The package exposes inert object representations, deterministic serialization,
and a bridge to the existing local validator. It does not create Agents,
Runtimes, permissions, authority, or execution side effects.
"""

from sdk.objects import (
    BaseObject,
    CapabilityObject,
    EvidenceReferenceObject,
    ExecutionObject,
    VerificationObject,
)
from sdk.serialization import object_to_dict, object_to_json
from sdk.validation import validate_object

__all__ = [
    "BaseObject",
    "CapabilityObject",
    "EvidenceReferenceObject",
    "ExecutionObject",
    "VerificationObject",
    "object_to_dict",
    "object_to_json",
    "validate_object",
]
