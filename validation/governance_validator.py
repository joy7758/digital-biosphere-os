#!/usr/bin/env python3
"""Validate the Governance Archetype Layer without third-party packages.

Agent-readable contract:
- Exactly three archetype definitions describe federation, hierarchy, and
  ecology; definitions do not bind entities or create authority.
- The v0.1 binding registry is empty and every future record defaults to
  pending until attributable evidence and approval exist.
- Transition definitions are admissibility rules, not executed transitions.
- Evaluation scores remain null and cannot select an archetype or affect
  identity, capability, permission, fitness, runtime, organism, or C/E/V state.
- PASS proves local structural consistency only and grants no authority.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ARCHETYPE_NAMES = ("federation", "hierarchy", "ecology")
ARCHETYPE_MODELS = {
    "federation": {
        "authority_model": "distributed",
        "decision_model": "consent / protocol",
        "strength": ["autonomy", "interoperability"],
        "risk": ["coordination cost"],
    },
    "hierarchy": {
        "authority_model": "delegated",
        "decision_model": "command chain",
        "strength": ["efficiency"],
        "risk": ["centralization"],
    },
    "ecology": {
        "authority_model": "emergent",
        "decision_model": "selection pressure",
        "strength": ["adaptation"],
        "risk": ["unpredictability"],
    },
}
BINDING_STATUSES = ("pending", "active", "suspended", "revoked", "retired")
TRANSITION_STATUSES = (
    "defined_not_executed",
    "proposed",
    "approved",
    "executed",
    "rejected",
    "revoked",
)
EXPECTED_TRANSITION_TRIGGERS = {
    "sufficient_evidence",
    "stable_interaction",
    "verified_runtime",
}
REQUIRED_TRANSITION_EXECUTION_FIELDS = {
    "subject_entity_or_scope",
    "evidence_refs",
    "verification_ref",
    "decision_authority",
    "identity_continuity_ref",
    "rollback_plan",
    "evolution_record",
    "timestamp",
}
EVALUATION_DIMENSIONS = (
    "coordination_efficiency",
    "autonomy",
    "stability",
    "adaptability",
    "centralization_risk",
)
REQUIRED_ARCHETYPE_FIELDS = {
    "archetype_id",
    "name",
    "description",
    "authority_model",
    "decision_model",
    "strength",
    "risk",
}
REQUIRED_BINDING_FIELDS = {
    "binding_id",
    "entity_id",
    "archetype_id",
    "scope",
    "status",
    "evidence_ref",
}
REQUIRED_TRANSITION_FIELDS = {"transition_id", "from", "to", "trigger", "requirements"}
ARCHETYPE_ID_RE = re.compile(
    r"^dbio://governance-archetype/(federation|hierarchy|ecology)/v[0-9][A-Za-z0-9._-]*$"
)
BINDING_ID_RE = re.compile(
    r"^dbio://governance-binding/[a-z0-9][a-z0-9.-]*/(federation|hierarchy|ecology)/v[0-9][A-Za-z0-9._-]*$"
)
TRANSITION_ID_RE = re.compile(
    r"^dbio://governance-transition/(federation|hierarchy|ecology)-to-(federation|hierarchy|ecology)/v[0-9][A-Za-z0-9._-]*$"
)
IDENTITY_MUTATION_FIELDS = {
    "canonical_id",
    "entity_type",
    "repository",
    "owner",
    "parent_entity",
    "child_entities",
    "lineage",
    "identity_status",
}
CAPABILITY_AUTHORITY_FIELDS = {
    "capability_id",
    "capabilities",
    "assigned_capabilities",
    "capability_assignment_status",
    "capability_grants",
}
PERMISSION_AUTHORITY_FIELDS = {
    "permission",
    "permissions",
    "permission_status",
    "permission_grants",
    "required_permission",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping."""
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
    """Index mapping records and reject missing or duplicate identifiers."""
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


def reject_governance_authority_fields(
    record: dict[str, Any], where: str, errors: list[str]
) -> None:
    """Reject fields that would mutate identity or grant capability/permission."""
    for label, forbidden in (
        ("identity mutation", IDENTITY_MUTATION_FIELDS),
        ("capability authority", CAPABILITY_AUTHORITY_FIELDS),
        ("permission authority", PERMISSION_AUTHORITY_FIELDS),
    ):
        present = forbidden & set(record)
        if present:
            errors.append(f"{where}: forbidden {label} fields {sorted(present)}")


