"""Zero-side-effect and documentation-alignment tests for the demo."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

from examples.mcp_reference_demo import run_reference_demo
from examples.mcp_reference_demo.synthetic_agent import (
    declare_synthetic_tool_call,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = REPOSITORY_ROOT / "examples/mcp_reference_demo"
GOVERNED_STATE_DIRECTORIES = ("constitution", "registry", "evolution", "evidence")


def _governed_state_digest() -> str:
    digest = hashlib.sha256()
    for directory in GOVERNED_STATE_DIRECTORIES:
        root = REPOSITORY_ROOT / directory
        for item in sorted(path for path in root.rglob("*") if path.is_file()):
            digest.update(item.relative_to(REPOSITORY_ROOT).as_posix().encode("utf-8"))
            digest.update(item.read_bytes())
    return digest.hexdigest()


class DemoNoSideEffectTests(unittest.TestCase):
    def test_demo_does_not_modify_governed_state(self) -> None:
        before = _governed_state_digest()
        result = run_reference_demo()
        after = _governed_state_digest()

        self.assertTrue(result["demo_contract_satisfied"])
        self.assertEqual(after, before)

    def test_demo_reports_all_governance_effects_false(self) -> None:
        non_effects = run_reference_demo()["non_effects"]

        self.assertTrue(non_effects)
        self.assertTrue(all(value is False for value in non_effects.values()))

    def test_synthetic_agent_module_creates_no_agent_identity(self) -> None:
        declaration = declare_synthetic_tool_call()

        self.assertIsInstance(declaration, dict)
        for prohibited in ("agent", "agent_id", "runtime", "permission"):
            self.assertNotIn(prohibited, declaration)

        source = (DEMO_ROOT / "synthetic_agent.py").read_text(encoding="utf-8")
        self.assertNotIn("class Agent", source)
        self.assertNotIn("Agent(", source)

    def test_demo_source_has_no_network_or_file_write_operation(self) -> None:
        source = "\n".join(
            item.read_text(encoding="utf-8")
            for item in sorted(DEMO_ROOT.glob("*.py"))
        )
        for operation in (
            "import requests",
            "import socket",
            "subprocess.run(",
            ".write_text(",
            ".write_bytes(",
            "open(",
        ):
            with self.subTest(operation=operation):
                self.assertNotIn(operation, source)

    def test_candidate_contains_no_governance_or_evidence_fields(self) -> None:
        candidate = run_reference_demo()["mapping_result"]["candidate"]

        for field in (
            "agent",
            "runtime",
            "permission",
            "capability",
            "evidence",
            "execution_result",
        ):
            self.assertNotIn(field, candidate)

    def test_readme_and_report_preserve_demo_boundaries(self) -> None:
        readme = (DEMO_ROOT / "README.md").read_text(encoding="utf-8")
        report = (DEMO_ROOT / "demo_report.md").read_text(encoding="utf-8")

        for statement in (
            "DEMO_NE_PRODUCTION=true",
            "SYNTHETIC_NE_REAL=true",
            "VALIDATION_NE_TRUTH=true",
            "REAL_MCP_CONNECTED=false",
        ):
            self.assertIn(statement, readme)
        for observation in (
            "mapping_status=MAPPED",
            "result=UNKNOWN",
            "REJECTED/FAIL",
            "VERSION_MISMATCH",
            "PRODUCTION_READY=false",
        ):
            self.assertIn(observation, report)


if __name__ == "__main__":
    unittest.main()
