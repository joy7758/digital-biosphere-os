"""Separate-process crash worker used only by TA-F011/TA-F012 tests."""

from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

from dbos.telemetry_admission.service import TelemetryAdmissionService
from dbos.telemetry_admission.store import SQLiteTelemetryAdmissionStore
from fixtures import make_envelope


def main() -> int:
    path = Path(sys.argv[1])
    fault_point = sys.argv[2]
    counters: Counter[str] = Counter()

    def identifier(kind: str) -> str:
        counters[kind] += 1
        return f"ta:{kind}:subprocess-{counters[kind]}"

    def crash(point: str) -> None:
        if point == fault_point:
            os._exit(73)

    store = SQLiteTelemetryAdmissionStore(
        path,
        id_factory=identifier,
        fault_injector=crash,
    )
    service = TelemetryAdmissionService(store)
    service.admit(
        make_envelope(observation_id="ta:observation:subprocess"),
        admission_id="ta:admission:subprocess",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
