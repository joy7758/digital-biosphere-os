#!/usr/bin/env python3
"""Validate Digital Biosphere capability-evidence governance records.

Agent-readable contract:
- Registry inputs use JSON-compatible YAML 1.2 and need no third-party package.
- Every v0.1 evidence record must trace to one existing capability claim.
- E-levels are sequential; a record cannot skip required predecessor evidence.
- Capability maturity cannot exceed the support of current, non-invalid evidence.
- PASS proves structural consistency and path availability only; it does not
  approve evidence, capabilities, assignments, permissions, or autonomy.
- Exit 0 means PASS; exit 1 means the evidence layer must fail closed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

EVIDENCE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5")
EVIDENCE_RANK = {level: index for index, level in enumerate(EVIDENCE_LEVELS)}
CAPABILITY_LEVELS = ("C0", "C1", "C2", "C3", "C4", "C5")
CAPABILITY_RANK = {level: index for index, level in enumerate(CAPABILITY_LEVELS)}
MINIMUM_EVIDENCE_BY_CAPABILITY = {
    "C0": "E0",
    "C1": "E1",
    "C2": "E2",
    "C3": "E2",
    "C4": "E3",
    "C5": "E5",
}
MAXIMUM_CAPABILITY_BY_EVIDENCE = {
    "E0": "C0",
    "E1": "C1",
    "E2": "C3",
    "E3": "C4",
    "E4": "C4",
    "E5": "C5",
}
REQUIRED_PREDECESSORS = {
    "E0": (),
    "E1": (),
    "E2": ("E1",),
    "E3": ("E1", "E2"),
    "E4": ("E1", "E2", "E3"),
    "E5": ("E1", "E2", "E3", "E4"),
}
VALID_EVIDENCE_STATUSES = {
    "pending",
    "assessed",
    "verified",
    "independently_verified",
    "observed",
    "invalid",
    "revoked",
}
VALID_STATUS_BY_LEVEL = {
    "E0": {"pending", "invalid", "revoked"},
    "E1": {"pending", "assessed", "invalid", "revoked"},
    "E2": {"assessed", "verified", "invalid", "revoked"},
    "E3": {"verified", "invalid", "revoked"},
    "E4": {"independently_verified", "invalid", "revoked"},
    "E5": {"observed", "invalid", "revoked"},
}
EVIDENCE_ID_RE = re.compile(
    r"^dbio:evidence:(?P<entity_id>[a-z0-9][a-z0-9.-]*):(?P<sequence>[0-9]{3})$"
)
PROFILE_ID_RE = re.compile(
    r"^dbio:capability-profile:(?P<entity_id>[a-z0-9][a-z0-9.-]*):(?P<sequence>[0-9]{3})$"
)
REQUIRED_EVIDENCE_FIELDS = {
    "evidence_id",
    "claim_id",
    "evidence_type",
    "source",
    "artifact",
    "verification",
    "status",
}
REQUIRED_PROFILE_FIELDS = {
    "entity",
    "capability",
    "scope",
    "environment",
    "limitation",
    "evidence_level",
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


def validate(
    evidence_doc: dict[str, Any],
    evidence_types_doc: dict[str, Any],
    claims_doc: dict[str, Any],
    profiles_doc: dict[str, Any],
    reviews_doc: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    evidence_records = evidence_doc.get("evidence")
    type_records = evidence_types_doc.get("levels")
    claims = claims_doc.get("claims")
    profiles = profiles_doc.get("profiles")
    reviews = reviews_doc.get("reviews")
    for name, value in (
        ("evidence", evidence_records),
        ("levels", type_records),
        ("claims", claims),
        ("profiles", profiles),
        ("reviews", reviews),
    ):
        if not isinstance(value, list):
            return {"status": "FAIL", "errors": [f"{name} must be a list"]}

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

    approved_claim_ids = {
        review.get("claim_id")
        for review in reviews
        if isinstance(review, dict) and review.get("decision") == "approved"
    }

    configured_levels: list[str] = []
    for index, record in enumerate(type_records):
        where = f"levels[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        evidence_type = record.get("evidence_type")
        configured_levels.append(evidence_type)
        if evidence_type not in EVIDENCE_RANK:
            errors.append(f"{where}: invalid evidence_type {evidence_type!r}")
            continue
        if tuple(record.get("required_predecessors", [])) != REQUIRED_PREDECESSORS[evidence_type]:
            errors.append(f"{where}: predecessor definition mismatch for {evidence_type}")
        if record.get("maximum_supported_capability_maturity") != MAXIMUM_CAPABILITY_BY_EVIDENCE[evidence_type]:
            errors.append(f"{where}: maximum capability support mismatch for {evidence_type}")
    if tuple(configured_levels) != EVIDENCE_LEVELS:
        errors.append("evidence levels must be ordered exactly E0 through E5")
    if len(configured_levels) != len(set(configured_levels)):
        errors.append("evidence levels must be unique")

    configured_minimums = evidence_types_doc.get("capability_support_rules", {}).get(
        "minimum_evidence_by_capability_maturity", {}
    )
    if configured_minimums != MINIMUM_EVIDENCE_BY_CAPABILITY:
        errors.append("minimum evidence-to-capability support mapping mismatch")

    evidence_ids: set[str] = set()
    evidence_by_claim: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    evidence_distribution: Counter[str] = Counter()
    evidence_status_counts: Counter[str] = Counter()
    artifact_paths: set[str] = set()

    for index, record in enumerate(evidence_records):
        where = f"evidence[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_EVIDENCE_FIELDS - set(record)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        evidence_id = record.get("evidence_id")
        claim_id = record.get("claim_id")
        evidence_type = record.get("evidence_type")
        status = record.get("status")
        claim = claim_by_id.get(claim_id)

        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f"{where}.evidence_id must be a non-empty string")
        else:
            if evidence_id in evidence_ids:
                errors.append(f"duplicate evidence_id: {evidence_id}")
            evidence_ids.add(evidence_id)
            match = EVIDENCE_ID_RE.match(evidence_id)
            if not match:
                errors.append(f"{evidence_id}: malformed evidence_id")
            elif claim is not None:
                expected_suffix = claim_id.removeprefix("dbio:claim:")
                if evidence_id != f"dbio:evidence:{expected_suffix}":
                    errors.append(f"{evidence_id}: evidence_id does not match claim_id")

        if claim is None:
            errors.append(f"{where}: unknown claim reference {claim_id!r}")
        else:
            evidence_by_claim[claim_id].append(record)
        if evidence_type not in EVIDENCE_RANK:
            errors.append(f"{where}: invalid evidence_type {evidence_type!r}")
        else:
            evidence_distribution[evidence_type] += 1
        if status not in VALID_EVIDENCE_STATUSES:
            errors.append(f"{where}: invalid status {status!r}")
        else:
            evidence_status_counts[status] += 1
            if evidence_type in VALID_STATUS_BY_LEVEL and status not in VALID_STATUS_BY_LEVEL[evidence_type]:
                errors.append(f"{where}: status {status!r} is invalid for {evidence_type}")

        source = record.get("source")
        if not isinstance(source, dict):
            errors.append(f"{where}.source must be a mapping")
        else:
            if source.get("registry") != "registry/capability-claims.yaml":
                errors.append(f"{where}: source registry must be capability-claims.yaml")
            if source.get("claim_id") != claim_id:
                errors.append(f"{where}: source claim_id mismatch")
            if claim is not None and source.get("source_evidence_id") != claim.get("source_evidence_id"):
                errors.append(f"{where}: source potential-evidence reference mismatch")

        artifact = record.get("artifact")
        paths: list[Any] = []
        if not isinstance(artifact, dict):
            errors.append(f"{where}.artifact must be a mapping")
        else:
            paths = artifact.get("paths")
            if not isinstance(paths, list) or not paths:
                errors.append(f"{where}.artifact.paths must be a non-empty list")
                paths = []
            elif len(paths) != len(set(paths)):
                errors.append(f"{where}.artifact.paths contains duplicates")
            for path_value in paths:
                if not isinstance(path_value, str) or not path_value:
                    errors.append(f"{where}: artifact path must be a non-empty string")
                    continue
                artifact_paths.add(path_value)
                if not Path(path_value).is_file():
                    errors.append(f"{where}: missing artifact reference {path_value}")
            if evidence_type == "E1" and claim is not None:
                if paths != claim.get("evidence_sources"):
                    errors.append(f"{where}: E1 artifact references differ from claim sources")
                if artifact.get("status") != "referenced_not_assessed":
                    errors.append(f"{where}: E1 artifact must remain referenced_not_assessed")
                for field in ("integrity_status", "content_relevance"):
                    if artifact.get(field) != "not_assessed":
                        errors.append(f"{where}: E1 {field} must remain not_assessed")
            if evidence_type in {"E2", "E3", "E4", "E5"}:
                if artifact.get("integrity_status") in {None, "unknown", "not_assessed"}:
                    errors.append(f"{where}: {evidence_type} requires assessed artifact integrity")
                if artifact.get("content_relevance") in {None, "unknown", "not_assessed"}:
                    errors.append(f"{where}: {evidence_type} requires assessed content relevance")

        verification = record.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{where}.verification must be a mapping")
        elif status == "pending":
            if verification.get("status") != "not_reviewed":
                errors.append(f"{where}: pending evidence must remain not_reviewed")
            for field in ("reviewer", "review_id", "verified_at", "method"):
                if verification.get(field) is not None:
                    errors.append(f"{where}: pending evidence cannot simulate {field}")

        supported_maturity = record.get("supported_capability_maturity")
        if supported_maturity not in CAPABILITY_RANK:
            errors.append(f"{where}: invalid supported_capability_maturity {supported_maturity!r}")
        elif evidence_type in EVIDENCE_RANK:
            maximum = MAXIMUM_CAPABILITY_BY_EVIDENCE[evidence_type]
            if CAPABILITY_RANK[supported_maturity] > CAPABILITY_RANK[maximum]:
                errors.append(f"{where}: {evidence_type} cannot support {supported_maturity}")
        if record.get("capability_assignment_status") != "not_assigned":
            errors.append(f"{where}: evidence cannot assign a capability")
        if record.get("permission_status") != "not_granted":
            errors.append(f"{where}: evidence cannot grant permission")
        if "capability_id" in record:
            errors.append(f"{where}: evidence must not create capability_id")

    effective_level_by_claim: dict[str, str] = {}
    for claim_id, claim in claim_by_id.items():
        records = evidence_by_claim.get(claim_id, [])
        active_types = {
            record.get("evidence_type")
            for record in records
            if record.get("evidence_type") in EVIDENCE_RANK
            and record.get("status") not in {"invalid", "revoked"}
        }
        for evidence_type in sorted(active_types, key=EVIDENCE_RANK.get):
            missing = set(REQUIRED_PREDECESSORS[evidence_type]) - active_types
            if missing:
                errors.append(
                    f"{claim_id}: {evidence_type} skips required predecessors {sorted(missing)}"
                )
        highest = max(active_types, key=EVIDENCE_RANK.get) if active_types else "E0"
        effective_level_by_claim[claim_id] = highest
        maturity = claim.get("maturity_level")
        if maturity not in CAPABILITY_RANK:
            errors.append(f"{claim_id}: invalid capability maturity {maturity!r}")
            continue
        minimum = MINIMUM_EVIDENCE_BY_CAPABILITY[maturity]
        if EVIDENCE_RANK[highest] < EVIDENCE_RANK[minimum]:
            errors.append(
                f"{claim_id}: capability maturity {maturity} requires {minimum}, current maximum is {highest}"
            )
        if maturity == "C3" and EVIDENCE_RANK[highest] <= EVIDENCE_RANK["E1"]:
            errors.append(f"{claim_id}: E1 cannot support C3")
        if maturity == "C4" and EVIDENCE_RANK[highest] <= EVIDENCE_RANK["E2"]:
            errors.append(f"{claim_id}: E2 cannot support C4")
        if maturity == "C5" and EVIDENCE_RANK[highest] <= EVIDENCE_RANK["E3"]:
            errors.append(f"{claim_id}: E3 cannot automatically support C5")
        if CAPABILITY_RANK[maturity] >= CAPABILITY_RANK["C3"] and claim_id not in approved_claim_ids:
            errors.append(f"{claim_id}: C3 or higher requires an approved capability review")
        if CAPABILITY_RANK[maturity] >= CAPABILITY_RANK["C4"]:
            if not claim.get("governance_evidence") or not claim.get("revocation_mechanism"):
                errors.append(f"{claim_id}: C4 or higher requires governance and revocation evidence")
        if maturity == "C5":
            if not claim.get("autonomy_authorization") or not claim.get("runtime_enforcement_evidence"):
                errors.append(f"{claim_id}: C5 requires autonomy authorization and runtime enforcement evidence")

    missing_claim_evidence = set(claim_by_id) - set(evidence_by_claim)
    extra_claim_evidence = set(evidence_by_claim) - set(claim_by_id)
    if missing_claim_evidence:
        errors.append(f"claims missing evidence records: {sorted(missing_claim_evidence)}")
    if extra_claim_evidence:
        errors.append(f"evidence references unknown claims: {sorted(extra_claim_evidence)}")

    profile_ids: set[str] = set()
    profiled_claim_ids: set[str] = set()
    profile_evidence_distribution: Counter[str] = Counter()
    profile_status_counts: Counter[str] = Counter()
    for index, profile in enumerate(profiles):
        where = f"profiles[{index}]"
        if not isinstance(profile, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_PROFILE_FIELDS - set(profile)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        profile_id = profile.get("profile_id")
        claim_id = profile.get("claim_id")
        claim = claim_by_id.get(claim_id)
        if not isinstance(profile_id, str) or not PROFILE_ID_RE.match(profile_id):
            errors.append(f"{where}: malformed profile_id")
        elif profile_id in profile_ids:
            errors.append(f"duplicate profile_id: {profile_id}")
        else:
            profile_ids.add(profile_id)
        if claim is None:
            errors.append(f"{where}: unknown claim reference {claim_id!r}")
        else:
            if claim_id in profiled_claim_ids:
                errors.append(f"duplicate capability profile for claim: {claim_id}")
            profiled_claim_ids.add(claim_id)
            expected_id = f"dbio:capability-profile:{claim_id.removeprefix('dbio:claim:')}"
            if profile_id != expected_id:
                errors.append(f"{where}: profile_id does not match claim_id")
            if profile.get("entity") != claim.get("entity_id"):
                errors.append(f"{where}: profile entity does not match claim")
            if profile.get("capability") != claim.get("capability_candidate"):
                errors.append(f"{where}: profile capability differs from claim candidate")
            if profile.get("scope") != claim.get("scope"):
                errors.append(f"{where}: profile scope differs from claim")
            if profile.get("environment") != claim.get("environment"):
                errors.append(f"{where}: profile environment differs from claim")
            if profile.get("evidence_level") != effective_level_by_claim.get(claim_id):
                errors.append(f"{where}: profile evidence_level differs from current evidence")
        evidence_level = profile.get("evidence_level")
        if evidence_level not in EVIDENCE_RANK:
            errors.append(f"{where}: invalid evidence_level {evidence_level!r}")
        else:
            profile_evidence_distribution[evidence_level] += 1
        status = profile.get("status")
        profile_status_counts[status] += 1
        limitations = profile.get("limitation")
        if not isinstance(limitations, (str, list)) or not limitations:
            errors.append(f"{where}.limitation must be non-empty")
        if profile.get("capability_assignment_status") != "not_assigned":
            errors.append(f"{where}: profile cannot assign a capability")
        if profile.get("permission_status") != "not_granted":
            errors.append(f"{where}: profile cannot grant permission")
        if "capability_id" in profile:
            errors.append(f"{where}: profile must not create capability_id")

    if set(claim_by_id) != profiled_claim_ids:
        errors.append("capability profiles must cover every claim exactly once")

    evidence_meta = evidence_doc.get("metadata", {})
    type_distribution = evidence_types_doc.get("current_distribution", {})
    profile_meta = profiles_doc.get("metadata", {})
    if evidence_meta.get("evidence_count") != len(evidence_records):
        errors.append("evidence metadata.evidence_count mismatch")
    if evidence_meta.get("pending_evidence_count") != evidence_status_counts.get("pending", 0):
        errors.append("evidence metadata.pending_evidence_count mismatch")
    if evidence_meta.get("claim_count") != len(claims):
        errors.append("evidence metadata.claim_count mismatch")
    if evidence_meta.get("assigned_capability_count") != 0:
        errors.append("evidence metadata must report zero assigned capabilities")
    if evidence_meta.get("permission_grant_count") != 0:
        errors.append("evidence metadata must report zero permission grants")
    for level in EVIDENCE_LEVELS:
        actual = evidence_distribution.get(level, 0)
        if evidence_meta.get("evidence_distribution", {}).get(level, 0) != actual:
            errors.append(f"evidence distribution mismatch for {level}")
        if type_distribution.get(level, 0) != actual:
            errors.append(f"evidence-type current_distribution mismatch for {level}")
    if profile_meta.get("profile_count") != len(profiles):
        errors.append("profile metadata.profile_count mismatch")
    if profile_meta.get("pending_profile_count") != profile_status_counts.get("pending_candidate", 0):
        errors.append("profile metadata.pending_profile_count mismatch")
    if profile_meta.get("assigned_capability_count") != 0:
        errors.append("profile metadata must report zero assigned capabilities")
    if profile_meta.get("permission_grant_count") != 0:
        errors.append("profile metadata must report zero permission grants")
    for level in EVIDENCE_LEVELS:
        if profile_meta.get("evidence_level_distribution", {}).get(level, 0) != profile_evidence_distribution.get(level, 0):
            errors.append(f"profile evidence-level distribution mismatch for {level}")

    capability_maturity_distribution = Counter(
        claim.get("maturity_level") for claim in claims
    )
    return {
        "status": "FAIL" if errors else "PASS",
        "capability_claim_count": len(claims),
        "capability_evidence_count": len(evidence_records),
        "capability_profile_count": len(profiles),
        "unique_artifact_reference_path_count": len(artifact_paths),
        "evidence_level_distribution": {
            level: evidence_distribution.get(level, 0) for level in EVIDENCE_LEVELS
        },
        "evidence_status_distribution": {
            status: evidence_status_counts.get(status, 0)
            for status in (
                "pending",
                "assessed",
                "verified",
                "independently_verified",
                "observed",
                "invalid",
                "revoked",
            )
        },
        "capability_maturity_distribution": {
            level: capability_maturity_distribution.get(level, 0)
            for level in CAPABILITY_LEVELS
        },
        "approved_review_count": sum(
            1 for review in reviews
            if isinstance(review, dict) and review.get("decision") == "approved"
        ),
        "assigned_capability_count": 0,
        "permission_grant_count": 0,
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, default=root / "registry" / "capability-evidence.yaml"
    )
    parser.add_argument(
        "--evidence-types", type=Path, default=root / "registry" / "evidence-types.yaml"
    )
    parser.add_argument(
        "--claims", type=Path, default=root / "registry" / "capability-claims.yaml"
    )
    parser.add_argument(
        "--profiles", type=Path, default=root / "registry" / "capability-profiles.yaml"
    )
    parser.add_argument(
        "--reviews", type=Path, default=root / "registry" / "capability-reviews.yaml"
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        result = validate(
            load_json_yaml(args.evidence),
            load_json_yaml(args.evidence_types),
            load_json_yaml(args.claims),
            load_json_yaml(args.profiles),
            load_json_yaml(args.reviews),
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"EVIDENCE_VALIDATION: {result['status']}")
        print(f"evidence={result.get('capability_evidence_count', 0)}")
        print(f"profiles={result.get('capability_profile_count', 0)}")
        print(f"approved_reviews={result.get('approved_review_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
