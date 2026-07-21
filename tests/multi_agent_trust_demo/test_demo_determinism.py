#!/usr/bin/env python3
"""Determinism and CLI tests for the trust demo."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from examples.multi_agent_trust_demo.demo import build_demo


class MultiAgentTrustDemoDeterminismTests(unittest.TestCase):
    def test_two_builds_are_identical(self) -> None:
        self.assertEqual(build_demo(), build_demo())

    def test_cli_prints_same_json_and_exits_zero(self) -> None:
        root = Path(__file__).resolve().parents[2]
        completed = subprocess.run(
            [sys.executable, "-m", "examples.multi_agent_trust_demo.run_demo"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout), build_demo())

    def test_demo_contains_no_generated_timestamp(self) -> None:
        serialized = json.dumps(build_demo(), sort_keys=True)
        self.assertNotIn("2026-", serialized)


if __name__ == "__main__":
    unittest.main()
