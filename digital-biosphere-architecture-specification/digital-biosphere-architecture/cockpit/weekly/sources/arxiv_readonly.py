"""Bounded arXiv Atom GET adapter. External text is data, never instruction."""

from __future__ import annotations

import hashlib
import time
import xml.etree.ElementTree as ET
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


MAX_RESPONSE_BYTES = 1_048_576
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


class ArxivReadOnlyAdapter:
    def __init__(
        self,
        opener: Callable[..., Any] | None = None,
        endpoint: str = "https://export.arxiv.org/api/query",
        max_response_bytes: int = MAX_RESPONSE_BYTES,
        retries: int = 2,
    ) -> None:
        self._opener = opener or urlopen
        self.endpoint = endpoint
        self.max_response_bytes = max_response_bytes
        self.retries = retries

    def _get(self, params: dict[str, Any]) -> tuple[bytes, str, str]:
        url = f"{self.endpoint}?{urlencode(params)}"
        request = Request(
            url,
            headers={"User-Agent": "DBA-Capability-Discovery/0.1 (reference-only)"},
            method="GET",
        )
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with self._opener(request, timeout=20) as response:
                    content_type = response.headers.get("Content-Type", "")
                    if not any(value in content_type.lower() for value in ("atom", "xml")):
                        raise ValueError("ARXIV_RESPONSE_TYPE_REJECTED")
                    body = response.read(self.max_response_bytes + 1)
                    if len(body) > self.max_response_bytes:
                        raise ValueError("SOURCE_RESPONSE_TOO_LARGE")
                    return body, hashlib.sha256(body).hexdigest(), url
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(0.2 * (attempt + 1))
        raise last_error or RuntimeError("ARXIV_SOURCE_UNAVAILABLE")

    @staticmethod
    def _parse(body: bytes, response_digest: str) -> list[dict[str, Any]]:
        root = ET.fromstring(body)
        records = []
        for entry in root.findall(f"{ATOM}entry"):
            identifier = (entry.findtext(f"{ATOM}id") or "").strip()
            title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
            summary = " ".join((entry.findtext(f"{ATOM}summary") or "").split())[:800]
            links = [item.attrib for item in entry.findall(f"{ATOM}link")]
            abs_link = next(
                (item.get("href") for item in links if item.get("rel") == "alternate"),
                identifier,
            )
            records.append({
                "source_kind": "ARXIV",
                "name": title or identifier,
                "summary": summary,
                "source_reference": abs_link,
                "arxiv_identifier": identifier,
                "published_at": entry.findtext(f"{ATOM}published"),
                "updated_at": entry.findtext(f"{ATOM}updated"),
                "doi": entry.findtext(f"{ARXIV}doi"),
                "source_digest_sha256": response_digest,
            })
        return records

    def search(self, query: str, max_results: int, observed_at: str) -> dict[str, Any]:
        return self._request_batch({
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        }, observed_at, "ARXIV")

    def fetch_ids(self, identifiers: list[str], observed_at: str) -> dict[str, Any]:
        if not identifiers:
            return {
                "status": "AVAILABLE",
                "records": [],
                "evidence": {
                    "source": "ARXIV_REGISTERED",
                    "method": "GET",
                    "observed_at": observed_at,
                    "source_digest_sha256": hashlib.sha256(b"").hexdigest(),
                },
            }
        return self._request_batch({
            "id_list": ",".join(sorted(set(identifiers))),
            "max_results": len(set(identifiers)),
        }, observed_at, "ARXIV_REGISTERED")

    def _request_batch(self, params: dict[str, Any], observed_at: str, source: str):
        try:
            body, digest, url = self._get(params)
            return {
                "status": "AVAILABLE",
                "records": self._parse(body, digest),
                "evidence": {
                    "source": source,
                    "url": url,
                    "method": "GET",
                    "observed_at": observed_at,
                    "source_digest_sha256": digest,
                },
            }
        except (HTTPError, URLError, TimeoutError, ValueError, ET.ParseError) as exc:
            return {
                "status": "NOT_ASSESSED_SOURCE_UNAVAILABLE",
                "records": [],
                "evidence": {
                    "source": source,
                    "url": self.endpoint,
                    "method": "GET",
                    "observed_at": observed_at,
                    "reason": type(exc).__name__,
                    "partial_payload_used": False,
                },
            }
