#!/usr/bin/env python3
"""Validate the Event Attestation Layer without third-party packages.

Agent-readable contract:
- Producer types and attestation methods are vocabulary, not instances.
- Producers resolve to an existing type-appropriate identity before use.
- Attestations reference an existing event, producer, and declared method.
- Trust-anchor registration never creates trust or factual truth automatically.
- A signature binds an identified producer to a bounded claim; it cannot replace
  event provenance, occurrence evidence, integrity, or verification.
- The v0.1 producer, attestation, and trust-anchor registries remain empty.
- Attestation never creates an Agent, runtime, organism, capability, permission,
  fitness result, trust grant, or C/E/V promotion.
- Exit 0 means local structural PASS only; exit 1 fails closed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PRODUCER_TYPES = ("runtime", "service", "human", "automated")
PRODUCER_STATUSES = ("proposed", "active", "suspended", "revoked", "retired")
ATTESTATION_METHODS = (
    "self_attestation",
    "automated_attestation",
    "external_attestation",
)
METHOD_INDEPENDENCE = {
    "self_attestation": "none",
    "automated_attestation": "none_without_separate_identity_method_and_conflict_evidence",
    "external_attestation": "requires_separate_identity_and_conflict_evidence",
}
ATTESTATION_STATUSES = (
    "pending",
    "signed",
    "verified",
    "invalid",
    "revoked",
    "superseded",
)
TRUST_LEVELS = (
    "unknown",
    "identity_supported",
    "scope_supported",
    "independently_verified",
    "revoked",
)
REQUIRED_PRODUCER_FIELDS = {
    "producer_id",
    "producer_type",
    "identity_ref",
    "capability_scope",
    "status",
}
REQUIRED_ATTESTATION_FIELDS = {
    "attestation_id",
    "event_id",
    "producer_id",
    "attestation_method",
    "claim",
    "signature_ref",
    "status",
}
REQUIRED_CLAIM_FIELDS = {"event_id", "statement", "scope", "source_boundary"}
REQUIRED_ANCHOR_FIELDS = {
    "anchor_id",
    "identity_ref",
    "evidence_ref",
    "scope",
    "trust_level",
}
REQUIRED_METHOD_FIELDS = {"method_id", "requirements", "independence"}
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
    "runtime_created",
    "organism_created",
    "fitness_score",
    "maturity_level",
    "verification_level",
    "evidence_level",
}
ZERO_EFFECT_FIELDS = (
    "capability_assignment_count",
    "permission_grant_count",
    "agent_created_count",
    "runtime_created_count",
    "trust_grant_count",
    "authority_grant_count",
    "capability_effect_count",
    "c_e_v_level_change_count",
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


def nonempty_scope(value: Any) -> bool:
    """Accept an explicit non-empty mapping, list, or bounded string."""
    return (
        (isinstance(value, dict) and bool(value))
        or (isinstance(value, list) and bool(value))
        or nonempty_string(value)
    )


def reject_authority_fields(record: dict[str, Any], label: str, errors: list[str]) -> None:
    """Reject fields that would smuggle identity, ability, authority, or level state."""
    present = sorted(FORBIDDEN_AUTHORITY_KEYS.intersection(record))
    if present:
        errors.append(f"{label}: attestation record cannot create authority fields {present}")


def require_zero_effect_metadata(metadata: Any, label: str, errors: list[str]) -> None:
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in ZERO_EFFECT_FIELDS:
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label} metadata {field} must remain zero")


def identity_matches_producer_type(
    producer_type: str,
    identity_ref: str,
    entities: dict[str, dict[str, Any]],
    runtimes: dict[str, dict[str, Any]],
    verifiers: dict[str, dict[str, Any]],
) -> bool:
    """Resolve a producer identity through the type-appropriate existing registry."""
    if producer_type == "runtime":
        return identity_ref in runtimes
    if producer_type == "service":
        return entities.get(identity_ref, {}).get("entity_type") == "service"
    if producer_type == "human":
        verifier = verifiers.get(identity_ref, {})
        return (
            verifier.get("type") in {"maintainer", "external"}
            and isinstance(verifier.get("identity_evidence"), list)
            and bool(verifier.get("identity_evidence"))
        )
    if producer_type == "automated":
        verifier = verifiers.get(identity_ref)
        entity = entities.get(identity_ref)
        return (
            isinstance(verifier, dict)
            and verifier.get("type") == "automated"
        ) or (
            isinstance(entity, dict)
            and entity.get("entity_type") != "agent"
        )
    return False


def generic_identity_exists(
    identity_ref: Any,
    entities: dict[str, dict[str, Any]],
    runtimes: dict[str, dict[str, Any]],
    verifiers: dict[str, dict[str, Any]],
) -> bool:
    return (
        isinstance(identity_ref, str)
        and identity_ref in (set(entities) | set(runtimes) | set(verifiers))
    )


def evidence_reference_exists(
    reference: Any,
    evidence: dict[str, dict[str, Any]],
    verifications: dict[str, dict[str, Any]],
    root: Path,
) -> bool:
    """Resolve an evidence reference without interpreting it as trust."""
    if not nonempty_string(reference):
        return False
    if reference in evidence or reference in verifications:
        return True
    candidate = root / reference
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return candidate.is_file()


def contains_signing_secret(reference: Any) -> bool:
    if not isinstance(reference, str):
        return False
    lowered = reference.lower()
    return (
        "-----begin" in lowered
        or "private key" in lowered
        or "private_key" in lowered
        or "secret_key" in lowered
        or "signing_secret" in lowered
    )


def validate(
    producer_doc: dict[str, Any],
    attestation_doc: dict[str, Any],
    anchor_doc: dict[str, Any],
    method_doc: dict[str, Any],
    event_doc: dict[str, Any],
    integrity_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    verifier_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    claim_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    mapping_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate attestation taxonomy, empty state, references, and non-authority."""
    errors: list[str] = []

    entities = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    runtimes = index_records(runtime_doc.get("runtime_instances"), "runtime_id", "runtime_instances", errors)
    verifiers = index_records(verifier_doc.get("verifiers"), "verifier_id", "verifiers", errors)
    capabilities = index_records(capability_doc.get("capabilities"), "capability_id", "capabilities", errors)
    claims = index_records(claim_doc.get("claims"), "claim_id", "capability_claims", errors)
    evidence = index_records(evidence_doc.get("evidence"), "evidence_id", "capability_evidence", errors)
    verifications = index_records(
        verification_doc.get("verification_records"),
        "verification_id",
        "verification_records",
        errors,
    )
    events = index_records(event_doc.get("events"), "event_id", "events", errors)
    integrity = index_records(
        integrity_doc.get("event_integrity_records"),
        "event_id",
        "event_integrity_records",
        errors,
    )

    method_by_id = index_records(
        method_doc.get("attestation_methods"),
        "method_id",
        "attestation_methods",
        errors,
    )
    if tuple(method_by_id) != ATTESTATION_METHODS:
        errors.append("attestation methods must preserve self, automated, and external ordered definitions")
    for method_id, method in method_by_id.items():
        missing = REQUIRED_METHOD_FIELDS - set(method)
        if missing:
            errors.append(f"{method_id}: missing method fields {sorted(missing)}")
        requirements = method.get("requirements")
        if not isinstance(requirements, list) or not requirements or not all(
            nonempty_string(item) for item in requirements
        ):
            errors.append(f"{method_id}: requirements must be a non-empty string list")
        if method.get("independence") != METHOD_INDEPENDENCE.get(method_id):
            errors.append(f"{method_id}: independence boundary mismatch")
        if method.get("trust_effect") != "none" or method.get("fact_effect") != "none":
            errors.append(f"{method_id}: method cannot create trust or factual truth")
        reject_authority_fields(method, method_id, errors)
    method_meta = method_doc.get("metadata", {})
    if method_meta.get("attestation_method_count") != len(method_by_id):
        errors.append("attestation method metadata count mismatch")
    if method_meta.get("method_instance_count") != 0:
        errors.append("attestation method definitions cannot report method instances")
    if method_meta.get("automatic_trust_count") != 0:
        errors.append("attestation methods cannot grant trust automatically")
    if method_meta.get("automatic_authority_effect") != "none":
        errors.append("attestation methods cannot create authority")

    producers = index_records(
        producer_doc.get("event_producers"), "producer_id", "event_producers", errors
    )
    producer_type_counts: Counter[str] = Counter()
    for producer_id, producer in producers.items():
        missing = REQUIRED_PRODUCER_FIELDS - set(producer)
        if missing:
            errors.append(f"{producer_id}: missing producer fields {sorted(missing)}")
        producer_type = producer.get("producer_type")
        if producer_type not in PRODUCER_TYPES:
            errors.append(f"{producer_id}: invalid producer_type {producer_type!r}")
        else:
            producer_type_counts[producer_type] += 1
        identity_ref = producer.get("identity_ref")
        if not nonempty_string(identity_ref):
            errors.append(f"{producer_id}: producer must have a non-empty identity_ref")
        elif producer_type in PRODUCER_TYPES and not identity_matches_producer_type(
            producer_type, identity_ref, entities, runtimes, verifiers
        ):
            errors.append(f"{producer_id}: identity_ref does not resolve for producer_type {producer_type}")
        scope = producer.get("capability_scope")
        if not isinstance(scope, list):
            errors.append(f"{producer_id}: capability_scope must be a list")
            scope = []
        unknown_capabilities = sorted(
            item for item in scope if not isinstance(item, str) or item not in capabilities
        )
        if unknown_capabilities:
            errors.append(f"{producer_id}: capability_scope references unconfirmed capabilities {unknown_capabilities}")
        if producer.get("status") not in PRODUCER_STATUSES:
            errors.append(f"{producer_id}: invalid producer status {producer.get('status')!r}")
        reject_authority_fields(producer, producer_id, errors)
    producer_meta = producer_doc.get("metadata", {})
    if producer_meta.get("producer_type_count") != len(PRODUCER_TYPES):
        errors.append("producer type metadata count mismatch")
    if producer_meta.get("producer_count") != len(producers):
        errors.append("producer metadata count mismatch")
    for producer_type in PRODUCER_TYPES:
        if producer_meta.get("producer_type_distribution", {}).get(producer_type) != producer_type_counts.get(producer_type, 0):
            errors.append(f"producer type distribution mismatch for {producer_type}")
    require_zero_effect_metadata(producer_meta, "producer", errors)

    anchors = index_records(
        anchor_doc.get("trust_anchors"), "anchor_id", "trust_anchors", errors
    )
    trust_level_counts: Counter[str] = Counter()
    for anchor_id, anchor in anchors.items():
        missing = REQUIRED_ANCHOR_FIELDS - set(anchor)
        if missing:
            errors.append(f"{anchor_id}: missing trust-anchor fields {sorted(missing)}")
        if not generic_identity_exists(anchor.get("identity_ref"), entities, runtimes, verifiers):
            errors.append(f"{anchor_id}: identity_ref must resolve to an existing identity")
        level = anchor.get("trust_level")
        if level not in TRUST_LEVELS:
            errors.append(f"{anchor_id}: invalid trust_level {level!r}")
        else:
            trust_level_counts[level] += 1
        if not nonempty_scope(anchor.get("scope")):
            errors.append(f"{anchor_id}: scope must be explicit and non-empty")
        evidence_ref = anchor.get("evidence_ref")
        if level == "unknown":
            if evidence_ref is not None:
                errors.append(f"{anchor_id}: unknown trust level requires evidence_ref=null")
        elif level in TRUST_LEVELS and not evidence_reference_exists(
            evidence_ref, evidence, verifications, root
        ):
            errors.append(f"{anchor_id}: trust level {level} requires resolvable evidence_ref")
        if anchor.get("automatic_trust") is True or anchor.get("trust_granted") is True:
            errors.append(f"{anchor_id}: trust anchor cannot grant trust automatically")
        reject_authority_fields(anchor, anchor_id, errors)
    anchor_meta = anchor_doc.get("metadata", {})
    if anchor_meta.get("trust_anchor_count") != len(anchors):
        errors.append("trust-anchor metadata count mismatch")
    for level in TRUST_LEVELS:
        if anchor_meta.get("trust_level_distribution", {}).get(level) != trust_level_counts.get(level, 0):
            errors.append(f"trust level distribution mismatch for {level}")
    require_zero_effect_metadata(anchor_meta, "trust anchor", errors)

    attestations = index_records(
        attestation_doc.get("event_attestations"),
        "attestation_id",
        "event_attestations",
        errors,
    )
    attestation_status_counts: Counter[str] = Counter()
    signature_count = 0
    for attestation_id, attestation in attestations.items():
        missing = REQUIRED_ATTESTATION_FIELDS - set(attestation)
        if missing:
            errors.append(f"{attestation_id}: missing attestation fields {sorted(missing)}")
        event_id = attestation.get("event_id")
        event = events.get(event_id)
        if event is None:
            errors.append(f"{attestation_id}: attestation must reference an existing event")
        producer_id = attestation.get("producer_id")
        if producer_id not in producers:
            errors.append(f"{attestation_id}: attestation must reference an existing producer")
        method_id = attestation.get("attestation_method")
        if method_id not in method_by_id:
            errors.append(f"{attestation_id}: attestation_method is not registered")
        claim = attestation.get("claim")
        if not isinstance(claim, dict):
            errors.append(f"{attestation_id}: claim must be a mapping")
            claim = {}
        missing_claim = REQUIRED_CLAIM_FIELDS - set(claim)
        if missing_claim:
            errors.append(f"{attestation_id}: claim missing fields {sorted(missing_claim)}")
        if claim.get("event_id") != event_id:
            errors.append(f"{attestation_id}: claim event_id must match attestation event_id")
        if not nonempty_string(claim.get("statement")) or not nonempty_scope(claim.get("scope")):
            errors.append(f"{attestation_id}: claim statement and scope must be explicit")
        if claim.get("source_boundary") != "signature_does_not_replace_event_source":
            errors.append(f"{attestation_id}: claim must preserve the event-source boundary")
        status = attestation.get("status")
        if status not in ATTESTATION_STATUSES:
            errors.append(f"{attestation_id}: invalid attestation status {status!r}")
        else:
            attestation_status_counts[status] += 1
        signature_ref = attestation.get("signature_ref")
        if signature_ref is not None:
            signature_count += 1
        if status == "pending" and signature_ref is not None:
            errors.append(f"{attestation_id}: pending attestation requires signature_ref=null")
        if status == "pending" and attestation.get("timestamp") is not None:
            errors.append(f"{attestation_id}: pending attestation requires timestamp=null")
        if status in {"signed", "verified"} and not nonempty_string(signature_ref):
            errors.append(f"{attestation_id}: {status} attestation requires signature_ref")
        if contains_signing_secret(signature_ref):
            errors.append(f"{attestation_id}: signature_ref must not contain a private key or signing secret")
        anchor_refs = attestation.get("trust_anchor_refs", [])
        if not isinstance(anchor_refs, list):
            errors.append(f"{attestation_id}: trust_anchor_refs must be a list")
            anchor_refs = []
        unknown_anchors = sorted(set(anchor_refs) - set(anchors))
        if unknown_anchors:
            errors.append(f"{attestation_id}: unknown trust-anchor references {unknown_anchors}")
        if status == "verified":
            if not anchor_refs:
                errors.append(f"{attestation_id}: verified attestation requires trust_anchor_refs")
            for anchor_ref in anchor_refs:
                if anchors.get(anchor_ref, {}).get("trust_level") not in {
                    "scope_supported",
                    "independently_verified",
                }:
                    errors.append(f"{attestation_id}: verified attestation requires current scoped trust-anchor evidence")
            integrity_record = integrity.get(event_id, {})
            if integrity_record.get("integrity_status") != "verified":
                errors.append(f"{attestation_id}: verified attestation requires verified event integrity")
            if method_id == "external_attestation" and not any(
                anchors.get(anchor_ref, {}).get("trust_level") == "independently_verified"
                for anchor_ref in anchor_refs
            ):
                errors.append(f"{attestation_id}: external verified attestation requires independent anchor evidence")
        if event is not None:
            source = event.get("source")
            if not isinstance(source, dict) or not all(
                nonempty_string(source.get(field)) for field in ("kind", "locator", "collected_at")
            ):
                errors.append(f"{attestation_id}: signature cannot substitute for missing event source")
            if not nonempty_string(event.get("evidence_ref")):
                errors.append(f"{attestation_id}: signature cannot substitute for missing event evidence")
        reject_authority_fields(attestation, attestation_id, errors)
    attestation_meta = attestation_doc.get("metadata", {})
    if attestation_meta.get("attestation_count") != len(attestations):
        errors.append("attestation metadata count mismatch")
    for status in ATTESTATION_STATUSES:
        if attestation_meta.get("attestation_status_distribution", {}).get(status) != attestation_status_counts.get(status, 0):
            errors.append(f"attestation status distribution mismatch for {status}")
    if attestation_meta.get("signature_count") != signature_count:
        errors.append("attestation signature metadata count mismatch")
    if attestation_meta.get("verified_attestation_count") != attestation_status_counts.get("verified", 0):
        errors.append("verified attestation metadata count mismatch")
    require_zero_effect_metadata(attestation_meta, "attestation", errors)

    # This user-authorized v0.1 layer defines contracts only; records remain empty.
    if events:
        errors.append("event attestation layer must not create factual events")
    if producers:
        errors.append("v0.1 baseline must not instantiate event producers")
    if attestations:
        errors.append("v0.1 baseline must not fabricate event attestations")
    if anchors:
        errors.append("v0.1 baseline must not fabricate trust anchors")
    if runtimes:
        errors.append("event attestation layer must not create a runtime")

    candidate_records = candidate_doc.get("organism_candidates")
    if not isinstance(candidate_records, list):
        errors.append("organism_candidates must be a list")
        candidate_records = []
    if candidate_records:
        errors.append("event attestation layer must not create an organism candidate")
    ecological_records = ecological_doc.get("ecological_entities")
    if not isinstance(ecological_records, list):
        errors.append("ecological_entities must be a list")
        ecological_records = []
    for ecological_record in ecological_records:
        if not isinstance(ecological_record, dict):
            errors.append("ecological entity must be a mapping")
            continue
        if ecological_record.get("ecological_type") in {"Runtime", "Candidate Organism", "Digital Organism"}:
            errors.append("attestation cannot promote runtime or organism status")
        if ecological_record.get("evolution_stage") != "pre-organism":
            errors.append("attestation cannot change evolution stage")
        if ecological_record.get("fitness_status") != "unknown" or ecological_record.get("fitness_score") is not None:
            errors.append("attestation cannot calculate fitness")
    if any(entity.get("entity_type") == "agent" for entity in entities.values()):
        errors.append("event attestation layer must not create an Agent entity")

    if capabilities:
        errors.append("event attestation layer must not create a capability")
    for claim_id, claim in claims.items():
        if claim.get("status") != "pending" or claim.get("maturity_level") != "C1":
            errors.append(f"{claim_id}: attestation must preserve capability claims at pending/C1")
            break
    for evidence_id, evidence_record in evidence.items():
        if evidence_record.get("status") != "pending" or evidence_record.get("evidence_type") != "E1":
            errors.append(f"{evidence_id}: attestation must preserve capability evidence at pending/E1")
            break
    for verification_id, verification in verifications.items():
        if (
            verification.get("status") != "pending"
            or verification.get("decision") != "pending"
            or verification.get("verification_level") != "V0"
        ):
            errors.append(f"{verification_id}: attestation must preserve verification at pending/V0")
            break

    mappings = index_records(mapping_doc.get("mappings"), "layer", "SAEE mappings", errors)
    attestation_mapping = mappings.get("Attestation")
    expected_mapping = {
        "current_authority": "constitution/event-attestation-constitution.yaml",
        "current_registry": "registry/event-attestations.yaml",
        "saee_correspondence": "evidence reliability",
        "status": "defined_attestation_model_no_records",
        "authority_effect": "none",
    }
    if attestation_mapping is None:
        errors.append("SAEE mapping must include Attestation -> Evidence Reliability")
    else:
        for field, expected in expected_mapping.items():
            if attestation_mapping.get(field) != expected:
                errors.append(f"Attestation SAEE mapping {field} mismatch")
    if mapping_doc.get("metadata", {}).get("mapping_count") != len(mappings):
        errors.append("SAEE mapping metadata count mismatch")

    attestation_constitution = root / "constitution" / "event-attestation-constitution.yaml"
    integrity_constitution = root / "constitution" / "event-integrity-constitution.yaml"
    if not attestation_constitution.is_file():
        errors.append("event attestation constitution does not exist")
    if not integrity_constitution.is_file():
        errors.append("event integrity constitution does not exist")
    else:
        constitution_text = integrity_constitution.read_text(encoding="utf-8")
        for token in (
            'event_attestation_constitution: "event-attestation-constitution.yaml"',
            'attestation_registry: "../registry/event-attestations.yaml"',
            'producer_registry: "../registry/event-producers.yaml"',
            'trust_anchor_registry: "../registry/trust-anchors.yaml"',
            'method_registry: "../registry/attestation-methods.yaml"',
        ):
            if token not in constitution_text:
                errors.append(f"event integrity constitution attestation reference missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "producer_count": len(producers),
        "producer_type_distribution": {
            producer_type: producer_type_counts.get(producer_type, 0)
            for producer_type in PRODUCER_TYPES
        },
        "attestation_count": len(attestations),
        "attestation_status_distribution": {
            status: attestation_status_counts.get(status, 0)
            for status in ATTESTATION_STATUSES
        },
        "trust_anchor_count": len(anchors),
        "trust_level_distribution": {
            level: trust_level_counts.get(level, 0) for level in TRUST_LEVELS
        },
        "attestation_method_count": len(method_by_id),
        "event_count": len(events),
        "signature_count": signature_count,
        "trust_grant_count": 0,
        "capability_count": len(capabilities),
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "runtime_instance_count": len(runtimes),
        "organism_candidate_count": len(candidate_records),
        "digital_organism_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producers", type=Path, default=root / "registry" / "event-producers.yaml")
    parser.add_argument("--attestations", type=Path, default=root / "registry" / "event-attestations.yaml")
    parser.add_argument("--anchors", type=Path, default=root / "registry" / "trust-anchors.yaml")
    parser.add_argument("--methods", type=Path, default=root / "registry" / "attestation-methods.yaml")
    parser.add_argument("--events", type=Path, default=root / "registry" / "events.yaml")
    parser.add_argument("--integrity", type=Path, default=root / "registry" / "event-integrity.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--verifiers", type=Path, default=root / "registry" / "verifiers.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
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
            load_json_yaml(args.producers),
            load_json_yaml(args.attestations),
            load_json_yaml(args.anchors),
            load_json_yaml(args.methods),
            load_json_yaml(args.events),
            load_json_yaml(args.integrity),
            load_json_yaml(args.entities),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.verifiers),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            load_json_yaml(args.verification),
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
