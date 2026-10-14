"""Read the previous compatible capability registry from GitHub artifact memory."""

from __future__ import annotations

import hashlib
import io
import json
import os
import zipfile
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError

try:
    from ..sources.github_readonly import GithubApi
except ImportError:
    from sources.github_readonly import GithubApi

from .fingerprint import registry_digest


ARTIFACT_PREFIX = "dba-automatic-capability-discovery-"


class CapabilityArtifactMemory:
    def __init__(self, api: GithubApi | None = None) -> None:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.api = api or (GithubApi(token=token) if token else None)

    def load_previous(
        self,
        repository: str,
        workflow: str,
        current_run_id: str,
        observed_at: str,
    ) -> dict[str, Any]:
        base = {
            "previous_registry": None,
            "previous_registry_loaded": False,
            "previous_artifact_rejected": False,
            "memory_bootstrap_source": "DCDAT_001_BASELINE",
        }
        if self.api is None:
            return {
                **base,
                "status": "NO_CURRENT_REPOSITORY_CREDENTIAL",
                "source_reference": f"github-actions:{repository}/{workflow}",
            }
        try:
            runs = self.api.request_json(
                f"repos/{repository}/actions/workflows/{workflow}/runs?branch=main&per_page=50"
            ).get("workflow_runs", [])
            rejected = False
            for run in runs:
                if str(run.get("id")) == str(current_run_id):
                    continue
                if (
                    run.get("head_branch") != "main"
                    or run.get("status") != "completed"
                    or run.get("conclusion") != "success"
                ):
                    continue
                artifacts = self.api.request_json(
                    f"repos/{repository}/actions/runs/{run['id']}/artifacts?per_page=100"
                ).get("artifacts", [])
                for artifact in artifacts:
                    if artifact.get("expired") or not str(artifact.get("name", "")).startswith(
                        ARTIFACT_PREFIX
                    ):
                        continue
                    archive = self.api.request_bytes(
                        artifact["archive_download_url"], max_bytes=5_242_880
                    )
                    if not self._artifact_digest_valid(archive, artifact.get("digest")):
                        rejected = True
                        continue
                    registry = self._registry_from_archive(archive)
                    if not self._registry_valid(registry):
                        rejected = True
                        continue
                    return {
                        **base,
                        "status": "PREVIOUS_CAPABILITY_ARTIFACT_AVAILABLE",
                        "source_reference": f"github-actions-run:{run['id']}/artifact:{artifact['id']}",
                        "previous_registry": registry,
                        "previous_registry_loaded": True,
                        "previous_artifact_rejected": rejected,
                        "memory_bootstrap_source": "PREVIOUS_SUCCESSFUL_MAIN_ARTIFACT",
                        "previous_run_id": str(run["id"]),
                        "artifact_id": str(artifact["id"]),
                    }
            return {
                **base,
                "status": (
                    "PREVIOUS_ARTIFACT_REJECTED"
                    if rejected
                    else "NO_PREVIOUS_CAPABILITY_ARTIFACT"
                ),
                "source_reference": f"github-actions:{repository}/{workflow}",
                "previous_artifact_rejected": rejected,
            }
        except (
            HTTPError,
            URLError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            zipfile.BadZipFile,
        ) as exc:
            return {
                **base,
                "status": "PREVIOUS_ARTIFACT_REJECTED",
                "source_reference": f"github-actions:{repository}/{workflow}",
                "previous_artifact_rejected": True,
                "reason": type(exc).__name__,
            }

    @staticmethod
    def _artifact_digest_valid(archive: bytes, expected: str | None) -> bool:
        if not expected:
            return True
        algorithm, separator, value = expected.partition(":")
        return (
            separator == ":"
            and algorithm.lower() == "sha256"
            and hashlib.sha256(archive).hexdigest() == value.lower()
        )

    @staticmethod
    def _registry_from_archive(archive: bytes) -> dict[str, Any]:
        with zipfile.ZipFile(io.BytesIO(archive)) as package:
            names = [
                name
                for name in package.namelist()
                if name == "reference-absorption-registry.json"
                or name.endswith("/reference-absorption-registry.json")
            ]
            if len(names) != 1:
                raise ValueError("CAPABILITY_REGISTRY_NOT_UNIQUE")
            return json.loads(package.read(names[0]).decode("utf-8"))

    @staticmethod
    def _registry_valid(registry: Any) -> bool:
        if (
            not isinstance(registry, dict)
            or registry.get("schema") != "dba.reference_absorption_registry.v0.2"
        ):
            return False
        expected = registry.get("current_registry_digest")
        if not isinstance(expected, str) or registry_digest(registry) != expected:
            return False
        try:
            parsed = datetime.fromisoformat(
                str(registry.get("updated_at")).replace("Z", "+00:00")
            )
        except ValueError:
            return False
        return (
            parsed.tzinfo is not None
            and (datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days <= 30
        )
