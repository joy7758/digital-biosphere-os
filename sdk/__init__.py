"""Local DBOS Object SDK Skeleton v0.1.

The package exposes inert object representations, deterministic serialization,
and a bridge to the existing local validator. It does not create Agents,
Runtimes, permissions, authority, or execution side effects.
"""

from sdk.objects import (
    BaseObject,
    CapabilityObject,
    EntityObject,
    EvidenceReferenceObject,
    ExecutionObject,
    VerificationObject,
)
from sdk.serialization import object_to_dict, object_to_json

__all__ = [
    "BaseObject",
    "CapabilityObject",
    "EntityObject",
    "EvidenceReferenceObject",
    "ExecutionObject",
    "VerificationObject",
    "object_to_dict",
    "object_to_json",
]
