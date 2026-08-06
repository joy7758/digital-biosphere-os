#!/usr/bin/env python3
"""Tests for the fail-closed repository test runner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.run_tests import discover_test_directories, run, run_test_directory


class RunTestsToolingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.test_directory = Path(self.temporary_directory.name)
        self.root = Path(__file__).resolve().parents[2]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_one_passing_test_is_counted(self) -> None:
        (self.test_directory / "test_sample.py").write_text(
            "import unittest\n\n"
            "class SampleTest(unittest.TestCase):\n"
            "    def test_passes(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )

        result = run_test_directory(self.root, self.test_directory, verbose=False)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["test_count"], 1)

    def test_empty_discovery_fails_closed(self) -> None:
        result = run_test_directory(self.root, self.test_directory, verbose=False)

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["test_count"], 0)
        self.assertIn("NO_TESTS_DISCOVERED", result["errors"])

    def test_failing_test_preserves_nonzero_result(self) -> None:
        (self.test_directory / "test_sample.py").write_text(
            "import unittest\n\n"
            "class SampleTest(unittest.TestCase):\n"
            "    def test_fails(self):\n"
            "        self.fail('expected failure')\n",
            encoding="utf-8",
        )

        result = run_test_directory(self.root, self.test_directory, verbose=False)

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["test_count"], 1)
        self.assertIn("UNITTEST_EXIT_1", result["errors"])

    def test_discover_test_directories_no_tests_dir(self) -> None:
        directories = discover_test_directories(self.test_directory)
        self.assertEqual(directories, [])

    def test_discover_test_directories_ignores_empty(self) -> None:
        tests_dir = self.test_directory / "tests"
        tests_dir.mkdir()
        empty_subdir = tests_dir / "empty"
        empty_subdir.mkdir()

        directories = discover_test_directories(self.test_directory)
        self.assertEqual(directories, [])

    def test_discover_test_directories_finds_tests(self) -> None:
        tests_dir = self.test_directory / "tests"
        tests_dir.mkdir()
        valid_subdir = tests_dir / "valid"
        valid_subdir.mkdir()
        (valid_subdir / "test_something.py").write_text("", encoding="utf-8")

        directories = discover_test_directories(self.test_directory)
        self.assertEqual(directories, [valid_subdir])

    def test_run_empty_directories(self) -> None:
        result = run(self.root, [], verbose=False)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["test_directory_count"], 0)
        self.assertEqual(result["test_count"], 0)
        self.assertIn("NO_TEST_DIRECTORIES", result["errors"])
        self.assertIn("NO_TESTS_DISCOVERED", result["errors"])

    def test_run_discovery_failure(self) -> None:
        result = run(self.root, [self.test_directory], verbose=False)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["test_directory_count"], 1)
        self.assertEqual(result["test_count"], 0)
        self.assertIn("ONE_OR_MORE_TEST_DIRECTORIES_FAILED", result["errors"])
        self.assertIn("NO_TESTS_DISCOVERED", result["errors"])


if __name__ == "__main__":
    unittest.main()
