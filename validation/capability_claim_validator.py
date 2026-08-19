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


class _Validator:
    def __init__(
        self,
        claims_doc: dict[str, Any],
        reviews_doc: dict[str, Any],
        maturity_doc: dict[str, Any],
        entities_doc: dict[str, Any],
        relationships_doc: dict[str, Any],
    ):
        self.claims_doc = claims_doc
        self.reviews_doc = reviews_doc
        self.maturity_doc = maturity_doc
        self.entities_doc = entities_doc
        self.relationships_doc = relationships_doc

        self.errors: list[str] = []
        self.claims = claims_doc.get("claims")
        self.reviews = reviews_doc.get("reviews")
        self.levels = maturity_doc.get("levels")
        self.entities = entities_doc.get("entities")
        self.relationships = relationships_doc.get("entity_capability_relationships")

        self.entity_ids: set[str] = set()
        self.potential_by_id: dict[str, dict[str, Any]] = {}
        self.claim_ids: set[str] = set()
        self.claim_by_id: dict[str, dict[str, Any]] = {}
        self.converted_source_ids: set[str] = set()
        self.classification_counts: Counter[str] = Counter()
        self.status_counts: Counter[str] = Counter()
        self.maturity_counts: Counter[str] = Counter()
        self.unresolved_counts: Counter[str] = Counter()
        self.evidence_paths: set[str] = set()
        self.review_ids: set[str] = set()
        self.review_by_id: dict[str, dict[str, Any]] = {}
        self.reviews_by_claim: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        self.decision_counts: Counter[str] = Counter()

    def run(self) -> dict[str, Any]:
        if not self._check_base_lists():
            return {"status": "FAIL", "errors": self.errors}

        self._collect_entities()
        self._process_relationships()
        self._process_claims()
        self._check_conversions()
        self._process_reviews()
        self._check_maturity()
        self._check_levels()
        self._validate_metadata()

        return self._build_result()

    def _check_base_lists(self) -> bool:
        for name, value in (
            ("claims", self.claims),
            ("reviews", self.reviews),
            ("levels", self.levels),
            ("entities", self.entities),
            ("entity_capability_relationships", self.relationships),
        ):
            if not isinstance(value, list):
                self.errors.append(f"{name} must be a list")
                return False
        return True

    def _collect_entities(self) -> None:
        self.entity_ids = {
            entity.get("entity_id")
            for entity in self.entities
            if isinstance(entity, dict) and isinstance(entity.get("entity_id"), str)
        }

    def _process_relationships(self) -> None:
        for rel_index, relationship in enumerate(self.relationships):
            where = f"entity_capability_relationships[{rel_index}]"
            if not isinstance(relationship, dict):
                self.errors.append(f"{where} must be a mapping")
                continue
            entity_id = relationship.get("entity_id")
            potentials = relationship.get("potential_capability_evidence")
            if entity_id not in self.entity_ids:
                self.errors.append(f"{where}: unknown entity reference {entity_id!r}")
            if not isinstance(potentials, list):
                self.errors.append(f"{where}.potential_capability_evidence must be a list")
                continue
            for potential in potentials:
                if not isinstance(potential, dict):
                    self.errors.append(f"{where}: potential evidence must be a mapping")
                    continue
                evidence_id = potential.get("evidence_id")
                if not isinstance(evidence_id, str) or not evidence_id:
                    self.errors.append(f"{where}: potential evidence requires evidence_id")
                    continue
                if evidence_id in self.potential_by_id:
                    self.errors.append(f"duplicate source potential evidence_id: {evidence_id}")
                self.potential_by_id[evidence_id] = {"entity_id": entity_id, **potential}

    def _process_claims(self) -> None:
        for index, claim in enumerate(self.claims):
            where = f"claims[{index}]"
            if not isinstance(claim, dict):
                self.errors.append(f"{where} must be a mapping")
                continue
            missing = REQUIRED_CLAIM_FIELDS - set(claim)
            if missing:
                self.errors.append(f"{where} missing fields: {sorted(missing)}")

            claim_id = claim.get("claim_id")
            entity_id = claim.get("entity_id")
            capability_candidate = claim.get("capability_candidate")
            capability_type = claim.get("capability_type")
            status = claim.get("status")
            maturity_level = claim.get("maturity_level")
            source_evidence_id = claim.get("source_evidence_id")

            if not isinstance(claim_id, str) or not claim_id:
                self.errors.append(f"{where}.claim_id must be a non-empty string")
            else:
                if claim_id in self.claim_ids:
                    self.errors.append(f"duplicate claim_id: {claim_id}")
                self.claim_ids.add(claim_id)
                self.claim_by_id[claim_id] = claim
                match = CLAIM_ID_RE.match(claim_id)
                if not match:
                    self.errors.append(f"{claim_id}: malformed claim_id")
                elif match.group("entity_id") != entity_id:
                    self.errors.append(f"{claim_id}: claim_id entity does not match entity_id")

            if entity_id not in self.entity_ids:
                self.errors.append(f"{where}: unknown entity reference {entity_id!r}")
            if not isinstance(capability_candidate, str) or not capability_candidate.strip():
                self.errors.append(f"{where}.capability_candidate must be a non-empty string")
            if capability_type not in VALID_CAPABILITY_TYPES:
                self.errors.append(f"{where}: invalid capability_type {capability_type!r}")
            else:
                self.classification_counts[capability_type] += 1
            if status not in VALID_CLAIM_STATUSES:
                self.errors.append(f"{where}: invalid status {status!r}")
            else:
                self.status_counts[status] += 1
            if maturity_level not in MATURITY_RANK:
                self.errors.append(f"{where}: invalid maturity_level {maturity_level!r}")
            else:
                self.maturity_counts[maturity_level] += 1

            for field in ("scope", "environment", "side_effect"):
                if field not in claim:
                    continue
                if is_unknown(claim.get(field)):
                    self.unresolved_counts[field] += 1
            if capability_type == "unknown":
                self.unresolved_counts["capability_type"] += 1

            sources = claim.get("evidence_sources")
            if not isinstance(sources, list) or not sources:
                self.errors.append(f"{where}.evidence_sources must be a non-empty list")
                sources = []
            elif len(sources) != len(set(sources)):
                self.errors.append(f"{where}.evidence_sources contains duplicates")
            for source in sources:
                if not isinstance(source, str) or not source:
                    self.errors.append(f"{where}: evidence source must be a non-empty path string")
                    continue
                self.evidence_paths.add(source)
                if not Path(source).is_file():
                    self.errors.append(f"{where}: missing evidence source {source}")

            if not isinstance(source_evidence_id, str) or not source_evidence_id:
                self.errors.append(f"{where}.source_evidence_id must be a non-empty string")
            elif source_evidence_id in self.converted_source_ids:
                self.errors.append(f"duplicate source-evidence conversion: {source_evidence_id}")
            else:
                self.converted_source_ids.add(source_evidence_id)
                source_record = self.potential_by_id.get(source_evidence_id)
                if source_record is None:
                    self.errors.append(f"{where}: unknown source_evidence_id {source_evidence_id}")
                else:
                    if source_record.get("entity_id") != entity_id:
                        self.errors.append(f"{where}: source evidence entity mismatch")
                    if source_record.get("statement") != capability_candidate:
                        self.errors.append(f"{where}: candidate statement differs from source evidence")
                    if source_record.get("source_paths") != sources:
                        self.errors.append(f"{where}: evidence sources differ from source evidence")
                    if source_record.get("status") != "potential_evidence_only":
                        self.errors.append(f"{where}: source record is not potential_evidence_only")

            if status in ACTIVE_STATUS_LEVEL and maturity_level != ACTIVE_STATUS_LEVEL[status]:
                self.errors.append(
                    f"{where}: status {status!r} requires maturity {ACTIVE_STATUS_LEVEL[status]}"
                )
            if maturity_level in {"C2", "C3", "C4", "C5"}:
                for field in ("capability_type", "scope", "environment", "side_effect"):
                    if is_unknown(claim.get(field)):
                        self.errors.append(f"{where}: {maturity_level} requires resolved {field}")
                if claim.get("evidence_assessment") in {
                    None,
                    "",
                    "source_exists_content_not_reviewed",
                }:
                    self.errors.append(f"{where}: {maturity_level} requires evidence sufficiency assessment")

            if claim.get("capability_assignment_status") != "not_assigned":
                self.errors.append(f"{where}: v0.1 claim cannot assign a capability")
            if claim.get("permission_status") != "not_granted":
                self.errors.append(f"{where}: v0.1 claim cannot grant permission")
            if "capability_id" in claim:
                self.errors.append(f"{where}: a claim must not create capability_id")

    def _check_conversions(self) -> None:
        missing_conversions = set(self.potential_by_id) - self.converted_source_ids
        extra_conversions = self.converted_source_ids - set(self.potential_by_id)
        if missing_conversions:
            self.errors.append(f"potential evidence missing claim conversion: {sorted(missing_conversions)}")
        if extra_conversions:
            self.errors.append(f"claim conversions without source evidence: {sorted(extra_conversions)}")

    def _process_reviews(self) -> None:
        for index, review in enumerate(self.reviews):
            where = f"reviews[{index}]"
            if not isinstance(review, dict):
                self.errors.append(f"{where} must be a mapping")
                continue
            missing = REQUIRED_REVIEW_FIELDS - set(review)
            if missing:
                self.errors.append(f"{where} missing fields: {sorted(missing)}")
            review_id = review.get("review_id")
            claim_id = review.get("claim_id")
            decision = review.get("decision")
            if not isinstance(review_id, str) or not review_id:
                self.errors.append(f"{where}.review_id must be a non-empty string")
            elif review_id in self.review_ids:
                self.errors.append(f"duplicate review_id: {review_id}")
            else:
                self.review_ids.add(review_id)
                self.review_by_id[review_id] = review
            if claim_id not in self.claim_by_id:
                self.errors.append(f"{where}: unknown claim reference {claim_id!r}")
            else:
                self.reviews_by_claim[claim_id].append(review)
            if not isinstance(review.get("reviewer"), str) or not review.get("reviewer", "").strip():
                self.errors.append(f"{where}.reviewer must be attributable")
            if decision not in VALID_REVIEW_DECISIONS:
                self.errors.append(f"{where}: invalid decision {decision!r}")
            else:
                self.decision_counts[decision] += 1
            limitations = review.get("limitations")
            if not isinstance(limitations, (str, list)):
                self.errors.append(f"{where}.limitations must be a string or list")
            if not valid_timestamp(review.get("timestamp")):
                self.errors.append(f"{where}.timestamp must be ISO 8601")

    def _check_maturity(self) -> None:
        for claim_id, claim in self.claim_by_id.items():
            maturity_level = claim.get("maturity_level")
            status = claim.get("status")
            rank = MATURITY_RANK.get(maturity_level, -1)
            claim_reviews = self.reviews_by_claim.get(claim_id, [])
            approved_reviews = [
                review for review in claim_reviews
                if review.get("decision") == "approved"
            ]
            if rank >= MATURITY_RANK["C3"]:
                if not approved_reviews:
                    self.errors.append(f"{claim_id}: C3 or higher requires an approved review")
                verification_review_id = claim.get("verification_review_id")
                verification_review = self.review_by_id.get(verification_review_id)
                if (
                    verification_review is None
                    or verification_review.get("claim_id") != claim_id
                    or verification_review.get("decision") != "approved"
                ):
                    self.errors.append(f"{claim_id}: invalid or missing verification_review_id")
            if rank >= MATURITY_RANK["C4"]:
                if not claim.get("governance_evidence"):
                    self.errors.append(f"{claim_id}: C4 or higher requires governance_evidence")
                if not claim.get("revocation_mechanism"):
                    self.errors.append(f"{claim_id}: C4 or higher requires revocation_mechanism")
            if rank >= MATURITY_RANK["C5"]:
                authorization = claim.get("autonomy_authorization")
                if not isinstance(authorization, dict) or not authorization:
                    self.errors.append(f"{claim_id}: C5 requires explicit autonomy_authorization")
                if not claim.get("runtime_enforcement_evidence"):
                    self.errors.append(f"{claim_id}: C5 requires runtime_enforcement_evidence")
            if status == "revoked":
                revoked_reviews = [
                    review for review in claim_reviews
                    if review.get("decision") == "revoked"
                ]
                if not revoked_reviews or not claim.get("revocation_record"):
                    self.errors.append(f"{claim_id}: revoked status requires review and revocation_record")

    def _check_levels(self) -> None:
        level_ids = [level.get("level") for level in self.levels if isinstance(level, dict)]
        if tuple(level_ids) != MATURITY_LEVELS:
            self.errors.append("maturity levels must be ordered exactly C0 through C5")
        if len(level_ids) != len(set(level_ids)):
            self.errors.append("maturity levels must be unique")

    def _validate_metadata(self) -> None:
        claim_meta = self.claims_doc.get("metadata", {})
        review_meta = self.reviews_doc.get("metadata", {})
        expected_classification = claim_meta.get("classification_counts", {})
        expected_maturity = claim_meta.get("maturity_distribution", {})
        current_distribution = self.maturity_doc.get("current_distribution", {})
        if claim_meta.get("claim_count") != len(self.claims):
            self.errors.append("claim metadata.claim_count mismatch")
        if claim_meta.get("pending_claim_count") != self.status_counts.get("pending", 0):
            self.errors.append("claim metadata.pending_claim_count mismatch")
        if claim_meta.get("source_potential_evidence_count") != len(self.potential_by_id):
            self.errors.append("claim metadata.source_potential_evidence_count mismatch")
        if claim_meta.get("reviewed_claim_count") != len(self.reviews_by_claim):
            self.errors.append("claim metadata.reviewed_claim_count mismatch")
        approved_claim_count = sum(
            any(review.get("decision") == "approved" for review in claim_reviews)
            for claim_reviews in self.reviews_by_claim.values()
        )
        if claim_meta.get("approved_claim_count") != approved_claim_count:
            self.errors.append("claim metadata.approved_claim_count mismatch")
        if claim_meta.get("assigned_capability_count") != 0:
            self.errors.append("claim metadata must report zero assigned capabilities")
        if claim_meta.get("permission_grant_count") != 0:
            self.errors.append("claim metadata must report zero permission grants")
        for capability_type in VALID_CAPABILITY_TYPES:
            if expected_classification.get(capability_type, 0) != self.classification_counts.get(capability_type, 0):
                self.errors.append(f"claim classification count mismatch for {capability_type}")
        for level in MATURITY_LEVELS:
            actual = self.maturity_counts.get(level, 0)
            if expected_maturity.get(level, 0) != actual:
                self.errors.append(f"claim maturity count mismatch for {level}")
            if current_distribution.get(level, 0) != actual:
                self.errors.append(f"maturity registry current_distribution mismatch for {level}")
        if review_meta.get("review_count") != len(self.reviews):
            self.errors.append("review metadata.review_count mismatch")
        for decision in VALID_REVIEW_DECISIONS:
            if review_meta.get("decision_counts", {}).get(decision, 0) != self.decision_counts.get(decision, 0):
                self.errors.append(f"review decision count mismatch for {decision}")

    def _build_result(self) -> dict[str, Any]:
        ordered_types = (
            "unknown",
            "information",
            "computation",
            "modification",
            "external_action",
            "self_evolution",
        )
        return {
            "status": "FAIL" if self.errors else "PASS",
            "entity_count": len(self.entity_ids),
            "source_potential_evidence_count": len(self.potential_by_id),
            "capability_claim_count": len(self.claims),
            "unique_evidence_source_path_count": len(self.evidence_paths),
            "claim_classification_counts": {
                key: self.classification_counts.get(key, 0) for key in ordered_types
            },
            "claim_status_counts": {
                key: self.status_counts.get(key, 0)
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
                level: self.maturity_counts.get(level, 0) for level in MATURITY_LEVELS
            },
            "review_count": len(self.reviews),
            "approved_review_count": self.decision_counts.get("approved", 0),
            "assigned_capability_count": 0,
            "permission_grant_count": 0,
            "unresolved_field_counts": {
                key: self.unresolved_counts.get(key, 0)
                for key in ("capability_type", "scope", "environment", "side_effect")
            },
            "errors": self.errors,
        }


def validate(
    claims_doc: dict[str, Any],
    reviews_doc: dict[str, Any],
    maturity_doc: dict[str, Any],
    entities_doc: dict[str, Any],
    relationships_doc: dict[str, Any],
) -> dict[str, Any]:
    return _Validator(
        claims_doc, reviews_doc, maturity_doc, entities_doc, relationships_doc
    ).run()


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
