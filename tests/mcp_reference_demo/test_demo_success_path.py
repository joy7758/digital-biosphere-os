"""End-to-end success-path tests for the synthetic MCP reference demo."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from examples.mcp_reference_demo import run_reference_demo
from examples.mcp_reference_demo.synthetic_mcp_event import (
    build_synthetic_mcp_tool_call_event,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = REPOSITORY_ROOT / "examples/mcp_reference_demo/run_demo.py"


class DemoSuccessPathTests(unittest.TestCase):
    def test_demo_contract_is_satisfied(self) -> None:
        result = run_reference_demo()

        self.assertTrue(result["demo_contract_satisfied"])
        self.assertEqual(result["demo_status"], "LOCAL_SYNTHETIC_REFERENCE_DEMO")

    def test_synthetic_input_contains_exact_adapter_contract(self) -> None:
        fixture = build_synthetic_mcp_tool_call_event()

        self.assertEqual(
            set(fixture),
            {
                "tool_call_id",
                "tool_name",
                "arguments_reference",
                "context_reference",
                "source_reference",
                "entity_reference",
                "protocol_revision",
                "mapping_profile_version",
            },
        )
        self.assertEqual(
            fixture["protocol_revision"],
            "DBOS_MCP_SYNTHETIC_TOOL_CALL_V0_1",
        )

    def test_mapping_produces_only_unknown_execution_candidate(self) -> None:
        result = run_reference_demo()
        mapping = result["mapping_result"]
        candidate = mapping["candidate"]

        self.assertEqual(mapping["mapping_status"], "MAPPED")
        self.assertTrue(mapping["validator_invoked"])
        self.assertEqual(candidate["object_type"], "EXECUTION")
        self.assertEqual(candidate["status"], "UNKNOWN")
        self.assertIsNone(candidate["output_reference"])
        self.assertTrue(mapping["execution_candidate_id"].startswith("extension:"))

    def test_validation_result_preserves_unknown(self) -> None:
        validation = run_reference_demo()["validation_result"]

        self.assertEqual(validation["result"], "UNKNOWN")
        self.assertEqual(validation["validator_version"], "v0.1")
        self.assertTrue(
            any(
                issue["error_code"] == "UNKNOWN"
                and issue["field_reference"] == "$.status"
                for issue in validation["errors"]
            )
        )

    def test_cli_prints_deterministic_json_and_exits_zero(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        first = subprocess.run(
            [sys.executable, str(DEMO_SCRIPT)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        second = subprocess.run(
            [sys.executable, str(DEMO_SCRIPT)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertTrue(json.loads(first.stdout)["demo_contract_satisfied"])


if __name__ == "__main__":
    unittest.main()
