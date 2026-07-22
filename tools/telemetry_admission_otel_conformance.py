#!/usr/bin/env python3
"""Execute only authorized offline OTel case bindings and report zero effects.

The report is a DBOS-local execution receipt, not either DBA full-catalog
result-set schema.  A 32/32 or 36/36 subset PASS remains ``full_catalog_result
= BLOCKED`` because DQ-020/PR-G3 deployment cases are not authorized.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dbos.telemetry_admission.references import (  # noqa: E402
    SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
    SEMANTIC_RESULT_SCHEMA_FILENAME,
    read_pinned_json,
)


SEMANTIC_BINDING = (
    ROOT / "tests" / "telemetry_admission" / "semantic_pr_g2_bindings.v0.1.json"
)
SCHEMA_RESOURCE_BINDING = (
    ROOT / "tests" / "telemetry_admission" / "schema_resource_pr_g2_bindings.v0.1.json"
)
SOURCE_PATTERNS = (
    "dbos/telemetry_admission/**/*.py",
    "dbos/telemetry_admission/**/*.json",
    "dbos/telemetry_admission/**/*.yaml",
    "dbos/telemetry_admission/**/*.md",
    "dbos/telemetry_admission/**/*.sql",
    "schemas/telemetry-*.yaml",
    "tests/telemetry_admission/**/*.py",
    "tests/telemetry_admission/**/*.json",
    "tools/telemetry_admission_*.py",
    "requirements/telemetry-admission-*.lock",
    "requirements/README.md",
    "validation/telemetry_admission_validator.py",
    "README.md",
    "pyproject.toml",
)
ZERO_EFFECTS = {
    "agent_created": False,
    "runtime_created": False,
    "entity_created": False,
    "capability_created": False,
    "permission_created": False,
    "execution_created": False,
    "evidence_created": False,
    "verification_created": False,
    "collector_created": False,
    "network_endpoint_created": False,
    "saee_called": False,
    "gate_state_changed": False,
    "production_ready_declared": False,
}


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def source_manifest() -> dict[str, Any]:
    """Return the exact DQ-018 implementation-byte manifest."""

    paths: set[Path] = set()
    for pattern in SOURCE_PATTERNS:
        paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    entries = []
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix()
        value = path.read_bytes()
        entries.append(
            {
                "path": relative,
                "size_bytes": len(value),
                "digest": _sha256_bytes(value),
            }
        )
    canonical = json.dumps(
        entries,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return {
        "file_count": len(entries),
        "total_bytes": sum(item["size_bytes"] for item in entries),
        "manifest_digest": _sha256_bytes(canonical),
        "entries": entries,
    }


# Backward-compatible internal aliases for the already frozen test surface.
_source_manifest = source_manifest


def _read_optional_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        return None


def _resolve_git_directories() -> tuple[Path | None, Path | None]:
    """Resolve Git metadata without invoking a process or trusting PATH."""

    marker = ROOT / ".git"
    if marker.is_dir():
        git_dir = marker.resolve()
    elif marker.is_file():
        pointer = _read_optional_text(marker)
        if pointer is None or not pointer.startswith("gitdir: "):
            return None, None
        referenced = Path(pointer.removeprefix("gitdir: "))
        git_dir = (
            referenced if referenced.is_absolute() else marker.parent / referenced
        ).resolve()
    else:
        return None, None

    common_pointer = _read_optional_text(git_dir / "commondir")
    common_dir = (git_dir / common_pointer).resolve() if common_pointer else git_dir
    return git_dir, common_dir


def _resolve_packed_ref(common_dir: Path, reference: str) -> str | None:
    packed = _read_optional_text(common_dir / "packed-refs")
    if packed is None:
        return None
    for line in packed.splitlines():
        if not line or line.startswith(("#", "^")):
            continue
        commit, separator, packed_reference = line.partition(" ")
        if separator and packed_reference == reference:
            return commit
    return None


def git_observation() -> dict[str, Any]:
    """Read immutable Git identity only; source bytes remain manifest-bound."""

    git_dir, common_dir = _resolve_git_directories()
    head = _read_optional_text(git_dir / "HEAD") if git_dir else None
    reference = (
        head.removeprefix("ref: ") if head and head.startswith("ref: ") else None
    )
    base_commit = head if head and reference is None else None
    if reference and git_dir and common_dir:
        base_commit = _read_optional_text(git_dir / reference)
        if base_commit is None:
            base_commit = _read_optional_text(common_dir / reference)
        if base_commit is None:
            base_commit = _resolve_packed_ref(common_dir, reference)
    branch = reference.removeprefix("refs/heads/") if reference else None
    return {
        "base_commit": base_commit,
        "branch": branch,
        "worktree_state": "NOT_EVALUATED_BY_OFFLINE_REPORT_TOOL",
        "source_binding": "IMPLEMENTATION_MANIFEST_ONLY",
        "source_commit_includes_current_implementation": False,
    }


_git_observation = git_observation


def _environment_binding() -> dict[str, Any]:
    components: dict[str, str] = {}
    for distribution in ("jsonschema", "PyYAML"):
        try:
            components[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            components[distribution] = "MISSING"
    material = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "components": components,
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return {**material, "environment_digest": _sha256_bytes(encoded)}


def _execute_binding(binding_path: Path) -> dict[str, Any]:
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    case_results: list[dict[str, Any]] = []
    for case in binding["authorized_cases"]:
        module_name, class_name, method_name = case["test_node"].split(".")
        module = importlib.import_module(f"tests.telemetry_admission.{module_name}")
        test_class = getattr(module, class_name)
        result = unittest.TestResult()
        test_class(method_name).run(result)
        if result.wasSuccessful() and result.testsRun == 1:
            status = "PASS"
            failure_class = None
        else:
            status = "FAIL"
            failures = result.failures + result.errors
            failure_class = failures[0][0].__class__.__name__ if failures else "UNKNOWN"
        case_results.append(
            {
                "case_id": case["case_id"],
                "test_node": case["test_node"],
                "result": status,
                "failure_class": failure_class,
                "effects": dict(ZERO_EFFECTS),
            }
        )
    blocked_results = [
        {
            "case_id": case["case_id"],
            "gate_refs": case["gate_refs"],
            "result": "BLOCKED_NOT_AUTHORIZED",
            "effects": dict(ZERO_EFFECTS),
        }
        for case in binding["blocked_not_authorized_cases"]
    ]
    passed = sum(case["result"] == "PASS" for case in case_results)
    failed = len(case_results) - passed
    return {
        "binding_id": binding["binding_id"],
        "catalog_id": binding["catalog_id"],
        "catalog_digest": binding["catalog_digest"],
        "authorized_subset_result": "PASS" if failed == 0 else "FAIL",
        "full_catalog_result": "BLOCKED" if failed == 0 else "FAIL",
        "authorized_case_count": len(case_results),
        "authorized_passed": passed,
        "authorized_failed": failed,
        "blocked_not_authorized_count": len(blocked_results),
        "case_results": case_results,
        "blocked_case_results": blocked_results,
        "effects": dict(ZERO_EFFECTS),
    }


def build_report(observed_at: str | None = None) -> dict[str, Any]:
    """Run exact local bindings and return a deterministic-shape receipt."""

    generated_at = observed_at or datetime.now(timezone.utc).isoformat()
    for filename in (
        SEMANTIC_RESULT_SCHEMA_FILENAME,
        SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME,
    ):
        Draft202012Validator.check_schema(read_pinned_json(filename))
    semantic = _execute_binding(SEMANTIC_BINDING)
    schema_resource = _execute_binding(SCHEMA_RESOURCE_BINDING)
    subset_pass = (
        semantic["authorized_subset_result"] == "PASS"
        and schema_resource["authorized_subset_result"] == "PASS"
    )
    return {
        "report_schema_version": "0.1",
        "report_id": "TMAI-DBOS-DQ018-OTEL-OFFLINE-CONFORMANCE-LOCAL",
        "generated_at": generated_at,
        "scope": "DQ_018_PR_G2_OFFLINE_SUBSET_ONLY",
        "source": git_observation(),
        "implementation_manifest": source_manifest(),
        "environment": _environment_binding(),
        "official_result_schema_meta_validation": "PASS",
        "semantic": semantic,
        "schema_resource": schema_resource,
        "authorized_subset_result": "PASS" if subset_pass else "FAIL",
        "full_catalog_result": "BLOCKED" if subset_pass else "FAIL",
        "full_catalog_block_reason": (
            "DQ_020_PR_G3_DEPLOYMENT_CASES_NOT_AUTHORIZED_AND_NOT_EXECUTED"
        ),
        "independent_review_complete": False,
        "production_ready": False,
        "effects": dict(ZERO_EFFECTS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--observed-at")
    args = parser.parse_args()
    report = build_report(args.observed_at)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"AUTHORIZED_SUBSET_RESULT={report['authorized_subset_result']}")
        print(f"FULL_CATALOG_RESULT={report['full_catalog_result']}")
        print(
            "SEMANTIC="
            f"{report['semantic']['authorized_passed']}/"
            f"{report['semantic']['authorized_case_count']} "
            f"BLOCKED={report['semantic']['blocked_not_authorized_count']}"
        )
        print(
            "SCHEMA_RESOURCE="
            f"{report['schema_resource']['authorized_passed']}/"
            f"{report['schema_resource']['authorized_case_count']} "
            f"BLOCKED={report['schema_resource']['blocked_not_authorized_count']}"
        )
        print("PRODUCTION_READY=false")
    return 0 if report["authorized_subset_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
