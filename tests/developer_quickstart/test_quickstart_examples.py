"""Executable and zero-governance-effect tests for the developer quick start."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CREATE_SCRIPT = REPOSITORY_ROOT / "examples/basic_object/create_entity_object.py"
VALIDATE_SCRIPT = REPOSITORY_ROOT / "examples/basic_object/validate_object.py"
NEGATIVE_SCRIPT = (
    REPOSITORY_ROOT
    / "examples/basic_object/negative/validate_negative_cases.py"
)
GOVERNED_STATE_DIRECTORIES = ("constitution", "registry", "evolution", "evidence")


def _run(script: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def _governed_state_digest() -> str:
    digest = hashlib.sha256()
    for directory in GOVERNED_STATE_DIRECTORIES:
        root = REPOSITORY_ROOT / directory
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            digest.update(path.relative_to(REPOSITORY_ROOT).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


class DeveloperQuickStartTests(unittest.TestCase):
    def test_create_example_prints_synthetic_entity_object(self) -> None:
        completed = _run(CREATE_SCRIPT)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        target = json.loads(completed.stdout)
        self.assertEqual(target["object_type"], "ENTITY")
        self.assertEqual(target["entity_type"], "repository")
        self.assertEqual(target["lifecycle_state"], "PROPOSED")
        self.assertNotIn("permission", target)
        self.assertTrue(any("No real entity" in item for item in target["limitations"]))

    def test_validate_example_prints_only_nine_field_result(self) -> None:
        completed = _run(VALIDATE_SCRIPT)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(
            set(result),
            {
                "validation_id",
                "validator_version",
                "target_reference",
                "schema_reference",
                "result",
                "errors",
                "warnings",
                "limitations",
                "timestamp",
            },
        )
        self.assertIsNone(result["validation_id"])
        self.assertIsNone(result["timestamp"])

    def test_negative_examples_are_rejected_as_documented(self) -> None:
        completed = _run(NEGATIVE_SCRIPT)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        records = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(
            {
                record["case"]: record["validation_result"]["result"]
                for record in records
            },
            {
                "capability_with_permission": "FAIL",
                "unknown_field": "FAIL",
                "version_mismatch": "VERSION_MISMATCH",
            },
        )

    def test_examples_do_not_modify_governed_state(self) -> None:
        before = _governed_state_digest()
        for script in (CREATE_SCRIPT, VALIDATE_SCRIPT, NEGATIVE_SCRIPT):
            completed = _run(script)
            self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(_governed_state_digest(), before)

    def test_examples_define_no_agent_runtime_or_api_server(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (CREATE_SCRIPT, VALIDATE_SCRIPT, NEGATIVE_SCRIPT)
        )
        for declaration in ("class Agent", "class Runtime", "class APIServer"):
            self.assertNotIn(declaration, source)

    def test_examples_have_no_network_or_file_write_operation(self) -> None:
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (CREATE_SCRIPT, VALIDATE_SCRIPT, NEGATIVE_SCRIPT)
        )
        for operation in (
            "import requests",
            "import socket",
            ".write_text(",
            ".write_bytes(",
            "open(",
        ):
            self.assertNotIn(operation, source)

    def test_quickstart_documents_all_runnable_commands(self) -> None:
        quickstart = (
            REPOSITORY_ROOT / "docs/developer-quickstart.md"
        ).read_text(encoding="utf-8")
        for script in (CREATE_SCRIPT, VALIDATE_SCRIPT, NEGATIVE_SCRIPT):
            command = f"python3 {script.relative_to(REPOSITORY_ROOT).as_posix()}"
            self.assertIn(command, quickstart)

    def test_quickstart_preserves_infrastructure_boundaries(self) -> None:
        quickstart = (
            REPOSITORY_ROOT / "docs/developer-quickstart.md"
        ).read_text(encoding="utf-8")
        for statement in (
            "PASS_NE_AUTHORIZATION=true",
            "VALIDATION_NE_PERMISSION=true",
            "VALIDATION_NE_EXECUTION=true",
            "不是已发布的软件包",
        ):
            self.assertIn(statement, quickstart)


if __name__ == "__main__":
    unittest.main()
