#!/usr/bin/env python3
"""Validate the Governance Evidence Layer without third-party packages.

Agent-readable contract:
- Governance claims and evidence are empty in the v0.1 baseline.
- Each canonical entity has exactly one unobserved intake entry with unknown
  dimension, null value, and null timestamp; an entry is not observed fact.
- Governance maturity G0-G5 is sequential and separate from C/E/V axes.
- Claims and evidence never bind an archetype or grant governance authority.
- PASS proves local structural consistency only and changes no entity state.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

G_LEVELS = ("G0", "G1", "G2", "G3", "G4", "G5")
GE_LEVELS = ("GE1", "GE2", "GE3", "GE4", "GE5")
CLAIM_STATUSES = (
    "pending",
    "evidenced",
    "verified",
    "adaptive",
    "ecological",
    "rejected",
    "withdrawn",
    "revoked",
)
ACTIVE_STATUS_MATURITY = {
    "pending": "G1",
    "evidenced": "G2",
    "verified": "G3",
    "adaptive": "G4",
    "ecological": "G5",
}
EVIDENCE_STATUSES = (
    "pending",
    "assessed",
    "verified",
    "independently_verified",
    "continuously_observed",
    "invalid",
    "revoked",
)
OBSERVATION_DIMENSIONS = (
    "unknown",
    "coordination_efficiency",
    "autonomy",
    "stability",
    "adaptability",
    "centralization_risk",
)
OBSERVATION_STATUSES = ("unobserved", "observed", "invalid", "revoked")
REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "entity_id",
    "claimed_archetype",
    "scope",
    "status",
    "evidence_refs",
    "governance_maturity",
}
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "claim_id",
    "evidence_type",
    "source",
    "verification",
    "timestamp",
    "status",
}
REQUIRED_OBSERVATION_FIELDS = {
    "observation_id",
    "entity_id",
    "governance_dimension",
    "value",
    "timestamp",
    "status",
}
CLAIM_ID_RE = re.compile(r"^dbio:governance-claim:[a-z0-9][a-z0-9.-]*:[0-9]{3}$")
EVIDENCE_ID_RE = re.compile(r"^dbio:governance-evidence:[a-z0-9][a-z0-9.-]*:[0-9]{3}$")
OBSERVATION_ID_RE = re.compile(
    r"^dbio://governance-observation/([a-z0-9][a-z0-9.-]*)/intake/v[0-9][A-Za-z0-9._-]*$"
)
FORBIDDEN_GOVERNANCE_AUTHORITY_FIELDS = {
    "binding_id",
    "binding_status",
    "governance_binding",
    "governance_authority",
    "authority_grant",
    "decision_authority",
    "executed_transition",
    "selected_archetype",
}
FORBIDDEN_IDENTITY_FIELDS = {
    "canonical_id",
    "entity_type",
    "repository",
    "owner",
    "parent_entity",
    "child_entities",
    "identity_status",
}
FORBIDDEN_CAPABILITY_FIELDS = {
    "capability_id",
    "capabilities",
    "assigned_capabilities",
    "capability_assignment_status",
}
FORBIDDEN_PERMISSION_FIELDS = {
    "permission",
    "permissions",
    "permission_status",
    "permission_grants",
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
    """Index mapping records and reject missing or duplicate identifiers."""
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
    """Reject identity mutation, binding, capability, and permission fields."""
    groups = (
        ("governance authority", FORBIDDEN_GOVERNANCE_AUTHORITY_FIELDS),
        ("identity mutation", FORBIDDEN_IDENTITY_FIELDS),
        ("capability authority", FORBIDDEN_CAPABILITY_FIELDS),
        ("permission authority", FORBIDDEN_PERMISSION_FIELDS),
    )
    for label, forbidden in groups:
        present = forbidden & set(record)
        if present:
            errors.append(f"{where}: forbidden {label} fields {sorted(present)}")


def require_zero_effects(metadata: Any, label: str, errors: list[str]) -> None:
    """Require every effect or authority count in metadata to remain zero."""
    if not isinstance(metadata, dict):
        errors.append(f"{label} metadata must be a mapping")
        return
    for field in (
        "binding_effect_count",
        "claim_effect_count",
        "governance_authority_grant_count",
        "capability_effect_count",
        "permission_effect_count",
    ):
        if field in metadata and metadata.get(field) != 0:
            errors.append(f"{label}.{field} must remain zero")


def highest_current_ge(evidence_records: list[dict[str, Any]]) -> int:
    """Return the highest non-invalid governance evidence index."""
    indexes = [
        GE_LEVELS.index(record["evidence_type"]) + 1
        for record in evidence_records
        if record.get("evidence_type") in GE_LEVELS
        and record.get("status") not in {"pending", "invalid", "revoked"}
    ]
    return max(indexes, default=0)


def validate(
    claim_doc: dict[str, Any],
    governance_evidence_doc: dict[str, Any],
    maturity_doc: dict[str, Any],
    observation_doc: dict[str, Any],
    entity_doc: dict[str, Any],
    archetype_doc: dict[str, Any],
    binding_doc: dict[str, Any],
    capability_doc: dict[str, Any],
    capability_claim_doc: dict[str, Any],
    capability_evidence_doc: dict[str, Any],
    verification_doc: dict[str, Any],
    runtime_doc: dict[str, Any],
    candidate_doc: dict[str, Any],
    ecological_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    """Validate governance evidence references, maturity, and non-authority."""
    errors: list[str] = []
    entity_by_id = index_records(entity_doc.get("entities"), "entity_id", "entities", errors)
    archetype_by_id = index_records(
        archetype_doc.get("governance_archetypes"),
        "archetype_id",
        "governance_archetypes",
        errors,
    )
    claim_by_id = index_records(
        claim_doc.get("governance_claims"),
        "claim_id",
        "governance_claims",
        errors,
    )
    evidence_by_id = index_records(
        governance_evidence_doc.get("governance_evidence"),
        "evidence_id",
        "governance_evidence",
        errors,
    )

    evidence_by_claim: dict[str, list[dict[str, Any]]] = {}
    evidence_status_counts: Counter[str] = Counter()
    for evidence_id, evidence in evidence_by_id.items():
        missing = REQUIRED_EVIDENCE_FIELDS - set(evidence)
        if missing:
            errors.append(f"{evidence_id}: missing fields {sorted(missing)}")
        if not EVIDENCE_ID_RE.match(evidence_id):
            errors.append(f"{evidence_id}: malformed evidence_id")
        claim_id = evidence.get("claim_id")
        if claim_id not in claim_by_id:
            errors.append(f"{evidence_id}: unknown governance claim {claim_id!r}")
        elif isinstance(claim_id, str):
            evidence_by_claim.setdefault(claim_id, []).append(evidence)
        evidence_type = evidence.get("evidence_type")
        if evidence_type not in GE_LEVELS:
            errors.append(f"{evidence_id}: invalid governance evidence type {evidence_type!r}")
        status = evidence.get("status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"{evidence_id}: invalid evidence status {status!r}")
        else:
            evidence_status_counts[status] += 1
        if not isinstance(evidence.get("source"), dict) or not evidence.get("source"):
            errors.append(f"{evidence_id}: source must be a non-empty mapping")
        verification = evidence.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{evidence_id}: verification must be a mapping")
            verification = {}
        if status == "pending":
            if evidence.get("timestamp") is not None:
                errors.append(f"{evidence_id}: pending evidence requires timestamp=null")
            if verification.get("status") not in {None, "pending", "not_verified"}:
                errors.append(f"{evidence_id}: pending evidence cannot claim verification")
        if evidence_type == "GE4":
            if verification.get("independent") is not True:
                errors.append(f"{evidence_id}: GE4 requires independent verification")
            for field in ("verifier_id", "identity_evidence", "method", "conflict_of_interest", "limitations"):
                if not verification.get(field):
                    errors.append(f"{evidence_id}: GE4 verification missing {field}")
        if evidence_type == "GE5":
            for field in ("observation_window", "coverage", "drift", "stability", "revocation_conditions"):
                if not verification.get(field):
                    errors.append(f"{evidence_id}: GE5 verification missing {field}")
        reject_authority_fields(evidence, evidence_id, errors)

    claim_status_counts: Counter[str] = Counter()
    maturity_counts: Counter[str] = Counter()
    for claim_id, claim in claim_by_id.items():
        missing = REQUIRED_CLAIM_FIELDS - set(claim)
        if missing:
            errors.append(f"{claim_id}: missing fields {sorted(missing)}")
        if not CLAIM_ID_RE.match(claim_id):
            errors.append(f"{claim_id}: malformed claim_id")
        if claim.get("entity_id") not in entity_by_id:
            errors.append(f"{claim_id}: unknown entity {claim.get('entity_id')!r}")
        if claim.get("claimed_archetype") not in archetype_by_id:
            errors.append(f"{claim_id}: unknown claimed archetype {claim.get('claimed_archetype')!r}")
        if not isinstance(claim.get("scope"), str) or not claim.get("scope"):
            errors.append(f"{claim_id}: scope must be a non-empty string")
        status = claim.get("status")
        if status not in CLAIM_STATUSES:
            errors.append(f"{claim_id}: invalid claim status {status!r}")
        else:
            claim_status_counts[status] += 1
        maturity = claim.get("governance_maturity")
        if maturity not in G_LEVELS:
            errors.append(f"{claim_id}: invalid governance maturity {maturity!r}")
        else:
            maturity_counts[maturity] += 1
        if status in ACTIVE_STATUS_MATURITY and maturity != ACTIVE_STATUS_MATURITY[status]:
            errors.append(f"{claim_id}: status and governance maturity are inconsistent")
        refs = claim.get("evidence_refs")
        if not isinstance(refs, list):
            errors.append(f"{claim_id}: evidence_refs must be a list")
            refs = []
        if len(refs) != len(set(refs)):
            errors.append(f"{claim_id}: duplicate evidence reference")
        actual_ids = {record.get("evidence_id") for record in evidence_by_claim.get(claim_id, [])}
        if set(refs) != actual_ids:
            errors.append(f"{claim_id}: evidence_refs do not match claim-bound governance evidence")
        maturity_index = G_LEVELS.index(maturity) if maturity in G_LEVELS else 0
        if maturity_index >= 2 and highest_current_ge(evidence_by_claim.get(claim_id, [])) < maturity_index:
            errors.append(f"{claim_id}: governance maturity skips required evidence support")
        if maturity == "G3":
            if not any(
                record.get("evidence_type") == "GE3"
                and record.get("status") == "verified"
                and isinstance(record.get("verification"), dict)
                and record["verification"].get("status") == "verified"
                for record in evidence_by_claim.get(claim_id, [])
            ):
                errors.append(f"{claim_id}: G3 requires verified GE3 evidence")
        if maturity == "G4":
            if not any(
                record.get("evidence_type") == "GE4"
                and record.get("status") == "independently_verified"
                for record in evidence_by_claim.get(claim_id, [])
            ):
                errors.append(f"{claim_id}: G4 requires independently verified GE4 evidence")
        if maturity == "G5":
            if not any(
                record.get("evidence_type") == "GE5"
                and record.get("status") == "continuously_observed"
                for record in evidence_by_claim.get(claim_id, [])
            ):
                errors.append(f"{claim_id}: G5 requires continuously observed GE5 evidence")
        reject_authority_fields(claim, claim_id, errors)

    claim_meta = claim_doc.get("metadata", {})
    if claim_meta.get("claim_count") != len(claim_by_id):
        errors.append("governance claim metadata count mismatch")
    if claim_meta.get("pending_claim_count") != claim_status_counts.get("pending", 0):
        errors.append("pending governance claim metadata count mismatch")
    if claim_meta.get("approved_claim_count") != 0:
        errors.append("governance claim registry cannot claim approvals")
    require_zero_effects(claim_meta, "governance claim", errors)
    evidence_meta = governance_evidence_doc.get("metadata", {})
    if evidence_meta.get("evidence_count") != len(evidence_by_id):
        errors.append("governance evidence metadata count mismatch")
    if evidence_meta.get("pending_evidence_count") != evidence_status_counts.get("pending", 0):
        errors.append("pending governance evidence metadata count mismatch")
    if evidence_meta.get("verified_evidence_count") != evidence_status_counts.get("verified", 0):
        errors.append("verified governance evidence metadata count mismatch")
    if evidence_meta.get("independent_evidence_count") != evidence_status_counts.get("independently_verified", 0):
        errors.append("independent governance evidence metadata count mismatch")
    require_zero_effects(evidence_meta, "governance evidence", errors)
    if claim_by_id:
        errors.append("v0.1 baseline must not generate governance claims automatically")
    if evidence_by_id:
        errors.append("v0.1 baseline must not generate governance evidence automatically")

    levels = maturity_doc.get("levels")
    maturity_by_level = index_records(levels, "level", "governance_maturity.levels", errors)
    if tuple(maturity_by_level) != G_LEVELS:
        errors.append("governance maturity levels must preserve G0-G5 order")
    for index, level in enumerate(G_LEVELS):
        expected_predecessors = list(G_LEVELS[:index])
        if maturity_by_level.get(level, {}).get("required_predecessors") != expected_predecessors:
            errors.append(f"{level}: governance maturity predecessors are incomplete or out of order")
    distribution = maturity_doc.get("current_distribution")
    if not isinstance(distribution, dict):
        errors.append("governance maturity current_distribution must be a mapping")
        distribution = {}
    expected_distribution = {level: 0 for level in G_LEVELS}
    expected_distribution["G0"] = len(entity_by_id) if not claim_by_id else len(entity_by_id) - len({c.get("entity_id") for c in claim_by_id.values()})
    for level, count in maturity_counts.items():
        expected_distribution[level] += count
    if distribution != expected_distribution:
        errors.append("governance maturity distribution does not match claims and G0 unknown entities")
    maturity_meta = maturity_doc.get("metadata", {})
    if maturity_meta.get("canonical_entity_count") != len(entity_by_id):
        errors.append("governance maturity canonical entity count mismatch")

    observations = observation_doc.get("governance_observations")
    observation_by_id = index_records(
        observations,
        "observation_id",
        "governance_observations",
        errors,
    )
    observation_by_entity: dict[str, dict[str, Any]] = {}
    observed_value_count = 0
    non_null_timestamp_count = 0
    for observation_id, observation in observation_by_id.items():
        missing = REQUIRED_OBSERVATION_FIELDS - set(observation)
        if missing:
            errors.append(f"{observation_id}: missing fields {sorted(missing)}")
        match = OBSERVATION_ID_RE.match(observation_id)
        if not match:
            errors.append(f"{observation_id}: malformed observation_id")
        entity_id = observation.get("entity_id")
        if entity_id not in entity_by_id:
            errors.append(f"{observation_id}: unknown entity {entity_id!r}")
        if match and entity_id != match.group(1):
            errors.append(f"{observation_id}: entity_id does not match observation_id")
        if entity_id in observation_by_entity:
            errors.append(f"duplicate governance observation entry for entity {entity_id!r}")
        elif isinstance(entity_id, str):
            observation_by_entity[entity_id] = observation
        if observation.get("governance_dimension") not in OBSERVATION_DIMENSIONS:
            errors.append(f"{observation_id}: invalid governance dimension")
        if observation.get("status") not in OBSERVATION_STATUSES:
            errors.append(f"{observation_id}: invalid observation status")
        if observation.get("status") != "unobserved":
            errors.append(f"{observation_id}: v0.1 intake entry must remain unobserved")
        if observation.get("governance_dimension") != "unknown":
            errors.append(f"{observation_id}: unobserved entry dimension must remain unknown")
        if observation.get("value") is not None:
            observed_value_count += 1
            errors.append(f"{observation_id}: unobserved entry value must remain null")
        if observation.get("timestamp") is not None:
            non_null_timestamp_count += 1
            errors.append(f"{observation_id}: unobserved entry timestamp must remain null")
        reject_authority_fields(observation, observation_id, errors)
    if set(observation_by_entity) != set(entity_by_id):
        errors.append("every canonical entity must have exactly one governance observation intake entry")
    observation_meta = observation_doc.get("metadata", {})
    if observation_meta.get("observation_entry_count") != len(observation_by_id):
        errors.append("governance observation entry metadata count mismatch")
    if observation_meta.get("unobserved_entry_count") != len(observation_by_id):
        errors.append("unobserved governance entry metadata count mismatch")
    if observation_meta.get("observed_value_count") != observed_value_count:
        errors.append("observed governance value metadata count mismatch")
    if observation_meta.get("non_null_timestamp_count") != non_null_timestamp_count:
        errors.append("governance observation timestamp metadata count mismatch")
    require_zero_effects(observation_meta, "governance observation", errors)

    bindings = binding_doc.get("governance_bindings")
    if not isinstance(bindings, list) or bindings:
        errors.append("governance claims or evidence must not create an archetype binding")
        bindings = []
    capabilities = capability_doc.get("capabilities")
    if not isinstance(capabilities, list) or capabilities:
        errors.append("governance evidence must not create a capability")
        capabilities = []
    capability_claims = capability_claim_doc.get("claims")
    if not isinstance(capability_claims, list):
        errors.append("capability claims must be a list")
        capability_claims = []
    for claim in capability_claims:
        if not isinstance(claim, dict) or claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("governance evidence must preserve capability claims at C1/pending")
            break
    capability_evidence = capability_evidence_doc.get("evidence")
    if not isinstance(capability_evidence, list):
        errors.append("capability evidence must be a list")
        capability_evidence = []
    for evidence in capability_evidence:
        if not isinstance(evidence, dict) or evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("governance evidence must preserve capability evidence at E1/pending")
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
            errors.append("governance evidence must preserve verification at V0/pending")
            break
    runtimes = runtime_doc.get("runtime_instances")
    if not isinstance(runtimes, list) or runtimes:
        errors.append("governance evidence must not create a runtime")
        runtimes = []
    candidates = candidate_doc.get("organism_candidates")
    if not isinstance(candidates, list) or candidates:
        errors.append("governance evidence must not create an organism candidate")
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
            errors.append("governance evidence cannot promote runtime or organism status")
        if ecological_entity.get("evolution_stage") != "pre-organism":
            errors.append("governance evidence cannot change evolution stage")
        if ecological_entity.get("fitness_status") != "unknown" or ecological_entity.get("fitness_score") is not None:
            errors.append("governance evidence cannot change fitness")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("governance evidence must not create an Agent entity")

    governance_evidence_constitution = root / "constitution" / "governance-evidence-constitution.yaml"
    governance_archetype_constitution = root / "constitution" / "governance-archetype-constitution.yaml"
    if not governance_evidence_constitution.is_file():
        errors.append("governance evidence constitution does not exist")
    if not governance_archetype_constitution.is_file():
        errors.append("governance archetype constitution does not exist")
    else:
        text = governance_archetype_constitution.read_text(encoding="utf-8")
        if 'governance_evidence_constitution: "governance-evidence-constitution.yaml"' not in text:
            errors.append("governance archetype constitution does not reference governance evidence")
        for token in (
            'claims: "../registry/governance-claims.yaml"',
            'evidence: "../registry/governance-evidence.yaml"',
            'maturity: "../registry/governance-maturity.yaml"',
            'observations: "../registry/governance-observations.yaml"',
        ):
            if token not in text:
                errors.append(f"governance archetype evidence requirement missing {token}")

    return {
        "status": "FAIL" if errors else "PASS",
        "governance_claim_count": len(claim_by_id),
        "governance_evidence_count": len(evidence_by_id),
        "governance_maturity_distribution": {
            level: distribution.get(level, 0) for level in G_LEVELS
        },
        "governance_observation_entry_count": len(observation_by_id),
        "observed_governance_value_count": observed_value_count,
        "governance_binding_count": len(bindings),
        "governance_authority_grant_count": 0,
        "capability_count": len(capabilities),
        "permission_grant_count": 0,
        "runtime_instance_count": len(runtimes),
        "organism_candidate_count": len(candidates),
        "digital_organism_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims", type=Path, default=root / "registry" / "governance-claims.yaml")
    parser.add_argument("--governance-evidence", type=Path, default=root / "registry" / "governance-evidence.yaml")
    parser.add_argument("--maturity", type=Path, default=root / "registry" / "governance-maturity.yaml")
    parser.add_argument("--observations", type=Path, default=root / "registry" / "governance-observations.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--archetypes", type=Path, default=root / "registry" / "governance-archetypes.yaml")
    parser.add_argument("--bindings", type=Path, default=root / "registry" / "governance-bindings.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--capability-claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--capability-evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        result = validate(
            load_json_yaml(args.claims),
            load_json_yaml(args.governance_evidence),
            load_json_yaml(args.maturity),
            load_json_yaml(args.observations),
            load_json_yaml(args.entities),
            load_json_yaml(args.archetypes),
            load_json_yaml(args.bindings),
            load_json_yaml(args.capabilities),
            load_json_yaml(args.capability_claims),
            load_json_yaml(args.capability_evidence),
            load_json_yaml(args.verification),
            load_json_yaml(args.runtimes),
            load_json_yaml(args.candidates),
            load_json_yaml(args.ecological),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"GOVERNANCE_EVIDENCE_VALIDATION: {result['status']}")
        print(f"claims={result.get('governance_claim_count', 0)}")
        print(f"evidence={result.get('governance_evidence_count', 0)}")
        print(f"observations={result.get('governance_observation_entry_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
