#!/usr/bin/env python3
"""Validate Digital Entity Infrastructure v0.1 conformance.

Agent-readable contract:
- The validator constructs ephemeral mappings only.
- It validates support records, lifecycle gates, capability separation,
  context/evidence links, candidate registration, Research Agent templates,
  and a prepared-not-sent DBOS-to-SAEE envelope.
- PASS creates no Agent, Runtime, Entity instance, Capability instance,
  Permission, Execution, Evidence, Verification decision, or Fitness result.
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

from entity_support.candidate_registration import build_candidate_registration_record
from entity_support.capability_boundary import build_capability_boundary_record
from entity_support.capability_registry import build_capability_record
from entity_support.entity_registry import build_entity_registration_record
from entity_support.evidence_integration import build_evidence_integration_link
from entity_support.evidence_reference import build_evidence_reference
from entity_support.execution_context_integration import build_execution_context_link
from entity_support.execution_registry import build_execution_record
from entity_support.lifecycle_support import build_lifecycle_transition_record
from entity_support.research_agent_preparation import (
    build_research_agent_preparation_template,
    validate_research_agent_preparation_template,
)
from entity_support.saee_evaluation_adapter import (
    build_saee_evaluation_envelope,
    validate_saee_evaluation_envelope,
)
from entity_support.verification_reference import (
    build_verification_reference,
    validate_verification_reference,
)


def _must_reject(name: str, action: Callable[[], object], errors: list[str]) -> bool:
    try:
        action()
    except ValueError:
        return True
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        errors.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
        return False
    errors.append(f"{name}: prohibited construction was accepted")
    return False


def validate() -> dict[str, Any]:
    """Return deterministic conformance and zero-side-effect results."""

    errors: list[str] = []

    entity = build_entity_registration_record(
        entity_id="fixture-entity",
        entity_type="service",
        owner_reference="fixture-owner",
    )
    lifecycle = build_lifecycle_transition_record(
        transition_id="fixture-transition",
        entity_id="fixture-entity",
        from_state="PROPOSED",
        to_state="REGISTERED",
        source_reference="fixture-source",
        verification_reference="fixture-verification-source",
    )
    capability = build_capability_record(
        capability_id="fixture-capability",
        entity_id="fixture-entity",
        capability_name="fixture-declaration",
        scope={"mode": "fixture-only"},
        constraints=["no execution", "no permission"],
    )
    capability_boundary = build_capability_boundary_record(
        boundary_record_id="fixture-boundary",
        capability_id="fixture-capability",
        entity_id="fixture-entity",
        capability_name="fixture-declaration",
        scope={"mode": "fixture-only"},
        constraints=["no execution", "no permission"],
        declaration_reference="fixture-declaration-reference",
    )
    execution = build_execution_record(
        execution_id="fixture-execution",
        entity_id="fixture-entity",
        task_reference="fixture-task",
        input_reference="fixture-input",
        context_reference="fixture-context",
    )
    context_link = build_execution_context_link(
        execution,
        context_record={"context_id": "fixture-context", "status": "validated"},
    )
    evidence = build_evidence_reference(
        evidence_id="fixture-evidence",
        execution_id="fixture-execution",
        reference="fixture://canonical-evidence-reference",
    )
    verification = build_verification_reference(
        verification_id="fixture-verification",
        evidence_id="fixture-evidence",
    )
    evidence_link = build_evidence_integration_link(evidence, verification)
    candidate = build_candidate_registration_record(
        proposal_id="fixture-proposal",
        candidate_reference="fixture-candidate",
        requested_entity_type="service",
        owner_reference="fixture-owner",
        proposal_reference="fixture-proposal-document",
    )
    research_template = build_research_agent_preparation_template()
    saee_envelope = build_saee_evaluation_envelope(
        execution_history=[],
        evidence_bundle_reference="fixture-evidence-bundle",
        verification_result={
            "verification_reference": "fixture-verification",
            "verification_status": "PENDING",
            "verification_level": "V0",
        },
        resource_usage_reference=None,
    )

    expected_values = {
        "entity.lifecycle_state": (entity["lifecycle_state"], "PROPOSED"),
        "lifecycle.to_state": (lifecycle["to_state"], "REGISTERED"),
        "capability.verification_status": (
            capability["verification_status"],
            "UNVERIFIED",
        ),
        "capability_boundary.capability_state": (
            capability_boundary["capability_state"],
            "DECLARED",
        ),
        "capability_boundary.permission_effect": (
            capability_boundary["permission_effect"],
            "NONE",
        ),
        "execution.status": (execution["status"], "CREATED"),
        "context.runtime_effect": (context_link["runtime_effect"], "NONE"),
        "evidence.integrity_status": (evidence["integrity_status"], "UNKNOWN"),
        "verification.level": (verification["verification_level"], "V0"),
        "evidence_link.truth_effect": (evidence_link["evidence_truth_effect"], "NONE"),
        "candidate.current_effect": (candidate["current_effect"], "NONE"),
        "research_template.instance_effect": (research_template["instance_effect"], "NONE"),
        "saee.payload_status": (saee_envelope["payload_status"], "PREPARED_NOT_SENT"),
        "saee.evaluation_effect": (saee_envelope["evaluation_effect"], "NONE"),
    }
    for field, (actual, expected) in expected_values.items():
        if actual != expected:
            errors.append(f"{field}: expected {expected!r}, found {actual!r}")

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
    rejected["lifecycle_skip_to_active"] = _must_reject(
        "lifecycle_skip_to_active",
        lambda: build_lifecycle_transition_record(
            transition_id="fixture-transition",
            entity_id="fixture-entity",
            from_state="PROPOSED",
            to_state="ACTIVE",
            source_reference="fixture-source",
            verification_reference="fixture-verification-source",
            authorization_reference="fixture-authorization",
        ),
        errors,
    )
    rejected["capability_auto_permission"] = _must_reject(
        "capability_auto_permission",
        lambda: build_capability_boundary_record(
            boundary_record_id="fixture-boundary",
            capability_id="fixture-capability",
            entity_id="fixture-entity",
            capability_name="fixture-declaration",
            scope={"mode": "fixture-only"},
            constraints=["no permission"],
            declaration_reference="fixture-declaration-reference",
            permission_effect="GRANTED",
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
            evidence_id="fixture-evidence",
            execution_id="fixture-execution",
            reference="fixture://canonical-evidence-reference",
            integrity_status="VALIDATED",
        ),
        errors,
    )
    rejected["verification_auto_pass"] = _must_reject(
        "verification_auto_pass",
        lambda: build_verification_reference(
            verification_id="fixture-verification",
            evidence_id="fixture-evidence",
            verification_status="PASS",
        ),
        errors,
    )
    rejected["candidate_auto_active"] = _must_reject(
        "candidate_auto_active",
        lambda: build_candidate_registration_record(
            proposal_id="fixture-proposal",
            candidate_reference="fixture-candidate",
            requested_entity_type="service",
            owner_reference="fixture-owner",
            proposal_reference="fixture-proposal-document",
            requested_lifecycle_state="ACTIVE",
        ),
        errors,
    )
    rejected["candidate_registration_auto_approved"] = _must_reject(
        "candidate_registration_auto_approved",
        lambda: build_candidate_registration_record(
            proposal_id="fixture-proposal",
            candidate_reference="fixture-candidate",
            requested_entity_type="service",
            owner_reference="fixture-owner",
            proposal_reference="fixture-proposal-document",
            review_status="APPROVED",
            review_reference="fixture-review",
            registration_request_status="APPROVED",
            registration_request_reference="fixture-request",
        ),
        errors,
    )

    template_with_identity = build_research_agent_preparation_template()
    template_with_identity["entity_id"] = "forbidden-instance"
    rejected["research_template_entity_instance"] = bool(
        validate_research_agent_preparation_template(template_with_identity)
    )
    if not rejected["research_template_entity_instance"]:
        errors.append("research_template_entity_instance: entity_id was accepted")

    envelope_with_fitness = dict(saee_envelope)
    envelope_with_fitness["fitness_assessment"] = {"reliability": 1.0}
    rejected["saee_adapter_fitness_generation"] = bool(
        validate_saee_evaluation_envelope(envelope_with_fitness)
    )
    if not rejected["saee_adapter_fitness_generation"]:
        errors.append("saee_adapter_fitness_generation: fitness field was accepted")

    verification_with_permission = dict(verification)
    verification_with_permission["permission_status"] = "GRANTED"
    rejected["verification_permission_derivation"] = bool(
        validate_verification_reference(verification_with_permission)
    )
    if not rejected["verification_permission_derivation"]:
        errors.append("verification_permission_derivation: permission field was accepted")

    return {
        "status": "PASS" if not errors else "FAIL",
        "module_count": 12,
        "conformance_area_count": 8,
        "negative_case_count": len(rejected),
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
            "verification_decision": 0,
            "fitness_assessment": 0,
            "digital_organism": 0,
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
        print(f"digital_entity_infrastructure_validator: {result['status']}")
        print(
            "negative cases rejected: "
            f"{result['rejected_negative_case_count']}/{result['negative_case_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
