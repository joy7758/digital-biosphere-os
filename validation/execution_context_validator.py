#!/usr/bin/env python3
"""Validate the Event Execution Context Layer without third-party packages.

Agent-readable contract:
- Context identity binds an existing entity to an existing declared environment.
- Configuration and snapshot digests use sha256:<64 lowercase hex>.
- Input and output snapshots belong to exactly one existing context.
- Dependency identity is composite(context_id, dependency), and every context
  dependency_refs list exactly matches its recorded dependency names.
- Structural validity does not prove execution occurrence or reproducibility.
- Context, digest, snapshot, dependency, or reproducibility language never creates
  an event, runtime, Agent, organism, capability, permission, or C/E/V promotion.
- The v0.1 context, snapshot, and dependency registries remain empty.
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

CONTEXT_STATUSES = (
    "proposed",
    "recorded",
    "validated",
    "invalid",
    "revoked",
    "superseded",
)
CONTEXT_ID_RE = re.compile(
    r"^dbio:execution-context:([a-z0-9][a-z0-9._-]*):([1-9][0-9]*)$"
)
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
REQUIRED_CONTEXT_FIELDS = {
    "context_id",
    "entity_id",
    "environment_ref",
    "software_version",
    "configuration_digest",
    "dependency_refs",
    "status",
}
REQUIRED_INPUT_FIELDS = {"snapshot_id", "context_id", "input_ref", "hash", "timestamp"}
REQUIRED_OUTPUT_FIELDS = {"snapshot_id", "context_id", "output_ref", "hash", "timestamp"}
REQUIRED_DEPENDENCY_FIELDS = {"context_id", "dependency", "version", "source"}
FORBIDDEN_AUTHORITY_KEYS = {
    "agent_id",
    "agent_created",
    "runtime_id",
    "runtime_created",
    "organism_id",
    "organism_created",
    "capability_id",
    "capability_assignment",
    "capability_assignment_status",
    "permission",
    "permissions",
    "permission_grant",
    "permission_status",
    "fitness_score",
    "maturity_level",
    "evidence_level",
    "verification_level",
}
ZERO_EFFECT_FIELDS = (
    "event_created_count",
    "runtime_created_count",
    "agent_created_count",
    "organism_created_count",
    "capability_effect_count",
    "permission_grant_count",
    "c_e_v_level_change_count",
    "evidence_created_count",
    "installation_authority_count",
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


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and DIGEST_RE.fullmatch(value) is not None


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
        errors.append(f"{label}: execution context cannot create authority fields {present}")


def require_zero_effect_metadata(metadata: Any, label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in ZERO_EFFECT_FIELDS:
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def validate_snapshot_id(snapshot_id: str, kind: str, context_id: Any) -> bool:
    if not isinstance(context_id, str):
        return False
    prefix = f"dbio:snapshot:{kind}:{context_id}:"
    if not snapshot_id.startswith(prefix):
        return False
    sequence = snapshot_id[len(prefix):]
    return sequence.isdigit() and int(sequence) > 0 and not sequence.startswith("0")


def validate(
    context_doc: dict[str, Any],
    input_doc: dict[str, Any],
    output_doc: dict[str, Any],
    dependency_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    environment_doc: dict[str, Any],
    event_doc: dict[str, Any],
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
    """Validate empty execution-context registries and cross-layer boundaries."""
    errors: list[str] = []
    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    environments = index_records(
        environment_doc.get("environments"), "environment_id", "environments", errors
    )
    events = index_records(event_doc.get("events"), "event_id", "events", errors)
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

    contexts = index_records(
        context_doc.get("execution_contexts"),
        "context_id",
        "execution_contexts",
        errors,
    )
    context_status_counts: Counter[str] = Counter()
    for context_id, context in contexts.items():
        missing = REQUIRED_CONTEXT_FIELDS - set(context)
        if missing:
            errors.append(f"{context_id}: missing context fields {sorted(missing)}")
        match = CONTEXT_ID_RE.fullmatch(context_id)
        if match is None:
            errors.append(f"{context_id}: invalid context_id format")
        entity_id = context.get("entity_id")
        if entity_id not in entities:
            errors.append(f"{context_id}: context must reference an existing entity")
        elif match is not None and match.group(1) != entity_id:
            errors.append(f"{context_id}: context_id entity segment must match entity_id")
        environment_ref = context.get("environment_ref")
        if environment_ref not in environments:
            errors.append(f"{context_id}: context must reference an existing environment")
        if not nonempty_string(context.get("software_version")):
            errors.append(f"{context_id}: software_version must be non-empty")
        if not valid_digest(context.get("configuration_digest")):
            errors.append(f"{context_id}: configuration_digest must use sha256 lowercase format")
        dependency_refs = context.get("dependency_refs")
        if not isinstance(dependency_refs, list) or not all(
            nonempty_string(item) for item in dependency_refs
        ):
            errors.append(f"{context_id}: dependency_refs must be a string list")
        elif len(dependency_refs) != len(set(dependency_refs)):
            errors.append(f"{context_id}: dependency_refs must be unique within the context")
        status = context.get("status")
        if status not in CONTEXT_STATUSES:
            errors.append(f"{context_id}: invalid context status {status!r}")
        else:
            context_status_counts[status] += 1
        if status in {"recorded", "validated"} and not valid_timestamp(context.get("timestamp")):
            errors.append(f"{context_id}: {status} context requires timezone-aware timestamp")
        for field, kind in (
            ("input_snapshot_refs", "input"),
            ("output_snapshot_refs", "output"),
        ):
            refs = context.get(field, [])
            if not isinstance(refs, list) or not all(nonempty_string(item) for item in refs):
                errors.append(f"{context_id}: {field} must be a string list")
            elif len(refs) != len(set(refs)):
                errors.append(f"{context_id}: {field} must not contain duplicates")
        reproducibility = context.get("reproducibility")
        if reproducibility is not None:
            if not isinstance(reproducibility, dict):
                errors.append(f"{context_id}: reproducibility must be a mapping when present")
            elif reproducibility.get("status") == "reproduced":
                required = {"method", "evidence_refs", "verifier_ref", "limitations"}
                if not required.issubset(reproducibility):
                    errors.append(f"{context_id}: reproduced status requires method, evidence, verifier, and limitations")
                if not isinstance(reproducibility.get("evidence_refs"), list) or not reproducibility.get("evidence_refs"):
                    errors.append(f"{context_id}: reproduced status requires non-empty evidence_refs")
        reject_authority_fields(context, context_id, errors)

    input_snapshots = index_records(
        input_doc.get("input_snapshots"), "snapshot_id", "input_snapshots", errors
    )
    output_snapshots = index_records(
        output_doc.get("output_snapshots"), "snapshot_id", "output_snapshots", errors
    )
    duplicate_snapshot_ids = sorted(set(input_snapshots).intersection(output_snapshots))
    if duplicate_snapshot_ids:
        errors.append(f"snapshot_id must be unique across input and output registries: {duplicate_snapshot_ids}")

    input_by_context: dict[str, list[str]] = defaultdict(list)
    for snapshot_id, snapshot in input_snapshots.items():
        missing = REQUIRED_INPUT_FIELDS - set(snapshot)
        if missing:
            errors.append(f"{snapshot_id}: missing input snapshot fields {sorted(missing)}")
        context_id = snapshot.get("context_id")
        if context_id not in contexts:
            errors.append(f"{snapshot_id}: input snapshot must belong to an existing context")
        if not validate_snapshot_id(snapshot_id, "input", context_id):
            errors.append(f"{snapshot_id}: invalid input snapshot_id format or context binding")
        if not nonempty_string(snapshot.get("input_ref")):
            errors.append(f"{snapshot_id}: input_ref must be non-empty")
        if not valid_digest(snapshot.get("hash")):
            errors.append(f"{snapshot_id}: input snapshot hash must use sha256 lowercase format")
        if not valid_timestamp(snapshot.get("timestamp")):
            errors.append(f"{snapshot_id}: input snapshot timestamp must be timezone-aware")
        if isinstance(context_id, str):
            input_by_context[context_id].append(snapshot_id)
        reject_authority_fields(snapshot, snapshot_id, errors)

    output_by_context: dict[str, list[str]] = defaultdict(list)
    for snapshot_id, snapshot in output_snapshots.items():
        missing = REQUIRED_OUTPUT_FIELDS - set(snapshot)
        if missing:
            errors.append(f"{snapshot_id}: missing output snapshot fields {sorted(missing)}")
        context_id = snapshot.get("context_id")
        if context_id not in contexts:
            errors.append(f"{snapshot_id}: output snapshot must belong to an existing context")
        if not validate_snapshot_id(snapshot_id, "output", context_id):
            errors.append(f"{snapshot_id}: invalid output snapshot_id format or context binding")
        if not nonempty_string(snapshot.get("output_ref")):
            errors.append(f"{snapshot_id}: output_ref must be non-empty")
        if not valid_digest(snapshot.get("hash")):
            errors.append(f"{snapshot_id}: output snapshot hash must use sha256 lowercase format")
        if not valid_timestamp(snapshot.get("timestamp")):
            errors.append(f"{snapshot_id}: output snapshot timestamp must be timezone-aware")
        if isinstance(context_id, str):
            output_by_context[context_id].append(snapshot_id)
        reject_authority_fields(snapshot, snapshot_id, errors)

    dependencies_raw = dependency_doc.get("execution_dependencies")
    if not isinstance(dependencies_raw, list):
        errors.append("execution_dependencies must be a list")
        dependencies_raw = []
    dependency_keys: set[tuple[str, str]] = set()
    dependencies_by_context: dict[str, list[str]] = defaultdict(list)
    for index, dependency in enumerate(dependencies_raw):
        where = f"execution_dependencies[{index}]"
        if not isinstance(dependency, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_DEPENDENCY_FIELDS - set(dependency)
        if missing:
            errors.append(f"{where}: missing dependency fields {sorted(missing)}")
        context_id = dependency.get("context_id")
        name = dependency.get("dependency")
        if context_id not in contexts:
            errors.append(f"{where}: dependency must belong to an existing context")
        if not nonempty_string(name):
            errors.append(f"{where}: dependency must be non-empty")
        if isinstance(context_id, str) and isinstance(name, str) and name:
            key = (context_id, name)
            if key in dependency_keys:
                errors.append(f"duplicate execution dependency: {context_id} / {name}")
            else:
                dependency_keys.add(key)
                dependencies_by_context[context_id].append(name)
        if not nonempty_string(dependency.get("version")):
            errors.append(f"{where}: dependency version must be non-empty")
        if not nonempty_string(dependency.get("source")):
            errors.append(f"{where}: dependency source must be non-empty")
        reject_authority_fields(dependency, where, errors)

    for context_id, context in contexts.items():
        declared_dependencies = context.get("dependency_refs", [])
        if isinstance(declared_dependencies, list) and all(
            isinstance(item, str) for item in declared_dependencies
        ):
            if sorted(declared_dependencies) != sorted(dependencies_by_context.get(context_id, [])):
                errors.append(f"{context_id}: dependency_refs do not exactly match dependency records")
        declared_inputs = context.get("input_snapshot_refs", [])
        if isinstance(declared_inputs, list) and sorted(declared_inputs) != sorted(input_by_context.get(context_id, [])):
            errors.append(f"{context_id}: input_snapshot_refs do not exactly match input snapshots")
        declared_outputs = context.get("output_snapshot_refs", [])
        if isinstance(declared_outputs, list) and sorted(declared_outputs) != sorted(output_by_context.get(context_id, [])):
            errors.append(f"{context_id}: output_snapshot_refs do not exactly match output snapshots")

    context_meta = context_doc.get("metadata", {})
    if context_meta.get("execution_context_count") != len(contexts):
        errors.append("execution context metadata count mismatch")
    for status in CONTEXT_STATUSES:
        if context_meta.get("context_status_distribution", {}).get(status) != context_status_counts.get(status, 0):
            errors.append(f"context status distribution mismatch for {status}")
    if context_meta.get("reproducible_context_count") != 0:
        errors.append("v0.1 execution context metadata cannot claim reproducibility")
    require_zero_effect_metadata(context_meta, "execution context", errors)

    input_meta = input_doc.get("metadata", {})
    if input_meta.get("input_snapshot_count") != len(input_snapshots):
        errors.append("input snapshot metadata count mismatch")
    if input_meta.get("content_material_retained_count") != 0:
        errors.append("input snapshot metadata cannot claim retained content material")
    require_zero_effect_metadata(input_meta, "input snapshot", errors)
    output_meta = output_doc.get("metadata", {})
    if output_meta.get("output_snapshot_count") != len(output_snapshots):
        errors.append("output snapshot metadata count mismatch")
    if output_meta.get("content_material_retained_count") != 0:
        errors.append("output snapshot metadata cannot claim retained content material")
    require_zero_effect_metadata(output_meta, "output snapshot", errors)
    dependency_meta = dependency_doc.get("metadata", {})
    if dependency_meta.get("execution_dependency_count") != len(dependencies_raw):
        errors.append("execution dependency metadata count mismatch")
    if dependency_meta.get("resolved_artifact_count") != 0:
        errors.append("execution dependency metadata cannot claim resolved artifacts")
    if dependency_meta.get("transitive_dependency_coverage_count") != 0:
        errors.append("execution dependency metadata cannot claim transitive coverage")
    require_zero_effect_metadata(dependency_meta, "execution dependency", errors)

    # The authorized v0.1 layer defines schemas only and must remain fact-free.
    if contexts:
        errors.append("v0.1 baseline must not fabricate execution contexts")
    if input_snapshots:
        errors.append("v0.1 baseline must not fabricate input snapshots")
    if output_snapshots:
        errors.append("v0.1 baseline must not fabricate output snapshots")
    if dependencies_raw:
        errors.append("v0.1 baseline must not fabricate execution dependencies")
    if events:
        errors.append("execution context layer must not create real events")
    if attestations:
        errors.append("execution context layer must not create attestations")
    if runtimes:
        errors.append("execution context layer must not create a runtime")
    if capabilities:
        errors.append("execution context layer must not create a capability")

    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list):
        errors.append("organism_candidates must be a list")
        candidates = []
    if candidates:
        errors.append("execution context layer must not create an organism candidate")
    ecological_entities = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_entities, list):
        errors.append("ecological_entities must be a list")
        ecological_entities = []
    for ecological_entity in ecological_entities:
        if not isinstance(ecological_entity, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_entity.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("execution context cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("execution context cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("execution context cannot calculate fitness")
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("execution context layer must not create an Agent entity")

    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(f"{claim_id}: execution context must preserve capability claims at pending/C1")
            break
    for evidence_id, evidence_record in evidence.items():
        if evidence_record.get("status") != "pending" or evidence_record.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: execution context must preserve capability evidence at pending/E1")
            break
    for verification_id, verification in verifications.items():
        if (
            verification.get("status") != "pending"
            or verification.get("decision") != "pending"
            or verification.get("verification_level") != "V0"
        ):
            errors.append(f"{verification_id}: execution context must preserve verification at pending/V0")
            break

    mappings = index_records(mapping_doc.get("mappings"), "layer", "SAEE mappings", errors)
    context_mapping = mappings.get("Execution Context")
    expected_mapping = {
        "current_authority": "constitution/execution-context-constitution.yaml",
        "current_registry": "registry/execution-contexts.yaml",
        "saee_correspondence": "event reliability",
        "status": "defined_execution_context_model_no_records",
        "authority_effect": "none",
    }
    if context_mapping is None:
        errors.append("SAEE mapping must include Execution Context -> Event Reliability")
    else:
        for field, expected in expected_mapping.items():
            if context_mapping.get(field) != expected:
                errors.append(f"Execution Context SAEE mapping {field} mismatch")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mappings):
        errors.append("SAEE mapping metadata count mismatch")

    context_constitution = root / "constitution" / "execution-context-constitution.yaml"
    attestation_constitution = root / "constitution" / "event-attestation-constitution.yaml"
    if not context_constitution.is_file():
        errors.append("execution context constitution does not exist")
    if not attestation_constitution.is_file():
        errors.append("event attestation constitution does not exist")
    else:
        constitution_text = attestation_constitution.read_text(encoding="utf-8")
        for token in (
            'execution_context_reference: "execution-context-constitution.yaml"',
            'context_registry: "../registry/execution-contexts.yaml"',
            'input_snapshot_registry: "../registry/input-snapshots.yaml"',
            'output_snapshot_registry: "../registry/output-snapshots.yaml"',
            'dependency_registry: "../registry/execution-dependencies.yaml"',
        ):
            if token not in constitution_text:
                errors.append(f"event attestation constitution execution-context reference missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "execution_context_count": len(contexts),
        "context_status_distribution": {
            status: context_status_counts.get(status, 0) for status in CONTEXT_STATUSES
        },
        "input_snapshot_count": len(input_snapshots),
        "output_snapshot_count": len(output_snapshots),
        "snapshot_count": len(input_snapshots) + len(output_snapshots),
        "execution_dependency_count": len(dependencies_raw),
        "event_count": len(events),
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
    parser.add_argument("--contexts", type=Path, default=root / "registry" / "execution-contexts.yaml")
    parser.add_argument("--inputs", type=Path, default=root / "registry" / "input-snapshots.yaml")
    parser.add_argument("--outputs", type=Path, default=root / "registry" / "output-snapshots.yaml")
    parser.add_argument("--dependencies", type=Path, default=root / "registry" / "execution-dependencies.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--environments", type=Path, default=root / "registry" / "environments.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
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
            load_json_yaml(args.contexts),
            load_json_yaml(args.inputs),
            load_json_yaml(args.outputs),
            load_json_yaml(args.dependencies),
            load_json_yaml(args.entities),
            load_json_yaml(args.environments),
            load_json_yaml(args.events),
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
