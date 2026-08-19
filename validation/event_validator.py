#!/usr/bin/env python3
"""Validate the Digital Biosphere Event Layer without third-party packages.

Agent-readable contract:
- Eight event types are vocabulary definitions, not occurrences or handlers.
- The v0.1 event and event-observation registries are empty.
- Each canonical entity has one defined, inactive, append-only event stream.
- Events require identity, type, timestamp, source, and evidence linkage.
- Event structure never grants capability, permission, governance authority,
  runtime, Agent, organism status, fitness, evolution, or C/E/V promotion.
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

EVENT_TYPES = (
    "identity_event",
    "capability_event",
    "evidence_event",
    "verification_event",
    "resource_event",
    "execution_event",
    "evolution_event",
    "governance_event",
)
EVENT_STATUSES = ("recorded", "validated", "invalidated", "superseded", "revoked")
STREAM_STATUSES = ("defined", "active", "suspended", "retired")
RETENTION_POLICY = "append_only_until_explicit_retirement_policy"
REQUIRED_TYPE_FIELDS = {
    "event_type",
    "description",
    "minimum_linkage",
    "state_effect",
    "authority_effect",
}
REQUIRED_EVENT_FIELDS = {
    "event_id",
    "entity_id",
    "event_type",
    "timestamp",
    "source",
    "input_ref",
    "output_ref",
    "resource_ref",
    "evidence_ref",
    "status",
}
REQUIRED_STREAM_FIELDS = {
    "stream_id",
    "entity_id",
    "event_types",
    "retention",
    "status",
}
REQUIRED_OBSERVATION_FIELDS = {
    "observation_id",
    "event_id",
    "metric",
    "value",
    "timestamp",
}
EVENT_ID_RE = re.compile(r"^dbio:event:([a-z0-9][a-z0-9.-]*):[0-9]{3}$")
STREAM_ID_RE = re.compile(
    r"^dbio://event-stream/([a-z0-9][a-z0-9.-]*)/v[0-9][A-Za-z0-9._-]*$"
)
OBSERVATION_ID_RE = re.compile(
    r"^dbio:event-observation:([a-z0-9][a-z0-9.-]*):[0-9]{3}$"
)
TYPE_SPECIFIC_LINKAGE = {
    "resource_event": ("resource_ref",),
    "execution_event": ("input_ref", "output_ref"),
    "evolution_event": ("output_ref",),
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


def reject_authority_fields(
    record: dict[str, Any], where: str, errors: list[str]
) -> None:
    """Reject fields that would grant authority or create governed state."""
    present = FORBIDDEN_AUTHORITY_FIELDS & set(record)
    if present:
        errors.append(f"{where}: forbidden authority fields {sorted(present)}")


def require_zero_metadata(metadata: Any, label: str, errors: list[str]) -> None:
    """Require non-authorizing metadata counters to remain zero."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in (
        "permission_grant_count",
        "capability_effect_count",
        "c_e_v_level_change_count",
        "agent_created_count",
        "runtime_created_count",
        "organism_created_count",
        "fitness_effect_count",
        "evolution_effect_count",
        "observer_count",
    ):
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label}.{field} must remain zero")


