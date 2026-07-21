"""Inert Capability Object representation; capability is not permission."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from sdk.objects.base import BaseObject, freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityObject(BaseObject):
    """Caller-supplied capability boundary declaration with no grant effect."""

    capability_id: str
    entity_reference: Mapping[str, Any]
    capability_name: str
    scope: Mapping[str, Any] | Sequence[Any]
    constraints: Mapping[str, Any] | Sequence[Any]
    verification_status: str
    object_type: str = field(init=False, default="CAPABILITY")

    def __post_init__(self) -> None:
        super(CapabilityObject, self).__post_init__()
        object.__setattr__(self, "entity_reference", freeze_value(self.entity_reference))
        object.__setattr__(self, "scope", freeze_value(self.scope))
        object.__setattr__(self, "constraints", freeze_value(self.constraints))
