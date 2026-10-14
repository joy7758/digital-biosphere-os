"""Thin orchestration for the DBA weekly cockpit."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .contracts import CellResult
    from .cells.drift import DriftCell
    from .cells.environment_discovery import EnvironmentDiscoveryCell
    from .cells.evidence_admission import EvidenceAdmissionCell
    from .cells.handoff import HandoffCell
    from .cells.human_view import HumanViewCell
    from .cells.memory import MemoryCell
    from .cells.project_discovery import ProjectDiscoveryCell
    from .cells.quality import QualityCell
    from .cells.relationship_discovery import RelationshipDiscoveryCell
    from .cells.security import SecurityCell
    from .cells.upgrade import UpgradeCell
except ImportError:  # Direct execution from cockpit/weekly/run_weekly.py.
    from contracts import CellResult
    from cells.drift import DriftCell
    from cells.environment_discovery import EnvironmentDiscoveryCell
    from cells.evidence_admission import EvidenceAdmissionCell
    from cells.handoff import HandoffCell
    from cells.human_view import HumanViewCell
    from cells.memory import MemoryCell
    from cells.project_discovery import ProjectDiscoveryCell
    from cells.quality import QualityCell
    from cells.relationship_discovery import RelationshipDiscoveryCell
    from cells.security import SecurityCell
    from cells.upgrade import UpgradeCell


class WeeklyCoordinator:
    """Call Cells in order, isolate failures, merge standard outputs, and write artifacts."""

    def __init__(self, cell_types: list[type] | None = None):
        self.cell_types = cell_types or [
            ProjectDiscoveryCell,
            EnvironmentDiscoveryCell,
            RelationshipDiscoveryCell,
            EvidenceAdmissionCell,
            SecurityCell,
            UpgradeCell,
            QualityCell,
            DriftCell,
            MemoryCell,
            HandoffCell,
        ]

    def run(
        self,
        context: dict[str, Any],
        output_dir: Path,
        snapshot_name: str = "latest.json",
    ) -> dict[str, Any]:
        working = dict(context)
        results: list[CellResult] = []
        discovery_failure_count = 0
        deterministic = bool(context.get("deterministic"))

        for cell_type in self.cell_types:
            cell = cell_type()
            started = time.monotonic()
            try:
                result = cell.run(working)
            except Exception as exc:  # Cell failure isolation is mandatory.
                reason = "DISCOVERY_UNAVAILABLE" if "DISCOVERY" in cell.cell_id else "CELL_FAILURE"
                result = CellResult(
                    cell_id=cell.cell_id,
                    status="NOT_ASSESSED",
                    outputs={},
                    findings=[],
                    reason_code=reason,
                    exception_summary=f"{type(exc).__name__}: {exc}",
                )
                if reason == "DISCOVERY_UNAVAILABLE":
                    discovery_failure_count += 1
            result.duration_ms = (
                0 if deterministic else max(0, round((time.monotonic() - started) * 1000))
            )
            results.append(result)
            self._merge_result(working, result)

        provisional_runs = [self._result_record(item) for item in results]
        provisional_runs.extend(
            [
                {"cell_id": "HUMAN_VIEW_CELL", "status": "PASS", "duration_ms": 0},
                {"cell_id": "WEEKLY_COORDINATOR_CELL", "status": "PASS", "duration_ms": 0},
            ]
        )
        snapshot = self._snapshot(working, provisional_runs, discovery_failure_count)
        output_dir.mkdir(parents=True, exist_ok=True)

        human_started = time.monotonic()
        try:
            human_result = HumanViewCell().run(
                {
                    **working,
                    "snapshot": snapshot,
                    "output_dir": output_dir,
                }
            )
        except Exception as exc:  # Human view failure remains isolated.
            human_result = CellResult(
                cell_id="HUMAN_VIEW_CELL",
                status="NOT_ASSESSED",
                outputs={},
                findings=[],
                reason_code="CELL_FAILURE",
                exception_summary=f"{type(exc).__name__}: {exc}",
            )
        human_result.duration_ms = (
            0 if deterministic else max(0, round((time.monotonic() - human_started) * 1000))
        )
        results.append(human_result)

        coordinator_result = CellResult(
            cell_id="WEEKLY_COORDINATOR_CELL",
            status="PASS",
            outputs={"snapshot_name": snapshot_name},
            findings=[],
        )
        results.append(coordinator_result)
        snapshot["cell_runs"] = [self._result_record(item) for item in results]
        snapshot["logical_cells"] = list(snapshot["cell_runs"])

        if human_result.status == "PASS":
            HumanViewCell().render(snapshot, output_dir)

        (output_dir / snapshot_name).write_text(
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "cell-run-summary.json").write_text(
            json.dumps(
                {
                    "snapshot_id": snapshot["snapshot_id"],
                    "observed_at": snapshot["observed_at"],
                    "cell_runs": snapshot["cell_runs"],
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return snapshot

    @staticmethod
    def _record_key(record: dict[str, Any]) -> str | None:
        for key in (
            "signal_id",
            "project_id",
            "blind_spot_id",
            "decision_id",
            "finding_id",
            "handoff_id",
        ):
            value = record.get(key)
            if isinstance(value, str):
                return value
        return None

    @classmethod
    def _merge_records(cls, existing: list[dict[str, Any]], incoming: list[dict[str, Any]]):
        positions = {
            key: index
            for index, item in enumerate(existing)
            if (key := cls._record_key(item)) is not None
        }
        for item in incoming:
            key = cls._record_key(item)
            if key is not None and key in positions:
                existing[positions[key]].update(item)
            else:
                existing.append(dict(item))
                if key is not None:
                    positions[key] = len(existing) - 1

    @classmethod
    def _merge_result(cls, context: dict[str, Any], result: CellResult) -> None:
        outputs = result.outputs if isinstance(result.outputs, dict) else {}
        for key, value in outputs.items():
            if key.endswith("_records") and isinstance(value, list):
                target = context.setdefault(key, [])
                cls._merge_records(target, value)
            elif key.endswith("_updates") and isinstance(value, list):
                target_key = f"{key[:-8]}_records"
                target = context.setdefault(target_key, [])
                cls._merge_records(target, value)
            elif key == "blind_spots" and isinstance(value, list):
                target = context.setdefault(key, [])
                cls._merge_records(target, value)
            else:
                context[key] = value
        if result.findings:
            target = context.setdefault("findings", [])
            cls._merge_records(target, result.findings)

    @staticmethod
    def _result_record(result: CellResult) -> dict[str, Any]:
        record = {
            "cell_id": result.cell_id,
            "status": result.status,
            "duration_ms": result.duration_ms,
        }
        if result.reason_code:
            record["reason_code"] = result.reason_code
        if result.exception_summary:
            record["exception_summary"] = result.exception_summary
        summary = getattr(result, "summary", None)
        if summary:
            record["summary"] = summary
        return record

    def _snapshot(
        self,
        context: dict[str, Any],
        cell_runs: list[dict[str, Any]],
        discovery_failure_count: int,
    ) -> dict[str, Any]:
        projects = self._projects(context)
        discoveries = list(context.get("discovery_records", []))
        decisions = list(context.get("decisions", []))
        blind_spots = list(context.get("blind_spots", []))
        admission = dict(context.get("admission_summary", {}))

        status_counts: dict[str, int] = {}
        for project in projects:
            status = project.get("status", "NOT_ASSESSED")
            status_counts[status] = status_counts.get(status, 0) + 1

        discovery_state = self.classify_discovery_failures(discovery_failure_count)
        if discovery_state == "DISCOVERY_UNAVAILABLE":
            overall_status = "DISCOVERY_UNAVAILABLE"
        elif discovery_state == "PARTIAL_DISCOVERY_NOT_ASSESSED":
            overall_status = "PARTIAL_DISCOVERY_NOT_ASSESSED"
        elif status_counts.get("NOT_ASSESSED", 0) or status_counts.get("BLIND_SPOT", 0):
            overall_status = "PASS_WITH_NOT_ASSESSED"
        elif status_counts.get("ATTENTION", 0):
            overall_status = "ATTENTION"
        else:
            overall_status = "PASS"
        capability_mode = (
            context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY"
        )
        capability_source = context.get("capability_source_summary", {})
        if capability_mode:
            if capability_source.get("status") == "DISCOVERY_UNAVAILABLE":
                overall_status = "DISCOVERY_UNAVAILABLE"
            elif capability_source.get("status") == "PASS_WITH_PARTIAL_SOURCE_COVERAGE":
                overall_status = "PASS_WITH_NOT_ASSESSED"
            else:
                overall_status = "PASS"

        observed_at = context.get("as_of", "UNKNOWN")
        try:
            parsed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
            iso = parsed.isocalendar()
            week = f"{iso.year}-W{iso.week:02d}"
        except (AttributeError, ValueError):
            week = "UNKNOWN"

        counts = {
            "projects": len(projects),
            "stable": status_counts.get("STABLE", 0),
            "observed": status_counts.get("OBSERVED", 0),
            "attention": status_counts.get("ATTENTION", 0),
            "blind_spot": status_counts.get("BLIND_SPOT", 0),
            "not_assessed": status_counts.get("NOT_ASSESSED", 0),
            "discovered_count": admission.get("discovered_count", len(discoveries)),
            "admitted_count": admission.get("admitted_count", 0),
            "rejected_or_pending_count": admission.get("rejected_or_pending_count", 0),
            "decisions": len(decisions),
            "blind_spots": len(blind_spots),
            "live_source_success": context.get("source_observation_summary", {}).get(
                "live_source_success_count", 0
            ),
            "source_not_assessed": context.get("source_observation_summary", {}).get(
                "not_assessed_count", 0
            ),
        }
        known_project_count = sum(
            counts[key] for key in ("stable", "observed", "attention", "blind_spot", "not_assessed")
        )
        counts["other"] = counts["projects"] - known_project_count
        counts["project_count_sum_match"] = (
            known_project_count + counts["other"] == counts["projects"]
        )
        weekly_sentence = (
            f"本周共纳入{counts['projects']}个项目视图：{counts['stable']}个稳定，"
            f"{counts['observed']}个已观察，{counts['attention']}个需关注，"
            f"{counts['blind_spot']}个盲区，{counts['not_assessed']}个尚未评估，"
            f"{counts['other']}个其他状态。共收集{counts['discovered_count']}项信号，"
            f"其中{counts['admitted_count']}项已通过证据准入，"
            f"{counts['rejected_or_pending_count']}项被拒绝或待确认；"
            f"有{counts['decisions']}项需要人工决定。"
        )
        registry = context.get("capability_reference_registry", {})
        delta = context.get("capability_discovery_delta", {})
        delta_counts = delta.get("counts", {})
        capability_summary = {}
        highlights: list[dict[str, Any]] = []
        if capability_mode:
            entries = registry.get("entries", [])
            highlights = [
                item
                for item in entries
                if item.get("observation_state")
                in {
                    "NEW_REFERENCE",
                    "UPDATED_REFERENCE",
                    "CONFLICTING_REFERENCE",
                    "STALE_REFERENCE",
                }
                or item.get("ac2_readiness_status") == "REVIEW_ELIGIBLE"
            ][:5]
            capability_summary = {
                "status": capability_source.get("status", "DISCOVERY_UNAVAILABLE"),
                "automation_scope": "AC0_DISCOVERY_AND_AC1_REFERENCE_ONLY",
                "raw_candidate_count": capability_source.get("raw_candidate_count", 0),
                "identity_resolved_count": capability_source.get(
                    "identity_resolved_count", 0
                ),
                "admitted_count": sum(
                    item.get("absorption_status")
                    not in {"REFERENCE_REJECTED", "REFERENCE_CONFLICT"}
                    for item in entries
                ),
                "reference_absorbed_count": sum(
                    item.get("absorption_status") == "REFERENCE_ABSORBED"
                    for item in entries
                ),
                "new_reference_count": delta_counts.get("NEW_REFERENCE", 0),
                "updated_reference_count": delta_counts.get("UPDATED_REFERENCE", 0),
                "conflict_count": delta_counts.get("CONFLICTING_REFERENCE", 0),
                "source_not_assessed_count": capability_source.get(
                    "source_not_assessed_count", 0
                ),
                "code_adopted": 0,
                "runtime_changed": False,
                "ac2_automated": False,
                "reference_only": True,
                "human_decision_count": len(decisions),
            }
            capability_summary["human_summary_zh"] = (
                f"本周自动检查了{capability_summary['raw_candidate_count']}个外部候选，"
                f"新登记{capability_summary['new_reference_count']}个参考候选，"
                f"更新{capability_summary['updated_reference_count']}个既有候选，"
                f"发现{capability_summary['conflict_count']}个身份冲突；"
                "没有安装代码，也没有改变任何项目。"
            )
            weekly_sentence = capability_summary["human_summary_zh"]
        return {
            "schema_version": "0.1",
            "snapshot_id": f"DBA-WEEKLY-{week}",
            "week": week,
            "observed_at": observed_at,
            "overall_status": overall_status,
            "mode": context.get("snapshot_mode", "PROTOTYPE_READ_ONLY_CANDIDATE"),
            "discovery_state": discovery_state,
            "discovery_failure_count": discovery_failure_count,
            "weekly_sentence_zh": weekly_sentence,
            "counts": counts,
            "cell_runs": cell_runs,
            "discoveries": discoveries,
            "decisions": decisions,
            "decisions_source": "HANDOFF_CELL",
            "changes": context.get(
                "changes",
                {"improved": [], "worsened": [], "unknown": [], "observed_this_week": []},
            ),
            "projects": projects,
            "blind_spots": blind_spots,
            "preset_queries": context.get("preset_queries", []),
            "findings": context.get("findings", []),
            "handoff_packets": context.get("handoff_packets", []),
            "logical_cells": list(cell_runs),
            "source_references": context.get("source_paths", {}),
            "run_identity": context.get("run_identity", {}),
            "source_observation_summary": context.get("source_observation_summary", {}),
            "memory": context.get("memory", {"status": "NOT_ASSESSED"}),
            "capability_discovery": capability_summary,
            "capability_highlights": highlights,
            "capability_groups": registry.get("capability_groups", []),
            "capability_registry_digest": registry.get(
                "current_registry_digest", "NOT_APPLICABLE"
            ),
            "capability_reference_registry": registry,
            "capability_discovery_records": context.get(
                "capability_discovery_records", []
            ),
            "capability_source_evidence_manifest": context.get(
                "capability_source_evidence_manifest", {}
            ),
            "capability_discovery_boundary": context.get(
                "capability_discovery_boundary", {}
            ),
            "capability_discovery_delta": delta,
            "admission_summary": admission,
            "dependency_audit_state": context.get(
                "dependency_audit_state",
                {"status": "NOT_ASSESSED"},
            ),
            "boundaries": {
                "read_only": True,
                "view_not_truth": True,
                "new_truth_source": False,
                "new_control_plane": False,
                "auto_fix": False,
                "auto_pr": False,
                "auto_merge": False,
                "auto_deploy": False,
                "prototype_only": context.get("snapshot_mode") != "LIVE_READ_ONLY_OBSERVATION_PILOT",
                "pilot_only": context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT",
                "schedule_enabled": False,
                "automatic_capability_discovery": capability_mode,
                "ac0_automated": capability_mode,
                "ac1_automated": capability_mode,
                "ac2_automated": False,
                "reference_only": capability_mode,
                "code_adopted": 0,
                "runtime_changed": False,
                "source_mutation": bool(context.get("source_mutation", False)),
            },
        }

    @staticmethod
    def classify_discovery_failures(failure_count: int) -> str:
        if failure_count == 0:
            return "AVAILABLE"
        if failure_count in {1, 2}:
            return "PARTIAL_DISCOVERY_NOT_ASSESSED"
        return "DISCOVERY_UNAVAILABLE"

    @staticmethod
    def _projects(context: dict[str, Any]) -> list[dict[str, Any]]:
        return list(context.get("project_records", []))
