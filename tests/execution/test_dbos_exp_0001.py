"""Tests for the deterministic execution runner DBOS-EXP-0001."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from execution.dbos_exp_0001 import (
    ALLOWED_SNAPSHOT_ROOTS,
    capture_snapshot,
    check_authorization,
    collect_environment,
    run_experiment,
    run_validators,
)


class TestDbosExp0001(unittest.TestCase):
    def setUp(self) -> None:
        self.root_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.root_dir.name)

        # Create directories for allowed snapshot roots
        for dirname in ALLOWED_SNAPSHOT_ROOTS:
            (self.root / dirname).mkdir(parents=True)

        self.validator_file = self.root / "validation" / "dummy_validator.py"
        self.validator_file.write_text("print('{}')", encoding="utf-8")
        self.validator_file.chmod(0o755)

        self.output_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.output_dir.name)

    def tearDown(self) -> None:
        self.root_dir.cleanup()
        self.output_dir.cleanup()

    def test_collect_environment(self) -> None:
        result = collect_environment(self.root, self.output_path)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue((self.output_path / "environment-observation.json").exists())
        self.assertTrue((self.output_path / "environment-observation.receipt.json").exists())

        observation = json.loads((self.output_path / "environment-observation.json").read_text(encoding="utf-8"))
        self.assertEqual(observation["experiment_id"], "DBOS-EXP-0001")
        self.assertEqual(len(observation["facts"]), 5)  # os, python, dependency, configuration, hardware

    def test_capture_snapshot(self) -> None:
        capture_snapshot(self.root, self.output_path)

        self.assertTrue((self.output_path / "snapshot-manifest.json").exists())
        self.assertTrue((self.output_path / "validator-manifest.json").exists())
        self.assertTrue((self.output_path / "dbos-input-snapshot.tar").exists())

        manifest = json.loads((self.output_path / "snapshot-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file_count"], 1)
        self.assertEqual(manifest["files"][0]["path"], "validation/dummy_validator.py")

        validator_manifest = json.loads((self.output_path / "validator-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(validator_manifest["validator_count"], 1)
        self.assertEqual(validator_manifest["validators"][0]["path"], "validation/dummy_validator.py")

    def test_capture_snapshot_empty_fails(self) -> None:
        self.validator_file.unlink()
        with self.assertRaisesRegex(ValueError, "snapshot file set is empty"):
            capture_snapshot(self.root, self.output_path)

    def test_capture_snapshot_missing_directory_fails(self) -> None:
        (self.root / "constitution").rmdir()
        with self.assertRaisesRegex(ValueError, "required snapshot directory missing: constitution"):
            capture_snapshot(self.root, self.output_path)

    def test_check_authorization(self) -> None:
        auth = {
            "experiment_id": "DBOS-EXP-0001",
            "experiment_authorization_id": "DBOS-EXP-0001-AUTH-0001",
            "executor_authorization_id": "DBOS-EXP-0001-EXECUTOR-AUTH-0001",
            "runner_id": "dbio:runner:automated:dbos-self-validation:v0.1",
            "status": "authorized",
            "agent_creation": False,
            "runtime_creation": False,
            "digital_organism_creation": False,
            "capability_upgrade": False,
            "permission_grant": False,
            "authorized_by": "someone",
            "authorization_evidence": [{"foo": "bar"}],
        }

        auth_file = self.root / "auth.json"
        auth_file.write_text(json.dumps(auth), encoding="utf-8")

        result = check_authorization(auth_file)
        self.assertEqual(result["experiment_id"], "DBOS-EXP-0001")

    def test_check_authorization_fails_invalid_experiment_id(self) -> None:
        auth = {
            "experiment_id": "INVALID",
            "experiment_authorization_id": "DBOS-EXP-0001-AUTH-0001",
            "executor_authorization_id": "DBOS-EXP-0001-EXECUTOR-AUTH-0001",
            "runner_id": "dbio:runner:automated:dbos-self-validation:v0.1",
            "status": "authorized",
            "agent_creation": False,
            "runtime_creation": False,
            "digital_organism_creation": False,
            "capability_upgrade": False,
            "permission_grant": False,
            "authorized_by": "someone",
            "authorization_evidence": [{"foo": "bar"}],
        }
        auth_file = self.root / "auth.json"
        auth_file.write_text(json.dumps(auth), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "authorization experiment_id must be 'DBOS-EXP-0001'"):
            check_authorization(auth_file)

    def test_run_validators(self) -> None:
        extracted_dir = tempfile.TemporaryDirectory()
        extracted_root = Path(extracted_dir.name)

        validator_path = extracted_root / "validation/dummy_validator.py"
        validator_path.parent.mkdir(parents=True)
        validator_path.write_text("import sys\nprint('{}')\nsys.exit(0)", encoding="utf-8")

        validator_manifest = {"execution_order": ["validation/dummy_validator.py"]}

        results = run_validators(extracted_root, validator_manifest)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "PASS")
        self.assertEqual(results[0]["returncode"], 0)

        extracted_dir.cleanup()

    def test_run_validators_fails_on_nonzero_exit(self) -> None:
        extracted_dir = tempfile.TemporaryDirectory()
        extracted_root = Path(extracted_dir.name)

        validator_path = extracted_root / "validation/failing_validator.py"
        validator_path.parent.mkdir(parents=True)
        validator_path.write_text("import sys\nsys.exit(1)", encoding="utf-8")

        validator_manifest = {"execution_order": ["validation/failing_validator.py"]}

        results = run_validators(extracted_root, validator_manifest)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "FAIL")
        self.assertEqual(results[0]["returncode"], 1)

        extracted_dir.cleanup()

    def test_run_experiment_success(self) -> None:
        auth = {
            "experiment_id": "DBOS-EXP-0001",
            "experiment_authorization_id": "DBOS-EXP-0001-AUTH-0001",
            "executor_authorization_id": "DBOS-EXP-0001-EXECUTOR-AUTH-0001",
            "runner_id": "dbio:runner:automated:dbos-self-validation:v0.1",
            "status": "authorized",
            "agent_creation": False,
            "runtime_creation": False,
            "digital_organism_creation": False,
            "capability_upgrade": False,
            "permission_grant": False,
            "authorized_by": "someone",
            "authorization_evidence": [{"foo": "bar"}],
        }
        auth_file = self.root / "auth.json"
        auth_file.write_text(json.dumps(auth), encoding="utf-8")

        snapshot_dir_obj = tempfile.TemporaryDirectory()
        snapshot_dir = Path(snapshot_dir_obj.name)
        capture_snapshot(self.root, snapshot_dir)

        self.validator_file.write_text("import sys\nsys.exit(0)", encoding="utf-8")

        capture_snapshot(self.root, snapshot_dir)

        result = run_experiment(self.root, snapshot_dir, auth_file, self.output_path)

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["failure_count"], 0)
        self.assertTrue((self.output_path / "experiment-result.json").exists())
        self.assertTrue((self.output_path / "evidence-bundle.json").exists())

        snapshot_dir_obj.cleanup()

    def test_run_experiment_validator_failure(self) -> None:
        auth = {
            "experiment_id": "DBOS-EXP-0001",
            "experiment_authorization_id": "DBOS-EXP-0001-AUTH-0001",
            "executor_authorization_id": "DBOS-EXP-0001-EXECUTOR-AUTH-0001",
            "runner_id": "dbio:runner:automated:dbos-self-validation:v0.1",
            "status": "authorized",
            "agent_creation": False,
            "runtime_creation": False,
            "digital_organism_creation": False,
            "capability_upgrade": False,
            "permission_grant": False,
            "authorized_by": "someone",
            "authorization_evidence": [{"foo": "bar"}],
        }
        auth_file = self.root / "auth.json"
        auth_file.write_text(json.dumps(auth), encoding="utf-8")

        self.validator_file.write_text("import sys\nsys.exit(1)", encoding="utf-8")

        snapshot_dir_obj = tempfile.TemporaryDirectory()
        snapshot_dir = Path(snapshot_dir_obj.name)
        capture_snapshot(self.root, snapshot_dir)

        with self.assertRaisesRegex(RuntimeError, "frozen validator suite did not pass completely"):
            run_experiment(self.root, snapshot_dir, auth_file, self.output_path)

        result = json.loads((self.output_path / "experiment-result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["stop_reason"], "validator_failure_or_incomplete_suite")

        snapshot_dir_obj.cleanup()

if __name__ == "__main__":
    unittest.main()
