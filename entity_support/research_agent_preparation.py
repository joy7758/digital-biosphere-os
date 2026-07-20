"""Provide a non-instantiating Research Agent preparation template.

Agent-readable contract:
- OPERATIONAL_ENTITY is an architecture role classification, not a new DBOS
  canonical entity_type and not an Entity identity.
- RESEARCH_AGENT is role metadata, not an Agent instance.
- Capability entries are declaration templates without capability_id,
  verification, authorization, permission, or execution effect.
- Human oversight is mandatory and publication authority remains NONE.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

RESEARCH_AGENT_CAPABILITY_NAMES = (
    "LITERATURE_ANALYSIS",
    "KNOWLEDGE_SYNTHESIS",
    "EXPERIMENT_PLANNING",
    "CODE_ASSISTANCE",
    "EVIDENCE_ORGANIZATION",
)
PROHIBITED_INSTANCE_KEYS = frozenset(
    {
        "agent_id",
        "entity_id",
        "runtime_id",
        "capability_id",
        "permission",
        "permission_id",
        "permission_status",
    }
)

_RESEARCH_AGENT_PREPARATION_TEMPLATE: dict[str, Any] = {
    "template_id": "RESEARCH_AGENT_PREPARATION_TEMPLATE_V0_1",
    "entity_classification": "OPERATIONAL_ENTITY",
    "research_role": "RESEARCH_AGENT",
    "template_status": "PREPARATION_ONLY",
    "identity_status": "NOT_ASSIGNED",
    "lifecycle_status": "PROPOSED_CANDIDATE_ONLY",
    "research_role_metadata": {
        "purpose": "RESEARCH_ASSISTANCE",
        "responsibility": "ASSISTANCE_ONLY",
        "human_oversight_required": True,
        "publication_authority": "NONE",
        "research_conclusion_authority": "NONE",
    },
    "capability_profile_template": [
        {
            "capability_name": name,
            "template_status": "DECLARATION_TEMPLATE",
            "risk_level": "UNKNOWN",
            "permission_effect": "NONE",
        }
        for name in RESEARCH_AGENT_CAPABILITY_NAMES
    ],
    "forbidden_actions": [
        "AUTONOMOUS_PUBLICATION",
        "RAW_DATA_MODIFICATION",
        "HISTORICAL_EVIDENCE_DELETION",
        "IDENTITY_MODIFICATION",
        "AUTHORIZATION_BYPASS",
        "RESEARCH_TASK_EXECUTION",
    ],
    "instance_effect": "NONE",
}


def _find_prohibited_keys(value: object, path: str = "template") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_INSTANCE_KEYS:
                errors.append(f"prohibited instance key: {child_path}")
            errors.extend(_find_prohibited_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_prohibited_keys(child, f"{path}[{index}]"))
    return errors


def validate_research_agent_preparation_template(template: dict[str, Any]) -> list[str]:
    """Return template errors without registering a Research Agent."""

    errors = _find_prohibited_keys(template)
    if template.get("entity_classification") != "OPERATIONAL_ENTITY":
        errors.append("entity_classification must remain OPERATIONAL_ENTITY")
    if template.get("research_role") != "RESEARCH_AGENT":
        errors.append("research_role must remain RESEARCH_AGENT")
    if template.get("template_status") != "PREPARATION_ONLY":
        errors.append("template_status must remain PREPARATION_ONLY")
    if template.get("identity_status") != "NOT_ASSIGNED":
        errors.append("identity_status must remain NOT_ASSIGNED")
    if template.get("instance_effect") != "NONE":
        errors.append("instance_effect must remain NONE")

    role_metadata = template.get("research_role_metadata")
    if not isinstance(role_metadata, dict):
        errors.append("research_role_metadata must be a mapping")
    else:
        if role_metadata.get("human_oversight_required") is not True:
            errors.append("human oversight must remain required")
        for field in ("publication_authority", "research_conclusion_authority"):
            if role_metadata.get(field) != "NONE":
                errors.append(f"{field} must remain NONE")

    profile = template.get("capability_profile_template")
    if not isinstance(profile, list):
        errors.append("capability_profile_template must be a list")
    else:
        names = [item.get("capability_name") for item in profile if isinstance(item, dict)]
        if tuple(names) != RESEARCH_AGENT_CAPABILITY_NAMES:
            errors.append("capability profile must use the bounded reference template")
        for index, item in enumerate(profile):
            if not isinstance(item, dict):
                errors.append(f"capability_profile_template[{index}] must be a mapping")
                continue
            if item.get("template_status") != "DECLARATION_TEMPLATE":
                errors.append(f"capability_profile_template[{index}] is not template-only")
            if item.get("permission_effect") != "NONE":
                errors.append(f"capability_profile_template[{index}] has permission effect")
    return errors


def build_research_agent_preparation_template() -> dict[str, Any]:
    """Return a deep copy of the bounded template without creating an Agent."""

    template = deepcopy(_RESEARCH_AGENT_PREPARATION_TEMPLATE)
    errors = validate_research_agent_preparation_template(template)
    if errors:
        raise ValueError("; ".join(errors))
    return template


__all__ = [
    "PROHIBITED_INSTANCE_KEYS",
    "RESEARCH_AGENT_CAPABILITY_NAMES",
    "build_research_agent_preparation_template",
    "validate_research_agent_preparation_template",
]
