"""Common observation result without decision or execution authority."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


AVAILABLE = "AVAILABLE"
NOT_ASSESSED_CREDENTIAL_UNAVAILABLE = "NOT_ASSESSED_CREDENTIAL_UNAVAILABLE"
NOT_ASSESSED_SOURCE_UNAVAILABLE = "NOT_ASSESSED_SOURCE_UNAVAILABLE"
SOURCE_DRIFT = "SOURCE_DRIFT"
SOURCE_MUTATION_DETECTED = "SOURCE_MUTATION_DETECTED"


@dataclass
class SourceResult:
    """A sourced point-in-time observation; never a project decision."""

    source_id: str
    project_id: str
    status: str
    source_reference: str
    observed_at: str
    retrieved_at: str
    payload: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    source_mode: str = "LIVE_READ_ONLY"
    authority: str = "OBSERVATION_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def unavailable(
        cls,
        *,
        source_id: str,
        project_id: str,
        source_reference: str,
        observed_at: str,
        status: str = NOT_ASSESSED_SOURCE_UNAVAILABLE,
        reason: str,
        limitations: list[str] | None = None,
    ) -> "SourceResult":
        return cls(
            source_id=source_id,
            project_id=project_id,
            status=status,
            source_reference=source_reference,
            observed_at=observed_at,
            retrieved_at=observed_at,
            payload={"reason": reason},
            limitations=limitations or ["Unavailable evidence is not interpreted as a healthy state."],
        )
