#!/usr/bin/env python3
"""Validate Digital Biosphere capability governance registries.

Agent-readable contract:
- capabilities.yaml and entity-capabilities.yaml use JSON-compatible YAML 1.2.
- entities.yaml is the canonical identity source.
- The validator never grants a capability or permission.
- Exit 0 means the declarative registries are internally consistent.
- Exit 1 means the capability baseline must fail closed.
No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

VALID_CAPABILITY_TYPES = {
    "information",
    "computation",
    "modification",
    "external_action",
    "self_evolution",
}
VALID_RISK_LEVELS = {"unknown", "low", "moderate", "high", "critical"}
VALID_RELATIONSHIP_STATUSES = {"unknown", "proposed", "verified"}
VALID_PERMISSION_STATUSES = {"not_derived", "explicitly_granted", "explicitly_denied"}
CAPABILITY_ID_RE = re.compile(
    r"^dbio://capability/"
    r"(?P<capability_type>information|computation|modification|external_action|self_evolution)/"
    r"(?P<name>[a-z0-9][a-z0-9.-]*)/"
    r"(?P<version>v[a-zA-Z0-9][a-zA-Z0-9._-]*|unversioned|unresolved)$"
)
REQUIRED_CAPABILITY_FIELDS = {
    "capability_id",
    "name",
    "type",
    "risk_level",
    "required_permission",
    "evidence_requirement",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one mapping")
    return data


def validate(
    capabilities_doc: dict[str, Any],
    relationships_doc: dict[str, Any],
    entities_doc: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    capabilities = capabilities_doc.get("capabilities")
    relationships = relationships_doc.get("entity_capability_relationships")
    entities = entities_doc.get("entities")

    if not isinstance(capabilities, list):
        return {"status": "FAIL", "errors": ["capabilities must be a list"]}
    if not isinstance(relationships, list):
        return {"status": "FAIL", "errors": ["entity_capability_relationships must be a list"]}
    if not isinstance(entities, list):
        return {"status": "FAIL", "errors": ["entities must be a list"]}

    entity_ids = {
        entity.get("entity_id")
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("entity_id"), str)
    }
    capability_ids: set[str] = set()
    capability_by_id: dict[str, dict[str, Any]] = {}
    capability_counts: Counter[str] = Counter()

    for index, capability in enumerate(capabilities):
        where = f"capabilities[{index}]"
        if not isinstance(capability, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_CAPABILITY_FIELDS - set(capability)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        capability_id = capability.get("capability_id")
        capability_type = capability.get("type")
        risk_level = capability.get("risk_level")
        if not isinstance(capability_id, str):
            errors.append(f"{where}.capability_id must be a string")
            continue
        if capability_id in capability_ids:
            errors.append(f"duplicate capability_id: {capability_id}")
        capability_ids.add(capability_id)
        capability_by_id[capability_id] = capability
        match = CAPABILITY_ID_RE.match(capability_id)
        if not match:
            errors.append(f"{capability_id}: malformed capability_id")
        elif match.group("capability_type") != capability_type:
            errors.append(f"{capability_id}: capability_id type mismatch")
        if capability_type not in VALID_CAPABILITY_TYPES:
            errors.append(f"{capability_id}: invalid type {capability_type!r}")
        else:
            capability_counts[capability_type] += 1
        if risk_level not in VALID_RISK_LEVELS:
            errors.append(f"{capability_id}: invalid risk_level {risk_level!r}")
        required_permission = capability.get("required_permission")
        if isinstance(required_permission, bool):
            errors.append(f"{capability_id}: required_permission cannot be boolean or inferred")
        if isinstance(required_permission, str) and required_permission.lower() in {
            "auto",
            "automatic",
            "derived",
            "inherited",
        }:
            errors.append(f"{capability_id}: permission cannot be auto-derived")
        evidence_requirement = capability.get("evidence_requirement")
        if not isinstance(evidence_requirement, (str, list, dict)):
            errors.append(f"{capability_id}: evidence_requirement must be explicit")

    relationship_entity_ids: set[str] = set()
    relationship_counts: Counter[str] = Counter()
    potential_evidence_count = 0
    assigned_count = 0

    for index, relationship in enumerate(relationships):
        where = f"entity_capability_relationships[{index}]"
        if not isinstance(relationship, dict):
            errors.append(f"{where} must be a mapping")
            continue
        entity_id = relationship.get("entity_id")
        status = relationship.get("relationship_status")
        permission_status = relationship.get("permission_status")
        assigned = relationship.get("assigned_capabilities")
        permission_evidence = relationship.get("permission_evidence")
        potentials = relationship.get("potential_capability_evidence")

        if entity_id not in entity_ids:
            errors.append(f"{where}: unknown entity reference {entity_id!r}")
        elif entity_id in relationship_entity_ids:
            errors.append(f"duplicate entity relationship: {entity_id}")
        else:
            relationship_entity_ids.add(entity_id)

        if status not in VALID_RELATIONSHIP_STATUSES:
            errors.append(f"{entity_id}: invalid relationship_status {status!r}")
        else:
            relationship_counts[status] += 1
        if permission_status not in VALID_PERMISSION_STATUSES:
            errors.append(f"{entity_id}: invalid permission_status {permission_status!r}")
        if not isinstance(assigned, list):
            errors.append(f"{entity_id}: assigned_capabilities must be a list")
            assigned = []
        if not isinstance(permission_evidence, list):
            errors.append(f"{entity_id}: permission_evidence must be a list")
            permission_evidence = []
        if not isinstance(potentials, list):
            errors.append(f"{entity_id}: potential_capability_evidence must be a list")
            potentials = []

        if status == "unknown":
            if assigned:
                errors.append(f"{entity_id}: unknown relationship cannot assign capabilities")
            if permission_status != "not_derived":
                errors.append(f"{entity_id}: unknown relationship must keep permission not_derived")
            if permission_evidence:
                errors.append(f"{entity_id}: unknown relationship cannot contain permission evidence")

        for capability_id in assigned:
            assigned_count += 1
            if capability_id not in capability_by_id:
                errors.append(f"{entity_id}: assigned capability does not exist: {capability_id}")
            if status != "verified":
                errors.append(f"{entity_id}: assignment requires verified relationship")
            if permission_status != "explicitly_granted":
                errors.append(f"{entity_id}: assignment requires explicit permission")
            if not permission_evidence:
                errors.append(f"{entity_id}: assignment requires permission evidence")

        evidence_ids: set[str] = set()
        for potential in potentials:
            potential_evidence_count += 1
            if not isinstance(potential, dict):
                errors.append(f"{entity_id}: potential evidence must be a mapping")
                continue
            evidence_id = potential.get("evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id:
                errors.append(f"{entity_id}: potential evidence requires evidence_id")
            elif evidence_id in evidence_ids:
                errors.append(f"{entity_id}: duplicate potential evidence_id {evidence_id}")
            else:
                evidence_ids.add(evidence_id)
            potential_type = potential.get("potential_type")
            risk_level = potential.get("risk_level")
            if potential_type not in VALID_CAPABILITY_TYPES | {"unknown"}:
                errors.append(f"{entity_id}: invalid potential_type {potential_type!r}")
            if risk_level not in VALID_RISK_LEVELS:
                errors.append(f"{entity_id}: invalid potential risk_level {risk_level!r}")
            if potential.get("status") != "potential_evidence_only":
                errors.append(f"{entity_id}: potential evidence status must remain evidence-only")
            if "capability_id" in potential:
                errors.append(f"{entity_id}: potential evidence must not create capability_id")
            for source in potential.get("source_paths", []):
                if not Path(source).exists():
                    errors.append(f"{entity_id}: missing potential evidence source {source}")

    missing_relationships = entity_ids - relationship_entity_ids
    extra_relationships = relationship_entity_ids - entity_ids
    if missing_relationships:
        errors.append(f"entities missing capability relationship: {sorted(missing_relationships)}")
    if extra_relationships:
        errors.append(f"capability relationships reference extra entities: {sorted(extra_relationships)}")

    capability_meta = capabilities_doc.get("metadata", {})
    relationship_meta = relationships_doc.get("metadata", {})
    expected_counts = capabilities_doc.get("classification_counts", {})
    for capability_type in VALID_CAPABILITY_TYPES:
        if expected_counts.get(capability_type, 0) != capability_counts.get(capability_type, 0):
            errors.append(f"capability classification count mismatch for {capability_type}")
    if capability_meta.get("confirmed_capability_count") != len(capabilities):
        errors.append("metadata.confirmed_capability_count mismatch")
    if relationship_meta.get("entity_count") != len(relationships):
        errors.append("relationship metadata.entity_count mismatch")
    if relationship_meta.get("assigned_relationship_count") != assigned_count:
        errors.append("metadata.assigned_relationship_count mismatch")
    if relationship_meta.get("potential_capability_evidence_count") != potential_evidence_count:
        errors.append("metadata.potential_capability_evidence_count mismatch")
    if capability_meta.get("potential_capability_evidence_count") != potential_evidence_count:
        errors.append("capability metadata potential evidence count mismatch")

    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entities),
        "registered_capability_count": len(capabilities),
        "assigned_capability_count": assigned_count,
        "potential_capability_evidence_count": potential_evidence_count,
        "capability_classification_counts": {
            key: capability_counts.get(key, 0)
            for key in (
                "information",
                "computation",
                "modification",
                "external_action",
                "self_evolution",
            )
        },
        "relationship_status_counts": {
            key: relationship_counts.get(key, 0)
            for key in ("unknown", "proposed", "verified")
        },
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capabilities",
        type=Path,
        default=root / "registry" / "capabilities.yaml",
    )
    parser.add_argument(
        "--relationships",
        type=Path,
        default=root / "registry" / "entity-capabilities.yaml",
    )
    parser.add_argument(
        "--entities",
        type=Path,
        default=root / "registry" / "entities.yaml",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        result = validate(
            load_json_yaml(args.capabilities),
            load_json_yaml(args.relationships),
            load_json_yaml(args.entities),
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"CAPABILITY_VALIDATION: {result['status']}")
        print(f"entities={result.get('entity_count', 0)}")
        print(f"registered_capabilities={result.get('registered_capability_count', 0)}")
        print(f"assigned_capabilities={result.get('assigned_capability_count', 0)}")
        print(f"potential_evidence={result.get('potential_capability_evidence_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

