"""Fail-closed error language for the synthetic MCP Tool Call adapter.

These diagnostics explain mapping failures only. They cannot repair input,
retry a tool, create authority, or grant permission.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

class AdapterErrorCode(str, Enum):
    """The five error codes frozen by the MCP Adapter v0.1 specification."""

    INVALID_TOOL_REFERENCE = "INVALID_TOOL_REFERENCE"
    UNKNOWN_RESOURCE = "UNKNOWN_RESOURCE"
    VERSION_MISMATCH = "VERSION_MISMATCH"
    UNRESOLVED_CONTEXT = "UNRESOLVED_CONTEXT"
    CONFLICTING_REFERENCE = "CONFLICTING_REFERENCE"


class MappingStatus(str, Enum):
    """Candidate mapping outcomes with no registration or execution effect."""

    MAPPED = "MAPPED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    VERSION_MISMATCH = "VERSION_MISMATCH"


@dataclass(frozen=True, slots=True)
class AdapterError:
    """One immutable adapter diagnostic without automatic recovery behavior."""

    code: AdapterErrorCode
    message: str
    field_reference: str
    resolution_hint: str

    def __post_init__(self) -> None:
        for name in ("message", "field_reference", "resolution_hint"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")

    def to_dict(self) -> dict[str, str]:
        """Return a detached serializable diagnostic."""

        return {
            "error_code": self.code.value,
            "message": self.message,
            "field_reference": self.field_reference,
            "resolution_hint": self.resolution_hint,
        }
