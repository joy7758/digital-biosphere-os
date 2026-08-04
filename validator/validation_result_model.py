"""Immutable result model for DBOS Object Schema Validator v0.1.

The result is diagnostic only. No result value grants authority, permission,
capability, verification, execution, registration, or lifecycle transition.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


VALIDATOR_VERSION = "v0.1"


class ValidationStatus(str, Enum):
    """Top-level fail-closed outcomes required by the v0.1 tooling contract."""

    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    VERSION_MISMATCH = "VERSION_MISMATCH"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Internal diagnostic projected to the five-field v0.1 error contract."""

    code: str
    path: str
    message: str
    rule: str
    severity: str = "ERROR"
    resolution_hint: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("code", "path", "message", "rule"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.severity not in {"ERROR", "WARNING"}:
            raise ValueError("severity must be ERROR or WARNING")
        if self.resolution_hint is not None and (
            not isinstance(self.resolution_hint, str) or not self.resolution_hint
        ):
            raise ValueError("resolution_hint must be null or a non-empty string")

    def to_dict(self) -> dict[str, str | None]:
        hint = self.resolution_hint or f"Review the contract rule: {self.rule}."
        return {
            "error_code": self.code,
            "message": self.message,
            "field_reference": self.path,
            "severity": self.severity,
            "resolution_hint": hint,
        }


DEFAULT_LIMITATIONS = (
    "Local structure and governance-constraint validation only.",
    "PASS does not establish truth, authority, authorization, permission, or capability grant.",
    "Validation does not execute, repair, register, activate, or mutate the target object.",
    "Reference checks are local consistency checks, not source resolution or independent verification.",
)


@dataclass(frozen=True, slots=True)
class SchemaReference:
    """Immutable identity of the exact schema used for local validation."""

    schema_id: str
    schema_digest: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.schema_id, str) or not self.schema_id:
            raise ValueError("schema_id must be a non-empty string")
        if self.schema_digest is not None and (
            not isinstance(self.schema_digest, str)
            or not self.schema_digest.startswith("sha256:")
            or len(self.schema_digest) != 71
        ):
            raise ValueError("schema_digest must be null or a sha256 digest")

    def to_dict(self) -> dict[str, str | None]:
        return {
            "schema_id": self.schema_id,
            "schema_digest": self.schema_digest,
        }


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Stable nine-field v0.1 result with no governance side effects."""

    validator_version: str
    target_reference: str | None
    result: ValidationStatus
    errors: tuple[ValidationIssue, ...]
    schema_reference: SchemaReference | None = None
    validation_id: str | None = None
    warnings: tuple[ValidationIssue, ...] = ()
    limitations: tuple[str, ...] = DEFAULT_LIMITATIONS
    timestamp: str | None = None

    def __post_init__(self) -> None:
        self._validate_strings()
        self._validate_diagnostics()
        self._validate_timestamp()

    def _validate_strings(self) -> None:
        if not isinstance(self.validator_version, str) or not self.validator_version:
            raise ValueError("validator_version must be a non-empty string")
        if self.validation_id is not None and (
            not isinstance(self.validation_id, str) or not self.validation_id
        ):
            raise ValueError("validation_id must be null or a non-empty string")
        if self.target_reference is not None and (
            not isinstance(self.target_reference, str) or not self.target_reference
        ):
            raise ValueError("target_reference must be null or a non-empty string")

    def _validate_diagnostics(self) -> None:
        if self.result is ValidationStatus.PASS and self.errors:
            raise ValueError("PASS must not contain errors")
        if self.result is not ValidationStatus.PASS and not self.errors:
            raise ValueError("A non-PASS result must contain at least one error")
        if any(issue.severity != "ERROR" for issue in self.errors):
            raise ValueError("errors must contain ERROR diagnostics only")
        if any(issue.severity != "WARNING" for issue in self.warnings):
            raise ValueError("warnings must contain WARNING diagnostics only")
        if not self.limitations or any(
            not isinstance(item, str) or not item for item in self.limitations
        ):
            raise ValueError("limitations must contain at least one non-empty string")

    def _validate_timestamp(self) -> None:
        if self.timestamp is not None:
            if not isinstance(self.timestamp, str) or not self.timestamp:
                raise ValueError("timestamp must be null or a non-empty RFC 3339 string")
            normalized = (
                self.timestamp[:-1] + "+00:00"
                if self.timestamp.endswith("Z")
                else self.timestamp
            )
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError as exc:
                raise ValueError("timestamp must be an RFC 3339 string") from exc
            if parsed.tzinfo is None:
                raise ValueError("timestamp must include a timezone")

    @property
    def passed(self) -> bool:
        """Return structural success only; this is never an authority decision."""

        return self.result is ValidationStatus.PASS

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible copy without exposing or changing the input."""

        return {
            "validation_id": self.validation_id,
            "validator_version": self.validator_version,
            "target_reference": self.target_reference,
            "schema_reference": (
                self.schema_reference.to_dict()
                if self.schema_reference is not None
                else None
            ),
            "result": self.result.value,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "limitations": list(self.limitations),
            "timestamp": self.timestamp,
        }
