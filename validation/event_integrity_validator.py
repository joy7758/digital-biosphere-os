#!/usr/bin/env python3
"""Validate the Event Integrity Layer without third-party packages.

Agent-readable contract:
- The v0.1 integrity and witness registries contain no factual records.
- Twenty-three ordering rules cover the twenty-three defined event streams.
- Five integrity checks are definitions and have no completed runs.
- Missing hashes, predecessor linkage, checks, provenance, or witnesses cannot
  produce verified integrity.
- Witness type never grants trust automatically.
- PASS creates no event, Agent, runtime, organism, capability, permission,
  trust, evidence maturity, fitness, evolution result, or C/E/V promotion.
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

INTEGRITY_STATUSES = (
    "pending",
    "structurally_valid",
    "verified",
    "invalid",
    "chain_broken",
    "revoked",
)
WITNESS_TYPES = ("self", "automated", "external")
TRUST_LEVELS = (
    "unknown",
    "local_structural",
    "identity_verified",
    "independent_verified",
    "revoked",
)
CHECK_IDS = (
    "hash_validation",
    "sequence_validation",
    "source_validation",
    "timestamp_validation",
    "witness_validation",
)
ORDERING_METHOD = "sequence_ordering_with_hash_chaining"
CLOCK_MODEL = "event_occurrence_time_plus_integrity_record_time_no_global_total_order"
DEDUPLICATION_RULE = "reject_duplicate_event_id_current_hash_or_stream_sequence"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
WITNESS_ID_RE = re.compile(
    r"^dbio://event-witness/[a-z0-9][a-z0-9.-]*/v[0-9][A-Za-z0-9._-]*$"
)
REQUIRED_INTEGRITY_FIELDS = {
    "event_id",
    "stream_id",
    "sequence",
    "previous_hash",
    "current_hash",
    "timestamp",
    "clock_source",
    "integrity_status",
}
REQUIRED_WITNESS_FIELDS = {
    "witness_id",
    "witness_type",
    "identity_ref",
    "verification_method",
    "trust_level",
}
REQUIRED_ORDERING_FIELDS = {
    "stream_id",
    "ordering_method",
    "clock_model",
    "deduplication_rule",
}
REQUIRED_CHECK_FIELDS = {
    "check_id",
    "description",
    "required_inputs",
    "pass_condition",
    "failure_status",
    "authority_effect",
}
FORBIDDEN_AUTHORITY_FIELDS = {
    "permission",
    "permissions",
    "permission_status",
    "permission_grant",
    "permission_grants",
    "capability_id",
    "capabilities",
    "assigned_capabilities",
    "capability_assignment_status",
    "agent_id",
    "runtime_id",
    "candidate_id",
    "digital_organism_id",
    "governance_authority",
    "authority_grant",
    "fitness_score",
    "selection_result",
    "created_event",
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


def reject_authority_fields(record: dict[str, Any], where: str, errors: list[str]) -> None:
    """Reject fields that create events, authority, capability, or permission."""
    present = FORBIDDEN_AUTHORITY_FIELDS & set(record)
    if present:
        errors.append(f"{where}: forbidden authority fields {sorted(present)}")


def require_zero_metadata(metadata: Any, label: str, errors: list[str]) -> None:
    """Require all non-authorizing effect counts to remain zero."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in (
        "event_created_count",
        "trust_grant_count",
        "permission_grant_count",
        "capability_effect_count",
        "c_e_v_level_change_count",
        "agent_created_count",
        "runtime_created_count",
        "organism_created_count",
        "pass_count",
        "fail_count",
        "ordered_event_count",
        "duplicate_event_count",
        "chain_break_count",
    ):
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label}.{field} must remain zero")


