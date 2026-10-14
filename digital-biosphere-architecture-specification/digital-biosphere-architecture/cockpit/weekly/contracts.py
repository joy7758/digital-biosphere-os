"""Shared, read-only contracts for DBA Weekly Cockpit v0.1."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


LIFECYCLE_STATES = {
    "OPEN", "CONTINUING", "CLOSED", "REAPPEARED",
    "NOT_ASSESSED", "STALE", "CONFLICT",
}
SEVERITIES = {
    "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL", "NOT_ASSESSED",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_assignments(text: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^([A-Z][A-Z0-9_]*)=(.+)$", text, re.MULTILINE)
    }


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return parsed


def freshness(observed_at: str, as_of: str, max_age_days: int = 7) -> str:
    age = (parse_time(as_of) - parse_time(observed_at)).total_seconds()
    return "FRESH" if -60 <= age <= max_age_days * 86400 else "STALE"


@dataclass
class CellResult:
    cell_id: str
    status: str
    duration_ms: int = 0
    outputs: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    reason_code: str | None = None
    exception_summary: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discovery_signal(
    signal_id: str,
    project_id: str,
    signal_type: str,
    summary_zh: str,
    source_reference: str | None,
    source_authority: str,
    observed_at: str | None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "signal_id": signal_id,
        "project_id": project_id,
        "signal_type": signal_type,
        "summary_zh": summary_zh,
        "source_reference": source_reference,
        "source_authority": source_authority,
        "observed_at": observed_at,
        "discovery_status": "DISCOVERED",
        "authorization": "NONE",
        "payload": payload or {},
    }


def finding(
    finding_id: str,
    project_id: str,
    finding_type: str,
    summary_zh: str,
    impact_zh: str,
    current_effect_zh: str,
    source_reference: str,
    source_authority: str,
    observed_at: str,
    freshness_state: str,
    confidence: str,
    lifecycle_status: str,
    severity: str,
    owner_conversation: str,
    recommended_next_step_zh: str,
    *,
    blocking: bool = False,
    technical_evidence: list[str] | None = None,
) -> dict[str, Any]:
    if lifecycle_status not in LIFECYCLE_STATES:
        raise ValueError(f"invalid lifecycle status: {lifecycle_status}")
    if severity not in SEVERITIES:
        raise ValueError(f"invalid severity: {severity}")
    return {
        "finding_id": finding_id,
        "project_id": project_id,
        "finding_type": finding_type,
        "summary_zh": summary_zh,
        "impact_zh": impact_zh,
        "current_effect_zh": current_effect_zh,
        "source_reference": source_reference,
        "source_authority": source_authority,
        "observed_at": observed_at,
        "freshness": freshness_state,
        "confidence": confidence,
        "lifecycle_status": lifecycle_status,
        "severity": severity,
        "owner_conversation": owner_conversation,
        "recommended_next_step_zh": recommended_next_step_zh,
        "currently_blocking": blocking,
        "technical_evidence": technical_evidence or [],
        "authorization": "NONE",
    }
