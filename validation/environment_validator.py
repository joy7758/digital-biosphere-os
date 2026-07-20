#!/usr/bin/env python3
"""Validate the Ecological Environment Layer without third-party packages.

Agent-readable contract:
- One existing governance workspace may be defined as an environment model,
  but it is not active and contains no runtime or entity interaction.
- Resource models define five measurement vocabularies only; limit null means
  undefined, no resource is allocated, and no entity is bound.
- Selection pressures are definitions with null thresholds and no fitness or
  selection effect.
- Environment -> Evolution Pressure is interpretive only.
- PASS creates no Agent, runtime, Candidate Organism, Digital Organism,
  capability, permission, interaction, fitness score, or C/E/V upgrade.
- Exit 0 means PASS; exit 1 means the environment layer must fail closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ENVIRONMENT_TYPES = (
    "governance_workspace",
    "development",
    "test",
    "simulation",
    "production",
    "external",
)
ENVIRONMENT_STATUSES = {"defined", "active", "suspended", "retired"}
RESOURCE_TYPES = ("token", "compute", "storage", "data_access", "human_attention")
PRESSURE_DIMENSIONS = (
    "reliability_pressure",
    "evidence_pressure",
    "efficiency_pressure",
    "adaptability_pressure",
    "stability_pressure",
)
INTERACTION_TYPES = {
    "observes",
    "consumes",
    "produces",
    "transforms",
    "constrains",
    "adapts_to",
}
FITNESS_DIMENSIONS = (
    "reliability",
    "evidence_quality",
    "efficiency",
    "adaptability",
    "stability",
)
REQUIRED_ENVIRONMENT_FIELDS = {
    "environment_id",
    "environment_type",
    "resource_model",
    "task_model",
    "constraints",
    "status",
}
REQUIRED_RESOURCE_FIELDS = {"resource_id", "resource_type", "measurement", "limit"}
REQUIRED_PRESSURE_FIELDS = {"pressure_id", "dimension", "description", "threshold"}
REQUIRED_INTERACTION_FIELDS = {
    "entity_id",
    "environment_id",
    "interaction_type",
    "resource_dependency",
    "effect",
}
ENVIRONMENT_ID_RE = re.compile(r"^dbio://environment/[a-z0-9][a-z0-9-]*/v[0-9][a-zA-Z0-9._-]*$")
RESOURCE_ID_RE = re.compile(r"^dbio://resource-model/[a-z0-9][a-z0-9-]*/v[0-9][a-zA-Z0-9._-]*$")
PRESSURE_ID_RE = re.compile(r"^dbio://selection-pressure/[a-z0-9][a-z0-9-]*/v[0-9][a-zA-Z0-9._-]*$")


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
    """Index mappings and fail closed on missing or duplicate identifiers."""
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


def validate(
    environment_doc: dict[str, Any],
    resource_doc: dict[str, Any],
    pressure_doc: dict[str, Any],
    interaction_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    fitness_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    mapping_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []

    entity_by_id = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    environment_by_id = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    resource_by_id = index_records(
        resource_doc.get("resource_models"), "resource_id", "resource_models", errors
    )
    pressure_by_id = index_records(
        pressure_doc.get("selection_pressures"),
        "pressure_id",
        "selection_pressures",
        errors,
    )

    if tuple(environment_doc.get("environment_types", [])) != ENVIRONMENT_TYPES:
        errors.append("environment types must preserve the six ordered definitions")

    environment_status_counts: Counter[str] = Counter()
    for environment_id, environment in environment_by_id.items():
        missing = REQUIRED_ENVIRONMENT_FIELDS - set(environment)
        if missing:
            errors.append(f"{environment_id}: missing fields {sorted(missing)}")
        if not ENVIRONMENT_ID_RE.match(environment_id):
            errors.append(f"{environment_id}: malformed environment_id")
        environment_type = environment.get("environment_type")
        if environment_type not in ENVIRONMENT_TYPES:
            errors.append(f"{environment_id}: invalid environment_type {environment_type!r}")
        status = environment.get("status")
        if status not in ENVIRONMENT_STATUSES:
            errors.append(f"{environment_id}: invalid environment status {status!r}")
        else:
            environment_status_counts[status] += 1
        if status != "defined" or environment.get("activation_status") != "not_active":
            errors.append(f"{environment_id}: v0.1 environment must remain defined and not active")

        resource_refs = environment.get("resource_model")
        if not isinstance(resource_refs, list) or not resource_refs:
            errors.append(f"{environment_id}: resource_model must be a non-empty list")
        else:
            if len(resource_refs) != len(set(resource_refs)):
                errors.append(f"{environment_id}: duplicate resource model reference")
            for resource_ref in resource_refs:
                if resource_ref not in resource_by_id:
                    errors.append(f"{environment_id}: unknown resource model {resource_ref!r}")

        task_model = environment.get("task_model")
        if not isinstance(task_model, dict):
            errors.append(f"{environment_id}: task_model must be a mapping")
        else:
            if task_model.get("model_status") != "defined":
                errors.append(f"{environment_id}: task model must remain defined only")
            if task_model.get("runtime_execution_authority") != "none":
                errors.append(f"{environment_id}: task model cannot authorize runtime execution")
            if task_model.get("external_project_action_authority") != "none":
                errors.append(f"{environment_id}: task model cannot authorize external actions")
        if not isinstance(environment.get("constraints"), list) or not environment.get("constraints"):
            errors.append(f"{environment_id}: constraints must be a non-empty list")

        evidence_source = environment.get("evidence_source")
        if not isinstance(evidence_source, dict):
            errors.append(f"{environment_id}: evidence_source must be a mapping")
        else:
            evidence_path = evidence_source.get("path")
            if not isinstance(evidence_path, str) or not Path(evidence_path).resolve() == root.resolve():
                errors.append(f"{environment_id}: evidence path must resolve to this governance workspace")
            if evidence_source.get("observation_claim") != "path_exists_only":
                errors.append(f"{environment_id}: environment evidence must remain path_exists_only")

        for effect_field in (
            "runtime_effect",
            "fitness_effect",
            "organism_effect",
            "capability_effect",
            "permission_effect",
        ):
            if environment.get(effect_field) != "none":
                errors.append(f"{environment_id}: {effect_field} must remain none")
        forbidden_identity_fields = {
            "entity_id",
            "agent_id",
            "runtime_id",
            "candidate_id",
            "digital_organism_id",
        }
        present_forbidden = forbidden_identity_fields & set(environment)
        if present_forbidden:
            errors.append(
                f"{environment_id}: environment cannot create or bind identity fields {sorted(present_forbidden)}"
            )

    environment_meta = environment_doc.get("metadata", {})
    if environment_meta.get("environment_count") != len(environment_by_id):
        errors.append("environment metadata count mismatch")
    if environment_meta.get("defined_environment_count") != environment_status_counts.get("defined", 0):
        errors.append("defined environment metadata count mismatch")
    if environment_meta.get("active_environment_count") != environment_status_counts.get("active", 0):
        errors.append("active environment metadata count mismatch")

    resource_types_seen: list[str] = []
    for resource_id, resource in resource_by_id.items():
        missing = REQUIRED_RESOURCE_FIELDS - set(resource)
        if missing:
            errors.append(f"{resource_id}: missing fields {sorted(missing)}")
        if not RESOURCE_ID_RE.match(resource_id):
            errors.append(f"{resource_id}: malformed resource_id")
        resource_type = resource.get("resource_type")
        resource_types_seen.append(resource_type)
        if resource_type not in RESOURCE_TYPES:
            errors.append(f"{resource_id}: invalid resource_type {resource_type!r}")
        else:
            expected_slug = resource_type.replace("_", "-")
            if f"/{expected_slug}/" not in resource_id:
                errors.append(f"{resource_id}: resource_id does not match resource_type")
        if not isinstance(resource.get("measurement"), str) or not resource.get("measurement"):
            errors.append(f"{resource_id}: measurement must be a non-empty string")
        if resource.get("limit") is not None:
            errors.append(f"{resource_id}: v0.1 resource limit must remain null")
        if resource.get("entity_binding") is not None:
            errors.append(f"{resource_id}: resource model cannot bind an entity")
        if resource.get("allocation_status") != "not_allocated":
            errors.append(f"{resource_id}: resource model cannot allocate resources")
    if tuple(resource_types_seen) != RESOURCE_TYPES:
        errors.append("resource models must preserve token, compute, storage, data_access, human_attention order")

    resource_meta = resource_doc.get("metadata", {})
    if resource_meta.get("resource_model_count") != len(resource_by_id):
        errors.append("resource-model metadata count mismatch")
    if resource_meta.get("entity_binding_count") != 0:
        errors.append("resource models must report zero entity bindings")
    if resource_meta.get("non_null_limit_count") != sum(
        resource.get("limit") is not None for resource in resource_by_id.values()
    ):
        errors.append("resource-model non-null limit metadata count mismatch")
    if resource_meta.get("resource_allocation_count") != 0:
        errors.append("resource models must report zero allocations")

    pressure_dimensions_seen: list[str] = []
    for pressure_id, pressure in pressure_by_id.items():
        missing = REQUIRED_PRESSURE_FIELDS - set(pressure)
        if missing:
            errors.append(f"{pressure_id}: missing fields {sorted(missing)}")
        if not PRESSURE_ID_RE.match(pressure_id):
            errors.append(f"{pressure_id}: malformed pressure_id")
        dimension = pressure.get("dimension")
        pressure_dimensions_seen.append(dimension)
        if dimension not in PRESSURE_DIMENSIONS:
            errors.append(f"{pressure_id}: invalid selection-pressure dimension {dimension!r}")
        if not isinstance(pressure.get("description"), str) or not pressure.get("description"):
            errors.append(f"{pressure_id}: description must be a non-empty string")
        if pressure.get("threshold") is not None:
            errors.append(f"{pressure_id}: v0.1 threshold must remain null")
        if pressure.get("application_status") != "not_applied":
            errors.append(f"{pressure_id}: selection pressure cannot be applied in v0.1")
        if pressure.get("fitness_effect") != "none":
            errors.append(f"{pressure_id}: selection pressure cannot modify fitness")
        for forbidden_field in ("fitness_score", "ranking", "selection_result", "organism_effect"):
            if forbidden_field in pressure:
                errors.append(f"{pressure_id}: forbidden field {forbidden_field}")
    if tuple(pressure_dimensions_seen) != PRESSURE_DIMENSIONS:
        errors.append("selection pressures must preserve the five ordered dimensions")

    pressure_meta = pressure_doc.get("metadata", {})
    if pressure_meta.get("selection_pressure_count") != len(pressure_by_id):
        errors.append("selection-pressure metadata count mismatch")
    if pressure_meta.get("non_null_threshold_count") != sum(
        pressure.get("threshold") is not None for pressure in pressure_by_id.values()
    ):
        errors.append("selection-pressure threshold metadata count mismatch")
    for zero_field in (
        "applied_pressure_count",
        "fitness_modification_count",
        "selection_result_count",
    ):
        if pressure_meta.get(zero_field) != 0:
            errors.append(f"selection-pressure metadata {zero_field} must remain zero")

    dimensions = fitness_doc.get("fitness_dimensions")
    if not isinstance(dimensions, dict) or tuple(dimensions) != FITNESS_DIMENSIONS:
        errors.append("fitness model must preserve the five SAEE dimensions")
        dimensions = {}
    for dimension_id, dimension in dimensions.items():
        if not isinstance(dimension, dict):
            errors.append(f"fitness dimension {dimension_id} must be a mapping")
        elif dimension.get("score") is not None or dimension.get("status") != "unknown":
            errors.append(f"fitness dimension {dimension_id} must remain unknown with score null")
    aggregate = fitness_doc.get("aggregate_fitness")
    if not isinstance(aggregate, dict) or aggregate.get("score") is not None:
        errors.append("aggregate fitness score must remain null")

    interactions = interaction_doc.get("ecological_interactions")
    if not isinstance(interactions, list):
        errors.append("ecological_interactions must be a list")
        interactions = []
    for index, interaction in enumerate(interactions):
        where = f"ecological_interactions[{index}]"
        if not isinstance(interaction, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_INTERACTION_FIELDS - set(interaction)
        if missing:
            errors.append(f"{where}: missing fields {sorted(missing)}")
        if interaction.get("entity_id") not in entity_by_id:
            errors.append(f"{where}: unknown entity_id")
        if interaction.get("environment_id") not in environment_by_id:
            errors.append(f"{where}: unknown environment_id")
        if interaction.get("interaction_type") not in INTERACTION_TYPES:
            errors.append(f"{where}: invalid interaction_type")
        if not isinstance(interaction.get("resource_dependency"), list):
            errors.append(f"{where}: resource_dependency must be a list")
        else:
            for resource_ref in interaction.get("resource_dependency", []):
                if resource_ref not in resource_by_id:
                    errors.append(f"{where}: unknown resource dependency {resource_ref!r}")
        if interaction.get("effect") not in {None, "unknown", "none"}:
            errors.append(f"{where}: interaction effect cannot establish a selection or organism result")
        for forbidden_field in (
            "runtime_id",
            "fitness_score",
            "candidate_id",
            "digital_organism_id",
            "capability_id",
            "permission",
        ):
            if forbidden_field in interaction:
                errors.append(f"{where}: forbidden field {forbidden_field}")
    interaction_meta = interaction_doc.get("metadata", {})
    if interaction_meta.get("interaction_count") != len(interactions):
        errors.append("ecological-interaction metadata count mismatch")
    if interaction_meta.get("status") == "empty_interaction_baseline" and interactions:
        errors.append("v0.1 ecological-interaction registry must remain empty")
    for zero_field in (
        "runtime_interaction_count",
        "fitness_effect_count",
        "organism_effect_count",
        "permission_grant_count",
    ):
        if interaction_meta.get(zero_field) != 0:
            errors.append(f"interaction metadata {zero_field} must remain zero")

    mappings = mapping_doc.get("mappings")
    mapping_by_layer = index_records(mappings, "layer", "mappings", errors)
    environment_mapping = mapping_by_layer.get("Environment")
    if environment_mapping is None:
        errors.append("SAEE mapping must include Environment -> Evolution Pressure")
    else:
        expected_mapping = {
            "current_authority": "constitution/environment-constitution.yaml",
            "current_registry": "registry/environments.yaml",
            "saee_correspondence": "evolution pressure",
            "status": "defined_model_not_applied",
            "authority_effect": "none",
        }
        for field, expected in expected_mapping.items():
            if environment_mapping.get(field) != expected:
                errors.append(f"Environment mapping {field} mismatch")
        for reference_field in ("current_authority", "current_registry"):
            reference = environment_mapping.get(reference_field)
            if not isinstance(reference, str) or not (root / reference).is_file():
                errors.append(f"Environment mapping missing reference {reference!r}")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mapping_by_layer):
        errors.append("SAEE mapping metadata count mismatch")

    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("environment layer must not create a runtime instance")
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("environment layer must not create an organism candidate")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {
            "Runtime",
            "Candidate Organism",
            "Digital Organism",
        }:
            errors.append("environment layer cannot create runtime or organism ecological status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("environment layer cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("environment layer cannot change entity fitness")

    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("environment layer must not create an Agent entity")
    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("environment layer must not create a capability")
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("environment layer must preserve every claim at C1/pending")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("evidence must be a list")
        evidence_records = []
    for evidence in evidence_records:
        if not isinstance(evidence, dict) or evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("environment layer must preserve every evidence record at E1/pending")
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
            errors.append("environment layer must preserve every verification at V0/pending")
            break

    return {
        "status": "FAIL" if errors else "PASS",
        "environment_count": len(environment_by_id),
        "environment_status_distribution": {
            status: environment_status_counts.get(status, 0)
            for status in ("defined", "active", "suspended", "retired")
        },
        "resource_model_count": len(resource_by_id),
        "resource_type_distribution": {
            resource_type: sum(
                resource.get("resource_type") == resource_type
                for resource in resource_by_id.values()
            )
            for resource_type in RESOURCE_TYPES
        },
        "selection_pressure_count": len(pressure_by_id),
        "non_null_pressure_threshold_count": sum(
            pressure.get("threshold") is not None for pressure in pressure_by_id.values()
        ),
        "ecological_interaction_count": len(interactions),
        "known_fitness_score_count": sum(
            isinstance(dimension, dict) and dimension.get("score") is not None
            for dimension in dimensions.values()
        ),
        "runtime_instance_count": len(runtimes) if isinstance(runtimes, list) else 0,
        "organism_candidate_count": len(candidates) if isinstance(candidates, list) else 0,
        "digital_organism_count": 0,
        "capability_count": len(capabilities) if isinstance(capabilities, list) else 0,
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--resources", type=Path, default=root / "registry" / "resource-models.yaml")
    parser.add_argument("--pressures", type=Path, default=root / "registry" / "selection-pressures.yaml")
    parser.add_argument("--interactions", type=Path, default=root / "registry" / "ecological-interactions.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--fitness", type=Path, default=root / "registry" / "fitness-model.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--mapping", type=Path, default=root / "registry" / "evolution-mapping.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced
    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        result = validate(
            load_json_yaml(args.environments),
            load_json_yaml(args.resources),
            load_json_yaml(args.pressures),
            load_json_yaml(args.interactions),
            load_json_yaml(args.entities),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.fitness),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            load_json_yaml(args.mapping),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"ECOLOGICAL_ENVIRONMENT_VALIDATION: {result['status']}")
        print(f"environments={result.get('environment_count', 0)}")
        print(f"resource_models={result.get('resource_model_count', 0)}")
        print(f"selection_pressures={result.get('selection_pressure_count', 0)}")
        print(f"interactions={result.get('ecological_interaction_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
