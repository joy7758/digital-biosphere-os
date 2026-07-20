#!/usr/bin/env python3
"""Validate capability claims, evidence references, reviews, and maturity gates.

Agent-readable contract:
- Registry inputs use JSON-compatible YAML 1.2 and require no third-party package.
- entity-capabilities.yaml remains the source of the 78 potential-evidence records.
- A PASS proves structural consistency and evidence-path availability only.
- A PASS does not approve, assign, permission, execute, or autonomize a capability.
- Exit 0 means the local declarative verification layer is internally consistent.
- Exit 1 means the verification layer must fail closed.
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

VALID_CAPABILITY_TYPES = {
    "unknown",
    "information",
    "computation",
    "modification",
    "external_action",
    "self_evolution",
}
VALID_CLAIM_STATUSES = {
    "pending",
    "evidenced",
    "verified",
    "governed",
    "autonomous",
    "rejected",
    "withdrawn",
    "revoked",
}
VALID_REVIEW_DECISIONS = {"approved", "rejected", "needs_changes", "revoked"}
MATURITY_LEVELS = ("C0", "C1", "C2", "C3", "C4", "C5")
MATURITY_RANK = {level: index for index, level in enumerate(MATURITY_LEVELS)}
ACTIVE_STATUS_LEVEL = {
    "pending": "C1",
    "evidenced": "C2",
    "verified": "C3",
    "governed": "C4",
    "autonomous": "C5",
}
CLAIM_ID_RE = re.compile(
    r"^dbio:claim:(?P<entity_id>[a-z0-9][a-z0-9.-]*):(?P<sequence>[0-9]{3})$"
)
REQUIRED_CLAIM_FIELDS = {
    "claim_id",
    "entity_id",
    "capability_candidate",
    "capability_type",
    "scope",
    "environment",
    "side_effect",
    "evidence_sources",
    "status",
}
REQUIRED_REVIEW_FIELDS = {
    "review_id",
    "claim_id",
    "reviewer",
    "decision",
    "limitations",
    "timestamp",
}


def load_json_yaml(path: Path) -> dict[str, Any]:
    """Load one JSON-compatible YAML mapping."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain one mapping")
    return data


