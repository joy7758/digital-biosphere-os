"""Prepare a DBOS-to-SAEE data envelope without evaluating or sending it.

Agent-readable contract:
- This is a local data structure, not an API, endpoint, transport, or SAEE call.
- DBOS provides references; SAEE remains the owner of future evaluation.
- The envelope status is PREPARED_NOT_SENT and evaluation_effect is NONE.
- Fitness, risk, evolution, governance decision, command, and permission fields
  are prohibited recursively.
- No lifecycle, capability, evidence, or verification state is changed.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

SAEE_ENVELOPE_FIELDS = (
    "contract_version",
    "execution_history",
    "evidence_bundle_reference",
    "verification_result",
    "resource_usage_reference",
    "producer",
    "consumer",
    "payload_status",
    "authority_class",
    "evaluation_effect",
)
PROHIBITED_EVALUATION_KEYS = frozenset(
    {
        "fitness",
        "fitness_assessment",
        "risk_assessment",
        "evolution_recommendation",
        "governance_suggestion",
        "decision",
        "command",
        "permission",
        "permission_status",
    }
)
VERIFICATION_RESULT_FIELDS = (
    "verification_reference",
    "verification_status",
    "verification_level",
)


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _find_prohibited_keys(value: object, path: str = "envelope") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_EVALUATION_KEYS:
                errors.append(f"prohibited evaluation key: {child_path}")
            errors.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return errors


def validate_saee_evaluation_envelope(envelope: Mapping[str, Any]) -> list[str]:
    """Return errors without invoking SAEE or calculating evaluation output."""

    errors = _find_prohibited_keys(envelope)
    missing = [field for field in SAEE_ENVELOPE_FIELDS if field not in envelope]
    extra = sorted(set(envelope) - set(SAEE_ENVELOPE_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    if envelope.get("contract_version") != "DBA-INTERFACE-0.1":
        errors.append("contract_version must remain DBA-INTERFACE-0.1")

    history = envelope.get("execution_history")
    if not isinstance(history, list) or not all(_is_non_empty_string(item) for item in history):
        errors.append("execution_history must be a list of non-empty references")
    elif len(history) != len(set(history)):
        errors.append("execution_history references must be unique")
    if not _is_non_empty_string(envelope.get("evidence_bundle_reference")):
        errors.append("evidence_bundle_reference must be a non-empty string")
    resource_reference = envelope.get("resource_usage_reference")
    if resource_reference is not None and not _is_non_empty_string(resource_reference):
        errors.append("resource_usage_reference must be null or a non-empty string")

    verification = envelope.get("verification_result")
    if not isinstance(verification, Mapping):
        errors.append("verification_result must be a mapping")
    else:
        missing_verification = [
            field for field in VERIFICATION_RESULT_FIELDS if field not in verification
        ]
        extra_verification = sorted(set(verification) - set(VERIFICATION_RESULT_FIELDS))
        if missing_verification:
            errors.append(f"verification_result missing fields: {missing_verification}")
        if extra_verification:
            errors.append(f"verification_result unexpected fields: {extra_verification}")
        if not _is_non_empty_string(verification.get("verification_reference")):
            errors.append("verification_reference must be a non-empty string")
        if verification.get("verification_status") not in {"UNKNOWN", "PENDING"}:
            errors.append("verification_status must remain UNKNOWN or PENDING")
        if verification.get("verification_level") != "V0":
            errors.append("verification_level must remain V0")

    expected = {
        "producer": "DBOS",
        "consumer": "SAEE",
        "payload_status": "PREPARED_NOT_SENT",
        "authority_class": "DATA_TRANSFER_PREPARATION",
        "evaluation_effect": "NONE",
    }
    for field, expected_value in expected.items():
        if envelope.get(field) != expected_value:
            errors.append(f"{field} must remain {expected_value}")
    return errors


def build_saee_evaluation_envelope(
    *,
    execution_history: list[str],
    evidence_bundle_reference: str,
    verification_result: Mapping[str, str],
    resource_usage_reference: str | None = None,
) -> dict[str, Any]:
    """Return a prepared-not-sent envelope with no evaluation effect."""

    envelope = {
        "contract_version": "DBA-INTERFACE-0.1",
        "execution_history": list(execution_history),
        "evidence_bundle_reference": evidence_bundle_reference,
        "verification_result": deepcopy(dict(verification_result)),
        "resource_usage_reference": resource_usage_reference,
        "producer": "DBOS",
        "consumer": "SAEE",
        "payload_status": "PREPARED_NOT_SENT",
        "authority_class": "DATA_TRANSFER_PREPARATION",
        "evaluation_effect": "NONE",
    }
    errors = validate_saee_evaluation_envelope(envelope)
    if errors:
        raise ValueError("; ".join(errors))
    return envelope


__all__ = [
    "PROHIBITED_EVALUATION_KEYS",
    "SAEE_ENVELOPE_FIELDS",
    "VERIFICATION_RESULT_FIELDS",
    "build_saee_evaluation_envelope",
    "validate_saee_evaluation_envelope",
]
