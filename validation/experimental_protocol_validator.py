#!/usr/bin/env python3
"""Validate the Experimental Protocol Layer without third-party packages.

Agent-readable contract:
- Experiment definitions, procedures, and reproducibility rules are contracts,
  not runs, events, observations, evidence, runtimes, or authorizations.
- A future defined experiment binds a canonical subject to at least one procedure
  and all five reproducibility requirements while execution_authority remains
  not_granted until a separate attributable decision exists.
- Procedures are declarative ordered steps and cannot execute tools or fabricate
  outputs, timestamps, observations, fitness, or completion states.
- Experiment observations require an existing experiment and never create
  fitness, evolution, capability, permission, or C/E/V promotion automatically.
- One genesis experiment and one eight-step procedure may be registered while
  observations, executions, events, contexts, runtimes, and results remain empty;
  five reproducibility requirement definitions exist with zero satisfied rules.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_STATUSES = (
    "proposed",
    "defined",
    "registered",
    "authorized",
    "running",
    "observed",
    "completed",
    "invalid",
    "revoked",
    "retired",
)
REQUIREMENT_IDS = (
    "version_lock",
    "dependency_lock",
    "input_consistency",
    "environment_consistency",
    "execution_method",
)
EXPERIMENT_ID_RE = re.compile(r"^dbio:experiment:([a-z0-9][a-z0-9._-]*):([1-9][0-9]*)$")
DBOS_EXPERIMENT_ID_RE = re.compile(r"^DBOS-EXP-[0-9]{4}$")
REQUIRED_EXPERIMENT_FIELDS = {
    "experiment_id",
    "name",
    "objective",
    "subject",
    "protocol",
    "status",
    "created_at",
}
REQUIRED_PROTOCOL_FIELDS = {
    "version",
    "procedure_refs",
    "reproducibility_requirement_refs",
    "execution_authority",
    "limitations",
}
REQUIRED_PROCEDURE_FIELDS = {
    "procedure_id",
    "experiment_id",
    "steps",
    "environment",
    "inputs",
    "expected_outputs",
    "status",
}
PROCEDURE_STATUSES = (
    "procedure_defined",
    "authorized",
    "executing",
    "completed",
    "invalid",
    "revoked",
)
REQUIRED_STEP_FIELDS = {
    "step_id",
    "action",
    "input_refs",
    "expected_output_refs",
    "side_effect",
    "authority_required",
    "stop_conditions",
    "evidence_requirement",
}
REQUIRED_REQUIREMENT_FIELDS = {
    "requirement_id",
    "name",
    "description",
    "required_material",
    "validation_boundary",
    "authority_effect",
}
REQUIRED_OBSERVATION_FIELDS = {
    "observation_id",
    "experiment_id",
    "metric",
    "value",
    "timestamp",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "agent_id",
    "agent_created",
    "capability_id",
    "capability_assignment",
    "capability_assignment_status",
    "permission",
    "permissions",
    "permission_grant",
    "permission_status",
    "fitness_score",
    "fitness_effect",
    "evolution_effect",
    "maturity_level",
    "evidence_level",
    "verification_level",
}
FORBIDDEN_PROCEDURE_RESULT_KEYS = {
    "actual_output",
    "execution_result",
    "executed_at",
    "exit_status",
    "observation",
    "event_id",
    "fitness",
}
ZERO_EFFECT_FIELDS = (
    "event_created_count",
    "runtime_created_count",
    "agent_created_count",
    "organism_created_count",
    "fitness_effect_count",
    "evolution_effect_count",
    "capability_effect_count",
    "permission_grant_count",
    "c_e_v_level_change_count",
    "evidence_created_count",
    "execution_result_count",
    "executed_procedure_count",
    "executed_experiment_count",
    "authorized_experiment_count",
)


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


def nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(nonempty_string(item) for item in value)
    )


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def reject_authority_fields(record: dict[str, Any], label: str, errors: list[str]) -> None:
    present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(record))
    if present:
        errors.append(f"{label}: experimental protocol cannot create authority fields {present}")


def require_zero_effect_metadata(metadata: Any, label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in ZERO_EFFECT_FIELDS:
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(
    experiment_doc: dict[str, Any],
    procedure_doc: dict[str, Any],
    requirement_doc: dict[str, Any],
    observation_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    environment_doc: dict[str, Any],
    context_doc: dict[str, Any],
    input_doc: dict[str, Any],
    output_doc: dict[str, Any],
    event_doc: dict[str, Any],
    event_observation_doc: dict[str, Any],
    attestation_doc: dict[str, Any],
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
    """Validate experiment protocol taxonomy, empty fact state, and boundaries."""
    errors: list[str] = []
    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    environments = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    contexts = index_records(
        context_doc.get("execution_contexts"), "context_id", "execution_contexts", errors
    )
    input_snapshots = index_records(
        input_doc.get("input_snapshots"), "snapshot_id", "input_snapshots", errors
    )
    output_snapshots = index_records(
        output_doc.get("output_snapshots"), "snapshot_id", "output_snapshots", errors
    )
    events = index_records(event_doc.get("events"), "event_id", "events", errors)
    event_observations = index_records(
        event_observation_doc.get("event_observations"),
        "observation_id",
        "event_observations",
        errors,
    )
    attestations = index_records(
        attestation_doc.get("event_attestations"),
        "attestation_id",
        "event_attestations",
        errors,
    )
    capabilities = index_records(
        capability_doc.get("capabilities"), "capability_id", "capabilities", errors
    )
    claims = index_records(claim_doc.get("claims"), "claim_id", "capability_claims", errors)
    evidence = index_records(
        evidence_doc.get("evidence"), "evidence_id", "capability_evidence", errors
    )
    verifications = index_records(
        verification_doc.get("verification_records"),
        "verification_id",
        "verification_records",
        errors,
    )
    runtimes = index_records(
        runtime_doc.get("runtime_instances"), "runtime_id", "runtime_instances", errors
    )

    requirements = index_records(
        requirement_doc.get("reproducibility_requirements"),
        "requirement_id",
        "reproducibility_requirements",
        errors,
    )
    if tuple(requirements) != REQUIREMENT_IDS:
        errors.append("reproducibility requirements must preserve all five ordered definitions")
    for requirement_id, requirement in requirements.items():
        missing = REQUIRED_REQUIREMENT_FIELDS - set(requirement)
        if missing:
            errors.append(f"{requirement_id}: missing requirement fields {sorted(missing)}")
        for field in ("name", "description", "validation_boundary"):
            if not nonempty_string(requirement.get(field)):
                errors.append(f"{requirement_id}: {field} must be non-empty")
        if not nonempty_string_list(requirement.get("required_material")):
            errors.append(f"{requirement_id}: required_material must be a non-empty string list")
        if requirement.get("authority_effect") != "none":
            errors.append(f"{requirement_id}: reproducibility requirement cannot create authority")
        if requirement.get("satisfied") is True or requirement.get("verified") is True:
            errors.append(f"{requirement_id}: requirement definition cannot claim satisfaction or verification")
        reject_authority_fields(requirement, requirement_id, errors)
    requirement_meta = requirement_doc.get("metadata", {})
    if requirement_meta.get("reproducibility_requirement_count") != len(requirements):
        errors.append("reproducibility requirement metadata count mismatch")
    for field in (
        "satisfied_requirement_count",
        "verified_requirement_count",
        "automatic_reproducibility_count",
    ):
        if requirement_meta.get(field) != 0:
            errors.append(f"reproducibility requirement metadata {field} must remain zero")
    if requirement_meta.get("automatic_authority_effect") != "none":
        errors.append("reproducibility requirements cannot create authority automatically")

    experiments = index_records(
        experiment_doc.get("experiments"), "experiment_id", "experiments", errors
    )
    procedures = index_records(
        procedure_doc.get("experiment_procedures"),
        "procedure_id",
        "experiment_procedures",
        errors,
    )
    procedures_by_experiment: dict[str, list[str]] = defaultdict(list)
    step_count = 0
    for procedure_id, procedure in procedures.items():
        missing = REQUIRED_PROCEDURE_FIELDS - set(procedure)
        if missing:
            errors.append(f"{procedure_id}: missing procedure fields {sorted(missing)}")
        experiment_id = procedure.get("experiment_id")
        if experiment_id not in experiments:
            errors.append(f"{procedure_id}: procedure must reference an existing experiment")
        elif isinstance(experiment_id, str):
            procedures_by_experiment[experiment_id].append(procedure_id)
        if not procedure_id.startswith(f"dbio:experiment-procedure:{experiment_id}:"):
            errors.append(f"{procedure_id}: procedure_id must bind the referenced experiment")
        if procedure.get("status") not in PROCEDURE_STATUSES:
            errors.append(f"{procedure_id}: invalid procedure status {procedure.get('status')!r}")
        if procedure.get("status") in {"authorized", "executing", "completed"}:
            errors.append(f"{procedure_id}: experimental protocol registration cannot claim procedure execution state")
        if procedure.get("environment") not in environments:
            errors.append(f"{procedure_id}: procedure must reference an existing environment")
        if not isinstance(procedure.get("inputs"), list):
            errors.append(f"{procedure_id}: inputs must be a list")
        if not isinstance(procedure.get("expected_outputs"), list) or not procedure.get("expected_outputs"):
            errors.append(f"{procedure_id}: expected_outputs must be a non-empty list")
        steps = procedure.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{procedure_id}: steps must be a non-empty list")
            steps = []
        step_ids: set[str] = set()
        for index, step in enumerate(steps):
            where = f"{procedure_id}.steps[{index}]"
            if not isinstance(step, dict):
                errors.append(f"{where} must be a mapping")
                continue
            step_count += 1
            missing_step = REQUIRED_STEP_FIELDS - set(step)
            if missing_step:
                errors.append(f"{where}: missing step fields {sorted(missing_step)}")
            step_id = step.get("step_id")
            if not nonempty_string(step_id):
                errors.append(f"{where}: step_id must be non-empty")
            elif step_id in step_ids:
                errors.append(f"{procedure_id}: duplicate step_id {step_id}")
            else:
                step_ids.add(step_id)
            if not nonempty_string(step.get("action")):
                errors.append(f"{where}: action must be non-empty")
            for field in ("input_refs", "expected_output_refs", "stop_conditions"):
                if not isinstance(step.get(field), list):
                    errors.append(f"{where}: {field} must be a list")
            if not nonempty_string(step.get("side_effect")):
                errors.append(f"{where}: side_effect must be explicit")
            if step.get("authority_required") not in {"none", "separate_authorization"}:
                errors.append(f"{where}: authority_required must be none or separate_authorization")
            evidence_requirement = step.get("evidence_requirement")
            if not (
                nonempty_string(evidence_requirement)
                or nonempty_string_list(evidence_requirement)
            ):
                errors.append(f"{where}: evidence_requirement must be explicit")
            fabricated = sorted(FORBIDDEN_PROCEDURE_RESULT_KEYS.intersection(step))
            if fabricated:
                errors.append(f"{where}: procedure step cannot contain execution results {fabricated}")
            reject_authority_fields(step, where, errors)
        fabricated = sorted(FORBIDDEN_PROCEDURE_RESULT_KEYS.intersection(procedure))
        if fabricated:
            errors.append(f"{procedure_id}: procedure cannot contain execution results {fabricated}")
        reject_authority_fields(procedure, procedure_id, errors)

    experiment_status_counts: Counter[str] = Counter()
    for experiment_id, experiment in experiments.items():
        missing = REQUIRED_EXPERIMENT_FIELDS - set(experiment)
        if missing:
            errors.append(f"{experiment_id}: missing experiment fields {sorted(missing)}")
        match = EXPERIMENT_ID_RE.fullmatch(experiment_id)
        dbos_match = DBOS_EXPERIMENT_ID_RE.fullmatch(experiment_id)
        if match is None and dbos_match is None:
            errors.append(f"{experiment_id}: invalid experiment_id format")
        subject = experiment.get("subject")
        governed_subject = (
            subject == "digital-biosphere-os"
            and experiment.get("subject_kind") == "governed_system_subject"
            and experiment.get("subject_ref") == "constitution/constitution.yaml"
            and (root / "constitution" / "constitution.yaml").is_file()
        )
        if subject not in entities and not governed_subject:
            errors.append(f"{experiment_id}: experiment subject must resolve to an entity or bounded governed-system subject")
        elif match is not None and match.group(1) != subject:
            errors.append(f"{experiment_id}: experiment_id subject segment must match subject")
        if not nonempty_string(experiment.get("name")):
            errors.append(f"{experiment_id}: name must be non-empty")
        if not nonempty_string(experiment.get("objective")):
            errors.append(f"{experiment_id}: objective must be non-empty")
        if not valid_timestamp(experiment.get("created_at")):
            errors.append(f"{experiment_id}: created_at must be timezone-aware")
        status = experiment.get("status")
        if status not in EXPERIMENT_STATUSES:
            errors.append(f"{experiment_id}: invalid experiment status {status!r}")
        else:
            experiment_status_counts[status] += 1
        protocol = experiment.get("protocol")
        if not isinstance(protocol, dict):
            errors.append(f"{experiment_id}: protocol must be a mapping")
            protocol = {}
        missing_protocol = REQUIRED_PROTOCOL_FIELDS - set(protocol)
        if missing_protocol:
            errors.append(f"{experiment_id}: protocol missing fields {sorted(missing_protocol)}")
        if not nonempty_string(protocol.get("version")):
            errors.append(f"{experiment_id}: protocol version must be non-empty")
        procedure_refs = protocol.get("procedure_refs")
        if not nonempty_string_list(procedure_refs):
            errors.append(f"{experiment_id}: protocol requires at least one procedure_ref")
            procedure_refs = []
        elif len(procedure_refs) != len(set(procedure_refs)):
            errors.append(f"{experiment_id}: procedure_refs must be unique")
        if sorted(procedure_refs) != sorted(procedures_by_experiment.get(experiment_id, [])):
            errors.append(f"{experiment_id}: procedure_refs do not exactly match procedure records")
        requirement_refs = protocol.get("reproducibility_requirement_refs")
        if not isinstance(requirement_refs, list) or tuple(requirement_refs) != REQUIREMENT_IDS:
            errors.append(f"{experiment_id}: protocol must reference all five ordered reproducibility requirements")
        execution_authority = protocol.get("execution_authority")
        if status in {"proposed", "defined", "registered"} and execution_authority != "not_granted":
            errors.append(f"{experiment_id}: proposed, defined, or registered experiment cannot have execution authority")
        if not isinstance(protocol.get("limitations"), list) or not protocol.get("limitations"):
            errors.append(f"{experiment_id}: protocol limitations must be a non-empty list")
        if status in {"authorized", "running", "observed", "completed"}:
            if not nonempty_string(experiment.get("authorization_ref")):
                errors.append(f"{experiment_id}: {status} experiment requires authorization_ref")
        if status in {"running", "observed", "completed"}:
            context_ref = experiment.get("execution_context_ref")
            runtime_ref = experiment.get("runtime_ref")
            if context_ref not in contexts:
                errors.append(f"{experiment_id}: {status} experiment requires existing execution_context_ref")
            if runtime_ref not in runtimes:
                errors.append(f"{experiment_id}: {status} experiment requires existing runtime_ref")
            context = contexts.get(context_ref, {})
            if context.get("entity_id") != subject:
                errors.append(f"{experiment_id}: execution context entity must match experiment subject")
        reject_authority_fields(experiment, experiment_id, errors)

    observations = index_records(
        observation_doc.get("experiment_observations"),
        "observation_id",
        "experiment_observations",
        errors,
    )
    observations_by_experiment: Counter[str] = Counter()
    for observation_id, observation in observations.items():
        missing = REQUIRED_OBSERVATION_FIELDS - set(observation)
        if missing:
            errors.append(f"{observation_id}: missing observation fields {sorted(missing)}")
        experiment_id = observation.get("experiment_id")
        experiment = experiments.get(experiment_id)
        if experiment is None:
            errors.append(f"{observation_id}: observation must reference an existing experiment")
        else:
            observations_by_experiment[experiment_id] += 1
            if experiment.get("status") not in {"running", "observed", "completed"}:
                errors.append(f"{observation_id}: observation requires a running, observed, or completed experiment")
        if not observation_id.startswith(f"dbio:experiment-observation:{experiment_id}:"):
            errors.append(f"{observation_id}: observation_id must bind the referenced experiment")
        if not nonempty_string(observation.get("metric")):
            errors.append(f"{observation_id}: metric must be non-empty")
        if observation.get("value") is None:
            errors.append(f"{observation_id}: value must be non-null")
        if not valid_timestamp(observation.get("timestamp")):
            errors.append(f"{observation_id}: timestamp must be timezone-aware")
        reject_authority_fields(observation, observation_id, errors)
    for experiment_id, experiment in experiments.items():
        if experiment.get("status") in {"observed", "completed"} and observations_by_experiment.get(experiment_id, 0) == 0:
            errors.append(f"{experiment_id}: observed or completed experiment requires observation records")

    experiment_meta = experiment_doc.get("metadata", {})
    if experiment_meta.get("default_experiment_status") != "defined":
        errors.append("experiment schema default status must remain defined")
    if experiment_meta.get("experiment_count") != len(experiments):
        errors.append("experiment metadata count mismatch")
    for status in EXPERIMENT_STATUSES:
        if experiment_meta.get("experiment_status_distribution", {}).get(status) != experiment_status_counts.get(status, 0):
            errors.append(f"experiment status distribution mismatch for {status}")
    require_zero_effect_metadata(experiment_meta, "experiment", errors)
    procedure_meta = procedure_doc.get("metadata", {})
    if procedure_meta.get("procedure_count") != len(procedures):
        errors.append("procedure metadata count mismatch")
    if procedure_meta.get("procedure_step_count") != step_count:
        errors.append("procedure step metadata count mismatch")
    require_zero_effect_metadata(procedure_meta, "procedure", errors)
    observation_meta = observation_doc.get("metadata", {})
    if observation_meta.get("observation_count") != len(observations):
        errors.append("experiment observation metadata count mismatch")
    require_zero_effect_metadata(observation_meta, "experiment observation", errors)

    # Registration is allowed; execution, observations, and generated facts are not.
    if any(experiment.get("status") in {"authorized", "running", "observed", "completed"} for experiment in experiments.values()):
        errors.append("experimental protocol registration must not authorize or execute experiments")
    if any(procedure.get("status") in {"authorized", "executing", "completed"} for procedure in procedures.values()):
        errors.append("experimental protocol registration must not execute procedures")
    if observations:
        errors.append("v0.1 baseline must not fabricate experiment observations")
    if contexts or input_snapshots or output_snapshots:
        errors.append("experimental protocol layer must not create execution context or snapshots")
    if events or event_observations:
        errors.append("experimental protocol layer must not create events or event observations")
    if attestations:
        errors.append("experimental protocol layer must not create attestations")
    if runtimes:
        errors.append("experimental protocol layer must not create a runtime")
    if capabilities:
        errors.append("experimental protocol layer must not create a capability")

    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list):
        errors.append("organism_candidates must be a list")
        candidates = []
    if candidates:
        errors.append("experimental protocol layer must not create an organism candidate")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("experiment protocol cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("experiment protocol cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("experiment observation cannot calculate fitness")
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("experimental protocol layer must not create an Agent entity")

    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(f"{claim_id}: experiment protocol must preserve capability claims at pending/C1")
            break
    for evidence_id, evidence_record in evidence.items():
        if evidence_record.get("status") != "pending" or evidence_record.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: experiment protocol must preserve capability evidence at pending/E1")
            break
    for verification_id, verification in verifications.items():
        if (
            verification.get("status") != "pending"
            or verification.get("decision") != "pending"
            or verification.get("verification_level") != "V0"
        ):
            errors.append(f"{verification_id}: experiment protocol must preserve verification at pending/V0")
            break

    mappings = index_records(mapping_doc.get("mappings"), "layer", "SAEE mappings", errors)
    experiment_mapping = mappings.get("Experiment")
    expected_mapping = {
        "current_authority": "constitution/experimental-protocol-constitution.yaml",
        "current_registry": "registry/experiments.yaml",
        "saee_correspondence": "observation-mediated evolution",
        "status": "registered_experimental_protocol_one_experiment_unexecuted",
        "authority_effect": "none",
    }
    if experiment_mapping is None:
        errors.append("SAEE mapping must include Experiment -> Observation -> Evolution")
    else:
        for field, expected in expected_mapping.items():
            if experiment_mapping.get(field) != expected:
                errors.append(f"Experiment SAEE mapping {field} mismatch")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mappings):
        errors.append("SAEE mapping metadata count mismatch")

    protocol_constitution = root / "constitution" / "experimental-protocol-constitution.yaml"
    context_constitution = root / "constitution" / "execution-context-constitution.yaml"
    if not protocol_constitution.is_file():
        errors.append("experimental protocol constitution does not exist")
    if not context_constitution.is_file():
        errors.append("execution context constitution does not exist")
    else:
        constitution_text = context_constitution.read_text(encoding="utf-8")
        for token in (
            'experimental_protocol_reference: "experimental-protocol-constitution.yaml"',
            'experiment_registry: "../registry/experiments.yaml"',
            'procedure_registry: "../registry/experiment-procedures.yaml"',
            'reproducibility_requirement_registry: "../registry/reproducibility-requirements.yaml"',
            'observation_registry: "../registry/experiment-observations.yaml"',
        ):
            if token not in constitution_text:
                errors.append(f"execution context constitution experiment reference missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "experiment_count": len(experiments),
        "experiment_status_distribution": {
            status: experiment_status_counts.get(status, 0)
            for status in EXPERIMENT_STATUSES
        },
        "procedure_count": len(procedures),
        "procedure_step_count": step_count,
        "reproducibility_requirement_count": len(requirements),
        "satisfied_reproducibility_requirement_count": 0,
        "experiment_observation_count": len(observations),
        "execution_count": 0,
        "event_count": len(events),
        "execution_context_count": len(contexts),
        "attestation_count": len(attestations),
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
    parser.add_argument("--experiments", type=Path, default=root / "registry" / "experiments.yaml")
    parser.add_argument("--procedures", type=Path, default=root / "registry" / "experiment-procedures.yaml")
    parser.add_argument("--requirements", type=Path, default=root / "registry" / "reproducibility-requirements.yaml")
    parser.add_argument("--observations", type=Path, default=root / "registry" / "experiment-observations.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--inputs", type=Path, default=root / "registry" / "input-snapshots.yaml")
    parser.add_argument("--outputs", type=Path, default=root / "registry" / "output-snapshots.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--event-observations", type=Path, default=root / "registry" / "event-observations.yaml")
    parser.add_argument("--attestations", type=Path, default=root / "registry" / "event-attestations.yaml")
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
            load_json_yaml(args.requirements),
            load_json_yaml(args.observations),
            load_json_yaml(args.entities),
            load_json_yaml(args.environments),
            load_json_yaml(args.contexts),
            load_json_yaml(args.inputs),
            load_json_yaml(args.outputs),
            load_json_yaml(args.events),
            load_json_yaml(args.event_observations),
            load_json_yaml(args.attestations),
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
