"""Bounded public-source discovery preparation for the existing 12 Cells."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from ..sources.arxiv_readonly import ArxivReadOnlyAdapter
    from ..sources.github_readonly import GithubPublicSearchAdapter
except ImportError:
    from sources.arxiv_readonly import ArxivReadOnlyAdapter
    from sources.github_readonly import GithubPublicSearchAdapter

from .artifact_memory import CapabilityArtifactMemory
from .deduplication import deduplicate_candidates
from .fingerprint import registry_digest, sha256_bytes, sha256_json
from .identity import (
    identity_from_reference,
    normalize_arxiv,
    normalize_repository,
    normalized_name,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _classify(text: str, taxonomy: dict[str, Any], fallback: str | None = None) -> str:
    normalized = normalized_name(text)
    scores = []
    for group in taxonomy.get("groups", []):
        score = sum(
            1
            for keyword in group.get("keywords", [])
            if normalized_name(keyword) in normalized
        )
        if score:
            scores.append((score, group["group_id"]))
    if scores:
        return sorted(scores, key=lambda item: (-item[0], item[1]))[0][1]
    return fallback or "OTHER_OR_UNCLASSIFIED"


def _matches_profile_relevance(
    record: dict[str, Any], profile: dict[str, Any] | None
) -> bool:
    """Fail closed unless each configured semantic term group has a lexical hit."""
    if profile is None:
        return True
    groups = profile.get("relevance_term_groups", [])
    if not groups or any(not isinstance(group, list) or not group for group in groups):
        return False
    text = normalized_name(f"{record.get('name', '')} {record.get('summary', '')}")
    return all(
        any(normalized_name(str(term)) in text for term in group)
        for group in groups
    )


def _baseline_registry(
    discovery_root: Path, observed_at: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline = discovery_root / "baseline" / "dcdat-001"
    records_path = baseline / "capability-discovery-records.json"
    registry_path = baseline / "reference-absorption-registry.json"
    records = _read_json(records_path)
    old_registry = _read_json(registry_path)
    baseline_digest = sha256_bytes(records_path.read_bytes())
    old_by_id = {item["candidate_id"]: item for item in old_registry.get("entries", [])}
    entries, prepared = [], []
    for item in records.get("candidates", []):
        source_identities = [
            identity
            for reference in item.get("sources", [])
            if (identity := identity_from_reference(reference)) is not None
        ]
        old = old_by_id.get(item["candidate_id"], {})
        limitation = item.get("identity_risk", "Historical baseline limitations preserved.")
        entry = {
            "candidate_id": item["candidate_id"],
            "candidate_fingerprint_sha256": item["candidate_fingerprint_sha256"],
            "canonical_identity": item["canonical_identity"],
            "name": item["name"],
            "capability_group": item["capability_group"],
            "source_identities": source_identities,
            "first_seen_at": records.get("observed_at", observed_at),
            "last_seen_at": records.get("observed_at", observed_at),
            "last_changed_at": records.get("observed_at", observed_at),
            "source_revisions": [item.get("source_revision", "NOT_PINNED")],
            "source_digests": [baseline_digest],
            "source_status": item.get("source_status", "BASELINE_HISTORICAL_RECORD"),
            "identity_status": "RESOLVED_BASELINE_IDENTITY",
            "license_status": item.get("license_status", "LICENSE_NOT_ASSESSED"),
            "code_source_status": item.get("code_source_status", "NOT_ASSESSED"),
            "absorption_status": "REFERENCE_UNCHANGED",
            "implementation_status": "NOT_ADOPTED",
            "limitations": old.get("limitations", [limitation]),
            "relevance_targets": ["DCELL_SUPPORTING_ARCHITECTURE", "GENERAL_REFERENCE"],
            "current_problem_match": False,
            "observation_state": "CONTINUING_REFERENCE",
            "external_code_executed": False,
            "dependency_installed": False,
            "runtime_modified": False,
            "ac2_readiness_status": "NOT_READY",
        }
        entries.append(entry)
        prepared.append({
            "signal_id": f"CAPABILITY-{item['candidate_id']}",
            "kind": "EXTERNAL_CAPABILITY_CANDIDATE",
            "candidate_id": item["candidate_id"],
            "candidate_fingerprint_sha256": item["candidate_fingerprint_sha256"],
            "canonical_identity": item["canonical_identity"],
            "name": item["name"],
            "normalized_name": normalized_name(item["name"]),
            "subject": item["name"],
            "title_zh": item["name"],
            "summary": item.get("capability_claim", ""),
            "capability_group": item["capability_group"],
            "delivery_type": "BASELINE_REFERENCE",
            "product_boundary": "HISTORICAL_REFERENCE",
            "source_identities": source_identities,
            "source_references": item.get("sources", []),
            "source_reference": (
                f"baseline/dcdat-001/capability-discovery-records.json"
                f"#{item['candidate_id']}"
            ),
            "source_digests": [baseline_digest],
            "source_digest": baseline_digest,
            "source_revisions": [item.get("source_revision", "NOT_PINNED")],
            "source_status": "BASELINE_HISTORICAL_RECORD",
            "identity_status": "RESOLVED_BASELINE_IDENTITY",
            "identity_conflict": False,
            "license_status": item.get("license_status", "LICENSE_NOT_ASSESSED"),
            "code_source_status": item.get("code_source_status", "NOT_ASSESSED"),
            "observed_at": observed_at,
            "freshness": "CURRENT",
            "authority": "OBSERVATION_ONLY",
            "admission_status": "PENDING",
            "admission_label_zh": "DCDAT-001持续参考候选",
            "details_zh": "历史候选已导入，首次自动运行不得把它重复计为新发现。",
            "origin": "DCDAT_001_BASELINE",
            "limitations": old.get("limitations", [limitation]),
            "relevance_targets": ["DCELL_SUPPORTING_ARCHITECTURE", "GENERAL_REFERENCE"],
            "current_problem_match": False,
        })
    registry = {
        "schema": "dba.reference_absorption_registry.v0.2",
        "registry_id": "DBA-CAPABILITY-REFERENCE-REGISTRY",
        "registry_revision": 0,
        "created_at": records.get("observed_at", observed_at),
        "updated_at": records.get("observed_at", observed_at),
        "previous_registry_digest": None,
        "current_registry_digest": "PENDING",
        "source_query_profile_digest": "DCDAT_001_BASELINE",
        "record_role": "STATE_VIEW_AND_REFERENCE_INDEX_NOT_IMPLEMENTATION_STATE",
        "absorption_policy": "AC-1_REFERENCE_ONLY",
        "entries": entries,
        "capability_groups": old_registry.get("overlap_groups", []),
        "identity_guardrails": old_registry.get("identity_guardrails", [])
        + ["A_MEM_REPRODUCTION_REPOSITORY_IS_NOT_AUTOMATICALLY_THE_PAPER_IMPLEMENTATION"],
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
        "memory_status": "DCDAT_001_BASELINE",
    }
    registry["current_registry_digest"] = registry_digest(registry)
    return registry, prepared


def _source_candidate(
    record: dict[str, Any],
    profile: dict[str, Any] | None,
    taxonomy: dict[str, Any],
) -> dict[str, Any] | None:
    kind = record.get("source_kind")
    if kind == "ARXIV":
        arxiv_id, version = normalize_arxiv(record.get("arxiv_identifier", ""))
        if not arxiv_id:
            return None
        identities = [{
            "type": "PAPER",
            "identity": f"arxiv:{arxiv_id}",
            "revision": version or "VERSION_NOT_EXPOSED",
        }]
        if record.get("doi"):
            identities.append({
                "type": "DOI",
                "identity": f"doi:{str(record['doi']).casefold()}",
            })
        delivery = "PAPER_ONLY"
        revision = f"arxiv:{arxiv_id}:{version or record.get('updated_at', 'UNKNOWN')}"
        code_status = "NOT_ASSESSED"
        license_status = "LICENSE_NOT_ASSESSED"
    elif kind == "GITHUB":
        repository = normalize_repository(record.get("repository", ""))
        if not repository:
            return None
        identities = [{
            "type": "REPOSITORY",
            "identity": f"github:{repository}",
            "revision": record.get("head_sha", "HEAD_NOT_ASSESSED"),
        }]
        delivery = "REPOSITORY_ONLY"
        revision = f"github:{repository}:{record.get('head_sha', 'HEAD_NOT_ASSESSED')}"
        code_status = "PUBLIC_REPOSITORY_METADATA_OBSERVED_NOT_EXECUTED"
        license_status = record.get("license_status", "LICENSE_NOT_ASSESSED")
    else:
        return None
    text = f"{record.get('name', '')} {record.get('summary', '')}"
    fallback = profile.get("capability_group") if profile else None
    return {
        "name": record.get("name", "UNKNOWN"),
        "normalized_name": normalized_name(record.get("name", "UNKNOWN")),
        "summary": record.get("summary", "")[:800],
        "capability_group": _classify(text, taxonomy, fallback),
        "delivery_type": delivery,
        "product_boundary": "INDEPENDENT_DELIVERABLE",
        "source_identities": identities,
        "source_references": [record.get("source_reference", "UNKNOWN")],
        "source_reference": record.get("source_reference", "UNKNOWN"),
        "source_digests": [record["source_digest_sha256"]],
        "source_digest": record["source_digest_sha256"],
        "source_revisions": [revision],
        "source_status": "SOURCE_METADATA_OBSERVED",
        "identity_status": "RESOLVED_EXACT_IDENTITY",
        "identity_conflict": False,
        "license_status": license_status,
        "code_source_status": code_status,
        "observed_at": record.get("observed_at"),
        "freshness": "CURRENT",
        "authority": "OBSERVATION_ONLY",
        "admission_status": "PENDING",
        "admission_label_zh": "待证据准入",
        "details_zh": "仅登记公开来源元数据；标题、摘要和仓库描述均视为不可信外部数据。",
        "origin": "PUBLIC_SOURCE_DISCOVERY",
        "profile_ids": (
            [profile["profile_id"]] if profile else ["REGISTERED_SOURCE_REFRESH"]
        ),
        "limitations": [
            "Metadata observation does not establish safety, superiority, compatibility, or official implementation status."
        ],
        "relevance_targets": (
            profile.get("relevance_targets", ["GENERAL_REFERENCE"])
            if profile
            else ["GENERAL_REFERENCE"]
        ),
        "current_problem_match": False,
    }


def build_capability_discovery_context(
    weekly_root: Path,
    observed_at: str,
    *,
    repository: str,
    workflow: str,
    run_id: str,
    arxiv_adapter: ArxivReadOnlyAdapter | None = None,
    github_adapter: GithubPublicSearchAdapter | None = None,
    artifact_memory: CapabilityArtifactMemory | None = None,
) -> dict[str, Any]:
    root = weekly_root / "discovery"
    profiles = _read_json(root / "query-profiles.json")
    taxonomy = _read_json(root / "capability-taxonomy.json")
    source_registry = _read_json(root / "public-source-registry.json")
    profile_digest = sha256_json(profiles)
    baseline_registry, baseline_records = _baseline_registry(root, observed_at)
    memory = (artifact_memory or CapabilityArtifactMemory()).load_previous(
        repository, workflow, run_id, observed_at
    )
    previous_registry = memory.get("previous_registry") or baseline_registry
    previous_entries = previous_registry.get("entries", [])
    arxiv = arxiv_adapter or ArxivReadOnlyAdapter()
    github = github_adapter or GithubPublicSearchAdapter()
    raw: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    evidence: list[dict[str, Any]] = []
    source_statuses: list[str] = []
    total_limit = int(profiles.get("max_total_raw_results", 150))
    per_profile_default = int(profiles.get("max_raw_results_per_profile", 30))

    baseline_arxiv = sorted({
        identity["identity"].split(":", 1)[1]
        for entry in baseline_registry["entries"]
        for identity in entry.get("source_identities", [])
        if identity.get("type") == "PAPER"
        and identity.get("identity", "").startswith("arxiv:")
    })
    baseline_repositories = sorted({
        identity["identity"].split(":", 1)[1]
        for entry in baseline_registry["entries"]
        for identity in entry.get("source_identities", [])
        if identity.get("type") == "REPOSITORY"
        and identity.get("identity", "").startswith("github:")
    })
    registered_arxiv = arxiv.fetch_ids(baseline_arxiv, observed_at)
    evidence.append(registered_arxiv["evidence"])
    source_statuses.append(registered_arxiv["status"])
    raw.extend((record, None) for record in registered_arxiv["records"])
    registered_github = github.observe_repositories(baseline_repositories, observed_at)
    evidence.extend(registered_github["evidence"])
    source_statuses.append(registered_github["status"])
    raw.extend((record, None) for record in registered_github["records"])

    as_of = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    lookback = int(profiles.get("lookback_days", 14))
    start = (as_of - timedelta(days=lookback)).date().isoformat()
    for profile in [item for item in profiles.get("profiles", []) if item.get("enabled")]:
        if len(raw) >= total_limit:
            break
        limit = min(
            int(profile.get("max_candidates", per_profile_default)),
            total_limit - len(raw),
        )
        arxiv_query = (
            f"({profile['arxiv_query']}) AND submittedDate:"
            f"[{start.replace('-', '')}0000 TO "
            f"{as_of.date().isoformat().replace('-', '')}2359]"
        )
        batch = arxiv.search(arxiv_query, limit, observed_at)
        evidence.append({**batch["evidence"], "profile_id": profile["profile_id"]})
        source_statuses.append(batch["status"])
        raw.extend((record, profile) for record in batch["records"][:limit])
        if len(raw) >= total_limit:
            break
        github_query = f"{profile['github_query']} pushed:>={start}"
        batch = github.search(
            github_query, min(limit, total_limit - len(raw)), observed_at
        )
        evidence.extend(
            {**item, "profile_id": profile["profile_id"]}
            for item in batch["evidence"]
        )
        source_statuses.append(batch["status"])
        raw.extend(
            (record, profile)
            for record in batch["records"][: max(0, total_limit - len(raw))]
        )

    normalized: list[dict[str, Any]] = []
    relevance_rejections: list[dict[str, Any]] = []
    for record, profile in raw:
        if not _matches_profile_relevance(record, profile):
            relevance_rejections.append({
                "profile_id": profile.get("profile_id", "UNKNOWN_PROFILE"),
                "source_reference": record.get("source_reference", "UNKNOWN"),
                "source_digest_sha256": record.get("source_digest_sha256", "UNKNOWN"),
                "reason": "DETERMINISTIC_RELEVANCE_TERM_GROUP_MISS",
            })
            continue
        candidate = _source_candidate(record, profile, taxonomy)
        if candidate is not None:
            normalized.append(candidate)
    candidates, conflicts = deduplicate_candidates(
        baseline_records + normalized, previous_entries
    )
    max_absorptions = int(
        profiles.get("max_new_reference_absorptions_per_run", 25)
    )
    previous_ids = {item["candidate_id"] for item in previous_entries}
    accepted, new_count = [], 0
    truncated = False
    for candidate in candidates:
        if candidate["candidate_id"] not in previous_ids:
            if new_count >= max_absorptions:
                truncated = True
                continue
            new_count += 1
        candidate["signal_id"] = f"CAPABILITY-{candidate['candidate_id']}"
        candidate["kind"] = "EXTERNAL_CAPABILITY_CANDIDATE"
        candidate["subject"] = candidate["name"]
        candidate["title_zh"] = candidate["name"]
        candidate["observed_at"] = observed_at
        candidate["freshness"] = "CURRENT"
        candidate["authority"] = "OBSERVATION_ONLY"
        accepted.append(candidate)

    available = sum(status == "AVAILABLE" for status in source_statuses)
    unavailable = len(source_statuses) - available
    discovery_status = (
        "DISCOVERY_UNAVAILABLE"
        if available == 0
        else "PASS_WITH_PARTIAL_SOURCE_COVERAGE"
        if unavailable
        else "PASS"
    )
    manifest = {
        "schema": "dba.source_evidence_manifest.v0.1",
        "observed_at": observed_at,
        "discovery_source_universe": "BOUNDED_APPROVED_PUBLIC_SOURCES",
        "open_world_completeness_claim": False,
        "input_configuration_digest": sha256_json({
            "profiles": profiles,
            "taxonomy": taxonomy,
            "sources": source_registry,
        }),
        "source_query_profile_digest": profile_digest,
        "requests": evidence,
        "available_source_batches": available,
        "unavailable_source_batches": unavailable,
        "partial_payload_used": False,
        "private_source_discovery": False,
        "private_discovery_token_used": False,
        "exposed_token_used": False,
        "relevance_gate": {
            "policy": "DETERMINISTIC_ALL_GROUPS_ANY_TERM_V0.1",
            "configuration_digest": profile_digest,
            "rejected_count": len(relevance_rejections),
            "rejections": relevance_rejections,
        },
    }
    relationships = [{
        "relationship_id": f"GUARDRAIL-{index + 1:02d}",
        "rule": rule,
        "status": "PRESERVED",
        "authority": "REFERENCE_ONLY",
    } for index, rule in enumerate(baseline_registry.get("identity_guardrails", []))]
    return {
        "capability_discovery_records": accepted,
        "capability_relationship_records": relationships,
        "capability_previous_registry": previous_registry,
        "capability_memory_metadata": memory,
        "capability_query_profile_digest": profile_digest,
        "capability_source_evidence_manifest": manifest,
        "capability_source_summary": {
            "status": discovery_status,
            "raw_candidate_count": len(raw),
            "identity_resolved_count": len(accepted) - len(conflicts),
            "identity_conflict_count": len(conflicts),
            "relevance_admitted_count": len(normalized),
            "relevance_rejected_count": len(relevance_rejections),
            "source_not_assessed_count": unavailable,
            "truncated_by_bounded_limit": truncated or len(raw) >= total_limit,
            "model_calls": 0,
        },
        "capability_discovery_boundary": {
            "automation_scope": "AC0_DISCOVERY_AND_AC1_REFERENCE_ONLY",
            "bounded_public_source_universe": True,
            "open_world_completeness_claim": False,
            "model_calls": 0,
            "external_ai_api": False,
            "external_code_executed": False,
            "dependency_installed": False,
            "code_adopted": 0,
            "runtime_changed": False,
            "dcell_changed": False,
            "red_yan_changed": False,
            "titmas_implementation_changed": False,
            "ac2_authorized": False,
            "ac2_executed": False,
            "logical_cell_count": 12,
            "coordinator_mode": "ORCHESTRATION_ONLY",
        },
    }
