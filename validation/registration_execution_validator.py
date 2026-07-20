#!/usr/bin/env python3
"""Validate the fail-closed Digital Entity Registration Execution Layer.

Agent-readable contract:
- Inputs and outputs are ephemeral fixture mappings only.
- PASS proves AUTHORIZED gating, REGISTERED-only output, receipt retention, and
  candidate → authorization → entity continuity.
- PASS does not persist a Registered Entity or create Agent, Runtime,
  Permission, Capability Grant, task Execution, Evidence, or SAEE output.
- Exit 0: PASS
- Exit 1: FAIL
No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from entity_support.candidate.candidate_proposal import build_candidate_proposal
from entity_support.candidate.candidate_registration_request import (
    build_candidate_registration_request,
)
from entity_support.candidate.candidate_registry import build_candidate_registry_record
from entity_support.candidate.candidate_review import build_candidate_review
from entity_support.registration.registration_executor import (
    execute_entity_registration,
)
from entity_support.registration.registration_validator import (
    build_registration_authorization_input,
    validate_identity_continuity,
)

EXPECTED_NEGATIVE_CASES = (
    "unauthorized_registration",
    "automatic_active",
    "automatic_permission",
    "automatic_capability_grant",
    "missing_candidate_source",
    "missing_authorization_source",
)
FIXTURE_TIMESTAMP = "2026-07-20T12:00:00+08:00"


def _candidate() -> dict[str, object]:
    candidate_id = "fixture-registration-candidate"
    proposal = build_candidate_proposal(
        candidate_id=candidate_id,
        proposed_type="operational_entity",
        role="bounded_fixture",
        description="ephemeral registration validator fixture",
        proposer_reference="fixture-proposer",
    )
    review = build_candidate_review(
        review_id="fixture-registration-review",
        candidate_id=candidate_id,
        reviewer_reference="fixture-reviewer",
        review_status="APPROVED",
        review_notes="fixture review only",
    )
    request = build_candidate_registration_request(
        request_id="fixture-registration-request",
        candidate_id=candidate_id,
        requested_entity_type="service",
        mapping_reference="fixture-architecture-mapping",
        status="ACCEPTED",
    )
    return build_candidate_registry_record(
        candidate_id=candidate_id,
        proposal=proposal,
        review=review,
        registration_request=request,
    )


def _authorization() -> dict[str, Any]:
    return build_registration_authorization_input(
        authorization_id="fixture-registration-authorization",
        decision_reference="fixture-admission-decision",
        candidate_id="fixture-registration-candidate",
        target_entity_type="service",
        authorized_scope={
            "operation": "entity_registration",
            "lifecycle_target": "REGISTERED",
        },
        issuer_reference="fixture-authority-record",
        timestamp=FIXTURE_TIMESTAMP,
    )


def _must_fail_registration(
    name: str,
    candidate_factory: Callable[[], dict[str, object]],
    authorization_factory: Callable[[], dict[str, Any]],
    errors: list[str],
) -> bool:
    try:
        result = execute_entity_registration(
            candidate=candidate_factory(),
            authorization=authorization_factory(),
            registered_at=FIXTURE_TIMESTAMP,
        )
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        errors.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
        return False
    rejected = (
        result.get("entity_record") is None
        and result.get("receipt", {}).get("status") == "FAILED"
        and bool(result.get("errors"))
    )
    if not rejected:
        errors.append(f"{name}: prohibited registration was not rejected")
    return rejected


def validate() -> dict[str, Any]:
    """Return deterministic validation results with zero persistent effects."""

    errors: list[str] = []
    receipt_log: list[dict[str, str | None]] = []
    candidate = _candidate()
    authorization = _authorization()
    success = execute_entity_registration(
        candidate=candidate,
        authorization=authorization,
        registered_at=FIXTURE_TIMESTAMP,
        receipt_log=receipt_log,
    )
    entity = success.get("entity_record")
    receipt = success.get("receipt")
    if not isinstance(entity, dict) or entity.get("lifecycle_state") != "REGISTERED":
        errors.append("authorized fixture must produce one REGISTERED mapping")
    if not isinstance(receipt, dict) or receipt.get("status") != "SUCCESS":
        errors.append("authorized fixture must produce one SUCCESS receipt")
    if success.get("errors") != ():
        errors.append("authorized fixture returned errors")
    if len(receipt_log) != 1 or receipt_log[0] != receipt:
        errors.append("successful receipt was not retained in caller-provided log")
    if isinstance(entity, dict) and isinstance(receipt, dict):
        continuity = validate_identity_continuity(
            candidate=candidate,
            authorization=authorization,
            entity_record=entity,
            receipt=receipt,
        )
        if continuity:
            errors.extend(f"identity_continuity: {error}" for error in continuity)

    rejected: dict[str, bool] = {}

    def authorization_with(**updates: object) -> dict[str, Any]:
        record = _authorization()
        record.update(updates)
        return record

    rejected["unauthorized_registration"] = _must_fail_registration(
        "unauthorized_registration",
        _candidate,
        lambda: authorization_with(status="PENDING"),
        errors,
    )
    rejected["automatic_active"] = _must_fail_registration(
        "automatic_active",
        _candidate,
        lambda: authorization_with(
            authorized_scope={
                "operation": "entity_registration",
                "lifecycle_target": "ACTIVE",
            }
        ),
        errors,
    )
    rejected["automatic_permission"] = _must_fail_registration(
        "automatic_permission",
        _candidate,
        lambda: authorization_with(permission_status="GRANTED"),
        errors,
    )
    rejected["automatic_capability_grant"] = _must_fail_registration(
        "automatic_capability_grant",
        _candidate,
        lambda: authorization_with(
            authorized_scope={
                "operation": "entity_registration",
                "lifecycle_target": "REGISTERED",
                "capability_grant": "GRANTED",
            }
        ),
        errors,
    )

    def candidate_without_source() -> dict[str, object]:
        record = _candidate()
        record.pop("candidate_id")
        return record

    rejected["missing_candidate_source"] = _must_fail_registration(
        "missing_candidate_source",
        candidate_without_source,
        _authorization,
        errors,
    )
    rejected["missing_authorization_source"] = _must_fail_registration(
        "missing_authorization_source",
        _candidate,
        lambda: {key: value for key, value in _authorization().items() if key != "authorization_id"},
        errors,
    )

    for name in EXPECTED_NEGATIVE_CASES:
        if name not in rejected:
            errors.append(f"missing negative case: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "fixture_registered_record_count": 1 if isinstance(entity, dict) else 0,
        "fixture_receipt_count": len(receipt_log),
        "negative_case_count": len(EXPECTED_NEGATIVE_CASES),
        "rejected_negative_case_count": sum(rejected.values()),
        "negative_case_results": rejected,
        "persistent_side_effect_counts": {
            "registered_entity": 0,
            "active_entity": 0,
            "agent": 0,
            "runtime": 0,
            "permission": 0,
            "capability_grant": 0,
            "task_execution": 0,
            "canonical_evidence": 0,
            "saee_call": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    result = validate()
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"registration_execution_validator: {result['status']}")
        print(
            "negative cases rejected: "
            f"{result['rejected_negative_case_count']}/{result['negative_case_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

