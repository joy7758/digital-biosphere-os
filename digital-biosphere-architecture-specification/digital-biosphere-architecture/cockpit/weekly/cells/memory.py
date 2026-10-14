"""Describe temporal change only when a previous snapshot exists."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value


class MemoryCell(WeeklyCell):
    cell_id = "MEMORY_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            metadata = context.get("capability_memory_metadata", {})
            delta = context.get(
                "capability_discovery_delta", {"counts": {}, "events": []}
            )
            previous_loaded = metadata.get("previous_registry_loaded") is True
            memory = {
                "status": (
                    "COMPARISON_AVAILABLE"
                    if previous_loaded
                    else "BOOTSTRAPPED_FROM_DCDAT_001"
                ),
                "PREVIOUS_CAPABILITY_REGISTRY_LOADED": previous_loaded,
                "PREVIOUS_LIVE_ARTIFACT_LOADED": previous_loaded,
                "MEMORY_COMPARISON_EXECUTED": True,
                "MEMORY_BOOTSTRAP_SOURCE": metadata.get(
                    "memory_bootstrap_source", "DCDAT_001_BASELINE"
                ),
                "PREVIOUS_ARTIFACT_REJECTED": metadata.get(
                    "previous_artifact_rejected", False
                ),
                "PREVIOUS_CAPABILITY_RUN_ID": metadata.get("previous_run_id"),
                "PREVIOUS_CAPABILITY_ARTIFACT_ID": metadata.get("artifact_id"),
                "PREVIOUS_CAPABILITY_SOURCE_REFERENCE": metadata.get(
                    "source_reference"
                ),
                "note_zh": "已比较本轮候选与上一轮合格注册表；无合格制品时使用DCDAT-001且明确记录。",
                "capability_delta": delta,
            }
            changes = {
                "improved": [],
                "worsened": [
                    item["candidate_id"]
                    for item in delta.get("events", [])
                    if item["state"] == "CONFLICTING_REFERENCE"
                ],
                "unknown": [
                    item["candidate_id"]
                    for item in delta.get("events", [])
                    if item["state"] in {"NO_LONGER_OBSERVED", "STALE_REFERENCE"}
                ],
                "observed_this_week": [
                    item["candidate_id"]
                    for item in delta.get("events", [])
                    if item["state"]
                    in {
                        "NEW_REFERENCE",
                        "UPDATED_REFERENCE",
                        "CONTINUING_REFERENCE",
                        "REAPPEARED_REFERENCE",
                    }
                ],
            }
            return make_result(
                self.cell_id,
                "PASS",
                "Capability reference memory was compared without overwriting historical events.",
                outputs={"memory": memory, "changes": changes},
            )
        previous = source_value(context, "previous_snapshot")
        discoveries = context.get("discovery_records", [])
        live_mode = context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT"
        artifact = context.get("artifact_memory_metadata", {})
        if not previous:
            artifact_status = artifact.get("memory_status")
            memory = {
                "status": artifact_status or "NOT_ASSESSED_NO_PREVIOUS_SNAPSHOT",
                "previous_snapshot_reference": None,
                "trend_claim_allowed": False,
                "note_zh": (
                    "没有符合条件的上一轮实时制品，尚不能形成跨运行变化判断。"
                    if live_mode else "首次快照，尚不能判断这些信号是否相对于上周新增。"
                ),
                "PREVIOUS_LIVE_ARTIFACT_LOADED": False,
                "MEMORY_COMPARISON_EXECUTED": False,
                "ARTIFACT_FROM_CURRENT_RUN_REJECTED": artifact.get(
                    "ARTIFACT_FROM_CURRENT_RUN_REJECTED", True if live_mode else None
                ),
                "FAILED_OR_EXPIRED_ARTIFACT_REJECTED": artifact.get(
                    "FAILED_OR_EXPIRED_ARTIFACT_REJECTED", True if live_mode else None
                ),
            }
            changes = {
                "improved": [],
                "worsened": [],
                "unknown": ["首次快照，尚不能判断这些信号是否相对于上周新增。"],
                "observed_this_week": [
                    item.get("title_zh", item.get("subject", "本周信号"))
                    for item in discoveries
                    if item.get("freshness") == "CURRENT"
                ],
            }
            status = "NOT_ASSESSED"
        else:
            current_findings = context.get("findings", [])
            comparison = self.compare_findings(previous.get("findings", []), current_findings)
            memory = {
                "status": "COMPARISON_AVAILABLE",
                "previous_snapshot_reference": previous.get("snapshot_id", "UNKNOWN"),
                "trend_claim_allowed": True,
                "note_zh": "已按 finding_id、project_id 与 finding_type 比较上一轮实时制品。",
                "PREVIOUS_LIVE_ARTIFACT_LOADED": True,
                "MEMORY_COMPARISON_EXECUTED": True,
                "ARTIFACT_FROM_CURRENT_RUN_REJECTED": artifact.get(
                    "ARTIFACT_FROM_CURRENT_RUN_REJECTED", True
                ),
                "FAILED_OR_EXPIRED_ARTIFACT_REJECTED": artifact.get(
                    "FAILED_OR_EXPIRED_ARTIFACT_REJECTED", True
                ),
                "comparison": comparison,
            }
            changes = {
                "improved": comparison["CLOSED"],
                "worsened": comparison["NEW"] + comparison["REAPPEARED"],
                "unknown": comparison["CONTINUING"],
                "observed_this_week": comparison["NEW"] + comparison["CONTINUING"] + comparison["REAPPEARED"],
            }
            status = "PASS"
        return make_result(
            self.cell_id,
            status,
            "Memory preserved temporal boundaries without inventing week-over-week change.",
            outputs={"memory": memory, "changes": changes},
        )

    @staticmethod
    def compare_findings(
        previous_findings: list[dict[str, Any]], current_findings: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        def identity(item: dict[str, Any]) -> tuple[str, str, str] | None:
            values = (
                item.get("finding_id"), item.get("project_id"), item.get("finding_type")
            )
            return values if all(isinstance(value, str) and value for value in values) else None

        previous = {key: item for item in previous_findings if (key := identity(item))}
        current = {key: item for item in current_findings if (key := identity(item))}
        continuing = sorted(" | ".join(key) for key in previous.keys() & current.keys())
        new = sorted(" | ".join(key) for key in current.keys() - previous.keys())
        closed = sorted(" | ".join(key) for key in previous.keys() - current.keys())
        reappeared = sorted(
            " | ".join(key)
            for key in previous.keys() & current.keys()
            if previous[key].get("lifecycle_status") == "CLOSED"
        )
        continuing = [item for item in continuing if item not in reappeared]
        return {
            "NEW": new,
            "CONTINUING": continuing,
            "CLOSED": closed,
            "REAPPEARED": reappeared,
        }
