"""Interpret only security observations admitted by Evidence Admission."""

from __future__ import annotations

from typing import Any

from . import WeeklyCell, make_result


class SecurityCell(WeeklyCell):
    cell_id = "SECURITY_CELL"

    def _run(self, context: dict[str, Any]):
        if context.get("snapshot_mode") == "AUTOMATIC_CAPABILITY_DISCOVERY":
            return make_result(
                self.cell_id,
                "PASS",
                "No external security claim was promoted beyond admitted source metadata.",
                outputs={
                    "security_observations": [],
                    "security_conclusion_created": False,
                },
            )
        admitted = list(context.get("admitted_observations", []))
        consumed = [
            item for item in admitted
            if item.get("kind") == "DEPENDENCY_SECURITY_CONFLICT_CANDIDATE"
        ]
        observations = [
            {
                "signal_id": item["signal_id"],
                "interpretation": "CURRENT_SECURITY_CANDIDATE_REQUIRES_RECONCILIATION",
                "runtime_binding": item.get("runtime_binding", "NOT_ESTABLISHED"),
                "exploitability": item.get("exploitability", "NOT_ASSESSED"),
                "authorization": "NONE",
            }
            for item in consumed
        ]
        return make_result(
            self.cell_id,
            "PASS_WITH_OBSERVATION" if observations else "NOT_ASSESSED",
            "Security interpretation consumed admitted observations only.",
            observations=observations,
            outputs={
                "security_observations": observations,
                "security_consumed_signal_ids": [item["signal_id"] for item in consumed],
            },
        )
