"""Canonical JSON and SHA-256 identities for discovery artifacts."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def candidate_fingerprint(candidate: dict[str, Any]) -> str:
    payload = {
        "normalized_name": candidate["normalized_name"],
        "source_identities": sorted(
            candidate.get("source_identities", []),
            key=lambda item: (item.get("type", ""), item.get("identity", "")),
        ),
        "delivery_type": candidate.get("delivery_type", "UNKNOWN"),
        "capability_group": candidate.get("capability_group", "OTHER_OR_UNCLASSIFIED"),
        "product_boundary": candidate.get("product_boundary", "INDEPENDENT_DELIVERABLE"),
    }
    return sha256_json(payload)


def registry_digest(registry: dict[str, Any]) -> str:
    payload = copy.deepcopy(registry)
    payload.pop("current_registry_digest", None)
    return sha256_json(payload)
