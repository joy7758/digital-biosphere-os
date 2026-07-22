"""Integrity-checked, offline OpenTelemetry reference artifacts.

The artifacts in :mod:`dbos.telemetry_admission.profiles` are immutable
snapshots of human-adopted DBA contracts.  Runtime network resolution is not
implemented: every read verifies the exact byte digest before parsing.
"""

from __future__ import annotations

import hashlib
import json
from importlib import resources
from typing import Any

import yaml

from .contracts import (
    OTEL_SCHEMA_ARTIFACT_DIGEST,
    SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST,
    SCHEMA_RESOURCE_RESULT_SCHEMA_DIGEST,
    SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
    SEMANTIC_MAPPING_CATALOG_DIGEST,
    SEMANTIC_RESULT_SCHEMA_DIGEST,
)


SEMANTIC_MAPPING_FILENAME = "opentelemetry-semantic-mapping.v0.1.json"
SEMANTIC_CONFORMANCE_FILENAME = "opentelemetry-semantic-conformance-cases.v0.1.json"
SCHEMA_RESOURCE_CONFORMANCE_FILENAME = (
    "opentelemetry-schema-resource-conformance-cases.v0.1.json"
)
SEMANTIC_RESULT_SCHEMA_FILENAME = (
    "opentelemetry-semantic-conformance-result-set.schema.v0.1.json"
)
SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME = (
    "opentelemetry-schema-resource-conformance-result-set.schema.v0.1.json"
)
OTEL_SCHEMA_FILENAME = "opentelemetry-schema-1.43.0.yaml"

REFERENCE_ARTIFACT_DIGESTS = {
    SEMANTIC_MAPPING_FILENAME: SEMANTIC_MAPPING_CATALOG_DIGEST,
    SEMANTIC_CONFORMANCE_FILENAME: SEMANTIC_CONFORMANCE_CATALOG_DIGEST,
    SCHEMA_RESOURCE_CONFORMANCE_FILENAME: (SCHEMA_RESOURCE_CONFORMANCE_CATALOG_DIGEST),
    SEMANTIC_RESULT_SCHEMA_FILENAME: SEMANTIC_RESULT_SCHEMA_DIGEST,
    SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME: SCHEMA_RESOURCE_RESULT_SCHEMA_DIGEST,
    OTEL_SCHEMA_FILENAME: OTEL_SCHEMA_ARTIFACT_DIGEST,
}


class ReferenceIntegrityError(RuntimeError):
    """Raised when a vendored contract is missing, drifted, or malformed."""

    def __init__(self, reason_code: str) -> None:
        self.reason_code = reason_code
        super().__init__(reason_code)


def sha256_digest(value: bytes) -> str:
    """Return the protocol digest form for immutable artifact bytes."""

    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def read_pinned_bytes(
    filename: str,
    *,
    expected_digest: str | None = None,
) -> bytes:
    """Read a package artifact and fail closed unless its bytes are exact."""

    expected = expected_digest or REFERENCE_ARTIFACT_DIGESTS.get(filename)
    if expected is None:
        raise ReferenceIntegrityError("TA_REFERENCE_NOT_ALLOWLISTED")
    try:
        value = (
            resources.files("dbos.telemetry_admission.profiles")
            .joinpath(filename)
            .read_bytes()
        )
    except (FileNotFoundError, ModuleNotFoundError, OSError) as exc:
        raise ReferenceIntegrityError("TA_REFERENCE_UNAVAILABLE") from exc
    if sha256_digest(value) != expected:
        raise ReferenceIntegrityError("TA_REFERENCE_DIGEST_MISMATCH")
    return value


def read_pinned_json(
    filename: str,
    *,
    expected_digest: str | None = None,
) -> dict[str, Any]:
    """Return an exact JSON object after digest and shape validation."""

    value = read_pinned_bytes(filename, expected_digest=expected_digest)
    try:
        parsed = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReferenceIntegrityError("TA_REFERENCE_PARSE_FAILED") from exc
    if not isinstance(parsed, dict):
        raise ReferenceIntegrityError("TA_REFERENCE_SHAPE_INVALID")
    return parsed


def read_pinned_yaml(
    filename: str,
    *,
    expected_digest: str | None = None,
) -> dict[str, Any]:
    """Return an exact YAML object using the non-executing safe loader."""

    value = read_pinned_bytes(filename, expected_digest=expected_digest)
    try:
        parsed = yaml.safe_load(value)
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ReferenceIntegrityError("TA_REFERENCE_PARSE_FAILED") from exc
    if not isinstance(parsed, dict):
        raise ReferenceIntegrityError("TA_REFERENCE_SHAPE_INVALID")
    return parsed


__all__ = [
    "OTEL_SCHEMA_FILENAME",
    "REFERENCE_ARTIFACT_DIGESTS",
    "ReferenceIntegrityError",
    "SCHEMA_RESOURCE_CONFORMANCE_FILENAME",
    "SCHEMA_RESOURCE_RESULT_SCHEMA_FILENAME",
    "SEMANTIC_CONFORMANCE_FILENAME",
    "SEMANTIC_MAPPING_FILENAME",
    "SEMANTIC_RESULT_SCHEMA_FILENAME",
    "read_pinned_bytes",
    "read_pinned_json",
    "read_pinned_yaml",
    "sha256_digest",
]
