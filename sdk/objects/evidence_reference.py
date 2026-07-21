"""Inert Evidence Reference Object; a reference does not establish truth."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from sdk.objects.base import BaseObject, freeze_value


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceReferenceObject(BaseObject):
    """Caller-supplied evidence pointer with no evidence mutation effect."""

    evidence_id: str
    execution_reference: Mapping[str, Any]
    source_reference: Mapping[str, Any]
    integrity_status: str
    object_type: str = field(init=False, default="EVIDENCE_REFERENCE")

    def __post_init__(self) -> None:
        super(EvidenceReferenceObject, self).__post_init__()
        object.__setattr__(
            self, "execution_reference", freeze_value(self.execution_reference)
        )
        object.__setattr__(self, "source_reference", freeze_value(self.source_reference))
