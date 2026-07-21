"""Immutable SDK-facing failure wrapper with no automatic recovery behavior."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from validator import ValidationResult, ValidationStatus


class SDKErrorCode(str, Enum):
    """Non-success outcomes exposed by the v0.1 SDK skeleton."""

    UNKNOWN = "UNKNOWN"
    FAIL = "FAIL"
    CONFLICT = "CONFLICT"
    VERSION_MISMATCH = "VERSION_MISMATCH"


_ERROR_CODE_BY_STATUS = {
    ValidationStatus.UNKNOWN: SDKErrorCode.UNKNOWN,
    ValidationStatus.FAIL: SDKErrorCode.FAIL,
    ValidationStatus.CONFLICT: SDKErrorCode.CONFLICT,
    ValidationStatus.VERSION_MISMATCH: SDKErrorCode.VERSION_MISMATCH,
}


@dataclass(frozen=True, slots=True)
class SDKValidationFailure:
    """Diagnostic wrapper around an unchanged canonical ValidationResult."""

    code: SDKErrorCode
    result: ValidationResult
    auto_repair_performed: bool = False

    def __post_init__(self) -> None:
        if self.result.result is ValidationStatus.PASS:
            raise ValueError("PASS cannot be wrapped as an SDK validation failure")
        if self.auto_repair_performed:
            raise ValueError("The DBOS SDK v0.1 never performs automatic repair")


def validation_failure_from_result(
    result: ValidationResult,
) -> SDKValidationFailure | None:
    """Map non-PASS status without raising, retrying, repairing, or mutating."""

    if not isinstance(result, ValidationResult):
        raise TypeError("result must be a DBOS ValidationResult")
    if result.result is ValidationStatus.PASS:
        return None
    return SDKValidationFailure(code=_ERROR_CODE_BY_STATUS[result.result], result=result)
