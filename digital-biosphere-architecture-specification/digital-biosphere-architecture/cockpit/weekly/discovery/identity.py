"""Deterministic identity normalization without fuzzy or model-based merging."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


ARXIV_PATTERN = re.compile(r"(?P<family>\d{4}\.\d{4,5})(?:v(?P<version>\d+))?", re.I)
GITHUB_PATTERN = re.compile(r"^/?(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$")


def normalized_name(value: str) -> str:
    return " ".join(str(value).strip().casefold().split())


def normalize_arxiv(value: str) -> tuple[str | None, str | None]:
    match = ARXIV_PATTERN.search(str(value))
    if not match:
        return None, None
    family = match.group("family")
    version = f"v{match.group('version')}" if match.group("version") else None
    return family, version


def normalize_repository(value: str) -> str | None:
    raw = str(value).strip()
    if raw.startswith(("http://", "https://")):
        parsed = urlparse(raw)
        if parsed.hostname not in {"github.com", "www.github.com"}:
            return None
        raw = parsed.path
    match = GITHUB_PATTERN.match(raw)
    if not match:
        return None
    return f"{match.group('owner').casefold()}/{match.group('repo').casefold()}"


def identity_from_reference(reference: str) -> dict[str, str] | None:
    arxiv_id, version = normalize_arxiv(reference)
    if arxiv_id:
        identity = {"type": "PAPER", "identity": f"arxiv:{arxiv_id}"}
        if version:
            identity["revision"] = version
        return identity
    repository = normalize_repository(reference)
    if repository:
        return {"type": "REPOSITORY", "identity": f"github:{repository}"}
    return None


def source_identity_key(identity: dict[str, Any]) -> str:
    return f"{identity.get('type', 'UNKNOWN')}:{identity.get('identity', 'UNKNOWN')}"


def canonical_identity(source_identities: list[dict[str, Any]], fallback: str) -> str:
    priority = {"DOI": 0, "PAPER": 1, "REPOSITORY": 2, "MANAGED_PRODUCT": 3, "OFFICIAL": 4}
    identities = sorted(
        source_identities,
        key=lambda item: (priority.get(item.get("type", ""), 99), item.get("identity", "")),
    )
    return identities[0]["identity"] if identities else fallback
