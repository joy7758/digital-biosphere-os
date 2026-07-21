#!/usr/bin/env python3
"""Run every DBOS unittest directory and fail closed when discovery is empty.

This is a developer test runner, not a DBOS Runtime or execution service. Each
test directory runs in a separate Python process so same-named test modules and
directory-local fixture helpers cannot collide in ``sys.modules``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

TEST_COUNT_PATTERN = re.compile(r"Ran (\d+) tests? in ")


def discover_test_directories(root: Path) -> list[Path]:
    """Return first-level test directories containing at least one test file."""
    tests_root = root / "tests"
    if not tests_root.is_dir():
        return []
    return [
        directory
        for directory in sorted(tests_root.iterdir())
        if directory.is_dir() and any(directory.rglob("test_*.py"))
    ]


def run_test_directory(root: Path, test_directory: Path, verbose: bool) -> dict[str, Any]:
    """Run one discovery boundary and return a machine-readable result."""
    resolved_directory = test_directory.resolve()
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    python_path_entries = [str(root.resolve()), str(resolved_directory)]
    existing_python_path = environment.get("PYTHONPATH")
    if existing_python_path:
        python_path_entries.append(existing_python_path)
    environment["PYTHONPATH"] = os.pathsep.join(python_path_entries)

    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(resolved_directory),
        "-p",
        "test_*.py",
    ]
    if verbose:
        command.append("-v")
    completed = subprocess.run(
        command,
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    combined_output = "\n".join(
        part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
    )
    match = TEST_COUNT_PATTERN.search(combined_output)
    test_count = int(match.group(1)) if match else 0
    errors: list[str] = []
    if test_count == 0:
        errors.append("NO_TESTS_DISCOVERED")
    if completed.returncode != 0:
        errors.append(f"UNITTEST_EXIT_{completed.returncode}")
    return {
        "test_directory": str(resolved_directory),
        "status": "PASS" if not errors else "FAIL",
        "test_count": test_count,
        "returncode": completed.returncode,
        "errors": errors,
        "output": combined_output if errors or verbose else None,
    }


def run(root: Path, test_directories: list[Path], verbose: bool = False) -> dict[str, Any]:
    """Run all requested directories without hiding later directory failures."""
    results = [run_test_directory(root, directory, verbose) for directory in test_directories]
    total_test_count = sum(result["test_count"] for result in results)
    errors: list[str] = []
    if not test_directories:
        errors.append("NO_TEST_DIRECTORIES")
    if total_test_count == 0:
        errors.append("NO_TESTS_DISCOVERED")
    if any(result["status"] != "PASS" for result in results):
        errors.append("ONE_OR_MORE_TEST_DIRECTORIES_FAILED")
    return {
        "status": "PASS" if not errors else "FAIL",
        "runner": "dbos_unittest_directory_runner",
        "test_directory_count": len(test_directories),
        "test_count": total_test_count,
        "agent_created": False,
        "runtime_created": False,
        "permission_granted": False,
        "governed_state_modified": False,
        "errors": errors,
        "results": results,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test-dir",
        action="append",
        type=Path,
        help="Test directory to run; repeat for more. Defaults to every tests/* directory.",
    )
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    directories = (
        [directory if directory.is_absolute() else root / directory for directory in args.test_dir]
        if args.test_dir
        else discover_test_directories(root)
    )
    result = run(root, directories, args.verbose)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for directory_result in result["results"]:
            print(
                f"TEST_DIRECTORY={directory_result['test_directory']} "
                f"STATUS={directory_result['status']} "
                f"TESTS={directory_result['test_count']}"
            )
            if directory_result["output"]:
                print(directory_result["output"])
        print(f"DBOS_TEST_RESULT={result['status']}")
        print(f"DBOS_TEST_DIRECTORY_COUNT={result['test_directory_count']}")
        print(f"DBOS_TEST_COUNT={result['test_count']}")
        for error in result["errors"]:
            print(f"ERROR={error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
