"""Persist append-only Authorization state records in a caller-selected registry.

Agent-readable contract:
- The configured file is canonical only for this bounded authorization store.
- State records are append-only; one ``authorization_id`` may have a validated
  ``PENDING -> AUTHORIZED|REJECTED`` or ``AUTHORIZED -> REVOKED`` history.
- Concurrent writers are serialized with a sidecar file lock.
- Registry insertion does not issue Permission, create Entity, or execute registration.
- No default live DBOS path is selected; callers must explicitly provide a path.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

import fcntl

from entity_support.authorization.authorization_record import (
    validate_authorization_record,
)

AUTHORIZATION_REGISTRY_SCHEMA_VERSION = "0.1"
AUTHORIZATION_REGISTRY_KIND = "DigitalEntityRegistrationAuthorizationRegistry"
AUTHORIZATION_STATUS_TRANSITIONS = {
    "PENDING": frozenset({"AUTHORIZED", "REJECTED"}),
    "AUTHORIZED": frozenset({"REVOKED"}),
    "REJECTED": frozenset(),
    "REVOKED": frozenset(),
}


def _empty_document() -> dict[str, object]:
    return {
        "schema_version": AUTHORIZATION_REGISTRY_SCHEMA_VERSION,
        "kind": AUTHORIZATION_REGISTRY_KIND,
        "authorization_records": [],
    }


def _atomic_write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


@contextmanager
def _exclusive_store_lock(path: Path):
    """Serialize one store's read-check-write operation across processes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _parse_timestamp(value: object) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _validate_transition(
    previous: Mapping[str, Any], current: Mapping[str, Any]
) -> list[str]:
    """Validate an immutable authorization status-history transition."""

    errors: list[str] = []
    allowed = AUTHORIZATION_STATUS_TRANSITIONS[str(previous["status"])]
    if current["status"] not in allowed:
        errors.append(
            f"invalid authorization transition: {previous['status']} -> "
            f"{current['status']}"
        )
    if _parse_timestamp(current["created_at"]) <= _parse_timestamp(
        previous["created_at"]
    ):
        errors.append("authorization transition created_at must increase")
    for field in ("candidate_id", "target_entity_type"):
        if current[field] != previous[field]:
            errors.append(f"authorization transition cannot change {field}")
    for field in ("decision_reference", "scope", "issuer_reference", "expires_at"):
        prior_value = previous[field]
        if prior_value is not None and current[field] != prior_value:
            errors.append(f"authorization transition cannot change established {field}")
    return errors


class AuthorizationRegistry:
    """Append-only Authorization Record store with explicit path ownership."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_document()
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read authorization registry: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("authorization registry must contain one mapping")
        if document.get("schema_version") != AUTHORIZATION_REGISTRY_SCHEMA_VERSION:
            raise ValueError("authorization registry schema_version is unsupported")
        if document.get("kind") != AUTHORIZATION_REGISTRY_KIND:
            raise ValueError("authorization registry kind is unsupported")
        records = document.get("authorization_records")
        if not isinstance(records, list):
            raise ValueError("authorization_records must be a list")
        latest: dict[str, Mapping[str, Any]] = {}
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"authorization_records[{index}] must be a mapping")
            errors = validate_authorization_record(record)
            if errors:
                raise ValueError(f"authorization_records[{index}]: {'; '.join(errors)}")
            authorization_id = record["authorization_id"]
            previous = latest.get(authorization_id)
            if previous is not None:
                transition_errors = _validate_transition(previous, record)
                if transition_errors:
                    raise ValueError(
                        f"authorization_records[{index}]: "
                        f"{'; '.join(transition_errors)}"
                    )
            latest[authorization_id] = record
        return document

    def initialize(self) -> None:
        """Create an empty registry only when the explicit path does not exist."""

        with _exclusive_store_lock(self.path):
            if self.path.exists():
                self._read()
                return
            _atomic_write_json(self.path, _empty_document())

    def list_records(self) -> list[dict[str, Any]]:
        return deepcopy(self._read()["authorization_records"])

    def count(self) -> int:
        return len(self._read()["authorization_records"])

    def authorization_count(self) -> int:
        """Return distinct authorization identities, not state-history rows."""

        return len(
            {
                record["authorization_id"]
                for record in self._read()["authorization_records"]
            }
        )

    def get(self, authorization_id: str) -> dict[str, Any] | None:
        for record in reversed(self._read()["authorization_records"]):
            if record["authorization_id"] == authorization_id:
                return deepcopy(record)
        return None

    @contextmanager
    def hold_latest(self, authorization_id: str):
        """Hold the latest record stable across one registration transaction.

        RegistrationStore uses this guard so an Authorization cannot be revoked
        between the effectiveness check and the successful registration append.
        """

        with _exclusive_store_lock(self.path):
            record = self.get(authorization_id)
            if record is None:
                raise ValueError(f"unknown authorization_id: {authorization_id}")
            yield record

    def append(self, record: Mapping[str, Any]) -> dict[str, Any]:
        errors = validate_authorization_record(record)
        if errors:
            raise ValueError("; ".join(errors))
        with _exclusive_store_lock(self.path):
            document = self._read()
            prior_records = [
                item
                for item in document["authorization_records"]
                if item["authorization_id"] == record["authorization_id"]
            ]
            if prior_records:
                transition_errors = _validate_transition(prior_records[-1], record)
                if transition_errors:
                    raise ValueError("; ".join(transition_errors))
            stored = deepcopy(dict(record))
            document["authorization_records"].append(stored)
            _atomic_write_json(self.path, document)
        return deepcopy(stored)

__all__ = [
    "AUTHORIZATION_REGISTRY_KIND",
    "AUTHORIZATION_REGISTRY_SCHEMA_VERSION",
    "AUTHORIZATION_STATUS_TRANSITIONS",
    "AuthorizationRegistry",
]
