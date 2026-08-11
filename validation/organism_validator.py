#!/usr/bin/env python3
"""Validate Digital Organism Genesis registries and qualification gates.

Agent-readable contract:
- Runtime, resource-flow, behavior-trace, and candidate registries are empty in
  the v0.1 baseline.
- A candidate requires all eight independent qualification criteria plus an
  attributable approved qualification review.
- Entity, runtime, capability, evidence, verification, ecology, or fitness
  never promotes a candidate automatically.
- PASS creates no Agent, runtime, Candidate Organism, Digital Organism,
  capability, permission, or C/E/V upgrade.
- Exit 0 means PASS; exit 1 means Genesis qualification must fail closed.
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

QUALIFICATION_REQUIREMENTS = (
    "identity_verified",
    "runtime_exists",
    "capability_verified",
    "evidence_level_at_least_E3",
    "verification_level_at_least_V3",
    "resource_flow_recorded",
    "behavior_trace_available",
    "evolution_record_available",
)
RUNTIME_STATES = {"proposed", "active", "suspended", "stopped", "revoked", "retired"}
RESOURCE_TYPES = {
    "compute",
    "memory",
    "storage",
    "network",
    "token",
    "energy",
    "time",
    "data",
    "external_service",
}
CANDIDATE_STATUSES = {
    "proposed",
    "qualifying",
    "qualified",
    "disqualified",
    "withdrawn",
    "retired",
}
C_RANK = {f"C{index}": index for index in range(6)}
E_RANK = {f"E{index}": index for index in range(6)}
V_RANK = {f"V{index}": index for index in range(6)}
RUNTIME_ID_RE = re.compile(
    r"^dbio://runtime/(?P<entity_id>[a-z0-9][a-z0-9.-]*)/"
    r"(?P<environment>[a-zA-Z0-9._-]+)/(?P<instance_id>[a-zA-Z0-9._-]+)$"
)
CANDIDATE_ID_RE = re.compile(
    r"^dbio://organism-candidate/(?P<entity_id>[a-z0-9][a-z0-9.-]*)/"
    r"(?P<version>v[a-zA-Z0-9][a-zA-Z0-9._-]*)$"
)
LEDGER_ENTRY_RE = re.compile(
    r'^  - id: "(?P<id>[^"]+)"(?P<body>.*?)(?=^  - id: |\Z)',
    re.MULTILINE | re.DOTALL,
)
LEDGER_SUBJECT_RE = re.compile(r'^\s+subject_entity_id: "(?P<entity>[^"]+)"', re.MULTILINE)


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one mapping")
    return value


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def index_records(
    records: Any, key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
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


def ledger_subjects(ledger_text: str) -> dict[str, str]:
    """Extract only explicit subject_entity_id bindings from the append-only ledger."""
    result: dict[str, str] = {}
    for match in LEDGER_ENTRY_RE.finditer(ledger_text):
        subject_match = LEDGER_SUBJECT_RE.search(match.group("body"))
        if subject_match:
            result[match.group("id")] = subject_match.group("entity")
    return result


def approved_qualification_review(review: Any) -> bool:
    if not isinstance(review, dict):
        return False
    required = {"reviewer", "decision", "limitations", "timestamp"}
    return (
        required.issubset(review)
        and isinstance(review.get("reviewer"), str)
        and bool(review.get("reviewer"))
        and review.get("decision") == "approved"
        and isinstance(review.get("limitations"), list)
        and valid_timestamp(review.get("timestamp"))
    )


def validate(docs: dict[str, dict[str, Any]], texts: dict[str, str]) -> dict[str, Any]:
    errors: list[str] = []
    entity_by_id = index_records(docs["entities"].get("entities"), "entity_id", "entities", errors)
    capability_by_id = index_records(
        docs["capabilities"].get("capabilities"), "capability_id", "capabilities", errors
    )
    claim_by_id = index_records(docs["claims"].get("claims"), "claim_id", "claims", errors)
    review_by_id = index_records(docs["reviews"].get("reviews"), "review_id", "reviews", errors)
    evidence_by_id = index_records(docs["evidence"].get("evidence"), "evidence_id", "evidence", errors)
    verification_by_id = index_records(
        docs["verification"].get("verification_records"),
        "verification_id",
        "verification_records",
        errors,
    )
    ecological_by_id = index_records(
        docs["ecological"].get("ecological_entities"),
        "entity_id",
        "ecological_entities",
        errors,
    )
    runtime_by_id = index_records(
        docs["runtimes"].get("runtime_instances"), "runtime_id", "runtime_instances", errors
    )
    resource_by_id = index_records(
        docs["resource_flows"].get("resource_flows"), "resource_flow_id", "resource_flows", errors
    )
    trace_by_id = index_records(
        docs["behavior_traces"].get("behavior_traces"), "trace_id", "behavior_traces", errors
    )
    candidate_by_id = index_records(
        docs["candidates"].get("organism_candidates"),
        "candidate_id",
        "organism_candidates",
        errors,
    )
    evolution_subject_by_id = ledger_subjects(texts["ledger"])

    claims_by_entity: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claim_by_id.values():
        entity_id = claim.get("entity_id")
        if isinstance(entity_id, str):
            claims_by_entity[entity_id].append(claim)
    approved_claim_ids = {
        review.get("claim_id")
        for review in review_by_id.values()
        if review.get("decision") == "approved"
    }

    verified_claim_by_entity = {
        entity_id: any(
            C_RANK.get(claim.get("maturity_level"), -1) >= C_RANK["C3"]
            and claim.get("status") in {"verified", "governed", "autonomous"}
            and claim.get("claim_id") in approved_claim_ids
            for claim in claims
        )
        for entity_id, claims in claims_by_entity.items()
    }

    for runtime_id, runtime in runtime_by_id.items():
        match = RUNTIME_ID_RE.match(runtime_id)
        if not match:
            errors.append(f"{runtime_id}: malformed runtime_id")
        entity_id = runtime.get("entity_id")
        if entity_id not in entity_by_id:
            errors.append(f"{runtime_id}: unknown entity {entity_id!r}")
        elif match and match.group("entity_id") != entity_id:
            errors.append(f"{runtime_id}: runtime_id entity does not match entity_id")
        environment = runtime.get("environment")
        if not isinstance(environment, str) or not environment:
            errors.append(f"{runtime_id}: environment must be non-empty")
        elif match and match.group("environment") != environment:
            errors.append(f"{runtime_id}: runtime_id environment does not match")
        if runtime.get("lifecycle_state") not in RUNTIME_STATES:
            errors.append(f"{runtime_id}: invalid lifecycle_state")
        for field in ("resource_refs", "trace_refs", "evidence_refs"):
            if not isinstance(runtime.get(field), list):
                errors.append(f"{runtime_id}: {field} must be a list")
        if runtime.get("agent_status", "not_an_agent") != "not_an_agent":
            errors.append(f"{runtime_id}: runtime cannot create an Agent")
        if runtime.get("capability_assignment_status", "not_assigned") != "not_assigned":
            errors.append(f"{runtime_id}: runtime cannot assign capability")
        if runtime.get("permission_status", "not_granted") != "not_granted":
            errors.append(f"{runtime_id}: runtime cannot grant permission")

    for resource_id, flow in resource_by_id.items():
        runtime_id = flow.get("runtime_id")
        if runtime_id not in runtime_by_id:
            errors.append(f"{resource_id}: unknown runtime reference {runtime_id!r}")
        if flow.get("resource_type") not in RESOURCE_TYPES:
            errors.append(f"{resource_id}: invalid resource_type")
        if flow.get("input") is None or flow.get("output") is None:
            errors.append(f"{resource_id}: resource input and output must be recorded")
        if not valid_timestamp(flow.get("timestamp")):
            errors.append(f"{resource_id}: resource flow requires ISO 8601 timestamp")
    for runtime_id, runtime in runtime_by_id.items():
        for resource_id in runtime.get("resource_refs", []):
            flow = resource_by_id.get(resource_id)
            if flow is None:
                errors.append(f"{runtime_id}: unknown resource_ref {resource_id!r}")
            elif flow.get("runtime_id") != runtime_id:
                errors.append(f"{runtime_id}: resource_ref belongs to another runtime")

    for trace_id, trace in trace_by_id.items():
        runtime_id = trace.get("runtime_id")
        if runtime_id not in runtime_by_id:
            errors.append(f"{trace_id}: unknown runtime reference {runtime_id!r}")
        if trace.get("action") is None or trace.get("result") is None:
            errors.append(f"{trace_id}: action and result must be recorded")
        evidence_ref = trace.get("evidence_ref")
        if evidence_ref not in evidence_by_id:
            errors.append(f"{trace_id}: unknown evidence_ref {evidence_ref!r}")
        if not valid_timestamp(trace.get("timestamp")):
            errors.append(f"{trace_id}: behavior trace requires ISO 8601 timestamp")
    for runtime_id, runtime in runtime_by_id.items():
        for trace_id in runtime.get("trace_refs", []):
            trace = trace_by_id.get(trace_id)
            if trace is None:
                errors.append(f"{runtime_id}: unknown trace_ref {trace_id!r}")
            elif trace.get("runtime_id") != runtime_id:
                errors.append(f"{runtime_id}: trace_ref belongs to another runtime")
        for evidence_id in runtime.get("evidence_refs", []):
            if evidence_id not in evidence_by_id:
                errors.append(f"{runtime_id}: unknown evidence_ref {evidence_id!r}")

    def compute_missing(entity_id: str, qualification: Any) -> list[str]:
        qualification = qualification if isinstance(qualification, dict) else {}
        missing: list[str] = []
        entity = entity_by_id.get(entity_id, {})
        identity_verified = (
            entity.get("verification", {}).get("status") == "verified"
            and entity.get("lifecycle", {}).get("state") not in {"suspended", "retired"}
        )
        if not identity_verified:
            missing.append("identity_verified")

        runtime_id = qualification.get("runtime_id")
        runtime = runtime_by_id.get(runtime_id)
        runtime_exists = (
            runtime is not None
            and runtime.get("entity_id") == entity_id
            and runtime.get("lifecycle_state") == "active"
        )
        if not runtime_exists:
            missing.append("runtime_exists")

        capability_ids = qualification.get("capability_ids")
        capability_records_exist = (
            isinstance(capability_ids, list)
            and bool(capability_ids)
            and all(capability_id in capability_by_id for capability_id in capability_ids)
        )
        verified_claim_exists = verified_claim_by_entity.get(entity_id, False)
        if not (capability_records_exist and verified_claim_exists):
            missing.append("capability_verified")

        evidence_refs = qualification.get("evidence_refs")
        qualified_evidence = False
        if isinstance(evidence_refs, list):
            qualified_evidence = any(
                (evidence := evidence_by_id.get(evidence_id)) is not None
                and evidence.get("status") not in {"invalid", "revoked", "pending"}
                and E_RANK.get(evidence.get("evidence_type"), -1) >= E_RANK["E3"]
                and (claim := claim_by_id.get(evidence.get("claim_id"))) is not None
                and claim.get("entity_id") == entity_id
                for evidence_id in evidence_refs
            )
        if not qualified_evidence:
            missing.append("evidence_level_at_least_E3")

        verification_refs = qualification.get("verification_refs")
        qualified_verification = False
        if isinstance(verification_refs, list):
            for verification_id in verification_refs:
                verification = verification_by_id.get(verification_id)
                if (
                    verification is not None
                    and verification.get("subject") == entity_id
                    and V_RANK.get(verification.get("verification_level"), -1) >= V_RANK["V3"]
                    and verification.get("status") == "completed"
                    and verification.get("decision") == "pass"
                ):
                    qualified_verification = True
                    break
        if not qualified_verification:
            missing.append("verification_level_at_least_V3")

        resource_refs = qualification.get("resource_flow_refs")
        resource_flow_recorded = (
            runtime_exists
            and isinstance(resource_refs, list)
            and bool(resource_refs)
            and all(
                reference in resource_by_id
                and resource_by_id[reference].get("runtime_id") == runtime_id
                for reference in resource_refs
            )
        )
        if not resource_flow_recorded:
            missing.append("resource_flow_recorded")

        trace_refs = qualification.get("trace_refs")
        behavior_trace_available = (
            runtime_exists
            and isinstance(trace_refs, list)
            and bool(trace_refs)
            and all(
                reference in trace_by_id
                and trace_by_id[reference].get("runtime_id") == runtime_id
                for reference in trace_refs
            )
        )
        if not behavior_trace_available:
            missing.append("behavior_trace_available")

        evolution_ref = qualification.get("evolution_ref")
        if evolution_subject_by_id.get(evolution_ref) != entity_id:
            missing.append("evolution_record_available")
        return missing

    candidate_status_counts: Counter[str] = Counter()
    for candidate_id, candidate in candidate_by_id.items():
        match = CANDIDATE_ID_RE.match(candidate_id)
        if not match:
            errors.append(f"{candidate_id}: malformed candidate_id")
        entity_id = candidate.get("entity_id")
        if entity_id not in entity_by_id or entity_id not in ecological_by_id:
            errors.append(f"{candidate_id}: unknown entity {entity_id!r}")
        elif match and match.group("entity_id") != entity_id:
            errors.append(f"{candidate_id}: candidate_id entity does not match")
        status = candidate.get("qualification_status")
        if status not in CANDIDATE_STATUSES:
            errors.append(f"{candidate_id}: invalid qualification_status")
        else:
            candidate_status_counts[status] += 1
        calculated_missing = compute_missing(entity_id, candidate.get("qualification_evidence"))
        recorded_missing = candidate.get("missing_requirements")
        if recorded_missing != calculated_missing:
            errors.append(f"{candidate_id}: missing_requirements do not match qualification evidence")
        if status == "qualified":
            if calculated_missing:
                errors.append(
                    f"{candidate_id}: qualified candidate has missing requirements {calculated_missing}"
                )
            review = candidate.get("qualification_evidence", {}).get("qualification_review") if isinstance(candidate.get("qualification_evidence"), dict) else None
            if not approved_qualification_review(review):
                errors.append(f"{candidate_id}: qualified candidate requires approved qualification review")
        if "digital_organism_id" in candidate:
            errors.append(f"{candidate_id}: Genesis cannot create Digital Organism")
        if candidate.get("agent_status", "not_an_agent") != "not_an_agent":
            errors.append(f"{candidate_id}: Genesis cannot create Agent")
        if candidate.get("capability_assignment_status", "not_assigned") != "not_assigned":
            errors.append(f"{candidate_id}: Genesis cannot assign capability")
        if candidate.get("permission_status", "not_granted") != "not_granted":
            errors.append(f"{candidate_id}: Genesis cannot grant permission")

    runtime_meta = docs["runtimes"].get("metadata", {})
    resource_meta = docs["resource_flows"].get("metadata", {})
    trace_meta = docs["behavior_traces"].get("metadata", {})
    candidate_meta = docs["candidates"].get("metadata", {})
    if runtime_meta.get("runtime_instance_count") != len(runtime_by_id):
        errors.append("runtime metadata count mismatch")
    if runtime_meta.get("active_runtime_count") != sum(
        runtime.get("lifecycle_state") == "active" for runtime in runtime_by_id.values()
    ):
        errors.append("active runtime metadata count mismatch")
    if resource_meta.get("resource_flow_count") != len(resource_by_id):
        errors.append("resource-flow metadata count mismatch")
    if trace_meta.get("behavior_trace_count") != len(trace_by_id):
        errors.append("behavior-trace metadata count mismatch")
    if candidate_meta.get("candidate_count") != len(candidate_by_id):
        errors.append("candidate metadata count mismatch")
    if candidate_meta.get("qualified_candidate_count") != candidate_status_counts.get("qualified", 0):
        errors.append("qualified candidate metadata count mismatch")
    if candidate_meta.get("digital_organism_count") != 0:
        errors.append("Genesis metadata must report zero Digital Organisms")

    if runtime_meta.get("status") == "empty_runtime_baseline" and runtime_by_id:
        errors.append("v0.1 runtime registry must remain empty")
    if resource_meta.get("status") == "empty_resource_flow_baseline" and resource_by_id:
        errors.append("v0.1 resource-flow registry must remain empty")
    if trace_meta.get("status") == "empty_behavior_trace_baseline" and trace_by_id:
        errors.append("v0.1 behavior-trace registry must remain empty")
    if candidate_meta.get("status") == "empty_candidate_baseline" and candidate_by_id:
        errors.append("v0.1 candidate registry must remain empty")

    aggregate_missing_counts = Counter()
    for entity_id in entity_by_id:
        aggregate_missing_counts.update(compute_missing(entity_id, {}))
    for requirement in QUALIFICATION_REQUIREMENTS:
        if candidate_meta.get("baseline_missing_requirement_counts", {}).get(requirement) != aggregate_missing_counts.get(requirement, 0):
            errors.append(f"baseline missing-requirement count mismatch for {requirement}")
    if tuple(docs["candidates"].get("qualification_requirements", [])) != QUALIFICATION_REQUIREMENTS:
        errors.append("qualification requirements must preserve all eight ordered criteria")

    transitions = docs["mapping"].get("genesis_transitions")
    if not isinstance(transitions, list) or len(transitions) != 1:
        errors.append("SAEE mapping must contain one Genesis transition")
    else:
        transition = transitions[0]
        if transition.get("from") != "Runtime" or transition.get("to") != "Candidate Organism":
            errors.append("Genesis transition must map Runtime to Candidate Organism")
        if transition.get("automatic") is not False:
            errors.append("Runtime cannot automatically become Candidate Organism")
        if tuple(transition.get("required_conditions", [])) != QUALIFICATION_REQUIREMENTS:
            errors.append("Genesis transition must require all eight qualification conditions")
        if transition.get("current_runtime_count") != len(runtime_by_id):
            errors.append("Genesis transition runtime count mismatch")
        if transition.get("current_candidate_count") != len(candidate_by_id):
            errors.append("Genesis transition candidate count mismatch")

    if capability_by_id:
        errors.append("v0.1 Genesis integration must not create capabilities")
    if any(entity.get("entity_type") == "agent" for entity in entity_by_id.values()):
        errors.append("v0.1 Genesis integration must not create Agent entity")
    for claim in claim_by_id.values():
        if claim.get("maturity_level") != "C1" or claim.get("status") != "pending":
            errors.append("Genesis integration must preserve all claims at C1/pending")
            break
    for evidence in evidence_by_id.values():
        if evidence.get("evidence_type") != "E1" or evidence.get("status") != "pending":
            errors.append("Genesis integration must preserve all evidence at E1/pending")
            break
    for verification in verification_by_id.values():
        if verification.get("verification_level") != "V0" or verification.get("status") != "pending" or verification.get("decision") != "pending":
            errors.append("Genesis integration must preserve all verification at V0/pending")
            break

    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entity_by_id),
        "runtime_instance_count": len(runtime_by_id),
        "resource_flow_count": len(resource_by_id),
        "behavior_trace_count": len(trace_by_id),
        "candidate_count": len(candidate_by_id),
        "qualified_candidate_count": candidate_status_counts.get("qualified", 0),
        "digital_organism_count": 0,
        "baseline_missing_requirement_counts": {
            requirement: aggregate_missing_counts.get(requirement, 0)
            for requirement in QUALIFICATION_REQUIREMENTS
        },
        "capability_count": len(capability_by_id),
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "c_e_v_level_change_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtimes", type=Path, default=root / "registry" / "runtime-instances.yaml")
    parser.add_argument("--resource-flows", type=Path, default=root / "registry" / "resource-flows.yaml")
    parser.add_argument("--behavior-traces", type=Path, default=root / "registry" / "behavior-traces.yaml")
    parser.add_argument("--candidates", type=Path, default=root / "registry" / "organism-candidates.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--capabilities", type=Path, default=root / "registry" / "capabilities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--reviews", type=Path, default=root / "registry" / "capability-reviews.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--verification", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--ecological", type=Path, default=root / "registry" / "ecological-entities.yaml")
    parser.add_argument("--mapping", type=Path, default=root / "registry" / "evolution-mapping.yaml")
    parser.add_argument("--ledger", type=Path, default=root / "evolution" / "evolution-ledger.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        docs = {
            "runtimes": load_json_yaml(args.runtimes),
            "resource_flows": load_json_yaml(args.resource_flows),
            "behavior_traces": load_json_yaml(args.behavior_traces),
            "candidates": load_json_yaml(args.candidates),
            "entities": load_json_yaml(args.entities),
            "capabilities": load_json_yaml(args.capabilities),
            "claims": load_json_yaml(args.claims),
            "reviews": load_json_yaml(args.reviews),
            "evidence": load_json_yaml(args.evidence),
            "verification": load_json_yaml(args.verification),
            "ecological": load_json_yaml(args.ecological),
            "mapping": load_json_yaml(args.mapping),
        }
        texts = {
            "ledger": args.ledger.read_text(encoding="utf-8"),
        }
        result = validate(docs, texts)
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"ORGANISM_GENESIS_VALIDATION: {result['status']}")
        print(f"runtimes={result.get('runtime_instance_count', 0)}")
        print(f"resource_flows={result.get('resource_flow_count', 0)}")
        print(f"behavior_traces={result.get('behavior_trace_count', 0)}")
        print(f"candidates={result.get('candidate_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
