"""Immutable common object representation for the local DBOS SDK skeleton.

Construction preserves caller-supplied declarations exactly. It does not
generate identifiers or timestamps, normalize governance states, or establish
that any represented fact is true. Validation remains a separate explicit step.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


def freeze_value(value: Any) -> Any:
    """Return an immutable recursive copy without adding semantic meaning."""

    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze_value(item) for key, item in value.items()})
    if isinstance(value, tuple):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, list):
        return tuple(freeze_value(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted((freeze_value(item) for item in value), key=repr))
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseObject:
    """Eight-field DBOS common contract with no behavioral methods."""

    object_id: str
    source: Mapping[str, Any]
    status: str
    limitations: Sequence[str]
    version: str = "v0.1"
    created_at: str | None = None
    updated_at: str | None = None
    object_type: str = field(init=False, default="UNKNOWN")

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", freeze_value(self.source))
        object.__setattr__(self, "limitations", freeze_value(self.limitations))
