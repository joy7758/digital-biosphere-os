#!/usr/bin/env python3
"""Validate the deterministic Automated Experiment Runner model without running it.

Agent-readable contract:
- Runner is a deterministic Executor implementation, not an Agent, Runtime,
  Candidate Organism, or Digital Organism.
- The v0.1 Runner, scope, execution, and evidence registries are empty.
- One environment slot is defined but unqualified and contains no fabricated
  OS, Python, dependency, digest, lock, or execution facts.
- Runner records can reference only registered experiments and ordered steps.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "DBOS-EXP-0001"
RUNNER_ENVIRONMENT_ID = "dbio://runner-environment/dbos-exp-0001/local-governance-workspace/v0.1"
SOURCE_ENVIRONMENT_ID = "dbio://environment/local-governance-workspace/v0.1"
ENVIRONMENT_LOCK_ID = "DBOS-EXP-0001-ENV-LOCK-0001"
ENVIRONMENT_QUALIFICATION_ID = "DBOS-EXP-0001-RUNNER-ENV-QUAL-0001"
STEP_IDS = tuple(f"DBOS-EXP-0001-STEP-{index:02d}" for index in range(1, 9))
RUNNER_TYPES = {"automated_runner"}
EXECUTION_MODES = {"deterministic"}
RUNNER_STATUSES = {"proposed", "identity_verified", "registered", "ready", "suspended", "revoked", "retired"}
SCOPE_STATUSES = {"proposed", "defined", "approved", "suspended", "revoked", "superseded"}
ENVIRONMENT_STATUSES = {"defined", "qualified", "frozen", "invalid", "revoked", "superseded"}
EXECUTION_STATUSES = {"pending", "authorized", "running", "stopped", "succeeded", "failed", "invalid", "revoked"}
TERMINAL_EXECUTION_STATUSES = {"stopped", "succeeded", "failed", "invalid", "revoked"}
MANDATORY_FORBIDDEN_OPERATIONS = {
    "modify_constitution",
    "modify_history",
    "create_agent",
    "grant_permission",
}
FORBIDDEN_EFFECT_KEYS = {
    "agent_id",
    "runtime_id",
    "organism_id",
    "capability_id",
    "capability_assignment",
    "permission",
    "permission_grant",
    "permission_status",
    "event_id",
    "snapshot_hash",
    "evidence_level",
    "verification_level",
    "maturity_level",
    "fitness_score",
}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping without third-party packages."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def index_records(records: Any, key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
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
        if not isinstance(identifier, str) or not identifier.strip():
            errors.append(f"{where}.{key} must be a non-empty string")
            continue
        if identifier in indexed:
            errors.append(f"duplicate {key}: {identifier}")
            continue
        indexed[identifier] = record
    return indexed


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timestamp(value: Any) -> bool:
    if not nonempty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reject_effect_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        present = sorted(FORBIDDEN_EFFECT_KEYS.intersection(value))
        if present:
            errors.append(f"{label}: Runner governance cannot contain authority or promotion fields {present}")
        for key, child in value.items():
            reject_effect_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_effect_keys(child, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate(docs: dict[str, dict[str, Any]], texts: dict[str, str], root: Path) -> dict[str, Any]:
    """Validate Runner identity, scope, environment, execution, and evidence boundaries."""
    errors: list[str] = []

    experiments = index_records(docs["experiments"].get("experiments"), "experiment_id", "experiments", errors)
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("Runner layer requires exactly registered DBOS-EXP-0001")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if experiment.get("status") != "registered" or experiment.get("execution_status") != "not_executed":
        errors.append("Runner modeling cannot authorize or execute DBOS-EXP-0001")
    for field in ("execution_context_ref", "runtime_ref", "run_ref"):
        if experiment.get(field) is not None:
            errors.append(f"DBOS-EXP-0001 {field} must remain null")

    procedures = index_records(
        docs["procedures"].get("experiment_procedures"), "procedure_id", "experiment_procedures", errors
    )
    procedure_steps_by_experiment: dict[str, tuple[str, ...]] = {}
    for procedure_id, procedure in procedures.items():
        experiment_id = procedure.get("experiment_id")
        steps = procedure.get("steps")
        if not isinstance(steps, list):
            errors.append(f"{procedure_id}: steps must be a list")
            continue
        step_ids = tuple(step.get("step_id") for step in steps if isinstance(step, dict))
        if any(not nonempty_string(step_id) for step_id in step_ids) or len(step_ids) != len(steps):
            errors.append(f"{procedure_id}: every procedure step requires step_id")
        if experiment_id in procedure_steps_by_experiment:
            errors.append(f"{experiment_id}: multiple procedures are ambiguous for Runner v0.1")
        elif isinstance(experiment_id, str):
            procedure_steps_by_experiment[experiment_id] = step_ids
    if procedure_steps_by_experiment.get(EXPERIMENT_ID) != STEP_IDS:
        errors.append("Runner step catalog must preserve the eight registered DBOS-EXP-0001 steps in order")

    identities = index_records(
        docs["executor_identities"].get("executor_identities"),
        "executor_identity_id",
        "executor_identities",
        errors,
    )
    executors = index_records(docs["executors"].get("executors"), "executor_id", "executors", errors)

    runner_doc = docs["runners"]
    runners = index_records(runner_doc.get("runners"), "runner_id", "runners", errors)
    runner_type_counts: Counter[str] = Counter()
    execution_mode_counts: Counter[str] = Counter()
    for runner_id, runner in runners.items():
        runner_type = runner.get("runner_type")
        if runner_type not in RUNNER_TYPES:
            errors.append(f"{runner_id}: invalid runner_type {runner_type!r}")
        else:
            runner_type_counts[runner_type] += 1
        execution_mode = runner.get("execution_mode")
        if execution_mode not in EXECUTION_MODES:
            errors.append(f"{runner_id}: execution_mode must be deterministic")
        else:
            execution_mode_counts[execution_mode] += 1
        identity_ref = runner.get("identity_ref")
        identity = identities.get(identity_ref)
        if identity is None:
            errors.append(f"{runner_id}: Runner must reference an existing Executor Identity")
        elif (
            identity.get("identity_type") != "automated"
            or identity.get("verification_status") != "verified"
            or identity.get("lifecycle_state") != "verified"
        ):
            errors.append(f"{runner_id}: Runner requires a verified automated Executor Identity")
        executor_ref = runner.get("executor_ref")
        executor = executors.get(executor_ref)
        if executor is None:
            errors.append(f"{runner_id}: Runner must reference a separately appointed Executor")
        elif executor.get("executor_type") != "automated_runner" or executor.get("identity_ref") != identity_ref:
            errors.append(f"{runner_id}: Runner Executor type and identity must match")
        if not nonempty_string(runner.get("version")):
            errors.append(f"{runner_id}: Runner version must be explicit")
        if runner.get("status") not in RUNNER_STATUSES:
            errors.append(f"{runner_id}: invalid Runner status {runner.get('status')!r}")
        scope_refs = runner.get("scope_refs", [])
        if not isinstance(scope_refs, list):
            errors.append(f"{runner_id}: scope_refs must be a list")
        environment_ref = runner.get("environment_ref")
        if environment_ref not in (None, RUNNER_ENVIRONMENT_ID):
            errors.append(f"{runner_id}: unknown Runner environment_ref {environment_ref!r}")
        if runner.get("status") == "ready":
            if not DIGEST_RE.fullmatch(str(runner.get("implementation_digest", ""))):
                errors.append(f"{runner_id}: ready Runner requires implementation_digest")
            if not scope_refs:
                errors.append(f"{runner_id}: ready Runner requires approved scope_refs")
            if environment_ref != RUNNER_ENVIRONMENT_ID:
                errors.append(f"{runner_id}: ready Runner requires the qualified Runner environment")
        if runner.get("agent_status") not in (None, "not_an_agent"):
            errors.append(f"{runner_id}: Runner cannot become an Agent")
        if runner.get("runtime_status") not in (None, "not_a_runtime"):
            errors.append(f"{runner_id}: Runner cannot become a Runtime")
        if runner.get("organism_status") not in (None, "not_an_organism"):
            errors.append(f"{runner_id}: Runner cannot become an Organism")
        if runner.get("authority_effect", "none") != "none":
            errors.append(f"{runner_id}: Runner registration cannot create execution authority")
        reject_effect_keys(runner, f"Runner {runner_id}", errors)

    if runners:
        errors.append("v0.1 Runner registry must remain empty until identity, appointment, readiness, and authorization exist")
    runner_meta = runner_doc.get("metadata", {})
    if runner_meta.get("runner_count") != 0:
        errors.append("Runner metadata count must remain zero")
    if runner_meta.get("runner_type_distribution", {}).get("automated_runner") != 0:
        errors.append("Runner type distribution must remain automated_runner=0")
    if runner_meta.get("execution_mode_distribution", {}).get("deterministic") != 0:
        errors.append("Runner execution-mode distribution must remain deterministic=0")
    require_zero(
        runner_meta,
        ("ready_runner_count", "agent_created_count", "runtime_created_count", "organism_created_count", "execution_authority_count", "capability_effect_count", "permission_grant_count"),
        "Runner",
        errors,
    )

    scope_doc = docs["runner_scopes"]
    scopes = index_records(scope_doc.get("runner_scopes"), "scope_id", "runner_scopes", errors)
    for scope_id, scope in scopes.items():
        runner_id = scope.get("runner_id")
        if not nonempty_string(runner_id) or runner_id not in runners:
            errors.append(f"{scope_id}: Runner scope must reference an existing Runner")
        allowed_experiments = scope.get("allowed_experiments")
        if not isinstance(allowed_experiments, list) or not allowed_experiments:
            errors.append(f"{scope_id}: allowed_experiments must be explicit and non-empty")
            allowed_experiments = []
        unknown_experiments = sorted(set(allowed_experiments) - set(experiments))
        if unknown_experiments:
            errors.append(f"{scope_id}: Runner can execute only registered experiments; unknown {unknown_experiments}")
        for experiment_id in allowed_experiments:
            if experiments.get(experiment_id, {}).get("status") != "registered":
                errors.append(f"{scope_id}: allowed experiment {experiment_id} is not registered")
        allowed_steps = scope.get("allowed_steps")
        if not isinstance(allowed_steps, list) or not allowed_steps:
            errors.append(f"{scope_id}: allowed_steps must be explicit and non-empty")
            allowed_steps = []
        catalog: list[str] = []
        for experiment_id in allowed_experiments:
            catalog.extend(procedure_steps_by_experiment.get(experiment_id, ()))
        if any(step_id not in catalog for step_id in allowed_steps):
            errors.append(f"{scope_id}: allowed_steps must reference registered procedure steps")
        ordered_projection = [step_id for step_id in catalog if step_id in allowed_steps]
        if allowed_steps != ordered_projection or len(allowed_steps) != len(set(allowed_steps)):
            errors.append(f"{scope_id}: allowed_steps must be unique and preserve registered procedure order")
        forbidden_operations = scope.get("forbidden_operations")
        if not isinstance(forbidden_operations, list):
            errors.append(f"{scope_id}: forbidden_operations must be a list")
            forbidden_operations = []
        missing_forbidden = sorted(MANDATORY_FORBIDDEN_OPERATIONS - set(forbidden_operations))
        if missing_forbidden:
            errors.append(f"{scope_id}: missing mandatory forbidden operations {missing_forbidden}")
        if scope.get("status", "proposed") not in SCOPE_STATUSES:
            errors.append(f"{scope_id}: invalid Runner scope status {scope.get('status')!r}")
        if scope.get("authority_effect", "none") != "none":
            errors.append(f"{scope_id}: Runner scope cannot create permission or execution authority")
        reject_effect_keys(scope, f"Runner scope {scope_id}", errors)

    if scopes:
        errors.append("v0.1 Runner scope registry must remain empty while no Runner exists")
    if scope_doc.get("registered_experiment_catalog") != [EXPERIMENT_ID]:
        errors.append("Runner scope experiment catalog must contain only DBOS-EXP-0001")
    if tuple(scope_doc.get("registered_step_catalog", [])) != STEP_IDS:
        errors.append("Runner scope step catalog must preserve all eight registered steps in order")
    if set(scope_doc.get("mandatory_forbidden_operations", [])) != MANDATORY_FORBIDDEN_OPERATIONS:
        errors.append("Runner scope registry must preserve mandatory forbidden operations")
    scope_meta = scope_doc.get("metadata", {})
    if scope_meta.get("scope_count") != 0:
        errors.append("Runner scope metadata count must remain zero")
    require_zero(scope_meta, ("approved_scope_count", "execution_authority_count", "permission_grant_count"), "Runner scope", errors)

    ecological_environments = index_records(
        docs["environments"].get("environments"), "environment_id", "environments", errors
    )
    environment_locks = index_records(
        docs["environment_locks"].get("environment_locks"), "lock_id", "environment_locks", errors
    )
    environment_doc = docs["runner_environments"]
    runner_environments = index_records(
        environment_doc.get("runner_environments"), "environment_id", "runner_environments", errors
    )
    if tuple(runner_environments) != (RUNNER_ENVIRONMENT_ID,):
        errors.append("Runner environment registry must contain exactly one defined slot")
    runner_environment = runner_environments.get(RUNNER_ENVIRONMENT_ID, {})
    if runner_environment.get("source_environment_ref") != SOURCE_ENVIRONMENT_ID or SOURCE_ENVIRONMENT_ID not in ecological_environments:
        errors.append("Runner environment must reference the existing local governance environment model")
    if runner_environment.get("environment_lock_ref") != ENVIRONMENT_LOCK_ID or ENVIRONMENT_LOCK_ID not in environment_locks:
        errors.append("Runner environment must reference the pending DBOS-EXP-0001 environment lock")
    if runner_environment.get("qualification_reference") != ENVIRONMENT_QUALIFICATION_ID:
        errors.append("Runner environment must reference the pending environment qualification review")
    if runner_environment.get("status") not in ENVIRONMENT_STATUSES:
        errors.append("Runner environment status is invalid")
    if runner_environment.get("status") != "defined":
        errors.append("v0.1 Runner environment must remain defined and unqualified")
    for field in ("os", "python_version", "configuration_digest", "locked_at"):
        if runner_environment.get(field) is not None:
            errors.append(f"defined Runner environment requires {field}=null until captured")
    if runner_environment.get("dependencies") != [] or runner_environment.get("evidence_refs") != []:
        errors.append("defined Runner environment cannot fabricate dependency or evidence material")
    if runner_environment.get("qualification_status") != "not_qualified":
        errors.append("Runner environment qualification_status must remain not_qualified")
    if runner_environment.get("runtime_status") != "not_a_runtime":
        errors.append("Runner environment cannot become a Runtime")
    if runner_environment.get("authority_effect") != "none":
        errors.append("Runner environment cannot create authority")
    reject_effect_keys(runner_environment, "Runner environment", errors)
    environment_meta = environment_doc.get("metadata", {})
    if environment_meta.get("environment_count") != 1 or environment_meta.get("environment_status_distribution", {}).get("defined") != 1:
        errors.append("Runner environment metadata must report one defined slot")
    require_zero(
        environment_meta,
        ("qualified_environment_count", "frozen_environment_count", "runtime_created_count", "execution_authority_count", "permission_grant_count"),
        "Runner environment",
        errors,
    )

    execution_doc = docs["runner_executions"]
    executions = index_records(
        execution_doc.get("runner_executions"), "execution_id", "runner_executions", errors
    )
    for execution_id, execution in executions.items():
        runner_id = execution.get("runner_id")
        runner = runners.get(runner_id)
        if runner is None:
            errors.append(f"{execution_id}: execution must reference an existing Runner")
        experiment_id = execution.get("experiment_id")
        if experiment_id not in experiments or experiments.get(experiment_id, {}).get("status") != "registered":
            errors.append(f"{execution_id}: Runner can execute only a registered experiment")
        scope = scopes.get(execution.get("scope_ref"))
        if scope is None or scope.get("runner_id") != runner_id or experiment_id not in scope.get("allowed_experiments", []):
            errors.append(f"{execution_id}: execution requires an approved matching Runner scope")
        elif scope.get("status") != "approved":
            errors.append(f"{execution_id}: execution scope must be approved")
        if execution.get("environment_ref") != RUNNER_ENVIRONMENT_ID:
            errors.append(f"{execution_id}: execution must bind the Runner environment")
        status = execution.get("status")
        if status not in EXECUTION_STATUSES:
            errors.append(f"{execution_id}: invalid execution status {status!r}")
        started_at = execution.get("started_at")
        ended_at = execution.get("ended_at")
        if status in {"pending", "authorized"} and (started_at is not None or ended_at is not None):
            errors.append(f"{execution_id}: pending or authorized execution requires null timestamps")
        if status == "running" and (not valid_timestamp(started_at) or ended_at is not None):
            errors.append(f"{execution_id}: running execution requires started_at and ended_at=null")
        if status in TERMINAL_EXECUTION_STATUSES and (not valid_timestamp(started_at) or not valid_timestamp(ended_at)):
            errors.append(f"{execution_id}: terminal execution requires timezone-aware start and end")
        output_refs = execution.get("output_refs")
        if not isinstance(output_refs, list):
            errors.append(f"{execution_id}: output_refs must be a list")
        if status in {"authorized", "running"} | TERMINAL_EXECUTION_STATUSES:
            if runner is None or runner.get("status") != "ready":
                errors.append(f"{execution_id}: executable state requires ready Runner")
            if runner_environment.get("status") not in {"qualified", "frozen"}:
                errors.append(f"{execution_id}: executable state requires qualified or frozen Runner environment")
        reject_effect_keys(execution, f"Runner execution {execution_id}", errors)

    if executions:
        errors.append("v0.1 Runner execution registry must remain empty; DBOS-EXP-0001 was not executed")
    execution_meta = execution_doc.get("metadata", {})
    if execution_meta.get("execution_count") != 0:
        errors.append("Runner execution metadata count must remain zero")
    require_zero(
        execution_meta,
        ("completed_execution_count", "event_created_count", "snapshot_created_count", "runtime_created_count", "agent_created_count", "capability_effect_count", "permission_grant_count", "c_e_v_level_change_count"),
        "Runner execution",
        errors,
    )

    evidence_doc = docs["runner_evidence"]
    runner_evidence = index_records(
        evidence_doc.get("runner_evidence"), "evidence_id", "runner_evidence", errors
    )
    for evidence_id, evidence_record in runner_evidence.items():
        if evidence_record.get("execution_id") not in executions:
            errors.append(f"{evidence_id}: Runner evidence must reference an existing execution")
        if not nonempty_string(evidence_record.get("artifact")):
            errors.append(f"{evidence_id}: artifact must be non-empty")
        if not DIGEST_RE.fullmatch(str(evidence_record.get("digest", ""))):
            errors.append(f"{evidence_id}: digest must be sha256")
        if not valid_timestamp(evidence_record.get("timestamp")):
            errors.append(f"{evidence_id}: timestamp must be timezone-aware")
        if evidence_record.get("authority_effect", "none") != "none":
            errors.append(f"{evidence_id}: Runner evidence cannot create authority")
        reject_effect_keys(evidence_record, f"Runner evidence {evidence_id}", errors)
    if runner_evidence:
        errors.append("v0.1 Runner evidence registry must remain empty because no execution occurred")
    evidence_meta = evidence_doc.get("metadata", {})
    if evidence_meta.get("runner_evidence_count") != 0:
        errors.append("Runner evidence metadata count must remain zero")
    require_zero(
        evidence_meta,
        ("verified_digest_count", "event_created_count", "snapshot_created_count", "trust_grant_count", "capability_effect_count", "permission_grant_count", "c_e_v_level_change_count"),
        "Runner evidence",
        errors,
    )

    executor_authorizations = docs["executor_authorizations"].get("executor_authorizations")
    if not isinstance(executor_authorizations, list) or len(executor_authorizations) != 1:
        errors.append("Runner layer must preserve one pending Executor authorization")
    else:
        authorization = executor_authorizations[0]
        if authorization.get("status") != "pending" or any(
            authorization.get(field) is not None for field in ("executor_id", "authorized_by", "scope_ref", "timestamp")
        ):
            errors.append("Runner layer cannot authorize an Executor")
    experiment_authorizations = docs["experiment_authorizations"].get("experiment_authorizations")
    if not isinstance(experiment_authorizations, list) or len(experiment_authorizations) != 1 or experiment_authorizations[0].get("status") != "pending":
        errors.append("Runner layer cannot authorize the experiment")

    if docs["events"].get("events") != []:
        errors.append("Runner layer cannot generate a real Event")
    if docs["contexts"].get("execution_contexts") != []:
        errors.append("Runner layer cannot generate an execution context")
    if docs["runtimes"].get("runtime_instances") != []:
        errors.append("Runner layer cannot create a Runtime")
    snapshots = docs["snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1:
        errors.append("Runner layer must preserve one pending snapshot slot")
    else:
        snapshot = snapshots[0]
        if snapshot.get("status") != "pending" or any(
            snapshot.get(field) is not None
            for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash", "captured_at")
        ):
            errors.append("Runner layer cannot generate or freeze a Snapshot")

    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != []:
        errors.append("Runner layer cannot create a capability")
    claims = docs["claims"].get("claims")
    if not isinstance(claims, list) or len(claims) != 78 or any(
        not isinstance(claim, dict) or claim.get("status") != "pending" or claim.get("maturity_level") != "C1"
        for claim in claims
    ):
        errors.append("Runner layer must preserve 78 pending C1 claims")
    capability_evidence = docs["capability_evidence"].get("evidence")
    if not isinstance(capability_evidence, list) or len(capability_evidence) != 78 or any(
        not isinstance(record, dict) or record.get("evidence_type") != "E1" or record.get("status") != "pending"
        for record in capability_evidence
    ):
        errors.append("Runner layer cannot alter 78 pending E1 evidence records")
    verification_records = docs["verification_records"].get("verification_records")
    if not isinstance(verification_records, list) or len(verification_records) != 78 or any(
        not isinstance(record, dict)
        or record.get("verification_level") != "V0"
        or record.get("decision") != "pending"
        or record.get("status") != "pending"
        for record in verification_records
    ):
        errors.append("Runner layer cannot alter 78 pending V0 verification records")
    entities = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    agent_count = sum(1 for entity in entities.values() if entity.get("entity_type") == "agent")
    if agent_count != 0 or docs["entities"].get("metadata", {}).get("classification_counts", {}).get("agent") != 0:
        errors.append("Runner layer cannot create or convert an Agent")

    required_tokens = {
        "runner_constitution": [
            "Runner != Agent",
            "Runner != Runtime",
            "Runner != Candidate Organism",
            "deterministic_execution:",
            "allowed_actions:",
            "forbidden_actions:",
            "lifecycle:",
        ],
        "executor_constitution": [
            "automated_runner_implementation:",
            "automated-runner-constitution.yaml",
            "Runner Registration != Executor Appointment",
        ],
        "readiness_constitution": [
            "runner_readiness_requirement:",
            "runner-environments.yaml",
            "current_status: \"pending\"",
        ],
        "context_constitution": [
            "runner_reference:",
            "runner-executions.yaml",
            "Runner Execution != Execution Context",
        ],
    }
    for text_name, tokens in required_tokens.items():
        for token in tokens:
            if token not in texts[text_name]:
                errors.append(f"{text_name} missing required boundary token: {token}")

    evolution_ids = [int(value) for value in EVOLUTION_ID_RE.findall(texts["evolution_ledger"])]
    if (
        not evolution_ids
        or len(evolution_ids) != len(set(evolution_ids))
        or sorted(evolution_ids) != list(range(1, max(evolution_ids) + 1))
        or max(evolution_ids) < 29
        or 29 not in evolution_ids
        or evolution_ids[-1] != max(evolution_ids)
    ):
        errors.append("evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0029, and append the latest ID last")
    if "automated_experiment_runner_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append("evolution ledger must contain the Automated Experiment Runner record")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "runner_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "experiment_id": EXPERIMENT_ID,
            "registered_step_count": len(STEP_IDS),
            "runner_count": len(runners),
            "runner_type_distribution": {runner_type: runner_type_counts[runner_type] for runner_type in sorted(RUNNER_TYPES)},
            "execution_mode_distribution": {mode: execution_mode_counts[mode] for mode in sorted(EXECUTION_MODES)},
            "runner_scope_count": len(scopes),
            "runner_environment_count": len(runner_environments),
            "runner_environment_status_distribution": dict(Counter(item.get("status") for item in runner_environments.values())),
            "runner_execution_count": len(executions),
            "runner_evidence_count": len(runner_evidence),
            "executor_identity_count": len(identities),
            "appointed_executor_count": len(executors),
            "capability_count": len(capabilities) if isinstance(capabilities, list) else None,
            "claim_count": len(claims) if isinstance(claims, list) else None,
            "capability_evidence_count": len(capability_evidence) if isinstance(capability_evidence, list) else None,
            "capability_verification_count": len(verification_records) if isinstance(verification_records, list) else None,
            "event_count": len(docs["events"].get("events", [])),
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "agent_count": agent_count,
            "permission_grant_count": 0,
            "remaining_gaps": [
                "no verified automated Executor Identity exists",
                "no automated Executor is appointed",
                "no Runner is registered",
                "no Runner scope exists",
                "Runner environment has null OS and Python versions, no dependencies or digest, and is not qualified",
                "snapshot, validator manifest, environment lock, and freeze are not frozen",
                "Executor, capture, and experiment authorizations remain pending",
                "experiment readiness remains pending",
                "no execution context, Runner execution, Event, or Runner evidence exists",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "runners": registry / "runners.yaml",
        "runner_scopes": registry / "runner-scopes.yaml",
        "runner_environments": registry / "runner-environments.yaml",
        "runner_executions": registry / "runner-executions.yaml",
        "runner_evidence": registry / "runner-evidence.yaml",
        "executor_identities": registry / "executor-identities.yaml",
        "executors": registry / "executors.yaml",
        "executor_authorizations": registry / "executor-authorizations.yaml",
        "experiment_authorizations": registry / "experiment-authorizations.yaml",
        "experiments": registry / "experiments.yaml",
        "procedures": registry / "experiment-procedures.yaml",
        "environments": registry / "environments.yaml",
        "environment_locks": registry / "environment-locks.yaml",
        "snapshots": registry / "experiment-snapshots.yaml",
        "events": registry / "events.yaml",
        "contexts": registry / "execution-contexts.yaml",
        "runtimes": registry / "runtime-instances.yaml",
        "capabilities": registry / "capabilities.yaml",
        "claims": registry / "capability-claims.yaml",
        "capability_evidence": registry / "capability-evidence.yaml",
        "verification_records": registry / "verification-records.yaml",
        "entities": registry / "entities.yaml",
    }
    docs = {name: load_json_yaml(path) for name, path in paths.items()}
    text_paths = {
        "runner_constitution": root / "constitution" / "automated-runner-constitution.yaml",
        "executor_constitution": root / "constitution" / "executor-constitution.yaml",
        "readiness_constitution": root / "constitution" / "experiment-readiness-constitution.yaml",
        "context_constitution": root / "constitution" / "execution-context-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in text_paths.items()}
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DBOS v0.1 Automated Experiment Runner")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    root = args.root.resolve()
    from execution_chain_compat import delegate_if_advanced
    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        docs, texts = load_inputs(root)
        result = validate(docs, texts, root)
    except (OSError, ValueError) as exc:
        result = {
            "status": "FAIL",
            "validator": "runner_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS runner_validator: "
            f"runners={summary['runner_count']}, scopes={summary['runner_scope_count']}, "
            f"environments={summary['runner_environment_count']}, "
            f"executions={summary['runner_execution_count']}, evidence={summary['runner_evidence_count']}"
        )
    else:
        print("FAIL runner_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
