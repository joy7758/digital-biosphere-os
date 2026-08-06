#!/usr/bin/env python3
"""Validate Runner Environment Qualification without qualifying an environment.

Agent-readable contract:
- One identity record maps the existing Runner environment; it creates no new
  environment, Runner, Runtime, Agent, execution, Event, or Snapshot.
- One qualification review remains pending, with all criteria pending.
- Environment evidence is empty and the shared Freeze Layer lock remains
  pending with no fabricated OS, Python, dependency, configuration, or time.
- result=verified requires complete evidence, digests, a frozen lock, and an
  attributable active verifier whose declared scope covers qualification.
- Exit 0 means local structural PASS only; it is not qualification or authority.
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
QUALIFICATION_ID = "DBOS-EXP-0001-RUNNER-ENV-QUAL-0001"
QUALIFICATION_REGISTRY_PATH = "registry/environment-qualifications.yaml"

ENVIRONMENT_TYPES = {"runner_environment"}
IDENTITY_STATUSES = {"defined", "qualified", "suspended", "revoked", "retired"}
EVIDENCE_TYPES = {
    "identity",
    "os_inventory",
    "python_inventory",
    "dependency_lock",
    "configuration",
    "lock_material",
}
EVIDENCE_STATUSES = {"pending", "captured", "verified", "invalid", "revoked"}
CRITERIA = (
    "identity_attributed",
    "os_captured",
    "python_captured",
    "dependencies_digested",
    "configuration_digested",
    "environment_lock_complete",
)
CRITERION_STATUSES = {"pending", "passed", "failed", "inconclusive"}
QUALIFICATION_RESULTS = {"pending", "verified", "failed", "inconclusive", "revoked"}
LOCK_STATUSES = {"pending", "frozen", "thawed", "invalid", "revoked"}
QUALIFIED_ENVIRONMENT_STATUSES = {"qualified", "frozen"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)
FORBIDDEN_AUTHORITY_KEYS = {
    "agent_id",
    "runtime_id",
    "event_id",
    "snapshot_hash",
    "capability_id",
    "capability_assignment",
    "permission",
    "permission_grant",
    "permission_status",
    "evidence_level",
    "verification_level",
    "maturity_level",
    "fitness_score",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load JSON-compatible YAML with the Python standard library only."""
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


def attributable_source(value: Any) -> bool:
    if nonempty_string(value):
        return True
    if isinstance(value, dict):
        return bool(value) and all(nonempty_string(key) for key in value)
    return False


def reject_authority_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(value))
        if present:
            errors.append(f"{label}: qualification governance cannot contain authority or promotion fields {present}")
        for key, child in value.items():
            reject_authority_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_authority_keys(child, f"{label}[{index}]", errors)


