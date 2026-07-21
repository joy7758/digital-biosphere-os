"""Inert Entity Object representation; it does not create an active entity."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from sdk.objects.base import BaseObject, freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityObject(BaseObject):
    """Caller-supplied projection of an Entity identity record."""

    entity_id: str
    entity_type: str
    owner_reference: Mapping[str, Any]
    lifecycle_state: str
    source_reference: Mapping[str, Any]
    object_type: str = field(init=False, default="ENTITY")

    def __post_init__(self) -> None:
        super(EntityObject, self).__post_init__()
        object.__setattr__(self, "owner_reference", freeze_value(self.owner_reference))
        object.__setattr__(self, "source_reference", freeze_value(self.source_reference))
