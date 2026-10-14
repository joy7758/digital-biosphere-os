"""Interpret bounded quality evidence for registered projects."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value


class QualityCell(WeeklyCell):
    cell_id = "QUALITY_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            summary = context.get("capability_source_summary", {})
            complete = summary.get("status") == "PASS"
            return make_result(
                self.cell_id,
                "PASS" if complete else "NOT_ASSESSED",
                "Source completeness and identity evidence were reported without a composite score.",
                outputs={
                    "capability_quality": {
                        "source_status": summary.get(
                            "status", "DISCOVERY_UNAVAILABLE"
                        ),
                        "identity_conflict_count": summary.get(
                            "identity_conflict_count", 0
                        ),
                        "composite_score": None,
                    }
                },
            )
        if context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT":
            observation = context.get("source_observations", {}).get("DIGITAL_CELL_DEMO", {})
            available = observation.get("status") == "AVAILABLE"
            updates = [{
                "project_id": "DIGITAL_CELL_DEMO",
                "status": "OBSERVED" if available else "NOT_ASSESSED",
                "status_zh": "已实时观察" if available else "来源未评估",
                "source_label": "LIVE" if available else "NOT_ASSESSED",
                "why_zh": (
                    "已读取公开仓库 HEAD、近期 CI 与发布元数据。"
                    if available else "公开仓库实时观察未完成。"
                ),
                "attention_zh": "该观察不构成生产就绪、认证或部署结论。",
                "technical_evidence": [observation.get("source_reference", "UNKNOWN")],
            }]
            return make_result(
                self.cell_id,
                "PASS" if available else "NOT_ASSESSED",
                "Digital Cell public metadata was interpreted without certification claims.",
                outputs={"project_updates": updates},
            )
        source_ref = source_value(context, "source_paths", {}).get("convergence", "UNKNOWN")
        updates = [
            {
                "project_id": "DIGITAL_CELL_DEMO",
                "status": "STABLE",
                "status_zh": "参考演示稳定",
                "why_zh": "冻结参考演示及其既有验证记录可读取；本周未授权新增执行。",
                "attention_zh": "该状态不构成生产就绪或认证。",
                "technical_evidence": [source_ref],
            }
        ]
        return make_result(
            self.cell_id,
            "PASS",
            "Bounded quality evidence was interpreted without a composite score.",
            outputs={"project_updates": updates},
        )