def require_zero(metadata: Any, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in fields:
        if metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def verifier_covers_qualification(verifier: dict[str, Any]) -> bool:
    scope = verifier.get("scope")
    if not isinstance(scope, dict):
        return False
    registry_authority = scope.get("registry_authority")
    return isinstance(registry_authority, list) and QUALIFICATION_REGISTRY_PATH in registry_authority


def validate(docs: dict[str, dict[str, Any]], texts: dict[str, str], root: Path) -> dict[str, Any]:
    """Validate identity, evidence, qualification, lock, and non-authority invariants."""
    errors: list[str] = []

    ecological_environments = index_records(
        docs["ecological_environments"].get("environments"), "environment_id", "ecological_environments", errors
    )
    runner_environments = index_records(
        docs["runner_environments"].get("runner_environments"), "environment_id", "runner_environments", errors
    )
    identities = index_records(
        docs["environment_identities"].get("environment_identities"),
        "environment_id",
        "environment_identities",
        errors,
    )
    evidence_records = index_records(
        docs["environment_evidence"].get("environment_evidence"),
        "evidence_id",
        "environment_evidence",
        errors,
    )
    qualifications = index_records(
        docs["environment_qualifications"].get("environment_qualifications"),
        "qualification_id",
        "environment_qualifications",
        errors,
    )
    locks = index_records(docs["environment_locks"].get("environment_locks"), "lock_id", "environment_locks", errors)
    verifiers = index_records(docs["verifiers"].get("verifiers"), "verifier_id", "verifiers", errors)

    if tuple(runner_environments) != (RUNNER_ENVIRONMENT_ID,):
        errors.append("qualification layer requires exactly the existing Runner environment slot")
    runner_environment = runner_environments.get(RUNNER_ENVIRONMENT_ID, {})
    if runner_environment.get("source_environment_ref") != SOURCE_ENVIRONMENT_ID:
        errors.append("Runner environment must retain its ecological environment source")
    if SOURCE_ENVIRONMENT_ID not in ecological_environments:
        errors.append("Runner environment source must resolve to the existing ecological environment")
    if runner_environment.get("environment_lock_ref") != ENVIRONMENT_LOCK_ID:
        errors.append("Runner environment must retain the existing Freeze Layer lock reference")
    if runner_environment.get("qualification_reference") != QUALIFICATION_ID:
        errors.append("Runner environment must reference the pending qualification record")
    if runner_environment.get("status") != "defined" or runner_environment.get("qualification_status") != "not_qualified":
        errors.append("v0.1 Runner environment must remain defined and not_qualified")
    for field in ("os", "python_version", "configuration_digest", "locked_at"):
        if runner_environment.get(field) is not None:
            errors.append(f"unqualified Runner environment requires {field}=null")
    if runner_environment.get("dependencies") != [] or runner_environment.get("evidence_refs") != []:
        errors.append("unqualified Runner environment cannot fabricate dependency or evidence material")
    if runner_environment.get("runtime_status") != "not_a_runtime":
        errors.append("Runner environment cannot become a Runtime")
    if runner_environment.get("authority_effect") != "none":
        errors.append("Runner environment cannot create authority")
    reject_authority_keys(runner_environment, "Runner environment", errors)

    if tuple(identities) != (RUNNER_ENVIRONMENT_ID,):
        errors.append("environment identity registry must contain exactly one mapping for the existing Runner environment")
    identity = identities.get(RUNNER_ENVIRONMENT_ID, {})
    if identity.get("environment_type") not in ENVIRONMENT_TYPES:
        errors.append("Runner environment identity has invalid environment_type")
    if identity.get("status") not in IDENTITY_STATUSES:
        errors.append("Runner environment identity has invalid status")
    source = identity.get("source")
    if not isinstance(source, dict):
        errors.append("Runner environment identity source must be a mapping")
        source = {}
    if source.get("runner_environment_ref") != RUNNER_ENVIRONMENT_ID:
        errors.append("environment identity must resolve to the existing Runner environment")
    if source.get("source_environment_ref") != SOURCE_ENVIRONMENT_ID:
        errors.append("environment identity must preserve ecological-environment lineage")
    if source.get("environment_lock_ref") != ENVIRONMENT_LOCK_ID:
        errors.append("environment identity must preserve Freeze Layer lock lineage")
    if identity.get("status") == "qualified" and identity.get("owner") is None:
        errors.append("qualified environment identity requires attributable owner evidence")
    if identity.get("status") != "defined" or identity.get("qualification_status") != "pending":
        errors.append("v0.1 environment identity must remain defined with pending qualification")
    if identity.get("runtime_status") != "not_a_runtime" or identity.get("agent_status") != "not_an_agent":
        errors.append("environment identity cannot create a Runtime or Agent")
    if identity.get("authority_effect") != "none":
        errors.append("environment identity cannot create authority")
    reject_authority_keys(identity, "Environment identity", errors)

    evidence_type_counts: Counter[str] = Counter()
    for evidence_id, evidence in evidence_records.items():
        environment_id = evidence.get("environment_id")
        if environment_id not in identities:
            errors.append(f"{evidence_id}: evidence must reference an environment identity")
        evidence_type = evidence.get("evidence_type")
        if evidence_type not in EVIDENCE_TYPES:
            errors.append(f"{evidence_id}: invalid evidence_type {evidence_type!r}")
        else:
            evidence_type_counts[evidence_type] += 1
        if not attributable_source(evidence.get("source")):
            errors.append(f"{evidence_id}: evidence source must be attributable")
        if not DIGEST_RE.fullmatch(str(evidence.get("digest", ""))):
            errors.append(f"{evidence_id}: evidence digest must be non-empty sha256")
        if not valid_timestamp(evidence.get("timestamp")):
            errors.append(f"{evidence_id}: evidence timestamp must be timezone-aware")
        status = evidence.get("status", "pending")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{evidence_id}: invalid evidence status {status!r}")
        if status == "verified" and not attributable_source(evidence.get("verification")):
            errors.append(f"{evidence_id}: verified evidence requires attributable verification")
        if evidence.get("authority_effect", "none") != "none":
            errors.append(f"{evidence_id}: environment evidence cannot create authority")
        reject_authority_keys(evidence, f"Environment evidence {evidence_id}", errors)
    if evidence_records:
        errors.append("v0.1 environment evidence registry must remain empty until real material is captured")

    if tuple(qualifications) != (QUALIFICATION_ID,):
        errors.append("qualification registry must contain exactly one pending review")
    qualification = qualifications.get(QUALIFICATION_ID, {})
    if qualification.get("environment_id") != RUNNER_ENVIRONMENT_ID or RUNNER_ENVIRONMENT_ID not in identities:
        errors.append("qualification must reference the existing Runner environment identity")
    if qualification.get("lock_ref") != ENVIRONMENT_LOCK_ID or ENVIRONMENT_LOCK_ID not in locks:
        errors.append("qualification must reference the shared Freeze Layer environment lock")
    criteria = qualification.get("criteria")
    criterion_statuses: dict[str, str] = {}
    criterion_evidence_refs: list[str] = []
    if not isinstance(criteria, list):
        errors.append("qualification criteria must be a list")
        criteria = []
    for index, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            errors.append(f"qualification criteria[{index}] must be a mapping")
            continue
        criterion_id = criterion.get("criterion_id")
        if not nonempty_string(criterion_id) or criterion_id in criterion_statuses:
            errors.append(f"qualification criteria[{index}] requires a unique criterion_id")
            continue
        status = criterion.get("status")
        if status not in CRITERION_STATUSES:
            errors.append(f"{criterion_id}: invalid criterion status {status!r}")
        criterion_statuses[criterion_id] = status
        refs = criterion.get("evidence_refs")
        if not isinstance(refs, list):
            errors.append(f"{criterion_id}: evidence_refs must be a list")
            refs = []
        for evidence_ref in refs:
            if evidence_ref not in evidence_records:
                errors.append(f"{criterion_id}: unknown evidence_ref {evidence_ref!r}")
            elif evidence_records[evidence_ref].get("environment_id") != RUNNER_ENVIRONMENT_ID:
                errors.append(f"{criterion_id}: evidence must belong to the qualified environment")
        criterion_evidence_refs.extend(refs)
    if tuple(criterion_statuses) != CRITERIA:
        errors.append("qualification must preserve every required criterion exactly once and in order")

    qualification_evidence_refs = qualification.get("evidence_refs")
    if not isinstance(qualification_evidence_refs, list):
        errors.append("qualification evidence_refs must be a list")
        qualification_evidence_refs = []
    for evidence_ref in qualification_evidence_refs:
        if evidence_ref not in evidence_records:
            errors.append(f"qualification has unknown evidence_ref {evidence_ref!r}")
    if set(criterion_evidence_refs) - set(qualification_evidence_refs):
        errors.append("criterion evidence_refs must be retained in qualification evidence_refs")

    result = qualification.get("result")
    if result not in QUALIFICATION_RESULTS:
        errors.append(f"qualification has invalid result {result!r}")
    if result == "pending":
        if qualification.get("verified_by") is not None or qualification.get("timestamp") is not None:
            errors.append("pending qualification requires verified_by=null and timestamp=null")
        if any(status != "pending" for status in criterion_statuses.values()):
            errors.append("v0.1 pending qualification must not simulate criterion decisions")
        if qualification_evidence_refs:
            errors.append("v0.1 pending qualification cannot claim evidence before material exists")
    elif result == "verified":
        verifier = verifiers.get(qualification.get("verified_by"))
        if verifier is None:
            errors.append("verified qualification requires an existing verifier")
        elif verifier.get("status") != "active" or not verifier_covers_qualification(verifier):
            errors.append("verified qualification requires an active verifier with explicit environment-qualification scope")
        if not valid_timestamp(qualification.get("timestamp")):
            errors.append("verified qualification requires a timezone-aware timestamp")
        if set(criterion_statuses) != set(CRITERIA) or any(
            criterion_statuses.get(criterion_id) != "passed" for criterion_id in CRITERIA
        ):
            errors.append("verified qualification requires every criterion passed")
        if not qualification_evidence_refs or any(
            evidence_records.get(ref, {}).get("status") != "verified" for ref in qualification_evidence_refs
        ):
            errors.append("verified qualification requires retained verified evidence")
        if identity.get("owner") is None:
            errors.append("verified qualification requires attributable environment ownership")
        if runner_environment.get("status") not in QUALIFIED_ENVIRONMENT_STATUSES:
            errors.append("verified qualification requires qualified or frozen Runner environment status")
    if qualification.get("authority_effect") != "none":
        errors.append("environment qualification cannot create authority")
    reject_authority_keys(qualification, "Environment qualification", errors)

    if tuple(locks) != (ENVIRONMENT_LOCK_ID,):
        errors.append("qualification layer must reuse exactly the existing Freeze Layer lock")
    lock = locks.get(ENVIRONMENT_LOCK_ID, {})
    if lock.get("environment_id") != SOURCE_ENVIRONMENT_ID:
        errors.append("shared environment lock must retain its ecological environment identity")
    if lock.get("runner_environment_ref") != RUNNER_ENVIRONMENT_ID:
        errors.append("shared environment lock must bridge to the Runner environment identity")
    if lock.get("qualification_reference") != QUALIFICATION_ID:
        errors.append("shared environment lock must reference the qualification review")
    if lock.get("experiment_id") != EXPERIMENT_ID:
        errors.append("shared environment lock must remain scoped to DBOS-EXP-0001")
    if lock.get("status") not in LOCK_STATUSES:
        errors.append("shared environment lock has invalid status")
    for left, right in (("os", "os_version"), ("python", "runtime_version"), ("dependencies_digest", "dependency_hash")):
        if lock.get(left) != lock.get(right):
            errors.append(f"shared environment lock alias mismatch: {left} != {right}")
    if lock.get("status") == "frozen":
        if not nonempty_string(lock.get("os")) or not nonempty_string(lock.get("python")):
            errors.append("frozen environment lock requires exact OS and Python versions")
        for field in ("dependencies_digest", "configuration_digest"):
            if not DIGEST_RE.fullmatch(str(lock.get(field, ""))):
                errors.append(f"frozen environment lock requires valid {field}")
        if not valid_timestamp(lock.get("locked_at")):
            errors.append("frozen environment lock requires timezone-aware locked_at")
        if not isinstance(lock.get("evidence_refs"), list) or not lock.get("evidence_refs"):
            errors.append("frozen environment lock requires retained evidence_refs")
    if result == "verified" and lock.get("status") != "frozen":
        errors.append("qualification cannot be verified before the shared environment lock is frozen")
    if lock.get("status") != "pending" or any(
        lock.get(field) is not None
        for field in (
            "os_version",
            "runtime_version",
            "dependency_hash",
            "os",
            "python",
            "dependencies_digest",
            "configuration_digest",
            "locked_at",
        )
    ):
        errors.append("v0.1 shared environment lock must remain pending with no fabricated material")
    if lock.get("evidence_refs") != []:
        errors.append("v0.1 shared environment lock cannot claim evidence")
    if lock.get("authority_effect") != "none":
        errors.append("environment lock cannot create authority")
    reject_authority_keys(lock, "Environment lock", errors)

    identity_meta = docs["environment_identities"].get("metadata", {})
    if identity_meta.get("environment_identity_count") != 1:
        errors.append("environment identity metadata must report one mapping")
    require_zero(identity_meta, ("qualified_environment_count", "runtime_created_count", "agent_created_count", "permission_grant_count"), "Environment identity", errors)
    evidence_meta = docs["environment_evidence"].get("metadata", {})
    if evidence_meta.get("environment_evidence_count") != 0:
        errors.append("environment evidence metadata must remain zero")
    require_zero(evidence_meta, ("nonempty_digest_count", "verified_evidence_count", "event_created_count", "snapshot_created_count", "permission_grant_count"), "Environment evidence", errors)
    qualification_meta = docs["environment_qualifications"].get("metadata", {})
    if qualification_meta.get("qualification_count") != 1 or qualification_meta.get("result_distribution", {}).get("pending") != 1:
        errors.append("qualification metadata must report one pending review")
    require_zero(qualification_meta, ("qualified_environment_count", "automatic_pass_count", "execution_authority_count", "capability_effect_count", "permission_grant_count"), "Environment qualification", errors)

    if docs["runners"].get("runners") != []:
        errors.append("environment qualification layer cannot create a Runner")
    if docs["runner_executions"].get("runner_executions") != []:
        errors.append("environment qualification layer cannot execute an experiment")
    if docs["events"].get("events") != []:
        errors.append("environment qualification layer cannot generate an Event")
    if docs["execution_contexts"].get("execution_contexts") != []:
        errors.append("environment qualification layer cannot generate an execution context")
    if docs["runtimes"].get("runtime_instances") != []:
        errors.append("environment qualification layer cannot create a Runtime")
    snapshots = docs["snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1 or snapshots[0].get("status") != "pending":
        errors.append("environment qualification layer must preserve one pending snapshot slot")
    elif any(
        snapshots[0].get(field) is not None
        for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash", "captured_at")
    ):
        errors.append("environment qualification layer cannot generate Snapshot material")
    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != []:
        errors.append("environment qualification layer cannot create a capability")
    claims = docs["claims"].get("claims")
    if not isinstance(claims, list) or len(claims) != 78 or any(
        not isinstance(record, dict) or record.get("status") != "pending" or record.get("maturity_level") != "C1"
        for record in claims
    ):
        errors.append("environment qualification layer must preserve 78 pending C1 claims")
    capability_evidence = docs["capability_evidence"].get("evidence")
    if not isinstance(capability_evidence, list) or len(capability_evidence) != 78 or any(
        not isinstance(record, dict) or record.get("status") != "pending" or record.get("evidence_type") != "E1"
        for record in capability_evidence
    ):
        errors.append("environment qualification layer must preserve 78 pending E1 evidence records")
    verification_records = docs["verification_records"].get("verification_records")
    if not isinstance(verification_records, list) or len(verification_records) != 78 or any(
        not isinstance(record, dict)
        or record.get("status") != "pending"
        or record.get("decision") != "pending"
        or record.get("verification_level") != "V0"
        for record in verification_records
    ):
        errors.append("environment qualification layer must preserve 78 pending V0 verification records")
    entities = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    agent_count = sum(1 for entity in entities.values() if entity.get("entity_type") == "agent")
    if agent_count != 0:
        errors.append("environment qualification layer cannot create or convert an Agent")

    expected_validators = sorted(
        str(path.relative_to(root)) for path in (root / "validation").glob("*_validator.py")
    )
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
    validator_inputs = [record for record in inputs if isinstance(record, dict) and record.get("input_type") == "validator_list"] if isinstance(inputs, list) else []
    if len(validator_inputs) != 1 or validator_inputs[0].get("value") != expected_validators or validator_inputs[0].get("status") != "pending":
        errors.append("experiment validator-list input must match the live suite and remain pending")

    required_tokens = {
        "qualification_constitution": [
            "environment_identity:",
            "environment_evidence:",
            "qualification_criteria:",
            "environment_lock:",
            "revocation:",
            "Environment Definition != Environment Qualification",
        ],
        "context_constitution": [
            "qualified_environment_requirement:",
            "environment-qualifications.yaml",
            "current_qualified_environment_count: 0",
        ],
        "readiness_constitution": [
            "environment_qualification_reference:",
            "environment-qualification-constitution.yaml",
            "current_qualified_runner_environment_count: 0",
        ],
    }
    for text_name, tokens in required_tokens.items():
        for token in tokens:
            if token not in texts[text_name]:
                errors.append(f"{text_name} missing required boundary token: {token}")

    evolution_ids = [int(match.group(1)) for match in EVOLUTION_ID_RE.finditer(texts["evolution_ledger"])]
    num_ids = len(evolution_ids)
    if (
        not num_ids
        or num_ids != len(set(evolution_ids))
        or min(evolution_ids) != 1
        or max(evolution_ids) != num_ids
        or num_ids < 30
        or 30 not in evolution_ids
        or evolution_ids[-1] != num_ids
    ):
        errors.append("evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0030, and append the latest ID last")
    if "runner_environment_qualification_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append("evolution ledger must contain the Runner Environment Qualification record")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "environment_qualification_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "environment_count": len(identities),
            "runner_environment_count": len(runner_environments),
            "environment_identity_status_distribution": dict(Counter(item.get("status") for item in identities.values())),
            "environment_evidence_count": len(evidence_records),
            "environment_evidence_type_distribution": {item: evidence_type_counts[item] for item in sorted(EVIDENCE_TYPES)},
            "qualification_count": len(qualifications),
            "qualification_result_distribution": dict(Counter(item.get("result") for item in qualifications.values())),
            "qualified_environment_count": sum(1 for item in qualifications.values() if item.get("result") == "verified"),
            "environment_lock_count": len(locks),
            "environment_lock_status_distribution": dict(Counter(item.get("status") for item in locks.values())),
            "runner_count": len(docs["runners"].get("runners", [])),
            "execution_count": len(docs["runner_executions"].get("runner_executions", [])),
            "event_count": len(docs["events"].get("events", [])),
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "agent_count": agent_count,
            "permission_grant_count": 0,
            "remaining_gaps": [
                "environment owner identity is not attributed",
                "environment evidence registry is empty",
                "OS and Python versions are not captured",
                "dependency and configuration digests are absent",
                "the shared environment lock remains pending",
                "all six qualification criteria remain pending",
                "no in-scope verifier has issued an environment-qualification decision",
                "no Runner or Runner scope exists",
                "Executor, capture, and experiment authorizations remain pending",
                "snapshot, validator manifest, freeze manifest, and certificate remain pending",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "ecological_environments": registry / "environments.yaml",
        "runner_environments": registry / "runner-environments.yaml",
        "environment_identities": registry / "environment-identities.yaml",
        "environment_evidence": registry / "environment-evidence.yaml",
        "environment_qualifications": registry / "environment-qualifications.yaml",
        "environment_locks": registry / "environment-locks.yaml",
        "verifiers": registry / "verifiers.yaml",
        "runners": registry / "runners.yaml",
        "runner_executions": registry / "runner-executions.yaml",
        "events": registry / "events.yaml",
        "execution_contexts": registry / "execution-contexts.yaml",
        "runtimes": registry / "runtime-instances.yaml",
        "snapshots": registry / "experiment-snapshots.yaml",
        "capabilities": registry / "capabilities.yaml",
        "claims": registry / "capability-claims.yaml",
        "capability_evidence": registry / "capability-evidence.yaml",
        "verification_records": registry / "verification-records.yaml",
        "entities": registry / "entities.yaml",
        "validator_manifests": registry / "validator-manifests.yaml",
        "experiment_inputs": registry / "experiment-inputs.yaml",
    }
    docs = {name: load_json_yaml(path) for name, path in paths.items()}
    text_paths = {
        "qualification_constitution": root / "constitution" / "environment-qualification-constitution.yaml",
        "context_constitution": root / "constitution" / "execution-context-constitution.yaml",
        "readiness_constitution": root / "constitution" / "experiment-readiness-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in text_paths.items()}
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DBOS v0.1 Runner Environment Qualification")
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
            "validator": "environment_qualification_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS environment_qualification_validator: "
            f"environments={summary['environment_count']}, qualifications={summary['qualification_count']}, "
            f"qualified={summary['qualified_environment_count']}, locks={summary['environment_lock_count']}"
        )
    else:
        print("FAIL environment_qualification_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
