#!/usr/bin/env python3
"""Validate Environment Evidence Capture governance without collecting evidence.

Agent-readable contract:
- One capture request references the existing Runner environment and remains
  pending with collector=null and timestamp=null.
- Environment facts, digests, and collection evidence remain empty because no
  collection occurred.
- Facts require attributable sources; verified digests require non-empty valid
  hashes and verification material.
- Capture material cannot automatically qualify or freeze an environment,
  populate qualification evidence, create permission, or promote C/E/V.
- Exit 0 means local structural PASS only; it does not perform collection.
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
CAPTURE_ID = "DBOS-EXP-0001-ENV-EVIDENCE-CAPTURE-0001"
QUALIFICATION_ID = "DBOS-EXP-0001-RUNNER-ENV-QUAL-0001"
ENVIRONMENT_LOCK_ID = "DBOS-EXP-0001-ENV-LOCK-0001"

CAPTURE_STATUSES = {"pending", "collecting", "collected", "validated", "partial", "invalid", "revoked"}
MATERIAL_CAPTURE_STATUSES = {"collected", "validated", "partial"}
FACT_TYPES = {"os", "python", "dependency", "configuration", "hardware"}
FACT_STATUSES = {"captured", "validated", "partial", "invalid", "revoked"}
DIGEST_TYPES = {"dependency", "configuration", "environment"}
DIGEST_STATUSES = {"captured", "verified", "invalid", "revoked"}
COLLECTION_EVIDENCE_STATUSES = {"captured", "verified", "partial", "failed", "invalid", "revoked"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EVOLUTION_ID_RE = re.compile(r'^\s*- id: "DBOS-EVO-(\d{4})"\s*$', re.MULTILINE)
SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "credential",
    "password",
    "private_key",
    "secret",
    "token",
}
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
    """Load one JSON-compatible YAML mapping with no third-party dependency."""
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


def attributable(value: Any) -> bool:
    if nonempty_string(value):
        return True
    if isinstance(value, dict):
        return bool(value) and all(nonempty_string(key) for key in value)
    if isinstance(value, list):
        return bool(value) and all(attributable(item) for item in value)
    return False


def reject_sensitive_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in SENSITIVE_KEYS:
                errors.append(f"{label}: sensitive field {key!r} is prohibited")
            reject_sensitive_keys(child, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive_keys(child, f"{label}[{index}]", errors)


def reject_authority_keys(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(value))
        if present:
            errors.append(f"{label}: collection governance cannot contain authority or promotion fields {present}")
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


def list_field(record: dict[str, Any], field: str, label: str, errors: list[str]) -> list[Any]:
    value = record.get(field)
    if not isinstance(value, list):
        errors.append(f"{label}.{field} must be a list")
        return []
    return value


def validate(docs: dict[str, dict[str, Any]], texts: dict[str, str], root: Path) -> dict[str, Any]:
    """Validate capture references, material integrity, privacy, and zero-effect boundaries."""
    errors: list[str] = []

    ecological_environments = index_records(
        docs["ecological_environments"].get("environments"), "environment_id", "ecological_environments", errors
    )
    environment_identities = index_records(
        docs["environment_identities"].get("environment_identities"),
        "environment_id",
        "environment_identities",
        errors,
    )
    runner_environments = index_records(
        docs["runner_environments"].get("runner_environments"), "environment_id", "runner_environments", errors
    )
    collectors = index_records(
        docs["capture_collectors"].get("capture_collectors"), "collector_id", "capture_collectors", errors
    )
    captures = index_records(
        docs["captures"].get("environment_evidence_captures"),
        "capture_id",
        "environment_evidence_captures",
        errors,
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

    if tuple(environment_identities) != (RUNNER_ENVIRONMENT_ID,):
        errors.append("capture layer requires exactly the existing Runner environment identity")
    identity = environment_identities.get(RUNNER_ENVIRONMENT_ID, {})
    source = identity.get("source") if isinstance(identity.get("source"), dict) else {}
    if source.get("source_environment_ref") != SOURCE_ENVIRONMENT_ID or SOURCE_ENVIRONMENT_ID not in ecological_environments:
        errors.append("environment identity must retain its existing ecological source")
    if identity.get("status") != "defined" or identity.get("qualification_status") != "pending":
        errors.append("environment identity must remain defined with pending qualification")
    if identity.get("runtime_status") != "not_a_runtime" or identity.get("agent_status") != "not_an_agent":
        errors.append("environment capture cannot create a Runtime or Agent")
    if identity.get("authority_effect") != "none":
        errors.append("environment identity cannot create authority")

    if tuple(runner_environments) != (RUNNER_ENVIRONMENT_ID,):
        errors.append("capture layer requires exactly the existing Runner environment slot")
    runner_environment = runner_environments.get(RUNNER_ENVIRONMENT_ID, {})
    if runner_environment.get("status") != "defined" or runner_environment.get("qualification_status") != "not_qualified":
        errors.append("Runner environment must remain defined and not_qualified")
    for field in ("os", "python_version", "configuration_digest", "locked_at"):
        if runner_environment.get(field) is not None:
            errors.append(f"environment collection model cannot populate Runner environment {field}")
    if runner_environment.get("dependencies") != [] or runner_environment.get("evidence_refs") != []:
        errors.append("environment collection model cannot populate Runner dependencies or evidence")

    if tuple(captures) != (CAPTURE_ID,):
        errors.append("capture registry must contain exactly one pending request")
    capture = captures.get(CAPTURE_ID, {})
    if capture.get("environment_id") != RUNNER_ENVIRONMENT_ID or RUNNER_ENVIRONMENT_ID not in environment_identities:
        errors.append("capture must reference the existing Runner environment identity")
    status = capture.get("status")
    if status not in CAPTURE_STATUSES:
        errors.append(f"capture has invalid status {status!r}")
    collector_ref = capture.get("collector")
    timestamp = capture.get("timestamp")
    if status == "pending":
        if collector_ref is not None or timestamp is not None:
            errors.append("pending capture requires collector=null and timestamp=null")
    else:
        collector = collectors.get(collector_ref)
        if collector is None:
            errors.append("non-pending capture requires an existing attributable collector")
        elif collector.get("status") not in {"verified", "active"}:
            errors.append("non-pending capture requires a verified or active collector")
        if not valid_timestamp(timestamp):
            errors.append("non-pending capture requires a timezone-aware timestamp")
    fact_refs = list_field(capture, "fact_refs", "capture", errors)
    digest_refs = list_field(capture, "digest_refs", "capture", errors)
    collection_evidence_refs = list_field(capture, "collection_evidence_refs", "capture", errors)
    qualification_evidence_refs = list_field(capture, "qualification_evidence_refs", "capture", errors)
    for fact_ref in fact_refs:
        if fact_ref not in facts:
            errors.append(f"capture has unknown fact_ref {fact_ref!r}")
    for digest_ref in digest_refs:
        if digest_ref not in digests:
            errors.append(f"capture has unknown digest_ref {digest_ref!r}")
    for evidence_ref in collection_evidence_refs:
        if evidence_ref not in collection_evidence:
            errors.append(f"capture has unknown collection_evidence_ref {evidence_ref!r}")
    for evidence_ref in qualification_evidence_refs:
        if evidence_ref not in qualification_evidence:
            errors.append(f"capture has unknown qualification_evidence_ref {evidence_ref!r}")
    if status in MATERIAL_CAPTURE_STATUSES and (not fact_refs or not digest_refs or not collection_evidence_refs):
        errors.append("material capture status requires retained facts, digests, and collection evidence")
    if status == "validated" and not qualification_evidence_refs:
        errors.append("validated capture requires separately created qualification evidence references")
    if capture.get("authority_effect") != "none":
        errors.append("capture registration cannot create authority")
    reject_sensitive_keys(capture, "Environment capture", errors)
    reject_authority_keys(capture, "Environment capture", errors)
    if status != "pending" or collector_ref is not None or timestamp is not None:
        errors.append("v0.1 capture request must remain pending and unperformed")
    if any((fact_refs, digest_refs, collection_evidence_refs, qualification_evidence_refs)):
        errors.append("v0.1 pending capture cannot claim collected material")

    fact_type_counts: Counter[str] = Counter()
    for fact_id, fact in facts.items():
        environment_id = fact.get("environment_id")
        if environment_id not in environment_identities:
            errors.append(f"{fact_id}: fact must reference an environment identity")
        fact_type = fact.get("fact_type")
        if fact_type not in FACT_TYPES:
            errors.append(f"{fact_id}: invalid fact_type {fact_type!r}")
        else:
            fact_type_counts[fact_type] += 1
        if fact.get("value") is None or fact.get("value") == "":
            errors.append(f"{fact_id}: fact value must be explicit")
        if not attributable(fact.get("source")):
            errors.append(f"{fact_id}: fact must have an attributable source")
        if not valid_timestamp(fact.get("timestamp")):
            errors.append(f"{fact_id}: fact timestamp must be timezone-aware")
        capture_ref = fact.get("capture_id")
        parent_capture = captures.get(capture_ref)
        if parent_capture is None or parent_capture.get("environment_id") != environment_id:
            errors.append(f"{fact_id}: fact capture must exist and belong to the same environment")
        if fact.get("status", "captured") not in FACT_STATUSES:
            errors.append(f"{fact_id}: invalid fact status {fact.get('status')!r}")
        if fact.get("authority_effect", "none") != "none":
            errors.append(f"{fact_id}: environment fact cannot create authority")
        reject_sensitive_keys(fact, f"Environment fact {fact_id}", errors)
        reject_authority_keys(fact, f"Environment fact {fact_id}", errors)
    if facts:
        errors.append("v0.1 environment fact registry must remain empty because collection was not performed")

    digest_type_counts: Counter[str] = Counter()
    for digest_id, digest in digests.items():
        environment_id = digest.get("environment_id")
        if environment_id not in environment_identities:
            errors.append(f"{digest_id}: digest must reference an environment identity")
        digest_type = digest.get("digest_type")
        if digest_type not in DIGEST_TYPES:
            errors.append(f"{digest_id}: invalid digest_type {digest_type!r}")
        else:
            digest_type_counts[digest_type] += 1
        if digest.get("hash_algorithm") != "sha256":
            errors.append(f"{digest_id}: hash_algorithm must be sha256")
        if not DIGEST_RE.fullmatch(str(digest.get("hash_value", ""))):
            errors.append(f"{digest_id}: hash_value must be non-empty valid sha256")
        if not valid_timestamp(digest.get("created_at")):
            errors.append(f"{digest_id}: created_at must be timezone-aware")
        capture_ref = digest.get("capture_id")
        parent_capture = captures.get(capture_ref)
        if parent_capture is None or parent_capture.get("environment_id") != environment_id:
            errors.append(f"{digest_id}: digest capture must exist and belong to the same environment")
        source_refs = digest.get("source_refs", [])
        if not isinstance(source_refs, list):
            errors.append(f"{digest_id}: source_refs must be a list")
            source_refs = []
        for source_ref in source_refs:
            if source_ref not in facts:
                errors.append(f"{digest_id}: unknown source fact {source_ref!r}")
        digest_status = digest.get("status", "captured")
        if digest_status not in DIGEST_STATUSES:
            errors.append(f"{digest_id}: invalid digest status {digest_status!r}")
        if digest_status == "verified" and (not source_refs or not nonempty_string(digest.get("verification_ref"))):
            errors.append(f"{digest_id}: verified digest requires source_refs and verification_ref")
        if digest.get("authority_effect", "none") != "none":
            errors.append(f"{digest_id}: environment digest cannot create authority")
        reject_sensitive_keys(digest, f"Environment digest {digest_id}", errors)
        reject_authority_keys(digest, f"Environment digest {digest_id}", errors)
    if digests:
        errors.append("v0.1 environment digest registry must remain empty because collection was not performed")

    for evidence_id, evidence in collection_evidence.items():
        capture_ref = evidence.get("capture_id")
        parent_capture = captures.get(capture_ref)
        if parent_capture is None:
            errors.append(f"{evidence_id}: collection evidence must reference an existing capture")
        if not attributable(evidence.get("method")):
            errors.append(f"{evidence_id}: collection method must be attributable")
        if not attributable(evidence.get("source")):
            errors.append(f"{evidence_id}: collection source must be attributable")
        if not attributable(evidence.get("result")):
            errors.append(f"{evidence_id}: collection result must be explicit")
        if not valid_timestamp(evidence.get("timestamp")):
            errors.append(f"{evidence_id}: collection evidence timestamp must be timezone-aware")
        evidence_fact_refs = list_field(evidence, "fact_refs", evidence_id, errors)
        evidence_digest_refs = list_field(evidence, "digest_refs", evidence_id, errors)
        for fact_ref in evidence_fact_refs:
            if fact_ref not in facts:
                errors.append(f"{evidence_id}: unknown fact_ref {fact_ref!r}")
        for digest_ref in evidence_digest_refs:
            if digest_ref not in digests:
                errors.append(f"{evidence_id}: unknown digest_ref {digest_ref!r}")
        evidence_status = evidence.get("status", "captured")
        if evidence_status not in COLLECTION_EVIDENCE_STATUSES:
            errors.append(f"{evidence_id}: invalid collection evidence status {evidence_status!r}")
        if evidence_status == "verified":
            if parent_capture is None or parent_capture.get("status") != "validated":
                errors.append(f"{evidence_id}: verified collection evidence requires a validated capture")
            if not nonempty_string(evidence.get("verification_ref")):
                errors.append(f"{evidence_id}: verified collection evidence requires verification_ref")
        if evidence.get("authority_effect", "none") != "none":
            errors.append(f"{evidence_id}: collection evidence cannot create authority")
        reject_sensitive_keys(evidence, f"Collection evidence {evidence_id}", errors)
        reject_authority_keys(evidence, f"Collection evidence {evidence_id}", errors)
    if collection_evidence:
        errors.append("v0.1 collection evidence registry must remain empty because collection was not performed")

    if qualification_evidence:
        errors.append("capture governance cannot populate qualification evidence automatically")
    if tuple(qualifications) != (QUALIFICATION_ID,):
        errors.append("capture layer must preserve exactly one environment qualification review")
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
        errors.append("environment capture cannot approve qualification or advance any qualification criterion")

    if tuple(locks) != (ENVIRONMENT_LOCK_ID,):
        errors.append("capture layer must preserve the existing environment lock")
    lock = locks.get(ENVIRONMENT_LOCK_ID, {})
    if lock.get("environment_id") != SOURCE_ENVIRONMENT_ID or lock.get("runner_environment_ref") != RUNNER_ENVIRONMENT_ID:
        errors.append("environment lock must retain source and Runner environment references")
    if lock.get("evidence_capture_reference") != CAPTURE_ID:
        errors.append("environment lock must reference the pending environment evidence capture")
    if lock.get("evidence_reference") is not None or lock.get("evidence_refs") != []:
        errors.append("pending environment lock cannot claim collection evidence")
    if lock.get("status") != "pending" or lock.get("locked_at") is not None:
        errors.append("environment capture cannot freeze the environment lock")
    for field in ("os_version", "runtime_version", "dependency_hash", "os", "python", "dependencies_digest", "configuration_digest"):
        if lock.get(field) is not None:
            errors.append(f"environment capture model cannot populate lock field {field}")
    if lock.get("authority_effect") != "none":
        errors.append("environment lock cannot create authority")

    capture_meta = docs["captures"].get("metadata", {})
    if capture_meta.get("capture_count") != 1 or capture_meta.get("capture_status_distribution", {}).get("pending") != 1:
        errors.append("capture metadata must report one pending request")
    require_zero(capture_meta, ("attributable_collector_count", "collected_material_count", "fact_count", "digest_count", "collection_evidence_count", "qualified_environment_count", "frozen_environment_count", "runner_created_count", "execution_count", "permission_grant_count"), "Environment capture", errors)
    facts_meta = docs["facts"].get("metadata", {})
    if facts_meta.get("fact_count") != 0:
        errors.append("fact metadata must remain zero")
    require_zero(facts_meta, ("attributable_source_count", "qualified_environment_count", "permission_grant_count"), "Environment fact", errors)
    digests_meta = docs["digests"].get("metadata", {})
    if digests_meta.get("digest_count") != 0:
        errors.append("digest metadata must remain zero")
    require_zero(digests_meta, ("nonempty_hash_count", "verified_digest_count", "qualified_environment_count", "permission_grant_count"), "Environment digest", errors)
    collection_meta = docs["collection_evidence"].get("metadata", {})
    if collection_meta.get("collection_evidence_count") != 0:
        errors.append("collection evidence metadata must remain zero")
    require_zero(collection_meta, ("verified_collection_evidence_count", "qualification_evidence_created_count", "environment_qualification_count", "permission_grant_count"), "Collection evidence", errors)

    if docs["runners"].get("runners") != []:
        errors.append("environment capture layer cannot create a Runner")
    if docs["runner_executions"].get("runner_executions") != []:
        errors.append("environment capture layer cannot execute an experiment")
    if docs["events"].get("events") != []:
        errors.append("environment capture layer cannot generate an Event")
    if docs["execution_contexts"].get("execution_contexts") != []:
        errors.append("environment capture layer cannot generate an execution context")
    if docs["runtimes"].get("runtime_instances") != []:
        errors.append("environment capture layer cannot create a Runtime")
    snapshots = docs["snapshots"].get("experiment_snapshots")
    if not isinstance(snapshots, list) or len(snapshots) != 1 or snapshots[0].get("status") != "pending":
        errors.append("environment capture layer must preserve one pending experiment Snapshot slot")
    elif any(snapshots[0].get(field) is not None for field in ("file_tree_hash", "config_hash", "dependency_hash", "environment_hash", "captured_at")):
        errors.append("environment capture layer cannot generate a Snapshot hash")
    capabilities = docs["capabilities"].get("capabilities")
    if capabilities != []:
        errors.append("environment capture layer cannot create a capability")
    claims = docs["claims"].get("claims")
    if not isinstance(claims, list) or len(claims) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("maturity_level") != "C1" for item in claims):
        errors.append("environment capture layer must preserve 78 pending C1 claims")
    capability_evidence = docs["capability_evidence"].get("evidence")
    if not isinstance(capability_evidence, list) or len(capability_evidence) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("evidence_type") != "E1" for item in capability_evidence):
        errors.append("environment capture layer must preserve 78 pending E1 capability evidence records")
    verification_records = docs["verification_records"].get("verification_records")
    if not isinstance(verification_records, list) or len(verification_records) != 78 or any(not isinstance(item, dict) or item.get("status") != "pending" or item.get("decision") != "pending" or item.get("verification_level") != "V0" for item in verification_records):
        errors.append("environment capture layer must preserve 78 pending V0 verification records")
    entities = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    agent_count = sum(1 for entity in entities.values() if entity.get("entity_type") == "agent")
    if agent_count != 0:
        errors.append("environment capture layer cannot create or convert an Agent")

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
        "capture_constitution": [
            "evidence_collection:",
            "evidence_source:",
            "evidence_integrity:",
            "collection_boundary:",
            "privacy_protection:",
            "Capture Registration != Evidence Collection",
        ],
        "qualification_constitution": [
            "evidence_capture_dependency:",
            "environment-evidence-captures.yaml",
            "automatic_qualification_evidence_creation: false",
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
        or max(evolution_ids) < 31
        or 31 not in evolution_ids
        or evolution_ids[-1] != max(evolution_ids)
    ):
        errors.append("evolution ledger must preserve unique contiguous IDs, retain DBOS-EVO-0031, and append the latest ID last")
    if "environment_evidence_capture_layer_v0.1" not in texts["evolution_ledger"]:
        errors.append("evolution ledger must contain the Environment Evidence Capture record")

    return {
        "status": "PASS" if not errors else "FAIL",
        "validator": "environment_evidence_capture_validator",
        "schema_version": "0.1",
        "errors": errors,
        "summary": {
            "environment_count": len(environment_identities),
            "capture_count": len(captures),
            "capture_status_distribution": dict(Counter(item.get("status") for item in captures.values())),
            "fact_count": len(facts),
            "fact_type_distribution": {item: fact_type_counts[item] for item in sorted(FACT_TYPES)},
            "digest_count": len(digests),
            "digest_type_distribution": {item: digest_type_counts[item] for item in sorted(DIGEST_TYPES)},
            "collection_evidence_count": len(collection_evidence),
            "qualification_evidence_count": len(qualification_evidence),
            "qualified_environment_count": sum(1 for item in qualifications.values() if item.get("result") == "verified"),
            "environment_lock_status_distribution": dict(Counter(item.get("status") for item in locks.values())),
            "runner_count": len(docs["runners"].get("runners", [])),
            "execution_count": len(docs["runner_executions"].get("runner_executions", [])),
            "event_count": len(docs["events"].get("events", [])),
            "runtime_count": len(docs["runtimes"].get("runtime_instances", [])),
            "agent_count": agent_count,
            "permission_grant_count": 0,
            "remaining_qualification_gaps": [
                "no attributable authorized environment collector exists",
                "the environment evidence capture remains pending and unperformed",
                "OS, Python, dependency, configuration, and hardware facts are absent",
                "dependency, configuration, and aggregate environment digests are absent",
                "environment collection evidence is absent",
                "qualification environment evidence remains empty",
                "all six qualification criteria remain pending",
                "the shared environment lock remains pending and unfrozen",
                "no in-scope verifier has issued an environment-qualification decision",
                "no Runner or Runner scope exists",
                "Executor, capture, and experiment authorizations remain pending",
            ],
            "authority_effect": "none",
        },
    }


def load_inputs(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = root / "registry"
    paths = {
        "ecological_environments": registry / "environments.yaml",
        "environment_identities": registry / "environment-identities.yaml",
        "runner_environments": registry / "runner-environments.yaml",
        "capture_collectors": registry / "capture-collectors.yaml",
        "captures": registry / "environment-evidence-captures.yaml",
        "facts": registry / "environment-facts.yaml",
        "digests": registry / "environment-digests.yaml",
        "collection_evidence": registry / "environment-collection-evidence.yaml",
        "qualification_evidence": registry / "environment-evidence.yaml",
        "qualifications": registry / "environment-qualifications.yaml",
        "environment_locks": registry / "environment-locks.yaml",
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
        "capture_constitution": root / "constitution" / "environment-evidence-capture-constitution.yaml",
        "qualification_constitution": root / "constitution" / "environment-qualification-constitution.yaml",
        "evolution_ledger": root / "evolution" / "evolution-ledger.yaml",
    }
    texts = {name: path.read_text(encoding="utf-8") for name, path in text_paths.items()}
    return docs, texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DBOS v0.1 Environment Evidence Capture governance")
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
            "validator": "environment_evidence_capture_validator",
            "schema_version": "0.1",
            "errors": [str(exc)],
            "summary": {},
        }
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif result["status"] == "PASS":
        summary = result["summary"]
        print(
            "PASS environment_evidence_capture_validator: "
            f"environments={summary['environment_count']}, captures={summary['capture_count']}, "
            f"facts={summary['fact_count']}, digests={summary['digest_count']}, "
            f"evidence={summary['collection_evidence_count']}"
        )
    else:
        print("FAIL environment_evidence_capture_validator", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
