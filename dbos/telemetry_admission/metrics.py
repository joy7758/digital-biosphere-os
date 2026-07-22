"""Bounded in-memory self-observation for telemetry admission.

This helper is not an OpenTelemetry SDK integration or exporter. It retains
only low-cardinality counters and bounded diagnostics. A sink failure cannot
change admission truth.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from threading import Lock
from typing import Any

from .contracts import METRIC_OUTCOMES, SIGNAL_TYPES


MetricSink = Callable[[str, Mapping[str, str], float], None]


class AdmissionMetrics:
    """Thread-safe bounded metrics surface with no caller identifiers."""

    def __init__(self, sink: MetricSink | None = None) -> None:
        self._sink = sink
        self._lock = Lock()
        self._requests: Counter[tuple[str, str, str]] = Counter()
        self._items: Counter[tuple[str, str]] = Counter()
        self._duplicates: Counter[str] = Counter()
        # Retain only a count locally. Duration values are emitted to the
        # optional sink; keeping one tuple per admission would make this
        # reference helper grow without bound during a long-running caller.
        self._duration_observation_count = 0
        self._diagnostics: Counter[str] = Counter()

    def observe(
        self,
        *,
        outcome: str,
        signal_type: str,
        schema_version: str,
        accepted_items: int,
        rejected_items: int,
        duration_seconds: float,
    ) -> None:
        safe_outcome = outcome.lower()
        safe_signal = signal_type if signal_type in SIGNAL_TYPES else "UNKNOWN"
        if safe_outcome not in METRIC_OUTCOMES:
            safe_outcome = "unknown"
        safe_schema = schema_version if schema_version == "0.1.0" else "unsupported"
        safe_duration = max(0.0, float(duration_seconds))
        labels = {
            "outcome": safe_outcome,
            "signal_type": safe_signal,
            "schema_version": safe_schema,
        }
        with self._lock:
            self._requests[(safe_outcome, safe_signal, safe_schema)] += 1
            self._items[(safe_outcome, safe_signal)] += max(
                0, int(accepted_items) + int(rejected_items)
            )
            if safe_outcome.startswith("duplicate_"):
                self._duplicates[safe_outcome] += 1
            self._duration_observation_count += 1
        if self._sink is not None:
            try:
                self._sink("requests", labels, 1.0)
                self._sink("duration", {"outcome": safe_outcome}, safe_duration)
            except Exception:  # sink is explicitly non-authoritative
                with self._lock:
                    self._diagnostics["TA_METRICS_SINK_FAILURE"] += 1

    def snapshot(self) -> dict[str, Any]:
        """Return low-cardinality state; no observation or trace ID is accepted."""

        with self._lock:
            return {
                "requests": {
                    "|".join(key): value
                    for key, value in sorted(self._requests.items())
                },
                "items": {
                    "|".join(key): value for key, value in sorted(self._items.items())
                },
                "duplicates": dict(sorted(self._duplicates.items())),
                "duration_observation_count": self._duration_observation_count,
                "diagnostics": dict(sorted(self._diagnostics.items())),
            }


__all__ = ["AdmissionMetrics", "MetricSink"]
