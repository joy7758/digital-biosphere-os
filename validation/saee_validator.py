#!/usr/bin/env python3
"""Validate the SAEE ecological interpretation layer.

Agent-readable contract:
- Registry inputs use JSON-compatible YAML 1.2 and no third-party package.
- Ecological categories are mapped from the canonical entity registry.
- Entity, repository, protocol, service, Agent-related name, runtime, fitness,
  evidence, or verification never promotes an entity to organism status.
- Fitness has no capability, permission, C/E/V, selection, or organism effect.
- Environment maps to evolution pressure without automatic fitness or selection.
- Event maps to an observation substrate for evolution without creating events,
  observations, fitness, selection, or evolution results.
- Evolution principles preserve identity, evidence, lineage, and history.
- PASS proves local registry consistency only; it creates no Agent, capability,
  permission, runtime, Candidate Organism, or Digital Organism.
- Exit 0 means PASS; exit 1 means the SAEE layer must fail closed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ECOLOGICAL_TYPES = (
    "Artifact",
    "Protocol",
    "Service",
    "Runtime",
    "Candidate Organism",
    "Digital Organism",
)
FITNESS_STATUSES = ("unknown", "assessed", "invalid", "revoked")
EVOLUTION_STAGES = (
    "pre-organism",
    "candidate-organism",
    "digital-organism",
    "ecologically-retired",
)
BASELINE_IDENTITY_MAPPING = {
    "repository": "Artifact",
    "artifact": "Artifact",
    "protocol": "Protocol",
    "service": "Service",
    "agent": "Artifact",
}
EXPECTED_PRINCIPLES = (
    "identity_preservation",
    "evidence_preservation",
    "adaptive_improvement",
    "resource_balance",
    "ecological_diversity",
)
EXPECTED_DIMENSIONS = (
    "reliability",
    "evidence_quality",
    "efficiency",
    "adaptability",
    "stability",
)
EXPECTED_LAYER_MAPPING = {
    "Identity": ("digital organism identity", "mapped_existing_layer", "unchanged"),
    "Capability": ("adaptive potential", "mapped_existing_layer", "unchanged"),
    "Evidence": ("evolution memory", "mapped_existing_layer", "unchanged"),
    "Verification": ("selection pressure", "mapped_existing_layer", "unchanged"),
    "Runtime": ("ecological activity and environment interaction", "registration_model_established_no_instances", "none"),
    "Environment": ("evolution pressure", "defined_model_not_applied", "none"),
    "Event": ("observation substrate for evolution", "defined_event_model_no_events", "none"),
    "Event Integrity": ("evidence reliability", "defined_integrity_model_no_records", "none"),
    "Attestation": ("evidence reliability", "defined_attestation_model_no_records", "none"),
    "Execution Context": ("event reliability", "defined_execution_context_model_no_records", "none"),
    "Experiment": ("observation-mediated evolution", "registered_experimental_protocol_one_experiment_unexecuted", "none"),
    "Genesis Experiment": ("fact formation", "registered_genesis_experiment_not_authorized", "none"),
}
REQUIRED_ECOLOGICAL_FIELDS = {
    "entity_id",
    "current_type",
    "ecological_type",
    "fitness_status",
    "evolution_stage",
}
REQUIRED_PRINCIPLE_FIELDS = {
    "principle_id",
    "name",
    "description",
    "affected_layer",
    "constraint",
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
    """Index a list of mappings and reject missing or duplicate identifiers."""
    if not isinstance(records, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        where = f"{label}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        identifier = record.get(key)
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{where}.{key} must be a non-empty string")
            continue
        if identifier in result:
            errors.append(f"duplicate {key}: {identifier}")
            continue
        result[identifier] = record
    return result


def has_organism_qualification(record: dict[str, Any], target: str) -> bool:
    """Require explicit attributable promotion evidence; never infer it."""
    qualification = record.get("organism_qualification")
    if not isinstance(qualification, dict):
        return False
    required = {
        "status",
        "target",
        "evidence",
        "review_id",
        "recorded_at",
        "lineage_record",
    }
    return (
        required.issubset(qualification)
        and qualification.get("status") == "approved"
        and qualification.get("target") == target
        and isinstance(qualification.get("evidence"), list)
        and bool(qualification.get("evidence"))
        and isinstance(qualification.get("review_id"), str)
        and bool(qualification.get("review_id"))
        and isinstance(qualification.get("recorded_at"), str)
        and bool(qualification.get("recorded_at"))
        and isinstance(qualification.get("lineage_record"), str)
        and bool(qualification.get("lineage_record"))
    )


def validate(
    docs: dict[str, dict[str, Any]],
    root: Path,
) -> dict[str, Any]:
    ecological_doc = docs.get("ecological_entities", {})
    entities_doc = docs.get("entities", {})
    principles_doc = docs.get("principles", {})
    fitness_doc = docs.get("fitness", {})
    mapping_doc = docs.get("mapping", {})
    capabilities_doc = docs.get("capabilities", {})
    claims_doc = docs.get("claims", {})
    evidence_doc = docs.get("evidence", {})
    verification_doc = docs.get("verification", {})

    errors: list[str] = []
    entity_by_id = index_records(entities_doc.get("entities"), "entity_id", "entities", errors)
    ecological_by_id = index_records(
        ecological_doc.get("ecological_entities"),
        "entity_id",
        "ecological_entities",
        errors,
    )
    if set(entity_by_id) != set(ecological_by_id):
        missing = sorted(set(entity_by_id) - set(ecological_by_id))
        extra = sorted(set(ecological_by_id) - set(entity_by_id))
        if missing:
            errors.append(f"entities missing ecological mappings: {missing}")
        if extra:
            errors.append(f"ecological mappings reference unknown entities: {extra}")

    ecological_counts: Counter[str] = Counter()
    stage_counts: Counter[str] = Counter()
    fitness_counts: Counter[str] = Counter()
    for entity_id, record in ecological_by_id.items():
        missing_fields = REQUIRED_ECOLOGICAL_FIELDS - set(record)
        if missing_fields:
            errors.append(f"{entity_id}: missing fields {sorted(missing_fields)}")
        identity = entity_by_id.get(entity_id)
        current_type = record.get("current_type")
        ecological_type = record.get("ecological_type")
        fitness_status = record.get("fitness_status")
        stage = record.get("evolution_stage")
        if identity is not None and current_type != identity.get("entity_type"):
            errors.append(f"{entity_id}: current_type does not match canonical identity")
        expected_type = BASELINE_IDENTITY_MAPPING.get(current_type)
        if expected_type is None:
            errors.append(f"{entity_id}: unsupported current identity type {current_type!r}")
        if ecological_type not in ECOLOGICAL_TYPES:
            errors.append(f"{entity_id}: invalid ecological_type {ecological_type!r}")
        else:
            ecological_counts[ecological_type] += 1
        if stage not in EVOLUTION_STAGES:
            errors.append(f"{entity_id}: invalid evolution_stage {stage!r}")
        else:
            stage_counts[stage] += 1
        if fitness_status not in FITNESS_STATUSES:
            errors.append(f"{entity_id}: invalid fitness_status {fitness_status!r}")
        else:
            fitness_counts[fitness_status] += 1

        if ecological_type in {"Candidate Organism", "Digital Organism"}:
            if not has_organism_qualification(record, ecological_type):
                errors.append(f"{entity_id}: Entity cannot automatically become {ecological_type}")
        elif expected_type is not None and ecological_type != expected_type:
            errors.append(
                f"{entity_id}: baseline mapping requires {expected_type}, not {ecological_type}"
            )
        expected_stage = {
            "Candidate Organism": "candidate-organism",
            "Digital Organism": "digital-organism",
        }.get(ecological_type, "pre-organism")
        if stage != expected_stage:
            errors.append(f"{entity_id}: ecological_type and evolution_stage mismatch")

        if record.get("fitness_score") is not None:
            errors.append(f"{entity_id}: v0.1 fitness_score must remain null")
        if fitness_status != "unknown":
            errors.append(f"{entity_id}: v0.1 fitness_status must remain unknown")
        if record.get("capability_effect") != "none":
            errors.append(f"{entity_id}: fitness or ecology cannot affect capability")
        if record.get("permission_effect") != "none":
            errors.append(f"{entity_id}: fitness or ecology cannot grant permission")
        if record.get("c_e_v_level_effect") != "none":
            errors.append(f"{entity_id}: ecology cannot change C/E/V levels")
        if "capability_id" in record or "permissions" in record:
            errors.append(f"{entity_id}: ecological mapping cannot create capability or permission")

    ecological_meta = ecological_doc.get("metadata", {})
    if ecological_meta.get("entity_count") != len(ecological_by_id):
        errors.append("ecological metadata entity_count mismatch")
    for ecological_type in ECOLOGICAL_TYPES:
        if ecological_meta.get("ecological_type_distribution", {}).get(ecological_type, 0) != ecological_counts.get(ecological_type, 0):
            errors.append(f"ecological type distribution mismatch for {ecological_type}")
    for stage in EVOLUTION_STAGES:
        if ecological_meta.get("evolution_stage_distribution", {}).get(stage, 0) != stage_counts.get(stage, 0):
            errors.append(f"evolution stage distribution mismatch for {stage}")
    if ecological_meta.get("candidate_organism_count") != ecological_counts.get("Candidate Organism", 0):
        errors.append("candidate organism metadata count mismatch")
    if ecological_meta.get("digital_organism_count") != ecological_counts.get("Digital Organism", 0):
        errors.append("digital organism metadata count mismatch")

    principle_by_id = index_records(
        principles_doc.get("principles"), "principle_id", "principles", errors
    )
    if tuple(principle_by_id) != EXPECTED_PRINCIPLES:
        errors.append("evolution principles must preserve the five required ordered definitions")
    for principle_id, principle in principle_by_id.items():
        missing_fields = REQUIRED_PRINCIPLE_FIELDS - set(principle)
        if missing_fields:
            errors.append(f"{principle_id}: missing principle fields {sorted(missing_fields)}")
        constraint = principle.get("constraint")
        if not isinstance(constraint, str) or not constraint:
            errors.append(f"{principle_id}: constraint must be non-empty")
    identity_constraint = str(principle_by_id.get("identity_preservation", {}).get("constraint", "")).lower()
    if "erase" not in identity_constraint or "lineage" not in identity_constraint:
        errors.append("identity_preservation must prohibit identity loss and require lineage")
    evidence_constraint = str(principle_by_id.get("evidence_preservation", {}).get("constraint", "")).lower()
    for required_term in ("deleted", "overwritten", "rewritten", "additive"):
        if required_term not in evidence_constraint:
            errors.append(f"evidence_preservation constraint missing {required_term}")
    if principles_doc.get("metadata", {}).get("principle_count") != len(principle_by_id):
        errors.append("evolution principle metadata count mismatch")

    dimensions = fitness_doc.get("fitness_dimensions")
    if not isinstance(dimensions, dict):
        errors.append("fitness_dimensions must be a mapping")
        dimensions = {}
    if tuple(dimensions) != EXPECTED_DIMENSIONS:
        errors.append("fitness dimensions must be reliability, evidence_quality, efficiency, adaptability, stability")
    for dimension_id, dimension in dimensions.items():
        if not isinstance(dimension, dict):
            errors.append(f"fitness dimension {dimension_id} must be a mapping")
            continue
        if dimension.get("score") is not None:
            errors.append(f"fitness dimension {dimension_id}: score must remain null")
        if dimension.get("status") != "unknown":
            errors.append(f"fitness dimension {dimension_id}: status must remain unknown")
        if not isinstance(dimension.get("required_evidence"), list) or not dimension.get("required_evidence"):
            errors.append(f"fitness dimension {dimension_id}: required_evidence must be non-empty")
    aggregate = fitness_doc.get("aggregate_fitness")
    if not isinstance(aggregate, dict) or aggregate.get("score") is not None:
        errors.append("aggregate fitness score must remain null")
    governance_effect = fitness_doc.get("governance_effect")
    expected_governance_effect = {
        "capability_effect": "none",
        "permission_effect": "none",
        "c_e_v_level_effect": "none",
        "organism_status_effect": "none",
        "selection_effect": "none_without_future_evidence_and_review",
    }
    if governance_effect != expected_governance_effect:
        errors.append("fitness governance effect must remain non-authorizing")

    mappings = mapping_doc.get("mappings")
    mapping_by_layer = index_records(mappings, "layer", "mappings", errors)
    if tuple(mapping_by_layer) != tuple(EXPECTED_LAYER_MAPPING):
        errors.append("SAEE layer mapping must be ordered Identity, Capability, Evidence, Verification, Runtime, Environment, Event, Event Integrity, Attestation, Execution Context, Experiment, Genesis Experiment")
    for layer, expected in EXPECTED_LAYER_MAPPING.items():
        mapping = mapping_by_layer.get(layer, {})
        correspondence, status, authority_effect = expected
        if mapping.get("saee_correspondence") != correspondence:
            errors.append(f"{layer}: SAEE correspondence mismatch")
        if mapping.get("status") != status:
            errors.append(f"{layer}: mapping status mismatch")
        if mapping.get("authority_effect") != authority_effect:
            errors.append(f"{layer}: existing operational authority must remain unchanged")
        current_authority = mapping.get("current_authority")
        current_registry = mapping.get("current_registry")
        for reference in (current_authority, current_registry):
            if not isinstance(reference, str) or not (root / reference).is_file():
                errors.append(f"{layer}: missing current authority reference {reference!r}")
    transitions = mapping_doc.get("genesis_transitions")
    if not isinstance(transitions, list) or len(transitions) != 1:
        errors.append("SAEE mapping requires one Runtime to Candidate Organism transition model")
    else:
        transition = transitions[0]
        if transition.get("transition_id") != "runtime_to_candidate_organism":
            errors.append("SAEE Genesis transition id mismatch")
        if transition.get("from") != "Runtime" or transition.get("to") != "Candidate Organism":
            errors.append("SAEE Genesis transition must map Runtime to Candidate Organism")
        if transition.get("automatic") is not False:
            errors.append("Runtime to Candidate Organism transition cannot be automatic")
        if transition.get("current_runtime_count") != 0 or transition.get("current_candidate_count") != 0:
            errors.append("SAEE Genesis transition baseline must contain zero instances and candidates")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mapping_by_layer):
        errors.append("SAEE mapping metadata count mismatch")

    capabilities = capabilities_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("SAEE integration must not create or register capabilities")
    claims = claims_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append("SAEE integration must preserve every claim at pending/C1")
            break
        if claim.get("capability_assignment_status") != "not_assigned" or claim.get("permission_status") != "not_granted":
            errors.append("SAEE integration must not assign capability or grant permission through claims")
            break
    claim_ids = {
        claim.get("claim_id")
        for claim in claims
        if isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
    }
    if claims_doc.get("metadata", {}).get("claim_count") != len(claims):
        errors.append("SAEE integration must preserve the capability claim history count")
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("evidence must be a list")
        evidence_records = []
    for evidence_record in evidence_records:
        if not isinstance(evidence_record, dict) or evidence_record.get("evidence_type") != "E1" or evidence_record.get("status") != "pending":
            errors.append("SAEE integration must preserve every evidence record at E1/pending")
            break
    evidence_claim_ids = {
        evidence_record.get("claim_id")
        for evidence_record in evidence_records
        if isinstance(evidence_record, dict)
        and isinstance(evidence_record.get("claim_id"), str)
    }
    if evidence_doc.get("metadata", {}).get("evidence_count") != len(evidence_records):
        errors.append("SAEE integration must preserve the historical evidence count")
    if evidence_claim_ids != claim_ids:
        errors.append("SAEE integration must preserve one evidence history for every claim")
    verification_records = verification_doc.get("verification_records")
    if not isinstance(verification_records, list):
        errors.append("verification_records must be a list")
        verification_records = []
    for verification in verification_records:
        if not isinstance(verification, dict) or verification.get("verification_level") != "V0" or verification.get("status") != "pending" or verification.get("decision") != "pending":
            errors.append("SAEE integration must preserve every verification record at V0/pending")
            break
        if verification.get("capability_assignment_status") != "not_assigned" or verification.get("permission_status") != "not_granted":
            errors.append("SAEE integration must not assign capability or grant permission through verification")
            break
    verification_claim_ids = {
        verification.get("claim_id")
        for verification in verification_records
        if isinstance(verification, dict)
        and isinstance(verification.get("claim_id"), str)
    }
    if verification_doc.get("metadata", {}).get("verification_record_count") != len(verification_records):
        errors.append("SAEE integration must preserve the verification history count")
    if verification_claim_ids != claim_ids:
        errors.append("SAEE integration must preserve one verification history for every claim")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("SAEE v0.1 integration must not create an Agent entity")

    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entity_by_id),
        "ecological_entity_count": len(ecological_by_id),
        "ecological_type_distribution": {
            ecological_type: ecological_counts.get(ecological_type, 0)
            for ecological_type in ECOLOGICAL_TYPES
        },
        "evolution_stage_distribution": {
            stage: stage_counts.get(stage, 0) for stage in EVOLUTION_STAGES
        },
        "fitness_status_distribution": {
            status: fitness_counts.get(status, 0) for status in FITNESS_STATUSES
        },
        "fitness_dimension_count": len(dimensions),
        "known_fitness_score_count": sum(
            isinstance(dimension, dict) and dimension.get("score") is not None
            for dimension in dimensions.values()
        ),
        "evolution_principle_count": len(principle_by_id),
        "layer_mapping_count": len(mapping_by_layer),
        "capability_count": len(capabilities) if isinstance(capabilities, list) else 0,
        "capability_assignment_count": 0,
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ecological-entities", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--principles", type=Path, default=root / "registry" / "evolution-principles.yaml")
    parser.add_argument("--fitness", type=Path, default=root / "registry" / "fitness-model.yaml")
    parser.add_argument("--mapping", type=Path, default=root / "registry" / "evolution-mapping.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        docs = {
            "ecological_entities": load_json_yaml(args.ecological_entities),
            "entities": load_json_yaml(args.entities),
            "principles": load_json_yaml(args.principles),
            "fitness": load_json_yaml(args.fitness),
            "mapping": load_json_yaml(args.mapping),
            "capabilities": load_json_yaml(args.capabilities),
            "claims": load_json_yaml(args.claims),
            "evidence": load_json_yaml(args.evidence),
            "verification": load_json_yaml(args.verification),
        }
        result = validate(docs, root)
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"SAEE_VALIDATION: {result['status']}")
        print(f"ecological_entities={result.get('ecological_entity_count', 0)}")
        print(f"candidate_organisms={result.get('ecological_type_distribution', {}).get('Candidate Organism', 0)}")
        print(f"digital_organisms={result.get('ecological_type_distribution', {}).get('Digital Organism', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
