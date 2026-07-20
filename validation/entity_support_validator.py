#!/usr/bin/env python3
"""Validate the bounded Digital Entity Support Layer.

Agent-readable contract:
- Input: support-layer Python record builders only; no canonical registry input.
- Output: a deterministic JSON or text verdict about safe defaults and rejection gates.
- Exit 0: PASS
- Exit 1: FAIL
- Test fixtures are ephemeral mappings, not Entity, Agent, Runtime, Capability,
  Permission, Execution, Evidence, or Verification instances.
- No registry, evidence, experiment, or lifecycle file is read or written.
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

from entity_support.capability_registry import build_capability_record
from entity_support.entity_registry import build_entity_registration_record
from entity_support.evidence_reference import build_evidence_reference
from entity_support.execution_registry import build_execution_record
from entity_support.verification_reference import (
    build_verification_reference,
    validate_verification_reference,
)

EXPECTED_NEGATIVE_CASES = (
    "entity_auto_active",
    "capability_auto_authorized",
    "execution_auto_success",
    "evidence_auto_validated",
    "verification_permission_derivation",
)


def _must_reject(name: str, action: Callable[[], object], errors: list[str]) -> bool:
    """Return True only when a prohibited construction raises ValueError."""

    try:
        action()
    except ValueError:
        return True
    except Exception as exc:  # pragma: no cover - defensive diagnostic path
        errors.append(f"{name}: raised unexpected {type(exc).__name__}: {exc}")
        return False
    errors.append(f"{name}: prohibited state was accepted")
    return False


def validate() -> dict[str, Any]:
    """Validate safe defaults and all required fail-closed boundaries."""

    errors: list[str] = []

    entity = build_entity_registration_record(
        entity_id="fixture-entity",
        entity_type="service",
        owner_reference="fixture-owner",
    )
    capability = build_capability_record(
        capability_id="fixture-capability",
        entity_id="fixture-entity",
        capability_name="fixture-declaration",
        scope={"mode": "fixture-only"},
        constraints=["no execution", "no permission"],
    )
    execution = build_execution_record(
        execution_id="fixture-execution",
        entity_id="fixture-entity",
        task_reference="fixture-task",
        input_reference="fixture-input",
        context_reference="fixture-context",
    )
    evidence = build_evidence_reference(
        evidence_id="fixture-evidence-reference",
        execution_id="fixture-execution",
        reference="fixture://not-canonical-evidence",
    )
    verification = build_verification_reference(
        verification_id="fixture-verification-reference",
        evidence_id="fixture-evidence-reference",
    )

    expected_defaults = {
        "entity.lifecycle_state": (entity["lifecycle_state"], "PROPOSED"),
        "capability.verification_status": (
            capability["verification_status"],
            "UNVERIFIED",
        ),
        "execution.status": (execution["status"], "CREATED"),
        "evidence.integrity_status": (evidence["integrity_status"], "UNKNOWN"),
        "verification.verification_status": (
            verification["verification_status"],
            "PENDING",
        ),
        "verification.verification_level": (
            verification["verification_level"],
            "V0",
        ),
    }
    for field, (actual, expected) in expected_defaults.items():
        if actual != expected:
            errors.append(f"{field}: expected {expected!r}, found {actual!r}")

    forbidden_grant_fields = {
        "authorization",
        "authorization_status",
        "permission",
        "permission_status",
    }
    for record_name, record in (
        ("entity", entity),
        ("capability", capability),
        ("execution", execution),
        ("evidence", evidence),
        ("verification", verification),
    ):
        present = sorted(set(record) & forbidden_grant_fields)
        if present:
            errors.append(f"{record_name}: contains grant fields {present}")

    rejected: dict[str, bool] = {}
    rejected["entity_auto_active"] = _must_reject(
        "entity_auto_active",
        lambda: build_entity_registration_record(
            entity_id="fixture-entity",
            entity_type="service",
            owner_reference="fixture-owner",
            lifecycle_state="ACTIVE",
        ),
        errors,
    )
    rejected["capability_auto_authorized"] = _must_reject(
        "capability_auto_authorized",
        lambda: build_capability_record(
            capability_id="fixture-capability",
            entity_id="fixture-entity",
            capability_name="fixture-declaration",
            scope={"mode": "fixture-only"},
            constraints=["no permission"],
            verification_status="AUTHORIZED",
        ),
        errors,
    )
    rejected["execution_auto_success"] = _must_reject(
        "execution_auto_success",
        lambda: build_execution_record(
            execution_id="fixture-execution",
            entity_id="fixture-entity",
            task_reference="fixture-task",
            input_reference="fixture-input",
            context_reference="fixture-context",
            status="SUCCESS",
        ),
        errors,
    )
    rejected["evidence_auto_validated"] = _must_reject(
        "evidence_auto_validated",
        lambda: build_evidence_reference(
            evidence_id="fixture-evidence-reference",
            execution_id="fixture-execution",
            reference="fixture://not-canonical-evidence",
            integrity_status="VALIDATED",
        ),
        errors,
    )

    permission_derivation_errors = validate_verification_reference(
        {
            **verification,
            "permission_status": "GRANTED",
        }
    )
    rejected["verification_permission_derivation"] = any(
        "grant fields" in error for error in permission_derivation_errors
    )
    if not rejected["verification_permission_derivation"]:
        errors.append("verification_permission_derivation: grant field was not rejected")

    for name in EXPECTED_NEGATIVE_CASES:
        if name not in rejected:
            errors.append(f"missing negative case: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "support_schema_count": 5,
        "negative_case_count": len(EXPECTED_NEGATIVE_CASES),
        "rejected_negative_case_count": sum(rejected.values()),
        "negative_case_results": rejected,
        "side_effect_counts": {
            "agent": 0,
            "runtime": 0,
            "entity_instance": 0,
            "capability_instance": 0,
            "permission": 0,
            "execution": 0,
            "canonical_evidence": 0,
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
        print(f"entity_support_validator: {result['status']}")
        print(
            "negative cases rejected: "
            f"{result['rejected_negative_case_count']}/{result['negative_case_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
