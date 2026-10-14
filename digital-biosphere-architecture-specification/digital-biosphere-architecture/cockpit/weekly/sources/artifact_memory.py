"""Read a prior successful live artifact without changing GitHub state."""

from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError

from .github_readonly import GithubApi
from .source_result import AVAILABLE, NOT_ASSESSED_CREDENTIAL_UNAVAILABLE, SourceResult


ARTIFACT_PREFIX = "dba-weekly-cockpit-live-pilot-"


class ArtifactMemory:
    def __init__(self, api: GithubApi | None = None) -> None:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.api = api or (GithubApi(token=token) if token else None)

    def load_previous(
        self,
        *,
        repository: str,
        workflow: str,
        branch: str,
        current_run_id: str,
        observed_at: str,
    ) -> SourceResult:
        if self.api is None:
            return SourceResult.unavailable(
                source_id="github-actions-artifact-memory",
                project_id="DBA_COCKPIT",
                source_reference=f"github-actions:{repository}/{workflow}",
                observed_at=observed_at,
                status=NOT_ASSESSED_CREDENTIAL_UNAVAILABLE,
                reason="CURRENT_REPOSITORY_ACTIONS_READ_CREDENTIAL_UNAVAILABLE",
            )
        policy = {
            "ARTIFACT_FROM_CURRENT_RUN_REJECTED": True,
            "FAILED_OR_EXPIRED_ARTIFACT_REJECTED": True,
        }
        try:
            runs = self.api.request_json(
                f"repos/{repository}/actions/workflows/{workflow}/runs?branch={branch}&event=workflow_dispatch&per_page=50"
            ).get("workflow_runs", [])
            for run in runs:
                if str(run.get("id")) == str(current_run_id):
                    continue
                if run.get("head_branch") != branch:
                    continue
                if run.get("status") != "completed" or run.get("conclusion") != "success":
                    continue
                artifacts = self.api.request_json(
                    f"repos/{repository}/actions/runs/{run['id']}/artifacts?per_page=100"
                ).get("artifacts", [])
                for artifact in artifacts:
                    if artifact.get("expired") is True or not str(artifact.get("name", "")).startswith(ARTIFACT_PREFIX):
                        continue
                    archive = self.api.request_bytes(artifact["archive_download_url"])
                    digest_state = self._verify_digest(archive, artifact.get("digest"))
                    if digest_state == "FAIL":
                        continue
                    snapshot = self._snapshot_from_archive(archive)
                    if not self.valid_live_snapshot(snapshot):
                        continue
                    return SourceResult(
                        source_id="github-actions-artifact-memory",
                        project_id="DBA_COCKPIT",
                        status=AVAILABLE,
                        source_reference=f"github-actions-run:{run['id']}/artifact:{artifact['id']}",
                        observed_at=observed_at,
                        retrieved_at=observed_at,
                        payload={
                            **policy,
                            "memory_status": "PREVIOUS_LIVE_ARTIFACT_AVAILABLE",
                            "PREVIOUS_LIVE_ARTIFACT_LOADED": True,
                            "MEMORY_COMPARISON_EXECUTED": False,
                            "previous_run_id": str(run["id"]),
                            "artifact_id": str(artifact["id"]),
                            "artifact_digest_verification": digest_state,
                            "snapshot": snapshot,
                        },
                        limitations=["Artifact memory compares observations; it does not overwrite source history."],
                    )
            return SourceResult(
                source_id="github-actions-artifact-memory",
                project_id="DBA_COCKPIT",
                status=AVAILABLE,
                source_reference=f"github-actions:{repository}/{workflow}",
                observed_at=observed_at,
                retrieved_at=observed_at,
                payload={
                    **policy,
                    "memory_status": "NO_PREVIOUS_LIVE_ARTIFACT",
                    "PREVIOUS_LIVE_ARTIFACT_LOADED": False,
                    "MEMORY_COMPARISON_EXECUTED": False,
                    "snapshot": None,
                },
                limitations=["No qualifying prior live artifact means no cross-run trend claim is allowed."],
            )
        except (HTTPError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
            return SourceResult.unavailable(
                source_id="github-actions-artifact-memory",
                project_id="DBA_COCKPIT",
                source_reference=f"github-actions:{repository}/{workflow}",
                observed_at=observed_at,
                reason=f"ARTIFACT_MEMORY_READ_FAILED:{type(exc).__name__}",
            )

    @staticmethod
    def _verify_digest(archive: bytes, expected: str | None) -> str:
        if not expected:
            return "NOT_PROVIDED_BY_API"
        algorithm, separator, value = expected.partition(":")
        if separator != ":" or algorithm.lower() != "sha256":
            return "UNSUPPORTED"
        return "PASS" if hashlib.sha256(archive).hexdigest() == value.lower() else "FAIL"

    @staticmethod
    def _snapshot_from_archive(archive: bytes) -> dict[str, Any]:
        with zipfile.ZipFile(io.BytesIO(archive)) as package:
            candidates = [name for name in package.namelist() if name == "latest.json" or name.endswith("/latest.json")]
            if len(candidates) != 1:
                raise ValueError("LIVE_SNAPSHOT_NOT_UNIQUE")
            return json.loads(package.read(candidates[0]).decode("utf-8"))

    @staticmethod
    def valid_live_snapshot(snapshot: Any) -> bool:
        if not isinstance(snapshot, dict):
            return False
        if snapshot.get("schema_version") != "0.1":
            return False
        if snapshot.get("mode") != "LIVE_READ_ONLY_OBSERVATION_PILOT":
            return False
        if snapshot.get("boundaries", {}).get("pilot_only") is not True:
            return False
        observed_at = snapshot.get("observed_at")
        try:
            parsed = datetime.fromisoformat(str(observed_at).replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None
