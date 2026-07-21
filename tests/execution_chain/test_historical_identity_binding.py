#!/usr/bin/env python3
"""Tests for phase-aware historical identity evidence validation."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validation.execution_chain_validator import validate_subject_identity_evidence


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class HistoricalIdentityBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.evidence_root = self.root / "evidence" / "experiments" / "DBOS-EXP-0001"
        self.evidence_root.mkdir(parents=True)
        self.historical_bytes = b"historical identity bytes\n"
        self.identity = {
            "evidence": [
                {
                    "path": "README.md",
                    "sha256": sha256_bytes(self.historical_bytes),
                    "size": len(self.historical_bytes),
                }
            ]
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def retain_historical_binding(self) -> None:
        manifest_directory = self.evidence_root / "run-0001"
        manifest_directory.mkdir()
        manifest = {
            "artifacts": [
                {
                    "path": "README.md",
                    "digest": f"sha256:{sha256_bytes(self.historical_bytes)}",
                    "size": len(self.historical_bytes),
                }
            ]
        }
        (manifest_directory / "auxiliary-input-manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )

    def validate(self, phase: str) -> tuple[int, list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        drift_count = validate_subject_identity_evidence(
            self.root,
            self.evidence_root,
            self.identity,
            phase,
            errors,
            warnings,
        )
        return drift_count, errors, warnings

    def test_completed_phase_accepts_retained_binding_and_reports_current_drift(self) -> None:
        (self.root / "README.md").write_bytes(b"later documentation version\n")
        self.retain_historical_binding()

        drift_count, errors, warnings = self.validate("completed")

        self.assertEqual(errors, [])
        self.assertEqual(drift_count, 1)
        self.assertEqual(len(warnings), 1)
        self.assertIn("historical digest was not rewritten", warnings[0])

    def test_completed_phase_fails_without_retained_historical_binding(self) -> None:
        (self.root / "README.md").write_bytes(b"later documentation version\n")

        drift_count, errors, warnings = self.validate("completed")

        self.assertEqual(drift_count, 1)
        self.assertEqual(len(warnings), 1)
        self.assertTrue(any("no retained manifest binding" in error for error in errors))

    def test_pre_completion_phase_requires_current_exact_bytes(self) -> None:
        (self.root / "README.md").write_bytes(b"later documentation version\n")
        self.retain_historical_binding()

        drift_count, errors, warnings = self.validate("environment")

        self.assertEqual(drift_count, 0)
        self.assertEqual(warnings, [])
        self.assertTrue(any("size mismatch" in error for error in errors))
        self.assertTrue(any("digest mismatch" in error for error in errors))

    def test_exact_current_bytes_need_no_historical_fallback(self) -> None:
        (self.root / "README.md").write_bytes(self.historical_bytes)

        drift_count, errors, warnings = self.validate("completed")

        self.assertEqual((drift_count, errors, warnings), (0, [], []))


if __name__ == "__main__":
    unittest.main()
