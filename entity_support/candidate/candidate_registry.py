"""Compose candidate workflow records without creating a canonical registry.

Agent-readable contract:
- Candidate Registry here means an in-memory support record, not registry/entities.yaml.
- Proposal, Review, and Registration Request remain separate nested records.
- An ACCEPTED request still has current_effect=NONE and is not a registered Entity.
- The Research Agent value is a declaration template, not an Agent or Capability instance.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from entity_support.candidate.candidate_proposal import validate_candidate_proposal
from entity_support.candidate.candidate_registration_request import (
    validate_candidate_registration_request,
)
from entity_support.candidate.candidate_review import validate_candidate_review

CANDIDATE_REGISTRY_FIELDS = (
    "candidate_id",
    "proposal",
    "review",
    "registration_request",
    "current_effect",
)
NO_CURRENT_EFFECT = "NONE"

RESEARCH_AGENT_PROPOSED_CAPABILITIES = (
    "literature_analysis",
    "knowledge_synthesis",
    "experiment_planning",
    "code_assistance",
)
RESEARCH_AGENT_CANDIDATE_TEMPLATE_FIELDS = (
    "role",
    "proposed_capabilities",
)
_RESEARCH_AGENT_CANDIDATE_TEMPLATE: dict[str, object] = {
    "role": "research_agent",
    "proposed_capabilities": list(RESEARCH_AGENT_PROPOSED_CAPABILITIES),
}


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_research_agent_candidate_template(
    template: Mapping[str, Any],
) -> list[str]:
    """Return template errors without creating an Agent or Capability record."""

    errors: list[str] = []
    missing = [
        field for field in RESEARCH_AGENT_CANDIDATE_TEMPLATE_FIELDS if field not in template
    ]
    extra = sorted(set(template) - set(RESEARCH_AGENT_CANDIDATE_TEMPLATE_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")
    if template.get("role") != "research_agent":
        errors.append("role must remain research_agent")
    proposed_capabilities = template.get("proposed_capabilities")
    if not isinstance(proposed_capabilities, list):
        errors.append("proposed_capabilities must be a list")
    elif tuple(proposed_capabilities) != RESEARCH_AGENT_PROPOSED_CAPABILITIES:
        errors.append("proposed_capabilities must use the bounded declaration template")
    return errors


def build_research_agent_candidate_template() -> dict[str, object]:
    """Return the bounded declaration template without creating an Agent."""

    template = deepcopy(_RESEARCH_AGENT_CANDIDATE_TEMPLATE)
    errors = validate_research_agent_candidate_template(template)
    if errors:
        raise ValueError("; ".join(errors))
    return template


def validate_candidate_registry_record(record: Mapping[str, Any]) -> list[str]:
    """Validate linked workflow records while preserving zero current effect."""

    errors: list[str] = []
    missing = [field for field in CANDIDATE_REGISTRY_FIELDS if field not in record]
    extra = sorted(set(record) - set(CANDIDATE_REGISTRY_FIELDS))
    if missing:
        errors.append(f"missing fields: {missing}")
    if extra:
        errors.append(f"unexpected fields: {extra}")

    candidate_id = record.get("candidate_id")
    if not _is_non_empty_string(candidate_id):
        errors.append("candidate_id must be a non-empty string")

    proposal = record.get("proposal")
    if not isinstance(proposal, Mapping):
        errors.append("proposal must be a mapping")
    else:
        errors.extend(f"proposal: {error}" for error in validate_candidate_proposal(proposal))
        if proposal.get("candidate_id") != candidate_id:
            errors.append("proposal candidate_id must match registry candidate_id")

    review = record.get("review")
    if review is not None and not isinstance(review, Mapping):
        errors.append("review must be null or a mapping")
    elif isinstance(review, Mapping):
        errors.extend(f"review: {error}" for error in validate_candidate_review(review))
        if review.get("candidate_id") != candidate_id:
            errors.append("review candidate_id must match registry candidate_id")

    request = record.get("registration_request")
    if request is not None and not isinstance(request, Mapping):
        errors.append("registration_request must be null or a mapping")
    elif isinstance(request, Mapping):
        errors.extend(
            f"registration_request: {error}"
            for error in validate_candidate_registration_request(request)
        )
        if request.get("candidate_id") != candidate_id:
            errors.append("registration request candidate_id must match registry candidate_id")
        if request.get("status") in {"SUBMITTED", "ACCEPTED"} and (
            not isinstance(review, Mapping) or review.get("review_status") != "APPROVED"
        ):
            errors.append("SUBMITTED or ACCEPTED request requires an APPROVED review")

    if record.get("current_effect") != NO_CURRENT_EFFECT:
        errors.append("current_effect must remain NONE")
    return errors


def build_candidate_registry_record(
    *,
    candidate_id: str,
    proposal: Mapping[str, Any],
    review: Mapping[str, Any] | None = None,
    registration_request: Mapping[str, Any] | None = None,
    current_effect: str = NO_CURRENT_EFFECT,
) -> dict[str, object]:
    """Return a linked candidate record without persisting or registering it."""

    record: dict[str, object] = {
        "candidate_id": candidate_id,
        "proposal": dict(proposal),
        "review": dict(review) if review is not None else None,
        "registration_request": (
            dict(registration_request) if registration_request is not None else None
        ),
        "current_effect": current_effect,
    }
    errors = validate_candidate_registry_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


__all__ = [
    "CANDIDATE_REGISTRY_FIELDS",
    "NO_CURRENT_EFFECT",
    "RESEARCH_AGENT_CANDIDATE_TEMPLATE_FIELDS",
    "RESEARCH_AGENT_PROPOSED_CAPABILITIES",
    "build_candidate_registry_record",
    "build_research_agent_candidate_template",
    "validate_candidate_registry_record",
    "validate_research_agent_candidate_template",
]
