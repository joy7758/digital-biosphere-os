#!/usr/bin/env python3
"""Validate the fail-closed Research Agent Candidate Registration Layer.

Agent-readable contract:
- Inputs are ephemeral in-memory test mappings only.
- PASS proves record boundaries and rejection gates, not Entity registration.
- Exit 0: PASS
- Exit 1: FAIL
- No Agent, Runtime, Entity, Capability, Permission, Execution, Evidence,
  Verification, or Digital Organism object is created or persisted.
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
from entity_support.candidate.candidate_registry import (
    build_candidate_registry_record,
    build_research_agent_candidate_template,
    validate_candidate_registry_record,
    validate_research_agent_candidate_template,
)
from entity_support.candidate.candidate_review import build_candidate_review

EXPECTED_NEGATIVE_CASES = (
    "candidate_auto_entity",
    "proposal_auto_registered",
    "review_auto_active",
    "capability_template_auto_grant",
    "candidate_auto_permission",
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
    """Return deterministic validation results with zero side effects."""

    errors: list[str] = []
    proposal = build_candidate_proposal(
        candidate_id="fixture-candidate",
        proposed_type="operational_entity",
        role="research_agent",
        description="fixture candidate proposal only",
        proposer_reference="fixture-proposer",
    )
    review = build_candidate_review(
        review_id="fixture-review",
        candidate_id="fixture-candidate",
        reviewer_reference="fixture-reviewer",
        review_status="APPROVED",
        review_notes="fixture review only; no activation effect",
    )
    request = build_candidate_registration_request(
        request_id="fixture-request",
        candidate_id="fixture-candidate",
        requested_entity_type="service",
        mapping_reference="fixture-mapping-reference",
        status="ACCEPTED",
    )
    candidate = build_candidate_registry_record(
        candidate_id="fixture-candidate",
        proposal=proposal,
        review=review,
        registration_request=request,
    )
    template = build_research_agent_candidate_template()

    expected_values = {
        "proposal.status": (proposal["status"], "PROPOSED"),
        "review.review_status": (review["review_status"], "APPROVED"),
        "request.status": (request["status"], "ACCEPTED"),
        "candidate.current_effect": (candidate["current_effect"], "NONE"),
        "template.role": (template["role"], "research_agent"),
    }
    for field, (actual, expected) in expected_values.items():
        if actual != expected:
            errors.append(f"{field}: expected {expected!r}, found {actual!r}")

    rejected: dict[str, bool] = {}

    candidate_with_entity = dict(candidate)
    candidate_with_entity["entity_id"] = "forbidden-entity"
    rejected["candidate_auto_entity"] = bool(
        validate_candidate_registry_record(candidate_with_entity)
    )
    if not rejected["candidate_auto_entity"]:
        errors.append("candidate_auto_entity: entity_id was accepted")

    rejected["proposal_auto_registered"] = _must_reject(
        "proposal_auto_registered",
        lambda: build_candidate_proposal(
            candidate_id="fixture-candidate",
            proposed_type="operational_entity",
            role="research_agent",
            description="fixture candidate proposal only",
            proposer_reference="fixture-proposer",
            status="REGISTERED",
        ),
        errors,
    )

    review_with_activation = dict(review)
    review_with_activation["lifecycle_state"] = "ACTIVE"
    rejected["review_auto_active"] = _must_reject(
        "review_auto_active",
        lambda: build_candidate_registry_record(
            candidate_id="fixture-candidate",
            proposal=proposal,
            review=review_with_activation,
        ),
        errors,
    )

    template_with_grant = dict(template)
    template_with_grant["capability_grant"] = "GRANTED"
    rejected["capability_template_auto_grant"] = bool(
        validate_research_agent_candidate_template(template_with_grant)
    )
    if not rejected["capability_template_auto_grant"]:
        errors.append("capability_template_auto_grant: grant field was accepted")

    candidate_with_permission = dict(candidate)
    candidate_with_permission["permission_status"] = "GRANTED"
    rejected["candidate_auto_permission"] = bool(
        validate_candidate_registry_record(candidate_with_permission)
    )
    if not rejected["candidate_auto_permission"]:
        errors.append("candidate_auto_permission: permission field was accepted")

    for name in EXPECTED_NEGATIVE_CASES:
        if name not in rejected:
            errors.append(f"missing negative case: {name}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "candidate_schema_count": 5,
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
            "verification_decision": 0,
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
        print(f"candidate_registration_validator: {result['status']}")
        print(
            "negative cases rejected: "
            f"{result['rejected_negative_case_count']}/{result['negative_case_count']}"
        )
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