def valid_timestamp(value: Any) -> bool:
    """Accept an explicit ISO 8601 timestamp with timezone."""
    if not isinstance(value, str) or not value:
        return False
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(
    docs: dict[str, dict[str, Any]],
    texts: dict[str, str],
    root: Path,
) -> dict[str, Any]:
    """Validate event taxonomy, empty fact state, streams, and boundaries."""
    type_doc = docs.get("event_types", {})
    event_doc = docs.get("events", {})
    stream_doc = docs.get("event_streams", {})
    observation_doc = docs.get("event_observations", {})
    entity_doc = docs.get("entities", {})
    capability_doc = docs.get("capabilities", {})
    claim_doc = docs.get("capability_claims", {})
    evidence_doc = docs.get("capability_evidence", {})
    verification_doc = docs.get("verification_records", {})
    runtime_doc = docs.get("runtime_instances", {})
    candidate_doc = docs.get("organism_candidates", {})
    ecological_doc = docs.get("ecological_entities", {})
    governance_binding_doc = docs.get("governance_bindings", {})
    governance_claim_doc = docs.get("governance_claims", {})
    governance_evidence_doc = docs.get("governance_evidence", {})
    governance_observation_doc = docs.get("governance_observations", {})
    mapping_doc = docs.get("evolution_mapping", {})

    errors: list[str] = []
    entity_by_id = index_records(
        entity_doc.get("entities"), "entity_id", "entities", errors
    )
    type_by_name = index_records(
        type_doc.get("event_types"), "event_type", "event_types", errors
    )
    if tuple(type_by_name) != EVENT_TYPES:
        errors.append("event types must preserve all eight ordered definitions")
    for event_type, record in type_by_name.items():
        missing = REQUIRED_TYPE_FIELDS - set(record)
        if missing:
            errors.append(f"{event_type}: missing type fields {sorted(missing)}")
        if not isinstance(record.get("description"), str) or not record.get(
            "description"
        ):
            errors.append(f"{event_type}: description must be non-empty")
        linkage = record.get("minimum_linkage")
        if not isinstance(linkage, list) or not {
            "entity_id",
            "source",
            "evidence_ref",
        }.issubset(linkage):
            errors.append(f"{event_type}: minimum linkage is incomplete")
        if record.get("authority_effect") != "none":
            errors.append(f"{event_type}: event type cannot create authority")
        if not isinstance(record.get("state_effect"), str) or not record.get(
            "state_effect", ""
        ).startswith("none"):
            errors.append(f"{event_type}: event type cannot create state automatically")
        reject_authority_fields(record, event_type, errors)
    type_meta = type_doc.get("metadata", {})
    if type_meta.get("event_type_count") != len(type_by_name):
        errors.append("event type metadata count mismatch")
    for field in (
        "authority_effect",
        "capability_effect",
        "permission_effect",
        "automatic_level_effect",
    ):
        if type_meta.get(field) != "none":
            errors.append(f"event type metadata {field} must remain none")

    streams = stream_doc.get("event_streams")
    stream_by_id = index_records(streams, "stream_id", "event_streams", errors)
    stream_by_entity: dict[str, dict[str, Any]] = {}
    stream_status_counts: Counter[str] = Counter()
    for stream_id, stream in stream_by_id.items():
        missing = REQUIRED_STREAM_FIELDS - set(stream)
        if missing:
            errors.append(f"{stream_id}: missing stream fields {sorted(missing)}")
        match = STREAM_ID_RE.match(stream_id)
        if not match:
            errors.append(f"{stream_id}: malformed stream_id")
        entity_id = stream.get("entity_id")
        if entity_id not in entity_by_id:
            errors.append(f"{stream_id}: unknown entity {entity_id!r}")
        if match and entity_id != match.group(1):
            errors.append(f"{stream_id}: entity_id does not match stream_id")
        if entity_id in stream_by_entity:
            errors.append(f"duplicate event stream for entity {entity_id!r}")
        elif isinstance(entity_id, str):
            stream_by_entity[entity_id] = stream
        event_types = stream.get("event_types")
        if (tuple(event_types) if isinstance(event_types, list) else ()) != EVENT_TYPES:
            errors.append(
                f"{stream_id}: stream event types must preserve all registered types"
            )
        status = stream.get("status")
        if status not in STREAM_STATUSES:
            errors.append(f"{stream_id}: invalid stream status {status!r}")
        else:
            stream_status_counts[status] += 1
        if status != "defined":
            errors.append(f"{stream_id}: v0.1 stream must remain defined and inactive")
        if stream.get("retention") != RETENTION_POLICY:
            errors.append(f"{stream_id}: stream retention must remain append-only")
        reject_authority_fields(stream, stream_id, errors)
    if set(stream_by_entity) != set(entity_by_id):
        errors.append(
            "every canonical entity must have exactly one defined event stream"
        )
    stream_meta = stream_doc.get("metadata", {})
    if stream_meta.get("stream_count") != len(stream_by_id):
        errors.append("event stream metadata count mismatch")
    if stream_meta.get("defined_stream_count") != stream_status_counts.get(
        "defined", 0
    ):
        errors.append("defined event stream metadata count mismatch")
    if stream_meta.get("active_stream_count") != stream_status_counts.get("active", 0):
        errors.append("active event stream metadata count mismatch")
    if stream_meta.get("streamed_event_count") != 0:
        errors.append("defined streams cannot claim streamed events")
    require_zero_metadata(stream_meta, "event stream", errors)

    events = event_doc.get("events")
    event_by_id = index_records(events, "event_id", "events", errors)
    event_status_counts: Counter[str] = Counter()
    for event_id, event in event_by_id.items():
        missing = REQUIRED_EVENT_FIELDS - set(event)
        if missing:
            errors.append(f"{event_id}: missing event fields {sorted(missing)}")
        match = EVENT_ID_RE.match(event_id)
        if not match:
            errors.append(f"{event_id}: malformed event_id")
        entity_id = event.get("entity_id")
        if entity_id not in entity_by_id:
            errors.append(f"{event_id}: unknown entity {entity_id!r}")
        if match and entity_id != match.group(1):
            errors.append(f"{event_id}: entity_id does not match event_id")
        if entity_id not in stream_by_entity:
            errors.append(f"{event_id}: entity has no event stream")
        event_type = event.get("event_type")
        if event_type not in type_by_name:
            errors.append(f"{event_id}: invalid event type {event_type!r}")
        if not valid_timestamp(event.get("timestamp")):
            errors.append(f"{event_id}: timestamp must be ISO 8601 with timezone")
        source = event.get("source")
        if not isinstance(source, dict) or not source:
            errors.append(f"{event_id}: source must be a non-empty mapping")
            source = {}
        for field in ("kind", "locator"):
            if not isinstance(source.get(field), str) or not source.get(field):
                errors.append(f"{event_id}: source.{field} must be a non-empty string")
        if not valid_timestamp(source.get("collected_at")):
            errors.append(
                f"{event_id}: source.collected_at must be ISO 8601 with timezone"
            )
        evidence_ref = event.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref:
            errors.append(f"{event_id}: evidence_ref must be non-empty")
        for field in ("input_ref", "output_ref", "resource_ref"):
            value = event.get(field)
            if value is not None and (not isinstance(value, str) or not value):
                errors.append(f"{event_id}: {field} must be null or a non-empty string")
        for field in TYPE_SPECIFIC_LINKAGE.get(event_type, ()):
            if not isinstance(event.get(field), str) or not event.get(field):
                errors.append(f"{event_id}: {event_type} requires {field}")
        status = event.get("status")
        if status not in EVENT_STATUSES:
            errors.append(f"{event_id}: invalid event status {status!r}")
        else:
            event_status_counts[status] += 1
        reject_authority_fields(event, event_id, errors)
    event_meta = event_doc.get("metadata", {})
    if event_meta.get("event_count") != len(event_by_id):
        errors.append("event metadata count mismatch")
    if event_meta.get("validated_event_count") != event_status_counts.get(
        "validated", 0
    ):
        errors.append("validated event metadata count mismatch")
    if event_meta.get("event_created_evidence_count") != 0:
        errors.append("events cannot create evidence automatically")
    require_zero_metadata(event_meta, "event", errors)
    if event_by_id:
        errors.append("v0.1 baseline must not fabricate factual events")

    observations = observation_doc.get("event_observations")
    observation_by_id = index_records(
        observations, "observation_id", "event_observations", errors
    )
    for observation_id, observation in observation_by_id.items():
        missing = REQUIRED_OBSERVATION_FIELDS - set(observation)
        if missing:
            errors.append(
                f"{observation_id}: missing observation fields {sorted(missing)}"
            )
        match = OBSERVATION_ID_RE.match(observation_id)
        if not match:
            errors.append(f"{observation_id}: malformed observation_id")
        event_id = observation.get("event_id")
        event = event_by_id.get(event_id)
        if event is None:
            errors.append(f"{observation_id}: unknown event {event_id!r}")
        elif match and event.get("entity_id") != match.group(1):
            errors.append(
                f"{observation_id}: observation entity does not match event entity"
            )
        if not isinstance(observation.get("metric"), str) or not observation.get(
            "metric"
        ):
            errors.append(f"{observation_id}: metric must be non-empty")
        if observation.get("value") is None:
            errors.append(f"{observation_id}: observation value cannot be null")
        if not valid_timestamp(observation.get("timestamp")):
            errors.append(f"{observation_id}: timestamp must be ISO 8601 with timezone")
        reject_authority_fields(observation, observation_id, errors)
    observation_meta = observation_doc.get("metadata", {})
    if observation_meta.get("observation_count") != len(observation_by_id):
        errors.append("event observation metadata count mismatch")
    require_zero_metadata(observation_meta, "event observation", errors)
    if observation_by_id:
        errors.append("v0.1 baseline must not fabricate event observations")

    mappings = mapping_doc.get("mappings")
    mapping_by_layer = index_records(mappings, "layer", "SAEE mappings", errors)
    event_mapping = mapping_by_layer.get("Event")
    expected_event_mapping = {
        "current_authority": "constitution/event-constitution.yaml",
        "current_registry": "registry/events.yaml",
        "saee_correspondence": "observation substrate for evolution",
        "status": "defined_event_model_no_events",
        "authority_effect": "none",
    }
    if event_mapping is None:
        errors.append("SAEE mapping must include Event -> Observation -> Evolution")
    else:
        for field, expected in expected_event_mapping.items():
            if event_mapping.get(field) != expected:
                errors.append(f"Event SAEE mapping {field} mismatch")
        function = event_mapping.get("ecological_function")
        if (
            not isinstance(function, str)
            or "observation" not in function
            or "evolution" not in function
        ):
            errors.append(
                "Event SAEE mapping must describe observation and evolution boundaries"
            )
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mapping_by_layer):
        errors.append("SAEE mapping metadata count mismatch")

    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("event layer must not create a capability")
        capabilities = []
    claims = claim_doc.get("claims")
    if not isinstance(claims, list):
        errors.append("capability claims must be a list")
        claims = []
    for claim in claims:
        if (
            not isinstance(claim, dict)
            or claim.get("maturity_level") != "C1"
            or claim.get("status") != "pending"
        ):
            errors.append("event layer must preserve capability claims at C1/pending")
            break
    evidence_records = evidence_doc.get("evidence")
    if not isinstance(evidence_records, list):
        errors.append("capability evidence must be a list")
        evidence_records = []
    for evidence in evidence_records:
        if (
            not isinstance(evidence, dict)
            or evidence.get("evidence_type") != "E1"
            or evidence.get("status") != "pending"
        ):
            errors.append("event layer must preserve capability evidence at E1/pending")
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
            errors.append("event layer must preserve verification at V0/pending")
            break
    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("event layer must not create a runtime")
        runtimes = []
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("event layer must not create an organism candidate")
        candidates = []
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological entities must be a list")
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
            errors.append("event layer cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("event layer cannot change evolution stage")
        if (
            ecological_entity.get("fitness_status") != "unknown"
            or ecological_entity.get("fitness_score") is not None
        ):
            errors.append("event layer cannot calculate fitness")
    governance_bindings = governance_binding_doc.get("governance_bindings")
    if not isinstance(governance_bindings, list) or governance_bindings:
        errors.append("event layer cannot create governance bindings")
        governance_bindings = []
    governance_claims = governance_claim_doc.get("governance_claims")
    if not isinstance(governance_claims, list) or governance_claims:
        errors.append("event layer cannot create governance claims")
        governance_claims = []
    governance_evidence = governance_evidence_doc.get("governance_evidence")
    if not isinstance(governance_evidence, list) or governance_evidence:
        errors.append("event layer cannot create governance evidence")
        governance_evidence = []
    governance_observations = governance_observation_doc.get("governance_observations")
    if not isinstance(governance_observations, list):
        errors.append("governance observations must be a list")
        governance_observations = []
    for observation in governance_observations:
        if (
            not isinstance(observation, dict)
            or observation.get("governance_dimension") != "unknown"
            or observation.get("value") is not None
            or observation.get("timestamp") is not None
            or observation.get("status") != "unobserved"
        ):
            errors.append("event layer cannot populate governance observations")
            break
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("event layer must not create an Agent entity")

    event_constitution = root / "constitution" / "event-constitution.yaml"
    if not event_constitution.is_file():
        errors.append("event constitution does not exist")

    return {
        "status": "FAIL" if errors else "PASS",
        "event_type_count": len(type_by_name),
        "event_count": len(event_by_id),
        "event_status_distribution": {
            status: event_status_counts.get(status, 0) for status in EVENT_STATUSES
        },
        "event_stream_count": len(stream_by_id),
        "stream_status_distribution": {
            status: stream_status_counts.get(status, 0) for status in STREAM_STATUSES
        },
        "event_observation_count": len(observation_by_id),
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
    parser.add_argument(
        "--event-types", type=Path, default=root / "registry" / "event-types.yaml"
    )
    parser.add_argument(
        "--events", type=Path, default=root / "registry" / "events.yaml"
    )
    parser.add_argument(
        "--streams", type=Path, default=root / "registry" / "event-streams.yaml"
    )
    parser.add_argument(
        "--observations",
        type=Path,
        default=root / "registry" / "event-observations.yaml",
    )
    parser.add_argument(
        "--entities", type=Path, default=root / "registry" / "entities.yaml"
    )
    parser.add_argument(
        "--capabilities", type=Path, default=root / "registry" / "capabilities.yaml"
    )
    parser.add_argument(
        "--claims", type=Path, default=root / "registry" / "capability-claims.yaml"
    )
    parser.add_argument(
        "--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml"
    )
    parser.add_argument(
        "--verification",
        type=Path,
        default=root / "registry" / "verification-records.yaml",
    )
    parser.add_argument(
        "--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml"
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=root / "registry" / "organism-candidates.yaml",
    )
    parser.add_argument(
        "--ecological",
        type=Path,
        default=root / "registry" / "ecological-entities.yaml",
    )
    parser.add_argument(
        "--governance-bindings",
        type=Path,
        default=root / "registry" / "governance-bindings.yaml",
    )
    parser.add_argument(
        "--governance-claims",
        type=Path,
        default=root / "registry" / "governance-claims.yaml",
    )
    parser.add_argument(
        "--governance-evidence",
        type=Path,
        default=root / "registry" / "governance-evidence.yaml",
    )
    parser.add_argument(
        "--governance-observations",
        type=Path,
        default=root / "registry" / "governance-observations.yaml",
    )
    parser.add_argument(
        "--mapping", type=Path, default=root / "registry" / "evolution-mapping.yaml"
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    from execution_chain_compat import delegate_if_advanced

    delegated = delegate_if_advanced(root, args.format)
    if delegated is not None:
        return delegated
    try:
        docs = {
            "event_types": load_json_yaml(args.event_types),
            "events": load_json_yaml(args.events),
            "event_streams": load_json_yaml(args.streams),
            "event_observations": load_json_yaml(args.observations),
            "entities": load_json_yaml(args.entities),
            "capabilities": load_json_yaml(args.capabilities),
            "capability_claims": load_json_yaml(args.claims),
            "capability_evidence": load_json_yaml(args.evidence),
            "verification_records": load_json_yaml(args.verification),
            "runtime_instances": load_json_yaml(args.runtimes),
            "organism_candidates": load_json_yaml(args.candidates),
            "ecological_entities": load_json_yaml(args.ecological),
            "governance_bindings": load_json_yaml(args.governance_bindings),
            "governance_claims": load_json_yaml(args.governance_claims),
            "governance_evidence": load_json_yaml(args.governance_evidence),
            "governance_observations": load_json_yaml(args.governance_observations),
            "evolution_mapping": load_json_yaml(args.mapping),
        }
        result = validate(docs, {}, root)
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"EVENT_VALIDATION: {result['status']}")
        print(f"event_types={result.get('event_type_count', 0)}")
        print(f"events={result.get('event_count', 0)}")
        print(f"streams={result.get('event_stream_count', 0)}")
        print(f"observations={result.get('event_observation_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
