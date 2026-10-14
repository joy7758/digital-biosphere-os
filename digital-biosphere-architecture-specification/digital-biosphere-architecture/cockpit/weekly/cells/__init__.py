"""Small, replaceable Cells for the DBA weekly cockpit."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone
from typing import Any

try:
    from cockpit.weekly.contracts import CellResult
except ModuleNotFoundError:  # Direct execution from cockpit/weekly/run_weekly.py.
    from contracts import CellResult


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def source_value(context: dict[str, Any], key: str, default: Any = None) -> Any:
    """Return a named source without treating absence as a positive fact."""
    sources = context.get("sources", {})
    if isinstance(sources, dict) and key in sources:
        return sources[key]
    return context.get(key, default)


def make_result(
    cell_id: str,
    status: str,
    summary: str,
    *,
    discoveries: list[dict[str, Any]] | None = None,
    observations: list[dict[str, Any]] | None = None,
    findings: list[dict[str, Any]] | None = None,
    handoffs: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
) -> CellResult:
    """Build CellResult while keeping Cells decoupled from minor contract revisions."""
    payload = {
        "cell_id": cell_id,
        "status": status,
        "summary": summary,
        "discoveries": discoveries or [],
        "observations": observations or [],
        "findings": findings or [],
        "handoffs": handoffs or [],
        "handoff_packets": handoffs or [],
        "metadata": metadata or {},
        "outputs": outputs if outputs is not None else {
            "discoveries": discoveries or [],
            "observations": observations or [],
            "handoff_packets": handoffs or [],
            "metadata": metadata or {},
        },
        "completed_at": utc_now(),
    }
    signature = inspect.signature(CellResult)
    kwargs: dict[str, Any] = {}
    for name, parameter in signature.parameters.items():
        if name in payload:
            kwargs[name] = payload[name]
        elif parameter.default is inspect.Parameter.empty:
            kwargs[name] = None
    result = CellResult(**kwargs)
    for name, value in payload.items():
        if not hasattr(result, name):
            try:
                setattr(result, name, value)
            except (AttributeError, TypeError):
                pass
    return result


class WeeklyCell:
    """Shared interface; every Cell remains independently replaceable."""

    cell_id = "weekly-cell"

    def run(self, context: dict[str, Any]) -> CellResult:
        return self._run(context)

    def execute(self, context: dict[str, Any]) -> CellResult:
        return self._run(context)

    def evaluate(self, context: dict[str, Any]) -> CellResult:
        return self._run(context)

    def _run(self, context: dict[str, Any]) -> CellResult:
        raise NotImplementedError
