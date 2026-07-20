#!/usr/bin/env python3
"""Validate DBOS-EXP-0001 registration without executing it.

Agent-readable contract:
- Exactly one genesis experiment identity is registered: DBOS-EXP-0001.
- Its bounded subject is digital-biosphere-os resolved through the local total
  constitution, not promoted to a canonical entity, Agent, runtime, or organism.
- Exactly one eight-step procedure is procedure_defined; every step requires a
  separate future authorization and contains no execution result.
- Three inputs remain pending and unfrozen; six outputs remain expected with no
  artifact or evidence reference; four stop rules remain defined and unevaluated.
- The sole authorization remains pending with authorized_by=null and no effect.
- Events, integrity records, attestations, execution contexts, runtimes,
  observations, experiment evidence, and verification results remain absent.
- C/E/V levels, capability, permission, fitness, and organism state are unchanged.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
PROCEDURE_ID = "dbio:experiment-procedure:DBOS-EXP-0001:1"
AUTHORIZATION_ID = "DBOS-EXP-0001-AUTH-0001"
SUBJECT = "digital-biosphere-os"
SUBJECT_REF = "constitution/constitution.yaml"
ENVIRONMENT_ID = "dbio://environment/local-governance-workspace/v0.1"
REQUIREMENT_IDS = (
    "version_lock",
    "dependency_lock",
    "input_consistency",
    "environment_consistency",
    "execution_method",
)
INPUT_IDS = (
    "DBOS-EXP-0001-IN-0001",
    "DBOS-EXP-0001-IN-0002",
    "DBOS-EXP-0001-IN-0003",
)
INPUT_TYPES = (
    "constitution_version",
    "validator_list",
    "repository_state",
)
OUTPUT_IDS = tuple(f"DBOS-EXP-0001-OUT-{index:04d}" for index in range(1, 7))
OUTPUT_TYPES = (
    "execution_context",
    "event",
    "integrity_record",
    "attestation",
    "evidence_bundle",
    "verification_result",
)
STEP_ACTIONS = (
    "Load DBOS constitution",
    "Run validators",
    "Collect validation outputs",
    "Create execution context",
    "Generate event record",
    "Generate integrity record",
    "Generate attestation record",
    "Verify evidence",
)
STOP_RULES = {
    "DBOS-EXP-0001-STOP-SUCCESS-0001": ("success", "all required validators pass"),
    "DBOS-EXP-0001-STOP-FAIL-0001": ("failure", "any integrity failure"),
    "DBOS-EXP-0001-STOP-FAIL-0002": ("failure", "missing evidence"),
    "DBOS-EXP-0001-STOP-FAIL-0003": ("failure", "reproducibility failure"),
}
FORBIDDEN_RESULT_KEYS = {
    "actual_output",
    "event_id",
    "execution_result",
    "executed_at",
    "exit_status",
    "fitness_score",
    "maturity_level",
    "permission",
    "permission_status",
    "verification_level",
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
    """Index mappings and reject missing or duplicate identifiers."""
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


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def reject_result_fields(record: dict[str, Any], label: str, errors: list[str]) -> None:
    present = sorted(FORBIDDEN_RESULT_KEYS.intersection(record))
    if present:
        errors.append(f"{label}: registration cannot contain execution or authority results {present}")


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(
    experiment_doc: dict[str, Any],
    procedure_doc: dict[str, Any],
    input_doc: dict[str, Any],
    output_doc: dict[str, Any],
    stop_doc: dict[str, Any],
    authorization_doc: dict[str, Any],
    requirement_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    environment_doc: dict[str, Any],
    context_doc: dict[str, Any],
    event_doc: dict[str, Any],
    integrity_doc: dict[str, Any],
    attestation_doc: dict[str, Any],
    observation_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    mapping_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate the one registered, pending, non-executed genesis experiment."""
    errors: list[str] = []
    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    environments = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    requirements = index_records(
        requirement_doc.get("reproducibility_requirements"),
        "requirement_id",
        "reproducibility_requirements",
        errors,
    )
    if tuple(requirements) != REQUIREMENT_IDS:
        errors.append("genesis experiment requires all five ordered reproducibility definitions")
    for requirement_id, requirement in requirements.items():
        if requirement.get("authority_effect") != "none":
            errors.append(f"{requirement_id}: reproducibility requirement cannot create authority")
        if requirement.get("satisfied") is True or requirement.get("verified") is True:
            errors.append(f"{requirement_id}: genesis registration cannot satisfy or verify reproducibility")
    requirement_meta = requirement_doc.get("metadata", {})
    for field in (
        "satisfied_requirement_count",
        "verified_requirement_count",
        "automatic_reproducibility_count",
    ):
        if requirement_meta.get(field) != 0:
            errors.append(f"reproducibility metadata {field} must remain zero")

    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("genesis registry must contain exactly DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    expected_experiment = {
        "name": "Digital Biosphere Self Validation Experiment",
        "objective": "验证 DBOS 自身验证链是否可以产生可复现数字事实。",
        "subject": SUBJECT,
        "subject_kind": "governed_system_subject",
        "subject_ref": SUBJECT_REF,
        "status": "registered",
        "authorization_ref": AUTHORIZATION_ID,
        "execution_status": "not_executed",
        "execution_context_ref": None,
        "runtime_ref": None,
        "run_ref": None,
    }
    for field, expected in expected_experiment.items():
        if experiment.get(field) != expected:
            errors.append(f"{EXPERIMENT_ID}: {field} must remain {expected!r}")
    if SUBJECT in entities:
        errors.append("genesis registration must not silently create a canonical digital-biosphere-os entity")
    subject_path = root / SUBJECT_REF
    if not subject_path.is_file():
        errors.append("genesis governed-system subject_ref must resolve to the total constitution")
    protocol = experiment.get("protocol")
    if not isinstance(protocol, dict):
        errors.append("genesis experiment protocol must be a mapping")
        protocol = {}
    if protocol.get("version") != "v0.1":
        errors.append("genesis protocol version must be v0.1")
    if protocol.get("procedure_refs") != [PROCEDURE_ID]:
        errors.append("genesis protocol must reference exactly the registered procedure")
    if tuple(protocol.get("reproducibility_requirement_refs", [])) != REQUIREMENT_IDS:
        errors.append("genesis protocol must reference all five ordered reproducibility requirements")
    if protocol.get("execution_authority") != "not_granted":
        errors.append("registered genesis experiment cannot have execution authority")
    if not isinstance(protocol.get("limitations"), list) or not protocol.get("limitations"):
        errors.append("genesis protocol limitations must remain explicit")
    reject_result_fields(experiment, EXPERIMENT_ID, errors)
    experiment_meta = experiment_doc.get("metadata", {})
    if experiment_meta.get("experiment_count") != 1:
        errors.append("genesis experiment metadata count must be one")
    if experiment_meta.get("registered_experiment_count") != 1:
        errors.append("registered experiment metadata count must be one")
    if experiment_meta.get("experiment_status_distribution", {}).get("registered") != 1:
        errors.append("registered experiment status distribution must be one")
    require_zero(
        experiment_meta,
        (
            "authorized_experiment_count",
            "executed_experiment_count",
            "event_created_count",
            "runtime_created_count",
            "agent_created_count",
            "organism_created_count",
            "fitness_effect_count",
            "capability_effect_count",
            "permission_grant_count",
            "c_e_v_level_change_count",
        ),
        "experiment",
        errors,
    )

    procedures = index_records(
        procedure_doc.get("experiment_procedures"),
        "procedure_id",
        "experiment_procedures",
        errors,
    )
    if tuple(procedures) != (PROCEDURE_ID,):
        errors.append("genesis registry must contain exactly one registered procedure")
    procedure = procedures.get(PROCEDURE_ID, {})
    if procedure.get("experiment_id") != EXPERIMENT_ID:
        errors.append("genesis procedure must reference DBOS-EXP-0001")
    if procedure.get("environment") != ENVIRONMENT_ID or ENVIRONMENT_ID not in environments:
        errors.append("genesis procedure must reference the existing local governance environment")
    if procedure.get("status") != "procedure_defined":
        errors.append("genesis procedure status must remain procedure_defined")
    if tuple(procedure.get("inputs", [])) != INPUT_IDS:
        errors.append("genesis procedure inputs must reference the three registered inputs")
    if tuple(procedure.get("expected_outputs", [])) != OUTPUT_IDS:
        errors.append("genesis procedure outputs must reference the six expected outputs")
    steps = procedure.get("steps")
    if not isinstance(steps, list) or len(steps) != 8:
        errors.append("genesis procedure must contain exactly eight steps")
        steps = []
    actions = tuple(step.get("action") for step in steps if isinstance(step, dict))
    if actions != STEP_ACTIONS:
        errors.append("genesis procedure must preserve the eight ordered actions")
    expected_step_ids = tuple(f"DBOS-EXP-0001-STEP-{index:02d}" for index in range(1, 9))
    actual_step_ids = tuple(step.get("step_id") for step in steps if isinstance(step, dict))
    if actual_step_ids != expected_step_ids:
        errors.append("genesis procedure must preserve eight unique ordered step identifiers")
    all_stop_refs: set[str] = set()
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"genesis step {index + 1} must be a mapping")
            continue
        label = step.get("step_id", f"step-{index + 1}")
        if step.get("authority_required") != "separate_authorization":
            errors.append(f"{label}: every genesis step requires separate future authorization")
        if not nonempty_string(step.get("side_effect")):
            errors.append(f"{label}: side_effect boundary must be explicit")
        if not nonempty_string(step.get("evidence_requirement")):
            errors.append(f"{label}: future evidence requirement must be explicit")
        stop_refs = step.get("stop_conditions")
        if not isinstance(stop_refs, list) or not stop_refs:
            errors.append(f"{label}: stop_conditions must be a non-empty list")
        else:
            all_stop_refs.update(ref for ref in stop_refs if isinstance(ref, str))
        reject_result_fields(step, label, errors)
    if all_stop_refs != set(STOP_RULES):
        errors.append("genesis procedure steps must collectively reference all four stop rules")
    procedure_meta = procedure_doc.get("metadata", {})
    if procedure_meta.get("procedure_count") != 1 or procedure_meta.get("procedure_step_count") != 8:
        errors.append("genesis procedure metadata must report one procedure and eight steps")
    if procedure_meta.get("procedure_status_distribution", {}).get("procedure_defined") != 1:
        errors.append("procedure_defined status distribution must be one")
    require_zero(
        procedure_meta,
        (
            "executed_procedure_count",
            "execution_result_count",
            "event_created_count",
            "runtime_created_count",
            "agent_created_count",
            "permission_grant_count",
            "capability_effect_count",
        ),
        "procedure",
        errors,
    )

    inputs = index_records(
        input_doc.get("experiment_inputs"), "input_id", "experiment_inputs", errors
    )
    if tuple(inputs) != INPUT_IDS:
        errors.append("genesis input registry must contain exactly the three ordered inputs")
    for input_id, expected_type in zip(INPUT_IDS, INPUT_TYPES):
        record = inputs.get(input_id, {})
        if record.get("experiment_id") != EXPERIMENT_ID:
            errors.append(f"{input_id}: input must reference DBOS-EXP-0001")
        if record.get("input_type") != expected_type:
            errors.append(f"{input_id}: input_type must remain {expected_type}")
        if record.get("status") != "pending" or record.get("digest") is not None:
            errors.append(f"{input_id}: input must remain pending and unfrozen with digest=null")
    constitution_input = inputs.get(INPUT_IDS[0], {})
    if constitution_input.get("source_ref") != SUBJECT_REF:
        errors.append("constitution-version input must reference constitution/constitution.yaml")
    if constitution_input.get("value") != {"schema_version": "0.1"}:
        errors.append("constitution-version input must preserve observed schema_version 0.1")
    validator_input = inputs.get(INPUT_IDS[1], {})
    expected_validators = sorted(
        str(path.relative_to(root)) for path in (root / "validation").glob("*_validator.py")
    )
    if validator_input.get("value") != expected_validators:
        errors.append("validator-list input must exactly match the current validator paths")
    repository_input = inputs.get(INPUT_IDS[2], {})
    expected_repository_state = {
        "git_repository": False,
        "commit": None,
        "working_tree_state": "unavailable_not_a_git_repository",
    }
    if repository_input.get("source_ref") != str(root):
        errors.append("repository-state input must reference the DBOS root")
    if repository_input.get("value") != expected_repository_state:
        errors.append("repository-state input must preserve the observed non-Git state")
    if (root / ".git").exists():
        errors.append("repository-state input says non-Git but a .git identity now exists")
    input_meta = input_doc.get("metadata", {})
    if input_meta.get("input_count") != 3:
        errors.append("genesis input metadata count must be three")
    if input_meta.get("input_status_distribution", {}).get("pending") != 3:
        errors.append("all three genesis inputs must remain pending")
    require_zero(
        input_meta,
        ("frozen_input_count", "execution_count", "event_created_count", "permission_grant_count", "capability_effect_count"),
        "input",
        errors,
    )

    outputs = index_records(
        output_doc.get("experiment_outputs"), "output_id", "experiment_outputs", errors
    )
    if tuple(outputs) != OUTPUT_IDS:
        errors.append("genesis output registry must contain exactly six ordered expected outputs")
    for output_id, expected_type in zip(OUTPUT_IDS, OUTPUT_TYPES):
        record = outputs.get(output_id, {})
        if record.get("experiment_id") != EXPERIMENT_ID:
            errors.append(f"{output_id}: output must reference DBOS-EXP-0001")
        if record.get("output_type") != expected_type:
            errors.append(f"{output_id}: output_type must remain {expected_type}")
        if record.get("status") != "expected":
            errors.append(f"{output_id}: output status must remain expected")
        if record.get("artifact_ref") is not None or record.get("evidence_ref") is not None:
            errors.append(f"{output_id}: expected output must not contain artifact or evidence references")
        reject_result_fields(record, output_id, errors)
    output_meta = output_doc.get("metadata", {})
    if output_meta.get("output_count") != 6:
        errors.append("genesis output metadata count must be six")
    if output_meta.get("output_status_distribution", {}).get("expected") != 6:
        errors.append("all six genesis outputs must remain expected")
    require_zero(
        output_meta,
        (
            "generated_output_count",
            "event_created_count",
            "evidence_created_count",
            "verification_result_count",
            "permission_grant_count",
            "capability_effect_count",
        ),
        "output",
        errors,
    )

    stop_rules = index_records(
        stop_doc.get("experiment_stop_rules"),
        "stop_rule_id",
        "experiment_stop_rules",
        errors,
    )
    if tuple(stop_rules) != tuple(STOP_RULES):
        errors.append("genesis stop-rule registry must preserve one success and three failure rules")
    stop_status_counts: Counter[str] = Counter()
    for stop_rule_id, (outcome, condition) in STOP_RULES.items():
        record = stop_rules.get(stop_rule_id, {})
        if record.get("experiment_id") != EXPERIMENT_ID:
            errors.append(f"{stop_rule_id}: stop rule must reference DBOS-EXP-0001")
        if record.get("outcome") != outcome or record.get("condition") != condition:
            errors.append(f"{stop_rule_id}: stop-rule outcome or condition mismatch")
        status = record.get("status")
        stop_status_counts[status] += 1
        if status != "defined":
            errors.append(f"{stop_rule_id}: stop rule must remain defined and unevaluated")
        if not nonempty_string(record.get("scope")) or not nonempty_string(record.get("action")):
            errors.append(f"{stop_rule_id}: stop-rule scope and action must be explicit")
    stop_meta = stop_doc.get("metadata", {})
    if stop_meta.get("stop_rule_count") != 4:
        errors.append("genesis stop-rule metadata count must be four")
    if stop_meta.get("success_rule_count") != 1 or stop_meta.get("failure_rule_count") != 3:
        errors.append("genesis stop rules must report one success and three failure rules")
    if stop_meta.get("stop_rule_status_distribution", {}).get("defined") != 4:
        errors.append("all four genesis stop rules must remain defined")
    require_zero(
        stop_meta,
        ("evaluated_rule_count", "experiment_execution_count"),
        "stop rule",
        errors,
    )
    if stop_meta.get("automatic_execution_effect") != "none":
        errors.append("genesis stop rules cannot execute the experiment automatically")

    authorizations = index_records(
        authorization_doc.get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    if tuple(authorizations) != (AUTHORIZATION_ID,):
        errors.append("genesis authorization registry must contain exactly one pending record")
    authorization = authorizations.get(AUTHORIZATION_ID, {})
    if authorization.get("experiment_id") != EXPERIMENT_ID:
        errors.append("genesis authorization must reference DBOS-EXP-0001")
    if authorization.get("status") != "pending":
        errors.append("genesis authorization status must remain pending")
    if authorization.get("authorized_by") is not None or authorization.get("decision_at") is not None:
        errors.append("pending genesis authorization requires authorized_by=null and decision_at=null")
    scope = authorization.get("scope")
    if not isinstance(scope, dict) or scope.get("experiment_id") != EXPERIMENT_ID or scope.get("current_effect") != "none":
        errors.append("pending genesis authorization scope must be experiment-bound with current_effect=none")
    auth_meta = authorization_doc.get("metadata", {})
    if auth_meta.get("authorization_count") != 1:
        errors.append("genesis authorization metadata count must be one")
    if auth_meta.get("authorization_status_distribution", {}).get("pending") != 1:
        errors.append("genesis authorization distribution must remain pending=1")
    require_zero(
        auth_meta,
        ("active_authorization_count", "execution_authority_count", "permission_grant_count", "runtime_creation_authority_count"),
        "authorization",
        errors,
    )

    contexts = context_doc.get("execution_contexts")
    events = event_doc.get("events")
    integrity_records = integrity_doc.get("event_integrity_records")
    attestations = attestation_doc.get("event_attestations")
    observations = observation_doc.get("experiment_observations")
    runtimes = runtime_doc.get("runtime_instances")
    for value, label in (
        (contexts, "execution contexts"),
        (events, "events"),
        (integrity_records, "integrity records"),
        (attestations, "attestations"),
        (observations, "experiment observations"),
        (runtimes, "runtime instances"),
    ):
        if not isinstance(value, list):
            errors.append(f"{label} must be a list")
        elif value:
            errors.append(f"genesis registration must not create {label}")

    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("genesis registration must not create a capability")
        capabilities = []
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("capability claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append("genesis registration must preserve capability claims at pending/C1")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("capability evidence must be a list")
        evidence_records = []
    for evidence_record in evidence_records:
        if not isinstance(evidence_record, dict) or evidence_record.get("status") != "pending" or evidence_record.get("evidence_type") != "E1":
            errors.append("genesis registration must preserve capability evidence at pending/E1")
            break
    verification_records = verification_doc.get("verification_records")
    if not isinstance(verification_records, list):
        errors.append("verification records must be a list")
        verification_records = []
    for verification in verification_records:
        if (
            not isinstance(verification, dict)
            or verification.get("status") != "pending"
            or verification.get("decision") != "pending"
            or verification.get("verification_level") != "V0"
        ):
            errors.append("genesis registration must preserve verification at pending/V0")
            break
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("genesis registration must not create an organism candidate")
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
            errors.append("genesis registration cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("genesis registration cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("genesis registration cannot calculate fitness")
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("genesis registration must not create an Agent entity")

    mappings = index_records(mapping_doc.get("mappings"), "layer", "SAEE mappings", errors)
    mapping = mappings.get("Genesis Experiment")
    expected_mapping = {
        "current_authority": "constitution/experimental-protocol-constitution.yaml",
        "current_registry": "registry/experiments.yaml",
        "saee_correspondence": "fact formation",
        "status": "registered_genesis_experiment_not_authorized",
        "authority_effect": "none",
    }
    if mapping is None:
        errors.append("SAEE mapping must include Experiment -> Fact Formation")
    else:
        for field, expected in expected_mapping.items():
            if mapping.get(field) != expected:
                errors.append(f"Genesis Experiment SAEE mapping {field} mismatch")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mappings):
        errors.append("SAEE mapping metadata count mismatch")

    constitution_path = root / "constitution" / "experimental-protocol-constitution.yaml"
    if not constitution_path.is_file():
        errors.append("experimental protocol constitution does not exist")
    else:
        constitution_text = constitution_path.read_text(encoding="utf-8")
        for token in (
            'experiment_id: "DBOS-EXP-0001"',
            'input_registry: "../registry/experiment-inputs.yaml"',
            'output_registry: "../registry/experiment-outputs.yaml"',
            'stop_rule_registry: "../registry/experiment-stop-rules.yaml"',
            'authorization_registry: "../registry/experiment-authorizations.yaml"',
            'authorization_status: "pending"',
            'execution_status: "not_executed"',
            'relation: "Experiment -> Fact Formation"',
        ):
            if token not in constitution_text:
                errors.append(f"genesis experiment constitution reference missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_count": len(experiments),
        "experiment_status": experiment.get("status"),
        "procedure_count": len(procedures),
        "procedure_status": procedure.get("status"),
        "procedure_step_count": len(steps),
        "input_count": len(inputs),
        "pending_input_count": sum(record.get("status") == "pending" for record in inputs.values()),
        "expected_output_count": len(outputs),
        "generated_output_count": sum(record.get("status") == "generated" for record in outputs.values()),
        "stop_rule_count": len(stop_rules),
        "defined_stop_rule_count": stop_status_counts.get("defined", 0),
        "authorization_count": len(authorizations),
        "authorization_status": authorization.get("status"),
        "execution_count": 0,
        "event_count": len(events) if isinstance(events, list) else 0,
        "execution_context_count": len(contexts) if isinstance(contexts, list) else 0,
        "runtime_instance_count": len(runtimes) if isinstance(runtimes, list) else 0,
        "agent_created_count": 0,
        "organism_candidate_count": len(candidates),
        "digital_organism_count": 0,
        "capability_count": len(capabilities),
        "permission_grant_count": 0,
        "c_e_v_level_change_count": 0,
        "fact_formation_status": "not_formed",
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiments", type=Path, default=root / "registry" / "experiments.yaml")
    parser.add_argument("--procedures", type=Path, default=root / "registry" / "experiment-procedures.yaml")
    parser.add_argument("--inputs", type=Path, default=root / "registry" / "experiment-inputs.yaml")
    parser.add_argument("--outputs", type=Path, default=root / "registry" / "experiment-outputs.yaml")
    parser.add_argument("--stop-rules", type=Path, default=root / "registry" / "experiment-stop-rules.yaml")
    parser.add_argument("--authorizations", type=Path, default=root / "registry" / "experiment-authorizations.yaml")
    parser.add_argument("--requirements", type=Path, default=root / "registry" / "reproducibility-requirements.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--integrity", type=Path, default=root / "registry" / "event-integrity.yaml")
    parser.add_argument("--attestations", type=Path, default=root / "registry" / "event-attestations.yaml")
    parser.add_argument("--observations", type=Path, default=root / "registry" / "experiment-observations.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--mapping", type=Path, default=root / "registry" / "evolution-mapping.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced
    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        result = validate(
            load_json_yaml(args.experiments),
            load_json_yaml(args.procedures),
            load_json_yaml(args.inputs),
            load_json_yaml(args.outputs),
            load_json_yaml(args.stop_rules),
            load_json_yaml(args.authorizations),
            load_json_yaml(args.requirements),
            load_json_yaml(args.entities),
            load_json_yaml(args.environments),
            load_json_yaml(args.contexts),
            load_json_yaml(args.events),
            load_json_yaml(args.integrity),
            load_json_yaml(args.attestations),
            load_json_yaml(args.observations),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            load_json_yaml(args.mapping),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for error in result.get("errors", []):
            print(f"- {error}")
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
