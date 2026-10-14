"""Discover current environment signals without turning candidates into truth."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value


def _nested_number(source: dict[str, Any], *paths: tuple[str, ...], default: int) -> int:
    for path in paths:
        value: Any = source
        for key in path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        if isinstance(value, int):
            return value
    return default


def _packages(source: dict[str, Any], default: list[str] | None = None) -> list[str]:
    for path in (
        ("live_high_packages",),
        ("live_candidate", "high_packages"),
        ("live_candidate", "packages"),
        ("observed_result", "high_packages"),
    ):
        value: Any = source
        for key in path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return value
    return list(default or [])


class EnvironmentDiscoveryCell(WeeklyCell):
    cell_id = "ENVIRONMENT_DISCOVERY_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            summary = context.get("capability_source_summary", {})
            source_status = summary.get("status", "DISCOVERY_UNAVAILABLE")
            status = (
                "PASS"
                if source_status == "PASS"
                else "NOT_ASSESSED"
                if source_status == "DISCOVERY_UNAVAILABLE"
                else "PASS_WITH_CANDIDATES"
            )
            return make_result(
                self.cell_id,
                status,
                "Bounded public capability sources were observed without executing external content.",
                outputs={"capability_source_summary": summary},
            )
        if context.get("snapshot_mode") == "LIVE_READ_ONLY_OBSERVATION_PILOT":
            return self._run_live(context)
        as_of = context.get("as_of", "UNKNOWN")
        live = source_value(context, "live_dependency_audit", {}) or {}
        canonical_count = _nested_number(
            live,
            ("canonical_high_count",),
            ("canonical_retained", "high_count"),
            default=2,
        )
        live_count = _nested_number(
            live,
            ("live_high_count",),
            ("live_candidate", "high_count"),
            ("observed_result", "high_count"),
            default=4,
        )
        packages = _packages(live, ["image-size", "js-yaml", "nanoid", "vinext"])
        source_ref = source_value(context, "source_paths", {}).get(
            "live_dependency_audit",
            "inputs/live-dependency-audit-candidate-2026-08-29.json",
        )

        discoveries = [
            {
                "signal_id": "DISCOVERY-DEPENDENCY-AUDIT-CONFLICT",
                "kind": "DEPENDENCY_SECURITY_CONFLICT_CANDIDATE",
                "subject": "DBA dependency audit state",
                "title_zh": "依赖安全状态出现待复核冲突",
                "observed_state": "CONFLICT_CANDIDATE",
                "current_state": "DISCOVERED",
                "source_reference": source_ref,
                "observed_at": live.get("observed_at", as_of),
                "freshness": "CURRENT",
                "authority": "CANDIDATE_OBSERVATION",
                "admission_status": "PENDING",
                "admission_label_zh": "待证据准入",
                "details_zh": (
                    f"本周实时扫描报告{live_count}个高危依赖包，历史权威记录仍为"
                    f"{canonical_count}个；候选包为{', '.join(packages)}。"
                ),
                "canonical_high_count": canonical_count,
                "live_candidate_high_count": live_count,
                "live_high_packages": packages,
                "runtime_binding": "NOT_ESTABLISHED",
                "exploitability": "NOT_ASSESSED",
            },
            {
                "signal_id": "DISCOVERY-TITMAS-MATRIX-STALE",
                "kind": "COMPONENT_STATUS_SIGNAL",
                "subject": "TITMAS component matrix",
                "title_zh": "TITMAS 组件矩阵状态待刷新",
                "observed_state": "STALE",
                "current_state": "DISCOVERED",
                "source_reference": source_value(context, "source_paths", {}).get("component_matrix", "UNKNOWN"),
                "observed_at": as_of,
                "freshness": "STALE",
                "authority": "DISCOVERY_ONLY",
                "admission_status": "PENDING",
                "admission_label_zh": "待证据准入",
                "details_zh": "现有组件矩阵不能自动获得本周当前状态权威。",
            },
            {
                "signal_id": "DISCOVERY-SCOUT-STATUS-STALE",
                "kind": "PROJECT_STATUS_SIGNAL",
                "subject": "TITMAC Scout read-only status",
                "title_zh": "TITMAC Scout 当前只读状态待刷新",
                "observed_state": "UNKNOWN",
                "current_state": "DISCOVERED",
                "source_reference": source_value(context, "source_paths", {}).get("scout_projection", "UNKNOWN"),
                "observed_at": as_of,
                "freshness": "UNKNOWN",
                "authority": "DISCOVERY_ONLY",
                "admission_status": "PENDING",
                "admission_label_zh": "待证据准入",
                "details_zh": "现有投影没有提供足够新鲜度，不能推断当前状态。",
            },
        ]
        project_updates = [
            {
                "project_id": "TITMAC_SCOUT",
                "status": "BLIND_SPOT",
                "status_zh": "检查盲区",
                "why_zh": "当前只读状态来源缺少足够新鲜度，不能据此判定项目正常或异常。",
                "attention_zh": "如需刷新，必须获得单独只读授权。",
            }
        ]
        blind_spots = [
            {
                "blind_spot_id": "SCOUT_STATUS_STALE",
                "project_id": "TITMAC_SCOUT",
                "title_zh": "TITMAC Scout 的只读状态尚未刷新",
                "impact_zh": "当前周检不能确认其最新检查、版本与运行状态。",
                "status": "NOT_ASSESSED",
                "source_reference": source_value(context, "source_paths", {}).get("scout_projection", "UNKNOWN"),
            }
        ]
        return make_result(
            self.cell_id,
            "PASS_WITH_CANDIDATES",
            "Current environment candidates were recorded without authority escalation.",
            discoveries=discoveries,
            outputs={
                "discovery_records": discoveries,
                "project_updates": project_updates,
                "blind_spots": blind_spots,
            },
        )

    def _run_live(self, context: dict[str, Any]):
        as_of = context.get("as_of", "UNKNOWN")
        dependency = source_value(context, "live_dependency_audit", {}) or {}
        canonical_count = _nested_number(
            dependency, ("canonical_retained", "high_count"), default=2
        )
        live_count = _nested_number(
            dependency, ("observed_result", "high_count"), default=-1
        )
        packages = _packages(dependency)
        dependency_available = dependency.get("audit_status") == "AVAILABLE" and live_count >= 0
        conflict = dependency_available and live_count != canonical_count
        dependency_kind = (
            "DEPENDENCY_SECURITY_CONFLICT_CANDIDATE"
            if conflict else "DEPENDENCY_SECURITY_MATCH_CANDIDATE"
            if dependency_available else "DEPENDENCY_AUDIT_UNAVAILABLE"
        )
        dependency_state = (
            "CONFLICT_CANDIDATE" if conflict else "OBSERVED" if dependency_available else "UNKNOWN"
        )
        source_ref = source_value(context, "source_paths", {}).get(
            "live_dependency_audit", "digital-biosphere-architecture/site/package-lock.json"
        )
        observations = context.get("source_observations", {})
        titmas = observations.get("TITMAS_SUPPORTING_LAYER", {})
        scout = observations.get("TITMAC_SCOUT", {})
        scout_source_status = scout.get("status", "NOT_ASSESSED_SOURCE_UNAVAILABLE")
        scout_payload = scout.get("payload", {})
        scout_reason = scout_payload.get(
            "reason_code", scout_payload.get("reason", scout_source_status)
        )
        scout_reference = scout.get(
            "source_reference", "cockpit/source-registry.json#titmac-scout"
        )
        if scout_source_status == "AVAILABLE":
            scout_projection = {
                "project_id": "TITMAC_SCOUT",
                "status": "OBSERVED",
                "status_zh": "已实时观察",
                "source_label": "LIVE",
                "source_observation_status": "AVAILABLE",
                "why_zh": "现有只读状态适配器已完成实时观察。",
                "attention_zh": "仓库观察不构成运行时验收或生产就绪结论。",
                "technical_evidence": [scout_reference],
            }
            scout_blind_spot = None
        elif scout_source_status == "NOT_ASSESSED_CREDENTIAL_UNAVAILABLE":
            scout_projection = {
                "project_id": "TITMAC_SCOUT",
                "status": "NOT_ASSESSED",
                "status_zh": "跨仓库凭据不可用，未评估",
                "source_label": "NOT_ASSESSED",
                "source_observation_status": scout_source_status,
                "reason_code": "CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
                "why_zh": "跨仓库只读凭据不可用，未读取私有仓库状态。",
                "attention_zh": "未评估不等于正常。",
                "technical_evidence": [scout_reference],
            }
            scout_blind_spot = {
                "blind_spot_id": "SCOUT_CREDENTIAL_UNAVAILABLE",
                "project_id": "TITMAC_SCOUT",
                "title_zh": "TITMAC Scout 私有来源因凭据不可用而未评估",
                "impact_zh": "本轮不能确认其最新检查、版本与运行状态。",
                "status": scout_source_status,
                "reason_code": "CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
                "source_reference": scout_reference,
            }
        elif scout_source_status == "NOT_ASSESSED_SOURCE_UNAVAILABLE" and scout_reason == "SOURCE_STALE":
            scout_projection = {
                "project_id": "TITMAC_SCOUT",
                "status": "NOT_ASSESSED",
                "status_zh": "来源过期，未评估",
                "source_label": "STALE",
                "source_observation_status": scout_source_status,
                "reason_code": "SOURCE_STALE",
                "why_zh": "Scout 来源已过期，当前不能据此判断最新状态。",
                "attention_zh": "未评估不等于正常。",
                "technical_evidence": [scout_reference],
            }
            scout_blind_spot = {
                "blind_spot_id": "SCOUT_SOURCE_STALE",
                "project_id": "TITMAC_SCOUT",
                "title_zh": "TITMAC Scout 来源过期，未评估",
                "impact_zh": "Scout 来源已过期，当前不能据此判断最新状态。",
                "status": scout_source_status,
                "reason_code": "SOURCE_STALE",
                "source_reference": scout_reference,
            }
        elif scout_source_status == "SOURCE_DRIFT":
            scout_projection = {
                "project_id": "TITMAC_SCOUT",
                "status": "NOT_ASSESSED",
                "status_zh": "来源发生漂移，未评估",
                "source_label": "STALE",
                "source_observation_status": scout_source_status,
                "reason_code": "SOURCE_DRIFT",
                "why_zh": "Scout 来源发生漂移，当前不能据此判断最新状态。",
                "attention_zh": "需要来源所有者重新建立可验证的新鲜引用。",
                "technical_evidence": [scout_reference],
            }
            scout_blind_spot = {
                "blind_spot_id": "SCOUT_SOURCE_DRIFT",
                "project_id": "TITMAC_SCOUT",
                "title_zh": "TITMAC Scout 来源发生漂移，未评估",
                "impact_zh": "来源身份或内容发生漂移，当前观察不能建立最新状态。",
                "status": scout_source_status,
                "reason_code": "SOURCE_DRIFT",
                "source_reference": scout_reference,
            }
        else:
            scout_projection = {
                "project_id": "TITMAC_SCOUT",
                "status": "NOT_ASSESSED",
                "status_zh": "来源不可用，未评估",
                "source_label": "NOT_ASSESSED",
                "source_observation_status": scout_source_status,
                "reason_code": scout_reason,
                "why_zh": f"Scout 来源不可用；原因：{scout_reason}。",
                "attention_zh": "未评估不等于正常。",
                "technical_evidence": [scout_reference],
            }
            scout_blind_spot = {
                "blind_spot_id": "SCOUT_SOURCE_UNAVAILABLE",
                "project_id": "TITMAC_SCOUT",
                "title_zh": "TITMAC Scout 来源不可用，未评估",
                "impact_zh": f"当前不能确认最新状态；原因：{scout_reason}。",
                "status": scout_source_status,
                "reason_code": scout_reason,
                "source_reference": scout_reference,
            }
        http = context.get("public_http_observations", [])
        http_available = sum(item.get("status") == "AVAILABLE" for item in http)
        discoveries = [
            {
                "signal_id": "DISCOVERY-DEPENDENCY-AUDIT-LIVE",
                "kind": dependency_kind,
                "subject": "DBA dependency audit state",
                "title_zh": "依赖安全实时只读观察",
                "observed_state": dependency_state,
                "current_state": "DISCOVERED",
                "source_reference": source_ref,
                "observed_at": as_of,
                "freshness": "CURRENT" if dependency_available else "UNKNOWN",
                "authority": "LIVE_READ_ONLY_OBSERVATION",
                "admission_status": "PENDING",
                "admission_label_zh": "待证据准入",
                "details_zh": (
                    f"本轮只读扫描观察到{live_count}个高危依赖项，保留记录为{canonical_count}个。"
                    if dependency_available else "依赖审计未产生可解析结果，不能推断当前依赖状态。"
                ),
                "canonical_high_count": canonical_count,
                "live_candidate_high_count": live_count if dependency_available else None,
                "live_high_packages": packages,
                "runtime_binding": "NOT_ESTABLISHED",
                "exploitability": "NOT_ASSESSED",
            },
            {
                "signal_id": "DISCOVERY-TITMAS-LIVE-OBSERVATION",
                "kind": "PROJECT_LIVE_OBSERVATION",
                "subject": "TITMAS supporting repository",
                "title_zh": "TITMAS 支撑仓库只读观察",
                "observed_state": titmas.get("status", "NOT_ASSESSED"),
                "current_state": "DISCOVERED",
                "source_reference": titmas.get("source_reference", "UNKNOWN"),
                "observed_at": as_of,
                "freshness": "CURRENT" if titmas.get("status") == "AVAILABLE" else "UNKNOWN",
                "authority": "LIVE_READ_ONLY_OBSERVATION",
                "admission_status": "PENDING",
                "admission_label_zh": "待人工确认候选",
                "details_zh": "仓库元数据仅用于当前观察，不构成升级建议或项目验收。",
            },
            {
                "signal_id": "DISCOVERY-SCOUT-STATUS",
                "kind": "PROJECT_STATUS_SIGNAL",
                "subject": "TITMAC Scout read-only status",
                "title_zh": "TITMAC Scout 只读来源观察",
                "observed_state": scout_source_status,
                "current_state": "DISCOVERED",
                "source_reference": scout_reference,
                "observed_at": as_of,
                "freshness": "CURRENT" if scout_source_status == "AVAILABLE" else "STALE" if scout_reason in {"SOURCE_STALE", "SOURCE_DRIFT"} else "UNKNOWN",
                "authority": "LIVE_READ_ONLY_OBSERVATION",
                "admission_status": "PENDING",
                "admission_label_zh": "未评估",
                "details_zh": scout_projection["why_zh"],
            },
            {
                "signal_id": "DISCOVERY-DCELL-PUBLIC-ENDPOINTS",
                "kind": "PUBLIC_ENDPOINT_OBSERVATION",
                "subject": "dcell.net public endpoints",
                "title_zh": "dcell.net 公开端点只读观察",
                "observed_state": f"{http_available}/{len(http)}_OBSERVED",
                "current_state": "DISCOVERED",
                "source_reference": "https://dcell.net/",
                "observed_at": as_of,
                "freshness": "CURRENT" if http else "UNKNOWN",
                "authority": "HTTP_OBSERVATION_ONLY",
                "admission_status": "PENDING",
                "admission_label_zh": "待人工确认候选",
                "details_zh": "HTTP 状态仅证明本轮响应，不构成部署验收、健康认证或生产结论。",
            },
        ]
        project_updates = [scout_projection]
        blind_spots = [] if scout_blind_spot is None else [scout_blind_spot]
        return make_result(
            self.cell_id,
            "PASS_WITH_CANDIDATES",
            "Live environment observations were recorded without mutation or authority escalation.",
            discoveries=discoveries,
            outputs={
                "discovery_records": discoveries,
                "project_updates": project_updates,
                "blind_spots": blind_spots,
            },
        )
