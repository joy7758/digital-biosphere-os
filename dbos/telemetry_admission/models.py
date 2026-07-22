"""Immutable, bounded result models for telemetry admission.

These models carry classifications and references only. They deliberately do
not expose Evidence, Verification, Permission, Entity, Agent, Runtime, SAEE,
or raw telemetry fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ValidationDecision:
    """Deterministic validation decision before persistence."""

    state: str
    reason_codes: tuple[str, ...]
    limitations: tuple[str, ...]
    normalized_envelope: Mapping[str, Any] | None
    safe_observation_reference: str | None
    safe_source_digest: str | None

    def __post_init__(self) -> None:
        if self.normalized_envelope is not None and not isinstance(
            self.normalized_envelope, MappingProxyType
        ):
            object.__setattr__(
                self,
                "normalized_envelope",
                MappingProxyType(dict(self.normalized_envelope)),
            )


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    """Committed result returned only after the SQLite transaction commits."""

    admission_id: str
    observation_reference: str
    admission_record_id: str
    intake_receipt_reference: str
    state: str
    sequence: int
    reason_codes: tuple[str, ...]
    limitations: tuple[str, ...]
    accepted_item_count: int
    rejected_item_count: int
    committed: bool = True

    def as_dict(self) -> dict[str, Any]:
        """Return an allowlisted mapping without governance-effect fields."""

        return {
            "admission_id": self.admission_id,
            "observation_reference": self.observation_reference,
            "admission_record_id": self.admission_record_id,
            "intake_receipt_reference": self.intake_receipt_reference,
            "state": self.state,
            "sequence": self.sequence,
            "reason_codes": list(self.reason_codes),
            "limitations": list(self.limitations),
            "accepted_item_count": self.accepted_item_count,
            "rejected_item_count": self.rejected_item_count,
            "committed": self.committed,
        }


class TelemetryAdmissionError(RuntimeError):
    """Fail-closed error whose text never reflects untrusted input."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


__all__ = ["AdmissionResult", "TelemetryAdmissionError", "ValidationDecision"]
