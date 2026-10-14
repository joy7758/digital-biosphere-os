"""Create bounded human decisions from findings and blind spots."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result


class HandoffCell(WeeklyCell):
    cell_id = "HANDOFF_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            entries = context.get("capability_reference_registry", {}).get(
                "entries", []
            )
            decisions, packets = [], []
            for item in entries:
                needs_identity = (
                    item.get("identity_status") == "IDENTITY_REVIEW_REQUIRED"
                )
                review_eligible = (
                    item.get("ac2_readiness_status") == "REVIEW_ELIGIBLE"
                    and item.get("current_problem_match")
                )
                if not (needs_identity or review_eligible):
                    continue
                reason = (
                    "来源身份需要人工核对"
                    if needs_identity
                    else "候选与当前问题匹配，可评审是否进入AC-2"
                )
                decisions.append({
                    "decision_id": f"DECISION-CAPABILITY-{item['candidate_id']}",
                    "source_cell_id": self.cell_id,
                    "project_id": "DBA_COCKPIT",
                    "title_zh": f"是否评审 {item['name']} 的下一阶段边界",
                    "why_zh": reason,
                    "priority": "MEDIUM",
                    "evidence_references": [item["candidate_id"]],
                    "authority": "HUMAN_DECISION_REQUIRED",
                })
                packets.append({
                    "handoff_id": f"HANDOFF-CAPABILITY-{item['candidate_id']}",
                    "project_id": "DBA_COCKPIT",
                    "recipient_role": "DBA专用对话",
                    "decision_needed": reason,
                    "evidence_references": [item["candidate_id"]],
                    "suggested_next_review": "只评审是否进入AC-2；本包不含执行命令。",
                    "execution_commands": [],
                    "authority": "NONE",
                    "auto_action": False,
                })
            return make_result(
                self.cell_id,
                "PASS" if not decisions else "PASS_WITH_CANDIDATES",
                "Only identity conflicts or evidence-backed AC-2 review candidates created handoffs.",
                handoffs=packets,
                outputs={
                    "decisions": decisions,
                    "handoff_packets": packets,
                    "preset_queries": {
                        "本周外部能力发现了什么？": "查看外部能力发现摘要、更新与冲突。",
                        "是否采用了外部代码？": "没有。代码采用数量固定为0。",
                        "是否需要人工决定？": f"当前有{len(decisions)}项身份或AC-2边界事项。",
                    },
                },
            )
        findings = context.get("findings", [])
        blind_spots = context.get("blind_spots", [])
        decisions: list[dict[str, Any]] = []
        packets: list[dict[str, Any]] = []

        conflict = next(
            (item for item in findings if item.get("finding_type") == "DEPENDENCY_AUDIT_STATE_CONFLICT"),
            None,
        )
        if conflict:
            decision = {
                "decision_id": "DECISION-DEPENDENCY-SECURITY-REVIEW",
                "source_cell_id": self.cell_id,
                "project_id": conflict.get("project_id", "UNKNOWN"),
                "title_zh": "是否启动依赖安全专项复核",
                "why_zh": (
                    f"历史记录{conflict.get('canonical_high_count')}个，本周扫描"
                    f"{conflict.get('live_candidate_high_count')}个，当前存在状态冲突。"
                ),
                "priority": "HIGH",
                "evidence_references": [conflict.get("finding_id")],
                "authority": "HUMAN_DECISION_REQUIRED",
            }
            decisions.append(decision)
            packets.append(
                {
                    "handoff_id": "HANDOFF-DEPENDENCY-SECURITY-REVIEW",
                    "project_id": decision["project_id"],
                    "recipient_role": "HUMAN_REVIEWER",
                    "decision_needed": decision["title_zh"],
                    "evidence_references": decision["evidence_references"],
                    "suggested_next_review": "核对锁文件、扫描范围、运行绑定与权威状态来源。",
                    "execution_commands": [],
                    "authority": "NONE",
                }
            )

        scout = next(
            (item for item in blind_spots if item.get("blind_spot_id") == "SCOUT_STATUS_STALE"),
            None,
        )
        if scout:
            decision = {
                "decision_id": "DECISION-SCOUT-READ-ONLY-REFRESH",
                "source_cell_id": self.cell_id,
                "project_id": scout.get("project_id", "UNKNOWN"),
                "title_zh": "是否授权刷新 TITMAC Scout 的只读状态",
                "why_zh": "当前状态来源缺少足够新鲜度；刷新仍需单独、只读、限定范围的人工授权。",
                "priority": "MEDIUM",
                "evidence_references": [scout.get("blind_spot_id")],
                "authority": "HUMAN_DECISION_REQUIRED",
            }
            decisions.append(decision)
            packets.append(
                {
                    "handoff_id": "HANDOFF-SCOUT-READ-ONLY-REFRESH",
                    "project_id": decision["project_id"],
                    "recipient_role": "HUMAN_REVIEWER",
                    "decision_needed": decision["title_zh"],
                    "evidence_references": decision["evidence_references"],
                    "suggested_next_review": "如批准，仅刷新声明来源的只读状态，不扩大扫描范围。",
                    "execution_commands": [],
                    "authority": "NONE",
                }
            )

        if not packets:
            packets.append(
                {
                    "handoff_id": "HANDOFF-NO-ACTIONABLE-DECISION",
                    "project_id": "WEEKLY_COCKPIT",
                    "recipient_role": "HUMAN_REVIEWER",
                    "decision_needed": "确认本周没有形成可执行的人工决定",
                    "evidence_references": [],
                    "suggested_next_review": "继续保留只读观察与盲区。",
                    "execution_commands": [],
                    "authority": "NONE",
                }
            )

        preset_queries = {
            "本周需要决定什么？": f"当前有{len(decisions)}项待人工决定；具体内容来自交接 Cell。",
            "本周收集到多少信号？": f"共记录{len(context.get('discovery_records', []))}项发现信号，准入状态分别保留。",
            "哪些事项仍是盲区？": f"当前登记{len(blind_spots)}项盲区；未评估不等于正常。",
        }
        return make_result(
            self.cell_id,
            "PASS" if decisions else "NOT_ASSESSED",
            "Human decision items were generated from bounded findings and blind spots.",
            handoffs=packets,
            outputs={
                "decisions": decisions,
                "handoff_packets": packets,
                "preset_queries": preset_queries,
            },
        )
