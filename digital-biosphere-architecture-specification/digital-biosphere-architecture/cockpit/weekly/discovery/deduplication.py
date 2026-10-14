"""Exact-identity deduplication with fail-closed name collision handling."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .fingerprint import candidate_fingerprint
from .identity import canonical_identity, normalized_name, source_identity_key


def _known_indexes(entries: list[dict[str, Any]]):
    by_source: dict[str, set[str]] = defaultdict(set)
    by_name: dict[str, set[str]] = defaultdict(set)
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        candidate_id = entry["candidate_id"]
        by_id[candidate_id] = entry
        by_name[normalized_name(entry.get("name", candidate_id))].add(candidate_id)
        for identity in entry.get("source_identities", []):
            by_source[source_identity_key(identity)].add(candidate_id)
    return by_source, by_name, by_id


def deduplicate_candidates(
    raw_candidates: list[dict[str, Any]],
    known_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_source, known_names, known_by_id = _known_indexes(known_entries)
    merged: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []

    for raw_value in sorted(
        raw_candidates,
        key=lambda item: (
            item.get("normalized_name", ""),
            item.get("delivery_type", ""),
            str(item.get("source_identities", [])),
        ),
    ):
        raw = dict(raw_value)
        raw["normalized_name"] = normalized_name(raw.get("name", "UNKNOWN"))
        keys = {source_identity_key(item) for item in raw.get("source_identities", [])}
        matched = set().union(*(by_source.get(key, set()) for key in keys)) if keys else set()
        if raw.get("candidate_id") in known_by_id:
            matched = {raw["candidate_id"]}
        if len(matched) > 1:
            raw["identity_status"] = "IDENTITY_REVIEW_REQUIRED"
            raw["identity_conflict"] = True
            conflicts.append({
                "name": raw.get("name"),
                "matched_candidate_ids": sorted(matched),
                "reason": "SOURCE_IDENTITIES_MAP_TO_MULTIPLE_CANDIDATES",
            })
            candidate_id = f"CONFLICT-{candidate_fingerprint(raw)[:16].upper()}"
        elif matched:
            candidate_id = next(iter(matched))
        else:
            fingerprint = candidate_fingerprint(raw)
            candidate_id = raw.get("candidate_id") or f"CAP-{fingerprint[:16].upper()}"
            same_name = known_names.get(raw["normalized_name"], set())
            if same_name and candidate_id not in same_name:
                raw["identity_status"] = "IDENTITY_REVIEW_REQUIRED"
                raw["identity_conflict"] = True
                conflicts.append({
                    "name": raw.get("name"),
                    "matched_candidate_ids": sorted(same_name),
                    "reason": "NAME_MATCH_WITHOUT_IDENTITY_PROOF",
                })

        existing = merged.get(candidate_id)
        if existing is None:
            prior = known_by_id.get(candidate_id, {})
            raw["candidate_id"] = candidate_id
            raw["canonical_identity"] = prior.get("canonical_identity") or canonical_identity(
                raw.get("source_identities", []), candidate_id
            )
            raw["identity_status"] = raw.get("identity_status", "RESOLVED_EXACT_IDENTITY")
            raw["identity_conflict"] = bool(raw.get("identity_conflict", False))
            raw["candidate_fingerprint_sha256"] = prior.get(
                "candidate_fingerprint_sha256", candidate_fingerprint(raw)
            )
            merged[candidate_id] = raw
        else:
            for field in (
                "source_identities",
                "source_references",
                "source_digests",
                "source_revisions",
                "profile_ids",
                "limitations",
                "relevance_targets",
            ):
                values = existing.setdefault(field, [])
                for value in raw.get(field, []):
                    if value not in values:
                        values.append(value)
            existing["identity_conflict"] = existing.get("identity_conflict", False) or raw.get(
                "identity_conflict", False
            )
            if existing["identity_conflict"]:
                existing["identity_status"] = "IDENTITY_REVIEW_REQUIRED"

        for key in keys:
            by_source[key].add(candidate_id)
        known_names[raw["normalized_name"]].add(candidate_id)

    return sorted(merged.values(), key=lambda item: item["candidate_id"]), conflicts
