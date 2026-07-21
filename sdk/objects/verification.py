"""Inert Verification Object; verification is not authorization or permission."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from sdk.objects.base import BaseObject, freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationObject(BaseObject):
    """Caller-supplied verification projection with no verification execution."""

    verification_id: str
    target_reference: Mapping[str, Any]
    verification_type: str
    verification_status: str
    object_type: str = field(init=False, default="VERIFICATION")

    def __post_init__(self) -> None:
        super(VerificationObject, self).__post_init__()
        object.__setattr__(self, "target_reference", freeze_value(self.target_reference))
