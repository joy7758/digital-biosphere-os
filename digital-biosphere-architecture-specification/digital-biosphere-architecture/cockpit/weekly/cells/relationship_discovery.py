"""Discover declared relationships without treating them as defects."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value


class RelationshipDiscoveryCell(WeeklyCell):
    cell_id = "RELATIONSHIP_DISCOVERY_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            relationships = list(context.get("capability_relationship_records", []))
            return make_result(
                self.cell_id,
                "PASS",
                "Exact paper, repository, product, reproduction, and shared-repository boundaries were preserved.",
                observations=relationships,
                outputs={"capability_relationship_records": relationships},
            )
        as_of = context.get("as_of", "UNKNOWN")
        source_ref = source_value(context, "source_paths", {}).get("source_registry", "UNKNOWN")
        records = [
            {
                "signal_id": "RELATIONSHIP-RED-YAN-DBA",
                "kind": "DECLARED_PROJECT_RELATIONSHIP",
                "subject": "红岩公文与 DBA 驾驶舱",
                "title_zh": "红岩公文与 DBA 驾驶舱的声明关系",
                "observed_state": "DECLARED",
                "current_state": "DISCOVERED",
                "source_reference": source_ref,
                "observed_at": as_of,
                "freshness": "CURRENT",
                "authority": "RELATIONSHIP_REFERENCE_ONLY",
                "admission_status": "PENDING",
                "admission_label_zh": "待人工确认候选",
                "details_zh": "这是已声明的项目关系，不是新漏洞，也不授予跨项目控制权。",
            },
            {
                "signal_id": "RELATIONSHIP-TITMAS-DIGITAL-CELL",
                "kind": "DECLARED_PROJECT_RELATIONSHIP",
                "subject": "TITMAS 支撑层与数字细胞演示",
                "title_zh": "TITMAS 支撑层与数字细胞演示的声明关系",
                "observed_state": "DECLARED",
                "current_state": "DISCOVERED",
                "source_reference": source_ref,
                "observed_at": as_of,
                "freshness": "CURRENT",
                "authority": "RELATIONSHIP_REFERENCE_ONLY",
                "admission_status": "PENDING",
                "admission_label_zh": "待人工确认候选",
                "details_zh": "这是引用关系，不代表部署、认证、运行绑定或新的安全事实。",
            },
        ]
        return make_result(
            self.cell_id,
            "PASS",
            "Declared relationships were recorded as references, not vulnerabilities.",
            discoveries=records,
            outputs={"discovery_records": records},
        )
