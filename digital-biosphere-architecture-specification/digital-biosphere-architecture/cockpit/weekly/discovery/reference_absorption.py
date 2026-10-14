"""AC-1 reference-only registry construction and cross-run delta semantics."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .fingerprint import registry_digest


def _unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _ac2_status(entry: dict[str, Any]) -> str:
    if entry.get("identity_status") == "IDENTITY_REVIEW_REQUIRED":
        return "BLOCKED_BY_IDENTITY"
    repositories = [
        item for item in entry.get("source_identities", []) if item.get("type") == "REPOSITORY"
    ]
    if not repositories:
        return "BLOCKED_BY_NO_IMPLEMENTATION"
    if entry.get("license_status") != "LICENSE_FILE_OBSERVED":
        return "BLOCKED_BY_LICENSE"
    if not any(item.get("revision") for item in repositories):
        return "BLOCKED_BY_SOURCE_REVISION"
    return "REVIEW_ELIGIBLE"


def build_reference_registry(
    records: list[dict[str, Any]],
    admission_decisions: list[dict[str, Any]],
    previous_registry: dict[str, Any],
    *,
    observed_at: str,
    query_profile_digest: str,
    memory_status: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    previous_entries = {
        item["candidate_id"]: item for item in previous_registry.get("entries", [])
    }
    admitted = {
        item["observation"]["signal_id"]: item["status"]
        for item in admission_decisions
        if item.get("observation", {}).get("kind") == "EXTERNAL_CAPABILITY_CANDIDATE"
    }
    entries: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    observed_ids: set[str] = set()

    for record in records:
        candidate_id = record["candidate_id"]
        observed_ids.add(candidate_id)
        prior = previous_entries.get(candidate_id)
        admission = admitted.get(record["signal_id"], "REJECTED")
        if record.get("identity_conflict"):
            absorption = "REFERENCE_CONFLICT"
            delta = "CONFLICTING_REFERENCE"
        elif admission != "ADMITTED":
            absorption = "REFERENCE_REJECTED"
            delta = (
                "CONFLICTING_REFERENCE"
                if record.get("identity_status") == "IDENTITY_REVIEW_REQUIRED"
                else "NEW_REFERENCE"
            )
        elif prior is None:
            absorption = "REFERENCE_ABSORBED"
            delta = "NEW_REFERENCE"
        else:
            previous_digests = set(prior.get("source_digests", []))
            current_digests = set(record.get("source_digests", []))
            previous_revisions = set(prior.get("source_revisions", []))
            current_revisions = set(record.get("source_revisions", []))
            if current_digests - previous_digests or current_revisions - previous_revisions:
                absorption = "REFERENCE_UPDATED"
                delta = "UPDATED_REFERENCE"
            else:
                absorption = "REFERENCE_UNCHANGED"
                delta = "CONTINUING_REFERENCE"

        entry = {
            "candidate_id": candidate_id,
            "candidate_fingerprint_sha256": record["candidate_fingerprint_sha256"],
            "canonical_identity": record["canonical_identity"],
            "name": record["name"],
            "capability_group": record.get("capability_group", "OTHER_OR_UNCLASSIFIED"),
            "source_identities": record.get("source_identities", []),
            "first_seen_at": prior.get("first_seen_at", observed_at) if prior else observed_at,
            "last_seen_at": observed_at,
            "last_changed_at": (
                prior.get("last_changed_at", observed_at)
                if prior and delta == "CONTINUING_REFERENCE"
                else observed_at
            ),
            "source_revisions": _unique(
                (prior or {}).get("source_revisions", []) + record.get("source_revisions", [])
            ),
            "source_digests": _unique(
                (prior or {}).get("source_digests", []) + record.get("source_digests", [])
            ),
            "source_status": record.get("source_status", "NOT_ASSESSED_SOURCE_UNAVAILABLE"),
            "identity_status": record.get("identity_status", "RESOLVED_EXACT_IDENTITY"),
            "license_status": record.get("license_status", "LICENSE_NOT_ASSESSED"),
            "code_source_status": record.get("code_source_status", "NOT_ASSESSED"),
            "absorption_status": absorption,
            "implementation_status": "NOT_ADOPTED",
            "limitations": _unique(record.get("limitations", [])),
            "relevance_targets": _unique(record.get("relevance_targets", ["GENERAL_REFERENCE"])),
            "current_problem_match": bool(record.get("current_problem_match", False)),
            "observation_state": delta,
            "external_code_executed": False,
            "dependency_installed": False,
            "runtime_modified": False,
        }
        entry["ac2_readiness_status"] = _ac2_status(entry)
        entries.append(entry)
        events.append({
            "candidate_id": candidate_id,
            "state": delta,
            "absorption_status": absorption,
            "observed_at": observed_at,
        })

    for candidate_id, prior in previous_entries.items():
        if candidate_id in observed_ids:
            continue
        retained = dict(prior)
        retained["absorption_status"] = "REFERENCE_UNCHANGED"
        retained["observation_state"] = "NO_LONGER_OBSERVED"
        retained["implementation_status"] = "NOT_ADOPTED"
        entries.append(retained)
        events.append({
            "candidate_id": candidate_id,
            "state": "NO_LONGER_OBSERVED",
            "absorption_status": "REFERENCE_UNCHANGED",
            "observed_at": observed_at,
        })

    groups: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        groups[entry["capability_group"]].append(entry["candidate_id"])
    previous_digest = previous_registry.get("current_registry_digest")
    registry = {
        "schema": "dba.reference_absorption_registry.v0.2",
        "registry_id": "DBA-CAPABILITY-REFERENCE-REGISTRY",
        "registry_revision": int(previous_registry.get("registry_revision", 0)) + 1,
        "created_at": previous_registry.get("created_at", observed_at),
        "updated_at": observed_at,
        "previous_registry_digest": previous_digest,
        "current_registry_digest": "PENDING",
        "source_query_profile_digest": query_profile_digest,
        "record_role": "STATE_VIEW_AND_REFERENCE_INDEX_NOT_IMPLEMENTATION_STATE",
        "absorption_policy": "AC-1_REFERENCE_ONLY",
        "entries": sorted(entries, key=lambda item: item["candidate_id"]),
        "capability_groups": [
            {"group": group, "members": sorted(members)}
            for group, members in sorted(groups.items())
        ],
        "identity_guardrails": previous_registry.get("identity_guardrails", []),
        "run_effects": {
            "external_code_executed": False,
            "dependency_installed": False,
            "runtime_modified": False,
            "dcell_core_modified": False,
            "red_yan_modified": False,
            "titmas_implementation_modified": False,
            "frozen_history_modified": False,
        },
        "next_gate": {
            "level": "AC-2_SANDBOX",
            "status": "NOT_AUTHORIZED",
            "automated": False,
        },
        "memory_status": memory_status,
    }
    registry["current_registry_digest"] = registry_digest(registry)
    counts = defaultdict(int)
    for event in events:
        counts[event["state"]] += 1
    delta = {
        "schema": "dba.capability_discovery_delta.v0.1",
        "observed_at": observed_at,
        "previous_registry_digest": previous_digest,
        "current_registry_digest": registry["current_registry_digest"],
        "counts": dict(sorted(counts.items())),
        "events": sorted(events, key=lambda item: item["candidate_id"]),
    }
    return registry, delta
