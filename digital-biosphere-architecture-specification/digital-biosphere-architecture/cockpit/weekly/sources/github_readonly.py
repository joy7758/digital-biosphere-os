"""Allowlisted GitHub GET observations with no mutation methods."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .source_result import (
    AVAILABLE,
    NOT_ASSESSED_CREDENTIAL_UNAVAILABLE,
    NOT_ASSESSED_SOURCE_UNAVAILABLE,
    SOURCE_DRIFT,
    SourceResult,
)


ALLOWLIST = {
    "DBA_COCKPIT": "joy7758/digital-biosphere-architecture-specification",
    "RED_YAN_OFFICIAL_DOCUMENT": "joy7758/hongyan-official-document",
    "TITMAS_SUPPORTING_LAYER": "joy7758/titmas",
    "DIGITAL_CELL_DEMO": "joy7758/titmas-demo",
    "TITMAC_SCOUT": "joy7758/titmac-scout",
}

CURRENT_REPOSITORY_ACCESS_MODE = "GITHUB_API_CURRENT_REPOSITORY_READ_ONLY"
PUBLIC_REPOSITORY_ACCESS_MODE = "GITHUB_API_PUBLIC_REPOSITORY_READ_ONLY"
PRIVATE_CROSS_REPOSITORY_ACCESS_MODE = "CROSS_REPOSITORY_CREDENTIAL_GATED_READ_ONLY"
PROJECT_ACCESS_MODES = {
    "DBA_COCKPIT": CURRENT_REPOSITORY_ACCESS_MODE,
    "RED_YAN_OFFICIAL_DOCUMENT": PRIVATE_CROSS_REPOSITORY_ACCESS_MODE,
    "TITMAS_SUPPORTING_LAYER": PRIVATE_CROSS_REPOSITORY_ACCESS_MODE,
    "DIGITAL_CELL_DEMO": PUBLIC_REPOSITORY_ACCESS_MODE,
    "TITMAC_SCOUT": "EXISTING_READ_ONLY_STATUS_ADAPTER",
}

SENSITIVE_REDIRECT_HEADERS = frozenset(
    {"authorization", "proxy-authorization", "cookie", "cookie2"}
)


class ReadOnlyRedirectHandler(HTTPRedirectHandler):
    """Follow HTTPS redirects without forwarding credentials across origins."""

    @staticmethod
    def _origin(url: str) -> tuple[str, str | None, int | None]:
        parsed = urlparse(url)
        default_port = 443 if parsed.scheme.lower() == "https" else 80
        return parsed.scheme.lower(), parsed.hostname, parsed.port or default_port

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        if urlparse(redirected.full_url).scheme.lower() != "https":
            raise ValueError("GITHUB_REDIRECT_HTTPS_REQUIRED")
        if self._origin(req.full_url) != self._origin(redirected.full_url):
            for mapping in (redirected.headers, redirected.unredirected_hdrs):
                for name in list(mapping):
                    if name.lower() in SENSITIVE_REDIRECT_HEADERS:
                        del mapping[name]
        return redirected


class GithubApi:
    """Minimal GitHub API reader. Only GET is exposed."""

    def __init__(
        self,
        token: str | None = None,
        opener: Callable[..., Any] | None = None,
        api_root: str = "https://api.github.com",
    ) -> None:
        self._token = token or ""
        self._opener = opener or build_opener(ReadOnlyRedirectHandler()).open
        self._api_root = api_root.rstrip("/")

    def _request(self, reference: str) -> Request:
        url = reference if reference.startswith("https://") else f"{self._api_root}/{reference.lstrip('/')}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "dba-weekly-cockpit-read-only-pilot",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return Request(url, headers=headers, method="GET")

    @staticmethod
    def _read_bounded(response: Any, max_bytes: int) -> bytes:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("SOURCE_RESPONSE_TOO_LARGE")
        return body

    def request_json_with_digest(
        self,
        reference: str,
        *,
        allow_404: bool = False,
        max_bytes: int = 1_048_576,
    ) -> tuple[Any, str | None]:
        try:
            with self._opener(self._request(reference), timeout=20) as response:
                body = self._read_bounded(response, max_bytes)
                return json.loads(body.decode("utf-8")), hashlib.sha256(body).hexdigest()
        except HTTPError as exc:
            if allow_404 and exc.code == 404:
                return None, None
            raise

    def request_json(self, reference: str, *, allow_404: bool = False) -> Any:
        payload, _ = self.request_json_with_digest(reference, allow_404=allow_404)
        return payload

    def request_bytes(self, reference: str, *, max_bytes: int = 5_242_880) -> bytes:
        with self._opener(self._request(reference), timeout=30) as response:
            return self._read_bounded(response, max_bytes)


class GithubPublicSearchAdapter:
    """Public metadata search through the existing GET-only GithubApi."""

    def __init__(self, api: GithubApi | None = None) -> None:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.api = api or GithubApi(token=token)

    @staticmethod
    def _record(details, head, release, digest, observed_at):
        license_value = details.get("license") or {}
        return {
            "source_kind": "GITHUB",
            "name": details.get("name") or details.get("full_name") or "UNKNOWN",
            "summary": str(details.get("description") or "")[:800],
            "source_reference": details.get("html_url") or f"https://github.com/{details.get('full_name', '')}",
            "repository": details.get("full_name"),
            "default_branch": details.get("default_branch"),
            "head_sha": head.get("sha") if isinstance(head, dict) else None,
            "latest_release": release.get("tag_name") if isinstance(release, dict) else None,
            "updated_at": details.get("updated_at"),
            "pushed_at": details.get("pushed_at"),
            "archived": bool(details.get("archived")),
            "fork": bool(details.get("fork")),
            "license_status": "LICENSE_UI_ONLY" if license_value.get("spdx_id") else "LICENSE_NOT_FOUND",
            "license_spdx_ui": license_value.get("spdx_id"),
            "source_digest_sha256": digest,
            "observed_at": observed_at,
        }

    def observe_repositories(self, repositories: list[str], observed_at: str) -> dict[str, Any]:
        records, evidence = [], []
        for repository in sorted(set(repositories)):
            try:
                details, details_digest = self.api.request_json_with_digest(f"repos/{repository}")
                branch = details.get("default_branch", "main")
                head, head_digest = self.api.request_json_with_digest(
                    f"repos/{repository}/commits/{quote(branch, safe='')}"
                )
                release, release_digest = self.api.request_json_with_digest(
                    f"repos/{repository}/releases/latest", allow_404=True
                )
                digest = hashlib.sha256(json.dumps(
                    [details_digest, head_digest, release_digest],
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")).hexdigest()
                records.append(self._record(details, head, release, digest, observed_at))
                evidence.append({
                    "source": "GITHUB_REGISTERED",
                    "url": f"https://api.github.com/repos/{repository}",
                    "method": "GET",
                    "observed_at": observed_at,
                    "source_digest_sha256": digest,
                })
            except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                evidence.append({
                    "source": "GITHUB_REGISTERED",
                    "url": f"https://api.github.com/repos/{repository}",
                    "method": "GET",
                    "observed_at": observed_at,
                    "reason": type(exc).__name__,
                    "partial_payload_used": False,
                })
        status = "AVAILABLE" if records or not repositories else "NOT_ASSESSED_SOURCE_UNAVAILABLE"
        return {"status": status, "records": records, "evidence": evidence}

    def search(self, query: str, max_results: int, observed_at: str) -> dict[str, Any]:
        reference = (
            f"search/repositories?q={quote(query, safe='')}"
            f"&sort=updated&order=desc&per_page={max_results}"
        )
        try:
            payload, digest = self.api.request_json_with_digest(reference)
            repositories = [
                item.get("full_name") for item in payload.get("items", []) if item.get("full_name")
            ][:max_results]
            observed = self.observe_repositories(repositories, observed_at)
            return {
                "status": "AVAILABLE" if observed["records"] or not repositories else observed["status"],
                "records": observed["records"],
                "evidence": [{
                    "source": "GITHUB_PUBLIC_SEARCH",
                    "url": f"https://api.github.com/{reference}",
                    "method": "GET",
                    "observed_at": observed_at,
                    "source_digest_sha256": digest,
                }] + observed["evidence"],
            }
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            return {
                "status": "NOT_ASSESSED_SOURCE_UNAVAILABLE",
                "records": [],
                "evidence": [{
                    "source": "GITHUB_PUBLIC_SEARCH",
                    "url": f"https://api.github.com/{reference}",
                    "method": "GET",
                    "observed_at": observed_at,
                    "reason": type(exc).__name__,
                    "partial_payload_used": False,
                }],
            }


class GithubReadOnlyAdapter:
    """Observe only explicitly configured repositories."""

    def __init__(
        self,
        api: GithubApi | None = None,
        *,
        current_repository_api: GithubApi | None = None,
        public_repository_api: GithubApi | None = None,
        private_cross_repository_api: GithubApi | None = None,
    ) -> None:
        current_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        private_token = os.environ.get("DBA_COCKPIT_READ_TOKEN")
        self._legacy_api = api
        self.current_repository_api = current_repository_api or api or GithubApi(token=current_token)
        self.public_repository_api = public_repository_api or api or GithubApi()
        self.private_cross_repository_api = private_cross_repository_api or (
            (api or GithubApi(token=private_token)) if private_token else None
        )

    @staticmethod
    def _assert_allowlisted(project_id: str, repository: str) -> None:
        if ALLOWLIST.get(project_id) != repository:
            raise ValueError("REPOSITORY_NOT_ALLOWLISTED")

    def _api_for_project(self, project: dict[str, Any]) -> GithubApi | None:
        project_id = project["project_id"]
        access_mode = project.get("source_access_mode")
        credential_required = project.get("cross_repo_credential_required") is True
        if access_mode is None and self._legacy_api is not None:
            return self._legacy_api
        if PROJECT_ACCESS_MODES.get(project_id) != access_mode:
            raise ValueError("SOURCE_ACCESS_MODE_MISMATCH")
        if access_mode == CURRENT_REPOSITORY_ACCESS_MODE and not credential_required:
            return self.current_repository_api
        if access_mode == PUBLIC_REPOSITORY_ACCESS_MODE and not credential_required:
            return self.public_repository_api
        if access_mode == PRIVATE_CROSS_REPOSITORY_ACCESS_MODE and credential_required:
            return self.private_cross_repository_api
        raise ValueError("SOURCE_ACCESS_CONFIGURATION_INVALID")

    def observe_project(self, project: dict[str, Any], observed_at: str) -> SourceResult:
        project_id = project["project_id"]
        repository = project.get("repository")
        if not repository:
            return SourceResult.unavailable(
                source_id=f"github:{project_id}",
                project_id=project_id,
                source_reference="credential-gated-private-repository",
                observed_at=observed_at,
                status=NOT_ASSESSED_CREDENTIAL_UNAVAILABLE,
                reason="CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
            )
        self._assert_allowlisted(project_id, repository)
        if (
            project.get("cross_repo_credential_required")
            and self.private_cross_repository_api is None
        ):
            return SourceResult.unavailable(
                source_id=f"github:{repository}",
                project_id=project_id,
                source_reference=f"https://github.com/{repository}",
                observed_at=observed_at,
                status=NOT_ASSESSED_CREDENTIAL_UNAVAILABLE,
                reason="CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
            )
        try:
            api = self._api_for_project(project)
        except (KeyError, ValueError) as exc:
            return SourceResult.unavailable(
                source_id=f"github:{repository}",
                project_id=project_id,
                source_reference=f"https://github.com/{repository}",
                observed_at=observed_at,
                reason=f"GITHUB_READ_FAILED:{type(exc).__name__}",
            )
        if api is None:
            raise AssertionError("PRIVATE_CROSS_REPOSITORY_API_REQUIRED")
        try:
            metadata = api.request_json(f"repos/{repository}")
            branch = project.get("branch") or metadata.get("default_branch") or "main"
            commit = api.request_json(f"repos/{repository}/commits/{quote(branch, safe='')}")
            revision = commit["sha"]
            tree_digest = commit.get("commit", {}).get("tree", {}).get("sha")
            runs = api.request_json(
                f"repos/{repository}/actions/runs?branch={quote(branch, safe='')}&status=completed&per_page=5"
            )
            pulls = api.request_json(f"repos/{repository}/pulls?state=open&per_page=100")
            issues = api.request_json(f"repos/{repository}/issues?state=open&per_page=100")
            release = api.request_json(f"repos/{repository}/releases/latest", allow_404=True)
            status_file = self._status_file(api, project, repository, revision, branch)
            payload = {
                "repository": repository,
                "default_branch": branch,
                "head_revision": revision,
                "head_tree_digest": tree_digest,
                "head_date": commit.get("commit", {}).get("committer", {}).get("date"),
                "recent_completed_ci": [
                    {
                        "run_id": item.get("id"),
                        "name": item.get("name"),
                        "conclusion": item.get("conclusion"),
                        "head_sha": item.get("head_sha"),
                        "completed_at": item.get("updated_at"),
                    }
                    for item in runs.get("workflow_runs", [])
                ],
                "open_pull_request_count": len(pulls) if isinstance(pulls, list) else 0,
                "open_issue_count": len(
                    [item for item in issues if isinstance(item, dict) and "pull_request" not in item]
                ) if isinstance(issues, list) else 0,
                "latest_release": None if release is None else {
                    "tag": release.get("tag_name"),
                    "published_at": release.get("published_at"),
                    "url": release.get("html_url"),
                },
                "declared_status_file": status_file,
            }
            return SourceResult(
                source_id=f"github:{repository}",
                project_id=project_id,
                status=AVAILABLE,
                source_reference=f"https://github.com/{repository}/tree/{revision}",
                observed_at=observed_at,
                retrieved_at=observed_at,
                payload=payload,
                limitations=[
                    "GitHub metadata is a point-in-time observation, not project acceptance.",
                    "Repository visibility does not establish production deployment or safety.",
                ],
            )
        except IncompleteRead:
            return SourceResult(
                source_id=f"github:{repository}",
                project_id=project_id,
                status="NOT_ASSESSED",
                source_reference=f"https://github.com/{repository}",
                observed_at=observed_at,
                retrieved_at=observed_at,
                payload={
                    "repository": repository,
                    "source_kind": "GITHUB_REPOSITORY_METADATA",
                    "reason_code": "NOT_ASSESSED_SOURCE_UNAVAILABLE",
                    "source_available": False,
                    "evidence_admitted": False,
                    "partial_payload_used": False,
                    "exception_class": "IncompleteRead",
                },
                limitations=[
                    "The incomplete response was discarded without parsing partial bytes.",
                    "Source unavailability is not interpreted as a healthy project state.",
                ],
            )
        except (HTTPError, URLError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return SourceResult.unavailable(
                source_id=f"github:{repository}",
                project_id=project_id,
                source_reference=f"https://github.com/{repository}",
                observed_at=observed_at,
                reason=f"GITHUB_READ_FAILED:{type(exc).__name__}",
            )

    def _status_file(
        self,
        api: GithubApi,
        project: dict[str, Any],
        repository: str,
        revision: str,
        branch: str,
    ) -> dict[str, Any]:
        path = project.get("status_path")
        if not path:
            return {"status": "NOT_DECLARED", "path": None, "revision_relation": "NOT_APPLICABLE"}
        encoded = quote(path, safe="/")
        content = api.request_json(
            f"repos/{repository}/contents/{encoded}?ref={quote(revision, safe='')}", allow_404=True
        )
        if content is None:
            return {"status": "NOT_FOUND", "path": path, "revision_relation": "NOT_ASSESSED"}
        history = api.request_json(
            f"repos/{repository}/commits?path={encoded}&sha={quote(branch, safe='')}&per_page=1"
        )
        latest = history[0] if isinstance(history, list) and history else {}
        return {
            "status": "PRESENT",
            "path": path,
            "blob_sha": content.get("sha"),
            "size": content.get("size"),
            "last_changed_at": latest.get("commit", {}).get("committer", {}).get("date"),
            "revision_relation": "FETCHED_AT_EXACT_HEAD_REVISION",
        }

    def observe_scout(self, observed_at: str) -> SourceResult:
        """Reuse the existing fail-closed Scout adapter when a dedicated token exists."""
        repository = ALLOWLIST["TITMAC_SCOUT"]
        token = os.environ.get("DBA_COCKPIT_READ_TOKEN")
        if not token:
            return SourceResult.unavailable(
                source_id=f"github:{repository}",
                project_id="TITMAC_SCOUT",
                source_reference=f"https://github.com/{repository}",
                observed_at=observed_at,
                status=NOT_ASSESSED_CREDENTIAL_UNAVAILABLE,
                reason="CROSS_REPO_READ_CREDENTIAL_UNAVAILABLE",
            )

        dba_root = Path(__file__).resolve().parents[3]
        if str(dba_root) not in sys.path:
            sys.path.insert(0, str(dba_root))
        from cockpit.read_only_status_adapter import CockpitSourceError, ReadOnlyStatusAdapter

        def runner(command: list[str]) -> subprocess.CompletedProcess[str]:
            env = dict(os.environ)
            env["GH_TOKEN"] = token
            return subprocess.run(command, capture_output=True, text=True, check=False, env=env)

        try:
            projection = ReadOnlyStatusAdapter(command_runner=runner).fetch_github(
                "titmac-scout",
                retrieved_at=datetime.fromisoformat(observed_at.replace("Z", "+00:00")).astimezone(timezone.utc),
            )
            return SourceResult(
                source_id=f"github:{repository}:existing-adapter",
                project_id="TITMAC_SCOUT",
                status=AVAILABLE,
                source_reference=f"cockpit/source-registry.json#titmac-scout@{projection['source_revision']}",
                observed_at=observed_at,
                retrieved_at=observed_at,
                payload=projection,
                limitations=["The projection remains observation-only and fail-closed on source drift."],
            )
        except CockpitSourceError as exc:
            status = SOURCE_DRIFT if exc.code == "SOURCE_DRIFT" else NOT_ASSESSED_SOURCE_UNAVAILABLE
            return SourceResult.unavailable(
                source_id=f"github:{repository}:existing-adapter",
                project_id="TITMAC_SCOUT",
                source_reference="cockpit/source-registry.json#titmac-scout",
                observed_at=observed_at,
                status=status,
                reason=exc.code,
            )
