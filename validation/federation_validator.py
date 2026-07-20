#!/usr/bin/env python3
"""Validate the Digital Biosphere Federation Layer without dependencies.

Agent-readable contract:
- Every current entity is a proposed member with one central pending manifest.
- Central placeholders are not project-local adoption or registered membership.
- Repository identity and member identity remain independent; no repository is
  merged, moved, owned, or rewritten by federation records.
- Dependency edges require explicit evidence and never propagate authority.
- Federation roles are evidence-derived routing labels, not entity_type,
  capability, permission, trust, fitness, runtime, or organism status.
- PASS creates no Agent, runtime, organism, capability, permission, verified
  interoperability, repository merge, or C/E/V upgrade.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

MEMBER_STATUSES = ("proposed", "registered", "verified")
MANIFEST_STATUSES = ("pending", "submitted", "accepted", "rejected", "revoked")
RELATION_TYPES = ("depends_on", "implements", "verifies", "extends", "references")
FEDERATION_ROLES = (
    "foundation",
    "protocol",
    "governance",
    "evidence",
    "verification",
    "experimental",
    "unknown",
)
EXPECTED_RULES = (
    "protocol_may_be_implemented_by_service",
    "service_cannot_modify_protocol_identity",
    "verifier_not_verified_subject",
    "manifest_mediated_communication",
    "cross_project_change_requires_evolution_record",
    "reference_not_compatibility",
    "no_transitive_authority",
)
REQUIRED_MEMBER_FIELDS = {
    "member_id",
    "entity_id",
    "repository",
    "entity_type",
    "federation_status",
    "constitution_ref",
    "manifest_status",
}
REQUIRED_MANIFEST_FIELDS = {
    "manifest_id",
    "entity_id",
    "repository",
    "role",
    "dependencies",
    "constitution",
    "capability_claims",
    "evidence_refs",
    "evolution_tracking",
    "status",
}
REQUIRED_RELATION_FIELDS = {
    "relationship_id",
    "source_entity",
    "target_entity",
    "relation_type",
    "evidence_source",
    "status",
    "governance_effect",
}
MEMBER_ID_RE = re.compile(
    r"^dbio://federation-member/[a-z0-9][a-z0-9.-]*/v[0-9][A-Za-z0-9._-]*$"
)
MANIFEST_ID_RE = re.compile(
    r"^dbio://project-manifest/[a-z0-9][a-z0-9.-]*/v[0-9][A-Za-z0-9._-]*$"
)
RELATION_ID_RE = re.compile(r"^fedrel-[a-z0-9][a-z0-9-]*$")
FORBIDDEN_AUTHORITY_FIELDS = {
    "capability_id",
    "assigned_capabilities",
    "permission",
    "permissions",
    "agent_id",
    "runtime_id",
    "candidate_id",
    "digital_organism_id",
    "fitness_score",
    "ownership",
    "merged_entity_ids",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load a JSON-compatible YAML mapping."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def index_records(
    records: Any, key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    """Index mappings and reject missing or duplicate identifiers."""
    if not isinstance(records, list):
        errors.append(f"{label} must be a list")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        where = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{where}.{key} must be a non-empty string")
            continue
        if identifier in indexed:
            errors.append(f"duplicate {key}: {identifier}")
            continue
        indexed[identifier] = record
    return indexed


def reject_authority_fields(record: dict[str, Any], where: str, errors: list[str]) -> None:
    present = FORBIDDEN_AUTHORITY_FIELDS & set(record)
    if present:
        errors.append(f"{where}: forbidden authority or identity-merge fields {sorted(present)}")


def validate(
    member_doc: dict[str, Any],
    manifest_doc: dict[str, Any],
    graph_doc: dict[str, Any],
    rules_doc: dict[str, Any],
    map_doc: dict[str, Any],
    schema_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    entity_by_id = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    member_by_id = index_records(member_doc.get("members"), "member_id", "members", errors)
    manifest_by_id = index_records(
        manifest_doc.get("manifests"), "manifest_id", "manifests", errors
    )
    role_by_entity = index_records(
        map_doc.get("federation_map"), "entity_id", "federation_map", errors
    )

    member_by_entity: dict[str, dict[str, Any]] = {}
    member_status_counts: Counter[str] = Counter()
    for member_id, member in member_by_id.items():
        missing = REQUIRED_MEMBER_FIELDS - set(member)
        if missing:
            errors.append(f"{member_id}: missing fields {sorted(missing)}")
        if not MEMBER_ID_RE.match(member_id):
            errors.append(f"{member_id}: malformed member_id")
        entity_id = member.get("entity_id")
        entity = entity_by_id.get(entity_id)
        if entity is None:
            errors.append(f"{member_id}: unknown entity {entity_id!r}")
        else:
            if member.get("repository") != entity.get("repository"):
                errors.append(f"{member_id}: repository differs from canonical identity")
            if member.get("entity_type") != entity.get("entity_type"):
                errors.append(f"{member_id}: entity_type differs from canonical identity")
        if entity_id in member_by_entity:
            errors.append(f"duplicate federation member for entity {entity_id!r}")
        elif isinstance(entity_id, str):
            member_by_entity[entity_id] = member
        status = member.get("federation_status")
        if status not in MEMBER_STATUSES:
            errors.append(f"{member_id}: invalid federation_status {status!r}")
        else:
            member_status_counts[status] += 1
        if status != "proposed":
            errors.append(f"{member_id}: v0.1 member must remain proposed")
        if member.get("manifest_status") != "pending":
            errors.append(f"{member_id}: proposed member manifest_status must remain pending")
        constitution_ref = member.get("constitution_ref")
        if constitution_ref != "constitution/constitution.yaml":
            errors.append(f"{member_id}: constitution_ref must name the shared constitution")
        elif not (root / constitution_ref).is_file():
            errors.append(f"{member_id}: shared constitution reference does not exist")
        reject_authority_fields(member, member_id, errors)

    if set(member_by_entity) != set(entity_by_id):
        missing = sorted(set(entity_by_id) - set(member_by_entity))
        extra = sorted(set(member_by_entity) - set(entity_by_id))
        if missing:
            errors.append(f"entities missing proposed federation members: {missing}")
        if extra:
            errors.append(f"federation members reference unknown entities: {extra}")

    member_meta = member_doc.get("metadata", {})
    if member_meta.get("member_count") != len(member_by_id):
        errors.append("member metadata count mismatch")
    for status in MEMBER_STATUSES:
        if member_meta.get(f"{status}_member_count") != member_status_counts.get(status, 0):
            errors.append(f"member status metadata mismatch for {status}")
    if member_meta.get("project_local_manifest_adoption_count") != 0:
        errors.append("project-local manifest adoption count must remain zero")
    if member_meta.get("repository_merge_count") != 0:
        errors.append("repository merge count must remain zero")

    manifest_by_entity: dict[str, dict[str, Any]] = {}
    manifest_status_counts: Counter[str] = Counter()
    for manifest_id, manifest in manifest_by_id.items():
        missing = REQUIRED_MANIFEST_FIELDS - set(manifest)
        if missing:
            errors.append(f"{manifest_id}: missing fields {sorted(missing)}")
        if not MANIFEST_ID_RE.match(manifest_id):
            errors.append(f"{manifest_id}: malformed manifest_id")
        entity_id = manifest.get("entity_id")
        entity = entity_by_id.get(entity_id)
        member = member_by_entity.get(entity_id)
        if entity is None or member is None:
            errors.append(f"{manifest_id}: manifest entity is not a current proposed member")
        else:
            if manifest.get("repository") != entity.get("repository"):
                errors.append(f"{manifest_id}: repository differs from canonical identity")
        if entity_id in manifest_by_entity:
            errors.append(f"duplicate project manifest for entity {entity_id!r}")
        elif isinstance(entity_id, str):
            manifest_by_entity[entity_id] = manifest
        status = manifest.get("status")
        if status not in MANIFEST_STATUSES:
            errors.append(f"{manifest_id}: invalid manifest status {status!r}")
        else:
            manifest_status_counts[status] += 1
        if status != "pending":
            errors.append(f"{manifest_id}: v0.1 central manifest must remain pending")
        if manifest.get("constitution") != "constitution/constitution.yaml":
            errors.append(f"{manifest_id}: constitution reference mismatch")
        role = manifest.get("role")
        if role not in FEDERATION_ROLES:
            errors.append(f"{manifest_id}: invalid federation role {role!r}")
        mapped_role = role_by_entity.get(entity_id, {}).get("federation_role")
        if mapped_role != role:
            errors.append(f"{manifest_id}: manifest role differs from federation map")
        for list_field in (
            "dependencies",
            "capability_claims",
            "evidence_refs",
            "evolution_tracking",
        ):
            value = manifest.get(list_field)
            if not isinstance(value, list):
                errors.append(f"{manifest_id}: {list_field} must be a list")
            elif value:
                errors.append(
                    f"{manifest_id}: central pending placeholder cannot assert {list_field}"
                )
        reject_authority_fields(manifest, manifest_id, errors)

    if set(manifest_by_entity) != set(member_by_entity):
        errors.append("every proposed member must have exactly one central pending manifest")
    manifest_meta = manifest_doc.get("metadata", {})
    if manifest_meta.get("manifest_count") != len(manifest_by_id):
        errors.append("manifest metadata count mismatch")
    for status in ("pending", "submitted", "accepted"):
        if manifest_meta.get(f"{status}_manifest_count") != manifest_status_counts.get(status, 0):
            errors.append(f"manifest status metadata mismatch for {status}")
    for zero_field in (
        "project_local_manifest_count",
        "declared_dependency_count",
        "manifest_capability_claim_reference_count",
        "manifest_evidence_reference_count",
    ):
        if manifest_meta.get(zero_field) != 0:
            errors.append(f"manifest metadata {zero_field} must remain zero")

    schema_required = schema_doc.get("required")
    if not isinstance(schema_required, list) or not REQUIRED_MANIFEST_FIELDS.issubset(schema_required):
        errors.append("project-manifest schema does not require every federation manifest field")
    schema_properties = schema_doc.get("properties")
    if not isinstance(schema_properties, dict):
        errors.append("project-manifest schema properties must be a mapping")
    else:
        role_enum = schema_properties.get("role", {}).get("enum")
        if tuple(role_enum or []) != FEDERATION_ROLES:
            errors.append("project-manifest schema role enum mismatch")
        constitution_const = schema_properties.get("constitution", {}).get("const")
        if constitution_const != "constitution/constitution.yaml":
            errors.append("project-manifest schema shared constitution mismatch")

    nodes = graph_doc.get("nodes")
    node_by_entity = index_records(nodes, "entity_id", "dependency_graph.nodes", errors)
    if set(node_by_entity) != set(entity_by_id):
        errors.append("dependency graph nodes must equal canonical federation entities")
    relationships = graph_doc.get("relationships")
    relationship_by_id = index_records(
        relationships, "relationship_id", "dependency_graph.relationships", errors
    )
    relation_type_counts: Counter[str] = Counter()
    for relation_id, relationship in relationship_by_id.items():
        missing = REQUIRED_RELATION_FIELDS - set(relationship)
        if missing:
            errors.append(f"{relation_id}: missing fields {sorted(missing)}")
        if not RELATION_ID_RE.match(relation_id):
            errors.append(f"{relation_id}: malformed relationship_id")
        source = relationship.get("source_entity")
        target = relationship.get("target_entity")
        if source not in node_by_entity:
            errors.append(f"{relation_id}: unknown source entity {source!r}")
        if target not in node_by_entity:
            errors.append(f"{relation_id}: unknown target entity {target!r}")
        if source == target:
            errors.append(f"{relation_id}: self-relations cannot establish federation evidence")
        relation_type = relationship.get("relation_type")
        if relation_type not in RELATION_TYPES:
            errors.append(f"{relation_id}: invalid relation_type {relation_type!r}")
        else:
            relation_type_counts[relation_type] += 1
        evidence_source = relationship.get("evidence_source")
        if not isinstance(evidence_source, dict):
            errors.append(f"{relation_id}: evidence_source must be a mapping")
        else:
            evidence_path = evidence_source.get("path")
            locator = evidence_source.get("locator")
            if not isinstance(evidence_path, str) or not Path(evidence_path).is_file():
                errors.append(f"{relation_id}: evidence source path does not exist")
            if not isinstance(locator, str) or not locator:
                errors.append(f"{relation_id}: evidence locator must be non-empty")
        if relationship.get("status") in {"verified", "compatible", "active"}:
            errors.append(f"{relation_id}: relationship cannot claim verified interoperability")
        if relationship.get("governance_effect") != "none":
            errors.append(f"{relation_id}: dependency relation cannot grant governance authority")
        reject_authority_fields(relationship, relation_id, errors)

    graph_meta = graph_doc.get("metadata", {})
    if graph_meta.get("node_count") != len(node_by_entity):
        errors.append("dependency graph node metadata count mismatch")
    if graph_meta.get("relationship_count") != len(relationship_by_id):
        errors.append("dependency graph relationship metadata count mismatch")
    for relation_type in RELATION_TYPES:
        actual = relation_type_counts.get(relation_type, 0)
        recorded = graph_meta.get("relationship_type_distribution", {}).get(relation_type, 0)
        if actual != recorded:
            errors.append(f"dependency relationship distribution mismatch for {relation_type}")
    for zero_field in (
        "verified_interoperability_count",
        "identity_merge_count",
        "capability_effect_count",
        "permission_effect_count",
    ):
        if graph_meta.get(zero_field) != 0:
            errors.append(f"dependency graph metadata {zero_field} must remain zero")

    rules = rules_doc.get("rules")
    rule_by_id = index_records(rules, "rule_id", "interoperability_rules", errors)
    if tuple(rule_by_id) != EXPECTED_RULES:
        errors.append("interoperability rules must preserve all seven ordered rules")
    if rules_doc.get("metadata", {}).get("rule_count") != len(rule_by_id):
        errors.append("interoperability rule metadata count mismatch")
    for rule_id, rule in rule_by_id.items():
        if not isinstance(rule.get("statement"), str) or not rule.get("statement"):
            errors.append(f"{rule_id}: statement must be non-empty")
        if not isinstance(rule.get("constraint"), str) or not rule.get("constraint"):
            errors.append(f"{rule_id}: constraint must be non-empty")
        reject_authority_fields(rule, rule_id, errors)

    role_counts: Counter[str] = Counter()
    for entity_id, role_record in role_by_entity.items():
        if entity_id not in entity_by_id:
            errors.append(f"federation role references unknown entity {entity_id!r}")
        role = role_record.get("federation_role")
        if role not in FEDERATION_ROLES:
            errors.append(f"{entity_id}: invalid federation role {role!r}")
        else:
            role_counts[role] += 1
        if not isinstance(role_record.get("basis"), str) or not role_record.get("basis"):
            errors.append(f"{entity_id}: federation role requires evidence basis")
        if role == "unknown" and role_record.get("role_status") != "unresolved":
            errors.append(f"{entity_id}: unknown role must remain unresolved")
        if role != "unknown" and role_record.get("role_status") != "evidence_derived":
            errors.append(f"{entity_id}: classified role must be evidence_derived")
        reject_authority_fields(role_record, entity_id, errors)
    if set(role_by_entity) != set(entity_by_id):
        errors.append("federation map must contain exactly one role for every entity")
    map_meta = map_doc.get("metadata", {})
    if map_meta.get("entity_count") != len(role_by_entity):
        errors.append("federation map entity metadata count mismatch")
    for role in FEDERATION_ROLES:
        if map_meta.get("role_distribution", {}).get(role, 0) != role_counts.get(role, 0):
            errors.append(f"federation role distribution mismatch for {role}")
    if tuple(map_doc.get("valid_roles", [])) != FEDERATION_ROLES:
        errors.append("federation valid roles must preserve the ordered role taxonomy")

    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("federation must not create or register a capability")
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("federation must preserve every claim at C1/pending")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("evidence must be a list")
        evidence_records = []
    for evidence in evidence_records:
        if not isinstance(evidence, dict) or evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("federation must preserve every evidence record at E1/pending")
            break
    verification_records = verification_doc.get("verification_records")
    if not isinstance(verification_records, list):
        errors.append("verification_records must be a list")
        verification_records = []
    for verification in verification_records:
        if (
            not isinstance(verification, dict)
            or verification.get("verification_level") != "V0"
            or verification.get("status") != "pending"
            or verification.get("decision") != "pending"
        ):
            errors.append("federation must preserve every verification at V0/pending")
            break
    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("federation must not create a runtime")
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("federation must not create an organism candidate")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("federation cannot promote runtime or organism ecological status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("federation cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("federation cannot change fitness")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("federation must not create an Agent entity")

    return {
        "status": "FAIL" if errors else "PASS",
        "federation_member_count": len(member_by_id),
        "member_status_distribution": {
            status: member_status_counts.get(status, 0) for status in MEMBER_STATUSES
        },
        "manifest_count": len(manifest_by_id),
        "manifest_status_distribution": {
            status: manifest_status_counts.get(status, 0)
            for status in ("pending", "submitted", "accepted")
        },
        "project_local_manifest_adoption_count": 0,
        "dependency_graph_node_count": len(node_by_entity),
        "dependency_relationship_count": len(relationship_by_id),
        "dependency_relationship_distribution": {
            relation_type: relation_type_counts.get(relation_type, 0)
            for relation_type in RELATION_TYPES
        },
        "federation_role_distribution": {
            role: role_counts.get(role, 0) for role in FEDERATION_ROLES
        },
        "verified_interoperability_count": 0,
        "repository_merge_count": 0,
        "capability_count": len(capabilities) if isinstance(capabilities, list) else 0,
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "runtime_instance_count": len(runtimes) if isinstance(runtimes, list) else 0,
        "organism_candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "digital_organism_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--members", type=Path, default=root / "registry" / "federation-members.yaml")
    parser.add_argument("--manifests", type=Path, default=root / "registry" / "project-manifests.yaml")
    parser.add_argument("--graph", type=Path, default=root / "registry" / "dependency-graph.yaml")
    parser.add_argument("--rules", type=Path, default=root / "registry" / "interoperability-rules.yaml")
    parser.add_argument("--federation-map", type=Path, default=root / "registry" / "federation-map.yaml")
    parser.add_argument("--schema", type=Path, default=root / "schemas" / "project-manifest.schema.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        result = validate(
            load_json_yaml(args.members),
            load_json_yaml(args.manifests),
            load_json_yaml(args.graph),
            load_json_yaml(args.rules),
            load_json_yaml(args.federation_map),
            load_json_yaml(args.schema),
            load_json_yaml(args.entities),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"FEDERATION_VALIDATION: {result['status']}")
        print(f"members={result.get('federation_member_count', 0)}")
        print(f"manifests={result.get('manifest_count', 0)}")
        print(f"nodes={result.get('dependency_graph_node_count', 0)}")
        print(f"relationships={result.get('dependency_relationship_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
