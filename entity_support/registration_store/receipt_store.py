"""Persist immutable success and failure registration receipts.

Agent-readable contract:
- Receipt storage records an outcome; Receipt is not Evidence Truth.
- Every receipt references one persisted Registration Record with matching status.
- A ``FAILED`` receipt requires an error reference and cannot be overwritten.
- This store has no delete/update operation and grants no Permission or activation.
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

from entity_support.registration_store.registration_store import RegistrationStore

RECEIPT_STORE_SCHEMA_VERSION = "0.1"
RECEIPT_STORE_KIND = "DigitalEntityRegistrationReceiptStore"
STORED_RECEIPT_FIELDS = (
    "registration_id",
    "receipt_id",
    "status",
    "timestamp",
    "error_reference",
)
STORED_RECEIPT_STATUSES = frozenset({"SUCCESS", "FAILED"})


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


def validate_stored_receipt(receipt: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = [field for field in STORED_RECEIPT_FIELDS if field not in receipt]
    extra = sorted(set(receipt) - set(STORED_RECEIPT_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    for field in ("registration_id", "receipt_id"):
        if not _is_non_empty_string(receipt.get(field)):
            errors.append(f"{field} must be a non-empty string")
    if not _is_timezone_aware_timestamp(receipt.get("timestamp")):
        errors.append("timestamp must be a timezone-aware ISO 8601 string")
    status = receipt.get("status")
    if status not in STORED_RECEIPT_STATUSES:
        errors.append("status must be SUCCESS or FAILED")
    error_reference = receipt.get("error_reference")
    if status == "SUCCESS" and error_reference is not None:
        errors.append("SUCCESS receipt requires error_reference=null")
    if status == "FAILED" and not _is_non_empty_string(error_reference):
        errors.append("FAILED receipt requires error_reference")
    if error_reference is not None and not _is_non_empty_string(error_reference):
        errors.append("error_reference must be null or a non-empty string")
    return errors


def build_stored_receipt(
    *,
    registration_id: str,
    receipt_id: str,
    status: str,
    timestamp: str,
    error_reference: str | None = None,
) -> dict[str, str | None]:
    receipt = {
        "registration_id": registration_id,
        "receipt_id": receipt_id,
        "status": status,
        "timestamp": timestamp,
        "error_reference": error_reference,
    }
    errors = validate_stored_receipt(receipt)
    if errors:
        raise ValueError("; ".join(errors))
    return receipt


def _empty_document() -> dict[str, object]:
    return {
        "schema_version": RECEIPT_STORE_SCHEMA_VERSION,
        "kind": RECEIPT_STORE_KIND,
        "receipt_records": [],
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
    """Serialize immutable receipt uniqueness checking and append."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class ReceiptStore:
    """Append-only Receipt Store linked to persisted Registration Records."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_document()
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read receipt store: {exc}") from exc
        if not isinstance(document, dict):
            raise ValueError("receipt store must contain one mapping")
        if document.get("schema_version") != RECEIPT_STORE_SCHEMA_VERSION:
            raise ValueError("receipt store schema_version is unsupported")
        if document.get("kind") != RECEIPT_STORE_KIND:
            raise ValueError("receipt store kind is unsupported")
        records = document.get("receipt_records")
        if not isinstance(records, list):
            raise ValueError("receipt_records must be a list")
        receipt_ids: set[str] = set()
        registration_ids: set[str] = set()
        for index, receipt in enumerate(records):
            if not isinstance(receipt, dict):
                raise ValueError(f"receipt_records[{index}] must be a mapping")
            errors = validate_stored_receipt(receipt)
            if errors:
                raise ValueError(f"receipt_records[{index}]: {'; '.join(errors)}")
            if receipt["receipt_id"] in receipt_ids:
                raise ValueError(f"duplicate receipt_id: {receipt['receipt_id']}")
            if receipt["registration_id"] in registration_ids:
                raise ValueError(
                    f"registration_id already has a receipt: {receipt['registration_id']}"
                )
            receipt_ids.add(receipt["receipt_id"])
            registration_ids.add(receipt["registration_id"])
        return document

    def initialize(self) -> None:
        with _exclusive_store_lock(self.path):
            if self.path.exists():
                self._read()
                return
            _atomic_write_json(self.path, _empty_document())

    def list_records(self) -> list[dict[str, Any]]:
        return deepcopy(self._read()["receipt_records"])

    def count(self) -> int:
        return len(self._read()["receipt_records"])

    def append(
        self,
        receipt: Mapping[str, Any],
        *,
        registration_store: RegistrationStore,
    ) -> dict[str, Any]:
        errors = validate_stored_receipt(receipt)
        if errors:
            raise ValueError("; ".join(errors))
        registration = registration_store.get(str(receipt["registration_id"]))
        if registration is None:
            raise ValueError("receipt requires persisted Registration Record")
        if registration["status"] != receipt["status"]:
            raise ValueError("receipt status must match Registration Record")

        with _exclusive_store_lock(self.path):
            document = self._read()
            if any(
                item["receipt_id"] == receipt["receipt_id"]
                for item in document["receipt_records"]
            ):
                raise ValueError(f"duplicate receipt_id: {receipt['receipt_id']}")
            if any(
                item["registration_id"] == receipt["registration_id"]
                for item in document["receipt_records"]
            ):
                raise ValueError(
                    f"registration_id already has a receipt: {receipt['registration_id']}"
                )
            stored = deepcopy(dict(receipt))
            document["receipt_records"].append(stored)
            _atomic_write_json(self.path, document)
        return deepcopy(stored)


__all__ = [
    "RECEIPT_STORE_KIND",
    "RECEIPT_STORE_SCHEMA_VERSION",
    "STORED_RECEIPT_FIELDS",
    "STORED_RECEIPT_STATUSES",
    "ReceiptStore",
    "build_stored_receipt",
    "validate_stored_receipt",
]
