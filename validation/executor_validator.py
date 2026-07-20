#!/usr/bin/env python3
"""Validate the empty, unauthorized DBOS experiment-executor baseline.

Agent-readable contract:
- Executor is a bounded accountable role, not an Agent, Runtime, or Organism.
- No executor or executor scope exists in v0.1.
- One authorization slot remains pending with no executor, scope, authorizer,
  timestamp, authority, capability, or permission.
- No experiment, snapshot capture, event, runtime, or evidence mutation occurs.
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
AUTHORIZATION_ID = "DBOS-EXP-0001-EXECUTOR-AUTH-0001"
EXECUTOR_TYPES = {"automated_runner", "human_operator"}
EXECUTOR_STATUSES = {"proposed", "verified", "active", "suspended", "revoked", "retired"}
SCOPE_STATUSES = {"proposed", "defined", "approved", "suspended", "revoked", "superseded"}
AUTHORIZATION_STATUSES = {"pending", "authorized", "denied", "expired", "revoked"}
MANDATORY_FORBIDDEN_ACTIONS = {
    "modify constitution",
    "create agent",
    "grant permission",
    "alter evidence",
}
ALLOWED_ACTION_VOCABULARY = {
    "load registered experiment definition",
    "check frozen preconditions",
    "invoke explicitly authorized procedure step",
    "collect bounded execution outputs",
    "stop under registered stop rule",
}
FORBIDDEN_AUTHORITY_KEYS = {
    "agent_id",
    "runtime_id",
    "organism_id",
    "capability_id",
    "capability_assignment",
    "permission",
    "permission_grant",
    "execution_result",
    "event_id",
    "snapshot_hash",
    "evidence_level",
    "verification_level",
    "maturity_level",
}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping using only the standard library."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def index_records(records: Any, key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    """Index mapping records and reject missing or duplicate identifiers."""
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


def valid_timestamp(value: Any) -> bool:
    if not nonempty_string(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def reject_authority_keys(value: Any, label: str, errors: list[str]) -> None:
    """Reject outcome, identity-conversion, authority, and level fields in executor records."""
    if isinstance(value, dict):
        present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(value))
        if present:
            errors.append(f"{label}: executor governance cannot contain authority or result fields {present}")
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


def validate(
    docs: dict[str, dict[str, Any]],
    texts: dict[str, str],
    root: Path,
) -> dict[str, Any]:
    """Validate executor identity, scope, authorization, and no-effect boundaries."""
    errors: list[str] = []

    experiments = index_records(docs["experiments"].get("experiments"), "experiment_id", "experiments", errors)
    if tuple(experiments) != (EXPERIMENT_ID,):
        errors.append("executor layer requires exactly the registered DBOS-EXP-0001 experiment")
    experiment = experiments.get(EXPERIMENT_ID, {})
    if experiment.get("status") != "registered" or experiment.get("execution_status") != "not_executed":
        errors.append("executor modeling cannot authorize or execute DBOS-EXP-0001")
    for field in ("execution_context_ref", "runtime_ref", "run_ref"):
        if experiment.get(field) is not None:
            errors.append(f"experiment {field} must remain null")

    entities = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    subjects = index_records(docs["subjects"].get("experiment_subjects"), "subject_id", "experiment_subjects", errors)
    verifiers = index_records(docs["verifiers"].get("verifiers"), "verifier_id", "verifiers", errors)
    governed_identity_refs = set(entities) | set(subjects) | set(verifiers)
    governed_identity_refs.update(
        subject.get("entity_id") for subject in subjects.values() if nonempty_string(subject.get("entity_id"))
    )
    governed_identity_refs.update(
        entity.get("canonical_id") for entity in entities.values() if nonempty_string(entity.get("canonical_id"))
    )
    executor_identities = index_records(
        docs["executor_identities"].get("executor_identities"),
        "executor_identity_id",
        "executor_identities",
        errors,
    )

    executor_doc = docs["executors"]
    executors = index_records(executor_doc.get("executors"), "executor_id", "executors", errors)
    executor_type_counts: Counter[str] = Counter()
    for executor_id, executor in executors.items():
        executor_type = executor.get("executor_type")
        if executor_type not in EXECUTOR_TYPES:
            errors.append(f"{executor_id}: invalid executor_type {executor_type!r}")
        else:
            executor_type_counts[executor_type] += 1
        identity_ref = executor.get("identity_ref")
        enrolled_identity = executor_identities.get(identity_ref)
        if not nonempty_string(identity_ref) or enrolled_identity is None:
            errors.append(f"{executor_id}: executor must reference an existing enrolled Executor Identity")
        elif enrolled_identity.get("verification_status") != "verified" or enrolled_identity.get("lifecycle_state") != "verified":
            errors.append(f"{executor_id}: Executor Identity must be verified before appointment")
        scope_refs = executor.get("scope")
        if not isinstance(scope_refs, list):
            errors.append(f"{executor_id}: scope must be a list of executor-scope references")
        if not nonempty_string(executor.get("version")):
            errors.append(f"{executor_id}: version must be explicit")
        if executor.get("status") not in EXECUTOR_STATUSES:
            errors.append(f"{executor_id}: invalid executor status {executor.get('status')!r}")
        if executor.get("agent_status") not in (None, "not_an_agent"):
            errors.append(f"{executor_id}: executor cannot become an Agent")
        if executor.get("runtime_status") not in (None, "not_a_runtime"):
            errors.append(f"{executor_id}: executor cannot become a Runtime")
        if executor.get("organism_status") not in (None, "not_an_organism"):
            errors.append(f"{executor_id}: executor cannot become an Organism")
        reject_authority_keys(executor, f"executor {executor_id}", errors)
    if executors:
        errors.append("v0.1 executor registry must remain empty until explicit identity appointment")
    executor_meta = executor_doc.get("metadata", {})
    if executor_meta.get("executor_count") != 0:
        errors.append("executor metadata count must remain zero")
    for executor_type in EXECUTOR_TYPES:
        if executor_meta.get("executor_type_distribution", {}).get(executor_type) != 0:
            errors.append(f"executor type distribution for {executor_type} must remain zero")
    require_zero(
        executor_meta,
        ("verified_executor_count", "active_executor_count", "agent_created_count", "runtime_created_count", "organism_created_count", "capability_effect_count", "permission_grant_count"),
        "executor",
        errors,
    )

    scope_doc = docs["executor_scopes"]
    scopes = index_records(scope_doc.get("executor_scopes"), "scope_id", "executor_scopes", errors)
    for scope_id, scope in scopes.items():
        executor_id = scope.get("executor_id")
        if not nonempty_string(executor_id) or executor_id not in executors:
            errors.append(f"{scope_id}: scope must reference an existing executor")
        allowed_experiments = scope.get("allowed_experiments")
        if not isinstance(allowed_experiments, list) or not allowed_experiments:
            errors.append(f"{scope_id}: allowed_experiments must be explicit and non-empty")
        else:
            missing_experiments = sorted(set(allowed_experiments) - set(experiments))
            if missing_experiments:
                errors.append(f"{scope_id}: unknown allowed experiments {missing_experiments}")
        allowed_actions = scope.get("allowed_actions")
        if not isinstance(allowed_actions, list):
            errors.append(f"{scope_id}: allowed_actions must be a list")
        else:
            unknown_actions = sorted(set(allowed_actions) - ALLOWED_ACTION_VOCABULARY)
            if unknown_actions:
                errors.append(f"{scope_id}: actions outside controlled vocabulary {unknown_actions}")
        forbidden_actions = scope.get("forbidden_actions")
        if not isinstance(forbidden_actions, list):
            errors.append(f"{scope_id}: forbidden_actions must be a list")
        else:
            missing_forbidden = sorted(MANDATORY_FORBIDDEN_ACTIONS - set(forbidden_actions))
            if missing_forbidden:
                errors.append(f"{scope_id}: missing mandatory forbidden actions {missing_forbidden}")
        if scope.get("status", "proposed") not in SCOPE_STATUSES:
            errors.append(f"{scope_id}: invalid scope status {scope.get('status')!r}")
        if scope.get("authority_effect", "none") != "none":
            errors.append(f"{scope_id}: a scope cannot create execution authority")
        reject_authority_keys(scope, f"executor scope {scope_id}", errors)
    if scopes:
        errors.append("v0.1 executor scope registry must remain empty while no executor exists")
    scope_meta = scope_doc.get("metadata", {})
    if scope_meta.get("scope_count") != 0:
        errors.append("executor scope metadata count must remain zero")
    if set(scope_doc.get("mandatory_forbidden_actions", [])) != MANDATORY_FORBIDDEN_ACTIONS:
        errors.append("executor scope registry must preserve all mandatory forbidden actions")
    if set(scope_doc.get("allowed_action_vocabulary", [])) != ALLOWED_ACTION_VOCABULARY:
        errors.append("executor scope registry must preserve the controlled action vocabulary")
    require_zero(
        scope_meta,
        ("active_scope_count", "execution_authority_count", "capability_effect_count", "permission_grant_count", "historical_evidence_change_count"),
        "executor scope",
        errors,
    )

    authorization_doc = docs["executor_authorizations"]
    authorizations = index_records(
        authorization_doc.get("executor_authorizations"), "authorization_id", "executor_authorizations", errors
    )
    if tuple(authorizations) != (AUTHORIZATION_ID,):
        errors.append("executor authorization registry must contain exactly one pending slot")
    authorization = authorizations.get(AUTHORIZATION_ID, {})
    if authorization.get("experiment_id") != EXPERIMENT_ID or authorization.get("experiment_id") not in experiments:
        errors.append(f"{AUTHORIZATION_ID}: authorization must reference DBOS-EXP-0001")
    authorization_status = authorization.get("status")
    if authorization_status not in AUTHORIZATION_STATUSES:
        errors.append(f"{AUTHORIZATION_ID}: invalid authorization status {authorization_status!r}")
    if authorization_status == "pending":
        for field in ("executor_id", "authorized_by", "scope_ref", "timestamp"):
            if authorization.get(field) is not None:
                errors.append(f"{AUTHORIZATION_ID}: pending authorization requires {field}=null")
        if authorization.get("current_effect") != "none":
            errors.append(f"{AUTHORIZATION_ID}: pending authorization requires current_effect=none")
    elif authorization_status == "authorized":
        executor_id = authorization.get("executor_id")
        executor = executors.get(executor_id)
        if executor is None or executor.get("status") not in {"verified", "active"}:
            errors.append(f"{AUTHORIZATION_ID}: authorized state requires verified or active executor")
        scope_ref = authorization.get("scope_ref")
        scope = scopes.get(scope_ref)
        if scope is None or scope.get("executor_id") != executor_id or scope.get("status") != "approved":
            errors.append(f"{AUTHORIZATION_ID}: authorized state requires approved matching executor scope")
        authorized_by = authorization.get("authorized_by")
        if not nonempty_string(authorized_by) or authorized_by not in governed_identity_refs:
            errors.append(f"{AUTHORIZATION_ID}: authorized state requires attributable governed authorizer")
        if executor is not None and authorized_by == executor.get("identity_ref"):
            errors.append(f"{AUTHORIZATION_ID}: executor cannot self-authorize")
        if not valid_timestamp(authorization.get("timestamp")):
            errors.append(f"{AUTHORIZATION_ID}: authorized state requires timezone-aware timestamp")
        experiment_authorizations = index_records(
            docs["experiment_authorizations"].get("experiment_authorizations"),
            "authorization_id",
            "experiment_authorizations",
            errors,
        )
        if not any(
            record.get("experiment_id") == EXPERIMENT_ID and record.get("status") == "authorized"
            for record in experiment_authorizations.values()
        ):
            errors.append(f"{AUTHORIZATION_ID}: executor authorization cannot precede experiment authorization")
    if authorization_status != "pending":
        errors.append("v0.1 executor authorization must remain pending and cannot be generated automatically")
    reject_authority_keys(authorization, f"executor authorization {AUTHORIZATION_ID}", errors)
    authorization_meta = authorization_doc.get("metadata", {})
    if authorization_meta.get("executor_authorization_count") != 1:
        errors.append("executor authorization metadata must report one record")
    if authorization_meta.get("authorization_status_distribution", {}).get("pending") != 1:
        errors.append("executor authorization metadata must report one pending record")
    require_zero(
        authorization_meta,
        ("active_executor_authorization_count", "experiment_execution_authority_count", "capability_effect_count", "permission_grant_count"),
        "executor authorization",
        errors,
    )

    experiment_authorizations = index_records(
        docs["experiment_authorizations"].get("experiment_authorizations"),
        "authorization_id",
        "experiment_authorizations",
        errors,
    )
    if len(experiment_authorizations) != 1 or any(item.get("status") != "pending" for item in experiment_authorizations.values()):
        errors.append("experiment authorization must remain pending")

    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != [] or docs["capabilities"].get("metadata", {}).get("confirmed_capability_count") != 0:
        errors.append("executor layer cannot create or assign a capability")
    claims = docs["claims"].get("claims")
    if not isinstance(claims, list) or len(claims) != 78:
        errors.append("executor layer must preserve the 78-claim baseline")
    elif any(claim.get("status") != "pending" or claim.get("maturity_level") != "C1" for claim in claims if isinstance(claim, dict)):
        errors.append("executor layer cannot change capability claim status or C maturity")
    evidence = docs["capability_evidence"].get("evidence")
    if not isinstance(evidence, list) or len(evidence) != 78:
        errors.append("executor layer cannot delete or add historical capability evidence")
    elif any(
        record.get("evidence_type") != "E1" or record.get("status") != "pending"
        for record in evidence if isinstance(record, dict)
    ):
        errors.append("executor layer cannot alter historical E1 evidence status or level")
    verification_records = docs["verification_records"].get("verification_records")
    if not isinstance(verification_records, list) or len(verification_records) != 78:
        errors.append("executor layer must preserve 78 verification records")
    elif any(
        record.get("verification_level") != "V0" or record.get("decision") != "pending" or record.get("status") != "pending"
        for record in verification_records if isinstance(record, dict)
    ):
        errors.append("executor layer cannot alter V0 pending verification records")

    zero_list_requirements = {
        "events": ("events", "events"),
        "contexts": ("execution_contexts", "execution contexts"),
        "runtimes": ("runtime_instances", "runtime instances"),
        "candidates": ("organism_candidates", "organism candidates"),
        "behavior_traces": ("behavior_traces", "behavior traces"),
        "resource_flows": ("resource_flows", "resource flows"),
        "artifact_digests": ("artifact_digests", "artifact digests"),
        "capture_evidence": ("capture_evidence", "capture evidence"),
    }
    for doc_name, (field, label) in zero_list_requirements.items():
        if docs[doc_name].get(field) != []:
            errors.append(f"executor layer cannot generate {label}")

    snapshots = docs["experiment_snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1:
        errors.append("executor layer must preserve one pending snapshot slot")
    else:
        snapshot = snapshots[0]
        for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash", "captured_at"):
            if snapshot.get(field) is not None:
                errors.append(f"executor layer cannot generate snapshot field {field}")
        if snapshot.get("status") != "pending":
            errors.append("executor layer cannot capture or freeze the snapshot")

    captures = docs["snapshot_captures"].get("snapshot_captures")
    if not isinstance(captures, list) or len(captures) != 1:
        errors.append("executor layer must preserve one pending capture slot")
    else:
        capture = captures[0]
        if capture.get("status") != "pending" or capture.get("captured_at") is not None:
            errors.append("executor layer cannot execute snapshot capture")

    agent_count = sum(1 for entity in entities.values() if entity.get("entity_type") == "agent")
    if agent_count != 0 or docs["entities"].get("metadata", {}).get("classification_counts", {}).get("agent") != 0:
        errors.append("executor layer cannot create or convert an Agent identity")
    if docs["candidates"].get("metadata", {}).get("digital_organism_count") != 0:
        errors.append("executor layer cannot create a Digital Organism")

    required_constitution_tokens = {
        "executor_constitution": [
            "Executor != Agent.",
            "Executor != Runtime.",
            "Executor != Digital Organism.",
            "identity_enrollment_requirement:",
            "Executor Identity Verification != Executor Appointment.",
            "executor_lifecycle:",
            "executor_accountability:",
        ],
        "capture_readiness_constitution": [
            "collector_executor_separation:",
            "Collector != Executor.",
            "Capture Authorization != Executor Authorization.",
        ],
        "experiment_readiness_constitution": [
            "executor_readiness_requirement:",
            "executor-authorizations.yaml",
            "current_status: \"pending\"",
        ],
    }
    for text_name, tokens in required_constitution_tokens.items():
        for token in tokens:
            if token not in texts[text_name]:
                errors.append(f"{text_name} missing required boundary token: {token}")

    evolution_ids = [int(value) for value in EVOLUTION_ID_RE.findall(texts["evolution_ledger"])]
    if (
        not evolution_ids
        or len(evolution_ids) != len(set(evolution_ids))
        or sorted(evolution_ids) != list(range(1, max(evolution_ids) + 1))
        or max(evolution_ids) < 27
        or 27 not in evolution_ids
        or evolution_ids[-1] != max(evolution_ids)
    ):
        errors.append("evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0027, and append the latest ID last")
    if "executor_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append("evolution ledger must contain the executor-layer record")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "executor_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "experiment_id": EXPERIMENT_ID,
            "executor_count": len(executors),
            "executor_identity_count": len(executor_identities),
            "executor_type_distribution": {executor_type: executor_type_counts[executor_type] for executor_type in sorted(EXECUTOR_TYPES)},
            "executor_scope_count": len(scopes),
            "executor_authorization_count": len(authorizations),
            "authorization_status_distribution": dict(Counter(item.get("status") for item in authorizations.values())),
            "experiment_execution_status": experiment.get("execution_status"),
            "capability_count": len(capabilities) if isinstance(capabilities, list) else None,
            "claim_count": len(claims) if isinstance(claims, list) else None,
            "evidence_count": len(evidence) if isinstance(evidence, list) else None,
            "verification_record_count": len(verification_records) if isinstance(verification_records, list) else None,
            "event_count": len(docs["events"].get("events", [])),
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "agent_count": agent_count,
            "permission_grant_count": 0,
            "historical_evidence_change_count": 0,
            "remaining_gaps": [
                "no executor identity is appointed",
                "no executor scope exists",
                "executor authorization has no executor, scope, authorizer, or timestamp",
                "experiment and capture readiness remain pending",
                "experiment authorization remains pending",
                "snapshot, validator set, environment, and freeze are not frozen",
                "no execution context, runtime, event, action trace, or execution evidence exists",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "experiments": registry / "experiments.yaml",
        "executor_identities": registry / "executor-identities.yaml",
        "executors": registry / "executors.yaml",
        "executor_scopes": registry / "executor-scopes.yaml",
        "executor_authorizations": registry / "executor-authorizations.yaml",
        "entities": registry / "entities.yaml",
        "subjects": registry / "experiment-subjects.yaml",
        "verifiers": registry / "verifiers.yaml",
        "experiment_authorizations": registry / "experiment-authorizations.yaml",
        "capabilities": registry / "capabilities.yaml",
        "claims": registry / "capability-claims.yaml",
        "capability_evidence": registry / "capability-evidence.yaml",
        "verification_records": registry / "verification-records.yaml",
        "events": registry / "events.yaml",
        "contexts": registry / "execution-contexts.yaml",
        "runtimes": registry / "runtime-instances.yaml",
        "candidates": registry / "organism-candidates.yaml",
        "behavior_traces": registry / "behavior-traces.yaml",
        "resource_flows": registry / "resource-flows.yaml",
        "experiment_snapshots": registry / "experiment-snapshots.yaml",
        "snapshot_captures": registry / "snapshot-captures.yaml",
        "artifact_digests": registry / "artifact-digests.yaml",
        "capture_evidence": registry / "capture-evidence.yaml",
    }
    docs = {name: load_json_yaml(path) for name, path in paths.items()}
    text_paths = {
        "executor_constitution": root / "constitution" / "executor-constitution.yaml",
        "capture_readiness_constitution": root / "constitution" / "snapshot-capture-readiness-constitution.yaml",
        "experiment_readiness_constitution": root / "constitution" / "experiment-readiness-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in text_paths.items()}
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the DBOS v0.1 experiment executor layer")
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
            "validator": "executor_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS executor_validator: "
            f"executors={summary['executor_count']}, scopes={summary['executor_scope_count']}, "
            f"authorizations={summary['executor_authorization_count']}, authority=none"
        )
    else:
        print("FAIL executor_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
