"""Keep stale or rejected component signals out of upgrade recommendations."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result


class UpgradeCell(WeeklyCell):
    cell_id = "UPGRADE_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            entries = context.get("capability_reference_registry", {}).get("entries", [])
            eligible = [
                item["candidate_id"]
                for item in entries
                if item.get("ac2_readiness_status") == "REVIEW_ELIGIBLE"
                and item.get("current_problem_match")
            ]
            return make_result(
                self.cell_id,
                "PASS",
                "Reference candidates were classified for possible human AC-2 review without adoption.",
                outputs={
                    "upgrade_recommendations": [],
                    "ac2_review_eligible_candidate_ids": eligible,
                },
            )
        if context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT":
            observation = context.get("source_observations", {}).get("TITMAS_SUPPORTING_LAYER", {})
            available = observation.get("status") == "AVAILABLE"
            return make_result(
                self.cell_id,
                "PASS" if available else "NOT_ASSESSED",
                "Live repository metadata was observed without creating an upgrade recommendation.",
                outputs={
                    "project_updates": [{
                        "project_id": "TITMAS_SUPPORTING_LAYER",
                        "status": "OBSERVED" if available else "NOT_ASSESSED",
                        "status_zh": "已实时观察" if available else "来源未评估",
                        "source_label": "LIVE" if available else "NOT_ASSESSED",
                        "why_zh": "只读仓库元数据可用；本轮不形成升级建议。" if available else "实时来源不可用。",
                        "attention_zh": "仓库可见性不构成版本升级授权。",
                    }],
                    "upgrade_recommendations": [],
                },
            )
        rejected = context.get("rejected_observations", [])
        component_rejected = any(
            item.get("observation", {}).get("kind") == "COMPONENT_STATUS_SIGNAL"
            for item in rejected
        )
        updates = []
        if component_rejected:
            updates.append(
                {
                    "project_id": "TITMAS_SUPPORTING_LAYER",
                    "status": "NOT_ASSESSED",
                    "status_zh": "升级状态未评估",
                    "why_zh": "组件状态来源已过期，不能转化为本周升级建议。",
                    "attention_zh": "需要新的只读证据后再评估。",
                }
            )
        return make_result(
            self.cell_id,
            "NOT_ASSESSED" if component_rejected else "PASS",
            "Rejected or stale signals did not become upgrade recommendations.",
            outputs={
                "project_updates": updates,
                "upgrade_recommendations": [],
            },
        )
