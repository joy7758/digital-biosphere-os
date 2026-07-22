"""Offline orchestration boundary for telemetry admission.

The service accepts one already-normalized metadata mapping, validates it, and
asks the SQLite reference store to append the result. It has no listener,
decoder, exporter, Collector, Agent, Runtime, Evidence promotion, Permission,
or SAEE call.
"""

from __future__ import annotations

from collections.abc import Mapping
from time import perf_counter

from .contracts import ENVELOPE_SCHEMA_VERSION, SIGNAL_TYPES
from .metrics import AdmissionMetrics
from .models import AdmissionResult, TelemetryAdmissionError
from .store import SQLiteTelemetryAdmissionStore
from .validator import TelemetryEnvelopeValidator


class TelemetryAdmissionService:
    """Validate and transactionally record one metadata-only admission."""

    def __init__(
        self,
        store: SQLiteTelemetryAdmissionStore,
        *,
        validator: TelemetryEnvelopeValidator | None = None,
        metrics: AdmissionMetrics | None = None,
    ) -> None:
        self.store = store
        self.validator = validator or TelemetryEnvelopeValidator()
        self.metrics = metrics or AdmissionMetrics()

    def admit(
        self,
        envelope: object,
        *,
        admission_id: str | None = None,
        claimed_intake_receipt_reference: str | None = None,
        accepted_item_count: int | None = None,
        rejected_item_count: int | None = None,
    ) -> AdmissionResult:
        """Return a result only after commit; stable errors contain no payload."""

        started = perf_counter()
        decision = self.validator.validate(envelope)
        signal_type, schema_version = self._safe_metric_dimensions(envelope)
        try:
            result = self.store.record_decision(
                decision,
                admission_id=admission_id,
                claimed_intake_receipt_reference=claimed_intake_receipt_reference,
                accepted_item_count=accepted_item_count,
                rejected_item_count=rejected_item_count,
            )
        except TelemetryAdmissionError:
            self.metrics.observe(
                outcome="storage_failure",
                signal_type=signal_type,
                schema_version=schema_version,
                accepted_items=0,
                rejected_items=0,
                duration_seconds=perf_counter() - started,
            )
            raise
        self.metrics.observe(
            outcome=result.state.lower(),
            signal_type=signal_type,
            schema_version=schema_version,
            accepted_items=result.accepted_item_count,
            rejected_items=result.rejected_item_count,
            duration_seconds=perf_counter() - started,
        )
        return result

    @staticmethod
    def _safe_metric_dimensions(envelope: object) -> tuple[str, str]:
        if not isinstance(envelope, Mapping):
            return "UNKNOWN", "unsupported"
        signal = envelope.get("signal_type")
        schema = envelope.get("schema_version")
        return (
            str(signal) if signal in SIGNAL_TYPES else "UNKNOWN",
            ENVELOPE_SCHEMA_VERSION
            if schema == ENVELOPE_SCHEMA_VERSION
            else "unsupported",
        )


__all__ = ["TelemetryAdmissionService"]
