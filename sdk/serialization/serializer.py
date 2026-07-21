"""Serialize DBOS SDK data objects without changing their declarations."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import fields
from enum import Enum
from typing import Any

from sdk.objects.base import BaseObject


def _json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if isinstance(value, (frozenset, set)):
        converted = [_json_value(item) for item in value]
        return sorted(
            converted,
            key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, default=repr),
        )
    if isinstance(value, Enum):
        return value.value
    return value


def object_to_dict(target: BaseObject) -> dict[str, Any]:
    """Return a detached JSON-compatible representation of one SDK object."""

    if not isinstance(target, BaseObject):
        raise TypeError("target must be a DBOS SDK BaseObject")
    return {item.name: _json_value(getattr(target, item.name)) for item in fields(target)}


def object_to_json(target: BaseObject, *, indent: int | None = 2) -> str:
    """Return deterministic JSON; serialization performs no validation or I/O."""

    return json.dumps(
        object_to_dict(target),
        ensure_ascii=False,
        indent=indent,
        sort_keys=True,
    )
