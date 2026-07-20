#!/usr/bin/env python3
"""Validate Digital Biosphere verifier identities and verification records.

Agent-readable contract:
- Registry inputs use JSON-compatible YAML 1.2 and need no third-party package.
- Every verification record resolves to a verifier, entity, claim, and evidence.
- V-levels are sequential and cannot exceed the current evidence ceiling.
- PASS proves structural consistency only; it does not verify, approve, assign,
  permission, execute, certify, or autonomize a capability.
- Exit 0 means PASS; exit 1 means the verification layer must fail closed.
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

VERIFICATION_LEVELS = ("V0", "V1", "V2", "V3", "V4", "V5")
VERIFICATION_RANK = {level: index for index, level in enumerate(VERIFICATION_LEVELS)}
EVIDENCE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5")
EVIDENCE_RANK = {level: index for index, level in enumerate(EVIDENCE_LEVELS)}
TRUST_LEVELS = (
    "unknown",
    "self_asserted",
    "local_automated",
    "reproducible",
    "independent",
    "continuous",
)
TRUST_RANK = {level: index for index, level in enumerate(TRUST_LEVELS)}
MINIMUM_TRUST_BY_VERIFICATION = {
    "V0": "unknown",
    "V1": "self_asserted",
    "V2": "local_automated",
    "V3": "reproducible",
    "V4": "independent",
    "V5": "continuous",
}
MINIMUM_EVIDENCE_BY_VERIFICATION = {
    "V0": "E0",
    "V1": "E1",
    "V2": "E2",
    "V3": "E3",
    "V4": "E4",
    "V5": "E5",
}
EVIDENCE_SUPPORT_CEILING = {
    "E0": "V0",
    "E1": "V1",
    "E2": "V2",
    "E3": "V3",
    "E4": "V4",
    "E5": "V5",
}
REQUIRED_PREDECESSORS = {
    "V0": (),
    "V1": ("V0",),
    "V2": ("V0", "V1"),
    "V3": ("V0", "V1", "V2"),
    "V4": ("V0", "V1", "V2", "V3"),
    "V5": ("V0", "V1", "V2", "V3", "V4"),
}
VALID_VERIFIER_TYPES = {
    "automated",
    "maintainer",
    "external",
    "experimental",
}
VALID_VERIFIER_STATES = {"proposed", "active", "suspended", "revoked", "retired"}
VALID_RECORD_STATUSES = {"pending", "in_progress", "completed", "invalid", "revoked"}
VALID_DECISIONS = {"pending", "pass", "fail", "inconclusive", "revoked"}
VERIFIER_ID_RE = re.compile(
    r"^dbio:verifier:(?P<name>[a-z0-9][a-z0-9.-]*):"
    r"(?P<version>v[a-zA-Z0-9][a-zA-Z0-9._-]*)$"
)
VERIFICATION_ID_RE = re.compile(
    r"^dbio:verification:(?P<entity_id>[a-z0-9][a-z0-9.-]*):"
    r"(?P<sequence>[0-9]{3})$"
)
REQUIRED_VERIFIER_FIELDS = {
    "verifier_id",
    "type",
    "status",
    "scope",
    "method",
    "trust_level",
    "evidence_required",
}
REQUIRED_RECORD_FIELDS = {
    "verification_id",
    "subject",
    "claim_id",
    "verifier",
    "evidence",
    "decision",
    "timestamp",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load a JSON-compatible YAML document as one mapping."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one mapping")
    return data


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate(
    verifiers_doc: dict[str, Any],
    records_doc: dict[str, Any],
    levels_doc: dict[str, Any],
    entities_doc: dict[str, Any],
    claims_doc: dict[str, Any],
    evidence_doc: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    verifiers = verifiers_doc.get("verifiers")
    records = records_doc.get("verification_records")
    levels = levels_doc.get("levels")
    entities = entities_doc.get("entities")
    claims = claims_doc.get("claims")
    evidence_records = evidence_doc.get("evidence")
    for name, value in (
        ("verifiers", verifiers),
        ("verification_records", records),
        ("levels", levels),
        ("entities", entities),
        ("claims", claims),
        ("evidence", evidence_records),
    ):
        if not isinstance(value, list):
            return {"status": "FAIL", "errors": [f"{name} must be a list"]}

    entity_ids = {
        entity.get("entity_id")
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("entity_id"), str)
    }
    claim_by_id: dict[str, dict[str, Any]] = {}
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be a mapping")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"claims[{index}].claim_id must be a non-empty string")
            continue
        if claim_id in claim_by_id:
            errors.append(f"duplicate claim_id: {claim_id}")
        claim_by_id[claim_id] = claim

    evidence_by_id: dict[str, dict[str, Any]] = {}
    evidence_by_claim: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, evidence in enumerate(evidence_records):
        if not isinstance(evidence, dict):
            errors.append(f"evidence[{index}] must be a mapping")
            continue
        evidence_id = evidence.get("evidence_id")
        claim_id = evidence.get("claim_id")
        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f"evidence[{index}].evidence_id must be a non-empty string")
            continue
        if evidence_id in evidence_by_id:
            errors.append(f"duplicate evidence_id: {evidence_id}")
        evidence_by_id[evidence_id] = evidence
        if isinstance(claim_id, str):
            evidence_by_claim[claim_id].append(evidence)

    configured_levels: list[str] = []
    for index, level_record in enumerate(levels):
        where = f"levels[{index}]"
        if not isinstance(level_record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        level = level_record.get("verification_level")
        configured_levels.append(level)
        if level not in VERIFICATION_RANK:
            errors.append(f"{where}: invalid verification_level {level!r}")
            continue
        if tuple(level_record.get("required_predecessors", [])) != REQUIRED_PREDECESSORS[level]:
            errors.append(f"{where}: predecessor definition mismatch for {level}")
        if level_record.get("minimum_trust_level") != MINIMUM_TRUST_BY_VERIFICATION[level]:
            errors.append(f"{where}: minimum trust definition mismatch for {level}")
        if level_record.get("minimum_required_evidence_level") != MINIMUM_EVIDENCE_BY_VERIFICATION[level]:
            errors.append(f"{where}: minimum evidence definition mismatch for {level}")
    if tuple(configured_levels) != VERIFICATION_LEVELS:
        errors.append("verification levels must be ordered exactly V0 through V5")
    if len(configured_levels) != len(set(configured_levels)):
        errors.append("verification levels must be unique")
    if tuple(levels_doc.get("trust_levels", [])) != TRUST_LEVELS:
        errors.append("trust levels must be ordered exactly from unknown through continuous")
    if levels_doc.get("evidence_support_ceiling") != EVIDENCE_SUPPORT_CEILING:
        errors.append("evidence-to-verification support ceiling mismatch")

    verifier_ids: set[str] = set()
    verifier_by_id: dict[str, dict[str, Any]] = {}
    verifier_type_counts: Counter[str] = Counter()
    trust_counts: Counter[str] = Counter()
    for index, verifier in enumerate(verifiers):
        where = f"verifiers[{index}]"
        if not isinstance(verifier, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_VERIFIER_FIELDS - set(verifier)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        verifier_id = verifier.get("verifier_id")
        verifier_type = verifier.get("type")
        trust_level = verifier.get("trust_level")
        if not isinstance(verifier_id, str) or not VERIFIER_ID_RE.match(verifier_id):
            errors.append(f"{where}: malformed verifier_id")
        elif verifier_id in verifier_ids:
            errors.append(f"duplicate verifier_id: {verifier_id}")
        else:
            verifier_ids.add(verifier_id)
            verifier_by_id[verifier_id] = verifier
        if verifier_type not in VALID_VERIFIER_TYPES:
            errors.append(f"{where}: invalid verifier type {verifier_type!r}")
        else:
            verifier_type_counts[verifier_type] += 1
        if trust_level not in TRUST_RANK:
            errors.append(f"{where}: invalid trust_level {trust_level!r}")
        else:
            trust_counts[trust_level] += 1
        if not isinstance(verifier.get("scope"), dict) or not verifier.get("scope"):
            errors.append(f"{where}.scope must be a non-empty mapping")
        if not isinstance(verifier.get("method"), dict) or not verifier.get("method"):
            errors.append(f"{where}.method must be a non-empty mapping")
        evidence_required = verifier.get("evidence_required")
        if not isinstance(evidence_required, list) or not evidence_required:
            errors.append(f"{where}.evidence_required must be a non-empty list")
        lifecycle = verifier.get("lifecycle")
        if not isinstance(lifecycle, dict) or lifecycle.get("state") not in VALID_VERIFIER_STATES:
            errors.append(f"{where}: invalid verifier lifecycle")
        if verifier.get("status") not in VALID_VERIFIER_STATES:
            errors.append(f"{where}: invalid verifier status")
        elif isinstance(lifecycle, dict) and verifier.get("status") != lifecycle.get("state"):
            errors.append(f"{where}: verifier status must match lifecycle.state")
        implementation_evidence = verifier.get("implementation_evidence", [])
        if not isinstance(implementation_evidence, list):
            errors.append(f"{where}.implementation_evidence must be a list")
        else:
            for source in implementation_evidence:
                if not isinstance(source, str) or not source:
                    errors.append(f"{where}: implementation evidence path must be non-empty")
                elif not (root / source).is_file():
                    errors.append(f"{where}: missing implementation evidence {source}")
        if verifier_type == "automated" and trust_level == "local_automated":
            if verifier.get("independence_status") != "not_independent":
                errors.append(f"{where}: local automated verifier cannot claim independence")
            if verifier.get("agent_status") != "not_an_agent":
                errors.append(f"{where}: local verifier must remain not_an_agent")
            if verifier.get("reviewer_status") != "not_a_reviewer":
                errors.append(f"{where}: local verifier must remain not_a_reviewer")
            authority = verifier.get("authority")
            if not isinstance(authority, dict):
                errors.append(f"{where}.authority must be a mapping")
            else:
                for forbidden in (
                    "may_approve_capability",
                    "may_assign_capability",
                    "may_grant_permission",
                    "may_claim_independent_verification",
                ):
                    if authority.get(forbidden) is not False:
                        errors.append(f"{where}: {forbidden} must be false")

    verification_ids: set[str] = set()
    records_by_claim: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    decision_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    referenced_evidence_ids: set[str] = set()
    for index, record in enumerate(records):
        where = f"verification_records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_RECORD_FIELDS - set(record)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        verification_id = record.get("verification_id")
        subject = record.get("subject")
        claim_id = record.get("claim_id")
        verifier_id = record.get("verifier")
        evidence_ids = record.get("evidence")
        decision = record.get("decision")
        timestamp = record.get("timestamp")
        level = record.get("verification_level")
        status = record.get("status")
        claim = claim_by_id.get(claim_id)
        verifier = verifier_by_id.get(verifier_id)

        if not isinstance(verification_id, str) or not verification_id:
            errors.append(f"{where}.verification_id must be a non-empty string")
        else:
            if verification_id in verification_ids:
                errors.append(f"duplicate verification_id: {verification_id}")
            verification_ids.add(verification_id)
            match = VERIFICATION_ID_RE.match(verification_id)
            if not match:
                errors.append(f"{verification_id}: malformed verification_id")
            elif claim is not None:
                expected = f"dbio:verification:{claim_id.removeprefix('dbio:claim:')}"
                if verification_id != expected:
                    errors.append(f"{verification_id}: verification_id does not match claim_id")

        if subject not in entity_ids:
            errors.append(f"{where}: unknown subject entity {subject!r}")
        if claim is None:
            errors.append(f"{where}: unknown claim reference {claim_id!r}")
        else:
            records_by_claim[claim_id].append(record)
            if subject != claim.get("entity_id"):
                errors.append(f"{where}: subject does not match claim entity")
        if verifier is None:
            errors.append(f"{where}: unknown verifier reference {verifier_id!r}")
        elif verifier.get("lifecycle", {}).get("state") != "active" and decision == "pass":
            errors.append(f"{where}: inactive verifier cannot issue pass")

        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"{where}.evidence must be a non-empty list")
            evidence_ids = []
        elif len(evidence_ids) != len(set(evidence_ids)):
            errors.append(f"{where}.evidence contains duplicate references")
        for evidence_id in evidence_ids:
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                errors.append(f"{where}: unknown evidence reference {evidence_id!r}")
                continue
            referenced_evidence_ids.add(evidence_id)
            if evidence.get("claim_id") != claim_id:
                errors.append(f"{where}: evidence does not belong to claim")

        if decision not in VALID_DECISIONS:
            errors.append(f"{where}: invalid decision {decision!r}")
        else:
            decision_counts[decision] += 1
        if status not in VALID_RECORD_STATUSES:
            errors.append(f"{where}: invalid status {status!r}")
        else:
            status_counts[status] += 1
        if level not in VERIFICATION_RANK:
            errors.append(f"{where}: invalid verification_level {level!r}")
        else:
            level_counts[level] += 1

        method_evidence = record.get("method_evidence")
        independence = record.get("independence")
        if status == "pending":
            if decision != "pending":
                errors.append(f"{where}: pending status requires decision=pending")
            if timestamp is not None:
                errors.append(f"{where}: pending record requires timestamp=null")
            if level != "V0":
                errors.append(f"{where}: pending record must remain V0")
            if method_evidence != []:
                errors.append(f"{where}: pending record cannot contain method evidence")
            if not isinstance(independence, dict) or independence.get("status") != "not_assessed":
                errors.append(f"{where}: pending record cannot claim assessed independence")
        elif status == "in_progress":
            if decision != "pending" or timestamp is not None:
                errors.append(f"{where}: in_progress requires pending decision and timestamp=null")
        elif status == "completed":
            if decision not in {"pass", "fail", "inconclusive"}:
                errors.append(f"{where}: completed record requires pass, fail, or inconclusive")
            if not valid_timestamp(timestamp):
                errors.append(f"{where}: completed record requires ISO 8601 timestamp")
            if not isinstance(method_evidence, list) or not method_evidence:
                errors.append(f"{where}: completed record requires method evidence")
        elif status == "revoked":
            if decision != "revoked" or not valid_timestamp(timestamp):
                errors.append(f"{where}: revoked record requires decision=revoked and timestamp")
            if not record.get("revocation_record"):
                errors.append(f"{where}: revoked record requires revocation_record")

        if level in VERIFICATION_RANK and verifier is not None:
            trust_level = verifier.get("trust_level")
            minimum_trust = MINIMUM_TRUST_BY_VERIFICATION[level]
            if trust_level not in TRUST_RANK or TRUST_RANK[trust_level] < TRUST_RANK[minimum_trust]:
                errors.append(f"{where}: verifier trust {trust_level!r} cannot support {level}")

        if level in VERIFICATION_RANK and claim_id in evidence_by_claim:
            active_evidence_levels = [
                evidence.get("evidence_type")
                for evidence in evidence_by_claim[claim_id]
                if evidence.get("evidence_type") in EVIDENCE_RANK
                and evidence.get("status") not in {"invalid", "revoked"}
            ]
            highest_evidence = (
                max(active_evidence_levels, key=EVIDENCE_RANK.get)
                if active_evidence_levels else "E0"
            )
            ceiling = EVIDENCE_SUPPORT_CEILING[highest_evidence]
            if VERIFICATION_RANK[level] > VERIFICATION_RANK[ceiling]:
                errors.append(
                    f"{where}: {highest_evidence} supports at most {ceiling}, not {level}"
                )

        if level in {"V3", "V4", "V5"}:
            reproducibility = record.get("reproducibility")
            if not isinstance(reproducibility, dict) or not reproducibility:
                errors.append(f"{where}: {level} requires reproducibility evidence")
        if level in {"V4", "V5"}:
            if not isinstance(independence, dict) or independence.get("status") != "verified_independent":
                errors.append(f"{where}: {level} requires verified independence")
            elif independence.get("conflict_of_interest") not in {"none_declared", "managed_and_disclosed"}:
                errors.append(f"{where}: {level} requires conflict-of-interest disposition")
        if level == "V5":
            observation = record.get("continuous_observation")
            required_observation = {
                "window_start",
                "window_end",
                "coverage",
                "drift",
                "incidents",
                "expiry",
                "revocation_mechanism",
            }
            if not isinstance(observation, dict) or not required_observation.issubset(observation):
                errors.append(f"{where}: V5 requires complete continuous observation evidence")

        if record.get("capability_assignment_status") != "not_assigned":
            errors.append(f"{where}: verification cannot assign a capability")
        if record.get("permission_status") != "not_granted":
            errors.append(f"{where}: verification cannot grant permission")
        if "capability_id" in record:
            errors.append(f"{where}: verification must not create capability_id")

    for claim_id, claim_records in records_by_claim.items():
        active_levels = {
            record.get("verification_level")
            for record in claim_records
            if record.get("verification_level") in VERIFICATION_RANK
            and record.get("status") not in {"invalid", "revoked"}
        }
        for level in sorted(active_levels, key=VERIFICATION_RANK.get):
            missing = set(REQUIRED_PREDECESSORS[level]) - active_levels
            if missing:
                errors.append(f"{claim_id}: {level} skips required predecessors {sorted(missing)}")

    missing_claim_records = set(claim_by_id) - set(records_by_claim)
    extra_claim_records = set(records_by_claim) - set(claim_by_id)
    if missing_claim_records:
        errors.append(f"claims missing verification records: {sorted(missing_claim_records)}")
    if extra_claim_records:
        errors.append(f"verification records reference extra claims: {sorted(extra_claim_records)}")
    if records_doc.get("metadata", {}).get("one_to_one_claim_baseline") is True:
        duplicate_claim_records = sorted(
            claim_id for claim_id, claim_records in records_by_claim.items()
            if len(claim_records) != 1
        )
        if duplicate_claim_records:
            errors.append(f"v0.1 baseline requires one record per claim: {duplicate_claim_records}")

    verifier_meta = verifiers_doc.get("metadata", {})
    record_meta = records_doc.get("metadata", {})
    current_distribution = levels_doc.get("current_distribution", {})
    if verifier_meta.get("verifier_count") != len(verifiers):
        errors.append("verifier metadata.verifier_count mismatch")
    for trust_level in TRUST_LEVELS:
        if verifier_meta.get("trust_level_distribution", {}).get(trust_level, 0) != trust_counts.get(trust_level, 0):
            errors.append(f"verifier trust-level distribution mismatch for {trust_level}")
    if record_meta.get("verification_record_count") != len(records):
        errors.append("verification metadata.verification_record_count mismatch")
    if record_meta.get("claim_count") != len(claims):
        errors.append("verification metadata.claim_count mismatch")
    if record_meta.get("pending_count") != status_counts.get("pending", 0):
        errors.append("verification metadata.pending_count mismatch")
    if record_meta.get("assigned_capability_count") != 0:
        errors.append("verification metadata must report zero assigned capabilities")
    if record_meta.get("permission_grant_count") != 0:
        errors.append("verification metadata must report zero permission grants")
    for decision in VALID_DECISIONS:
        if record_meta.get("decision_counts", {}).get(decision, 0) != decision_counts.get(decision, 0):
            errors.append(f"verification decision count mismatch for {decision}")
    for level in VERIFICATION_LEVELS:
        actual = level_counts.get(level, 0)
        if record_meta.get("verification_level_distribution", {}).get(level, 0) != actual:
            errors.append(f"verification level distribution mismatch for {level}")
        if current_distribution.get(level, 0) != actual:
            errors.append(f"verification-level current_distribution mismatch for {level}")

    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entity_ids),
        "verifier_count": len(verifiers),
        "verifier_type_distribution": {
            verifier_type: verifier_type_counts.get(verifier_type, 0)
            for verifier_type in sorted(VALID_VERIFIER_TYPES)
        },
        "verifier_trust_distribution": {
            trust_level: trust_counts.get(trust_level, 0) for trust_level in TRUST_LEVELS
        },
        "capability_claim_count": len(claims),
        "verification_record_count": len(records),
        "verification_level_distribution": {
            level: level_counts.get(level, 0) for level in VERIFICATION_LEVELS
        },
        "verification_status_distribution": {
            status: status_counts.get(status, 0)
            for status in ("pending", "in_progress", "completed", "invalid", "revoked")
        },
        "decision_distribution": {
            decision: decision_counts.get(decision, 0)
            for decision in ("pending", "pass", "fail", "inconclusive", "revoked")
        },
        "referenced_evidence_count": len(referenced_evidence_ids),
        "assigned_capability_count": 0,
        "permission_grant_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verifiers", type=Path, default=root / "registry" / "verifiers.yaml"
    )
    parser.add_argument(
        "--records", type=Path, default=root / "registry" / "verification-records.yaml"
    )
    parser.add_argument(
        "--levels", type=Path, default=root / "registry" / "verification-level.yaml"
    )
    parser.add_argument(
        "--entities", type=Path, default=root / "registry" / "entities.yaml"
    )
    parser.add_argument(
        "--claims", type=Path, default=root / "registry" / "capability-claims.yaml"
    )
    parser.add_argument(
        "--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml"
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        result = validate(
            load_json_yaml(args.verifiers),
            load_json_yaml(args.records),
            load_json_yaml(args.levels),
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
        print(f"VERIFICATION_VALIDATION: {result['status']}")
        print(f"verifiers={result.get('verifier_count', 0)}")
        print(f"verification_records={result.get('verification_record_count', 0)}")
        print(f"pending={result.get('decision_distribution', {}).get('pending', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
