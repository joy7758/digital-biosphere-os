#!/usr/bin/env python3
"""Validate Automated Environment Collector governance without creating one.

Agent-readable contract:
- Collector is distinct from Agent, Executor, Runner, Runtime, capability,
  permission, and governance authority.
- Collector, scope, run, and Collector-evidence registries remain empty because
  no governed identity has been enrolled and no collection occurred.
- Any future Collector must be automated, deterministic, explicitly scoped,
  and read_only with mandatory privacy exclusions.
- Collector evidence cannot automatically qualify or freeze an environment or
  promote C/E/V.
- Exit 0 is local structural PASS only; it enrolls or runs nothing.
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
ENVIRONMENT_ID = "dbio://runner-environment/dbos-exp-0001/local-governance-workspace/v0.1"
CAPTURE_ID = "DBOS-EXP-0001-ENV-EVIDENCE-CAPTURE-0001"
QUALIFICATION_ID = "DBOS-EXP-0001-RUNNER-ENV-QUAL-0001"
LOCK_ID = "DBOS-EXP-0001-ENV-LOCK-0001"

COLLECTOR_TYPES = {"automated"}
ACCESS_MODES = {"read_only"}
COLLECTOR_STATUSES = {"proposed", "identity_verified", "registered", "active", "suspended", "revoked", "retired"}
SCOPE_STATUSES = {"proposed", "defined", "approved", "suspended", "revoked", "superseded"}
RUN_STATUSES = {"pending", "running", "completed", "partial", "failed", "invalid", "revoked"}
TERMINAL_RUN_STATUSES = {"completed", "partial", "failed", "invalid", "revoked"}
EVIDENCE_STATUSES = {"captured", "verified", "partial", "failed", "invalid", "revoked"}
ALLOWED_FACTS = (
    "operating_system",
    "python_version",
    "dependency_information",
    "configuration_information",
)
MANDATORY_EXCLUSIONS = (
    "credential",
    "secret",
    "private_key",
    "personal_data",
    "external_storage_content",
)
MANDATORY_FORBIDDEN_OPERATIONS = {
    "write_filesystem",
    "modify_constitution",
    "modify_registry_history",
    "modify_member_repository",
    "modify_external_project",
    "access_external_storage_content",
    "read_credential_or_secret",
    "create_agent",
    "create_runtime",
    "execute_experiment",
    "generate_event",
    "generate_snapshot",
    "qualify_environment",
    "freeze_environment",
    "grant_capability",
    "grant_permission",
    "upgrade_c_e_v",
}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)
FORBIDDEN_EFFECT_KEYS = {
    "agent_id",
    "executor_id",
    "runner_id",
    "runtime_id",
    "event_id",
    "snapshot_id",
    "snapshot_hash",
    "capability_id",
    "capability_assignment",
    "permission",
    "permission_grant",
    "evidence_level",
    "verification_level",
    "maturity_level",
    "fitness_score",
}
SENSITIVE_KEYS = {"credential", "secret", "private_key", "password", "token", "cookie", "personal_data"}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML with the standard library only."""
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


def attributable(value: Any) -> bool:
    if nonempty_string(value):
        return True
    if isinstance(value, dict):
        return bool(value) and all(nonempty_string(key) for key in value)
    if isinstance(value, list):
        return bool(value) and all(attributable(item) for item in value)
    return False


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
            errors.append(f"{label}: Collector governance cannot contain authority or role-creation fields {present}")
        for key, child in value.items():
            reject_effect_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_effect_keys(child, f"{label}[{index}]", errors)


