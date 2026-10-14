"""Discover registered projects and adjacent candidates without admitting them."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value


class ProjectDiscoveryCell(WeeklyCell):
    cell_id = "PROJECT_DISCOVERY_CELL"

    def _run(self, context: dict[str, Any]):
        as_of = context.get("as_of", "UNKNOWN")
        live_mode = context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT"
        source_observations = context.get("source_observations", {})
        registry = source_value(
            context,
            "project_registry",
            source_value(context, "project_check_registry", {}),
        )
        entries = registry.get("projects", registry.get("entries", [])) if isinstance(registry, dict) else registry
        project_records: list[dict[str, Any]] = []
        for item in entries or []:
            observation = source_observations.get(item["project_id"], {})
            observation_status = observation.get("status")
            if observation_status == "AVAILABLE":
                source_label = "LIVE"
                why = "已获得限定范围的实时只读来源观察；该观察不构成项目验收。"
            elif observation_status == "SOURCE_DRIFT":
                source_label = "STALE"
                why = "声明来源与实时来源发生漂移，当前状态按失败关闭处理。"
            elif live_mode:
                source_label = "NOT_ASSESSED"
                why = "实时来源不可用或凭据不可用；未评估不等于正常。"
            else:
                source_label = "RETAINED_SNAPSHOT"
                why = "已登记项目身份与保留来源，状态等待有边界的分析 Cell 更新。"
            project_records.append(
                {
                    "project_id": item["project_id"],
                    "display_name_zh": item.get("display_name_zh", item["project_id"]),
                    "lifecycle_mode": item.get("lifecycle_mode", "UNKNOWN"),
                    "owner_conversation": item.get("owner_conversation", "UNKNOWN"),
                    "source_reference": item.get("canonical_source_ref", "UNKNOWN"),
                    "source_access_mode": item.get("source_access_mode", "READ_ONLY"),
                    "source_label": source_label,
                    "source_observation_status": observation_status or "RETAINED_SNAPSHOT",
                    "status": "NOT_ASSESSED",
                    "status_zh": "尚未评估",
                    "why_zh": why,
                    "attention_zh": "未评估不等于正常。",
                    "technical_evidence": [
                        observation.get("source_reference", item.get("canonical_source_ref", "UNKNOWN"))
                    ],
                }
            )

        candidate = {
            "candidate_id": "candidate-openbao-2026-W35",
            "signal_id": "DISCOVERY-OPENBAO-CANDIDATE",
            "project_id": "openbao-adjacent-signal",
            "kind": "ADJACENT_PROJECT_CANDIDATE",
            "subject": "OpenBao",
            "display_name": "OpenBao（机密与密钥管理组件）候选",
            "title_zh": "OpenBao（机密与密钥管理组件）候选",
            "source_reference": "project-discovery:public-adjacent-candidate",
            "discovered_at": as_of,
            "observed_at": as_of,
            "lifecycle": "CANDIDATE",
            "current_state": "DISCOVERED",
            "observed_state": "DISCOVERED",
            "freshness": "UNKNOWN",
            "authority": "DISCOVERY_ONLY",
            "scan_authorized": False,
            "private_content_scanned": False,
            "read_only": True,
            "admission_status": "NOT_ADMITTED",
            "monitoring_status": "NOT_MONITORED",
            "admission_label_zh": "待人工确认候选",
            "details_zh": "OpenBao（机密与密钥管理组件）仍是待确认候选；应先刷新当前版本与安全事实。",
            "note": "Discovery does not grant evidence admission, monitoring, or scan authority.",
        }
        capability_records = list(context.get("capability_discovery_records", []))
        return make_result(
            self.cell_id,
            "PASS",
            "Registered project identities and one adjacent candidate were discovered without admission.",
            discoveries=[candidate] + capability_records,
            outputs={
                "project_records": project_records,
                "discovery_records": [candidate] + capability_records,
            },
        )