def is_unknown(value: Any) -> bool:
    """Return true when a bounded claim field is unresolved."""
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip() or value.strip().lower() == "unknown"
    if isinstance(value, dict):
        return value.get("status") == "unknown" or value.get("value") in {None, ""}
    return False


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate(
    claims_doc: dict[str, Any],
    reviews_doc: dict[str, Any],
    maturity_doc: dict[str, Any],
    entities_doc: dict[str, Any],
    relationships_doc: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    claims = claims_doc.get("claims")
    reviews = reviews_doc.get("reviews")
    levels = maturity_doc.get("levels")
    entities = entities_doc.get("entities")
    relationships = relationships_doc.get("entity_capability_relationships")

    for name, value in (
        ("claims", claims),
        ("reviews", reviews),
        ("levels", levels),
        ("entities", entities),
        ("entity_capability_relationships", relationships),
    ):
        if not isinstance(value, list):
            return {"status": "FAIL", "errors": [f"{name} must be a list"]}

    entity_ids = {
        entity.get("entity_id")
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("entity_id"), str)
    }

    potential_by_id: dict[str, dict[str, Any]] = {}
    for rel_index, relationship in enumerate(relationships):
        where = f"entity_capability_relationships[{rel_index}]"
        if not isinstance(relationship, dict):
            errors.append(f"{where} must be a mapping")
            continue
        entity_id = relationship.get("entity_id")
        potentials = relationship.get("potential_capability_evidence")
        if entity_id not in entity_ids:
            errors.append(f"{where}: unknown entity reference {entity_id!r}")
        if not isinstance(potentials, list):
            errors.append(f"{where}.potential_capability_evidence must be a list")
            continue
        for potential in potentials:
            if not isinstance(potential, dict):
                errors.append(f"{where}: potential evidence must be a mapping")
                continue
            evidence_id = potential.get("evidence_id")
            if not isinstance(evidence_id, str) or not evidence_id:
                errors.append(f"{where}: potential evidence requires evidence_id")
                continue
            if evidence_id in potential_by_id:
                errors.append(f"duplicate source potential evidence_id: {evidence_id}")
            potential_by_id[evidence_id] = {"entity_id": entity_id, **potential}

    claim_ids: set[str] = set()
    claim_by_id: dict[str, dict[str, Any]] = {}
    converted_source_ids: set[str] = set()
    classification_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    maturity_counts: Counter[str] = Counter()
    unresolved_counts: Counter[str] = Counter()
    evidence_paths: set[str] = set()

    for index, claim in enumerate(claims):
        where = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_CLAIM_FIELDS - set(claim)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")

        claim_id = claim.get("claim_id")
        entity_id = claim.get("entity_id")
        capability_candidate = claim.get("capability_candidate")
        capability_type = claim.get("capability_type")
        status = claim.get("status")
        maturity_level = claim.get("maturity_level")
        source_evidence_id = claim.get("source_evidence_id")

        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"{where}.claim_id must be a non-empty string")
        else:
            if claim_id in claim_ids:
                errors.append(f"duplicate claim_id: {claim_id}")
            claim_ids.add(claim_id)
            claim_by_id[claim_id] = claim
            match = CLAIM_ID_RE.match(claim_id)
            if not match:
                errors.append(f"{claim_id}: malformed claim_id")
            elif match.group("entity_id") != entity_id:
                errors.append(f"{claim_id}: claim_id entity does not match entity_id")

        if entity_id not in entity_ids:
            errors.append(f"{where}: unknown entity reference {entity_id!r}")
        if not isinstance(capability_candidate, str) or not capability_candidate.strip():
            errors.append(f"{where}.capability_candidate must be a non-empty string")
        if capability_type not in VALID_CAPABILITY_TYPES:
            errors.append(f"{where}: invalid capability_type {capability_type!r}")
        else:
            classification_counts[capability_type] += 1
        if status not in VALID_CLAIM_STATUSES:
            errors.append(f"{where}: invalid status {status!r}")
        else:
            status_counts[status] += 1
        if maturity_level not in MATURITY_RANK:
            errors.append(f"{where}: invalid maturity_level {maturity_level!r}")
        else:
            maturity_counts[maturity_level] += 1

        for field in ("scope", "environment", "side_effect"):
            if field not in claim:
                continue
            if is_unknown(claim.get(field)):
                unresolved_counts[field] += 1
        if capability_type == "unknown":
            unresolved_counts["capability_type"] += 1

        sources = claim.get("evidence_sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{where}.evidence_sources must be a non-empty list")
            sources = []
        elif len(sources) != len(set(sources)):
            errors.append(f"{where}.evidence_sources contains duplicates")
        for source in sources:
            if not isinstance(source, str) or not source:
                errors.append(f"{where}: evidence source must be a non-empty path string")
                continue
            evidence_paths.add(source)
            if not Path(source).is_file():
                errors.append(f"{where}: missing evidence source {source}")

        if not isinstance(source_evidence_id, str) or not source_evidence_id:
            errors.append(f"{where}.source_evidence_id must be a non-empty string")
        elif source_evidence_id in converted_source_ids:
            errors.append(f"duplicate source-evidence conversion: {source_evidence_id}")
        else:
            converted_source_ids.add(source_evidence_id)
            source_record = potential_by_id.get(source_evidence_id)
            if source_record is None:
                errors.append(f"{where}: unknown source_evidence_id {source_evidence_id}")
            else:
                if source_record.get("entity_id") != entity_id:
                    errors.append(f"{where}: source evidence entity mismatch")
                if source_record.get("statement") != capability_candidate:
                    errors.append(f"{where}: candidate statement differs from source evidence")
                if source_record.get("source_paths") != sources:
                    errors.append(f"{where}: evidence sources differ from source evidence")
                if source_record.get("status") != "potential_evidence_only":
                    errors.append(f"{where}: source record is not potential_evidence_only")

        if status in ACTIVE_STATUS_LEVEL and maturity_level != ACTIVE_STATUS_LEVEL[status]:
            errors.append(
                f"{where}: status {status!r} requires maturity {ACTIVE_STATUS_LEVEL[status]}"
            )
        if maturity_level in {"C2", "C3", "C4", "C5"}:
            for field in ("capability_type", "scope", "environment", "side_effect"):
                if is_unknown(claim.get(field)):
                    errors.append(f"{where}: {maturity_level} requires resolved {field}")
            if claim.get("evidence_assessment") in {
                None,
                "",
                "source_exists_content_not_reviewed",
            }:
                errors.append(f"{where}: {maturity_level} requires evidence sufficiency assessment")

        if claim.get("capability_assignment_status") != "not_assigned":
            errors.append(f"{where}: v0.1 claim cannot assign a capability")
        if claim.get("permission_status") != "not_granted":
            errors.append(f"{where}: v0.1 claim cannot grant permission")
        if "capability_id" in claim:
            errors.append(f"{where}: a claim must not create capability_id")

    missing_conversions = set(potential_by_id) - converted_source_ids
    extra_conversions = converted_source_ids - set(potential_by_id)
    if missing_conversions:
        errors.append(f"potential evidence missing claim conversion: {sorted(missing_conversions)}")
    if extra_conversions:
        errors.append(f"claim conversions without source evidence: {sorted(extra_conversions)}")

    review_ids: set[str] = set()
    review_by_id: dict[str, dict[str, Any]] = {}
    reviews_by_claim: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    decision_counts: Counter[str] = Counter()
    for index, review in enumerate(reviews):
        where = f"reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{where} must be a mapping")
            continue
        missing = REQUIRED_REVIEW_FIELDS - set(review)
        if missing:
            errors.append(f"{where} missing fields: {sorted(missing)}")
        review_id = review.get("review_id")
        claim_id = review.get("claim_id")
        decision = review.get("decision")
        if not isinstance(review_id, str) or not review_id:
            errors.append(f"{where}.review_id must be a non-empty string")
        elif review_id in review_ids:
            errors.append(f"duplicate review_id: {review_id}")
        else:
            review_ids.add(review_id)
            review_by_id[review_id] = review
        if claim_id not in claim_by_id:
            errors.append(f"{where}: unknown claim reference {claim_id!r}")
        else:
            reviews_by_claim[claim_id].append(review)
        if not isinstance(review.get("reviewer"), str) or not review.get("reviewer", "").strip():
            errors.append(f"{where}.reviewer must be attributable")
        if decision not in VALID_REVIEW_DECISIONS:
            errors.append(f"{where}: invalid decision {decision!r}")
        else:
            decision_counts[decision] += 1
        limitations = review.get("limitations")
        if not isinstance(limitations, (str, list)):
            errors.append(f"{where}.limitations must be a string or list")
        if not valid_timestamp(review.get("timestamp")):
            errors.append(f"{where}.timestamp must be ISO 8601")

    for claim_id, claim in claim_by_id.items():
        maturity_level = claim.get("maturity_level")
        status = claim.get("status")
        rank = MATURITY_RANK.get(maturity_level, -1)
        claim_reviews = reviews_by_claim.get(claim_id, [])
        approved_reviews = [
            review for review in claim_reviews
            if review.get("decision") == "approved"
        ]
        if rank >= MATURITY_RANK["C3"]:
            if not approved_reviews:
                errors.append(f"{claim_id}: C3 or higher requires an approved review")
            verification_review_id = claim.get("verification_review_id")
            verification_review = review_by_id.get(verification_review_id)
            if (
                verification_review is None
                or verification_review.get("claim_id") != claim_id
                or verification_review.get("decision") != "approved"
            ):
                errors.append(f"{claim_id}: invalid or missing verification_review_id")
        if rank >= MATURITY_RANK["C4"]:
            if not claim.get("governance_evidence"):
                errors.append(f"{claim_id}: C4 or higher requires governance_evidence")
            if not claim.get("revocation_mechanism"):
                errors.append(f"{claim_id}: C4 or higher requires revocation_mechanism")
        if rank >= MATURITY_RANK["C5"]:
            authorization = claim.get("autonomy_authorization")
            if not isinstance(authorization, dict) or not authorization:
                errors.append(f"{claim_id}: C5 requires explicit autonomy_authorization")
            if not claim.get("runtime_enforcement_evidence"):
                errors.append(f"{claim_id}: C5 requires runtime_enforcement_evidence")
        if status == "revoked":
            revoked_reviews = [
                review for review in claim_reviews
                if review.get("decision") == "revoked"
            ]
            if not revoked_reviews or not claim.get("revocation_record"):
                errors.append(f"{claim_id}: revoked status requires review and revocation_record")

    level_ids = [level.get("level") for level in levels if isinstance(level, dict)]
    if tuple(level_ids) != MATURITY_LEVELS:
        errors.append("maturity levels must be ordered exactly C0 through C5")
    if len(level_ids) != len(set(level_ids)):
        errors.append("maturity levels must be unique")

    claim_meta = claims_doc.get("metadata", {})
    review_meta = reviews_doc.get("metadata", {})
    expected_classification = claim_meta.get("classification_counts", {})
    expected_maturity = claim_meta.get("maturity_distribution", {})
    current_distribution = maturity_doc.get("current_distribution", {})
    if claim_meta.get("claim_count") != len(claims):
        errors.append("claim metadata.claim_count mismatch")
    if claim_meta.get("pending_claim_count") != status_counts.get("pending", 0):
        errors.append("claim metadata.pending_claim_count mismatch")
    if claim_meta.get("source_potential_evidence_count") != len(potential_by_id):
        errors.append("claim metadata.source_potential_evidence_count mismatch")
    if claim_meta.get("reviewed_claim_count") != len(reviews_by_claim):
        errors.append("claim metadata.reviewed_claim_count mismatch")
    approved_claim_count = sum(
        any(review.get("decision") == "approved" for review in claim_reviews)
        for claim_reviews in reviews_by_claim.values()
    )
    if claim_meta.get("approved_claim_count") != approved_claim_count:
        errors.append("claim metadata.approved_claim_count mismatch")
    if claim_meta.get("assigned_capability_count") != 0:
        errors.append("claim metadata must report zero assigned capabilities")
    if claim_meta.get("permission_grant_count") != 0:
        errors.append("claim metadata must report zero permission grants")
    for capability_type in VALID_CAPABILITY_TYPES:
        if expected_classification.get(capability_type, 0) != classification_counts.get(capability_type, 0):
            errors.append(f"claim classification count mismatch for {capability_type}")
    for level in MATURITY_LEVELS:
        actual = maturity_counts.get(level, 0)
        if expected_maturity.get(level, 0) != actual:
            errors.append(f"claim maturity count mismatch for {level}")
        if current_distribution.get(level, 0) != actual:
            errors.append(f"maturity registry current_distribution mismatch for {level}")
    if review_meta.get("review_count") != len(reviews):
        errors.append("review metadata.review_count mismatch")
    for decision in VALID_REVIEW_DECISIONS:
        if review_meta.get("decision_counts", {}).get(decision, 0) != decision_counts.get(decision, 0):
            errors.append(f"review decision count mismatch for {decision}")

    ordered_types = (
        "unknown",
        "information",
        "computation",
        "modification",
        "external_action",
        "self_evolution",
    )
    return {
        "status": "FAIL" if errors else "PASS",
        "entity_count": len(entity_ids),
        "source_potential_evidence_count": len(potential_by_id),
        "capability_claim_count": len(claims),
        "unique_evidence_source_path_count": len(evidence_paths),
        "claim_classification_counts": {
            key: classification_counts.get(key, 0) for key in ordered_types
        },
        "claim_status_counts": {
            key: status_counts.get(key, 0)
            for key in (
                "pending",
                "evidenced",
                "verified",
                "governed",
                "autonomous",
                "rejected",
                "withdrawn",
                "revoked",
            )
        },
        "maturity_distribution": {
            level: maturity_counts.get(level, 0) for level in MATURITY_LEVELS
        },
        "review_count": len(reviews),
        "approved_review_count": decision_counts.get("approved", 0),
        "assigned_capability_count": 0,
        "permission_grant_count": 0,
        "unresolved_field_counts": {
            key: unresolved_counts.get(key, 0)
            for key in ("capability_type", "scope", "environment", "side_effect")
        },
        "errors": errors,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claims", type=Path, default=root / "registry" / "capability-claims.yaml"
    )
    parser.add_argument(
        "--reviews", type=Path, default=root / "registry" / "capability-reviews.yaml"
    )
    parser.add_argument(
        "--maturity", type=Path, default=root / "registry" / "capability-maturity.yaml"
    )
    parser.add_argument(
        "--entities", type=Path, default=root / "registry" / "entities.yaml"
    )
    parser.add_argument(
        "--relationships",
        type=Path,
        default=root / "registry" / "entity-capabilities.yaml",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        result = validate(
            load_json_yaml(args.claims),
            load_json_yaml(args.reviews),
            load_json_yaml(args.maturity),
            load_json_yaml(args.entities),
            load_json_yaml(args.relationships),
        )
    except (OSError, ValueError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"CAPABILITY_CLAIM_VALIDATION: {result['status']}")
        print(f"claims={result.get('capability_claim_count', 0)}")
        print(f"reviews={result.get('review_count', 0)}")
        print(f"approved_reviews={result.get('approved_review_count', 0)}")
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