def valid_timestamp(value: Any) -> bool:
    """Accept an explicit ISO 8601 timestamp with timezone."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(
    integrity_doc: dict[str, Any],
    witness_doc: dict[str, Any],
    ordering_doc: dict[str, Any],
    check_doc: dict[str, Any],
    event_doc: dict[str, Any],
    stream_doc: dict[str, Any],
    observation_doc: dict[str, Any],
    entity_doc: dict[str, Any],
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
    """Validate integrity identity, chains, witnesses, checks, and boundaries."""
    errors: list[str] = []
    entity_by_id = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    event_by_id = index_records(event_doc.get("events"), "event_id", "events", errors)
    stream_by_id = index_records(
        stream_doc.get("event_streams"), "stream_id", "event_streams", errors
    )
    observation_by_id = index_records(
        observation_doc.get("event_observations"),
        "observation_id",
        "event_observations",
        errors,
    )

    witness_type_definitions = index_records(
        witness_doc.get("witness_type_definitions"),
        "witness_type",
        "witness_type_definitions",
        errors,
    )
    if tuple(witness_type_definitions) != WITNESS_TYPES:
        errors.append("witness types must preserve self, automated, external order")
    for witness_type, definition in witness_type_definitions.items():
        if not isinstance(definition.get("description"), str) or not definition.get("description"):
            errors.append(f"{witness_type}: witness type description must be non-empty")
        if definition.get("automatic_trust_effect") != "none":
            errors.append(f"{witness_type}: witness type cannot grant trust automatically")
        reject_authority_fields(definition, witness_type, errors)

    witness_by_id = index_records(
        witness_doc.get("event_witnesses"), "witness_id", "event_witnesses", errors
    )
    witness_type_counts: Counter[str] = Counter()
    trusted_witness_count = 0
    independent_witness_count = 0
    for witness_id, witness in witness_by_id.items():
        missing = REQUIRED_WITNESS_FIELDS - set(witness)
        if missing:
            errors.append(f"{witness_id}: missing witness fields {sorted(missing)}")
        if not WITNESS_ID_RE.match(witness_id):
            errors.append(f"{witness_id}: malformed witness_id")
        witness_type = witness.get("witness_type")
        if witness_type not in WITNESS_TYPES:
            errors.append(f"{witness_id}: invalid witness type {witness_type!r}")
        else:
            witness_type_counts[witness_type] += 1
        if not isinstance(witness.get("identity_ref"), str) or not witness.get("identity_ref"):
            errors.append(f"{witness_id}: identity_ref must be non-empty")
        if not isinstance(witness.get("verification_method"), str) or not witness.get("verification_method"):
            errors.append(f"{witness_id}: verification_method must be non-empty")
        trust_level = witness.get("trust_level")
        if trust_level not in TRUST_LEVELS:
            errors.append(f"{witness_id}: invalid trust level {trust_level!r}")
        if trust_level not in {"unknown", "revoked"}:
            trusted_witness_count += 1
        if witness_type == "self" and trust_level in {"local_structural", "independent_verified"}:
            errors.append(f"{witness_id}: self witness cannot establish structural or independent trust")
        if witness_type == "automated" and trust_level == "independent_verified":
            errors.append(f"{witness_id}: automated type cannot establish independence automatically")
        if trust_level == "independent_verified":
            independent_witness_count += 1
            for field in ("independence_evidence", "conflict_of_interest", "limitations"):
                if not witness.get(field):
                    errors.append(f"{witness_id}: independent trust missing {field}")
        reject_authority_fields(witness, witness_id, errors)
    witness_meta = witness_doc.get("metadata", {})
    if witness_meta.get("witness_type_definition_count") != len(witness_type_definitions):
        errors.append("witness type definition metadata count mismatch")
    if witness_meta.get("witness_count") != len(witness_by_id):
        errors.append("witness metadata count mismatch")
    for witness_type in WITNESS_TYPES:
        if witness_meta.get("witness_type_distribution", {}).get(witness_type) != witness_type_counts.get(witness_type, 0):
            errors.append(f"witness type distribution mismatch for {witness_type}")
    if witness_meta.get("trusted_witness_count") != trusted_witness_count:
        errors.append("trusted witness metadata count mismatch")
    if witness_meta.get("independent_witness_count") != independent_witness_count:
        errors.append("independent witness metadata count mismatch")
    require_zero_metadata(witness_meta, "witness", errors)
    if witness_by_id:
        errors.append("v0.1 baseline must not fabricate event witnesses")

    ordering_rules = ordering_doc.get("event_ordering_rules")
    ordering_by_stream = index_records(
        ordering_rules, "stream_id", "event_ordering_rules", errors
    )
    for stream_id, rule in ordering_by_stream.items():
        missing = REQUIRED_ORDERING_FIELDS - set(rule)
        if missing:
            errors.append(f"{stream_id}: missing ordering fields {sorted(missing)}")
        if stream_id not in stream_by_id:
            errors.append(f"{stream_id}: ordering rule references unknown stream")
        if rule.get("ordering_method") != ORDERING_METHOD:
            errors.append(f"{stream_id}: ordering method mismatch")
        if rule.get("clock_model") != CLOCK_MODEL:
            errors.append(f"{stream_id}: clock model mismatch")
        if rule.get("deduplication_rule") != DEDUPLICATION_RULE:
            errors.append(f"{stream_id}: deduplication rule mismatch")
        reject_authority_fields(rule, stream_id, errors)
    if set(ordering_by_stream) != set(stream_by_id):
        errors.append("every defined event stream must have exactly one ordering rule")
    ordering_meta = ordering_doc.get("metadata", {})
    if ordering_meta.get("ordering_rule_count") != len(ordering_by_stream):
        errors.append("ordering rule metadata count mismatch")
    if ordering_meta.get("covered_stream_count") != len(stream_by_id):
        errors.append("ordering covered-stream metadata count mismatch")
    if ordering_meta.get("global_total_order_defined") is not False:
        errors.append("event ordering cannot claim a global total order")
    if ordering_meta.get("authority_effect") != "none":
        errors.append("event ordering cannot create authority")
    require_zero_metadata(ordering_meta, "ordering", errors)

    check_by_id = index_records(
        check_doc.get("check_definitions"), "check_id", "check_definitions", errors
    )
    if tuple(check_by_id) != CHECK_IDS:
        errors.append("integrity checks must preserve all five ordered definitions")
    for check_id, check in check_by_id.items():
        missing = REQUIRED_CHECK_FIELDS - set(check)
        if missing:
            errors.append(f"{check_id}: missing check fields {sorted(missing)}")
        if not isinstance(check.get("description"), str) or not check.get("description"):
            errors.append(f"{check_id}: description must be non-empty")
        if not isinstance(check.get("required_inputs"), list) or not check.get("required_inputs"):
            errors.append(f"{check_id}: required_inputs must be non-empty")
        if not isinstance(check.get("pass_condition"), str) or not check.get("pass_condition"):
            errors.append(f"{check_id}: pass_condition must be non-empty")
        if check.get("authority_effect") != "none":
            errors.append(f"{check_id}: integrity check cannot create authority")
        reject_authority_fields(check, check_id, errors)
    check_runs = check_doc.get("check_runs")
    if not isinstance(check_runs, list):
        errors.append("check_runs must be a list")
        check_runs = []
    if check_runs:
        errors.append("v0.1 baseline must not fabricate integrity check runs")
    check_meta = check_doc.get("metadata", {})
    if check_meta.get("check_definition_count") != len(check_by_id):
        errors.append("integrity check definition metadata count mismatch")
    if check_meta.get("check_run_count") != len(check_runs):
        errors.append("integrity check run metadata count mismatch")
    require_zero_metadata(check_meta, "integrity check", errors)

    integrity_records = integrity_doc.get("event_integrity_records")
    integrity_by_event = index_records(
        integrity_records, "event_id", "event_integrity_records", errors
    )
    integrity_status_counts: Counter[str] = Counter()
    position_seen: set[tuple[str, int]] = set()
    hash_seen: set[str] = set()
    records_by_stream: dict[str, list[dict[str, Any]]] = {}
    for event_id, record in integrity_by_event.items():
        missing = REQUIRED_INTEGRITY_FIELDS - set(record)
        if missing:
            errors.append(f"{event_id}: missing integrity fields {sorted(missing)}")
        event = event_by_id.get(event_id)
        if event is None:
            errors.append(f"{event_id}: integrity record references unknown event")
        stream_id = record.get("stream_id")
        stream = stream_by_id.get(stream_id)
        if stream is None:
            errors.append(f"{event_id}: integrity record references unknown stream {stream_id!r}")
        elif event is not None and stream.get("entity_id") != event.get("entity_id"):
            errors.append(f"{event_id}: event and stream entity mismatch")
        sequence = record.get("sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            errors.append(f"{event_id}: sequence must be a positive integer")
        elif isinstance(stream_id, str):
            position = (stream_id, sequence)
            if position in position_seen:
                errors.append(f"{event_id}: duplicate stream sequence {position}")
            position_seen.add(position)
            records_by_stream.setdefault(stream_id, []).append(record)
        status = record.get("integrity_status")
        if status not in INTEGRITY_STATUSES:
            errors.append(f"{event_id}: invalid integrity status {status!r}")
        else:
            integrity_status_counts[status] += 1
        current_hash = record.get("current_hash")
        previous_hash = record.get("previous_hash")
        if current_hash is not None:
            if not isinstance(current_hash, str) or not HASH_RE.match(current_hash):
                errors.append(f"{event_id}: malformed current_hash")
            elif current_hash in hash_seen:
                errors.append(f"{event_id}: duplicate current_hash")
            else:
                hash_seen.add(current_hash)
        if status in {"structurally_valid", "verified"} and not (
            isinstance(current_hash, str) and HASH_RE.match(current_hash)
        ):
            errors.append(f"{event_id}: {status} requires current_hash")
        if sequence == 1 and previous_hash is not None:
            errors.append(f"{event_id}: sequence 1 requires previous_hash=null")
        if isinstance(sequence, int) and sequence > 1 and status in {"structurally_valid", "verified"}:
            if not isinstance(previous_hash, str) or not HASH_RE.match(previous_hash):
                errors.append(f"{event_id}: sequence greater than 1 requires a valid previous_hash")
        if not valid_timestamp(record.get("timestamp")):
            errors.append(f"{event_id}: integrity timestamp must be ISO 8601 with timezone")
        if not isinstance(record.get("clock_source"), str) or not record.get("clock_source"):
            errors.append(f"{event_id}: clock_source must be non-empty")
        witness_refs = record.get("witness_refs", [])
        if not isinstance(witness_refs, list):
            errors.append(f"{event_id}: witness_refs must be a list")
            witness_refs = []
        unknown_witnesses = sorted(set(witness_refs) - set(witness_by_id))
        if unknown_witnesses:
            errors.append(f"{event_id}: unknown witness references {unknown_witnesses}")
        check_results = record.get("check_results", {})
        if not isinstance(check_results, dict):
            errors.append(f"{event_id}: check_results must be a mapping")
            check_results = {}
        if status == "verified":
            if not witness_refs:
                errors.append(f"{event_id}: verified integrity requires witness_refs")
            if set(check_results) != set(CHECK_IDS):
                errors.append(f"{event_id}: verified integrity requires all five check results")
            for check_id in CHECK_IDS:
                result = check_results.get(check_id)
                if not isinstance(result, dict) or result.get("status") != "pass":
                    errors.append(f"{event_id}: verified integrity requires {check_id}=pass")
        reject_authority_fields(record, event_id, errors)

    for stream_id, records in records_by_stream.items():
        ordered = sorted(records, key=lambda record: record["sequence"])
        for index, record in enumerate(ordered):
            expected_sequence = index + 1
            if record.get("sequence") != expected_sequence:
                errors.append(f"{stream_id}: integrity sequence is not contiguous from 1")
            if index > 0 and record.get("previous_hash") != ordered[index - 1].get("current_hash"):
                errors.append(f"{stream_id}: previous_hash does not match prior current_hash")

    integrity_meta = integrity_doc.get("metadata", {})
    if integrity_meta.get("integrity_schema_count") != 1:
        errors.append("integrity schema count must remain one")
    if integrity_meta.get("integrity_record_count") != len(integrity_by_event):
        errors.append("integrity record metadata count mismatch")
    for status in INTEGRITY_STATUSES:
        if integrity_meta.get("integrity_status_distribution", {}).get(status) != integrity_status_counts.get(status, 0):
            errors.append(f"integrity status distribution mismatch for {status}")
    require_zero_metadata(integrity_meta, "event integrity", errors)
    if integrity_by_event:
        errors.append("v0.1 baseline must not fabricate event integrity records")

    mappings = mapping_doc.get("mappings")
    mapping_by_layer = index_records(mappings, "layer", "SAEE mappings", errors)
    integrity_mapping = mapping_by_layer.get("Event Integrity")
    expected_mapping = {
        "current_authority": "constitution/event-integrity-constitution.yaml",
        "current_registry": "registry/event-integrity.yaml",
        "saee_correspondence": "evidence reliability",
        "status": "defined_integrity_model_no_records",
        "authority_effect": "none",
    }
    if integrity_mapping is None:
        errors.append("SAEE mapping must include Event Integrity -> Evidence Reliability")
    else:
        for field, expected in expected_mapping.items():
            if integrity_mapping.get(field) != expected:
                errors.append(f"Event Integrity SAEE mapping {field} mismatch")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mapping_by_layer):
        errors.append("SAEE mapping metadata count mismatch")

    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("event integrity must not create a capability")
        capabilities = []
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("capability claims must be a list")
        claims = []
    for claim in claims:
        if not isinstance(claim, dict) or claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("event integrity must preserve capability claims at C1/pending")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("capability evidence must be a list")
        evidence_records = []
    for evidence in evidence_records:
        if not isinstance(evidence, dict) or evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("event integrity must preserve capability evidence at E1/pending")
            break
    verification_records = verification_doc.get("verification_records")
    if not isinstance(verification_records, list):
        errors.append("verification records must be a list")
        verification_records = []
    for verification in verification_records:
        if (
            not isinstance(verification, dict)
            or verification.get("verification_level") != "V0"
            or verification.get("status") != "pending"
            or verification.get("decision") != "pending"
        ):
            errors.append("event integrity must preserve verification at V0/pending")
            break
    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("event integrity must not create a runtime")
        runtimes = []
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("event integrity must not create an organism candidate")
        candidates = []
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("event integrity cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("event integrity cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("event integrity cannot calculate fitness")
    if event_by_id:
        errors.append("event integrity layer baseline must not create factual events")
    if observation_by_id:
        errors.append("event integrity layer baseline must not create event observations")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("event integrity must not create an Agent entity")

    event_constitution = root / "constitution" / "event-constitution.yaml"
    integrity_constitution = root / "constitution" / "event-integrity-constitution.yaml"
    if not integrity_constitution.is_file():
        errors.append("event integrity constitution does not exist")
    if not event_constitution.is_file():
        errors.append("event constitution does not exist")
    else:
        text = event_constitution.read_text(encoding="utf-8")
        if 'event_integrity_constitution: "event-integrity-constitution.yaml"' not in text:
            errors.append("event constitution does not reference event integrity constitution")
        for token in (
            'integrity_registry: "../registry/event-integrity.yaml"',
            'witness_registry: "../registry/event-witnesses.yaml"',
            'ordering_registry: "../registry/event-ordering.yaml"',
            'check_registry: "../registry/event-integrity-checks.yaml"',
        ):
            if token not in text:
                errors.append(f"event constitution integrity reference missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "integrity_schema_count": integrity_meta.get("integrity_schema_count", 0),
        "integrity_record_count": len(integrity_by_event),
        "integrity_status_distribution": {
            status: integrity_status_counts.get(status, 0) for status in INTEGRITY_STATUSES
        },
        "witness_count": len(witness_by_id),
        "witness_type_distribution": {
            witness_type: witness_type_counts.get(witness_type, 0)
            for witness_type in WITNESS_TYPES
        },
        "ordering_rule_count": len(ordering_by_stream),
        "integrity_check_definition_count": len(check_by_id),
        "integrity_check_run_count": len(check_runs),
        "event_count": len(event_by_id),
        "event_observation_count": len(observation_by_id),
        "capability_count": len(capabilities),
        "permission_grant_count": 0,
        "trust_grant_count": 0,
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
    parser.add_argument("--integrity", type=Path, default=root / "registry" / "event-integrity.yaml")
    parser.add_argument("--witnesses", type=Path, default=root / "registry" / "event-witnesses.yaml")
    parser.add_argument("--ordering", type=Path, default=root / "registry" / "event-ordering.yaml")
    parser.add_argument("--checks", type=Path, default=root / "registry" / "event-integrity-checks.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--streams", type=Path, default=root / "registry" / "event-streams.yaml")
    parser.add_argument("--observations", type=Path, default=root / "registry" / "event-observations.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
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
            load_json_yaml(args.integrity),
            load_json_yaml(args.witnesses),
            load_json_yaml(args.ordering),
            load_json_yaml(args.checks),
            load_json_yaml(args.events),
            load_json_yaml(args.streams),
            load_json_yaml(args.observations),
            load_json_yaml(args.entities),
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
        print(f"EVENT_INTEGRITY_VALIDATION: {result['status']}")
        print(f"integrity_schema={result.get('integrity_schema_count', 0)}")
        print(f"integrity_records={result.get('integrity_record_count', 0)}")
        print(f"witnesses={result.get('witness_count', 0)}")
        print(f"ordering_rules={result.get('ordering_rule_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
