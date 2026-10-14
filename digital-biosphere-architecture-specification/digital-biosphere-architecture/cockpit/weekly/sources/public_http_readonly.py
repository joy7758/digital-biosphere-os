"""Allowlisted public HTTP observations using GET or HEAD only."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .source_result import AVAILABLE, SourceResult


ALLOWED_ENDPOINTS = (
    "https://dcell.net/",
    "https://dcell.net/pilot",
    "https://dcell.net/health",
    "https://dcell.net/ready",
)


class PublicHttpReadOnlyAdapter:
    def __init__(self, opener: Callable[..., Any] = urlopen) -> None:
        self._opener = opener

    def observe(self, url: str, observed_at: str, method: str = "GET") -> SourceResult:
        if url not in ALLOWED_ENDPOINTS:
            raise ValueError("ENDPOINT_NOT_ALLOWLISTED")
        if method not in {"GET", "HEAD"}:
            raise ValueError("READ_ONLY_HTTP_METHOD_REQUIRED")
        request = Request(
            url,
            headers={"User-Agent": "dba-weekly-cockpit-read-only-pilot"},
            method=method,
        )
        started = time.monotonic()
        try:
            with self._opener(request, timeout=20) as response:
                body = response.read(1024 * 1024) if method == "GET" else b""
                status_code = response.getcode()
                headers = response.headers
        except HTTPError as exc:
            body = exc.read(1024 * 1024) if method == "GET" else b""
            status_code = exc.code
            headers = exc.headers
        except (URLError, TimeoutError, OSError) as exc:
            return SourceResult.unavailable(
                source_id=f"http:{url}",
                project_id="PUBLIC_DCELL_ENDPOINTS",
                source_reference=url,
                observed_at=observed_at,
                reason=f"PUBLIC_HTTP_READ_FAILED:{type(exc).__name__}",
            )
        return SourceResult(
            source_id=f"http:{url}",
            project_id="PUBLIC_DCELL_ENDPOINTS",
            status=AVAILABLE,
            source_reference=url,
            observed_at=observed_at,
            retrieved_at=observed_at,
            payload={
                "method": method,
                "status_code": status_code,
                "duration_ms": max(0, round((time.monotonic() - started) * 1000)),
                "content_type": headers.get("Content-Type"),
                "content_length": headers.get("Content-Length"),
                "body_sha256": hashlib.sha256(body).hexdigest() if method == "GET" else None,
                "body_truncated_at_bytes": 1024 * 1024 if len(body) == 1024 * 1024 else None,
            },
            limitations=["HTTP availability is not deployment acceptance, health certification, or project truth."],
        )

    def observe_all(self, observed_at: str) -> list[SourceResult]:
        return [self.observe(url, observed_at) for url in ALLOWED_ENDPOINTS]