def require_none_effects(metadata: Any, label: str, errors: list[str]) -> None:
    """Require every declared cross-layer effect to remain none or zero."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in ("identity_effect", "capability_effect", "permission_effect", "authority_effect"):
        if field in metadata and metadata.get(field) != "none":
            errors.append(f"{label}.{field} must remain none")
    for field in (
        "identity_change_count",
        "capability_effect_count",
        "permission_effect_count",
        "automatic_binding_count",
        "automatic_transition_count",
    ):
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label}.{field} must remain zero")


def validate(
    archetype_doc: dict[str, Any],
    binding_doc: dict[str, Any],
    transition_doc: dict[str, Any],
    evaluation_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    federation_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate taxonomy, empty application state, and cross-layer boundaries."""
    errors: list[str] = []
    entity_by_id = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    archetype_by_id = index_records(
        archetype_doc.get("governance_archetypes"),
        "archetype_id",
        "governance_archetypes",
        errors,
    )

    archetype_name_counts: Counter[str] = Counter()
    for archetype_id, archetype in archetype_by_id.items():
        missing = REQUIRED_ARCHETYPE_FIELDS - set(archetype)
        if missing:
            errors.append(f"{archetype_id}: missing fields {sorted(missing)}")
        if not ARCHETYPE_ID_RE.match(archetype_id):
            errors.append(f"{archetype_id}: malformed archetype_id")
        name = archetype.get("name")
        if name not in ARCHETYPE_NAMES:
            errors.append(f"{archetype_id}: invalid archetype name {name!r}")
            continue
        archetype_name_counts[name] += 1
        expected = ARCHETYPE_MODELS[name]
        for field, expected_value in expected.items():
            if archetype.get(field) != expected_value:
                errors.append(f"{archetype_id}: {field} differs from the v0.1 definition")
        if not isinstance(archetype.get("description"), str) or not archetype.get("description"):
            errors.append(f"{archetype_id}: description must be non-empty")
        reject_governance_authority_fields(archetype, archetype_id, errors)

    if tuple(archetype_name_counts) != ARCHETYPE_NAMES:
        errors.append("archetypes must preserve federation, hierarchy, ecology order")
    if any(archetype_name_counts.get(name, 0) != 1 for name in ARCHETYPE_NAMES):
        errors.append("exactly one definition is required for each governance archetype")
    archetype_meta = archetype_doc.get("metadata", {})
    if archetype_meta.get("archetype_count") != len(archetype_by_id):
        errors.append("archetype metadata count mismatch")
    for name in ARCHETYPE_NAMES:
        if archetype_meta.get("archetype_distribution", {}).get(name) != 1:
            errors.append(f"archetype distribution mismatch for {name}")
    if archetype_meta.get("binding_count") != 0:
        errors.append("archetype definition metadata cannot claim a binding")
    require_none_effects(archetype_meta, "archetype", errors)

    bindings = binding_doc.get("governance_bindings")
    binding_by_id = index_records(bindings, "binding_id", "governance_bindings", errors)
    binding_status_counts: Counter[str] = Counter()
    for binding_id, binding in binding_by_id.items():
        missing = REQUIRED_BINDING_FIELDS - set(binding)
        if missing:
            errors.append(f"{binding_id}: missing fields {sorted(missing)}")
        if not BINDING_ID_RE.match(binding_id):
            errors.append(f"{binding_id}: malformed binding_id")
        if binding.get("entity_id") not in entity_by_id:
            errors.append(f"{binding_id}: unknown entity {binding.get('entity_id')!r}")
        if binding.get("archetype_id") not in archetype_by_id:
            errors.append(f"{binding_id}: unknown archetype {binding.get('archetype_id')!r}")
        status = binding.get("status")
        if status not in BINDING_STATUSES:
            errors.append(f"{binding_id}: invalid binding status {status!r}")
        else:
            binding_status_counts[status] += 1
        if status != "pending":
            errors.append(f"{binding_id}: v0.1 bindings must remain pending")
        if not isinstance(binding.get("scope"), str) or not binding.get("scope"):
            errors.append(f"{binding_id}: scope must be a non-empty string")
        evidence_ref = binding.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref:
            errors.append(f"{binding_id}: evidence_ref must be a non-empty string")
        reject_governance_authority_fields(binding, binding_id, errors)

    binding_meta = binding_doc.get("metadata", {})
    if binding_meta.get("binding_count") != len(binding_by_id):
        errors.append("binding metadata count mismatch")
    if binding_meta.get("pending_binding_count") != binding_status_counts.get("pending", 0):
        errors.append("pending binding metadata count mismatch")
    if binding_meta.get("active_binding_count") != binding_status_counts.get("active", 0):
        errors.append("active binding metadata count mismatch")
    if binding_by_id:
        errors.append("v0.1 baseline must not automatically bind current entities")
    require_none_effects(binding_meta, "binding", errors)

    transition_definitions = transition_doc.get("transition_definitions")
    transition_by_id = index_records(
        transition_definitions,
        "transition_id",
        "transition_definitions",
        errors,
    )
    for transition_id, transition in transition_by_id.items():
        missing = REQUIRED_TRANSITION_FIELDS - set(transition)
        if missing:
            errors.append(f"{transition_id}: missing fields {sorted(missing)}")
        match = TRANSITION_ID_RE.match(transition_id)
        if not match:
            errors.append(f"{transition_id}: malformed transition_id")
        source = transition.get("from")
        target = transition.get("to")
        if source not in archetype_by_id:
            errors.append(f"{transition_id}: unknown source archetype {source!r}")
        if target not in archetype_by_id:
            errors.append(f"{transition_id}: unknown target archetype {target!r}")
        if source == target:
            errors.append(f"{transition_id}: source and target must differ")
        if set(transition.get("trigger", [])) != EXPECTED_TRANSITION_TRIGGERS:
            errors.append(f"{transition_id}: transition triggers cannot bypass evidence, interaction, or runtime verification")
        if not REQUIRED_TRANSITION_EXECUTION_FIELDS.issubset(
            set(transition.get("requirements", []))
        ):
            errors.append(f"{transition_id}: transition requirements are incomplete")
        if transition.get("status") not in TRANSITION_STATUSES:
            errors.append(f"{transition_id}: invalid transition status")
        if transition.get("status") != "defined_not_executed":
            errors.append(f"{transition_id}: v0.1 transition definition must remain unexecuted")
        if transition.get("authority_effect") != "none":
            errors.append(f"{transition_id}: transition definition cannot create authority")
        reject_governance_authority_fields(transition, transition_id, errors)

    executed = transition_doc.get("executed_transitions")
    if not isinstance(executed, list):
        errors.append("executed_transitions must be a list")
        executed = []
    if executed:
        errors.append("v0.1 baseline cannot contain an executed governance transition")
    transition_meta = transition_doc.get("metadata", {})
    if transition_meta.get("transition_definition_count") != len(transition_by_id):
        errors.append("transition definition metadata count mismatch")
    if transition_meta.get("executed_transition_count") != len(executed):
        errors.append("executed transition metadata count mismatch")
    require_none_effects(transition_meta, "transition", errors)

    dimensions = evaluation_doc.get("evaluation_dimensions")
    dimension_by_id = index_records(
        dimensions, "dimension_id", "evaluation_dimensions", errors
    )
    if tuple(dimension_by_id) != EVALUATION_DIMENSIONS:
        errors.append("evaluation dimensions must preserve the five ordered dimensions")
    for dimension_id, dimension in dimension_by_id.items():
        if not isinstance(dimension.get("description"), str) or not dimension.get("description"):
            errors.append(f"{dimension_id}: description must be non-empty")
        if dimension.get("score") is not None:
            errors.append(f"{dimension_id}: score must remain null")
        reject_governance_authority_fields(dimension, dimension_id, errors)
    if evaluation_doc.get("aggregate_score") is not None:
        errors.append("aggregate governance evaluation score must remain null")
    evaluations = evaluation_doc.get("evaluations")
    if not isinstance(evaluations, list) or evaluations:
        errors.append("v0.1 governance evaluations must remain an empty list")
    evaluation_meta = evaluation_doc.get("metadata", {})
    if evaluation_meta.get("evaluation_dimension_count") != len(dimension_by_id):
        errors.append("evaluation dimension metadata count mismatch")
    if evaluation_meta.get("non_null_score_count") != 0:
        errors.append("non-null governance evaluation score count must remain zero")
    if evaluation_meta.get("evaluation_record_count") != 0:
        errors.append("governance evaluation record count must remain zero")
    if evaluation_meta.get("selection_result_count") != 0:
        errors.append("governance evaluation cannot produce a selection result")
    if evaluation_meta.get("fitness_effect") != "none":
        errors.append("governance evaluation cannot modify ecological fitness")
    require_none_effects(evaluation_meta, "evaluation", errors)

    federation_members = federation_doc.get("members")
    if not isinstance(federation_members, list):
        errors.append("federation members must be a list")
        federation_members = []
    if any("archetype_id" in member or "governance_binding" in member for member in federation_members if isinstance(member, dict)):
        errors.append("federation membership cannot automatically create a governance binding")

    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("governance archetypes must not create a capability")
        capabilities = []
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("governance archetypes must preserve every claim at C1/pending")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("evidence must be a list")
        evidence_records = []
    for evidence in evidence_records:
        if not isinstance(evidence, dict) or evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("governance archetypes must preserve every evidence record at E1/pending")
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
            errors.append("governance archetypes must preserve every verification at V0/pending")
            break
    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("governance archetypes must not create a runtime")
        runtimes = []
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("governance archetypes must not create an organism candidate")
        candidates = []
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("governance archetypes cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("governance archetypes cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("governance archetypes cannot change fitness")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("governance archetypes must not create an Agent entity")

    governance_constitution = root / "constitution" / "governance-archetype-constitution.yaml"
    federation_constitution = root / "constitution" / "federation-constitution.yaml"
    saee_constitution = root / "constitution" / "saee-constitution.yaml"
    for path in (governance_constitution, federation_constitution, saee_constitution):
        if not path.is_file():
            errors.append(f"missing constitution reference: {path}")
    if federation_constitution.is_file():
        federation_text = federation_constitution.read_text(encoding="utf-8")
        if 'governance_archetype_constitution: "governance-archetype-constitution.yaml"' not in federation_text:
            errors.append("federation constitution does not reference the governance archetype layer")
        if 'exclusive_governance_mode: false' not in federation_text:
            errors.append("federation constitution must state that federation is not the exclusive governance mode")
    if saee_constitution.is_file():
        saee_text = saee_constitution.read_text(encoding="utf-8")
        if 'governance_archetype_constitution: "governance-archetype-constitution.yaml"' not in saee_text:
            errors.append("SAEE constitution does not reference the governance archetype layer")
        if 'authority_effect: "none"' not in saee_text:
            errors.append("SAEE governance adaptation strategy must retain authority_effect=none")

    return {
        "status": "FAIL" if errors else "PASS",
        "governance_archetype_count": len(archetype_by_id),
        "archetype_distribution": {
            name: archetype_name_counts.get(name, 0) for name in ARCHETYPE_NAMES
        },
        "binding_count": len(binding_by_id),
        "binding_status_distribution": {
            status: binding_status_counts.get(status, 0) for status in BINDING_STATUSES
        },
        "transition_definition_count": len(transition_by_id),
        "executed_transition_count": len(executed),
        "evaluation_dimensions": list(dimension_by_id),
        "non_null_evaluation_score_count": sum(
            1 for record in dimension_by_id.values() if record.get("score") is not None
        ),
        "capability_count": len(capabilities),
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "runtime_instance_count": len(runtimes),
        "organism_candidate_count": len(candidates),
        "digital_organism_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archetypes", type=Path, default=root / "registry" / "governance-archetypes.yaml")
    parser.add_argument("--bindings", type=Path, default=root / "registry" / "governance-bindings.yaml")
    parser.add_argument("--transitions", type=Path, default=root / "registry" / "governance-transitions.yaml")
    parser.add_argument("--evaluation", type=Path, default=root / "registry" / "governance-evaluation.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--federation-members", type=Path, default=root / "registry" / "federation-members.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        result = validate(
            load_json_yaml(args.archetypes),
            load_json_yaml(args.bindings),
            load_json_yaml(args.transitions),
            load_json_yaml(args.evaluation),
            load_json_yaml(args.entities),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.federation_members),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"GOVERNANCE_VALIDATION: {result['status']}")
        print(f"archetypes={result.get('governance_archetype_count', 0)}")
        print(f"bindings={result.get('binding_count', 0)}")
        print(f"transition_definitions={result.get('transition_definition_count', 0)}")
        print(f"executed_transitions={result.get('executed_transition_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
