"""Run the deterministic DBOS MCP reference demo and print one JSON report.

The demo performs in-memory translation and local validation only. It never
connects to MCP, invokes a tool, creates an Agent or Runtime, grants permission,
or writes an Execution Fact or Canonical Evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from adapters.mcp import MappingStatus, adapt_tool_call  # noqa: E402
from examples.mcp_reference_demo.synthetic_mcp_event import (  # noqa: E402
    build_synthetic_mcp_tool_call_event,
)


DEMO_ID = "DBOS-MCP-REFERENCE-DEMO-V0.1"

DEMO_LIMITATIONS = (
    "Local synthetic teaching demo only.",
    "No real Agent, MCP server, client, transport, tool call, or data access exists.",
    "The in-memory Execution candidate is not a canonical object or execution fact.",
    "Validation checks local structure and governance constraints, not truth.",
    "No permission, capability grant, canonical evidence, or production readiness is created.",
)

DEMO_NON_EFFECTS = {
    "agent_created": False,
    "runtime_created": False,
    "permission_created": False,
    "capability_granted": False,
    "tool_invoked": False,
    "execution_fact_created": False,
    "canonical_evidence_created": False,
    "mcp_server_created": False,
    "real_mcp_connected": False,
    "production_ready": False,
}


def _negative_case(
    case_id: str,
    input_delta: dict[str, Any],
    *,
    expected_mapping_status: str,
    expected_validation_result: str,
) -> dict[str, Any]:
    fixture = build_synthetic_mcp_tool_call_event()
    fixture.update(input_delta)
    observed = adapt_tool_call(fixture).to_dict()
    return {
        "case_id": case_id,
        "input_delta": input_delta,
        "expected_mapping_status": expected_mapping_status,
        "expected_validation_result": expected_validation_result,
        "observed_mapping_status": observed["mapping_status"],
        "observed_validation_result": observed["validation_result"]["result"],
        "adapter_errors": observed["adapter_errors"],
        "candidate_created": observed["candidate"] is not None,
        "expectation_met": (
            observed["mapping_status"] == expected_mapping_status
            and observed["validation_result"]["result"]
            == expected_validation_result
            and observed["candidate"] is None
        ),
    }


def run_reference_demo() -> dict[str, Any]:
    """Return the complete deterministic story without persisting any output."""

    synthetic_input = build_synthetic_mcp_tool_call_event()
    positive = adapt_tool_call(synthetic_input).to_dict()
    negative_cases = [
        _negative_case(
            "TOOL_TO_CAPABILITY_REJECTED",
            {"capability": "synthetic-capability-claim"},
            expected_mapping_status="REJECTED",
            expected_validation_result="FAIL",
        ),
        _negative_case(
            "TOOL_PERMISSION_TO_DBOS_PERMISSION_REJECTED",
            {"tool_permission": "ALLOW"},
            expected_mapping_status="REJECTED",
            expected_validation_result="FAIL",
        ),
        _negative_case(
            "UNKNOWN_VERSION_REJECTED",
            {"protocol_revision": "UNKNOWN_MCP_REVISION"},
            expected_mapping_status="VERSION_MISMATCH",
            expected_validation_result="VERSION_MISMATCH",
        ),
    ]
    success_path_met = (
        positive["mapping_status"] == MappingStatus.MAPPED.value
        and positive["candidate"] is not None
        and positive["candidate"]["object_type"] == "EXECUTION"
        and positive["candidate"]["status"] == "UNKNOWN"
        and positive["candidate"]["output_reference"] is None
        and positive["validator_invoked"] is True
        and positive["validation_result"]["result"] == "UNKNOWN"
    )
    return {
        "demo_id": DEMO_ID,
        "demo_status": "LOCAL_SYNTHETIC_REFERENCE_DEMO",
        "input": synthetic_input,
        "mapping_result": {
            "mapping_status": positive["mapping_status"],
            "execution_candidate_id": positive["execution_candidate_id"],
            "candidate": positive["candidate"],
            "validator_invoked": positive["validator_invoked"],
            "adapter_errors": positive["adapter_errors"],
        },
        "validation_result": positive["validation_result"],
        "negative_cases": negative_cases,
        "demo_contract_satisfied": (
            success_path_met
            and all(case["expectation_met"] for case in negative_cases)
        ),
        "limitations": list(DEMO_LIMITATIONS),
        "non_effects": dict(DEMO_NON_EFFECTS),
    }


def main() -> int:
    result = run_reference_demo()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["demo_contract_satisfied"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
