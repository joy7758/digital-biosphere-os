"""Read-only npm dependency observation that proves the worktree stayed unchanged."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from .source_result import AVAILABLE, SOURCE_MUTATION_DETECTED, SourceResult


class DependencyReadOnlyAdapter:
    def __init__(
        self,
        command_runner: Callable[[list[str], Path], subprocess.CompletedProcess[str]] | None = None,
        canonical_high_count: int = 2,
    ) -> None:
        self._runner = command_runner or self._run
        self._canonical_high_count = canonical_high_count

    @staticmethod
    def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)

    def observe(self, site_dir: Path, repository_root: Path, observed_at: str) -> SourceResult:
        before = self._runner(["git", "status", "--porcelain=v1", "-z"], repository_root).stdout
        npm_version_result = self._runner(["npm", "--version"], site_dir)
        audit = self._runner(["npm", "audit", "--omit=dev", "--json"], site_dir)
        audit_payload = self._parse_json(audit.stdout)
        outdated = self._runner(["npm", "outdated", "--json"], site_dir)
        outdated_payload = self._parse_json(outdated.stdout)
        after = self._runner(["git", "status", "--porcelain=v1", "-z"], repository_root).stdout

        vulnerabilities = audit_payload.get("vulnerabilities", {}) if isinstance(audit_payload, dict) else {}
        metadata_counts = audit_payload.get("metadata", {}).get("vulnerabilities", {}) if isinstance(audit_payload, dict) else {}
        high_count = metadata_counts.get("high") if isinstance(metadata_counts.get("high"), int) else None
        critical_count = metadata_counts.get("critical") if isinstance(metadata_counts.get("critical"), int) else None
        direct = sorted(name for name, item in vulnerabilities.items() if isinstance(item, dict) and item.get("isDirect") is True)
        transitive = sorted(name for name, item in vulnerabilities.items() if isinstance(item, dict) and item.get("isDirect") is not True)
        fix_available = sorted(
            name for name, item in vulnerabilities.items()
            if isinstance(item, dict) and item.get("fixAvailable") not in (False, None)
        )
        audit_available = isinstance(audit_payload, dict) and bool(audit_payload)
        conflict = high_count is not None and high_count != self._canonical_high_count
        unchanged = before == after
        status = AVAILABLE if unchanged else SOURCE_MUTATION_DETECTED
        return SourceResult(
            source_id="npm-audit:digital-biosphere-architecture/site",
            project_id="DBA_COCKPIT",
            status=status,
            source_reference="digital-biosphere-architecture/site/package-lock.json + npm advisory database",
            observed_at=observed_at,
            retrieved_at=observed_at,
            payload={
                "audit_status": "AVAILABLE" if audit_available else "NOT_ASSESSED",
                "audit_exit_code": audit.returncode,
                "npm_version": npm_version_result.stdout.strip() if npm_version_result.returncode == 0 else "NOT_ASSESSED",
                "canonical_retained": {"high_count": self._canonical_high_count},
                "observed_result": {
                    "high_count": high_count,
                    "critical_count": critical_count,
                    "high_packages": sorted(vulnerabilities),
                    "direct_packages": direct,
                    "transitive_packages": transitive,
                    "fix_available_packages": fix_available,
                },
                "comparison_status": "CONFLICT_REQUIRES_REVIEW" if conflict else (
                    "MATCHES_RETAINED_COUNT" if high_count is not None else "NOT_ASSESSED"
                ),
                "outdated_status": "AVAILABLE" if outdated_payload is not None else "NOT_ASSESSED",
                "outdated_exit_code": outdated.returncode,
                "outdated_packages": outdated_payload if outdated_payload is not None else {},
                "git_status_unchanged": unchanged,
                "runtime_binding": "NOT_ESTABLISHED",
                "exploitability": "NOT_ASSESSED",
                "auto_reconciliation": False,
            },
            limitations=[
                "A nonzero npm audit exit code is retained as evidence and does not stop other Cells.",
                "Advisory counts do not establish remote exploitability or runtime binding.",
                "No package install, update, audit fix, or lockfile mutation is performed.",
            ],
        )

    @staticmethod
    def _parse_json(value: str) -> dict[str, Any] | None:
        if not value.strip():
            return None
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
