"""Crash-conscious SQLite reference store for telemetry admission v0.1.

This is a single-host conformance backend. It provides no network endpoint,
multi-tenant isolation, HA, production deployment, Evidence store, identity
store, Permission store, Agent, Runtime, or SAEE integration.

The public surface is append/read/backup/restore only. SQL triggers reject
UPDATE and DELETE for every ledger table. A result is returned only after the
transaction that contains its envelope stub, lifecycle, receipt, and records
has committed.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
import tempfile
import uuid
from collections.abc import Callable, Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .contracts import (
    ADMISSION_POLICY_VERSION,
    ADMISSION_RECORD_FIELDS,
    ADMISSION_STATES,
    BUSY_TIMEOUT_MILLISECONDS,
    DIGEST_PATTERN,
    FINGERPRINT_VERSION,
    MAX_LIMITATIONS,
    MAX_REASON_CODES,
    OPAQUE_REFERENCE_PATTERN,
    REASON_CODE_SET,
    STORE_SCHEMA_VERSION,
    VALIDATOR_VERSION,
    order_reason_codes,
)
from .models import AdmissionResult, TelemetryAdmissionError, ValidationDecision


MIGRATION_VERSION = "0001"
MIGRATION_RESOURCE = Path(__file__).parent / "migrations" / "0001_initial.sql"
PRIOR_COMPATIBLE_VERSION = "0000"
PRIOR_COMPATIBLE_FIXTURE_RESOURCE = (
    Path(__file__).parent / "migrations" / "0000_prior_compatible.fixture.sql"
)
COMPATIBILITY_MIGRATION_VERSION = "0001-compat"
COMPATIBILITY_MIGRATION_RESOURCE = (
    Path(__file__).parent / "migrations" / "0001_compatibility.sql"
)
DATABASE_APPLICATION_ID = 0x544D4149  # ASCII "TMAI"
DATABASE_USER_VERSION = 1
ACTOR_REFERENCE = "dbos.telemetry_admission:0.1.0"

EXPECTED_TABLE_COLUMNS = {
    "schema_migrations": ("version", "checksum", "applied_at"),
    "observation_envelopes": (
        "observation_id",
        "envelope_json",
        "source_digest",
        "persistence_class",
        "comparison_fingerprint",
        "fingerprint_version",
        "payload_digest",
        "received_at",
    ),
    "admission_lifecycles": (
        "admission_id",
        "observation_reference",
        "source_digest",
        "idempotency_reference",
        "created_at",
    ),
    "admission_records": (
        "admission_record_id",
        "admission_id",
        "observation_reference",
        "sequence",
        "previous_record_reference",
        "state",
        "policy_version",
        "validator_version",
        "source_digest",
        "idempotency_reference",
        "intake_receipt_reference",
        "duplicate_reference",
        "comparison_fingerprint",
        "fingerprint_version",
        "accepted_item_count",
        "rejected_item_count",
        "reason_codes_json",
        "limitations_json",
        "recorded_at",
        "actor_reference",
        "record_digest",
    ),
    "intake_receipts": (
        "intake_receipt_reference",
        "admission_id",
        "source_digest",
        "issued_at",
    ),
    "untrusted_idempotency_hints": (
        "idempotency_reference",
        "admission_id",
        "comparison_fingerprint",
        "recorded_at",
    ),
    "backup_manifests": (
        "backup_id",
        "schema_version",
        "database_sha256",
        "record_chain_digest",
        "manifest_digest",
        "counts_json",
        "created_at",
    ),
}
EXPECTED_INDEXES = frozenset(
    {
        "idx_observation_fingerprint",
        "idx_admission_records_lifecycle",
        "idx_idempotency_hint",
    }
)
EXPECTED_APPEND_ONLY_TRIGGERS = frozenset(
    f"{table}_{operation}"
    for table in EXPECTED_TABLE_COLUMNS
    for operation in ("no_update", "no_delete")
)

FaultInjector = Callable[[str], None]
Clock = Callable[[], str]
IdFactory = Callable[[str], str]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _default_id_factory(kind: str) -> str:
    return f"ta:{kind}:{uuid.uuid4().hex}"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _sha256_json(value: object) -> str:
    return _sha256_bytes(_canonical_json(value).encode("utf-8"))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return f"sha256:{digest.hexdigest()}"


def _migration_sql() -> str:
    try:
        return MIGRATION_RESOURCE.read_text(encoding="utf-8")
    except OSError as exc:
        raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc


def migration_checksum() -> str:
    return _sha256_bytes(_migration_sql().encode("utf-8"))


def prior_compatible_fixture_checksum() -> str:
    try:
        content = PRIOR_COMPATIBLE_FIXTURE_RESOURCE.read_bytes()
    except OSError as exc:
        raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
    return _sha256_bytes(content)


def compatibility_migration_checksum() -> str:
    try:
        content = COMPATIBILITY_MIGRATION_RESOURCE.read_bytes()
    except OSError as exc:
        raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
    return _sha256_bytes(content)


DIRECT_MIGRATION_HISTORY = ((MIGRATION_VERSION, migration_checksum()),)
COMPATIBLE_MIGRATION_HISTORY = (
    (PRIOR_COMPATIBLE_VERSION, prior_compatible_fixture_checksum()),
    (COMPATIBILITY_MIGRATION_VERSION, compatibility_migration_checksum()),
)
PRIOR_MIGRATION_HISTORY = (
    (PRIOR_COMPATIBLE_VERSION, prior_compatible_fixture_checksum()),
)


def _split_sql_script(script: str) -> tuple[str, ...]:
    statements: list[str] = []
    buffer = ""
    for line in script.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement:
                statements.append(statement)
            buffer = ""
    if buffer.strip():
        raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
    return tuple(statements)


def _validate_explicit_path(path: str | Path, *, must_not_exist: bool = False) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or ".." in candidate.parts:
        raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    if (
        not candidate.parent.exists()
        or not candidate.parent.is_dir()
        or candidate.parent.is_symlink()
    ):
        raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    if candidate.is_symlink():
        raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    # Reject caller-controlled intermediate symlinks as well as a symlink at
    # the final parent.  A top-level platform alias such as macOS /var is
    # resolved below, but any deeper redirect can escape the caller-selected
    # store directory and therefore fails closed.
    anchor = Path(candidate.anchor)
    for ancestor in candidate.parents:
        if ancestor in {anchor, anchor / ancestor.name}:
            continue
        if ancestor.is_symlink():
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    if must_not_exist and candidate.exists():
        raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    if candidate.exists():
        if not candidate.is_file():
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
        mode = stat.S_IMODE(candidate.stat().st_mode)
        if mode & 0o077:
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
    return candidate.resolve(strict=False)


def _secure_create(path: Path) -> None:
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    os.close(descriptor)


def _secure_database_files(path: Path) -> None:
    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(candidate, flags)
        except FileNotFoundError:
            # SQLite may unlink transient WAL/SHM files between operations.
            continue
        except OSError as exc:
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE")
            os.fchmod(descriptor, 0o600)
        finally:
            os.close(descriptor)


def _safe_reference(value: str) -> bool:
    return OPAQUE_REFERENCE_PATTERN.fullmatch(value) is not None


def _fingerprint(envelope: Mapping[str, Any]) -> str:
    resource = envelope["resource"]
    if not isinstance(resource, Mapping):
        raise TelemetryAdmissionError("TA_SHAPE_INVALID")
    material = {
        "fingerprint_version": FINGERPRINT_VERSION,
        "source_digest": envelope["source_digest"],
        "signal_type": envelope["signal_type"],
        "producer_reference": envelope["producer_reference"],
        "transport_source_reference": envelope["transport_source_reference"],
        "resource_reference": resource["reference"],
        "signal_reference": envelope["signal_reference"],
    }
    return _sha256_json(material)


def _fallback_digest(admission_id: str) -> str:
    # This digest describes a generated rejection stub, not untrusted bytes.
    return _sha256_bytes(f"rejection-stub\0{admission_id}".encode("utf-8"))


def _default_counts(state: str) -> tuple[int, int]:
    if state == "ACCEPTED_AS_MATERIAL":
        return 1, 0
    if state == "PARTIAL":
        return 1, 1
    if state == "REJECTED":
        return 0, 1
    return 0, 0


class SQLiteTelemetryAdmissionStore:
    """Append-only SQLite reference backend for one explicit local path."""

    def __init__(
        self,
        path: str | Path,
        *,
        busy_timeout_ms: int = BUSY_TIMEOUT_MILLISECONDS,
        clock: Clock = _utc_now,
        id_factory: IdFactory = _default_id_factory,
        fault_injector: FaultInjector | None = None,
    ) -> None:
        if not isinstance(busy_timeout_ms, int) or not 1 <= busy_timeout_ms <= 60_000:
            raise ValueError("busy_timeout_ms must be between 1 and 60000")
        self.path = _validate_explicit_path(path)
        self.busy_timeout_ms = busy_timeout_ms
        self._clock = clock
        self._id_factory = id_factory
        self._fault_injector = fault_injector

    def _connect(self) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(
                self.path,
                timeout=self.busy_timeout_ms / 1000,
                isolation_level=None,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms}")
            connection.execute("PRAGMA synchronous=FULL")
            return connection
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc

    def initialize(self) -> None:
        """Create or verify the exact v0.1 store without implicit live paths."""

        if not self.path.exists():
            _secure_create(self.path)
        connection = self._connect()
        try:
            try:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                if not tables:
                    self._apply_initial_migration(connection)
                elif "schema_migrations" not in tables:
                    raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
                self._verify_migration(connection)
                journal_mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[
                    0
                ]
                if str(journal_mode).lower() != "wal":
                    raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            except sqlite3.OperationalError as exc:
                raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        finally:
            connection.close()
            _secure_database_files(self.path)

    def _apply_initial_migration(self, connection: sqlite3.Connection) -> None:
        checksum = migration_checksum()
        try:
            connection.execute("BEGIN IMMEDIATE")
            for statement in _split_sql_script(_migration_sql()):
                connection.execute(statement)
                self._fault("after_migration_statement")
            connection.execute(
                "INSERT INTO schema_migrations(version, checksum, applied_at) VALUES (?, ?, ?)",
                (MIGRATION_VERSION, checksum, self._clock()),
            )
            connection.execute(f"PRAGMA application_id={DATABASE_APPLICATION_ID}")
            connection.execute(f"PRAGMA user_version={DATABASE_USER_VERSION}")
            connection.commit()
        except (sqlite3.Error, TelemetryAdmissionError, RuntimeError) as exc:
            if connection.in_transaction:
                connection.rollback()
            if isinstance(exc, TelemetryAdmissionError):
                raise
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc

    @staticmethod
    def _verify_migration(connection: sqlite3.Connection) -> None:
        try:
            application_id = connection.execute("PRAGMA application_id").fetchone()[0]
            user_version = connection.execute("PRAGMA user_version").fetchone()[0]
            rows = connection.execute(
                "SELECT version, checksum FROM schema_migrations ORDER BY version"
            ).fetchall()
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
        if application_id != DATABASE_APPLICATION_ID:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        if user_version != DATABASE_USER_VERSION:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        history = tuple((str(row["version"]), str(row["checksum"])) for row in rows)
        if history not in {DIRECT_MIGRATION_HISTORY, COMPATIBLE_MIGRATION_HISTORY}:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        SQLiteTelemetryAdmissionStore._verify_schema_shape(connection)

    @staticmethod
    def _verify_schema_shape(
        connection: sqlite3.Connection,
        *,
        expected_indexes: frozenset[str] = EXPECTED_INDEXES,
    ) -> None:
        """Bind the migration row to the exact tables, columns, indexes, and triggers."""

        try:
            objects = connection.execute(
                "SELECT type,name,sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
            ).fetchall()
            tables = {str(row["name"]) for row in objects if row["type"] == "table"}
            indexes = {
                str(row["name"])
                for row in objects
                if row["type"] == "index" and row["sql"] is not None
            }
            triggers = {str(row["name"]) for row in objects if row["type"] == "trigger"}
            if tables != set(EXPECTED_TABLE_COLUMNS):
                raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            if indexes != expected_indexes:
                raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            if triggers != EXPECTED_APPEND_ONLY_TRIGGERS:
                raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            for table, expected_columns in EXPECTED_TABLE_COLUMNS.items():
                columns = tuple(
                    str(row["name"])
                    for row in connection.execute(f"PRAGMA table_info({table})")
                )
                if columns != expected_columns:
                    raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc

    def migration_preflight(self) -> dict[str, Any]:
        """Classify the store without mutating or silently migrating it."""

        connection = self._connect()
        try:
            application_id = int(
                connection.execute("PRAGMA application_id").fetchone()[0]
            )
            user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            rows = connection.execute(
                "SELECT version,checksum FROM schema_migrations ORDER BY version"
            ).fetchall()
            history = tuple((str(row["version"]), str(row["checksum"])) for row in rows)
            if (
                application_id == DATABASE_APPLICATION_ID
                and user_version == DATABASE_USER_VERSION
                and history in {DIRECT_MIGRATION_HISTORY, COMPATIBLE_MIGRATION_HISTORY}
            ):
                self._verify_schema_shape(connection)
                classification = "CURRENT"
            elif (
                application_id == DATABASE_APPLICATION_ID
                and user_version == 0
                and history == PRIOR_MIGRATION_HISTORY
            ):
                self._verify_schema_shape(
                    connection,
                    expected_indexes=EXPECTED_INDEXES
                    - frozenset({"idx_observation_fingerprint"}),
                )
                classification = "COMPATIBLE_MIGRATION_REQUIRED"
            else:
                classification = "BREAKING_OR_UNKNOWN_BLOCKED"
        except (sqlite3.Error, TelemetryAdmissionError):
            classification = "BREAKING_OR_UNKNOWN_BLOCKED"
            history = ()
            user_version = -1
        finally:
            connection.close()
        return {
            "classification": classification,
            "user_version": user_version,
            "migration_history": [
                {"version": version, "checksum": checksum}
                for version, checksum in history
            ],
            "mutation_performed": False,
        }

    def migrate_compatible(self, backup_path: str | Path) -> dict[str, Any]:
        """Backup, dry-run, and explicitly migrate the sole known prior fixture."""

        preflight = self.migration_preflight()
        if preflight["classification"] != "COMPATIBLE_MIGRATION_REQUIRED":
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        backup = _validate_explicit_path(backup_path, must_not_exist=True)
        _secure_create(backup)
        source = self._connect()
        target = sqlite3.connect(backup, isolation_level=None)
        try:
            source.backup(target)
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        finally:
            target.close()
            source.close()
            _secure_database_files(backup)
        backup_sha256 = _file_sha256(backup)

        with tempfile.TemporaryDirectory(prefix="dbos-ta-migration-dry-run-") as temp:
            dry_run_path = Path(temp) / "dry-run.sqlite3"
            _secure_create(dry_run_path)
            backup_connection = sqlite3.connect(
                f"file:{backup}?mode=ro", uri=True, isolation_level=None
            )
            dry_run_connection = sqlite3.connect(dry_run_path, isolation_level=None)
            dry_run_connection.row_factory = sqlite3.Row
            try:
                backup_connection.backup(dry_run_connection)
                self._apply_compatibility_migration(
                    dry_run_connection, invoke_faults=False
                )
                self._verify_migration(dry_run_connection)
            finally:
                dry_run_connection.close()
                backup_connection.close()

        connection = self._connect()
        try:
            self._apply_compatibility_migration(connection, invoke_faults=True)
            self._verify_migration(connection)
        finally:
            connection.close()
            _secure_database_files(self.path)
        if _file_sha256(backup) != backup_sha256:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        return {
            "status": "MIGRATED",
            "from_version": PRIOR_COMPATIBLE_VERSION,
            "to_version": MIGRATION_VERSION,
            "backup_sha256": backup_sha256,
            "backup_immutable": True,
            "dry_run": "PASS",
            "post_validation": "PASS",
            "migration_checksum": compatibility_migration_checksum(),
        }

    def _apply_compatibility_migration(
        self, connection: sqlite3.Connection, *, invoke_faults: bool
    ) -> None:
        try:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("BEGIN IMMEDIATE")
            script = COMPATIBILITY_MIGRATION_RESOURCE.read_text(encoding="utf-8")
            for statement in _split_sql_script(script):
                connection.execute(statement)
                if invoke_faults:
                    self._fault("after_compatibility_migration_statement")
            connection.execute(
                "INSERT INTO schema_migrations(version,checksum,applied_at) "
                "VALUES (?,?,?)",
                (
                    COMPATIBILITY_MIGRATION_VERSION,
                    compatibility_migration_checksum(),
                    self._clock(),
                ),
            )
            connection.execute(f"PRAGMA user_version={DATABASE_USER_VERSION}")
            connection.commit()
        except (OSError, RuntimeError, sqlite3.Error) as exc:
            if connection.in_transaction:
                connection.rollback()
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc

    @staticmethod
    def _applied_migration_checksums(
        connection: sqlite3.Connection,
    ) -> dict[str, str]:
        return {
            str(row["version"]): str(row["checksum"])
            for row in connection.execute(
                "SELECT version,checksum FROM schema_migrations ORDER BY version"
            )
        }

    def _fault(self, point: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(point)

    def record_decision(
        self,
        decision: ValidationDecision,
        *,
        admission_id: str | None = None,
        claimed_intake_receipt_reference: str | None = None,
        accepted_item_count: int | None = None,
        rejected_item_count: int | None = None,
    ) -> AdmissionResult:
        """Commit one decision and return acknowledgement only after commit."""

        self._validate_decision(decision)
        self.initialize()
        connection = self._connect()
        try:
            self._fault("before_transaction")
            connection.execute("BEGIN IMMEDIATE")
            self._verify_migration(connection)
            result = self._record_in_transaction(
                connection,
                decision,
                admission_id=admission_id,
                claimed_receipt=claimed_intake_receipt_reference,
                accepted_item_count=accepted_item_count,
                rejected_item_count=rejected_item_count,
            )
            self._fault("before_commit")
            connection.commit()
            self._fault("after_commit")
        except TelemetryAdmissionError:
            if connection.in_transaction:
                connection.rollback()
            raise
        except (sqlite3.Error, OSError, RuntimeError, ValueError) as exc:
            if connection.in_transaction:
                connection.rollback()
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        finally:
            connection.close()
            _secure_database_files(self.path)
        return result

    @staticmethod
    def _validate_decision(decision: object) -> None:
        """Reject forged validator output before it reaches persistence.

        ``ValidationDecision`` is intentionally agent-readable and public, so
        its Python type is not an authority token.  The store revalidates every
        accepted/partial/unknown normalized envelope and permits a content-free
        rejection stub only when it cannot create an acceptance effect.
        """

        if not isinstance(decision, ValidationDecision):
            raise TelemetryAdmissionError("TA_SHAPE_INVALID")
        if (
            (not decision.reason_codes and decision.normalized_envelope is None)
            or any(code not in REASON_CODE_SET for code in decision.reason_codes)
            or len(decision.reason_codes) > MAX_REASON_CODES
            or len(set(decision.reason_codes)) != len(decision.reason_codes)
            or len(decision.limitations) > MAX_LIMITATIONS
            or len(set(decision.limitations)) != len(decision.limitations)
            or any(not _safe_reference(value) for value in decision.limitations)
            or (
                decision.safe_observation_reference is not None
                and not _safe_reference(decision.safe_observation_reference)
            )
            or (
                decision.safe_source_digest is not None
                and DIGEST_PATTERN.fullmatch(decision.safe_source_digest) is None
            )
        ):
            raise TelemetryAdmissionError("TA_SHAPE_INVALID")

        if decision.normalized_envelope is None:
            if decision.state != "REJECTED":
                raise TelemetryAdmissionError("TA_SHAPE_INVALID")
            return

        # Import locally to keep the storage module's dependency direction
        # explicit while preventing callers from forging an accepted decision.
        from .validator import TelemetryEnvelopeValidator

        revalidated = TelemetryEnvelopeValidator().validate(
            dict(decision.normalized_envelope)
        )
        if (
            revalidated.normalized_envelope is None
            or revalidated.state != decision.state
            or revalidated.reason_codes != decision.reason_codes
            or revalidated.limitations != decision.limitations
            or revalidated.safe_observation_reference
            != decision.safe_observation_reference
            or revalidated.safe_source_digest != decision.safe_source_digest
            or _canonical_json(dict(revalidated.normalized_envelope))
            != _canonical_json(dict(decision.normalized_envelope))
        ):
            raise TelemetryAdmissionError("TA_SHAPE_INVALID")

    def _record_in_transaction(
        self,
        connection: sqlite3.Connection,
        decision: ValidationDecision,
        *,
        admission_id: str | None,
        claimed_receipt: str | None,
        accepted_item_count: int | None,
        rejected_item_count: int | None,
    ) -> AdmissionResult:
        reasons = set(decision.reason_codes)
        limitations = set(decision.limitations)
        state = decision.state
        normalized = (
            dict(decision.normalized_envelope)
            if decision.normalized_envelope is not None
            else None
        )
        source_digest = decision.safe_source_digest

        receipt_row: sqlite3.Row | None = None
        if claimed_receipt is not None and _safe_reference(claimed_receipt):
            receipt_row = connection.execute(
                "SELECT intake_receipt_reference, admission_id, source_digest "
                "FROM intake_receipts WHERE intake_receipt_reference=?",
                (claimed_receipt,),
            ).fetchone()

        if claimed_receipt is not None:
            if receipt_row is None:
                reasons.add("TA_INTAKE_RECEIPT_INVALID")
                state = "REJECTED"
                normalized = None
            elif (
                normalized is not None
                and admission_id == receipt_row["admission_id"]
                and source_digest == receipt_row["source_digest"]
            ):
                return self._append_confirmed_replay(
                    connection,
                    admission_id=str(receipt_row["admission_id"]),
                    receipt_reference=str(receipt_row["intake_receipt_reference"]),
                )
            else:
                reasons.add("TA_IDEMPOTENCY_CONFLICT")
                state = "REJECTED"
                normalized = None

        if admission_id is None or not _safe_reference(admission_id):
            admission_id = self._id_factory("admission")
        existing = connection.execute(
            "SELECT 1 FROM admission_lifecycles WHERE admission_id=?", (admission_id,)
        ).fetchone()
        if existing is not None:
            reasons.add("TA_IDEMPOTENCY_CONFLICT")
            state = "REJECTED"
            normalized = None
            admission_id = self._id_factory("admission")

        source_digest = source_digest or _fallback_digest(admission_id)
        comparison_fingerprint: str | None = None
        duplicate_reference: str | None = claimed_receipt
        if normalized is not None:
            comparison_fingerprint = _fingerprint(normalized)
            suspected = connection.execute(
                "SELECT al.admission_id FROM observation_envelopes oe "
                "JOIN admission_lifecycles al ON al.observation_reference=oe.observation_id "
                "WHERE oe.comparison_fingerprint=? AND oe.fingerprint_version=? "
                "ORDER BY al.created_at, al.admission_id LIMIT 1",
                (comparison_fingerprint, FINGERPRINT_VERSION),
            ).fetchone()
            hint = normalized["idempotency_reference"]
            if hint != "UNKNOWN":
                hint_match = connection.execute(
                    "SELECT admission_id FROM untrusted_idempotency_hints "
                    "WHERE idempotency_reference=? ORDER BY recorded_at, admission_id LIMIT 1",
                    (hint,),
                ).fetchone()
            else:
                hint_match = None
            if state in {"ACCEPTED_AS_MATERIAL", "PARTIAL"} and (
                suspected is not None or hint_match is not None
            ):
                state = "DUPLICATE_SUSPECTED"
                reasons.update(
                    {
                        "TA_DUPLICATE_SUSPECTED",
                        "TA_FINGERPRINT_COLLISION_OR_LEGITIMATE_DUPLICATE",
                    }
                )
                duplicate_reference = str((suspected or hint_match)["admission_id"])

        observation_reference = (
            str(normalized["observation_id"])
            if normalized is not None
            else self._id_factory("observation")
        )
        if connection.execute(
            "SELECT 1 FROM observation_envelopes WHERE observation_id=?",
            (observation_reference,),
        ).fetchone():
            reasons.add("TA_IDEMPOTENCY_CONFLICT")
            state = "REJECTED"
            normalized = None
            comparison_fingerprint = None
            observation_reference = self._id_factory("observation")

        recorded_at = self._clock()
        envelope_json = _canonical_json(normalized) if normalized is not None else None
        stub_material = {
            "observation_reference": observation_reference,
            "source_digest": source_digest,
            "reason_codes": list(order_reason_codes(reasons)),
        }
        payload_digest = _sha256_bytes(
            (envelope_json or _canonical_json(stub_material)).encode("utf-8")
        )
        connection.execute(
            "INSERT INTO observation_envelopes("
            "observation_id,envelope_json,source_digest,persistence_class,"
            "comparison_fingerprint,fingerprint_version,payload_digest,received_at"
            ") VALUES (?,?,?,?,?,?,?,?)",
            (
                observation_reference,
                envelope_json,
                source_digest,
                "VALIDATED_METADATA" if normalized is not None else "REJECTION_STUB",
                comparison_fingerprint,
                FINGERPRINT_VERSION,
                payload_digest,
                recorded_at,
            ),
        )
        idempotency_reference = (
            str(normalized["idempotency_reference"])
            if normalized is not None
            else "UNKNOWN"
        )
        connection.execute(
            "INSERT INTO admission_lifecycles("
            "admission_id,observation_reference,source_digest,idempotency_reference,created_at"
            ") VALUES (?,?,?,?,?)",
            (
                admission_id,
                observation_reference,
                source_digest,
                idempotency_reference,
                recorded_at,
            ),
        )
        self._fault("after_lifecycle_insert")

        receipt_reference = self._id_factory("receipt")
        connection.execute(
            "INSERT INTO intake_receipts("
            "intake_receipt_reference,admission_id,source_digest,issued_at"
            ") VALUES (?,?,?,?)",
            (receipt_reference, admission_id, source_digest, recorded_at),
        )
        if idempotency_reference != "UNKNOWN":
            connection.execute(
                "INSERT INTO untrusted_idempotency_hints("
                "idempotency_reference,admission_id,comparison_fingerprint,recorded_at"
                ") VALUES (?,?,?,?)",
                (
                    idempotency_reference,
                    admission_id,
                    comparison_fingerprint,
                    recorded_at,
                ),
            )

        previous: str | None = None
        for sequence, transition in ((1, "RECEIVED"), (2, "VALIDATING")):
            previous = self._insert_record(
                connection,
                admission_id=admission_id,
                observation_reference=observation_reference,
                sequence=sequence,
                previous_record_reference=previous,
                state=transition,
                source_digest=source_digest,
                idempotency_reference=idempotency_reference,
                receipt_reference=receipt_reference,
                duplicate_reference=None,
                comparison_fingerprint=comparison_fingerprint,
                accepted_item_count=0,
                rejected_item_count=0,
                reason_codes=(),
                limitations=(),
            )["admission_record_id"]

        default_accepted, default_rejected = _default_counts(state)
        accepted = (
            default_accepted if accepted_item_count is None else accepted_item_count
        )
        rejected = (
            default_rejected if rejected_item_count is None else rejected_item_count
        )
        if not isinstance(accepted, int) or isinstance(accepted, bool) or accepted < 0:
            raise ValueError("invalid accepted count")
        if not isinstance(rejected, int) or isinstance(rejected, bool) or rejected < 0:
            raise ValueError("invalid rejected count")
        if state == "ACCEPTED_AS_MATERIAL" and (accepted == 0 or rejected != 0):
            raise ValueError("accepted result requires accepted items only")
        if state == "PARTIAL" and (accepted == 0 or rejected == 0):
            raise ValueError("partial result requires accepted and rejected items")
        if state == "REJECTED" and (accepted != 0 or rejected == 0):
            raise ValueError("rejected result requires rejected items only")
        if state in {"DUPLICATE_CONFIRMED", "DUPLICATE_SUSPECTED", "UNKNOWN"} and (
            accepted != 0 or rejected != 0
        ):
            raise ValueError("non-material result requires zero item counts")
        terminal = self._insert_record(
            connection,
            admission_id=admission_id,
            observation_reference=observation_reference,
            sequence=3,
            previous_record_reference=previous,
            state=state,
            source_digest=source_digest,
            idempotency_reference=idempotency_reference,
            receipt_reference=receipt_reference,
            duplicate_reference=duplicate_reference,
            comparison_fingerprint=comparison_fingerprint,
            accepted_item_count=accepted,
            rejected_item_count=rejected,
            reason_codes=order_reason_codes(reasons),
            limitations=tuple(sorted(limitations)),
        )
        return AdmissionResult(
            admission_id=admission_id,
            observation_reference=observation_reference,
            admission_record_id=str(terminal["admission_record_id"]),
            intake_receipt_reference=receipt_reference,
            state=state,
            sequence=3,
            reason_codes=tuple(terminal["reason_codes"]),
            limitations=tuple(terminal["limitations"]),
            accepted_item_count=accepted,
            rejected_item_count=rejected,
        )

    def _append_confirmed_replay(
        self,
        connection: sqlite3.Connection,
        *,
        admission_id: str,
        receipt_reference: str,
    ) -> AdmissionResult:
        lifecycle = connection.execute(
            "SELECT * FROM admission_lifecycles WHERE admission_id=?", (admission_id,)
        ).fetchone()
        latest = connection.execute(
            "SELECT * FROM admission_records WHERE admission_id=? "
            "ORDER BY sequence DESC LIMIT 1",
            (admission_id,),
        ).fetchone()
        if lifecycle is None or latest is None:
            raise TelemetryAdmissionError("TA_INTAKE_RECEIPT_INVALID")
        sequence = int(latest["sequence"]) + 1
        record = self._insert_record(
            connection,
            admission_id=admission_id,
            observation_reference=str(lifecycle["observation_reference"]),
            sequence=sequence,
            previous_record_reference=str(latest["admission_record_id"]),
            state="DUPLICATE_CONFIRMED",
            source_digest=str(lifecycle["source_digest"]),
            idempotency_reference=str(lifecycle["idempotency_reference"]),
            receipt_reference=receipt_reference,
            duplicate_reference=str(latest["admission_record_id"]),
            comparison_fingerprint=latest["comparison_fingerprint"],
            accepted_item_count=0,
            rejected_item_count=0,
            reason_codes=("TA_DUPLICATE_CONFIRMED",),
            limitations=(),
        )
        return AdmissionResult(
            admission_id=admission_id,
            observation_reference=str(lifecycle["observation_reference"]),
            admission_record_id=str(record["admission_record_id"]),
            intake_receipt_reference=receipt_reference,
            state="DUPLICATE_CONFIRMED",
            sequence=sequence,
            reason_codes=("TA_DUPLICATE_CONFIRMED",),
            limitations=(),
            accepted_item_count=0,
            rejected_item_count=0,
        )

    def _insert_record(
        self,
        connection: sqlite3.Connection,
        *,
        admission_id: str,
        observation_reference: str,
        sequence: int,
        previous_record_reference: str | None,
        state: str,
        source_digest: str,
        idempotency_reference: str,
        receipt_reference: str,
        duplicate_reference: str | None,
        comparison_fingerprint: str | None,
        accepted_item_count: int,
        rejected_item_count: int,
        reason_codes: tuple[str, ...],
        limitations: tuple[str, ...],
    ) -> dict[str, Any]:
        if state not in ADMISSION_STATES:
            raise ValueError("unsupported admission state")
        ordered_reasons = order_reason_codes(reason_codes)
        if len(ordered_reasons) > MAX_REASON_CODES or any(
            code not in REASON_CODE_SET for code in ordered_reasons
        ):
            raise ValueError("invalid reason codes")
        if len(limitations) > MAX_LIMITATIONS or len(set(limitations)) != len(
            limitations
        ):
            raise ValueError("invalid limitations")
        record = {
            "admission_record_id": self._id_factory("record"),
            "admission_id": admission_id,
            "observation_reference": observation_reference,
            "sequence": sequence,
            "previous_record_reference": previous_record_reference,
            "state": state,
            "policy_version": ADMISSION_POLICY_VERSION,
            "validator_version": VALIDATOR_VERSION,
            "source_digest": source_digest,
            "idempotency_reference": idempotency_reference,
            "intake_receipt_reference": receipt_reference,
            "duplicate_reference": duplicate_reference,
            "comparison_fingerprint": comparison_fingerprint,
            "fingerprint_version": FINGERPRINT_VERSION,
            "accepted_item_count": accepted_item_count,
            "rejected_item_count": rejected_item_count,
            "reason_codes": list(ordered_reasons),
            "limitations": list(limitations),
            "recorded_at": self._clock(),
            "actor_reference": ACTOR_REFERENCE,
        }
        digest = _sha256_json(record)
        connection.execute(
            "INSERT INTO admission_records("
            "admission_record_id,admission_id,observation_reference,sequence,"
            "previous_record_reference,state,policy_version,validator_version,"
            "source_digest,idempotency_reference,intake_receipt_reference,"
            "duplicate_reference,comparison_fingerprint,fingerprint_version,"
            "accepted_item_count,rejected_item_count,reason_codes_json,"
            "limitations_json,recorded_at,actor_reference,record_digest"
            ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                record["admission_record_id"],
                record["admission_id"],
                record["observation_reference"],
                record["sequence"],
                record["previous_record_reference"],
                record["state"],
                record["policy_version"],
                record["validator_version"],
                record["source_digest"],
                record["idempotency_reference"],
                record["intake_receipt_reference"],
                record["duplicate_reference"],
                record["comparison_fingerprint"],
                record["fingerprint_version"],
                record["accepted_item_count"],
                record["rejected_item_count"],
                _canonical_json(record["reason_codes"]),
                _canonical_json(record["limitations"]),
                record["recorded_at"],
                record["actor_reference"],
                digest,
            ),
        )
        return record

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "admission_record_id": row["admission_record_id"],
            "admission_id": row["admission_id"],
            "observation_reference": row["observation_reference"],
            "sequence": row["sequence"],
            "previous_record_reference": row["previous_record_reference"],
            "state": row["state"],
            "policy_version": row["policy_version"],
            "validator_version": row["validator_version"],
            "source_digest": row["source_digest"],
            "idempotency_reference": row["idempotency_reference"],
            "intake_receipt_reference": row["intake_receipt_reference"],
            "duplicate_reference": row["duplicate_reference"],
            "comparison_fingerprint": row["comparison_fingerprint"],
            "fingerprint_version": row["fingerprint_version"],
            "accepted_item_count": row["accepted_item_count"],
            "rejected_item_count": row["rejected_item_count"],
            "reason_codes": json.loads(row["reason_codes_json"]),
            "limitations": json.loads(row["limitations_json"]),
            "recorded_at": row["recorded_at"],
            "actor_reference": row["actor_reference"],
        }

    def get_records(self, admission_id: str) -> list[dict[str, Any]]:
        connection = self._connect()
        try:
            self._verify_migration(connection)
            rows = connection.execute(
                "SELECT * FROM admission_records WHERE admission_id=? ORDER BY sequence",
                (admission_id,),
            ).fetchall()
            records = [self._record_from_row(row) for row in rows]
            for row, record in zip(rows, records, strict=True):
                if _sha256_json(record) != row["record_digest"]:
                    raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            return records
        except (sqlite3.Error, json.JSONDecodeError) as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
        finally:
            connection.close()

    def get_envelope(self, observation_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            self._verify_migration(connection)
            row = connection.execute(
                "SELECT envelope_json,payload_digest FROM observation_envelopes "
                "WHERE observation_id=?",
                (observation_id,),
            ).fetchone()
            if row is None or row["envelope_json"] is None:
                return None
            if (
                _sha256_bytes(row["envelope_json"].encode("utf-8"))
                != row["payload_digest"]
            ):
                raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            value = json.loads(row["envelope_json"])
            if not isinstance(value, dict):
                raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
            return value
        except (sqlite3.Error, json.JSONDecodeError) as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
        finally:
            connection.close()

    def get_receipt_for_admission(self, admission_id: str) -> str | None:
        """Return the committed DBOS receipt reference for one lifecycle."""

        if not _safe_reference(admission_id):
            return None
        connection = self._connect()
        try:
            self._verify_migration(connection)
            row = connection.execute(
                "SELECT intake_receipt_reference FROM intake_receipts "
                "WHERE admission_id=?",
                (admission_id,),
            ).fetchone()
            return None if row is None else str(row["intake_receipt_reference"])
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
        finally:
            connection.close()

    def counts(self) -> dict[str, int]:
        connection = self._connect()
        try:
            self._verify_migration(connection)
            count_queries = {
                "observation_envelopes": "SELECT COUNT(*) FROM observation_envelopes",
                "admission_lifecycles": "SELECT COUNT(*) FROM admission_lifecycles",
                "admission_records": "SELECT COUNT(*) FROM admission_records",
                "intake_receipts": "SELECT COUNT(*) FROM intake_receipts",
                "untrusted_idempotency_hints": (
                    "SELECT COUNT(*) FROM untrusted_idempotency_hints"
                ),
                "backup_manifests": "SELECT COUNT(*) FROM backup_manifests",
            }
            return {
                table: int(connection.execute(query).fetchone()[0])
                for table, query in count_queries.items()
            }
        finally:
            connection.close()

    def integrity_report(
        self, *, expected_receipt_references: Iterable[str] = ()
    ) -> dict[str, Any]:
        """Verify SQLite, FK, migration, append sequence, and stored digests."""

        expected_receipts = tuple(expected_receipt_references)
        errors: set[str] = set()
        counts: dict[str, int] = {}
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            self._verify_migration(connection)
            integrity_rows = [
                row[0] for row in connection.execute("PRAGMA integrity_check")
            ]
            if integrity_rows != ["ok"]:
                errors.add("TA_STORAGE_INTEGRITY_FAILURE")
            if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
                errors.add("TA_STORAGE_INTEGRITY_FAILURE")
            store_configuration = {
                "journal_mode": str(
                    connection.execute("PRAGMA journal_mode").fetchone()[0]
                ).lower(),
                "synchronous": int(
                    connection.execute("PRAGMA synchronous").fetchone()[0]
                ),
                "foreign_keys": int(
                    connection.execute("PRAGMA foreign_keys").fetchone()[0]
                ),
                "busy_timeout_ms": int(
                    connection.execute("PRAGMA busy_timeout").fetchone()[0]
                ),
            }
            if store_configuration != {
                "journal_mode": "wal",
                "synchronous": 2,
                "foreign_keys": 1,
                "busy_timeout_ms": self.busy_timeout_ms,
            }:
                errors.add("TA_STORAGE_INTEGRITY_FAILURE")
            rows = connection.execute(
                "SELECT * FROM admission_records ORDER BY admission_id,sequence"
            )
            current_admission_id: str | None = None
            expected_sequence = 0
            expected_previous: str | None = None
            for row in rows:
                admission_id = str(row["admission_id"])
                if admission_id != current_admission_id:
                    current_admission_id = admission_id
                    expected_sequence = 1
                    expected_previous = None
                else:
                    expected_sequence += 1
                record = self._record_from_row(row)
                if tuple(record) != ADMISSION_RECORD_FIELDS:
                    errors.add("TA_STORAGE_INTEGRITY_FAILURE")
                if _sha256_json(record) != row["record_digest"]:
                    errors.add("TA_STORAGE_INTEGRITY_FAILURE")
                if row["sequence"] != expected_sequence:
                    errors.add("TA_STORAGE_INTEGRITY_FAILURE")
                if row["previous_record_reference"] != expected_previous:
                    errors.add("TA_STORAGE_INTEGRITY_FAILURE")
                expected_previous = str(row["admission_record_id"])
            if any(not _safe_reference(value) for value in expected_receipts):
                errors.add("TA_STORAGE_INTEGRITY_FAILURE")
                missing_receipt_count = len(expected_receipts)
            elif expected_receipts:
                unique_receipts = set(expected_receipts)
                observed = sum(
                    connection.execute(
                        "SELECT 1 FROM intake_receipts "
                        "WHERE intake_receipt_reference=?",
                        (receipt,),
                    ).fetchone()
                    is not None
                    for receipt in unique_receipts
                )
                missing_receipt_count = len(unique_receipts) - observed
                if missing_receipt_count:
                    errors.add("TA_STORAGE_INTEGRITY_FAILURE")
            else:
                missing_receipt_count = 0
            counts = self.counts()
            applied_migration_checksums = self._applied_migration_checksums(connection)
        except (TelemetryAdmissionError, sqlite3.Error, json.JSONDecodeError):
            errors.add("TA_STORAGE_INTEGRITY_FAILURE")
            store_configuration = {}
            missing_receipt_count = len(expected_receipts)
            applied_migration_checksums = {}
        finally:
            if connection is not None:
                connection.close()
        return {
            "status": "PASS" if not errors else "FAIL",
            "schema_version": STORE_SCHEMA_VERSION,
            "migration_checksums": applied_migration_checksums,
            "counts": counts,
            "store_configuration": store_configuration,
            "missing_expected_receipt_count": missing_receipt_count,
            "errors": sorted(set(errors)),
            "repair_performed": False,
        }

    def _chain_digest(self) -> str:
        connection = self._connect()
        try:
            digests = [
                row[0]
                for row in connection.execute(
                    "SELECT record_digest FROM admission_records "
                    "ORDER BY admission_id,sequence"
                )
            ]
        finally:
            connection.close()
        return _sha256_json(digests)

    def backup(self, destination: str | Path) -> dict[str, Any]:
        """Create a consistent online backup at a new explicit path."""

        self.initialize()
        destination_path = _validate_explicit_path(destination, must_not_exist=True)
        _secure_create(destination_path)
        self._fault("before_backup")
        source = self._connect()
        target = sqlite3.connect(destination_path, isolation_level=None)
        try:
            source.backup(target)
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        finally:
            target.close()
            source.close()
            _secure_database_files(destination_path)
        self._fault("after_backup_copy")

        backup_store = SQLiteTelemetryAdmissionStore(
            destination_path,
            busy_timeout_ms=self.busy_timeout_ms,
            clock=self._clock,
            id_factory=self._id_factory,
        )
        backup_store.initialize()
        report = backup_store.integrity_report()
        if report["status"] != "PASS":
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        manifest_without_digest = {
            "backup_id": self._id_factory("backup"),
            "schema_version": STORE_SCHEMA_VERSION,
            # Bind the manifest to the history actually present in the
            # snapshot. A store upgraded from the compatible fixture has a
            # different, equally valid lineage from a directly initialized
            # store and must not be mislabeled as the direct path.
            "migration_checksums": dict(report["migration_checksums"]),
            "database_sha256": _file_sha256(destination_path),
            "record_chain_digest": backup_store._chain_digest(),
            "counts": report["counts"],
            "created_at": self._clock(),
        }
        manifest = {
            **manifest_without_digest,
            "manifest_digest": _sha256_json(manifest_without_digest),
        }
        self._fault("before_backup_manifest_commit")
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO backup_manifests("
                "backup_id,schema_version,database_sha256,record_chain_digest,"
                "manifest_digest,counts_json,created_at"
                ") VALUES (?,?,?,?,?,?,?)",
                (
                    manifest["backup_id"],
                    manifest["schema_version"],
                    manifest["database_sha256"],
                    manifest["record_chain_digest"],
                    manifest["manifest_digest"],
                    _canonical_json(manifest["counts"]),
                    manifest["created_at"],
                ),
            )
            connection.commit()
        except sqlite3.Error as exc:
            if connection.in_transaction:
                connection.rollback()
            raise TelemetryAdmissionError("TA_STORAGE_UNAVAILABLE") from exc
        finally:
            connection.close()
            _secure_database_files(self.path)
        self._fault("after_backup_manifest_commit")
        return manifest

    @classmethod
    def restore(
        cls,
        backup_path: str | Path,
        manifest: Mapping[str, Any],
        destination: str | Path,
        *,
        busy_timeout_ms: int = BUSY_TIMEOUT_MILLISECONDS,
        fault_injector: FaultInjector | None = None,
    ) -> "SQLiteTelemetryAdmissionStore":
        """Restore a verified backup to a new path; never overwrite a store."""

        if not isinstance(manifest, Mapping):
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        source_path = _validate_explicit_path(backup_path)
        destination_path = _validate_explicit_path(destination, must_not_exist=True)
        supplied_digest = manifest.get("manifest_digest")
        manifest_without_digest = {
            key: manifest[key]
            for key in (
                "backup_id",
                "schema_version",
                "migration_checksums",
                "database_sha256",
                "record_chain_digest",
                "counts",
                "created_at",
            )
            if key in manifest
        }
        migration_checksums = manifest.get("migration_checksums")
        counts = manifest.get("counts")
        if (
            len(manifest_without_digest) != 7
            or not isinstance(migration_checksums, Mapping)
            or any(
                not isinstance(key, str) or not isinstance(value, str)
                for key, value in migration_checksums.items()
            )
            or not isinstance(counts, Mapping)
            or set(counts) != set(EXPECTED_TABLE_COLUMNS) - {"schema_migrations"}
            or any(
                not isinstance(key, str)
                or not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
                for key, value in counts.items()
            )
            or supplied_digest != _sha256_json(manifest_without_digest)
            or manifest.get("schema_version") != STORE_SCHEMA_VERSION
            or tuple(sorted(migration_checksums.items()))
            not in {
                tuple(sorted(DIRECT_MIGRATION_HISTORY)),
                tuple(sorted(COMPATIBLE_MIGRATION_HISTORY)),
            }
            or manifest.get("database_sha256") != _file_sha256(source_path)
        ):
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")

        _secure_create(destination_path)
        try:
            source = sqlite3.connect(
                f"file:{source_path}?mode=ro",
                uri=True,
                isolation_level=None,
            )
            target = sqlite3.connect(destination_path, isolation_level=None)
            try:
                source.backup(target)
            finally:
                target.close()
                source.close()
        except sqlite3.Error as exc:
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE") from exc
        _secure_database_files(destination_path)
        if fault_injector is not None:
            fault_injector("after_restore_copy")
        restored = cls(destination_path, busy_timeout_ms=busy_timeout_ms)
        if fault_injector is not None:
            fault_injector("before_restore_validation")
        restored.initialize()
        report = restored.integrity_report()
        if (
            report["status"] != "PASS"
            or report["counts"] != manifest.get("counts")
            or restored._chain_digest() != manifest.get("record_chain_digest")
        ):
            raise TelemetryAdmissionError("TA_STORAGE_INTEGRITY_FAILURE")
        if fault_injector is not None:
            fault_injector("after_restore_validation")
        return restored


__all__ = [
    "DATABASE_APPLICATION_ID",
    "DATABASE_USER_VERSION",
    "COMPATIBILITY_MIGRATION_VERSION",
    "DIRECT_MIGRATION_HISTORY",
    "COMPATIBLE_MIGRATION_HISTORY",
    "MIGRATION_VERSION",
    "PRIOR_COMPATIBLE_VERSION",
    "PRIOR_COMPATIBLE_FIXTURE_RESOURCE",
    "SQLiteTelemetryAdmissionStore",
    "compatibility_migration_checksum",
    "migration_checksum",
    "prior_compatible_fixture_checksum",
]