def reject_sensitive_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).strip().lower() in SENSITIVE_KEYS:
                errors.append(f"{label}: prohibited sensitive field {key!r}")
            reject_sensitive_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive_keys(child, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def list_value(record: dict[str, Any], field: str, label: str, errors: list[str]) -> list[Any]:
    value = record.get(field)
    if not isinstance(value, list):
        errors.append(f"{label}.{field} must be a list")
        return []
    return value


def validate(docs: dict[str, dict[str, Any]], texts: dict[str, str], root: Path) -> dict[str, Any]:
    """Validate Collector identity, read-only scope, runs, evidence, and zero effects."""
    errors: list[str] = []

    entities = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    environments = index_records(
        docs["environment_identities"].get("environment_identities"), "environment_id", "environment_identities", errors
    )
    collectors = index_records(
        docs["collectors"].get("environment_collectors"), "collector_id", "environment_collectors", errors
    )
    scopes = index_records(docs["scopes"].get("collector_scopes"), "scope_id", "collector_scopes", errors)
    runs = index_records(docs["runs"].get("collector_runs"), "run_id", "collector_runs", errors)
    collector_evidence = index_records(
        docs["collector_evidence"].get("collector_evidence"), "evidence_id", "collector_evidence", errors
    )
    captures = index_records(
        docs["captures"].get("environment_evidence_captures"), "capture_id", "environment_evidence_captures", errors
    )
    facts = index_records(docs["facts"].get("environment_facts"), "fact_id", "environment_facts", errors)
    digests = index_records(docs["digests"].get("environment_digests"), "digest_id", "environment_digests", errors)
    collection_evidence = index_records(
        docs["collection_evidence"].get("environment_collection_evidence"),
        "evidence_id",
        "environment_collection_evidence",
        errors,
    )
    qualification_evidence = index_records(
        docs["qualification_evidence"].get("environment_evidence"),
        "evidence_id",
        "qualification_environment_evidence",
        errors,
    )
    qualifications = index_records(
        docs["qualifications"].get("environment_qualifications"),
        "qualification_id",
        "environment_qualifications",
        errors,
    )
    locks = index_records(docs["environment_locks"].get("environment_locks"), "lock_id", "environment_locks", errors)

    collector_type_counts: Counter[str] = Counter()
    access_mode_counts: Counter[str] = Counter()
    for collector_id, collector in collectors.items():
        collector_type = collector.get("collector_type")
        if collector_type not in COLLECTOR_TYPES:
            errors.append(f"{collector_id}: collector_type must be automated")
        else:
            collector_type_counts[collector_type] += 1
        identity_ref = collector.get("identity_ref")
        identity = entities.get(identity_ref)
        if identity is None:
            errors.append(f"{collector_id}: Collector identity_ref must resolve to an existing governed entity")
        elif identity.get("entity_type") == "agent":
            errors.append(f"{collector_id}: Collector identity cannot be an Agent")
        if not attributable(collector.get("method")):
            errors.append(f"{collector_id}: deterministic collection method must be explicit")
        access_mode = collector.get("access_mode")
        if access_mode not in ACCESS_MODES:
            errors.append(f"{collector_id}: Collector access_mode must be read_only")
        else:
            access_mode_counts[access_mode] += 1
        status = collector.get("status")
        if status not in COLLECTOR_STATUSES:
            errors.append(f"{collector_id}: invalid Collector status {status!r}")
        if status in {"registered", "active"}:
            if not nonempty_string(collector.get("version")):
                errors.append(f"{collector_id}: registered or active Collector requires version")
            if not DIGEST_RE.fullmatch(str(collector.get("implementation_digest", ""))):
                errors.append(f"{collector_id}: registered or active Collector requires implementation_digest")
        scope_refs = list_value(collector, "scope_refs", collector_id, errors)
        for scope_ref in scope_refs:
            scope = scopes.get(scope_ref)
            if scope is None or scope.get("collector_id") != collector_id:
                errors.append(f"{collector_id}: unknown or mismatched scope_ref {scope_ref!r}")
        if status == "active" and not scope_refs:
            errors.append(f"{collector_id}: active Collector requires at least one approved scope")
        for field, expected in (
            ("agent_status", "not_an_agent"),
            ("executor_status", "not_an_executor"),
            ("runtime_status", "not_a_runtime"),
            ("capability_status", "not_assigned"),
            ("permission_status", "not_granted"),
            ("authority_effect", "none"),
        ):
            if collector.get(field, expected) != expected:
                errors.append(f"{collector_id}: {field} must remain {expected}")
        reject_sensitive_keys(collector, f"Collector {collector_id}", errors)
        reject_effect_keys(collector, f"Collector {collector_id}", errors)
    if collectors:
        errors.append("v0.1 Collector registry must remain empty; no identity was enrolled")

    if tuple(docs["scopes"].get("allowed_fact_catalog", [])) != ALLOWED_FACTS:
        errors.append("Collector allowed_fact_catalog must preserve the four exact allowed facts")
    if tuple(docs["scopes"].get("mandatory_excluded_data", [])) != MANDATORY_EXCLUSIONS:
        errors.append("Collector mandatory_excluded_data must preserve all five exclusions")
    if set(docs["scopes"].get("mandatory_forbidden_operations", [])) != MANDATORY_FORBIDDEN_OPERATIONS:
        errors.append("Collector scopes must preserve every mandatory forbidden operation")
    for scope_id, scope in scopes.items():
        collector_id = scope.get("collector_id")
        if collector_id not in collectors:
            errors.append(f"{scope_id}: scope must reference an existing Collector")
        allowed_facts = list_value(scope, "allowed_facts", scope_id, errors)
        if not allowed_facts or len(allowed_facts) != len(set(allowed_facts)) or any(item not in ALLOWED_FACTS for item in allowed_facts):
            errors.append(f"{scope_id}: allowed_facts must be a unique non-empty catalog subset")
        excluded_data = list_value(scope, "excluded_data", scope_id, errors)
        missing_exclusions = sorted(set(MANDATORY_EXCLUSIONS) - set(excluded_data))
        if missing_exclusions:
            errors.append(f"{scope_id}: missing mandatory excluded data {missing_exclusions}")
        environment_refs = list_value(scope, "environment_refs", scope_id, errors)
        if not environment_refs or any(ref not in environments for ref in environment_refs):
            errors.append(f"{scope_id}: environment_refs must resolve to explicit environment identities")
        forbidden_operations = list_value(scope, "forbidden_operations", scope_id, errors)
        missing_forbidden = sorted(MANDATORY_FORBIDDEN_OPERATIONS - set(forbidden_operations))
        if missing_forbidden:
            errors.append(f"{scope_id}: missing mandatory forbidden operations {missing_forbidden}")
        status = scope.get("status", "proposed")
        if status not in SCOPE_STATUSES:
            errors.append(f"{scope_id}: invalid scope status {status!r}")
        if status == "approved" and not attributable(scope.get("allowed_sources")):
            errors.append(f"{scope_id}: approved scope requires explicit allowed_sources")
        if scope.get("authority_effect", "none") != "none":
            errors.append(f"{scope_id}: Collector scope cannot create authority")
        reject_sensitive_keys(scope, f"Collector scope {scope_id}", errors)
        reject_effect_keys(scope, f"Collector scope {scope_id}", errors)
    if scopes:
        errors.append("v0.1 Collector scope registry must remain empty while no Collector exists")

    output_catalog = set(facts) | set(digests)
    for run_id, run in runs.items():
        collector = collectors.get(run.get("collector_id"))
        if collector is None:
            errors.append(f"{run_id}: run must reference an existing Collector")
        elif collector.get("access_mode") != "read_only":
            errors.append(f"{run_id}: run Collector must be read_only")
        environment_id = run.get("environment_id")
        if environment_id not in environments:
            errors.append(f"{run_id}: run must reference an existing environment identity")
        scope = scopes.get(run.get("scope_ref"))
        if scope is None or scope.get("collector_id") != run.get("collector_id"):
            errors.append(f"{run_id}: run requires a matching Collector scope")
        elif scope.get("status") != "approved" or environment_id not in scope.get("environment_refs", []):
            errors.append(f"{run_id}: run requires an approved scope for the same environment")
        capture = captures.get(run.get("capture_ref"))
        if capture is None or capture.get("environment_id") != environment_id:
            errors.append(f"{run_id}: run requires the matching environment evidence capture")
        status = run.get("status")
        if status not in RUN_STATUSES:
            errors.append(f"{run_id}: invalid run status {status!r}")
        started_at = run.get("started_at")
        ended_at = run.get("ended_at")
        if status == "pending" and (started_at is not None or ended_at is not None):
            errors.append(f"{run_id}: pending run requires null timestamps")
        elif status == "running" and (not valid_timestamp(started_at) or ended_at is not None):
            errors.append(f"{run_id}: running run requires started_at and ended_at=null")
        elif status in TERMINAL_RUN_STATUSES and (not valid_timestamp(started_at) or not valid_timestamp(ended_at)):
            errors.append(f"{run_id}: terminal run requires timezone-aware start and end")
        output_refs = list_value(run, "output_refs", run_id, errors)
        unknown_outputs = sorted(set(output_refs) - output_catalog)
        if unknown_outputs:
            errors.append(f"{run_id}: unknown output_refs {unknown_outputs}")
        if status == "pending" and output_refs:
            errors.append(f"{run_id}: pending run cannot contain outputs")
        if status in {"running"} | TERMINAL_RUN_STATUSES and not DIGEST_RE.fullmatch(str(run.get("method_digest", ""))):
            errors.append(f"{run_id}: running or terminal run requires method_digest")
        if run.get("side_effects", []) != []:
            errors.append(f"{run_id}: read-only Collector run requires side_effects=[]")
        if run.get("authority_effect", "none") != "none":
            errors.append(f"{run_id}: Collector run cannot create authority")
        reject_sensitive_keys(run, f"Collector run {run_id}", errors)
        reject_effect_keys(run, f"Collector run {run_id}", errors)
    if runs:
        errors.append("v0.1 Collector run registry must remain empty; collection was not executed")

    for evidence_id, evidence in collector_evidence.items():
        run = runs.get(evidence.get("run_id"))
        if run is None:
            errors.append(f"{evidence_id}: Collector evidence must reference an existing run")
        if evidence.get("collector_id") != (run or {}).get("collector_id"):
            errors.append(f"{evidence_id}: evidence collector_id must match its run")
        if evidence.get("environment_id") != (run or {}).get("environment_id"):
            errors.append(f"{evidence_id}: evidence environment_id must match its run")
        fact_refs = list_value(evidence, "fact_refs", evidence_id, errors)
        digest_refs = list_value(evidence, "digest_refs", evidence_id, errors)
        if not fact_refs or any(ref not in facts for ref in fact_refs):
            errors.append(f"{evidence_id}: Collector evidence requires existing fact_refs")
        if not digest_refs or any(ref not in digests for ref in digest_refs):
            errors.append(f"{evidence_id}: Collector evidence requires existing digest_refs")
        run_outputs = set((run or {}).get("output_refs", []))
        if any(ref not in run_outputs for ref in fact_refs + digest_refs):
            errors.append(f"{evidence_id}: Collector evidence refs must be retained run outputs")
        if not attributable(evidence.get("method")):
            errors.append(f"{evidence_id}: evidence method must be attributable")
        if not valid_timestamp(evidence.get("timestamp")):
            errors.append(f"{evidence_id}: evidence timestamp must be timezone-aware")
        if not attributable(evidence.get("source_refs")):
            errors.append(f"{evidence_id}: evidence source_refs must be attributable")
        status = evidence.get("status", "captured")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{evidence_id}: invalid Collector evidence status {status!r}")
        if status == "verified":
            if run is None or run.get("status") != "completed":
                errors.append(f"{evidence_id}: verified evidence requires a completed run")
            if not nonempty_string(evidence.get("verification_ref")):
                errors.append(f"{evidence_id}: verified evidence requires verification_ref")
        if evidence.get("authority_effect", "none") != "none":
            errors.append(f"{evidence_id}: Collector evidence cannot create authority")
        reject_sensitive_keys(evidence, f"Collector evidence {evidence_id}", errors)
        reject_effect_keys(evidence, f"Collector evidence {evidence_id}", errors)
    if collector_evidence:
        errors.append("v0.1 Collector evidence registry must remain empty; no run occurred")

    if tuple(captures) != (CAPTURE_ID,):
        errors.append("Collector layer must preserve exactly one pending environment capture")
    capture = captures.get(CAPTURE_ID, {})
    if capture.get("environment_id") != ENVIRONMENT_ID or ENVIRONMENT_ID not in environments:
        errors.append("pending environment capture must retain the existing environment identity")
    if capture.get("collector") is not None or capture.get("collector_scope_ref") is not None or capture.get("collector_run_ref") is not None:
        errors.append("pending capture cannot appoint a Collector, scope, or run")
    if capture.get("collector_evidence_refs") != []:
        errors.append("pending capture cannot claim Collector evidence")
    if capture.get("status") != "pending" or capture.get("timestamp") is not None:
        errors.append("Collector modeling cannot execute environment collection")
    for field in ("fact_refs", "digest_refs", "collection_evidence_refs", "qualification_evidence_refs"):
        if capture.get(field) != []:
            errors.append(f"pending capture requires {field}=[]")

    if facts or digests or collection_evidence or qualification_evidence:
        errors.append("Collector modeling cannot fabricate environment facts, digests, collection evidence, or qualification evidence")
    if tuple(qualifications) != (QUALIFICATION_ID,):
        errors.append("Collector layer must preserve one environment qualification review")
    qualification = qualifications.get(QUALIFICATION_ID, {})
    criteria = qualification.get("criteria")
    if (
        qualification.get("result") != "pending"
        or qualification.get("verified_by") is not None
        or qualification.get("timestamp") is not None
        or qualification.get("evidence_refs") != []
        or not isinstance(criteria, list)
        or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("evidence_refs") != [] for item in criteria)
    ):
        errors.append("Collector governance cannot certify an environment or advance qualification criteria")
    if tuple(locks) != (LOCK_ID,):
        errors.append("Collector layer must preserve the existing environment lock")
    lock = locks.get(LOCK_ID, {})
    if lock.get("status") != "pending" or lock.get("evidence_reference") is not None or lock.get("evidence_refs") != []:
        errors.append("Collector governance cannot freeze the environment or create lock evidence")

    collector_meta = docs["collectors"].get("metadata", {})
    if collector_meta.get("collector_count") != 0:
        errors.append("Collector metadata count must remain zero")
    require_zero(collector_meta, ("active_collector_count", "agent_created_count", "executor_created_count", "runtime_created_count", "capability_effect_count", "permission_grant_count"), "Collector", errors)
    scope_meta = docs["scopes"].get("metadata", {})
    if scope_meta.get("scope_count") != 0:
        errors.append("Collector scope metadata count must remain zero")
    require_zero(scope_meta, ("approved_scope_count", "execution_authority_count", "capability_effect_count", "permission_grant_count"), "Collector scope", errors)
    run_meta = docs["runs"].get("metadata", {})
    if run_meta.get("collector_run_count") != 0:
        errors.append("Collector run metadata count must remain zero")
    require_zero(run_meta, ("completed_run_count", "write_side_effect_count", "experiment_execution_count", "event_created_count", "snapshot_created_count", "permission_grant_count"), "Collector run", errors)
    evidence_meta = docs["collector_evidence"].get("metadata", {})
    if evidence_meta.get("collector_evidence_count") != 0:
        errors.append("Collector evidence metadata count must remain zero")
    require_zero(evidence_meta, ("verified_collector_evidence_count", "qualification_evidence_created_count", "environment_qualification_count", "capability_effect_count", "permission_grant_count"), "Collector evidence", errors)

    if docs["runners"].get("runners") != []:
        errors.append("Collector layer cannot create a Runner")
    if docs["executors"].get("executors") != []:
        errors.append("Collector layer cannot appoint an Executor")
    if docs["runner_executions"].get("runner_executions") != []:
        errors.append("Collector layer cannot execute DBOS-EXP-0001")
    if docs["events"].get("events") != []:
        errors.append("Collector layer cannot generate an Event")
    if docs["execution_contexts"].get("execution_contexts") != []:
        errors.append("Collector layer cannot create an execution context")
    if docs["runtimes"].get("runtime_instances") != []:
        errors.append("Collector layer cannot create a Runtime")
    snapshots = docs["snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1 or snapshots[0].get("status") != "pending":
        errors.append("Collector layer must preserve one pending Snapshot slot")
    elif any(snapshots[0].get(field) is not None for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash", "captured_at")):
        errors.append("Collector layer cannot generate a Snapshot")
    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != []:
        errors.append("Collector layer cannot create a capability")
    claims = docs["claims"].get("claims")
    if not isinstance(claims, list) or len(claims) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("maturity_level") != "C1" for item in claims):
        errors.append("Collector layer must preserve 78 pending C1 claims")
    capability_evidence = docs["capability_evidence"].get("evidence")
    if not isinstance(capability_evidence, list) or len(capability_evidence) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("evidence_type") != "E1" for item in capability_evidence):
        errors.append("Collector layer must preserve 78 pending E1 capability evidence records")
    verification_records = docs["verification_records"].get("verification_records")
    if not isinstance(verification_records, list) or len(verification_records) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("decision") != "pending" or item.get("verification_level") != "V0" for item in verification_records):
        errors.append("Collector layer must preserve 78 pending V0 verification records")
    agent_count = sum(1 for entity in entities.values() if entity.get("entity_type") == "agent")
    if agent_count != 0:
        errors.append("Collector layer cannot create or convert an Agent")

    expected_validators = sorted(str(path.relative_to(root)) for path in (root / "validation").glob("*_validator.py"))
    manifests = docs["validator_manifests"].get("validator_manifests")
    if not isinstance(manifests, list) or len(manifests) != 1:
        errors.append("validator manifest must preserve one pending record")
    else:
        manifest = manifests[0]
        if manifest.get("validators") != expected_validators:
            errors.append("validator manifest must list the exact sorted validator suite")
        if manifest.get("status") != "pending" or manifest.get("digest") is not None or manifest.get("locked_digest") is not None:
            errors.append("validator manifest must remain pending and unfrozen")
    if docs["validator_manifests"].get("metadata", {}).get("declared_validator_count") != len(expected_validators):
        errors.append("validator manifest count must match the live validator suite")
    inputs = docs["experiment_inputs"].get("experiment_inputs")
    validator_inputs = [item for item in inputs if isinstance(item, dict) and item.get("input_type") == "validator_list"] if isinstance(inputs, list) else []
    if len(validator_inputs) != 1 or validator_inputs[0].get("value") != expected_validators or validator_inputs[0].get("status") != "pending":
        errors.append("experiment validator-list input must match the live suite and remain pending")

    required_tokens = {
        "collector_constitution": [
            "collector_definition:",
            "read_only_principle:",
            "collection_boundary:",
            "evidence_generation:",
            "privacy_boundary:",
            "revocation:",
            "Collector != Agent",
            "Collector != Executor",
            "Collector != Runtime",
        ],
        "capture_constitution": [
            "collector_dependency:",
            "environment-collectors.yaml",
            "automatic_collector_enrollment: false",
        ],
        "qualification_constitution": [
            "collector_evidence_requirement:",
            "collector-evidence.yaml",
            "automatic_qualification: false",
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
        or max(evolution_ids) < 32
        or 32 not in evolution_ids
        or evolution_ids[-1] != max(evolution_ids)
    ):
        errors.append("evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0032, and append the latest ID last")
    if "automated_environment_evidence_collector_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append("evolution ledger must contain the Automated Environment Evidence Collector record")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "environment_collector_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "collector_count": len(collectors),
            "collector_type_distribution": {item: collector_type_counts[item] for item in sorted(COLLECTOR_TYPES)},
            "access_mode_distribution": {item: access_mode_counts[item] for item in sorted(ACCESS_MODES)},
            "collector_scope_count": len(scopes),
            "collector_run_count": len(runs),
            "collector_evidence_count": len(collector_evidence),
            "environment_count": len(environments),
            "environment_fact_count": len(facts),
            "environment_digest_count": len(digests),
            "environment_collection_evidence_count": len(collection_evidence),
            "qualification_evidence_count": len(qualification_evidence),
            "environment_verified_count": sum(1 for item in qualifications.values() if item.get("result") == "verified"),
            "experiment_execution_count": len(docs["runner_executions"].get("runner_executions", [])),
            "runner_count": len(docs["runners"].get("runners", [])),
            "executor_count": len(docs["executors"].get("executors", [])),
            "agent_count": agent_count,
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "event_count": len(docs["events"].get("events", [])),
            "snapshot_hash_count": 0,
            "capability_count": len(capabilities) if isinstance(capabilities, list) else None,
            "permission_grant_count": 0,
            "remaining_environment_qualification_gaps": [
                "no governed identity is enrolled as an Automated Environment Collector",
                "no explicit Collector scope exists or is approved",
                "no Collector run exists",
                "no Collector evidence exists",
                "the environment evidence capture remains pending with collector=null",
                "environment facts, digests, and collection evidence remain empty",
                "qualification evidence remains empty and all six criteria remain pending",
                "the environment lock remains pending and unfrozen",
                "no in-scope qualification verifier decision exists",
                "no Runner, Runner scope, or verified Executor exists",
                "collection, Executor, and experiment authorizations remain pending",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "entities": registry / "entities.yaml",
        "environment_identities": registry / "environment-identities.yaml",
        "collectors": registry / "environment-collectors.yaml",
        "scopes": registry / "collector-scopes.yaml",
        "runs": registry / "collector-runs.yaml",
        "collector_evidence": registry / "collector-evidence.yaml",
        "captures": registry / "environment-evidence-captures.yaml",
        "facts": registry / "environment-facts.yaml",
        "digests": registry / "environment-digests.yaml",
        "collection_evidence": registry / "environment-collection-evidence.yaml",
        "qualification_evidence": registry / "environment-evidence.yaml",
        "qualifications": registry / "environment-qualifications.yaml",
        "environment_locks": registry / "environment-locks.yaml",
        "runners": registry / "runners.yaml",
        "executors": registry / "executors.yaml",
        "runner_executions": registry / "runner-executions.yaml",
        "events": registry / "events.yaml",
        "execution_contexts": registry / "execution-contexts.yaml",
        "runtimes": registry / "runtime-instances.yaml",
        "snapshots": registry / "experiment-snapshots.yaml",
        "capabilities": registry / "capabilities.yaml",
        "claims": registry / "capability-claims.yaml",
        "capability_evidence": registry / "capability-evidence.yaml",
        "verification_records": registry / "verification-records.yaml",
        "validator_manifests": registry / "validator-manifests.yaml",
        "experiment_inputs": registry / "experiment-inputs.yaml",
    }
    docs = {name: load_json_yaml(path) for name, path in paths.items()}
    text_paths = {
        "collector_constitution": root / "constitution" / "environment-collector-constitution.yaml",
        "capture_constitution": root / "constitution" / "environment-evidence-capture-constitution.yaml",
        "qualification_constitution": root / "constitution" / "environment-qualification-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in text_paths.items()}
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DBOS v0.1 Automated Environment Collector governance")
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
            "validator": "environment_collector_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS environment_collector_validator: "
            f"collectors={summary['collector_count']}, scopes={summary['collector_scope_count']}, "
            f"runs={summary['collector_run_count']}, evidence={summary['collector_evidence_count']}"
        )
    else:
        print("FAIL environment_collector_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
