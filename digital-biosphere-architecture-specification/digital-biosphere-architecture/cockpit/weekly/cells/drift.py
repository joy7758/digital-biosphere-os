"""Report conflicts between retained canonical state and current candidate evidence."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result, source_value
from .environment_discovery import _nested_number, _packages


class DriftCell(WeeklyCell):
    cell_id = "DRIFT_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            delta = context.get(
                "capability_discovery_delta", {"counts": {}, "events": []}
            )
            return make_result(
                self.cell_id,
                (
                    "ATTENTION"
                    if delta.get("counts", {}).get("CONFLICTING_REFERENCE", 0)
                    else "PASS"
                ),
                "Current source revisions were compared with reference memory without changing source projects.",
                outputs={"capability_drift": delta},
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
        explanation = (
            f"本周实时扫描报告{live_count}个高危依赖包，而驾驶舱历史权威记录仍为"
            f"{canonical_count}个。两者尚未对齐，需要核对锁文件、扫描范围和是否进入实际运行环境。"
        )
        finding = {
            "finding_id": "FINDING-DEPENDENCY-AUDIT-STATE-CONFLICT-2026-W35",
            "finding_type": "DEPENDENCY_AUDIT_STATE_CONFLICT",
            "project_id": "DBA_COCKPIT",
            "severity": "ATTENTION",
            "category": "SECURITY_DRIFT",
            "title": "历史与实时依赖审计状态冲突",
            "title_zh": "历史与实时依赖审计状态冲突",
            "human_explanation": explanation,
            "source_reference": source_ref,
            "observed_at": live.get("observed_at", as_of),
            "canonical_high_count": canonical_count,
            "live_candidate_high_count": live_count,
            "live_high_packages": packages,
            "runtime_binding": "NOT_ESTABLISHED",
            "exploitability": "NOT_ASSESSED",
            "reconciliation_required": True,
            "authorization": "NONE",
            "version_change_recommended": False,
        }
        project_updates = [
            {
                "project_id": "DBA_COCKPIT",
                "status": "ATTENTION",
                "status_zh": "依赖审计状态待复核",
                "why_zh": explanation,
                "attention_zh": f"候选包：{', '.join(packages)}；可利用性尚未评估。",
                "technical_evidence": [source_ref],
            },
            {
                "project_id": "RED_YAN_OFFICIAL_DOCUMENT",
                "status": "STABLE",
                "status_zh": "当前主线稳定",
                "why_zh": "现有权威快照可读取，本周驾驶舱未修改红岩项目。",
                "attention_zh": "该视图不替代红岩专用对话中的项目判断。",
                "technical_evidence": [source_value(context, "source_paths", {}).get("redyan", "UNKNOWN")],
            },
        ]
        blind_spots = [
            {
                "blind_spot_id": "DEPENDENCY_RUNTIME_BINDING_UNKNOWN",
                "project_id": "DBA_COCKPIT",
                "title_zh": "依赖漏洞的远端运行绑定未观察",
                "impact_zh": "当前只能确认扫描候选与历史记录冲突，不能确认这些包是否进入实际远端运行路径。",
                "status": "NOT_ASSESSED",
                "source_reference": source_ref,
            }
        ]
        return make_result(
            self.cell_id,
            "ATTENTION",
            "A canonical-versus-live dependency audit conflict requires review.",
            findings=[finding],
            outputs={
                "project_updates": project_updates,
                "blind_spots": blind_spots,
                "dependency_audit_state": {
                    "status": "CONFLICT_REQUIRES_REVIEW",
                    "canonical_high_count": canonical_count,
                    "live_candidate_high_count": live_count,
                    "live_high_packages": packages,
                    "runtime_binding": "NOT_ESTABLISHED",
                    "exploitability": "NOT_ASSESSED",
                    "auto_reconciliation": False,
                },
            },
        )

    def _run_live(self, context: dict[str, Any]):
        as_of = context.get("as_of", "UNKNOWN")
        live = source_value(context, "live_dependency_audit", {}) or {}
        canonical_count = _nested_number(live, ("canonical_retained", "high_count"), default=2)
        live_count = _nested_number(live, ("observed_result", "high_count"), default=-1)
        packages = _packages(live)
        audit_available = live.get("audit_status") == "AVAILABLE" and live_count >= 0
        conflict = audit_available and live_count != canonical_count
        source_ref = source_value(context, "source_paths", {}).get(
            "live_dependency_audit", "digital-biosphere-architecture/site/package-lock.json"
        )
        findings = []
        if conflict:
            explanation = (
                f"本轮实时只读扫描观察到{live_count}个高危依赖项，而保留记录仍为"
                f"{canonical_count}个。两者尚未对齐，且远端运行绑定未评估。"
            )
            findings.append({
                "finding_id": "FINDING-DEPENDENCY-AUDIT-STATE-CONFLICT",
                "finding_type": "DEPENDENCY_AUDIT_STATE_CONFLICT",
                "project_id": "DBA_COCKPIT",
                "severity": "ATTENTION",
                "category": "SECURITY_DRIFT",
                "title": "Retained and live dependency audit states conflict",
                "title_zh": "保留记录与实时依赖审计状态冲突",
                "human_explanation": explanation,
                "source_reference": source_ref,
                "observed_at": as_of,
                "canonical_high_count": canonical_count,
                "live_candidate_high_count": live_count,
                "live_high_packages": packages,
                "runtime_binding": "NOT_ESTABLISHED",
                "exploitability": "NOT_ASSESSED",
                "reconciliation_required": True,
                "authorization": "NONE",
                "version_change_recommended": False,
            })
        dba_observation = context.get("source_observations", {}).get("DBA_COCKPIT", {})
        redyan_observation = context.get("source_observations", {}).get("RED_YAN_OFFICIAL_DOCUMENT", {})
        redyan_source_status = redyan_observation.get("status", "NOT_ASSESSED_SOURCE_UNAVAILABLE")
        redyan_payload = redyan_observation.get("payload", {})
        redyan_reason = redyan_payload.get(
            "reason_code", redyan_payload.get("reason", redyan_source_status)
        )
        redyan_reference = redyan_observation.get(
            "source_reference", "credential-gated-private-repository"
        )
        redyan_evidence = [
            redyan_reference,
            f"observed_at:{redyan_observation.get('observed_at', as_of)}",
        ]
        redyan_head = (
            redyan_payload.get("revision")
            or redyan_payload.get("head_sha")
            or redyan_payload.get("default_branch_sha")
        )
        if redyan_head:
            redyan_evidence.append(f"head:{redyan_head}")
        if redyan_source_status == "AVAILABLE":
            redyan_update = {
                "project_id": "RED_YAN_OFFICIAL_DOCUMENT",
                "status": "OBSERVED",
                "status_zh": "已实时观察仓库状态",
                "source_label": "LIVE",
                "source_observation_status": "AVAILABLE",
                "why_zh": (
                    "已读取红岩仓库的限定只读元数据；该观察不构成红岩运行时验收、"
                    "产品验收或生产就绪结论。"
                ),
                "attention_zh": "红岩运行时真相仍由红岩产品线和其权威运行证据负责。",
                "technical_evidence": redyan_evidence,
            }
        elif redyan_source_status == "NOT_ASSESSED_CREDENTIAL_UNAVAILABLE":
            redyan_update = {
                "project_id": "RED_YAN_OFFICIAL_DOCUMENT",
                "status": "NOT_ASSESSED",
                "status_zh": "跨仓库凭据不可用，未评估",
                "source_label": "NOT_ASSESSED",
                "source_observation_status": redyan_source_status,
                "reason_code": "CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
                "why_zh": "跨仓库只读凭据不可用，未读取红岩仓库状态。",
                "attention_zh": "未评估不等于正常；保留快照不替代实时观察。",
                "technical_evidence": redyan_evidence,
            }
        else:
            redyan_status_zh = {
                "SOURCE_STALE": "来源过期，未评估",
                "SOURCE_DRIFT": "来源发生漂移，未评估",
            }.get(redyan_reason, "来源不可用，未评估")
            redyan_update = {
                "project_id": "RED_YAN_OFFICIAL_DOCUMENT",
                "status": "NOT_ASSESSED",
                "status_zh": redyan_status_zh,
                "source_label": "STALE" if redyan_reason in {"SOURCE_STALE", "SOURCE_DRIFT"} else "NOT_ASSESSED",
                "source_observation_status": redyan_source_status,
                "reason_code": redyan_reason,
                "why_zh": f"红岩仓库只读来源未能完成观察；原因：{redyan_reason}。",
                "attention_zh": "未评估不等于正常；不得以保留快照替代实时观察。",
                "technical_evidence": redyan_evidence,
            }
        dba_status = "ATTENTION" if conflict else "OBSERVED" if audit_available else "NOT_ASSESSED"
        project_updates = [
            {
                "project_id": "DBA_COCKPIT",
                "status": dba_status,
                "status_zh": "依赖审计状态待复核" if conflict else "已实时观察" if audit_available else "审计未评估",
                "source_label": "LIVE" if dba_observation.get("status") == "AVAILABLE" else "NOT_ASSESSED",
                "why_zh": (
                    findings[0]["human_explanation"] if findings else
                    "当前仓库与依赖审计已完成只读观察；未形成保留计数冲突。" if audit_available else
                    "依赖审计未产生可解析结果。"
                ),
                "attention_zh": "可利用性和远端运行绑定仍未评估。",
                "technical_evidence": [source_ref, dba_observation.get("source_reference", "UNKNOWN")],
            },
            redyan_update,
        ]
        blind_spots = [{
            "blind_spot_id": "DEPENDENCY_RUNTIME_BINDING_UNKNOWN",
            "project_id": "DBA_COCKPIT",
            "title_zh": "依赖漏洞的远端运行绑定未观察",
            "impact_zh": "本轮只比较审计计数，不能确认依赖是否进入实际远端运行路径。",
            "status": "NOT_ASSESSED",
            "source_reference": source_ref,
        }]
        return make_result(
            self.cell_id,
            "ATTENTION" if conflict else "PASS" if audit_available else "NOT_ASSESSED",
            "Live dependency state was compared with the retained count without reconciliation.",
            findings=findings,
            outputs={
                "project_updates": project_updates,
                "blind_spots": blind_spots,
                "dependency_audit_state": {
                    "status": "CONFLICT_REQUIRES_REVIEW" if conflict else "MATCHES_RETAINED_COUNT" if audit_available else "NOT_ASSESSED",
                    "canonical_high_count": canonical_count,
                    "live_candidate_high_count": live_count if audit_available else None,
                    "live_high_packages": packages,
                    "runtime_binding": "NOT_ESTABLISHED",
                    "exploitability": "NOT_ASSESSED",
                    "auto_reconciliation": False,
                    "git_status_unchanged": live.get("git_status_unchanged"),
                },
            },
        )
