"""Synthetic, non-persistent input for Validation Result Contract tests."""

from __future__ import annotations

from typing import Any


def _source(source_id: str) -> dict[str, str]:
    return {
        "namespace": "dbio",
        "source_id": source_id,
        "version": "v0.1",
        "status": "DECLARED",
    }


def _reference(reference_id: str, source: str) -> dict[str, str]:
    return {
        "reference_id": reference_id,
        "reference_type": "ENTITY",
        "namespace": "dbio",
        "version": "v0.1",
        "source": source,
        "status": "DECLARED",
    }


def synthetic_entity() -> dict[str, Any]:
    """Return an in-memory fixture that is never registered as an Entity."""

    entity_id = "dbio://repository/synthetic-result-contract-fixture/v0.1"
    source_id = "registry/entities.yaml"
    return {
        "object_id": entity_id,
        "object_type": "ENTITY",
        "version": "v0.1",
        "source": _source(source_id),
        "status": "DECLARED",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "limitations": ["Synthetic result-contract fixture only."],
        "entity_id": entity_id,
        "entity_type": "repository",
        "owner_reference": _reference(
            "dbio://entity/synthetic-result-contract-owner/v0.1",
            source_id,
        ),
        "lifecycle_state": "PROPOSED",
        "source_reference": _reference(entity_id, source_id),
    }
