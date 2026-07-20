"""Persist registration outcomes with Authorization and replay checks.

Agent-readable contract:
- A Registration Record stores an outcome; it does not activate an Entity.
- ``SUCCESS`` requires one effective canonical Authorization Record.
- One ``authorization_id`` can produce at most one successful registration,
  including when concurrent processes attempt the same authorization.
- ``FAILED`` records keep the failed attempt and cannot claim an ``entity_id``.
- This store never writes ``registry/entities.yaml`` or creates Agent/Runtime/Permission.
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
from entity_support.authorization.authorization_registry import AuthorizationRegistry
from entity_support.authorization.authorization_validator import (
    validate_authorization_for_registration,
)
from entity_support.registration.registration_validator import derive_entity_id

REGISTRATION_STORE_SCHEMA_VERSION = "0.1"
REGISTRATION_STORE_KIND = "DigitalEntityRegistrationRecordStore"
REGISTRATION_RECORD_FIELDS = (
    "registration_id",
    "entity_id",
    "candidate_reference",
    "authorization_reference",
    "registered_at",
    "status",
)
REGISTRATION_STATUSES = frozenset({"SUCCESS", "FAILED"})


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_timezone_aware_timestamp(value: object) -> bool:
    if not _is_non_empty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate_registration_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [field for field in REGISTRATION_RECORD_FIELDS if field not in record]
    extra = sorted(set(record) - set(REGISTRATION_RECORD_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in (
        "registration_id",
        "candidate_reference",
        "authorization_reference",
    ):
        if not _is_non_empty_string(record.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if not _is_timezone_aware_timestamp(record.get("registered_at")):
        errors.append("registered_at must be a timezone-aware ISO 8601 string")
    status = record.get("status")
    if status not in REGISTRATION_STATUSES:
        errors.append("status must be SUCCESS or FAILED")
    if status == "SUCCESS" and not _is_non_empty_string(record.get("entity_id")):
        errors.append("SUCCESS requires entity_id")
    if status == "FAILED" and record.get("entity_id") is not None:
        errors.append("FAILED must not claim entity_id")
    return errors


def build_registration_record(
    *,
    registration_id: str,
    entity_id: str | None,
    candidate_reference: str,
    authorization_reference: str,
    registered_at: str,
    status: str,
) -> dict[str, str | None]:
    record = {
        "registration_id": registration_id,
        "entity_id": entity_id,
        "candidate_reference": candidate_reference,
        "authorization_reference": authorization_reference,
        "registered_at": registered_at,
        "status": status,
    }
    errors = validate_registration_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def _empty_document() -> dict[str, object]:
    return {
        "schema_version": REGISTRATION_STORE_SCHEMA_VERSION,
        "kind": REGISTRATION_STORE_KIND,
        "registration_records": [],
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
    """Serialize replay checking and append as one store operation."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class RegistrationStore:
    """Append-only Registration Record store with replay protection."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_document()
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read registration store: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("registration store must contain one mapping")
        if document.get("schema_version") != REGISTRATION_STORE_SCHEMA_VERSION:
            raise ValueError("registration store schema_version is unsupported")
        if document.get("kind") != REGISTRATION_STORE_KIND:
            raise ValueError("registration store kind is unsupported")
        records = document.get("registration_records")
        if not isinstance(records, list):
            raise ValueError("registration_records must be a list")
        seen: set[str] = set()
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(f"registration_records[{index}] must be a mapping")
            errors = validate_registration_record(record)
            if errors:
                raise ValueError(f"registration_records[{index}]: {'; '.join(errors)}")
            registration_id = record["registration_id"]
            if registration_id in seen:
                raise ValueError(f"duplicate registration_id: {registration_id}")
            seen.add(registration_id)
        return document

    def initialize(self) -> None:
        with _exclusive_store_lock(self.path):
            if self.path.exists():
                self._read()
                return
            _atomic_write_json(self.path, _empty_document())

    def list_records(self) -> list[dict[str, Any]]:
        return deepcopy(self._read()["registration_records"])

    def count(self) -> int:
        return len(self._read()["registration_records"])

    def get(self, registration_id: str) -> dict[str, Any] | None:
        for record in self._read()["registration_records"]:
            if record["registration_id"] == registration_id:
                return deepcopy(record)
        return None

    def successful_count(self) -> int:
        return sum(
            record["status"] == "SUCCESS" for record in self._read()["registration_records"]
        )

    def append(
        self,
        record: Mapping[str, Any],
        *,
        authorization_registry: AuthorizationRegistry,
    ) -> dict[str, Any]:
        errors = validate_registration_record(record)
        if errors:
            raise ValueError("; ".join(errors))
        authorization_id = str(record["authorization_reference"])
        authorization = authorization_registry.get(authorization_id)
        if authorization is None:
            raise ValueError("registration requires canonical Authorization Record")
        with authorization_registry.hold_latest(authorization_id) as authorization:
            authorization_errors = validate_authorization_record(authorization)
            if authorization_errors:
                raise ValueError("; ".join(authorization_errors))
            if authorization["candidate_id"] != record["candidate_reference"]:
                raise ValueError("candidate_reference must match Authorization Record")

            with _exclusive_store_lock(self.path):
                document = self._read()
                if any(
                    item["registration_id"] == record["registration_id"]
                    for item in document["registration_records"]
                ):
                    raise ValueError(
                        f"duplicate registration_id: {record['registration_id']}"
                    )

                if record["status"] == "SUCCESS":
                    effectiveness_errors = validate_authorization_for_registration(
                        authorization,
                        at_time=str(record["registered_at"]),
                    )
                    if effectiveness_errors:
                        raise ValueError("; ".join(effectiveness_errors))
                    if any(
                        item["status"] == "SUCCESS"
                        and item["authorization_reference"]
                        == record["authorization_reference"]
                        for item in document["registration_records"]
                    ):
                        raise ValueError(
                            "authorization_id already produced a successful registration"
                        )
                    expected_entity_id = derive_entity_id(
                        str(authorization["candidate_id"]),
                        str(authorization["authorization_id"]),
                    )
                    if record["entity_id"] != expected_entity_id:
                        raise ValueError(
                            "entity_id lacks candidate/authorization continuity"
                        )

                stored = deepcopy(dict(record))
                document["registration_records"].append(stored)
                _atomic_write_json(self.path, document)
        return deepcopy(stored)


__all__ = [
    "REGISTRATION_RECORD_FIELDS",
    "REGISTRATION_STATUSES",
    "REGISTRATION_STORE_KIND",
    "REGISTRATION_STORE_SCHEMA_VERSION",
    "RegistrationStore",
    "build_registration_record",
    "validate_registration_record",
]
