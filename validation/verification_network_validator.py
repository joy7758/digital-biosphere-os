#!/usr/bin/env python3
"""Validate the Digital Biosphere verification network registries.

Agent-readable contract:
- Registry inputs use JSON-compatible YAML 1.2 and no third-party package.
- Verifier types define vocabulary; they do not create verifier instances.
- Every run resolves to one existing verification and an in-scope verifier.
- Every trust relationship resolves entity, claim, evidence, verifier, and run.
- PASS proves registry consistency only; it does not execute a run, establish
  trust or independence, upgrade V/E/C, create an Agent, assign a capability,
  grant permission, certify an external project, or prove production fitness.
- Exit 0 means PASS; exit 1 means the network must fail closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

VERIFIER_TYPES = ("automated", "maintainer", "external", "experimental")
VALID_TYPE_STATUSES = {"defined", "deprecated", "retired"}
VALID_VERIFIER_STATUSES = {"proposed", "active", "suspended", "revoked", "retired"}
VALID_RUN_STATUSES = {"pending", "in_progress", "completed", "invalid", "revoked"}
VALID_RUN_RESULTS = {"pending", "pass", "fail", "inconclusive", "revoked"}
NODE_TYPES = ("entity", "claim", "evidence", "verifier", "verification_run")
VALID_RELATIONSHIP_STATUSES = {"pending", "active", "invalid", "revoked"}
RUN_ID_RE = re.compile(
    r"^dbio:verification-run:(?P<entity_id>[a-z0-9][a-z0-9.-]*):"
    r"(?P<verification_sequence>[0-9]{3}):(?P<run_sequence>[0-9]{3})$"
)
REQUIRED_RUN_FIELDS = {
    "verification_run_id",
    "verification_id",
    "verifier_id",
    "environment",
    "input_digest",
    "method",
    "result",
    "timestamp",
}
REQUIRED_RELATIONSHIP_FIELDS = {
    "relationship_id",
    "entity",
    "claim",
    "evidence",
    "verifier",
    "verification_run",
    "status",
    "trust_effect",
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
    records: list[Any], key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    """Index mappings by a required non-empty string key and reject duplicates."""
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


def expected_run_id(verification_id: str) -> str:
    return verification_id.replace(
        "dbio:verification:", "dbio:verification-run:", 1
    ) + ":001"


def validate(
    verifier_types_doc: dict[str, Any],
    verifiers_doc: dict[str, Any],
    verification_records_doc: dict[str, Any],
    runs_doc: dict[str, Any],
    graph_doc: dict[str, Any],
    entities_doc: dict[str, Any],
    claims_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    values = {
        "types": verifier_types_doc.get("types"),
        "verifiers": verifiers_doc.get("verifiers"),
        "verification_records": verification_records_doc.get("verification_records"),
        "verification_runs": runs_doc.get("verification_runs"),
        "nodes": graph_doc.get("nodes"),
        "relationships": graph_doc.get("relationships"),
        "entities": entities_doc.get("entities"),
        "claims": claims_doc.get("claims"),
        "evidence": evidence_doc.get("evidence"),
    }
    for label, value in values.items():
        if not isinstance(value, list):
            return {"status": "FAIL", "errors": [f"{label} must be a list"]}

    types = values["types"]
    verifiers = values["verifiers"]
    verification_records = values["verification_records"]
    runs = values["verification_runs"]
    nodes = values["nodes"]
    relationships = values["relationships"]
    entities = values["entities"]
    claims = values["claims"]
    evidence = values["evidence"]

    type_by_id = index_records(types, "type", "types", errors)
    configured_types = tuple(
        record.get("type") for record in types if isinstance(record, dict)
    )
    if configured_types != VERIFIER_TYPES:
        errors.append("verifier types must be ordered exactly automated, maintainer, external, experimental")
    for type_id, record in type_by_id.items():
        if type_id not in VERIFIER_TYPES:
            errors.append(f"unsupported verifier type definition: {type_id}")
        if record.get("status") not in VALID_TYPE_STATUSES:
            errors.append(f"verifier type {type_id}: invalid status")
        if record.get("identity_evidence_required") is not True:
            errors.append(f"verifier type {type_id}: identity evidence must be required")
        if record.get("trust_effect") != "none_by_type_alone":
            errors.append(f"verifier type {type_id}: type alone cannot establish trust")

    entity_by_id = index_records(entities, "entity_id", "entities", errors)
    claim_by_id = index_records(claims, "claim_id", "claims", errors)
    evidence_by_id = index_records(evidence, "evidence_id", "evidence", errors)
    verification_by_id = index_records(
        verification_records, "verification_id", "verification_records", errors
    )
    verifier_by_id = index_records(verifiers, "verifier_id", "verifiers", errors)
    run_by_id = index_records(runs, "verification_run_id", "verification_runs", errors)

    verifier_type_counts: Counter[str] = Counter()
    for verifier_id, verifier in verifier_by_id.items():
        verifier_type = verifier.get("type")
        if verifier_type not in type_by_id or verifier_type not in VERIFIER_TYPES:
            errors.append(f"{verifier_id}: invalid verifier type {verifier_type!r}")
        else:
            verifier_type_counts[verifier_type] += 1
        status = verifier.get("status")
        if status not in VALID_VERIFIER_STATUSES:
            errors.append(f"{verifier_id}: invalid verifier status {status!r}")
        lifecycle = verifier.get("lifecycle")
        if not isinstance(lifecycle, dict) or lifecycle.get("state") != status:
            errors.append(f"{verifier_id}: status must match lifecycle.state")
        scope = verifier.get("scope")
        if not isinstance(scope, dict):
            errors.append(f"{verifier_id}: scope must be a mapping")
            scope = {}
        environments = scope.get("environments")
        if not isinstance(environments, list) or not environments:
            errors.append(f"{verifier_id}: scope.environments must be non-empty")
        registry_authority = scope.get("registry_authority")
        if not isinstance(registry_authority, list) or not registry_authority:
            errors.append(f"{verifier_id}: scope.registry_authority must be non-empty")
        if scope.get("subject_rule") != "registered_verification_records_only":
            errors.append(f"{verifier_id}: unsupported subject scope rule")
        if scope.get("external_project_execution") is not False:
            errors.append(f"{verifier_id}: external project execution must remain false")

        identity_evidence = verifier.get("identity_evidence")
        if verifier_type == "external" and (
            not isinstance(identity_evidence, list) or not identity_evidence
        ):
            errors.append(f"{verifier_id}: external verifier requires identity evidence")
        if isinstance(identity_evidence, list):
            for identity_reference in identity_evidence:
                if not isinstance(identity_reference, str) or not identity_reference:
                    errors.append(f"{verifier_id}: malformed identity evidence reference")
                elif "://" not in identity_reference and not (root / identity_reference).is_file():
                    errors.append(
                        f"{verifier_id}: missing identity evidence {identity_reference}"
                    )

    verification_to_runs: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    run_status_counts: Counter[str] = Counter()
    run_result_counts: Counter[str] = Counter()
    for run_id, run in run_by_id.items():
        missing = REQUIRED_RUN_FIELDS - set(run)
        if missing:
            errors.append(f"{run_id}: missing run fields {sorted(missing)}")
        match = RUN_ID_RE.match(run_id)
        if not match:
            errors.append(f"{run_id}: malformed verification_run_id")
        verification_id = run.get("verification_id")
        verifier_id = run.get("verifier_id")
        verification = verification_by_id.get(verification_id)
        verifier = verifier_by_id.get(verifier_id)
        if verification is None:
            errors.append(f"{run_id}: unknown verification reference {verification_id!r}")
        else:
            verification_to_runs[verification_id].append(run)
            if run_id != expected_run_id(verification_id):
                errors.append(f"{run_id}: run id does not match verification id")
            if verifier_id != verification.get("verifier"):
                errors.append(f"{run_id}: verifier does not match verification record")
        if verifier is None:
            errors.append(f"{run_id}: unknown verifier reference {verifier_id!r}")
        else:
            scope = verifier.get("scope", {})
            environments = scope.get("environments", [])
            if run.get("environment") not in environments:
                errors.append(f"{run_id}: environment is outside verifier scope")
            if "registry/verification-records.yaml" not in scope.get(
                "registry_authority", []
            ):
                errors.append(f"{run_id}: verifier lacks verification registry scope")
            if verifier.get("status") != "active":
                errors.append(f"{run_id}: verifier is not active")

        status = run.get("status")
        result = run.get("result")
        if status not in VALID_RUN_STATUSES:
            errors.append(f"{run_id}: invalid run status {status!r}")
        else:
            run_status_counts[status] += 1
        if result not in VALID_RUN_RESULTS:
            errors.append(f"{run_id}: invalid run result {result!r}")
        else:
            run_result_counts[result] += 1
        if status == "pending":
            if result != "pending":
                errors.append(f"{run_id}: pending run requires result=pending")
            if run.get("timestamp") is not None:
                errors.append(f"{run_id}: pending run requires timestamp=null")
            if run.get("input_digest") is not None:
                errors.append(f"{run_id}: pending run requires input_digest=null")
            if run.get("method") is not None:
                errors.append(f"{run_id}: pending run requires method=null")
            if run.get("output_evidence") != []:
                errors.append(f"{run_id}: pending run cannot contain output evidence")
            if run.get("scope_evaluation_status") != "pending":
                errors.append(f"{run_id}: pending run scope must remain pending")
        if run.get("verification_level_effect") != "none":
            errors.append(f"{run_id}: run cannot upgrade verification level automatically")
        if run.get("capability_assignment_status") != "not_assigned":
            errors.append(f"{run_id}: run cannot assign a capability")
        if run.get("permission_status") != "not_granted":
            errors.append(f"{run_id}: run cannot grant permission")
        if run.get("agent_creation_status") != "not_created":
            errors.append(f"{run_id}: run cannot create an Agent")
        if "capability_id" in run or "verification_level" in run:
            errors.append(f"{run_id}: pending run cannot create capability_id or V level")

    missing_runs = set(verification_by_id) - set(verification_to_runs)
    extra_runs = set(verification_to_runs) - set(verification_by_id)
    if missing_runs:
        errors.append(f"verification records missing runs: {sorted(missing_runs)}")
    if extra_runs:
        errors.append(f"runs reference extra verifications: {sorted(extra_runs)}")
    if runs_doc.get("metadata", {}).get("one_pending_run_per_verification_baseline") is True:
        non_single = sorted(
            verification_id
            for verification_id, linked_runs in verification_to_runs.items()
            if len(linked_runs) != 1
        )
        if non_single:
            errors.append(f"v0.1 baseline requires one run per verification: {non_single}")

    node_by_id = index_records(nodes, "node_id", "nodes", errors)
    node_type_counts: Counter[str] = Counter()
    expected_nodes: dict[str, tuple[str, str]] = {}
    for identifier in entity_by_id:
        expected_nodes[identifier] = ("entity", "registry/entities.yaml")
    for identifier in claim_by_id:
        expected_nodes[identifier] = ("claim", "registry/capability-claims.yaml")
    for identifier in evidence_by_id:
        expected_nodes[identifier] = ("evidence", "registry/capability-evidence.yaml")
    for identifier in verifier_by_id:
        expected_nodes[identifier] = ("verifier", "registry/verifiers.yaml")
    for identifier in run_by_id:
        expected_nodes[identifier] = ("verification_run", "registry/verification-runs.yaml")
    for node_id, node in node_by_id.items():
        node_type = node.get("node_type")
        if node_type not in NODE_TYPES:
            errors.append(f"{node_id}: invalid trust-graph node type {node_type!r}")
        else:
            node_type_counts[node_type] += 1
        expected = expected_nodes.get(node_id)
        if expected is None:
            errors.append(f"{node_id}: trust-graph node does not resolve")
        else:
            expected_type, expected_registry = expected
            if node_type != expected_type or node.get("registry") != expected_registry:
                errors.append(f"{node_id}: trust-graph node authority mismatch")
            if node.get("record_id") != node_id:
                errors.append(f"{node_id}: trust-graph record_id mismatch")
        if node.get("reference_status") != "registered":
            errors.append(f"{node_id}: trust-graph reference must be registered")
    missing_nodes = set(expected_nodes) - set(node_by_id)
    if missing_nodes:
        errors.append(f"trust graph missing nodes: {sorted(missing_nodes)}")

    relationship_by_id = index_records(
        relationships, "relationship_id", "relationships", errors
    )
    relationships_by_run: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for relationship_id, relationship in relationship_by_id.items():
        missing = REQUIRED_RELATIONSHIP_FIELDS - set(relationship)
        if missing:
            errors.append(f"{relationship_id}: missing relationship fields {sorted(missing)}")
        references = {
            "entity": relationship.get("entity"),
            "claim": relationship.get("claim"),
            "evidence": relationship.get("evidence"),
            "verifier": relationship.get("verifier"),
            "verification_run": relationship.get("verification_run"),
        }
        for node_type, node_id in references.items():
            node = node_by_id.get(node_id)
            if node is None:
                errors.append(f"{relationship_id}: unknown {node_type} node {node_id!r}")
            elif node.get("node_type") != node_type:
                errors.append(f"{relationship_id}: {node_id} is not a {node_type} node")
        run_id = relationship.get("verification_run")
        run = run_by_id.get(run_id)
        if isinstance(run_id, str):
            relationships_by_run[run_id].append(relationship)
        if run is not None:
            verification = verification_by_id.get(run.get("verification_id"))
            if verification is not None:
                if relationship.get("entity") != verification.get("subject"):
                    errors.append(f"{relationship_id}: entity does not match verification subject")
                if relationship.get("claim") != verification.get("claim_id"):
                    errors.append(f"{relationship_id}: claim does not match verification")
                if relationship.get("evidence") not in verification.get("evidence", []):
                    errors.append(f"{relationship_id}: evidence does not match verification")
                if relationship.get("verifier") != run.get("verifier_id"):
                    errors.append(f"{relationship_id}: verifier does not match run")
        if relationship.get("status") not in VALID_RELATIONSHIP_STATUSES:
            errors.append(f"{relationship_id}: invalid relationship status")
        if relationship.get("status") == "pending" and relationship.get("trust_effect") != "none":
            errors.append(f"{relationship_id}: pending relationship cannot establish trust")
        if relationship.get("capability_effect") != "none":
            errors.append(f"{relationship_id}: trust graph cannot assign capability")
        if relationship.get("permission_effect") != "none":
            errors.append(f"{relationship_id}: trust graph cannot grant permission")

    missing_relationships = set(run_by_id) - set(relationships_by_run)
    if missing_relationships:
        errors.append(f"runs missing trust relationships: {sorted(missing_relationships)}")
    duplicate_relationships = sorted(
        run_id for run_id, linked in relationships_by_run.items() if len(linked) != 1
    )
    if duplicate_relationships:
        errors.append(f"runs require one trust relationship: {duplicate_relationships}")

    type_meta = verifier_types_doc.get("metadata", {})
    verifier_meta = verifiers_doc.get("metadata", {})
    run_meta = runs_doc.get("metadata", {})
    graph_meta = graph_doc.get("metadata", {})
    if type_meta.get("type_definition_count") != len(types):
        errors.append("verifier-type metadata count mismatch")
    if type_meta.get("registered_verifier_count") != len(verifiers):
        errors.append("verifier-type registered count mismatch")
    if verifier_meta.get("verifier_count") != len(verifiers):
        errors.append("verifier metadata count mismatch")
    for verifier_type in VERIFIER_TYPES:
        actual = verifier_type_counts.get(verifier_type, 0)
        if type_meta.get("current_type_distribution", {}).get(verifier_type, 0) != actual:
            errors.append(f"verifier-type distribution mismatch for {verifier_type}")
        if verifier_meta.get("type_distribution", {}).get(verifier_type, 0) != actual:
            errors.append(f"verifier distribution mismatch for {verifier_type}")
    if run_meta.get("verification_run_count") != len(runs):
        errors.append("verification-run metadata count mismatch")
    if run_meta.get("verification_record_count") != len(verification_records):
        errors.append("verification-run record count mismatch")
    for status in VALID_RUN_STATUSES:
        if run_meta.get("status_distribution", {}).get(status, 0) != run_status_counts.get(status, 0):
            errors.append(f"verification-run status distribution mismatch for {status}")
    for result in VALID_RUN_RESULTS:
        if run_meta.get("result_distribution", {}).get(result, 0) != run_result_counts.get(result, 0):
            errors.append(f"verification-run result distribution mismatch for {result}")
    if graph_meta.get("node_count") != len(nodes):
        errors.append("trust-graph node count mismatch")
    for node_type in NODE_TYPES:
        if graph_meta.get("node_type_distribution", {}).get(node_type, 0) != node_type_counts.get(node_type, 0):
            errors.append(f"trust-graph node distribution mismatch for {node_type}")
    if graph_meta.get("relationship_count") != len(relationships):
        errors.append("trust-graph relationship count mismatch")
    if graph_meta.get("trust_established_count") != 0:
        errors.append("pending trust graph must establish zero trust")
    for metadata, label in ((run_meta, "verification-run"), (graph_meta, "trust-graph")):
        if metadata.get("capability_assignment_count", metadata.get("assigned_capability_count")) != 0:
            errors.append(f"{label} metadata must report zero capability assignments")
        if metadata.get("permission_grant_count") != 0:
            errors.append(f"{label} metadata must report zero permission grants")

    return {
        "status": "FAIL" if errors else "PASS",
        "verifier_type_definition_count": len(types),
        "verifier_count": len(verifiers),
        "verifier_type_distribution": {
            verifier_type: verifier_type_counts.get(verifier_type, 0)
            for verifier_type in VERIFIER_TYPES
        },
        "verification_record_count": len(verification_records),
        "verification_run_count": len(runs),
        "verification_run_status_distribution": {
            status: run_status_counts.get(status, 0)
            for status in ("pending", "in_progress", "completed", "invalid", "revoked")
        },
        "trust_graph_node_count": len(nodes),
        "trust_graph_node_type_distribution": {
            node_type: node_type_counts.get(node_type, 0) for node_type in NODE_TYPES
        },
        "trust_graph_relationship_count": len(relationships),
        "trust_established_count": 0,
        "assigned_capability_count": 0,
        "permission_grant_count": 0,
        "agent_created_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verifier-types", type=Path, default=root / "registry" / "verifier-types.yaml")
    parser.add_argument("--verifiers", type=Path, default=root / "registry" / "verifiers.yaml")
    parser.add_argument("--verification-records", type=Path, default=root / "registry" / "verification-records.yaml")
    parser.add_argument("--runs", type=Path, default=root / "registry" / "verification-runs.yaml")
    parser.add_argument("--trust-graph", type=Path, default=root / "registry" / "trust-graph.yaml")
    parser.add_argument("--entities", type=Path, default=root / "registry" / "entities.yaml")
    parser.add_argument("--claims", type=Path, default=root / "registry" / "capability-claims.yaml")
    parser.add_argument("--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    try:
        result = validate(
            load_json_yaml(args.verifier_types),
            load_json_yaml(args.verifiers),
            load_json_yaml(args.verification_records),
            load_json_yaml(args.runs),
            load_json_yaml(args.trust_graph),
            load_json_yaml(args.entities),
            load_json_yaml(args.claims),
            load_json_yaml(args.evidence),
            root,
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"VERIFICATION_NETWORK_VALIDATION: {result['status']}")
        print(f"verifiers={result.get('verifier_count', 0)}")
        print(f"verification_runs={result.get('verification_run_count', 0)}")
        print(f"trust_graph_nodes={result.get('trust_graph_node_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
